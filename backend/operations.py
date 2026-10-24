"""Operational extensions. All conclusions are evidence-gated; no manual completion flag."""
import datetime,json,uuid,math
from fastapi import APIRouter,Request,HTTPException
from pydantic import BaseModel,Field
from .db import connect,transaction
from .security import current_user,require,now
router=APIRouter(prefix='/api/operations',tags=['operations'])
def ident():return str(uuid.uuid4())
def actor(request,permission):
 u=current_user(request);require(u,permission);return u
def init_operations():
 with connect() as c:c.executescript('''
 CREATE TABLE IF NOT EXISTS device_bindings(id TEXT PRIMARY KEY,device_id TEXT NOT NULL UNIQUE,kind TEXT NOT NULL,warehouse_id TEXT,production_line TEXT,enabled INTEGER NOT NULL DEFAULT 1,created_by TEXT NOT NULL,created_at TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS evidence_links(id TEXT PRIMARY KEY,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,document_id TEXT NOT NULL REFERENCES documents(id),evidence_type TEXT NOT NULL,linked_by TEXT NOT NULL,linked_at TEXT NOT NULL,UNIQUE(entity_type,entity_id,document_id,evidence_type));
 CREATE TABLE IF NOT EXISTS verified_results(id TEXT PRIMARY KEY,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,decision TEXT NOT NULL,reason_json TEXT NOT NULL,checked_at TEXT NOT NULL,UNIQUE(entity_type,entity_id));
 CREATE TABLE IF NOT EXISTS operational_alerts(id TEXT PRIMARY KEY,rule_code TEXT NOT NULL,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,level TEXT NOT NULL,reason TEXT NOT NULL,detected_at TEXT NOT NULL,UNIQUE(rule_code,entity_type,entity_id));
 CREATE INDEX IF NOT EXISTS idx_evidence_entity ON evidence_links(entity_type,entity_id);
 ''')
class BindDevice(BaseModel):
 device_id:str=Field(min_length=1,max_length=80)
 kind:str=Field(min_length=2,max_length=40)
 warehouse_id:str|None=None
 production_line:str|None=None
@router.post('/device-bindings',status_code=201)
def bind_device(body:BindDevice,request:Request):
 u=actor(request,'assets.write')
 if body.kind not in ('scale_kg','meter_m','power_kwh','camera_event','humidity_pct','temperature_c'):raise HTTPException(422,'Loại thiết bị không hợp lệ')
 with transaction() as c:
  if body.warehouse_id and not c.execute('SELECT 1 FROM warehouses WHERE id=?',(body.warehouse_id,)).fetchone():raise HTTPException(404,'Kho không tồn tại')
  if c.execute('SELECT 1 FROM device_bindings WHERE device_id=?',(body.device_id,)).fetchone():raise HTTPException(409,'Thiết bị đã được gán')
  rid=ident();c.execute('INSERT INTO device_bindings VALUES(?,?,?,?,?,?,?,?)',(rid,body.device_id,body.kind,body.warehouse_id,body.production_line,1,u['username'],now()))
 return {'id':rid,'bound':True}
@router.get('/device-bindings')
def bindings(request:Request):
 actor(request,'assets.read')
 with connect() as c:return {'items':[dict(r) for r in c.execute('SELECT device_id,kind,warehouse_id,production_line,enabled FROM device_bindings ORDER BY device_id')]}
class LinkEvidence(BaseModel):
 entity_type:str
 entity_id:str
 document_id:str
 evidence_type:str
@router.post('/evidence',status_code=201)
def link_evidence(body:LinkEvidence,request:Request):
 u=actor(request,'documents.write')
 if body.entity_type!='production_batches':raise HTTPException(422,'Chỉ hỗ trợ bằng chứng ca sản xuất trong phiên bản này')
 if body.evidence_type not in ('meter_photo','scale_ticket','qc_report'):raise HTTPException(422,'Loại bằng chứng không hợp lệ')
 with transaction() as c:
  if not c.execute('SELECT 1 FROM production_batches WHERE id=?',(body.entity_id,)).fetchone():raise HTTPException(404,'Không có ca sản xuất')
  d=c.execute('SELECT uploaded_by FROM documents WHERE id=?',(body.document_id,)).fetchone()
  if not d:raise HTTPException(404,'Chứng từ không tồn tại')
  if u['role']!='director' and d['uploaded_by']!=u['username']:raise HTTPException(403,'Không có quyền gắn chứng từ người khác')
  if c.execute('SELECT 1 FROM evidence_links WHERE entity_type=? AND entity_id=? AND document_id=? AND evidence_type=?',(body.entity_type,body.entity_id,body.document_id,body.evidence_type)).fetchone():raise HTTPException(409,'Bằng chứng đã được gắn')
  rid=ident();c.execute('INSERT INTO evidence_links VALUES(?,?,?,?,?,?,?)',(rid,body.entity_type,body.entity_id,body.document_id,body.evidence_type,u['username'],now()))
 return {'id':rid,'linked':True,'verified':False}
@router.post('/verify/{batch_id}')
def verify(batch_id:str,request:Request):
 actor(request,'production.read')
 with transaction() as c:
  b=c.execute('SELECT * FROM production_batches WHERE id=?',(batch_id,)).fetchone()
  if not b:raise HTTPException(404,'Không có ca sản xuất')
  linked={r['evidence_type'] for r in c.execute('SELECT evidence_type FROM evidence_links WHERE entity_type=? AND entity_id=?',('production_batches',batch_id))}
  required={'meter_photo','scale_ticket','qc_report'}
  problems=[]
  if b['source_kind']!='real':problems.append('Số liệu không được khai báo là dữ liệu thực')
  if b['output_gross'] is None or b['output_pass'] is None or b['output_reject'] is None:problems.append('Thiếu số liệu sản lượng')
  elif b['output_pass']+b['output_reject']>b['output_gross']+1e-6:problems.append('Sản lượng QC vượt tổng sản lượng')
  missing=sorted(required-linked)
  if missing:problems.append('Thiếu bằng chứng: '+', '.join(missing))
  # Uploaded evidence is not proof of content accuracy. Never auto-approve based on existence alone.
  decision='rejected' if any('vượt' in x for x in problems) else 'pending_independent_review'
  if not problems:problems.append('Cần đối chiếu nội dung chứng từ, số đo thiết bị và chữ ký QC')
  c.execute('INSERT INTO verified_results VALUES(?,?,?,?,?,?) ON CONFLICT(entity_type,entity_id) DO UPDATE SET decision=excluded.decision,reason_json=excluded.reason_json,checked_at=excluded.checked_at',(ident(),'production_batches',batch_id,decision,json.dumps(problems,ensure_ascii=False),now()))
 return {'batch_id':batch_id,'decision':decision,'verified':False,'reasons':problems}
@router.get('/accounting/ledger')
def ledger(request:Request,account_code:str|None=None,limit:int=200):
 actor(request,'purchases.read')
 with connect() as c:
  sql='''SELECT e.id,e.entry_date,e.description,e.status,l.account_code,l.debit,l.credit FROM accounting_entries e JOIN accounting_lines l ON l.entry_id=e.id WHERE (? IS NULL OR l.account_code=?) ORDER BY e.entry_date DESC,e.created_at DESC LIMIT ?'''
  rows=[dict(r) for r in c.execute(sql,(account_code,account_code,min(max(limit,1),1000)))]
 return {'items':rows,'source':'posted_journal_entries','currency':'VND','note':'Chưa thay thế phần mềm kế toán tuân thủ đầy đủ pháp luật'}
@router.get('/alerts')
def alerts(request:Request):
 actor(request,'costs.read')
 with connect() as c:
  low=[dict(r) for r in c.execute('''SELECT i.id,i.sku,i.name,i.standard_qty,COALESCE(SUM(m.quantity_delta),0) stock FROM inventory_items i LEFT JOIN stock_movements m ON m.item_id=i.id GROUP BY i.id HAVING i.standard_qty>0 AND stock<=i.standard_qty*.4''')]
  bad=[dict(r) for r in c.execute('''SELECT id,batch_code,output_gross,output_pass,output_reject FROM production_batches WHERE output_pass+output_reject>output_gross''')]
  journal=c.execute('''SELECT COALESCE(SUM(debit-credit),0) FROM accounting_lines''').fetchone()[0]
 return {'items':[{'level':'red','type':'stock_low','entity_id':x['id'],'detail':x} for x in low]+[{'level':'red','type':'qc_mismatch','entity_id':x['id'],'detail':x} for x in bad]+([{'level':'red','type':'journal_imbalance','difference':journal}] if journal else []),'computed_at':now(),'source':'database_rules'}

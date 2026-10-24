"""SUNNY V86 API v1. Server-side authorization; all SQL parameterized."""
import os,json,uuid,math,hashlib,logging,time,threading,datetime,sqlite3
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request,Depends,UploadFile,File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from . import db,security
from .db import connect,transaction
ROOT=Path(__file__).resolve().parent.parent
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
log=logging.getLogger('sunny')
@asynccontextmanager
async def lifespan(app):
 db.init()
 security.bootstrap()
 init_compat()
 init_devices()
 init_operations()
 init_accounting()
 init_erp()
 init_registry()
 from .automation import start_worker, STOP
 start_worker()
 try:
  yield
 finally:
  STOP.set()

app=FastAPI(title='SUNNY FLEX 3D API',version='1.1.0',docs_url='/api/docs',openapi_url='/api/openapi.json',lifespan=lifespan)
now=security.now

def uid():return str(uuid.uuid4())
def actor(req):return security.current_user(req)
def allowed(req,perm):
 u=actor(req);security.require(u,perm);return u

def finite(v,maximum=1e12):
 try:f=float(v)
 except (ValueError,TypeError):raise HTTPException(422,'Giá trị không hợp lệ')
 if not math.isfinite(f) or f<0 or f>maximum:raise HTTPException(422,'Giá trị ngoài giới hạn')
 return f

def audit(c,u,action,entity,entity_id,payload=None):
 c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,new_json) VALUES(?,?,?,?,?,?)',(u['username'],action,entity,entity_id,now(),json.dumps(payload or {},ensure_ascii=False)))

def idem(c,key,u,route):
 if not key or len(key)<8 or len(key)>128:raise HTTPException(422,'Cần request_id từ 8–128 ký tự')
 old=c.execute('SELECT * FROM api_idempotency WHERE key=?',(key,)).fetchone()
 if old:
  if old['actor']!=u['username'] or old['route']!=route:raise HTTPException(409,'Mã phiếu đã sử dụng ở nghiệp vụ khác')
  return json.loads(old['result_json'])

def remember(c,key,u,route,result):
 c.execute('INSERT INTO api_idempotency VALUES(?,?,?,?,?)',(key,u['username'],route,json.dumps(result,ensure_ascii=False),now()))

@app.exception_handler(Exception)
async def unhandled(req,exc):
 error_id=uid();log.exception('internal_error id=%s route=%s',error_id,req.url.path)
 return JSONResponse(status_code=500,content={'error':'Lỗi hệ thống','error_id':error_id})

@app.get('/api/health')
def health():return {'status':'ok','time':now(),'database':'sqlite'}

class Login(BaseModel):username:str;password:str
@app.post('/api/auth/login')
def login(body:Login,request:Request):
 # Persistent account lockout must be implemented for public deployment.
 return {'access_token':security.authenticate(body.username,body.password),'token_type':'bearer','expires_in':28800}
@app.get('/api/auth/me')
def me(request:Request):
 u=actor(request);return {'username':u['username'],'role':u['role'],'owner_id':u['owner_id']}

TABLES={
 'customers':('customers.read','customers.write',('customer_code','name','phone','province','owner_employee_id','source_kind'),('customer_code','name')),
 'employees':('employees.read','employees.write',('department_id','employee_code','full_name','position','status','hired_on','source_kind'),('employee_code','full_name')),
 'assets':('assets.read','assets.write',('asset_code','name','category_id','acquired_on','acquisition_cost','residual_value','custodian_id','location','status','source_document_id'),('asset_code','name')),
 'marketing_campaigns':('marketing.read','marketing.write',('name','channel','budget_amount','owner_employee_id','starts_on','ends_on','status'),('name',)),
 'inventory_items':('stock.read','stock.write',('sku','name','category','unit','standard_qty','lead_days','daily_usage'),('sku','name','category','unit')),
 'sales_orders':('orders.read','orders.write',('order_code','customer_id','campaign_id','owner_employee_id','ordered_at','status','source_kind'),('order_code','customer_id')),
 'purchases':('purchases.read','purchases.write',('invoice_no','supplier_id','purchased_on','total_amount','classification','document_id','request_id','source_kind'),('purchased_on','total_amount','classification','request_id')),
 'production_batches':('production.read','production.write',('batch_code','product_id','shift_date','shift_code','leader_id','output_gross','output_pass','output_reject','source_kind'),('batch_code','shift_date')),
 'incidents':('incidents.write','incidents.write',('incident_code','category','occurred_at','department_id','employee_id','batch_id','estimated_loss','verified_loss','status','evidence_document_id'),('incident_code','category','occurred_at')),
 'duty_catalog':('duties.read','duties.write',('position','title','frequency','expected_evidence','weight'),('position','title','frequency')),
}

def scoped_filter(table,u):
 if u['role'] in ('sales','marketing','collaborator') and table in ('customers','sales_orders'):
  if not u['owner_id']:return (' AND 1=0',[])
  return (' AND owner_employee_id=?',[u['owner_id']])
 if u['role']=='collaborator' and table=='marketing_campaigns':return (' AND 1=0',[])
 return ('',[])

@app.get('/api/v1/{table}')
def list_records(table:str,request:Request,limit:int=100,offset:int=0):
 if table not in TABLES:raise HTTPException(404,'Không có phân hệ')
 u=allowed(request,TABLES[table][0]);where,params=scoped_filter(table,u)
 if u['role']=='worker' and table=='production_batches':raise HTTPException(403,'Chưa gắn ca làm; không được xem toàn bộ sản xuất')
 with connect() as c:
  rows=[dict(x) for x in c.execute('SELECT * FROM '+table+' WHERE 1=1'+where+' ORDER BY rowid DESC LIMIT ? OFFSET ?',(*params,min(max(limit,1),500),max(offset,0)))]
  total=c.execute('SELECT COUNT(*) FROM '+table+' WHERE 1=1'+where,params).fetchone()[0]
 return {'items':rows,'total':total,'limit':min(max(limit,1),500),'offset':offset}

@app.post('/api/v1/{table}',status_code=201)
def create_record(table:str,body:dict,request:Request):
 if table not in TABLES:raise HTTPException(404,'Không có phân hệ')
 u=allowed(request,TABLES[table][1]);columns=TABLES[table][2];required=TABLES[table][3]
 if any(body.get(x) is None or body.get(x)=='' for x in required):raise HTTPException(422,'Thiếu trường bắt buộc: '+','.join(x for x in required if not body.get(x)))
 if u['role'] in ('sales','marketing','collaborator') and table in ('customers','sales_orders'):
  if not u['owner_id']:raise HTTPException(403,'Tài khoản chưa gắn nhân viên')
  if body.get('owner_employee_id') not in (None,u['owner_id']):raise HTTPException(403,'Không được tạo cho người khác')
  body['owner_employee_id']=u['owner_id']
 for field in ('budget_amount','acquisition_cost','residual_value','total_amount','output_gross','output_pass','output_reject','standard_qty','lead_days','daily_usage','estimated_loss'):
  if field in body:finite(body[field])
 if table=='production_batches' and float(body.get('output_pass',0))+float(body.get('output_reject',0))>float(body.get('output_gross',0)):raise HTTPException(422,'QC vượt sản lượng')
 if table=='purchases':raise HTTPException(409,'Dùng /api/purchases/commit để chống trùng và đối soát')
 rid=uid();fields=[x for x in columns if x in body];vals=[body[x] for x in fields]
 if table=='employees':
  if 'created_at' not in fields:fields.append('created_at');vals.append(now())
 if table=='customers':
  if 'created_at' not in fields:fields.append('created_at');vals.append(now())
 try:
  with transaction() as c:
   c.execute('INSERT INTO '+table+'(id,'+','.join(fields)+') VALUES('+','.join(['?']*(len(fields)+1))+')',[rid,*vals])
   audit(c,u,'create',table,rid,{'fields':fields})
 except sqlite3.IntegrityError:raise HTTPException(409,'Trùng mã hoặc dữ liệu liên kết không tồn tại')
 return {'id':rid,'created':True}

@app.get('/api/warehouses')
def warehouses(request:Request):
 allowed(request,'stock.read')
 with connect() as c:return {'items':[dict(x) for x in c.execute('SELECT id,name FROM warehouses ORDER BY name')]}

@app.get('/api/stock/summary')
def stock_summary(request:Request):
 allowed(request,'stock.read')
 with connect() as c:
  rows=[dict(x) for x in c.execute('''SELECT i.id,i.sku,i.name,i.category,i.unit,i.standard_qty,i.lead_days,i.daily_usage,COALESCE(SUM(m.quantity_delta),0) stock FROM inventory_items i LEFT JOIN stock_movements m ON m.item_id=i.id GROUP BY i.id ORDER BY i.name''')]
 for r in rows:
  r['warning_40pct']=r['standard_qty']>0 and r['stock']<=.4*r['standard_qty']
  r['urgent_lead_time']=r['daily_usage']>0 and r['stock']<r['daily_usage']*r['lead_days']
  r['source']='derived_from_movements'
 return {'items':rows,'time':now()}

class Movement(BaseModel):
 request_id:str=Field(min_length=8,max_length=128)
 item_id:str;warehouse_id:str;quantity:float;kind:str;lot_id:str|None=None;batch_id:str|None=None;source_kind:str='real'
@app.post('/api/stock/movements')
def move(body:Movement,request:Request):
 u=allowed(request,'stock.write')
 if body.kind not in ('in','out'):raise HTTPException(422,'Loại phiếu không hợp lệ')
 q=finite(body.quantity,1e9)
 if q<=0:raise HTTPException(422,'Số lượng phải lớn hơn 0')
 with transaction() as c:
  old=idem(c,body.request_id,u,'stock_movement')
  if old:return old
  item=c.execute('SELECT * FROM inventory_items WHERE id=?',(body.item_id,)).fetchone()
  if not item:raise HTTPException(404,'Không có vật tư')
  if not c.execute('SELECT 1 FROM warehouses WHERE id=?',(body.warehouse_id,)).fetchone():raise HTTPException(404,'Kho không tồn tại')
  qty=c.execute('SELECT COALESCE(SUM(quantity_delta),0) FROM stock_movements WHERE item_id=? AND warehouse_id=?',(body.item_id,body.warehouse_id)).fetchone()[0]
  delta=q if body.kind=='in' else -q
  if qty+delta < -1e-9:raise HTTPException(409,'Xuất quá tồn kho')
  rid=uid();c.execute('''INSERT INTO stock_movements(id,request_id,item_id,lot_id,warehouse_id,batch_id,kind,quantity_delta,occurred_at,actor_id,source_kind) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',(rid,body.request_id,body.item_id,body.lot_id,body.warehouse_id,body.batch_id,body.kind,delta,now(),u['username'],body.source_kind))
  result={'id':rid,'stock_after':qty+delta,'warning_40pct':item['standard_qty']>0 and qty+delta<=.4*item['standard_qty']}
  remember(c,body.request_id,u,'stock_movement',result);audit(c,u,'stock_'+body.kind,'stock_movements',rid,result)
 return result

class Purchase(BaseModel):
 request_id:str=Field(min_length=8,max_length=128);purchased_on:str;classification:str;total_amount:int;invoice_no:str|None=None;supplier_id:str|None=None;source_kind:str='real'
@app.post('/api/purchases/commit')
def purchase(body:Purchase,request:Request):
 u=allowed(request,'purchases.write')
 if body.classification not in ('inventory','asset','prepaid','expense','pending'):raise HTTPException(422,'Sai phân loại')
 finite(body.total_amount,10**13)
 with transaction() as c:
  old=idem(c,body.request_id,u,'purchase')
  if old:return old
  rid=uid();c.execute('INSERT INTO purchases(id,request_id,purchased_on,classification,total_amount,invoice_no,supplier_id,source_kind) VALUES(?,?,?,?,?,?,?,?)',(rid,body.request_id,body.purchased_on,body.classification,body.total_amount,body.invoice_no,body.supplier_id,body.source_kind))
  result={'id':rid,'classification':body.classification,'accounting_status':'pending_review'}
  remember(c,body.request_id,u,'purchase',result);audit(c,u,'purchase_create','purchases',rid,result)
 return result

@app.get('/api/costs/3-percent')
def costs(request:Request,period:str|None=None):
 allowed(request,'costs.read')
 with connect() as c:
  where=' WHERE period=?' if period else '';params=(period,) if period else ()
  rows=[dict(x) for x in c.execute('SELECT category,SUM(amount) total,COUNT(*) transactions FROM cost_transactions'+where+' GROUP BY category ORDER BY total DESC',params)]
  total=sum(x['total'] for x in rows)
 return {'period':period,'total_cost':total,'target_saving_3pct':round(total*.03),'categories':rows,'verified_saving':0,'note':'Chỉ tổng hợp cost_transactions đã phân loại. Chưa đủ dữ liệu thì không khẳng định đạt KPI.'}

@app.get('/api/dashboard')
def dashboard(request:Request):
 u=actor(request)
 with connect() as c:
  counts={t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('customers','sales_orders','employees','assets','purchases','production_batches')}
  if u['role'] in ('sales','marketing','collaborator'):
   for t in ('customers','sales_orders'):
    if u['owner_id']:counts[t]=c.execute('SELECT COUNT(*) FROM '+t+' WHERE owner_employee_id=?',(u['owner_id'],)).fetchone()[0]
    else:counts[t]=0
   for t in ('employees','assets','purchases','production_batches'):counts.pop(t,None)
  elif u['role']=='worker':counts={k:v for k,v in counts.items() if k=='production_batches'}
 return {'counts':counts,'time':now(),'scope':u['role']}

@app.post('/api/documents/intake')
async def document_intake(request:Request,file:UploadFile=File(...),source_kind:str='real'):
 u=allowed(request,'documents.write')
 if source_kind not in ('real','sample','imported'):raise HTTPException(422,'Sai nguồn')
 # No automatic OCR claim; safe upload + queue for extraction integration.
 content=await file.read(5_000_001)
 if len(content)>5_000_000:raise HTTPException(413,'Tệp quá lớn')
 if file.content_type not in ('image/jpeg','image/png','application/pdf'):raise HTTPException(415,'Chỉ nhận JPEG, PNG hoặc PDF')
 digest=hashlib.sha256(content).hexdigest();folder=ROOT/'data'/'uploads';folder.mkdir(parents=True,exist_ok=True)
 ext={'image/jpeg':'.jpg','image/png':'.png','application/pdf':'.pdf'}[file.content_type]
 name=digest+ext;target=folder/name
 with transaction() as c:
  existing=c.execute('SELECT id FROM documents WHERE sha256=? AND source_kind=?',(digest,source_kind)).fetchone()
  if existing:return {'id':existing['id'],'duplicate':True,'ocr_status':'pending'}
  target.write_bytes(content)
  rid=uid();c.execute('INSERT INTO documents(id,sha256,original_name,media_type,storage_path,received_at,uploaded_by,source_kind,ocr_status) VALUES(?,?,?,?,?,?,?,?,?)',(rid,digest,(file.filename or '')[:200],file.content_type,str(target),now(),u['username'],source_kind,'pending'))
  c.execute('INSERT INTO api_jobs(id,job_type,payload_json,created_at) VALUES(?,?,?,?)',(uid(),'document_extraction',json.dumps({'document_id':rid}),now()))
  audit(c,u,'document_intake','documents',rid,{'sha256':digest})
 return {'id':rid,'duplicate':False,'ocr_status':'pending','note':'Đã xếp hàng chờ nhận diện; kết quả cần xác minh trước khi ghi nghiệp vụ'}

@app.post('/api/agents/run')
def agent_run(request:Request):
 u=allowed(request,'costs.read')
 from .agents import evaluate
 return evaluate('manual',u['username'])

@app.get('/api/agents/history')
def agent_history(request:Request,limit:int=30):
 allowed(request,'costs.read')
 with connect() as c:return {'items':[dict(x) for x in c.execute('SELECT * FROM agent_evaluations ORDER BY created_at DESC LIMIT ?',(min(max(limit,1),100),))]}

@app.get('/api/audit')
def audit_history(request:Request,limit:int=100):
 u=actor(request)
 if u['role']!='director':raise HTTPException(403,'Không có quyền')
 with connect() as c:return {'items':[dict(x) for x in c.execute('SELECT * FROM audit_log ORDER BY at DESC LIMIT ?',(min(max(limit,1),500),))]}

@app.get('/api/documents/{document_id}/extraction')
def get_extraction(document_id:str,request:Request):
 u=actor(request)
 security.require(u,'documents.write')
 with connect() as c:
  doc=c.execute('SELECT id,uploaded_by,ocr_status,original_name FROM documents WHERE id=?',(document_id,)).fetchone()
  if not doc:raise HTTPException(404,'Không tìm thấy tài liệu')
  if u['role']!='director' and doc['uploaded_by']!=u['username']:raise HTTPException(403,'Chỉ xem chứng từ của mình')
  results=[dict(r) for r in c.execute('SELECT id,document_type,fields_json,confidence,model_name,review_status,created_at FROM extraction_results WHERE document_id=? ORDER BY created_at DESC',(document_id,))]
 return {'document':dict(doc),'extractions':results}

class ReviewBody(BaseModel):approved:bool;note:str=''
@app.post('/api/documents/{document_id}/review')
def review_extraction(document_id:str,body:ReviewBody,request:Request):
 u=actor(request)
 if u['role'] not in ('director','accountant','warehouse','hr','production_lead'):raise HTTPException(403,'Không có quyền xác minh chứng từ')
 with transaction() as c:
  row=c.execute('SELECT id FROM extraction_results WHERE document_id=? ORDER BY created_at DESC LIMIT 1',(document_id,)).fetchone()
  if not row:raise HTTPException(404,'Chưa có kết quả nhận diện')
  status='approved' if body.approved else 'rejected'
  c.execute('UPDATE extraction_results SET review_status=? WHERE id=?',(status,row['id']))
  c.execute('UPDATE documents SET ocr_status=? WHERE id=?',(status,document_id))
  audit(c,u,'document_review','documents',document_id,{'status':status,'note':body.note[:500]})
 return {'document_id':document_id,'status':status,'note':'Duyệt trích xuất không tự tạo giao dịch kế toán hoặc xuất kho'}

@app.get('/api/automation/status')
def automation_status(request:Request):
 u=actor(request)
 if u['role']!='director':raise HTTPException(403,'Không có quyền')
 with connect() as c:
  jobs=[dict(r) for r in c.execute('SELECT status,COUNT(*) count FROM api_jobs GROUP BY status')]
 return {
  'worker_enabled':os.getenv('SUNNY_ENABLE_WORKER','0')=='1',
  'vision_configured':bool(os.getenv('APIVN_API_KEY','').strip()),
  'vision_provider':'apivn',
  'vision_base_url':os.getenv('APIVN_BASE_URL','https://apivn.vn/v1'),
  'vision_model':os.getenv('SUNNY_VISION_MODEL','gpt-6-luna'),
  'jobs':jobs,
  'agent_mode':'periodic_rule_based',
  'ocr_mode':'vision_api_if_configured',
  'automatic_financial_posting':False,
 }


@app.get('/api/meta/modules')
def modules(request:Request):
 u=actor(request)
 return {'role':u['role'],'modules':[{'key':k,'can_read':('*' in security.ROLES.get(u['role'],set()) or v[0] in security.ROLES.get(u['role'],set())),'can_write':('*' in security.ROLES.get(u['role'],set()) or v[1] in security.ROLES.get(u['role'],set())),'required_fields':list(v[3]),'allowed_fields':list(v[2])} for k,v in TABLES.items()]}

@app.get('/api/documents/review-queue')
def review_queue(request:Request,limit:int=100):
 u=actor(request);security.require(u,'documents.write')
 with connect() as c:
  where='' if u['role']=='director' else ' WHERE d.uploaded_by=?'
  params=[] if u['role']=='director' else [u['username']]
  rows=c.execute('SELECT d.id,d.original_name,d.received_at,d.ocr_status,d.uploaded_by,e.document_type,e.fields_json,e.confidence,e.review_status FROM documents d LEFT JOIN extraction_results e ON e.document_id=d.id'+where+' ORDER BY d.received_at DESC LIMIT ?',(*params,min(max(limit,1),500))).fetchall()
 return {'items':[dict(x) for x in rows]}

@app.get('/api/kpi/overview')
def kpi_overview(request:Request,period_type:str='month'):
 u=actor(request)
 if period_type not in ('day','week','month','quarter','year'):raise HTTPException(422,'Kỳ KPI không hợp lệ')
 with connect() as c:
  rows=c.execute('SELECT k.code,k.title,m.employee_id,m.period_start,m.target,m.actual,m.verified,m.source_kind FROM kpi_measurements m JOIN kpi_definitions k ON k.id=m.kpi_id WHERE m.period_type=? ORDER BY m.period_start DESC LIMIT 200',(period_type,)).fetchall()
 result=[]
 for r in rows:
  d=dict(r)
  if u['role'] not in ('director','accountant','hr') and d['employee_id']!=u['owner_id']:continue
  d['status']='unverified' if not d['verified'] or d['actual'] is None else ('green' if d['actual']>=d['target'] else 'yellow' if d['actual']>=d['target']*.8 else 'red')
  result.append(d)
 return {'period_type':period_type,'items':result,'note':'Chưa có dữ liệu thì không giả lập kết quả'}

@app.get('/api/agents/status')
def agents_status(request:Request):
 allowed(request,'costs.read')
 with connect() as c:
  rows=[dict(x) for x in c.execute('SELECT agent,MAX(created_at) last_run,COUNT(*) run_count FROM agent_evaluations GROUP BY agent')]
 return {'items':rows,'mode':'rule_based','llm_autonomy':False}

from .compat import router as compat_router, init_compat
app.include_router(compat_router)
from .devices import router as devices_router, init_devices
app.include_router(devices_router)

# Secure HTTP response defaults for API and frontend.
@app.middleware('http')
async def security_headers(request,call_next):
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff'
 response.headers['X-Frame-Options']='DENY'
 response.headers['Referrer-Policy']='no-referrer'
 response.headers['Cache-Control']='no-store' if request.url.path.startswith('/api/') else 'no-cache'
 return response

# Static frontend served separately. Only /public is exposed; private source, data, uploads, logs remain inaccessible.



class JournalLine(BaseModel):
 account_code:str=Field(min_length=2,max_length=30)
 debit:int=Field(ge=0,le=10**14)
 credit:int=Field(ge=0,le=10**14)
class JournalEntry(BaseModel):
 request_id:str=Field(min_length=8,max_length=128)
 entry_date:str
 description:str=Field(min_length=3,max_length=500)
 source_document_id:str|None=None
 lines:list[JournalLine]=Field(min_length=2,max_length=100)

@app.post('/api/accounting/journal',status_code=201)
def post_journal(body:JournalEntry,request:Request):
 u=allowed(request,'purchases.write')
 debits=sum(x.debit for x in body.lines);credits=sum(x.credit for x in body.lines)
 if debits!=credits or debits<=0:raise HTTPException(422,'Bút toán không cân đối Nợ/Có')
 if any((x.debit>0)==(x.credit>0) for x in body.lines):raise HTTPException(422,'Mỗi dòng chỉ có một bên Nợ hoặc Có')
 try:datetime.date.fromisoformat(body.entry_date)
 except ValueError:raise HTTPException(422,'Ngày phải theo YYYY-MM-DD')
 with transaction() as c:
  from .accounting import check_period
  check_period(c,body.entry_date)
  old=idem(c,body.request_id,u,'journal');
  if old:return old
  if body.source_document_id and not c.execute('SELECT 1 FROM documents WHERE id=?',(body.source_document_id,)).fetchone():raise HTTPException(404,'Chứng từ không tồn tại')
  rid=uid()
  c.execute('INSERT INTO accounting_entries(id,request_id,entry_date,description,source_document_id,created_by,created_at) VALUES(?,?,?,?,?,?,?)',(rid,body.request_id,body.entry_date,body.description,body.source_document_id,u['username'],now()))
  for line in body.lines:c.execute('INSERT INTO accounting_lines(id,entry_id,account_code,debit,credit) VALUES(?,?,?,?,?)',(uid(),rid,line.account_code,line.debit,line.credit))
  result={'id':rid,'balanced':True,'debit':debits,'credit':credits,'status':'posted'}
  remember(c,body.request_id,u,'journal',result);audit(c,u,'journal_post','accounting_entries',rid,{'debit':debits,'credit':credits})
 return result

@app.get('/api/accounting/trial-balance')
def trial_balance(request:Request):
 allowed(request,'purchases.read')
 with connect() as c:
  rows=[dict(r) for r in c.execute('SELECT account_code,SUM(debit) debit,SUM(credit) credit FROM accounting_lines GROUP BY account_code ORDER BY account_code')]
 return {'accounts':rows,'total_debit':sum(r['debit'] for r in rows),'total_credit':sum(r['credit'] for r in rows),'source':'posted_journal_entries'}

@app.post('/api/evidence/verify-production/{batch_id}')
def verify_production(batch_id:str,request:Request):
 u=allowed(request,'production.read')
 with transaction() as c:
  b=c.execute('SELECT * FROM production_batches WHERE id=?',(batch_id,)).fetchone()
  if not b:raise HTTPException(404,'Không có ca sản xuất')
  errors=[]
  if b['source_kind']!='real':errors.append('Nguồn dữ liệu không phải thực tế')
  if b['output_pass'] is None or b['output_gross'] is None:errors.append('Thiếu số liệu sản lượng')
  elif b['output_pass']>b['output_gross']:errors.append('Sản lượng đạt vượt sản lượng tổng')
  # Không có ảnh/QR/cân liên kết thì không thể kết luận đã xác minh.
  status='unverified' if not errors else 'rejected'
  details={'errors':errors,'missing_evidence':['ảnh đồng hồ mét','phiếu cân','biên bản QC'],'note':'Chưa có chứng cứ liên kết; không tự đánh dấu hoàn thành'}
  c.execute('INSERT INTO evidence_checks VALUES(?,?,?,?,?,?,?)',(uid(),'production_batches',batch_id,'automatic_consistency',status,json.dumps(details,ensure_ascii=False),now()))
  audit(c,u,'evidence_check','production_batches',batch_id,{'result':status})
 return {'batch_id':batch_id,'result':status,**details}

from .operations import router as operations_router, init_operations
from .accounting import router as accounting_router, init_accounting
app.include_router(accounting_router)
app.include_router(operations_router)
from .resources import router as resources_router
app.include_router(resources_router)
from .erp_workflows import router as erp_router, init_erp
app.include_router(erp_router)
from .erp_registry import router as registry_router, init_registry
app.include_router(registry_router)
from .erp_integrity import router as integrity_router
app.include_router(integrity_router)
# Catch-all frontend mount MUST come last; otherwise it swallows API routes.
if (ROOT/'public').exists():app.mount('/',StaticFiles(directory=str(ROOT/'public'),html=True),name='frontend')
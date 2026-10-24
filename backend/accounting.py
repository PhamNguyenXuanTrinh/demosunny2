"""Accounting extensions: ledger controls, AR/AP, tax register, periods and reversal.
Amounts are integer VND. Reports are management reports, not certified statutory filings.
"""
import datetime, json, uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from .db import connect, transaction
from .security import current_user, require, now

router=APIRouter(prefix='/api/accounting',tags=['accounting'])

def auth(req,write=False):
 u=current_user(req);require(u,'purchases.write' if write else 'purchases.read');return u

def audit(c,u,action,entity,ident,payload=None):
 c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,new_json) VALUES(?,?,?,?,?,?)',(u['username'],action,entity,ident,now(),json.dumps(payload or {},ensure_ascii=False)))

def init_accounting():
 with connect() as c:c.executescript('''
 CREATE TABLE IF NOT EXISTS accounting_periods(period TEXT PRIMARY KEY,status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed')),closed_at TEXT,closed_by TEXT);
 CREATE TABLE IF NOT EXISTS accounting_accounts(code TEXT PRIMARY KEY,name TEXT NOT NULL,account_type TEXT NOT NULL CHECK(account_type IN ('asset','liability','equity','revenue','expense')),active INTEGER NOT NULL DEFAULT 1);
 CREATE TABLE IF NOT EXISTS accounting_parties(id TEXT PRIMARY KEY,code TEXT NOT NULL UNIQUE,name TEXT NOT NULL,kind TEXT NOT NULL CHECK(kind IN ('customer','supplier','both')),tax_id TEXT);
 CREATE TABLE IF NOT EXISTS accounting_open_items(id TEXT PRIMARY KEY,party_id TEXT NOT NULL REFERENCES accounting_parties(id),kind TEXT NOT NULL CHECK(kind IN ('receivable','payable')),reference TEXT NOT NULL UNIQUE,issue_date TEXT NOT NULL,due_date TEXT NOT NULL,amount INTEGER NOT NULL CHECK(amount>0),settled INTEGER NOT NULL DEFAULT 0 CHECK(settled>=0 AND settled<=amount),source_entry_id TEXT REFERENCES accounting_entries(id));
 CREATE TABLE IF NOT EXISTS accounting_settlements(id TEXT PRIMARY KEY,open_item_id TEXT NOT NULL REFERENCES accounting_open_items(id),amount INTEGER NOT NULL CHECK(amount>0),paid_on TEXT NOT NULL,reference TEXT NOT NULL UNIQUE,created_by TEXT NOT NULL,created_at TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS accounting_tax_lines(id TEXT PRIMARY KEY,document_ref TEXT NOT NULL UNIQUE,tax_period TEXT NOT NULL,kind TEXT NOT NULL CHECK(kind IN ('input','output')),taxable_amount INTEGER NOT NULL CHECK(taxable_amount>=0),vat_amount INTEGER NOT NULL CHECK(vat_amount>=0),tax_rate_bp INTEGER NOT NULL CHECK(tax_rate_bp BETWEEN 0 AND 10000),created_by TEXT NOT NULL,created_at TEXT NOT NULL);
 CREATE INDEX IF NOT EXISTS idx_accounting_open_items_party ON accounting_open_items(party_id,kind,due_date);
 CREATE INDEX IF NOT EXISTS idx_accounting_tax_period ON accounting_tax_lines(tax_period,kind);
 ''')

def date_value(s):
 try:return datetime.date.fromisoformat(s)
 except (ValueError,TypeError):raise HTTPException(422,'Ngày không hợp lệ, cần YYYY-MM-DD')

def check_period(c,day):
 period=day[:7]
 r=c.execute('SELECT status FROM accounting_periods WHERE period=?',(period,)).fetchone()
 if r and r['status']=='closed':raise HTTPException(409,'Kỳ kế toán đã khóa')

class Account(BaseModel):
 code:str=Field(min_length=2,max_length=30);name:str=Field(min_length=2,max_length=150);account_type:str
@router.post('/accounts',status_code=201)
def account_add(b:Account,req:Request):
 u=auth(req,True)
 if b.account_type not in ('asset','liability','equity','revenue','expense'):raise HTTPException(422,'Sai nhóm tài khoản')
 with transaction() as c:
  if c.execute('SELECT 1 FROM accounting_accounts WHERE code=?',(b.code,)).fetchone():raise HTTPException(409,'Trùng tài khoản')
  c.execute('INSERT INTO accounting_accounts VALUES(?,?,?,1)',(b.code,b.name,b.account_type));audit(c,u,'account_add','accounting_accounts',b.code)
 return {'code':b.code,'created':True}
@router.get('/accounts')
def accounts(req:Request):
 auth(req)
 with connect() as c:return {'items':[dict(x) for x in c.execute('SELECT * FROM accounting_accounts ORDER BY code')]}

class Party(BaseModel):
 code:str=Field(min_length=1,max_length=50);name:str=Field(min_length=2,max_length=200);kind:str;tax_id:str|None=None
@router.post('/parties',status_code=201)
def party_add(b:Party,req:Request):
 u=auth(req,True)
 if b.kind not in ('customer','supplier','both'):raise HTTPException(422,'Sai loại đối tượng')
 with transaction() as c:
  if c.execute('SELECT 1 FROM accounting_parties WHERE code=?',(b.code,)).fetchone():raise HTTPException(409,'Trùng mã')
  ident=str(uuid.uuid4());c.execute('INSERT INTO accounting_parties VALUES(?,?,?,?,?)',(ident,b.code,b.name,b.kind,b.tax_id));audit(c,u,'party_add','accounting_parties',ident)
 return {'id':ident}
@router.get('/parties')
def parties(req:Request):
 auth(req)
 with connect() as c:return {'items':[dict(x) for x in c.execute('SELECT * FROM accounting_parties ORDER BY code')]}

class OpenItem(BaseModel):
 party_id:str;kind:str;reference:str=Field(min_length=3,max_length=100);issue_date:str;due_date:str;amount:int=Field(gt=0,le=10**14);source_entry_id:str|None=None
@router.post('/open-items',status_code=201)
def create_item(b:OpenItem,req:Request):
 u=auth(req,True);issued=date_value(b.issue_date);due=date_value(b.due_date)
 if due<issued:raise HTTPException(422,'Hạn thanh toán trước ngày chứng từ')
 if b.kind not in ('receivable','payable'):raise HTTPException(422,'Sai loại công nợ')
 with transaction() as c:
  check_period(c,b.issue_date)
  party=c.execute('SELECT kind FROM accounting_parties WHERE id=?',(b.party_id,)).fetchone()
  if not party:raise HTTPException(404,'Đối tượng không tồn tại')
  if party['kind'] not in ('both','customer' if b.kind=='receivable' else 'supplier'):raise HTTPException(422,'Loại đối tượng không phù hợp')
  if b.source_entry_id and not c.execute('SELECT 1 FROM accounting_entries WHERE id=?',(b.source_entry_id,)).fetchone():raise HTTPException(404,'Bút toán nguồn không tồn tại')
  if c.execute('SELECT 1 FROM accounting_open_items WHERE reference=?',(b.reference,)).fetchone():raise HTTPException(409,'Trùng tham chiếu')
  ident=str(uuid.uuid4());c.execute('INSERT INTO accounting_open_items VALUES(?,?,?,?,?,?,?,?,?)',(ident,b.party_id,b.kind,b.reference,b.issue_date,b.due_date,b.amount,0,b.source_entry_id));audit(c,u,'open_item_add','accounting_open_items',ident)
 return {'id':ident,'outstanding':b.amount}
class Settlement(BaseModel):
 open_item_id:str;reference:str=Field(min_length=3,max_length=100);amount:int=Field(gt=0,le=10**14);paid_on:str
@router.post('/settlements',status_code=201)
def settle(b:Settlement,req:Request):
 u=auth(req,True);date_value(b.paid_on)
 with transaction() as c:
  check_period(c,b.paid_on)
  r=c.execute('SELECT * FROM accounting_open_items WHERE id=?',(b.open_item_id,)).fetchone()
  if not r:raise HTTPException(404,'Khoản công nợ không tồn tại')
  if b.amount>r['amount']-r['settled']:raise HTTPException(409,'Thanh toán vượt số dư')
  if c.execute('SELECT 1 FROM accounting_settlements WHERE reference=?',(b.reference,)).fetchone():raise HTTPException(409,'Trùng mã thanh toán')
  ident=str(uuid.uuid4());c.execute('INSERT INTO accounting_settlements VALUES(?,?,?,?,?,?,?)',(ident,b.open_item_id,b.amount,b.paid_on,b.reference,u['username'],now()))
  c.execute('UPDATE accounting_open_items SET settled=settled+? WHERE id=?',(b.amount,b.open_item_id));audit(c,u,'settlement_add','accounting_settlements',ident,{'amount':b.amount})
 return {'id':ident,'outstanding':r['amount']-r['settled']-b.amount,'journal_status':'not_automatically_posted'}
@router.get('/open-items')
def open_items(req:Request,kind:str|None=None,as_of:str|None=None):
 auth(req)
 if kind not in (None,'receivable','payable'):raise HTTPException(422,'Sai loại công nợ')
 day=date_value(as_of or datetime.date.today().isoformat()).isoformat()
 with connect() as c:
  rows=[dict(x) for x in c.execute('''SELECT i.*,p.code party_code,p.name party_name FROM accounting_open_items i JOIN accounting_parties p ON p.id=i.party_id WHERE (? IS NULL OR i.kind=?) ORDER BY i.due_date''',(kind,kind))]
 for r in rows:
  r['outstanding']=r['amount']-r['settled'];r['overdue']=r['outstanding']>0 and r['due_date']<day
 return {'items':rows,'total_outstanding':sum(x['outstanding'] for x in rows),'as_of':day}

class TaxLine(BaseModel):
 document_ref:str=Field(min_length=3,max_length=100);tax_period:str;kind:str;taxable_amount:int=Field(ge=0,le=10**14);vat_amount:int=Field(ge=0,le=10**14);tax_rate_bp:int=Field(ge=0,le=10000)
@router.post('/vat-lines',status_code=201)
def vat_add(b:TaxLine,req:Request):
 u=auth(req,True)
 try:datetime.date.fromisoformat(b.tax_period+'-01')
 except ValueError:raise HTTPException(422,'Kỳ thuế cần YYYY-MM')
 if b.kind not in ('input','output'):raise HTTPException(422,'Sai loại thuế')
 if abs(b.vat_amount*10000-b.taxable_amount*b.tax_rate_bp)>max(10000,b.taxable_amount//1000):raise HTTPException(422,'Tiền thuế không phù hợp thuế suất')
 with transaction() as c:
  check_period(c,b.tax_period+'-01')
  if c.execute('SELECT 1 FROM accounting_tax_lines WHERE document_ref=?',(b.document_ref,)).fetchone():raise HTTPException(409,'Trùng chứng từ thuế')
  ident=str(uuid.uuid4());c.execute('INSERT INTO accounting_tax_lines VALUES(?,?,?,?,?,?,?,?,?)',(ident,b.document_ref,b.tax_period,b.kind,b.taxable_amount,b.vat_amount,b.tax_rate_bp,u['username'],now()));audit(c,u,'vat_add','accounting_tax_lines',ident)
 return {'id':ident,'created':True}
@router.get('/vat-summary')
def vat_summary(req:Request,period:str):
 auth(req)
 try:datetime.date.fromisoformat(period+'-01')
 except ValueError:raise HTTPException(422,'Kỳ thuế cần YYYY-MM')
 with connect() as c:rows=[dict(x) for x in c.execute('SELECT kind,SUM(taxable_amount) taxable,SUM(vat_amount) vat,COUNT(*) documents FROM accounting_tax_lines WHERE tax_period=? GROUP BY kind',(period,))]
 amounts={r['kind']:r['vat'] for r in rows}
 return {'period':period,'items':rows,'net_output_minus_input':amounts.get('output',0)-amounts.get('input',0),'note':'Bảng tổng hợp nội bộ, chưa phải tờ khai thuế hợp lệ'}

class PeriodAction(BaseModel):period:str
@router.post('/periods/close')
def close_period(b:PeriodAction,req:Request):
 u=auth(req,True)
 if u['role']!='director':raise HTTPException(403,'Chỉ giám đốc khóa kỳ')
 try:datetime.date.fromisoformat(b.period+'-01')
 except ValueError:raise HTTPException(422,'Kỳ cần YYYY-MM')
 with transaction() as c:
  if c.execute("SELECT status FROM accounting_periods WHERE period=?",(b.period,)).fetchone() and c.execute('SELECT status FROM accounting_periods WHERE period=?',(b.period,)).fetchone()['status']=='closed':raise HTTPException(409,'Kỳ đã khóa')
  c.execute("INSERT INTO accounting_periods(period,status,closed_at,closed_by) VALUES(?,'closed',?,?) ON CONFLICT(period) DO UPDATE SET status='closed',closed_at=excluded.closed_at,closed_by=excluded.closed_by",(b.period,now(),u['username']));audit(c,u,'period_close','accounting_periods',b.period)
 return {'period':b.period,'status':'closed'}
@router.get('/periods')
def periods(req:Request):
 auth(req)
 with connect() as c:return {'items':[dict(x) for x in c.execute('SELECT * FROM accounting_periods ORDER BY period DESC')]}
@router.get('/financial-summary')
def financial_summary(req:Request,start:str,end:str):
 auth(req);date_value(start);date_value(end)
 if start>end:raise HTTPException(422,'Ngày bắt đầu lớn hơn ngày kết thúc')
 with connect() as c:
  rows=[dict(x) for x in c.execute('''SELECT l.account_code,COALESCE(a.account_type,'unclassified') account_type,SUM(l.debit) debit,SUM(l.credit) credit FROM accounting_lines l JOIN accounting_entries e ON e.id=l.entry_id LEFT JOIN accounting_accounts a ON a.code=l.account_code WHERE e.status='posted' AND e.entry_date BETWEEN ? AND ? GROUP BY l.account_code,a.account_type ORDER BY l.account_code''',(start,end))]
 totals={k:0 for k in ('revenue','expense','asset','liability','equity','unclassified')}
 for r in rows:totals[r['account_type']]+=r['credit']-r['debit'] if r['account_type'] in ('revenue','liability','equity') else r['debit']-r['credit']
 return {'start':start,'end':end,'accounts':rows,'totals':totals,'operating_result':totals['revenue']-totals['expense'],'balanced':sum(x['debit'] for x in rows)==sum(x['credit'] for x in rows),'note':'Báo cáo quản trị; chưa có bút toán kết chuyển và chuẩn hóa đầy đủ VAS'}

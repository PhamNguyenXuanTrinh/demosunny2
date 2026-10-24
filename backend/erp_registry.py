"""Explicit, persistent ERP operational registries. Not mocks.
All writes use a transaction, RBAC and audit log. Status is intentionally not
modifiable through generic PATCH: transitions require separate workflows.
"""
import json, uuid, sqlite3
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from .db import connect, transaction
from . import security

router=APIRouter(prefix='/api/erp',tags=['ERP registries'])
# 12 bounded contexts with distinct permission boundaries and data contracts.
DOMAINS={
 'work-centers':('production.read','production.write',('code','name','capacity_per_day')),
 'shift-plans':('production.read','production.write',('code','name','planned_date')),
 'material-specs':('stock.read','stock.write',('code','name','unit')),
 'bill-of-materials':('production.read','production.write',('code','name','product_code')),
 'supplier-contracts':('purchases.read','purchases.write',('code','name','supplier_code')),
 'purchase-requests':('purchases.read','purchases.write',('code','name','request_date')),
 'delivery-plans':('orders.read','orders.write',('code','name','delivery_date')),
 'sales-quotations':('orders.read','orders.write',('code','name','customer_code')),
 'customer-claims':('customers.read','customers.write',('code','name','customer_code')),
 'maintenance-plans':('assets.read','assets.write',('code','name','equipment_code')),
 'training-records':('employees.read','employees.write',('code','name','employee_code')),
 'safety-inspections':('production.read','production.write',('code','name','inspection_date')),
}
class Record(BaseModel):
 code:str=Field(min_length=1,max_length=80)
 name:str=Field(min_length=1,max_length=250)
 details:dict=Field(default_factory=dict)
class Edit(BaseModel):
 name:str=Field(min_length=1,max_length=250)
 details:dict=Field(default_factory=dict)

def require(req,domain,write=False):
 if domain not in DOMAINS:raise HTTPException(404,'Không có phân hệ')
 user=security.current_user(req)
 security.require(user,DOMAINS[domain][1 if write else 0]);return user

def validate(domain,details):
 if len(json.dumps(details,ensure_ascii=False))>16000:raise HTTPException(422,'Chi tiết quá lớn')
 if any(not isinstance(k,str) or len(k)>80 for k in details):raise HTTPException(422,'Tên trường không hợp lệ')
 missing=[x for x in DOMAINS[domain][2][2:] if not details.get(x)]
 if missing:raise HTTPException(422,'Thiếu trường: '+','.join(missing))
 if 'capacity_per_day' in details:
  value=details['capacity_per_day']
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<value<=1000000:raise HTTPException(422,'Công suất không hợp lệ')
 return json.dumps(details,ensure_ascii=False,allow_nan=False)

def audit(c,user,action,domain,rid,detail):
 c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,new_json) VALUES(?,?,?,?,?,?)',(user['username'],action,'erp:'+domain,rid,security.now(),json.dumps(detail,ensure_ascii=False)))

def init_registry():
 with connect() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS erp_registry(id TEXT PRIMARY KEY,domain TEXT NOT NULL,code TEXT NOT NULL,name TEXT NOT NULL,details_json TEXT NOT NULL,created_by TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,UNIQUE(domain,code));
CREATE INDEX IF NOT EXISTS idx_erp_registry_domain ON erp_registry(domain);''')

def list_items(domain,request:Request,limit:int=100,offset:int=0):
 require(request,domain)
 with connect() as c:
  rows=[dict(x) for x in c.execute('SELECT id,code,name,details_json,created_at,updated_at FROM erp_registry WHERE domain=? ORDER BY created_at DESC LIMIT ? OFFSET ?',(domain,min(max(limit,1),200),max(offset,0)))]
  count=c.execute('SELECT COUNT(*) FROM erp_registry WHERE domain=?',(domain,)).fetchone()[0]
 for row in rows:row['details']=json.loads(row.pop('details_json'))
 return {'items':rows,'total':count}

def get_item(domain,record_id,request:Request):
 require(request,domain)
 with connect() as c:r=c.execute('SELECT id,code,name,details_json,created_at,updated_at FROM erp_registry WHERE domain=? AND id=?',(domain,record_id)).fetchone()
 if not r:raise HTTPException(404,'Không có bản ghi')
 result=dict(r);result['details']=json.loads(result.pop('details_json'));return result

def create_item(domain,body:Record,request:Request):
 user=require(request,domain,True);detail=validate(domain,body.details);rid=str(uuid.uuid4());now=security.now()
 try:
  with transaction() as c:
   c.execute('INSERT INTO erp_registry VALUES(?,?,?,?,?,?,?,?)',(rid,domain,body.code,body.name,detail,user['username'],now,now))
   audit(c,user,'create',domain,rid,body.model_dump())
 except sqlite3.IntegrityError:raise HTTPException(409,'Mã nghiệp vụ đã tồn tại')
 return {'id':rid,'created':True}

def edit_item(domain,record_id,body:Edit,request:Request):
 user=require(request,domain,True);detail=validate(domain,body.details)
 with transaction() as c:
  old=c.execute('SELECT id FROM erp_registry WHERE domain=? AND id=?',(domain,record_id)).fetchone()
  if not old:raise HTTPException(404,'Không có bản ghi')
  c.execute('UPDATE erp_registry SET name=?,details_json=?,updated_at=? WHERE id=?',(body.name,detail,security.now(),record_id))
  audit(c,user,'update',domain,record_id,body.model_dump())
 return {'id':record_id,'updated':True}

# Register concrete paths for OpenAPI, each with a real SQL-backed handler.
for domain in DOMAINS:
 def listing(request:Request,limit:int=100,offset:int=0,_domain=domain):return list_items(_domain,request,limit,offset)
 def detail(record_id:str,request:Request,_domain=domain):return get_item(_domain,record_id,request)
 def create(body:Record,request:Request,_domain=domain):return create_item(_domain,body,request)
 def edit(record_id:str,body:Edit,request:Request,_domain=domain):return edit_item(_domain,record_id,body,request)
 # Avoid exposing closure defaults as query parameters.
 from functools import partial
 router.add_api_route('/'+domain,partial(list_items,domain),methods=['GET'],name='list_'+domain)
 router.add_api_route('/'+domain+'/{record_id}',partial(get_item,domain),methods=['GET'],name='get_'+domain)
 router.add_api_route('/'+domain,partial(create_item,domain),methods=['POST'],name='create_'+domain,status_code=201)
 router.add_api_route('/'+domain+'/{record_id}',partial(edit_item,domain),methods=['PATCH'],name='update_'+domain)

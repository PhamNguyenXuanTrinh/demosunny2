"""Database-backed resource operations. Whitelist, RBAC, audit, and schema-aware validation."""
import json,sqlite3,uuid
from fastapi import APIRouter,Request,HTTPException
from . import security
from .db import connect,transaction
router=APIRouter(prefix='/api/resources',tags=['resources'])
# Permission pairs are deliberate; new resources require explicit authorization review.
RESOURCES={
 'suppliers':('purchases.read','purchases.write'),
 'products':('orders.read','orders.write'),
 'order_lines':('orders.read','orders.write'),
 'receipts':('orders.read','orders.write'),
 'customer_interactions':('customers.read','customers.write'),
 'qc_inspections':('production.read','qc.write'),
 'attendance':('employees.read','employees.write'),
 'payroll_drafts':('employees.read','employees.write'),
 'kpi_definitions':('duties.read','duties.write'),
 'kpi_measurements':('duties.read','duties.write'),
 'meters':('production.read','production.write'),
 'meter_readings':('production.read','production.write'),
 'asset_events':('assets.read','assets.write'),
 'cost_opportunities':('costs.read','costs.write'),
 'incidents':('incidents.write','incidents.write'),
 'stock_lots':('stock.read','stock.write'),
}
# Immutable evidence, balances and verified flags cannot be edited via generic resource routes.
READ_ONLY={'payroll_drafts','receipts','qc_inspections','meter_readings','kpi_measurements','stock_lots','asset_events'}
PROTECTED={'amount','net_salary','gross_salary','total_salary','salary','tax_amount','bank_account','verified','source_kind','status','evidence_document_id','source_document_id','verified_saving','verified_loss','approved_by','decision','password_hash','role','owner_id'}
def check(resource,request,write=False):
 if resource not in RESOURCES:raise HTTPException(404,'Phân hệ không tồn tại')
 user=security.current_user(request)
 security.require(user,RESOURCES[resource][1 if write else 0])
 if write and resource in READ_ONLY:raise HTTPException(403,'Chứng từ cần quy trình nghiệp vụ chuyên biệt')
 return user

def columns(c,resource):
 return {r['name']:dict(r) for r in c.execute('PRAGMA table_info("'+resource+'")')}

def valid_body(c,resource,body):
 if not isinstance(body,dict) or not body:raise HTTPException(422,'Dữ liệu không hợp lệ')
 schema=columns(c,resource)
 invalid=set(body)-set(schema)
 if invalid:raise HTTPException(422,'Trường không tồn tại: '+','.join(sorted(invalid)))
 forbidden=set(body)&(PROTECTED|{'id','created_at'})
 if forbidden:raise HTTPException(422,'Trường cần quy trình xác minh: '+','.join(sorted(forbidden)))
 for name,value in body.items():
  if value is not None and isinstance(value,(dict,list)):raise HTTPException(422,'Không nhận đối tượng lồng nhau')
  if isinstance(value,str) and len(value)>4096:raise HTTPException(422,'Dữ liệu quá dài')
 return body

@router.get('/{resource}')
def list_resource(resource:str,request:Request,limit:int=50,offset:int=0):
 check(resource,request)
 limit=max(1,min(limit,200));offset=max(0,offset)
 with connect() as c:
  items=[dict(r) for r in c.execute('SELECT * FROM "'+resource+'" ORDER BY rowid DESC LIMIT ? OFFSET ?',(limit,offset))]
  total=c.execute('SELECT COUNT(*) FROM "'+resource+'"').fetchone()[0]
 return {'items':items,'total':total,'limit':limit,'offset':offset}

@router.get('/{resource}/{record_id}')
def get_resource(resource:str,record_id:str,request:Request):
 check(resource,request)
 with connect() as c: row=c.execute('SELECT * FROM "'+resource+'" WHERE id=?',(record_id,)).fetchone()
 if not row:raise HTTPException(404,'Không có bản ghi')
 return dict(row)

@router.post('/{resource}',status_code=201)
def create_resource(resource:str,body:dict,request:Request):
 user=check(resource,request,True)
 rid=str(uuid.uuid4())
 try:
  with transaction() as c:
   valid_body(c,resource,body)
   schema=columns(c,resource)
   fields=dict(body)
   if 'created_at' in schema:fields['created_at']=security.now()
   names=['id',*fields]
   c.execute('INSERT INTO "'+resource+'" ('+','.join('"'+x+'"' for x in names)+') VALUES ('+','.join('?' for _ in names)+')',[rid,*fields.values()])
   c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,new_json) VALUES(?,?,?,?,?,?)',(user['username'],'create',resource,rid,security.now(),json.dumps(fields,ensure_ascii=False)))
 except sqlite3.IntegrityError as exc:raise HTTPException(409,'Trùng dữ liệu hoặc thiếu liên kết') from exc
 return {'id':rid,'created':True}

@router.patch('/{resource}/{record_id}')
def update_resource(resource:str,record_id:str,body:dict,request:Request):
 user=check(resource,request,True)
 try:
  with transaction() as c:
   valid_body(c,resource,body)
   old=c.execute('SELECT * FROM "'+resource+'" WHERE id=?',(record_id,)).fetchone()
   if not old:raise HTTPException(404,'Không có bản ghi')
   c.execute('UPDATE "'+resource+'" SET '+','.join('"'+k+'"=?' for k in body)+' WHERE id=?',[*body.values(),record_id])
   c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,old_json,new_json) VALUES(?,?,?,?,?,?,?)',(user['username'],'update',resource,record_id,security.now(),json.dumps(dict(old),ensure_ascii=False),json.dumps(body,ensure_ascii=False)))
 except sqlite3.IntegrityError as exc:raise HTTPException(409,'Dữ liệu không hợp lệ hoặc trùng') from exc
 return {'id':record_id,'updated':True}

import os,tempfile,importlib,sys
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
@pytest.fixture()
def api(tmp_path,monkeypatch):
 monkeypatch.setenv('SUNNY_DB_PATH',str(tmp_path/'test.sqlite3'))
 monkeypatch.setenv('SUNNY_ADMIN_PASSWORD','VeryStrongPasswordForTests2026!')
 from backend import db,security
 db.DB=tmp_path/'test.sqlite3'
 db.init();security.bootstrap()
 from backend.main import app
 with TestClient(app) as client:
  r=client.post('/api/auth/login',json={'username':'admin','password':'VeryStrongPasswordForTests2026!'})
  assert r.status_code==200,r.text
  token=r.json()['access_token']
  yield client,{'Authorization':'Bearer '+token}

def test_security(api):
 c,h=api
 assert c.get('/api/v1/customers').status_code==401
 assert c.get('/archive/V86_GOC_BAT_BIEN.html').status_code in (404,401)
 assert c.get('/data/sunny.sqlite3').status_code in (404,401)
 assert c.get('/api/dashboard',headers=h).status_code==200

def test_customer_and_order(api):
 c,h=api
 customer=c.post('/api/v1/customers',headers=h,json={'customer_code':'C-001','name':'Khách thử'});assert customer.status_code==201,customer.text
 order=c.post('/api/v1/sales_orders',headers=h,json={'order_code':'O-001','customer_id':customer.json()['id'],'ordered_at':'2026-10-24T10:00:00'});assert order.status_code==201,order.text
 assert c.get('/api/v1/sales_orders',headers=h).json()['total']==1
 assert c.post('/api/v1/customers',headers=h,json={'customer_code':'C-001','name':'Trùng'}).status_code==409

def test_stock_idempotent_and_40pct(api):
 c,h=api
 from backend.db import transaction
 with transaction() as db:db.execute("INSERT INTO warehouses(id,name) VALUES('W1','Kho')")
 item=c.post('/api/v1/inventory_items',headers=h,json={'sku':'XM','name':'Xi măng','category':'production','unit':'kg','standard_qty':100});assert item.status_code==201,item.text
 i=item.json()['id']
 def mv(key,kind,q):return c.post('/api/stock/movements',headers=h,json={'request_id':key,'item_id':i,'warehouse_id':'W1','kind':kind,'quantity':q})
 assert mv('RECEIPT00001','in',100).status_code==200
 assert mv('ISSUE0000001','out',60).json()['warning_40pct'] is True
 assert mv('ISSUE0000001','out',60).json()['stock_after']==40
 assert mv('ISSUE0000002','out',41).status_code==409
 assert c.get('/api/stock/summary',headers=h).json()['items'][0]['stock']==40
 assert c.post('/api/agents/run',headers=h).json()['results']['Kho']['count']==1

def test_purchases_costs_and_validation(api):
 c,h=api
 body={'request_id':'PURCHASE0001','purchased_on':'2026-10-24','classification':'prepaid','total_amount':1200000}
 a=c.post('/api/purchases/commit',headers=h,json=body);assert a.status_code==200,a.text
 b=c.post('/api/purchases/commit',headers=h,json=body);assert a.json()==b.json()
 assert c.post('/api/purchases/commit',headers=h,json={**body,'request_id':'PURCHASE0002','total_amount':-1}).status_code==422
 assert c.get('/api/costs/3-percent',headers=h).json()['total_cost']==0

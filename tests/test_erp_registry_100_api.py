import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.erp_registry import DOMAINS

def test_12_domain_registries_http_roundtrip(tmp_path,monkeypatch):
 from backend import db
 monkeypatch.setattr(db,"DB",tmp_path/"registry.sqlite3")
 with TestClient(app) as client:
  login=client.post('/api/auth/login',json={'username':os.getenv('SUNNY_ADMIN_USER','admin'),'password':os.environ['SUNNY_ADMIN_PASSWORD']})
  assert login.status_code==200,login.text
  headers={'Authorization':'Bearer '+login.json()['access_token']}
  for i,(domain,(_,_,required)) in enumerate(DOMAINS.items()):
   data={field:12000 if field=='capacity_per_day' else '2026-10-25' if 'date' in field else 'DEMO' for field in required[2:]}
   code=f'TEST-{domain}-{i}'
   created=client.post(f'/api/erp/{domain}',headers=headers,json={'code':code,'name':'Kiểm thử','details':data})
   assert created.status_code==201,(domain,created.text)
   rid=created.json()['id']
   assert client.get(f'/api/erp/{domain}/{rid}',headers=headers).status_code==200
   assert client.get(f'/api/erp/{domain}',headers=headers).status_code==200
   updated=client.patch(f'/api/erp/{domain}/{rid}',headers=headers,json={'name':'Đã cập nhật','details':data})
   assert updated.status_code==200,(domain,updated.text)
   assert client.get(f'/api/erp/{domain}/{rid}',headers=headers).json()['name']=='Đã cập nhật'
   assert client.post(f'/api/erp/{domain}',headers=headers,json={'code':code,'name':'Trùng','details':data}).status_code==409
   assert client.get(f'/api/erp/{domain}').status_code==401

def test_api_count_and_openapi_contract():
 with TestClient(app) as client:
  pairs={(method,route.path) for route in app.routes for method in getattr(route,'methods',set()) if route.path.startswith('/api/') and method not in ('HEAD','OPTIONS')}
  assert len(pairs)>=100
  response=client.get('/api/openapi.json')
  assert response.status_code==200
  paths=response.json()['paths']
  assert '/api/erp/work-centers' in paths

import os
from fastapi.testclient import TestClient
from backend.main import app

def test_integrity_auth_required():
 with TestClient(app) as client:
  for endpoint in ('dashboard','production-balance','journal-balance','unverified-production','pending-approvals','missing-source-documents'):
   assert client.get('/api/erp/integrity/'+endpoint).status_code==401

def test_integrity_director_read(tmp_path,monkeypatch):
 from backend import db
 monkeypatch.setattr(db,"DB",tmp_path/"integrity_test.sqlite3")
 with TestClient(app) as client:
  response=client.post('/api/auth/login',json={'username':'admin','password':os.environ['SUNNY_ADMIN_PASSWORD']})
  assert response.status_code==200
  headers={'Authorization':'Bearer '+response.json()['access_token']}
  for endpoint in ('dashboard','production-balance','journal-balance','unverified-production','pending-approvals','missing-source-documents'):
   result=client.get('/api/erp/integrity/'+endpoint,headers=headers)
   assert result.status_code==200,(endpoint,result.text)
  assert client.get('/api/erp/integrity/dashboard',headers=headers).json()['completion_certified'] is False

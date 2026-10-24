import os
from fastapi.testclient import TestClient
from backend.main import app

def test_erp_workflows_end_to_end(tmp_path,monkeypatch):
    from backend import db
    monkeypatch.setenv('SUNNY_ADMIN_PASSWORD','TestingPassword12345')
    monkeypatch.setattr(db,'DB',tmp_path/'v98.sqlite3')
    with TestClient(app) as client:
        login=client.post('/api/auth/login',json={'username':os.getenv('SUNNY_ADMIN_USER','admin'),'password':os.environ['SUNNY_ADMIN_PASSWORD']})
        assert login.status_code==200,login.text
        headers={'Authorization':'Bearer '+login.json()['access_token']}
        response=client.post('/api/erp/approvals',headers=headers,json={'kind':'expense','reference_id':'test-v98-'+__import__('uuid').uuid4().hex,'amount_vnd':150000,'justification':'Kiểm thử nghiệp vụ phê duyệt'})
        assert response.status_code==201,response.text
        rid=response.json()['id']
        assert client.get('/api/erp/approvals',headers=headers).status_code==200
        assert client.get('/api/erp/approvals/'+rid+'/history',headers=headers).json()['items'][0]['action']=='requested'
        # Segregation of duties: requester cannot approve own expense.
        assert client.post('/api/erp/approvals/'+rid+'/decision',headers=headers,json={'decision':'approved','note':'Kiểm tra phân quyền'}).status_code==403
        for period in ['day','week','month','quarter','year']:
            summary=client.get('/api/erp/production/summary',params={'period':period,'date':'2026-10-25'},headers=headers)
            assert summary.status_code==200,summary.text
            assert summary.json()['period']==period
        assert client.get('/api/erp/approvals').status_code==401
        assert client.get('/api/erp/production/summary',params={'period':'invalid'},headers=headers).status_code==422

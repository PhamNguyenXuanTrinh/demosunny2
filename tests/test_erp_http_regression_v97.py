"""Regression tests for HTTP routing and fail-closed resource security."""
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
        yield client,{'Authorization':'Bearer '+r.json()['access_token']}

def test_resources_routes_are_reachable(api):
    client, headers = api
    result=client.get('/api/resources/products',headers=headers)
    assert result.status_code==200, result.text
    assert 'items' in result.json()
    assert client.get('/api/resources/products').status_code==401

def test_resources_reject_unapproved_fields(api):
    client,headers=api
    result=client.post('/api/resources/products',headers=headers,json={'evil_column':'test'})
    assert result.status_code==422, result.text

def test_payroll_drafts_not_generic_writable(api):
    client,headers=api
    result=client.post('/api/resources/payroll_drafts',headers=headers,json={'gross_salary':999999})
    assert result.status_code==403, result.text

def test_openapi_documents_real_routes(api):
    client,headers=api
    schema=client.get('/api/openapi.json').json()
    assert '/api/resources/{resource}' in schema['paths']
    assert '/api/auth/login' in schema['paths']

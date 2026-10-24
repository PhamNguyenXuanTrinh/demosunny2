import pathlib
from fastapi.testclient import TestClient
from backend.main import app

def test_legacy_is_visibly_marked():
    html=(pathlib.Path(__file__).resolve().parents[1]/'public'/'legacy.html').read_text()
    assert 'url=/index.html' in html and 'dữ liệu thật' in html

def test_coverage_requires_login():
    r=TestClient(app).get('/api/integration/coverage')
    assert r.status_code==401

def test_openapi_contains_coverage():
    assert '/api/integration/coverage' in app.openapi()['paths']

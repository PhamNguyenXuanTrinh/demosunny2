"""Contract tests for the live UI, not for the separate unintegrated legacy UI."""
import re
from pathlib import Path
from fastapi.routing import APIRoute
from backend.main import app
ROOT=Path(__file__).resolve().parents[1]

def test_live_frontend_calls_have_backend_routes():
    html=(ROOT/'public'/'app.html').read_text(encoding='utf-8')
    routes={r.path for r in app.routes if isinstance(r,APIRoute)}
    paths=set(re.findall(r"api\('(/[^'\"?]+)",html))
    paths.update(re.findall(r"fetch\('(/api/[^'\"?]+)",html))
    missing=[]
    for path in paths:
        full=path if path.startswith('/api/') else '/api'+path
        if full in routes:continue
        if full.startswith('/api/v1/') and '/api/v1/{table}' in routes:continue
        missing.append(full)
    assert not missing, f'UI API endpoints missing: {missing}'

def test_frontend_has_auth_and_no_hardcoded_secret():
    html=(ROOT/'public'/'app.html').read_text(encoding='utf-8')
    assert '/api/auth/login' in html
    assert "Authorization:'Bearer '+token" in html
    assert 'sk-proj-' not in html

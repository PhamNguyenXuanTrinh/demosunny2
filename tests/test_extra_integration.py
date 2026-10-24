from test_api import api

def test_real_ui_served_and_auth_protected(api):
    c,h=api
    assert c.get('/').status_code==200
    assert c.get('/api/meta/modules').status_code==401
    assert c.get('/api/meta/modules',headers=h).status_code==200
    assert c.get('/api/automation/status',headers=h).status_code==200
    assert c.get('/api/agents/status',headers=h).status_code==200
    assert c.get('/api/kpi/overview?period_type=day',headers=h).status_code==200
    assert c.get('/api/documents/review-queue',headers=h).status_code==200

def test_no_fake_ai_and_legacy_stock_rejected(api):
    c,h=api
    r=c.post('/api/ask',headers=h,json={'question':'Doanh thu?'})
    assert r.status_code==200 and r.json()['verified'] is False
    assert c.post('/api/stock',headers=h,json={}).status_code==409

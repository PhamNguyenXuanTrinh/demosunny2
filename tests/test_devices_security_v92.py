import json,datetime
from test_api import api

def test_device_auth_replay_and_scope(api,monkeypatch):
 c,h=api
 monkeypatch.setenv('SUNNY_DEVICE_TOKENS_JSON',json.dumps({'SCALE01':'A'*32}))
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 payload={'device_id':'SCALE01','request_id':'device-reading-0001','kind':'scale_kg','value':250.5,'unit':'kg','observed_at':stamp}
 assert c.post('/api/devices/readings',json=payload).status_code==401
 ok=c.post('/api/devices/readings',headers={'X-Device-Token':'A'*32},json=payload)
 assert ok.status_code==201,ok.text
 assert c.post('/api/devices/readings',headers={'X-Device-Token':'A'*32},json=payload).json()['duplicate']
 assert c.post('/api/devices/readings',headers={'X-Device-Token':'A'*32},json={**payload,'value':251}).status_code==409
 assert len(c.get('/api/devices/readings',headers=h).json()['items'])==1
 assert c.post('/api/devices/readings',headers={'X-Device-Token':'A'*32},json={**payload,'request_id':'device-reading-0002','value':-1}).status_code==422

def test_security_headers(api):
 c,h=api
 r=c.get('/api/health')
 assert r.headers['x-content-type-options']=='nosniff'
 assert r.headers['x-frame-options']=='DENY'
 assert r.headers['cache-control']=='no-store'
 assert c.get('/api/devices/readings').status_code==401

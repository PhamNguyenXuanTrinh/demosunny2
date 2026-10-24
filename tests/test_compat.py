from test_api import api
def test_legacy_api_auth_and_realtime(api):
 c,h=api
 assert c.get('/api/realtime').status_code==401
 r=c.get('/api/realtime',headers=h)
 assert r.status_code==200,r.text
 assert r.json()['materials']==[]
 assert c.get('/api/integration/coverage',headers=h).json()['missing']==[]

def test_electric_idempotency(api):
 c,h=api
 body={'zone':'Máy chính','kwh':10,'unit_price':2000,'request_id':'electric-unique-001'}
 a=c.post('/api/electric',headers=h,json=body);assert a.status_code==200,a.text
 b=c.post('/api/electric',headers=h,json=body);assert b.status_code==200 and b.json()['duplicate']
 assert c.get('/api/realtime',headers=h).json()['electric_cost']==20000

def test_marketing_flow(api):
 c,h=api
 campaign=c.post('/api/marketing/create',headers=h,json={'kind':'campaign','name':'Thử nghiệm','channel':'TikTok','budget':5000})
 assert campaign.status_code==200,campaign.text
 lead=c.post('/api/marketing/create',headers=h,json={'kind':'lead','customer_name':'Khách thử','campaign_id':campaign.json()['id']})
 assert lead.status_code==200,lead.text
 data=c.get('/api/marketing',headers=h)
 assert data.status_code==200,data.text
 assert data.json()['metrics']['leads']==1
 assert c.post('/api/marketing/seed',headers=h,json={}).status_code==409

def test_ai_no_fake_claim(api):
 c,h=api
 assert c.get('/api/status',headers=h).json()['model_connected'] is False
 r=c.post('/api/ask',headers=h,json={'question':'Báo cáo KPI'})
 assert r.status_code==200 and r.json()['verified'] is False

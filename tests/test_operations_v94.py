from test_api import api

def test_operations_auth_and_accounting(api):
 c,h=api
 for route in ('/api/operations/alerts','/api/operations/accounting/ledger','/api/operations/device-bindings'):
  assert c.get(route).status_code==401
  r=c.get(route,headers=h)
  assert r.status_code==200,r.text
 assert c.post('/api/operations/device-bindings',headers=h,json={'device_id':'SCALE-A','kind':'scale_kg'}).status_code==201
 assert c.post('/api/operations/device-bindings',headers=h,json={'device_id':'SCALE-A','kind':'scale_kg'}).status_code==409
 assert len(c.get('/api/operations/device-bindings',headers=h).json()['items'])==1

def test_evidence_cannot_self_certify(api):
 c,h=api
 r=c.post('/api/v1/production_batches',headers=h,json={'batch_code':'B-94','shift_date':'2026-10-24','output_gross':100,'output_pass':95,'output_reject':5,'source_kind':'real'})
 assert r.status_code==201,r.text
 bid=r.json()['id']
 verify=c.post('/api/operations/verify/'+bid,headers=h)
 assert verify.status_code==200,verify.text
 assert verify.json()['verified'] is False
 assert 'Thiếu bằng chứng' in ' '.join(verify.json()['reasons'])
 assert c.post('/api/operations/evidence',headers=h,json={'entity_type':'production_batches','entity_id':bid,'document_id':'missing','evidence_type':'qc_report'}).status_code==404

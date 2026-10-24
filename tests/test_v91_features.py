from test_api import api

def test_journal_balance_and_idempotency(api):
 c,h=api
 payload={'request_id':'JOURNAL-20261024-0001','entry_date':'2026-10-24','description':'Mua vật tư','lines':[{'account_code':'152','debit':100000,'credit':0},{'account_code':'111','debit':0,'credit':100000}]}
 a=c.post('/api/accounting/journal',json=payload,headers=h)
 assert a.status_code==201,a.text
 assert c.post('/api/accounting/journal',json=payload,headers=h).json()['id']==a.json()['id']
 bal=c.get('/api/accounting/trial-balance',headers=h).json()
 assert bal['total_debit']==bal['total_credit']==100000
 payload['request_id']='JOURNAL-20261024-0002';payload['lines'][1]['credit']=90000
 assert c.post('/api/accounting/journal',json=payload,headers=h).status_code==422

def test_evidence_does_not_self_approve(api):
 c,h=api
 p=c.post('/api/v1/production_batches',headers=h,json={'batch_code':'B91','shift_date':'2026-10-24','output_gross':100,'output_pass':98,'output_reject':2,'source_kind':'real'})
 assert p.status_code==201,p.text
 result=c.post('/api/evidence/verify-production/'+p.json()['id'],headers=h)
 assert result.status_code==200
 assert result.json()['result']=='unverified'
 assert len(result.json()['missing_evidence'])==3

def test_pdf_conversion_without_remote_call(tmp_path,monkeypatch):
 import fitz
 from backend import automation
 pdf=fitz.open();pdf.new_page().insert_text((72,72),'Invoice 123')
 path=tmp_path/'doc.pdf';pdf.save(path);pdf.close()
 monkeypatch.setenv('OPENAI_API_KEY','dummy-for-mocked-test')
 import urllib.request
 def fake(req,timeout=0):
  import json
  data=json.loads(req.data)
  parts=data['messages'][0]['content']
  assert any(x.get('type')=='image_url' for x in parts)
  class Response:
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def read(self):return json.dumps({'choices':[{'message':{'content':'{"document_type":"invoice","fields":{"number":"123"},"confidence":0.9}'}}]}).encode()
  return Response()
 monkeypatch.setattr(urllib.request,'urlopen',fake)
 result=automation.vision_extract(str(path),'application/pdf')
 assert result[0]=='invoice' and result[1]['number']=='123'

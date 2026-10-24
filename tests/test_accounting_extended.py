from test_api import api

def test_accounting_ar_ap_and_overpayment(api):
 c,h=api
 a=c.post('/api/accounting/parties',headers=h,json={'code':'C001','name':'Khách hàng thử nghiệm','kind':'customer'})
 assert a.status_code==201,a.text
 p=a.json()['id']
 r=c.post('/api/accounting/open-items',headers=h,json={'party_id':p,'kind':'receivable','reference':'AR-001','issue_date':'2026-10-01','due_date':'2026-10-10','amount':100000})
 assert r.status_code==201,r.text
 i=r.json()['id']
 assert c.post('/api/accounting/settlements',headers=h,json={'open_item_id':i,'reference':'PAY-001','paid_on':'2026-10-12','amount':40000}).status_code==201
 assert c.post('/api/accounting/settlements',headers=h,json={'open_item_id':i,'reference':'PAY-002','paid_on':'2026-10-12','amount':70000}).status_code==409
 data=c.get('/api/accounting/open-items?kind=receivable&as_of=2026-10-15',headers=h).json()
 assert data['total_outstanding']==60000 and data['items'][0]['overdue']
 assert c.get('/api/accounting/open-items').status_code==401

def test_vat_and_period_lock(api):
 c,h=api
 x=c.post('/api/accounting/vat-lines',headers=h,json={'document_ref':'VAT-001','tax_period':'2026-09','kind':'output','taxable_amount':100000,'vat_amount':10000,'tax_rate_bp':1000})
 assert x.status_code==201,x.text
 assert c.post('/api/accounting/vat-lines',headers=h,json={'document_ref':'VAT-001','tax_period':'2026-09','kind':'output','taxable_amount':100000,'vat_amount':10000,'tax_rate_bp':1000}).status_code==409
 assert c.get('/api/accounting/vat-summary?period=2026-09',headers=h).json()['net_output_minus_input']==10000
 assert c.post('/api/accounting/periods/close',headers=h,json={'period':'2026-09'}).status_code==200
 assert c.post('/api/accounting/vat-lines',headers=h,json={'document_ref':'VAT-002','tax_period':'2026-09','kind':'input','taxable_amount':100000,'vat_amount':10000,'tax_rate_bp':1000}).status_code==409
 assert c.get('/api/accounting/financial-summary?start=2026-09-01&end=2026-09-30',headers=h).status_code==200

def test_chart_of_accounts_validation(api):
 c,h=api
 assert c.post('/api/accounting/accounts',headers=h,json={'code':'111','name':'Tiền mặt','account_type':'asset'}).status_code==201
 assert c.post('/api/accounting/accounts',headers=h,json={'code':'111','name':'Tiền mặt','account_type':'asset'}).status_code==409
 assert c.post('/api/accounting/accounts',headers=h,json={'code':'112','name':'Tiền gửi','account_type':'unknown'}).status_code==422
 assert any(x['code']=='111' for x in c.get('/api/accounting/accounts',headers=h).json()['items'])

"""Read-only ERP cross-module controls; never certify absent evidence."""
import datetime
from fastapi import APIRouter, Request, HTTPException
from .db import connect
from .security import current_user, require
router=APIRouter(prefix='/api/erp/integrity',tags=['ERP cross-module integrity'])

def access(request,permission):
 u=current_user(request);require(u,permission);return u

def rows(sql,params=()):
 with connect() as c:return [dict(r) for r in c.execute(sql,params).fetchall()]

@router.get('/production-balance')
def production_balance(request:Request,limit:int=100):
 access(request,'production.read')
 items=rows('SELECT id,batch_code,output_gross,output_pass,output_reject,source_kind FROM production_batches ORDER BY rowid DESC LIMIT ?', (min(max(limit,1),500),))
 for b in items:
  g,p,r=b['output_gross'],b['output_pass'],b['output_reject']
  b['consistent']=all(x is not None and x>=0 for x in (g,p,r)) and abs(g-p-r)<0.000001
  b['verified']=False
 return {'items':items,'note':'Số liệu cân đối không đồng nghĩa đã có chứng cứ QC'}

@router.get('/journal-balance')
def journal_balance(request:Request,limit:int=100):
 access(request,'purchases.read')
 items=rows('''SELECT e.id,e.entry_date,e.description,COUNT(l.id) line_count,COALESCE(SUM(l.debit),0) debit,COALESCE(SUM(l.credit),0) credit FROM accounting_entries e LEFT JOIN accounting_lines l ON l.entry_id=e.id GROUP BY e.id ORDER BY e.entry_date DESC LIMIT ?''',(min(max(limit,1),500),))
 for item in items:item['balanced']=item['line_count']>=2 and item['debit']>0 and item['debit']==item['credit']
 return {'items':items}

@router.get('/unverified-production')
def unverified_production(request:Request,limit:int=100):
 access(request,'production.read')
 items=rows('''SELECT b.id,b.batch_code,b.shift_date,b.source_kind,ec.result latest_check FROM production_batches b LEFT JOIN evidence_checks ec ON ec.rowid=(SELECT MAX(rowid) FROM evidence_checks WHERE entity_type='production_batches' AND entity_id=b.id) WHERE ec.result IS NULL OR ec.result!='verified' ORDER BY b.shift_date DESC LIMIT ?''',(min(max(limit,1),500),))
 return {'items':items,'verification_policy':'fail_closed'}

@router.get('/pending-approvals')
def pending_approvals(request:Request,limit:int=100):
 access(request,'purchases.read')
 return {'items':rows("SELECT id,kind,reference_id,amount_vnd,requested_by,created_at FROM erp_approval_requests WHERE status='pending' ORDER BY created_at LIMIT ?",(min(max(limit,1),500),))}

@router.get('/missing-source-documents')
def missing_source_documents(request:Request,limit:int=100):
 access(request,'purchases.read')
 return {'items':rows("SELECT id,request_id,entry_date,description FROM accounting_entries WHERE source_document_id IS NULL ORDER BY entry_date DESC LIMIT ?",(min(max(limit,1),500),)),'note':'Không kết luận bút toán sai; cần xác minh nguồn chứng từ'}

@router.get('/dashboard')
def integrity_dashboard(request:Request):
 access(request,'purchases.read')
 with connect() as c:
  count=lambda q:c.execute(q).fetchone()[0]
  return {'pending_approvals':count("SELECT COUNT(*) FROM erp_approval_requests WHERE status='pending'"), 'journal_entries_without_source_document':count('SELECT COUNT(*) FROM accounting_entries WHERE source_document_id IS NULL'), 'production_batches_without_verified_evidence':count("SELECT COUNT(*) FROM production_batches b WHERE NOT EXISTS(SELECT 1 FROM evidence_checks e WHERE e.entity_type='production_batches' AND e.entity_id=b.id AND e.result='verified')"), 'completion_certified':False,'data_source':'database','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}

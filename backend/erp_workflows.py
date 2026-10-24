"""ERP workflows backed by persisted records; no fabricated approval or completion."""
import datetime, json, uuid
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from .db import connect, transaction
from .security import current_user, require, now

router=APIRouter(prefix='/api/erp', tags=['ERP workflows'])

def auth(request,permission):
    user=current_user(request); require(user,permission); return user

def init_erp():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS erp_approval_requests(
            id TEXT PRIMARY KEY, kind TEXT NOT NULL, reference_id TEXT NOT NULL,
            amount_vnd INTEGER NOT NULL CHECK(amount_vnd>=0), justification TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pending','approved','rejected')),
            requested_by TEXT NOT NULL, reviewed_by TEXT, reviewed_at TEXT,
            created_at TEXT NOT NULL, UNIQUE(kind,reference_id));
        CREATE TABLE IF NOT EXISTS erp_approval_events(
            id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES erp_approval_requests(id),
            action TEXT NOT NULL, actor TEXT NOT NULL, note TEXT, occurred_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_erp_approvals_status ON erp_approval_requests(status);
        ''')

class ApprovalCreate(BaseModel):
    kind:str=Field(pattern='^(purchase|expense|payment|adjustment)$')
    reference_id:str=Field(min_length=1,max_length=100)
    amount_vnd:int=Field(ge=0,le=10**14)
    justification:str=Field(min_length=8,max_length=2000)

@router.post('/approvals',status_code=201)
def create_approval(body:ApprovalCreate,request:Request):
    user=auth(request,'purchases.write')
    rid=str(uuid.uuid4())
    try:
        with transaction() as c:
            c.execute('INSERT INTO erp_approval_requests(id,kind,reference_id,amount_vnd,justification,status,requested_by,created_at) VALUES(?,?,?,?,?,?,?,?)',
                (rid,body.kind,body.reference_id,body.amount_vnd,body.justification,'pending',user['username'],now()))
            c.execute('INSERT INTO erp_approval_events VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),rid,'requested',user['username'],body.justification,now()))
    except __import__('sqlite3').IntegrityError:raise HTTPException(409,'Yêu cầu đã tồn tại')
    return {'id':rid,'status':'pending'}

@router.get('/approvals')
def list_approvals(request:Request,status:str|None=None,limit:int=100):
    auth(request,'purchases.read')
    if status and status not in ('pending','approved','rejected'):raise HTTPException(422,'Trạng thái không hợp lệ')
    with connect() as c:
        rows=c.execute('SELECT * FROM erp_approval_requests WHERE (? IS NULL OR status=?) ORDER BY created_at DESC LIMIT ?', (status,status,min(max(limit,1),500))).fetchall()
    return {'items':[dict(x) for x in rows]}

class ApprovalDecision(BaseModel):
    decision:str=Field(pattern='^(approved|rejected)$')
    note:str=Field(min_length=8,max_length=2000)

@router.post('/approvals/{approval_id}/decision')
def decide_approval(approval_id:str,body:ApprovalDecision,request:Request):
    user=auth(request,'approvals.read')
    if user['role']!='director':raise HTTPException(403,'Chỉ giám đốc được phê duyệt')
    with transaction() as c:
        old=c.execute('SELECT * FROM erp_approval_requests WHERE id=?',(approval_id,)).fetchone()
        if not old:raise HTTPException(404,'Yêu cầu không tồn tại')
        if old['status']!='pending':raise HTTPException(409,'Đã xử lý, không thể phê duyệt lại')
        if old['requested_by']==user['username']:raise HTTPException(403,'Không được tự phê duyệt yêu cầu của mình')
        c.execute('UPDATE erp_approval_requests SET status=?,reviewed_by=?,reviewed_at=? WHERE id=?',(body.decision,user['username'],now(),approval_id))
        c.execute('INSERT INTO erp_approval_events VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),approval_id,body.decision,user['username'],body.note,now()))
    return {'id':approval_id,'status':body.decision,'financial_posted':False}

@router.get('/approvals/{approval_id}/history')
def approval_history(approval_id:str,request:Request):
    auth(request,'purchases.read')
    with connect() as c:
        if not c.execute('SELECT 1 FROM erp_approval_requests WHERE id=?',(approval_id,)).fetchone():raise HTTPException(404,'Không tồn tại')
        events=c.execute('SELECT action,actor,note,occurred_at FROM erp_approval_events WHERE request_id=? ORDER BY occurred_at',(approval_id,)).fetchall()
    return {'items':[dict(x) for x in events]}

@router.get('/production/summary')
def production_summary(request:Request,period:str='day',date:str|None=None):
    auth(request,'production.read')
    if period not in ('day','week','month','quarter','year'):raise HTTPException(422,'Kỳ không hợp lệ')
    try:anchor=datetime.date.fromisoformat(date) if date else datetime.date.today()
    except ValueError:raise HTTPException(422,'Ngày không hợp lệ')
    if period=='day':start=anchor;end=anchor+datetime.timedelta(days=1)
    elif period=='week':start=anchor-datetime.timedelta(days=anchor.weekday());end=start+datetime.timedelta(days=7)
    elif period=='month':start=anchor.replace(day=1);end=(start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1))
    elif period=='quarter':start=anchor.replace(month=((anchor.month-1)//3)*3+1,day=1);end=start.replace(year=start.year+1,month=1) if start.month==10 else start.replace(month=start.month+3)
    else:start=anchor.replace(month=1,day=1);end=start.replace(year=start.year+1)
    with connect() as c:
        r=c.execute('SELECT COUNT(*) batches,COALESCE(SUM(output_gross),0) gross,COALESCE(SUM(output_pass),0) passed,COALESCE(SUM(output_reject),0) rejected FROM production_batches WHERE shift_date>=? AND shift_date<?',(start.isoformat(),end.isoformat())).fetchone()
    result=dict(r)
    result.update({'period':period,'start':start.isoformat(),'end_exclusive':end.isoformat(),'pass_rate':result['passed']/result['gross'] if result['gross'] else None,'data_source':'production_batches','verification':'aggregate_only_not_evidence_approval'})
    return result

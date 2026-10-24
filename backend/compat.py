"""V87: compatibility endpoints. Authenticated; no fabricated data or implicit posting."""
import json,uuid,datetime,os,urllib.request,urllib.error,math
from fastapi import APIRouter,Request,HTTPException
from pydantic import BaseModel
from . import security
from .db import connect,transaction
from .agents import evaluate
router=APIRouter(prefix='/api')
def user(request):return security.current_user(request)
def permitted(request,permission):
 u=user(request);security.require(u,permission);return u

def init_compat():
 with connect() as c:c.executescript('''
 CREATE TABLE IF NOT EXISTS electric_readings(id TEXT PRIMARY KEY,zone TEXT NOT NULL,kwh REAL NOT NULL CHECK(kwh>=0),unit_price REAL NOT NULL CHECK(unit_price>=0),recorded_at TEXT NOT NULL,actor TEXT NOT NULL,request_id TEXT NOT NULL UNIQUE);
 CREATE TABLE IF NOT EXISTS marketing_expenses(id TEXT PRIMARY KEY,campaign_id TEXT,amount REAL NOT NULL CHECK(amount>=0),description TEXT,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending');
 ''')
@router.get('/status')
def status(request:Request):
 u=user(request)
 return {'status':'ok','agents':0,'model_connected':bool(os.getenv('OPENAI_API_KEY')),'mode':'rule_based','role':u['role'],'note':'Không tuyên bố AI thực nếu chưa cấu hình và thử nghiệm'}
@router.post('/run')
def run(request:Request,body:dict):
 u=permitted(request,'costs.read');r=evaluate('legacy_compat',u['username'])
 return {'mode':'rule_based_verified_db','results':[{'name':k,'findings':v} for k,v in r.get('results',{}).items()]}
@router.post('/ask')
def ask(request:Request,body:dict):
 u=user(request)
 q=str(body.get('question','')).strip()
 if not q or len(q)>3000:raise HTTPException(422,'Câu hỏi phải có 1–3000 ký tự')
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key:return {'answer':'Chưa cấu hình dịch vụ AI; không đưa ra kết luận giả.','mode':'not_configured','verified':False}
 with connect() as c:
  data={'customers':c.execute('SELECT COUNT(*) FROM customers').fetchone()[0], 'orders':c.execute('SELECT COUNT(*) FROM sales_orders').fetchone()[0], 'production_batches':c.execute('SELECT COUNT(*) FROM production_batches').fetchone()[0]}
 prompt='Bạn là trợ lý quản trị nhà máy FLEX 3D. Chỉ dùng số liệu xác minh từ máy chủ, không dùng context trình duyệt, không suy diễn. Nếu thiếu dữ liệu phải nói rõ. Dữ liệu: '+json.dumps(data,ensure_ascii=False)
 payload={'model':os.getenv('SUNNY_TEXT_MODEL','gpt-4.1-mini'),'messages':[{'role':'system','content':prompt},{'role':'user','content':q}],'temperature':0}
 req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=30) as r:result=json.load(r)
  answer=result['choices'][0]['message']['content']
 except (urllib.error.URLError,TimeoutError,KeyError,ValueError) as exc:
  raise HTTPException(503,'Dịch vụ AI không sẵn sàng; không có kết quả được xác minh') from exc
 return {'answer':answer,'mode':'llm_with_limited_verified_counts','verified':False,'note':'Phản hồi AI chưa được xác minh độc lập'}
@router.get('/realtime')
def realtime(request:Request):
 permitted(request,'stock.read')
 with connect() as c:
  mats=[dict(r) for r in c.execute('''SELECT i.id,i.name,i.unit,i.standard_qty standard,i.daily_usage daily,i.lead_days lead,COALESCE(SUM(s.quantity_delta),0) stock FROM inventory_items i LEFT JOIN stock_movements s ON s.item_id=i.id GROUP BY i.id''')]
  events=[dict(r) for r in c.execute('SELECT occurred_at created_at,kind,ABS(quantity_delta) qty,item_id material_id FROM stock_movements ORDER BY occurred_at DESC LIMIT 10')]
  kwh,cost=c.execute('SELECT COALESCE(SUM(kwh),0),COALESCE(SUM(kwh*unit_price),0) FROM electric_readings').fetchone()
 alerts=[]
 for m in mats:
  if m['standard'] and m['stock']<=m['standard']*.4:
   need=m['daily']*m['lead'];alerts.append({'id':m['id'],'name':m['name'],'stock':m['stock'],'unit':m['unit'],'threshold':m['standard']*.4,'need':need,'reorder':max(0,m['standard']-m['stock']),'urgent':m['stock']<need})
 return {'time':security.now(),'materials':mats,'alerts':alerts,'events':events,'electric_kwh':kwh,'electric_cost':cost,'source':'database'}
class Electric(BaseModel):
 zone:str;kwh:float;unit_price:float;request_id:str
@router.post('/electric')
def electric(body:Electric,request:Request):
 u=permitted(request,'costs.read')
 if u['role'] not in ('director','accountant'):raise HTTPException(403,'Chỉ kế toán hoặc giám đốc')
 if not body.zone.strip() or not 8<=len(body.request_id)<=128 or not math.isfinite(body.kwh) or not math.isfinite(body.unit_price) or not 0<=body.kwh<=1e8 or not 0<=body.unit_price<=1e8:raise HTTPException(422,'Dữ liệu không hợp lệ')
 with transaction() as c:
  existing=c.execute('SELECT id FROM electric_readings WHERE request_id=?',(body.request_id,)).fetchone()
  if existing:return {'id':existing['id'],'duplicate':True}
  rid=str(uuid.uuid4());c.execute('INSERT INTO electric_readings VALUES(?,?,?,?,?,?,?)',(rid,body.zone,body.kwh,body.unit_price,security.now(),u['username'],body.request_id))
 return {'id':rid,'duplicate':False}
@router.get('/marketing')
def marketing(request:Request):
 u=permitted(request,'marketing.read')
 with connect() as c:
  campaigns=[dict(r) for r in c.execute('SELECT id,name,channel,budget_amount budget,status FROM marketing_campaigns')]
  leads=[dict(r) for r in c.execute('SELECT * FROM marketing_leads')]
  expenses=[dict(r) for r in c.execute('SELECT * FROM marketing_expenses')]
  orders=c.execute('SELECT COUNT(*) FROM sales_orders').fetchone()[0]
 spent=sum(x['amount'] for x in expenses if x['status']=='approved')
 for c in campaigns:c.update(goal='',spent=sum(x['amount'] for x in expenses if x['campaign_id']==c['id'] and x['status']=='approved'),owner='Chưa phân công',source='real')
 return {'role':u['role'],'campaigns':campaigns,'leads':leads,'expenses':expenses,'attribution':[],'content':[],'alerts':[],'metrics':{'leads':len(leads),'orders':orders,'revenue':0,'collected':0,'spend':spent,'net_contribution':None,'cost_per_lead':spent/len(leads) if leads else None,'conversion':None},'note':'Doanh thu marketing chưa được đối soát nên không tự tạo số liệu'}
@router.post('/marketing/create')
def marketing_create(body:dict,request:Request):
 u=permitted(request,'marketing.write');kind=body.get('kind');rid=str(uuid.uuid4())
 with transaction() as c:
  if kind=='campaign':
   name=str(body.get('name','')).strip();channel=str(body.get('channel','')).strip()
   if not name or not channel:raise HTTPException(422,'Thiếu tên hoặc kênh')
   budget=float(body.get('budget') or 0)
   if not math.isfinite(budget) or budget<0 or budget>1e12:raise HTTPException(422,'Ngân sách không hợp lệ')
   c.execute('INSERT INTO marketing_campaigns(id,name,channel,budget_amount,status) VALUES(?,?,?,?,?)',(rid,name,channel,budget,'draft'))
  elif kind=='lead':
   name=str(body.get('customer_name','')).strip()
   if not name:raise HTTPException(422,'Thiếu tên khách')
   customer_id=str(uuid.uuid4());c.execute('INSERT INTO customers(id,customer_code,name,created_at) VALUES(?,?,?,?)',(customer_id,'LEAD-'+customer_id[:12],name,security.now()));c.execute('INSERT INTO marketing_leads(id,campaign_id,customer_id,created_at,status) VALUES(?,?,?,?,?)',(rid,body.get('campaign_id') or None,customer_id,security.now(),'new'))
  elif kind=='expense':
   amount=float(body.get('amount') or 0)
   if not math.isfinite(amount) or amount<=0 or amount>1e12:raise HTTPException(422,'Số tiền không hợp lệ')
   c.execute('INSERT INTO marketing_expenses(id,campaign_id,amount,description,created_at,actor) VALUES(?,?,?,?,?,?)',(rid,body.get('campaign_id'),amount,str(body.get('description',''))[:500],security.now(),u['username']))
  else:raise HTTPException(422,'Loại bản ghi không hợp lệ')
  c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,new_json) VALUES(?,?,?,?,?,?)',(u['username'],'marketing_create',kind,rid,security.now(),json.dumps({'kind':kind},ensure_ascii=False)))
 return {'id':rid,'kind':kind,'status':'pending_review' if kind=='expense' else 'created'}
@router.post('/marketing/review')
def marketing_review(body:dict,request:Request):
 u=user(request)
 if u['role'] not in ('director','accountant'):raise HTTPException(403,'Không được duyệt chi')
 status=body.get('status')
 if status not in ('approved','rejected'):raise HTTPException(422,'Trạng thái không hợp lệ')
 with transaction() as c:
  cur=c.execute("UPDATE marketing_expenses SET status=? WHERE id=? AND status='pending'",(status,body.get('id')))
  if cur.rowcount!=1:raise HTTPException(409,'Không có phiếu chờ duyệt')
  c.execute('INSERT INTO audit_log(actor_id,action,entity_type,entity_id,at,new_json) VALUES(?,?,?,?,?,?)',(u['username'],'marketing_review','marketing_expenses',str(body.get('id')),security.now(),json.dumps({'status':status})))
 return {'status':status}
@router.post('/marketing/seed')
def seed(request:Request):
 permitted(request,'marketing.write')
 raise HTTPException(409,'Không được nạp dữ liệu mẫu vào cơ sở dữ liệu vận hành')
@router.post('/stock')
def legacy_stock(request:Request):
 permitted(request,'stock.write')
 raise HTTPException(409,'API cũ dùng mã vật tư số không an toàn; chuyển sang /api/stock/movements với mã vật tư UUID và kho hợp lệ')
@router.get('/integration/coverage')
def coverage(request:Request):
 u=user(request)
 from .main import app
 routes={getattr(r,'path','') for r in app.routes}
 expected=['/api/health','/api/status','/api/run','/api/ask','/api/realtime','/api/stock','/api/electric','/api/marketing','/api/marketing/create','/api/marketing/review','/api/marketing/seed']
 return {'present':[p for p in expected if p in routes],'missing':[p for p in expected if p not in routes],'warning':'Đường dẫn tồn tại không chứng minh giao diện cũ tương thích hoặc nghiệp vụ hoàn chỉnh','role':u['role']}

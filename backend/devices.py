"""Device gateway: real telemetry only, per-device bearer secret, replay protection.
No automatic stock/accounting posting from untrusted measurements.
"""
import os,hashlib,hmac,uuid,datetime,json,math
from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel,Field
from .db import connect,transaction
from .security import now,current_user
router=APIRouter(prefix='/api/devices',tags=['devices'])
KINDS={'scale_kg','meter_m','power_kwh','camera_event','humidity_pct','temperature_c'}
class Reading(BaseModel):
 device_id:str=Field(min_length=1,max_length=80)
 request_id:str=Field(min_length=8,max_length=128)
 kind:str
 value:float
 observed_at:datetime.datetime
 unit:str=Field(max_length=20)
 metadata:dict=Field(default_factory=dict)
def init_devices():
 with connect() as c:c.executescript('''
 CREATE TABLE IF NOT EXISTS device_readings(id TEXT PRIMARY KEY,device_id TEXT NOT NULL,request_id TEXT NOT NULL UNIQUE,kind TEXT NOT NULL,value REAL NOT NULL,unit TEXT NOT NULL,observed_at TEXT NOT NULL,received_at TEXT NOT NULL,metadata_json TEXT NOT NULL,verification TEXT NOT NULL DEFAULT 'device_reported');
 CREATE INDEX IF NOT EXISTS idx_device_readings_time ON device_readings(observed_at);
 ''')
@router.post('/readings',status_code=201)
def ingest(body:Reading,request:Request):
 configured=os.getenv('SUNNY_DEVICE_TOKENS_JSON','')
 try:secrets=json.loads(configured) if configured else {}
 except ValueError:raise HTTPException(503,'Cấu hình thiết bị sai')
 secret=secrets.get(body.device_id)
 supplied=request.headers.get('X-Device-Token','')
 if not isinstance(secret,str) or len(secret)<24 or not hmac.compare_digest(supplied,secret):raise HTTPException(401,'Thiết bị không được cấp quyền')
 if body.kind not in KINDS or not math.isfinite(body.value) or abs(body.value)>1e12:raise HTTPException(422,'Số đo không hợp lệ')
 if body.kind in ('scale_kg','meter_m','power_kwh','humidity_pct') and body.value<0:raise HTTPException(422,'Số đo âm')
 if body.kind=='humidity_pct' and body.value>100:raise HTTPException(422,'Độ ẩm vượt giới hạn')
 if len(json.dumps(body.metadata))>4000:raise HTTPException(422,'Metadata quá lớn')
 ts=body.observed_at
 if ts.tzinfo is None:raise HTTPException(422,'Cần múi giờ')
 age=abs((datetime.datetime.now(datetime.timezone.utc)-ts.astimezone(datetime.timezone.utc)).total_seconds())
 if age>86400:raise HTTPException(422,'Thời điểm ngoài cửa sổ 24 giờ')
 with transaction() as c:
  old=c.execute('SELECT id,device_id FROM device_readings WHERE request_id=?',(body.request_id,)).fetchone()
  if old:
   if old['device_id']!=body.device_id:raise HTTPException(409,'Mã yêu cầu đã thuộc thiết bị khác')
   previous=c.execute('SELECT kind,value,unit,observed_at FROM device_readings WHERE id=?',(old['id'],)).fetchone()
   if (previous['kind'],previous['value'],previous['unit'],previous['observed_at'])!=(body.kind,body.value,body.unit,ts.isoformat()):raise HTTPException(409,'Trùng mã yêu cầu nhưng dữ liệu đã thay đổi')
   return {'id':old['id'],'duplicate':True,'verification':'device_reported'}
  rid=str(uuid.uuid4())
  c.execute('INSERT INTO device_readings VALUES(?,?,?,?,?,?,?,?,?,?)',(rid,body.device_id,body.request_id,body.kind,body.value,body.unit,ts.isoformat(),now(),json.dumps(body.metadata,ensure_ascii=False),'device_reported'))
 return {'id':rid,'duplicate':False,'verification':'device_reported'}
@router.get('/readings')
def list_readings(request:Request,limit:int=100):
 u=current_user(request)
 if u['role'] not in ('director','production_lead','warehouse','accountant','maintenance'):raise HTTPException(403,'Không có quyền')
 with connect() as c:rows=[dict(x) for x in c.execute('SELECT id,device_id,kind,value,unit,observed_at,received_at,verification FROM device_readings ORDER BY received_at DESC LIMIT ?',(min(max(limit,1),500),))]
 return {'items':rows,'note':'Số đo thiết bị chưa phải bằng chứng nghiệm thu QC hay chứng từ kế toán'}

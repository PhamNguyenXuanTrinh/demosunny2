import hashlib,hmac,secrets,datetime,os
from fastapi import HTTPException,Request
from .db import connect,transaction
UTC=datetime.timezone.utc
now=lambda:datetime.datetime.now(UTC).isoformat()
ROLES={
 'director':{'*'},
 'accountant':{'customers.read','orders.read','purchases.read','purchases.write','costs.read','assets.read','stock.read','approvals.read'},
 'warehouse':{'stock.read','stock.write','assets.read','assets.write','purchases.read','documents.write'},
 'production_lead':{'production.read','production.write','stock.read','qc.write','documents.write'},
 'worker':{'production.read','duties.read','incidents.write','documents.write'},
 'sales':{'customers.read','customers.write','orders.read','orders.write','marketing.read','documents.write'},
 'marketing':{'customers.read','customers.write','orders.read','marketing.read','marketing.write','documents.write'},
 'collaborator':{'customers.read','customers.write','orders.read','orders.write','duties.read'},
 'hr':{'employees.read','employees.write','duties.read','duties.write','documents.write'},
 'maintenance':{'assets.read','stock.read','incidents.write','documents.write'},
 'purchasing':{'purchases.read','purchases.write','stock.read','documents.write'},
}
def hash_password(p,salt=None):
 salt=salt or secrets.token_hex(16)
 return salt+'$'+hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(salt),310000).hex()
def verify(p,stored):
 try:
  salt,_=stored.split('$',1)
  return hmac.compare_digest(hash_password(p,salt),stored)
 except Exception:return False

def bootstrap():
 username=os.getenv('SUNNY_ADMIN_USER','admin');password=os.getenv('SUNNY_ADMIN_PASSWORD','')
 with connect() as c:
  exists=c.execute('SELECT COUNT(*) FROM api_accounts').fetchone()[0]
 if exists:return
 if len(password)<12:raise RuntimeError('Set SUNNY_ADMIN_PASSWORD (>=12 chars) before first start')
 with transaction() as c:c.execute('INSERT INTO api_accounts VALUES(?,?,?,?,?,?)',(secrets.token_hex(12),username,hash_password(password),'director',None,now()))

def authenticate(username,password):
 # Database-backed throttle: survives restart, prevents unlimited online password guessing.
 key=hashlib.sha256(username.casefold().encode()).hexdigest()
 current=datetime.datetime.now(UTC)
 with transaction() as c:
  c.execute("CREATE TABLE IF NOT EXISTS login_attempts(identity_hash TEXT PRIMARY KEY,failures INTEGER NOT NULL,locked_until TEXT)")
  attempt=c.execute('SELECT failures,locked_until FROM login_attempts WHERE identity_hash=?',(key,)).fetchone()
  if attempt and attempt['locked_until'] and datetime.datetime.fromisoformat(attempt['locked_until'])>current:
   raise HTTPException(429,'Tạm khóa đăng nhập; thử lại sau')
 with connect() as c:r=c.execute('SELECT * FROM api_accounts WHERE username=?',(username,)).fetchone()
 if not r or not verify(password,r['password_hash']):
  with transaction() as c:
   failures=(attempt['failures'] if attempt else 0)+1
   locked=(current+datetime.timedelta(minutes=15)).isoformat() if failures>=5 else None
   c.execute('INSERT INTO login_attempts(identity_hash,failures,locked_until) VALUES(?,?,?) ON CONFLICT(identity_hash) DO UPDATE SET failures=excluded.failures,locked_until=excluded.locked_until',(key,failures,locked))
  raise HTTPException(401,'Sai tài khoản hoặc mật khẩu')
 with transaction() as c:c.execute('DELETE FROM login_attempts WHERE identity_hash=?',(key,))
 token=secrets.token_urlsafe(32);exp=(datetime.datetime.now(UTC)+datetime.timedelta(hours=8)).isoformat()
 with transaction() as c:c.execute('INSERT INTO api_tokens VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),r['id'],exp))
 return token

def current_user(request:Request):
 token=request.headers.get('Authorization','').removeprefix('Bearer ').strip()
 if not token:raise HTTPException(401,'Cần đăng nhập')
 with connect() as c:r=c.execute('SELECT a.* FROM api_tokens t JOIN api_accounts a ON a.id=t.account_id WHERE t.token_hash=? AND t.expires_at>?',(hashlib.sha256(token.encode()).hexdigest(),now())).fetchone()
 if not r:raise HTTPException(401,'Phiên đăng nhập không hợp lệ')
 return dict(r)

def require(user,permission):
 if '*' not in ROLES.get(user['role'],set()) and permission not in ROLES.get(user['role'],set()):raise HTTPException(403,'Không có quyền')

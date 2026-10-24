from pathlib import Path
import re
from test_api import api

def test_primary_frontend_api_contract(api):
 c,h=api
 source=(Path(__file__).parents[1]/'public'/'index.html').read_text()
 calls=set(re.findall(r"['\"](/api/[a-zA-Z0-9_/{}/.-]+)['\"]",source))
 registered={r.path for r in c.app.routes}
 # Frontend dynamic paths may be templated; validate static API calls
 missing=[x for x in calls if x not in registered and not any('{' in r and re.fullmatch(re.sub(r'\{[^}]+\}',r'[^/]+',r),x) for r in registered)]
 assert not missing,missing

def test_no_public_private_paths(api):
 c,h=api
 for path in ['/backend/main.py','/database/schema_target.sql','/.env','/data/sunny.sqlite3','/archive/V86_GOC_BAT_BIEN.html']:
  assert c.get(path).status_code==404,path

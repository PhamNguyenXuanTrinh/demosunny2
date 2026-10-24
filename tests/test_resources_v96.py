from backend.resources import RESOURCES,READ_ONLY,valid_body
from fastapi import HTTPException
from backend.db import connect

def test_resources_whitelisted():
 assert len(RESOURCES)>=16
 assert 'api_accounts' not in RESOURCES
 assert READ_ONLY.issubset(RESOURCES)

def test_schema_validates_unknown_fields():
 with connect() as c:
  try:valid_body(c,'products',{'evil_column':'value'})
  except HTTPException as e:assert e.status_code==422
  else:assert False

def test_schema_blocks_verified_flags():
 with connect() as c:
  try:valid_body(c,'products',{'verified':1})
  except HTTPException as e:assert e.status_code==422
  else:assert False

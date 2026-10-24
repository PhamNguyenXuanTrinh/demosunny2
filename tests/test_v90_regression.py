import pytest
from fastapi.testclient import TestClient
from test_api import api

def test_warehouse_validation(api):
 c,h=api
 r=c.get('/api/warehouses',headers=h)
 assert r.status_code==200 and isinstance(r.json()['items'],list)
 i=c.post('/api/v1/inventory_items',headers=h,json={'sku':'XM90','name':'Xi măng','category':'production','unit':'kg'}).json()['id']
 assert c.post('/api/stock/movements',headers=h,json={'request_id':'V90INVALIDWH','item_id':i,'warehouse_id':'nonexistent','kind':'in','quantity':1}).status_code==404

def test_ask_no_fabricated_llm(api,monkeypatch):
 monkeypatch.delenv('OPENAI_API_KEY',raising=False)
 c,h=api
 r=c.post('/api/ask',headers=h,json={'question':'Báo cáo hôm nay'})
 assert r.status_code==200 and r.json()['verified'] is False

def test_invalid_marketing_budget(api):
 c,h=api
 r=c.post('/api/marketing/create',headers=h,json={'kind':'campaign','name':'Thử','channel':'tiktok','budget':-1})
 assert r.status_code==422

def test_legacy_redirects_to_authenticated_frontend():
 from pathlib import Path
 s=(Path(__file__).parents[1]/'public/legacy.html').read_text()
 assert 'url=/index.html' in s
 assert 'localStorage.setItem' not in s

from test_api import api

def test_login_throttle(api):
 client,_=api
 for _ in range(5):
  assert client.post('/api/auth/login',json={'username':'attacker','password':'bad'}).status_code==401
 assert client.post('/api/auth/login',json={'username':'attacker','password':'bad'}).status_code==429

def test_legacy_no_local_mock(api):
 client,_=api
 page=client.get('/legacy.html')
 assert page.status_code==200
 assert 'localStorage.setItem' not in page.text
 assert 'url=/index.html' in page.text

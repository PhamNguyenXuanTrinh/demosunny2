import json
from pathlib import Path
from backend.main import app
out=[]
for r in app.routes:
    methods=sorted(getattr(r,'methods',[]) or [])
    path=getattr(r,'path','')
    if path.startswith('/api/'):
        for m in methods:
            if m not in ('HEAD','OPTIONS'):
                out.append({'method':m,'path':path,'name':getattr(r,'name','')})
out.sort(key=lambda x:(x['path'],x['method']))
p=Path(__file__).parent/'docs'/'API_KIEM_KE_THUC_TE.json'
p.write_text(json.dumps({'total_method_paths':len(out),'routes':out},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(out)} cặp phương thức/đường dẫn API -> {p}')

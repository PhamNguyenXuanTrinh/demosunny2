#!/usr/bin/env python3
"""Cổng nghiệm thu: kiểm tra API, mã nguồn, cấu trúc và kiểm thử hiện có. Không thay thế UAT/bảo mật chuyên sâu."""
import os,json,sys,subprocess,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from backend.main import app
routes=sorted({(m,p.path) for p in app.routes for m in getattr(p,'methods',set()) if p.path.startswith('/api/') and m not in ('HEAD','OPTIONS')})
required=['backend/main.py','backend/db.py','backend/security.py','database/schema_target.sql','public/index.html','requirements.txt']
checks={f: (root/f).is_file() for f in required}
results={'api_method_path_count':len(routes),'api_target_minimum':100,'api_count_pass':len(routes)>=100,'files':checks,'files_pass':all(checks.values())}
(root/'nghiem_thu'/'DANH_SACH_API_KIEM_TRA.json').write_text(json.dumps([{'method':m,'path':p} for m,p in routes],ensure_ascii=False,indent=2),encoding='utf-8')
env=dict(os.environ);env['SUNNY_ADMIN_PASSWORD']='StrongTestPassword2026!';env['PYTHONDONTWRITEBYTECODE']='1'
proc=subprocess.run([sys.executable,'-m','pytest','-q','tests'],cwd=root,env=env,text=True,capture_output=True)
results['tests_pass']=proc.returncode==0;results['tests_exit_code']=proc.returncode;results['test_output']=(proc.stdout+'\n'+proc.stderr)[-12000:]
results['source_gate_pass']=results['api_count_pass'] and results['files_pass'] and results['tests_pass']
results['full_erp_accepted']=False
results['reason']='Chưa có bằng chứng UAT đầu-cuối, kiểm thử an ninh độc lập, xác nhận kế toán pháp định, thử thiết bị thực và khôi phục sao lưu.'
(root/'nghiem_thu'/'KET_QUA_CONG_NGHIEM_THU.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in results.items() if k!='test_output'},ensure_ascii=False,indent=2))
print(results['test_output'])
sys.exit(0 if results['source_gate_pass'] else 1)

"""Kiểm tra độc lập không cần máy thật; chạy tại thư mục gốc."""
import ast, json, pathlib, sys, zipfile
root=pathlib.Path(__file__).resolve().parents[1]
errors=[]
for path in sorted(root.rglob('*.py')):
 try:ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
 except Exception as e:errors.append(f'{path.relative_to(root)}: {e}')
for p in ['backend/main.py','backend/db.py','backend/security.py','backend/accounting.py','backend/devices.py','database/schema_target.sql','public/index.html','public/app.html','public/legacy.html','requirements.txt','docs/API_HUONG_DAN.md']:
 if not (root/p).is_file():errors.append('THIEU '+p)
print(json.dumps({'python_files':len(list(root.rglob('*.py'))),'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))

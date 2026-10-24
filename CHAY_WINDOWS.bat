@echo off
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if "%SUNNY_ADMIN_PASSWORD%"=="" (
 echo Can dat SUNNY_ADMIN_PASSWORD trong bien moi truong truoc khi chay.
 pause
 exit /b 1
)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765

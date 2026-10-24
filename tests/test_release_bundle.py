from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_handoff_includes_all_major_source_modules():
 for item in ('backend/main.py','backend/accounting.py','backend/devices.py','backend/automation.py','backend/security.py','database/schema_target.sql','public/index.html','public/app.html','public/legacy.html','archive/V86_GOC_BAT_BIEN.html','deploy/Dockerfile','deploy/docker-compose.yml'):
  assert (ROOT/item).is_file(),item

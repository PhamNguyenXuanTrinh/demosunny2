from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
def test_original_v86_is_default_and_preserved():
    assert hashlib.sha256((ROOT/'public/index.html').read_bytes()).digest()==hashlib.sha256((ROOT/'public/v86.html').read_bytes()).digest()
def test_integrated_app_retained_separately():
    assert (ROOT/'public/app.html').is_file()

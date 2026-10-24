import os, sqlite3, contextlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DB=Path(os.getenv('SUNNY_DB_PATH',str(ROOT/'data'/'sunny.sqlite3')))
SCHEMA=ROOT/'database'/'schema_target.sql'

def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB,timeout=30,isolation_level=None)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA busy_timeout=30000');c.execute('PRAGMA journal_mode=WAL')
 return c

@contextlib.contextmanager
def transaction():
 c=connect()
 try:
  c.execute('BEGIN IMMEDIATE');yield c;c.commit()
 except Exception:
  c.rollback();raise
 finally:c.close()

def init():
 with connect() as c:
  c.executescript(SCHEMA.read_text(encoding='utf8'))
  c.executescript('''
CREATE TABLE IF NOT EXISTS api_accounts(id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL,owner_id TEXT,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS api_tokens(token_hash TEXT PRIMARY KEY,account_id TEXT NOT NULL REFERENCES api_accounts(id),expires_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS api_idempotency(key TEXT PRIMARY KEY,actor TEXT NOT NULL,route TEXT NOT NULL,result_json TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS agent_evaluations(id TEXT PRIMARY KEY,agent TEXT NOT NULL,trigger_name TEXT NOT NULL,result_json TEXT NOT NULL,created_at TEXT NOT NULL,source_kind TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS api_jobs(id TEXT PRIMARY KEY,job_type TEXT NOT NULL,payload_json TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS accounting_entries(id TEXT PRIMARY KEY,request_id TEXT NOT NULL,entry_date TEXT NOT NULL,description TEXT NOT NULL,source_document_id TEXT,created_by TEXT NOT NULL,created_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'posted');
CREATE TABLE IF NOT EXISTS accounting_lines(id TEXT PRIMARY KEY,entry_id TEXT NOT NULL REFERENCES accounting_entries(id),account_code TEXT NOT NULL,debit INTEGER NOT NULL DEFAULT 0,credit INTEGER NOT NULL DEFAULT 0,CHECK(debit>=0 AND credit>=0),CHECK(NOT (debit>0 AND credit>0)));
CREATE TABLE IF NOT EXISTS evidence_checks(id TEXT PRIMARY KEY,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,check_type TEXT NOT NULL,result TEXT NOT NULL,details_json TEXT NOT NULL,checked_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_accounting_lines_entry ON accounting_lines(entry_id);
CREATE INDEX IF NOT EXISTS idx_evidence_checks_entity ON evidence_checks(entity_type,entity_id);
''')

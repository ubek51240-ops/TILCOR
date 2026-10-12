import sqlite3, os, shutil, json, hashlib

# Test migration and rollback in sandbox
sandbox_db = 'scratch/sandbox_phd_corpus.db'
if os.path.exists(sandbox_db):
    os.remove(sandbox_db)

shutil.copy2('data/phd_corpus.db', sandbox_db)
print(f"Copied data/phd_corpus.db to sandbox: {os.path.getsize(sandbox_db)} bytes")

# Check existing tables in sandbox
conn = sqlite3.connect(sandbox_db)
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Initial sandbox tables: {tables}")
conn.close()

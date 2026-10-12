import shutil, sqlite3
from scripts.rollback_phd_v2 import rollback_database

shutil.copy2('data/phd_corpus.db', 'scratch/test_rb.db')
shutil.copy2('data/phd_corpus.db.pre_stage3.bak', 'scratch/test_rb.db.pre_stage3.bak')
success = rollback_database('scratch/test_rb.db')
assert success

conn = sqlite3.connect('scratch/test_rb.db')
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
conn.close()
print("Tables after rollback in test copy:", tables)
assert 'works' not in tables
print("Rollback isolated test PASSED 100%!")

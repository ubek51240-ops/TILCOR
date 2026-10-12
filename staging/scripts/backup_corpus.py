"""
Automated daily backup utility for TILCOR parallel corpus.
Creates an atomic copy of data/phd_corpus.db with SHA256 checksum,
storing into backups/ with timestamp.
"""
import os
import shutil
import sqlite3
import hashlib
from datetime import datetime

def make_backup(db_path="data/phd_corpus.db", backup_dir="backups"):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database {db_path} not found.")
        
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"phd_corpus_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Use SQLite backup API for 100% online ACID consistency
    src_conn = sqlite3.connect(db_path)
    dst_conn = sqlite3.connect(backup_path)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    
    # Compute SHA256
    with open(backup_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
        
    sha_file = backup_path + ".sha256"
    with open(sha_file, "w", encoding="utf-8") as f:
        f.write(f"{sha256}  {backup_filename}\n")
        
    print(f"[BACKUP SUCCESS] Created: {backup_path}")
    print(f"  SHA256: {sha256}")
    return backup_path, sha256

if __name__ == "__main__":
    make_backup()

"""
Automated restore utility for TILCOR parallel corpus.
Verifies SHA256 checksum and foreign key constraints before restoring.
"""
import os
import shutil
import sqlite3
import hashlib

def verify_and_restore(backup_path, target_db="data/phd_corpus.db"):
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file {backup_path} not found.")
        
    sha_file = backup_path + ".sha256"
    if os.path.exists(sha_file):
        with open(sha_file, "r", encoding="utf-8") as f:
            expected_sha = f.read().split()[0].strip()
        with open(backup_path, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        if expected_sha.lower() != actual_sha.lower():
            raise ValueError(f"Checksum mismatch! Expected: {expected_sha}, Got: {actual_sha}")
        print("  SHA256 checksum verified: MATCH")

    # Check integrity of the backup database itself
    conn = sqlite3.connect(backup_path)
    cur = conn.cursor()
    fk_errors = cur.execute("PRAGMA foreign_key_check").fetchall()
    quick_check = cur.execute("PRAGMA quick_check").fetchone()[0]
    conn.close()
    
    if quick_check != "ok":
        raise ValueError(f"Integrity check failed on backup: {quick_check}")
    if fk_errors:
        raise ValueError(f"Foreign key errors in backup: {fk_errors}")
    print("  Integrity & foreign keys verified: 100% OK")

    # Perform atomic restore
    temp_target = target_db + ".restore_tmp"
    shutil.copyfile(backup_path, temp_target)
    if os.path.exists(target_db):
        os.replace(temp_target, target_db)
    else:
        os.rename(temp_target, target_db)
        
    print(f"[RESTORE SUCCESS] Database restored to: {target_db}")
    return True

if __name__ == "__main__":
    import glob
    backups = sorted(glob.glob("backups/phd_corpus_backup_*.db"))
    if not backups:
        print("No backups found.")
    else:
        latest = backups[-1]
        print(f"Restoring latest backup: {latest}")
        verify_and_restore(latest)

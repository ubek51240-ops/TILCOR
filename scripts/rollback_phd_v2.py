#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 3 DATABASE ROLLBACK SCRIPT
Restores database from snapshot phd_corpus.db.pre_stage3.bak
"""

import os, sys, shutil

sys.stdout.reconfigure(encoding='utf-8')

def rollback_database(db_path):
    print(f"\n=======================================================")
    print(f" ROLLING BACK DATABASE: {db_path}")
    print(f"=======================================================")
    
    backup_path = db_path + ".pre_stage3.bak"
    if not os.path.exists(backup_path):
        print(f"[!] Pre-migration backup not found: {backup_path}")
        return False

    shutil.copy2(backup_path, db_path)
    print(f"[+] Successfully restored {db_path} from {backup_path}")
    return True

if __name__ == '__main__':
    staging_db = os.path.join('staging', 'data', 'phd_corpus.db')
    if os.path.exists(staging_db):
        rollback_database(staging_db)

    prod_db = os.path.join('data', 'phd_corpus.db')
    if os.path.exists(prod_db):
        rollback_database(prod_db)

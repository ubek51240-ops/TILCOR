"""
Stage 10: Migration script to add licence_status to texts table.
"""
import sqlite3
import os

def migrate_db(db_path):
    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check existing columns in texts
    cur.execute("PRAGMA table_info(texts)")
    cols = [r[1] for r in cur.fetchall()]
    
    if "licence_status" not in cols:
        cur.execute("ALTER TABLE texts ADD COLUMN licence_status TEXT NOT NULL DEFAULT 'protected'")
        print("  Added column 'licence_status'")
    if "permission_note" not in cols:
        cur.execute("ALTER TABLE texts ADD COLUMN permission_note TEXT")
        print("  Added column 'permission_note'")
    if "permission_doc_path" not in cols:
        cur.execute("ALTER TABLE texts ADD COLUMN permission_doc_path TEXT")
        print("  Added column 'permission_doc_path'")
        
    # Set verified licence statuses per Prompt 10:
    # 1. Cho'lpon original (1936, author died 1938 > 70 years) -> public_domain
    # 2. Stevenson original (1883, author died 1894 > 70 years) -> public_domain
    # 3. Fort translation (2020) -> protected
    # 4. Hemingway original (1952, author died 1961, protected till 2031) -> protected
    # 5. G'afurov translation (1986) -> protected
    # 6. Sharif Rizo translation (unknown death year) -> protected (quarantined)
    
    cur.execute("UPDATE texts SET licence_status = 'public_domain' WHERE id IN ('txt-cholpon-uz', 'txt-stevenson-en')")
    cur.execute("UPDATE texts SET licence_status = 'protected' WHERE id IN ('txt-cholpon-en', 'txt-hemingway-en', 'txt-hemingway-uz', 'txt-stevenson-uz')")
    
    conn.commit()
    
    cur.execute("SELECT id, role, language, licence_status, status FROM texts")
    for r in cur.fetchall():
        print(f"  {r[0]}: role={r[1]}, lang={r[2]}, licence={r[3]}, status={r[4]}")
        
    conn.close()

if __name__ == "__main__":
    for db in ["data/phd_corpus.db", "staging/data/phd_corpus.db"]:
        if os.path.exists(db):
            migrate_db(db)

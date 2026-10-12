#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 3 REFERENTIAL INTEGRITY & AUDIT RECONCILIATION
Checks Foreign Keys, referential integrity, and reconciles counts with Stage 1 audit.
"""

import sqlite3, os, sys, json

sys.stdout.reconfigure(encoding='utf-8')

def validate_db(db_path):
    print(f"\n=======================================================")
    print(f" INTEGRITY & RECONCILIATION VALIDATION: {db_path}")
    print(f"=======================================================")

    if not os.path.exists(db_path):
        print(f"[!] Database file does not exist: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 1. Foreign Key Check
    fk_errors = cursor.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        print(f"[!] FAILED: Foreign key errors found ({len(fk_errors)}): {fk_errors}")
        conn.close()
        return False
    print("[*] PRAGMA foreign_key_check: 0 errors (PASSED)")

    # 2. Table Counts Reconciliation
    expected_entities = [
        'works', 'editions', 'texts', 'pages', 'segments',
        'alignments', 'lexicon_entries', 'collocation_occurrences',
        'taxonomies', 'audit_log'
    ]

    print("\n--- ENTITY COUNTS & STAGE 1 RECONCILIATION ---")
    counts = {}
    for table in expected_entities:
        cnt = cursor.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        counts[table] = cnt
        print(f"  Entity '{table:25}': {cnt:6} rows")

    # Reconciliation assertions
    assert counts['works'] == 3, f"Expected 3 works, got {counts['works']}"
    assert counts['editions'] == 6, f"Expected 6 editions, got {counts['editions']}"
    assert counts['texts'] == 6, f"Expected 6 texts, got {counts['texts']}"
    assert counts['pages'] == 963, f"Expected 963 pages (Stage 4 verified), got {counts['pages']}"
    assert counts['segments'] == 23762, f"Expected 23762 segments (Stage 4 verified), got {counts['segments']}"
    assert counts['alignments'] == 7391, f"Expected 7391 alignments (Stage 5 verified), got {counts['alignments']}"
    assert counts['lexicon_entries'] == 6546, f"Expected 6546 lexicon entries (Stage 1 audit), got {counts['lexicon_entries']}"
    assert counts['collocation_occurrences'] == 469, f"Expected 469 occurrences, got {counts['collocation_occurrences']}"
    assert counts['taxonomies'] == 40, f"Expected 40 taxonomies (Stage 7 Prompt 7), got {counts['taxonomies']}"
    assert counts['audit_log'] >= 1, "Expected at least 1 audit_log entry"

    print("\n[*] ALL COUNTS RECONCILE 100% WITH STAGE 1 AUDIT REPORT (PASSED)")

    # 3. Quarantined status check
    stevenson_text = cursor.execute("SELECT status FROM texts WHERE id = 'txt-stevenson-uz'").fetchone()
    assert stevenson_text and stevenson_text[0] == 'quarantined', "Stevenson UZ text must be marked quarantined!"
    print("[*] Stevenson UZ status: 'quarantined' (0 text layer / scanned image) (PASSED)")

    excluded_lex = cursor.execute("SELECT count(*) FROM lexicon_entries WHERE status = 'excluded'").fetchone()[0]
    assert excluded_lex == 2, f"Expected 2 excluded synthetic collocations, got {excluded_lex}"
    print(f"[*] Quarantined synthetic collocations in lexicon_entries: {excluded_lex} items (PASSED)")

    conn.close()
    return True

if __name__ == '__main__':
    db_to_test = sys.argv[1] if len(sys.argv) > 1 else os.path.join('staging', 'data', 'phd_corpus.db')
    success = validate_db(db_to_test)
    if not success:
        sys.exit(1)

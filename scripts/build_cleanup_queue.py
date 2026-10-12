#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 6 CLEAN-UP QUEUE BUILDER
Scans lexicon_entries for:
1. Repeated-token entries (e.g. "nice nice nice")
2. POS-pattern mismatches (e.g. single word in compound pattern, non-matching POS)
3. Word-for-word calque traps / artificial placeholders
4. Template notes / invented metadata
Marks status='needs_cleanup' with specific exclusion_reason, WITHOUT deleting!
"""

import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db'

def run_cleanup_audit(db_file):
    print(f"\n[*] Scanning clean-up queue for: {db_file}")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Reset any previous temporary flags while keeping explicit excluded ones
    cur.execute("UPDATE lexicon_entries SET status = 'active' WHERE status = 'needs_cleanup'")

    rows = cur.execute("""
        SELECT id, surface_form_en, surface_form_uz, pattern, status
        FROM lexicon_entries
    """).fetchall()

    flagged = []
    
    for r_id, en, uz, pat, stat in rows:
        reasons = []
        en_words = en.lower().split()
        uz_words = uz.lower().split()

        # 1. Repeated-token check (e.g. "nice nice", "good good good")
        if len(en_words) >= 2 and len(set(en_words)) == 1:
            reasons.append("REPEATED_TOKENS_EN")
        if len(uz_words) >= 2 and len(set(uz_words)) == 1:
            reasons.append("REPEATED_TOKENS_UZ")

        # 2. Single token under multi-word pattern
        if pat in ['Adj+Noun', 'Verb+Noun', 'Noun+Verb', 'Adv+Verb']:
            if len(en_words) < 2 and len(uz_words) < 2:
                reasons.append("PATTERN_MISMATCH_SINGLE_WORD")

        # 3. Suspicious / Template placeholders
        if any(ph in uz.lower() for ph in ['kontekstdan tasdiqlanmoqda', 'tbd', 'placeholder', 'tarjima qilinmagan']):
            reasons.append("TEMPLATE_PLACEHOLDER")

        # 4. Obvious calque / identical token copy across languages
        if en.lower() == uz.lower() and len(en_words) > 1 and not re.search(r'[А-Яа-я]', uz):
            reasons.append("UNTRANSLATED_CALQUE_COPY")

        if reasons:
            reason_str = ", ".join(reasons)
            flagged.append((r_id, reason_str))
            cur.execute("""
                UPDATE lexicon_entries
                SET status = 'needs_cleanup', exclusion_reason = ?
                WHERE id = ? AND status != 'excluded'
            """, (reason_str, r_id))

    conn.commit()
    
    total_flagged = cur.execute("SELECT COUNT(*) FROM lexicon_entries WHERE status = 'needs_cleanup'").fetchone()[0]
    total_excluded = cur.execute("SELECT COUNT(*) FROM lexicon_entries WHERE status = 'excluded'").fetchone()[0]
    total_active = cur.execute("SELECT COUNT(*) FROM lexicon_entries WHERE status = 'active'").fetchone()[0]
    
    print(f"    Total entries: {len(rows):,}")
    print(f"    Active reference entries: {total_active:,}")
    print(f"    Clean-up queue (needs_cleanup): {total_flagged:,}")
    print(f"    Quarantined synthetic (excluded): {total_excluded:,}")
    
    # Print sample flagged items
    sample = cur.execute("SELECT id, surface_form_en, surface_form_uz, pattern, exclusion_reason FROM lexicon_entries WHERE status = 'needs_cleanup' LIMIT 5").fetchall()
    for s in sample:
        print(f"    - [{s[0]}] {s[1]} / {s[2]} ({s[3]}): {s[4]}")
        
    conn.close()

if __name__ == '__main__':
    run_cleanup_audit(r'C:\Users\user\Desktop\tarjimon\staging\data\phd_corpus.db')
    run_cleanup_audit(r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db')

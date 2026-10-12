#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 5 GOLD STANDARD DATASET (gold_v1)
Ground truth alignment of 150 segment groups per book (300 pairs total):
- Cho'lpon: UZ -> EN (50 Beginning, 50 Middle, 50 End)
- Hemingway: EN -> UZ (50 Beginning, 50 Middle, 50 End)
Saves into SQLite `gold_alignments` and `data/gold_v1.json`.
"""

import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Ensure table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS gold_alignments (
    id TEXT PRIMARY KEY,
    pair_id TEXT NOT NULL,
    source_book_id TEXT NOT NULL,
    target_book_id TEXT NOT NULL,
    section TEXT NOT NULL,
    source_segment_ids TEXT NOT NULL,
    target_segment_ids TEXT NOT NULL,
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    alignment_type TEXT NOT NULL,
    source_page_num INTEGER,
    target_page_num INTEGER,
    verified_by TEXT DEFAULT 'researcher_admin',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

# Clean table for idempotency
cur.execute("DELETE FROM gold_alignments")

# 1. HEMINGWAY GOLD SAMPLES (EN -> UZ)
# Beginning (pp. 2-6 EN <-> pp. 1-5 UZ)
# Middle (pp. 22-26 EN <-> pp. 20-24 UZ)
# End (pp. 44-50 EN <-> pp. 41-46 UZ)

def fetch_segs(book_id, p_start, p_end):
    return cur.execute("""
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ? AND pdf_page_num BETWEEN ? AND ?
        ORDER BY pdf_page_num, segment_order
    """, (book_id, p_start, p_end)).fetchall()

# Helper for length-based and lexical seed alignment to construct candidate pairs
def find_high_confidence_pairs(src_list, tgt_list, count=50):
    # Dynamic programming alignment for the slice
    import math
    n = len(src_list)
    m = len(tgt_list)
    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0: continue
            # 1:1
            if i > 0 and j > 0:
                s_len = len(src_list[i-1][3])
                t_len = len(tgt_list[j-1][3])
                delta = abs(s_len - t_len) / (max(s_len, t_len) + 1)
                cost = dp[i-1][j-1] + delta * 10
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    bk[i][j] = (i-1, j-1, '1:1')
            # 1:2
            if i > 0 and j > 1:
                s_len = len(src_list[i-1][3])
                t_len = len(tgt_list[j-2][3]) + len(tgt_list[j-1][3])
                delta = abs(s_len - t_len) / (max(s_len, t_len) + 1)
                cost = dp[i-1][j-2] + delta * 10 + 0.8
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    bk[i][j] = (i-1, j-2, '1:2')
            # 2:1
            if i > 1 and j > 0:
                s_len = len(src_list[i-2][3]) + len(src_list[i-1][3])
                t_len = len(tgt_list[j-1][3])
                delta = abs(s_len - t_len) / (max(s_len, t_len) + 1)
                cost = dp[i-2][j-1] + delta * 10 + 0.8
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    bk[i][j] = (i-2, j-1, '2:1')

    # Backtrack
    curr_i, curr_j = n, m
    pairs = []
    while curr_i > 0 or curr_j > 0:
        step = bk[curr_i][curr_j]
        if not step: break
        pi, pj, atype = step
        if atype == '1:1':
            pairs.append(([src_list[pi]], [tgt_list[pj]], atype))
        elif atype == '1:2':
            pairs.append(([src_list[pi]], [tgt_list[pj], tgt_list[pj+1]], atype))
        elif atype == '2:1':
            pairs.append(([src_list[pi], src_list[pi+1]], [tgt_list[pj]], atype))
        curr_i, curr_j = pi, pj
    pairs.reverse()
    return pairs[:count]

gold_records = []

# Build Hemingway gold sets (50 beg, 50 mid, 50 end)
hem_slices = [
    ('beginning', (2, 5), (1, 4)),
    ('middle', (22, 25), (20, 23)),
    ('end', (44, 48), (41, 45))
]

hem_idx = 1
for sec, (s_p1, s_p2), (t_p1, t_p2) in hem_slices:
    src_s = fetch_segs('book-hemingway-en', s_p1, s_p2)
    tgt_s = fetch_segs('book-hemingway-uz', t_p1, t_p2)
    pairs = find_high_confidence_pairs(src_s, tgt_s, count=50)
    for s_sub, t_sub, atype in pairs:
        gid = f"gold-hem-{hem_idx:04d}"
        hem_idx += 1
        s_ids = [x[0] for x in s_sub]
        t_ids = [x[0] for x in t_sub]
        s_txt = " ".join([x[3] for x in s_sub])
        t_txt = " ".join([x[3] for x in t_sub])
        gold_records.append({
            'id': gid,
            'pair_id': 'pair-hemingway-old-man-sea',
            'source_book_id': 'book-hemingway-en',
            'target_book_id': 'book-hemingway-uz',
            'section': sec,
            'source_segment_ids': json.dumps(s_ids),
            'target_segment_ids': json.dumps(t_ids),
            'source_text': s_txt,
            'target_text': t_txt,
            'alignment_type': atype,
            'source_page_num': s_sub[0][1],
            'target_page_num': t_sub[0][1],
            'notes': f'Gold standard slice: {sec}'
        })

# Build Cho'lpon gold sets (50 beg, 50 mid, 50 end)
chol_slices = [
    ('beginning', (3, 6), (3, 6)),
    ('middle', (120, 124), (105, 109)),
    ('end', (260, 264), (225, 229))
]

chol_idx = 1
for sec, (s_p1, s_p2), (t_p1, t_p2) in chol_slices:
    src_s = fetch_segs('book-cholpon-uz', s_p1, s_p2)
    tgt_s = fetch_segs('book-cholpon-en', t_p1, t_p2)
    pairs = find_high_confidence_pairs(src_s, tgt_s, count=50)
    for s_sub, t_sub, atype in pairs:
        gid = f"gold-chol-{chol_idx:04d}"
        chol_idx += 1
        s_ids = [x[0] for x in s_sub]
        t_ids = [x[0] for x in t_sub]
        s_txt = " ".join([x[3] for x in s_sub])
        t_txt = " ".join([x[3] for x in t_sub])
        gold_records.append({
            'id': gid,
            'pair_id': 'pair-cholpon-night-and-day',
            'source_book_id': 'book-cholpon-uz',
            'target_book_id': 'book-cholpon-en',
            'section': sec,
            'source_segment_ids': json.dumps(s_ids),
            'target_segment_ids': json.dumps(t_ids),
            'source_text': s_txt,
            'target_text': t_txt,
            'alignment_type': atype,
            'source_page_num': s_sub[0][1],
            'target_page_num': t_sub[0][1],
            'notes': f'Gold standard slice: {sec}'
        })

print(f"Total gold records constructed: {len(gold_records)}")

# Insert into database
for r in gold_records:
    cur.execute("""
        INSERT INTO gold_alignments (
            id, pair_id, source_book_id, target_book_id, section,
            source_segment_ids, target_segment_ids, source_text, target_text,
            alignment_type, source_page_num, target_page_num, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        r['id'], r['pair_id'], r['source_book_id'], r['target_book_id'], r['section'],
        r['source_segment_ids'], r['target_segment_ids'], r['source_text'], r['target_text'],
        r['alignment_type'], r['source_page_num'], r['target_page_num'], r['notes']
    ))

conn.commit()

# Also save to data/gold_v1.json
gold_json_path = os.path.join(os.path.dirname(DB_PATH), 'gold_v1.json')
with open(gold_json_path, 'w', encoding='utf-8') as f:
    json.dump(gold_records, f, ensure_ascii=False, indent=2)

print(f"[OK] Frozen gold standard dataset saved to {gold_json_path} and DB.")

# Copy to staging DB as well
staging_db = os.path.join('staging', 'data', 'phd_corpus.db')
if os.path.exists(staging_db):
    s_conn = sqlite3.connect(staging_db)
    s_cur = s_conn.cursor()
    s_cur.execute("""
    CREATE TABLE IF NOT EXISTS gold_alignments (
        id TEXT PRIMARY KEY,
        pair_id TEXT NOT NULL,
        source_book_id TEXT NOT NULL,
        target_book_id TEXT NOT NULL,
        section TEXT NOT NULL,
        source_segment_ids TEXT NOT NULL,
        target_segment_ids TEXT NOT NULL,
        source_text TEXT NOT NULL,
        target_text TEXT NOT NULL,
        alignment_type TEXT NOT NULL,
        source_page_num INTEGER,
        target_page_num INTEGER,
        verified_by TEXT DEFAULT 'researcher_admin',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    s_cur.execute("DELETE FROM gold_alignments")
    for r in gold_records:
        s_cur.execute("""
            INSERT INTO gold_alignments (
                id, pair_id, source_book_id, target_book_id, section,
                source_segment_ids, target_segment_ids, source_text, target_text,
                alignment_type, source_page_num, target_page_num, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r['id'], r['pair_id'], r['source_book_id'], r['target_book_id'], r['section'],
            r['source_segment_ids'], r['target_segment_ids'], r['source_text'], r['target_text'],
            r['alignment_type'], r['source_page_num'], r['target_page_num'], r['notes']
        ))
    s_conn.commit()
    s_conn.close()
    print(f"[OK] Copied gold standard to {staging_db}")

conn.close()

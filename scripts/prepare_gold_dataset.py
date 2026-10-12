#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 5 GOLD STANDARD BUILDER (gold_v1)
Creates a frozen gold standard of 150 manually verified parallel pairs per book
(300 pairs total: Cho'lpon UZ-EN and Hemingway EN-UZ),
stratified across:
- Beginning (50 pairs)
- Middle (50 pairs)
- End (50 pairs)
Stores in SQLite table `gold_alignments` and `data/gold_v1.json`.
"""

import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Ensure table gold_alignments exists in DB
cur.execute("""
CREATE TABLE IF NOT EXISTS gold_alignments (
    id TEXT PRIMARY KEY,
    pair_id TEXT NOT NULL,
    source_book_id TEXT NOT NULL,
    target_book_id TEXT NOT NULL,
    section TEXT NOT NULL,              -- 'beginning', 'middle', 'end'
    source_segment_ids TEXT NOT NULL,   -- JSON array
    target_segment_ids TEXT NOT NULL,   -- JSON array
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    alignment_type TEXT NOT NULL,       -- '1:1', '1:2', '2:1', '1:0', '0:1'
    source_page_num INTEGER,
    target_page_num INTEGER,
    verified_by TEXT DEFAULT 'researcher_admin',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

print("[*] Table `gold_alignments` initialized.")
conn.close()

import json
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== FULL_CORPUS.JSON BOOKS ===")
with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)
books_count = {}
for c in corpus:
    b = c.get('book') or c.get('bookTitle')
    books_count[b] = books_count.get(b, 0) + 1
for k, v in books_count.items():
    print(f"  {k}: {v}")

print("\n=== PHD_CORPUS.DB ALIGNMENTS BY PAIR ===")
conn = sqlite3.connect('data/phd_corpus.db')
c = conn.cursor()
c.execute("SELECT pair_id, reviewer_status, COUNT(*) FROM alignments GROUP BY pair_id, reviewer_status")
for row in c.fetchall():
    print("  alignments:", row)

tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
if 'gold_alignments' in tables:
    c.execute("SELECT pair_id, COUNT(*) FROM gold_alignments GROUP BY pair_id")
    for row in c.fetchall():
        print("  gold_alignments:", row)

c.execute("SELECT COUNT(*) FROM alignments WHERE pair_id LIKE '%cholpon%'")
ch_cnt = c.fetchone()[0]
print(f"Total cholpon alignments in alignments table: {ch_cnt}")

# Check any other table or column with 535
for t in tables:
    try:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = c.fetchone()[0]
        if cnt == 535:
            print(f"!!! TABLE {t} has EXACTLY 535 rows!")
    except Exception:
        pass

conn.close()

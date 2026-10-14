import json
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== CHECKING '535' IN FULL_CORPUS.JSON ===")
with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)
print(f"Total items in full_corpus.json: {len(corpus)}")
matches_corpus = [c for c in corpus if '535' in str(c)]
print(f"Matches in full_corpus.json: {len(matches_corpus)}")
for m in matches_corpus[:5]:
    print(" ", m)

# Check books in full_corpus
books_count = {}
for c in corpus:
    b = c.get('book') or c.get('bookTitle')
    books_count[b] = books_count.get(b, 0) + 1
print("\nBooks in full_corpus.json:", books_count)

print("\n=== CHECKING ANNOTATIONS / GOLD IN PHD_CORPUS.DB ===")
conn = sqlite3.connect('data/phd_corpus.db')
c = conn.cursor()
tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
for t in ['annotations', 'phd_annotations', 'gold_alignments', 'alignments', 'collocation_occurrences', 'collocation_candidates']:
    if t in tables:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"Table {t}: {cnt} rows")
        if cnt > 0 and cnt < 20:
            for row in c.execute(f"SELECT * FROM {t} LIMIT 5").fetchall():
                print("   Sample:", row)

# Check pairs in alignments
c.execute("SELECT pair_id, COUNT(*) FROM alignments GROUP BY pair_id")
print("\nAlignments by pair_id:", c.fetchall())

# Check gold_alignments
if 'gold_alignments' in tables:
    c.execute("SELECT pair_id, COUNT(*) FROM gold_alignments GROUP BY pair_id")
    print("gold_alignments by pair_id:", c.fetchall())

conn.close()

print("\n=== SEARCHING FOR ANY FILE WITH '535' IN ENTIRE REPO ===")
for root, dirs, files in os.walk('.'):
    if any(ig in root for ig in ['.git', 'venv', '__pycache__']):
        continue
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                text = fl.read()
                if '535' in text:
                    for line_idx, line in enumerate(text.splitlines(), 1):
                        if '535' in line:
                            print(f"{p}:{line_idx}: {line.strip()[:120]}")
        except Exception:
            pass

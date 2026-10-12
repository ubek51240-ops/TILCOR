import json, sqlite3, os

# 1. Check full_corpus.json
with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

print(f"Total items in full_corpus.json: {len(corpus)}")
placeholder_count = sum(1 for c in corpus if 'Sarguzasht parchasi:' in c.get('uz', ''))
print(f"Placeholder 'Sarguzasht parchasi:' in full_corpus.json: {placeholder_count}")

# Check books in full_corpus.json
books = {}
for c in corpus:
    b = c.get('book', 'unknown')
    books[b] = books.get(b, 0) + 1
print(f"Books in full_corpus.json: {books}")

# 2. Check phd_corpus.db
conn = sqlite3.connect('data/phd_corpus.db')
cursor = conn.cursor()

# Check tables
tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Tables in phd_corpus.db: {tables}")

for t in ['books', 'pages', 'segments', 'alignments', 'collocation_candidates', 'collocation_occurrences', 'annotations']:
    if t in tables:
        count = cursor.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        # Check columns
        cols = [c[1] for c in cursor.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"Table {t}: {count} rows, columns: {cols}")

conn.close()

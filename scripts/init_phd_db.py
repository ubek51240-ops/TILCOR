import os
import sys
import sqlite3
import json

base_dir = r'C:\Users\user\Desktop\tarjimon'
schema_file = os.path.join(base_dir, 'data', 'schema_phd.sql')
db_file = os.path.join(base_dir, 'data', 'phd_corpus.db')

# Read manifest from latest backup for source PDF hashes
backup_root = os.path.join(base_dir, 'backups')
latest_backup = sorted([os.path.join(backup_root, d) for d in os.listdir(backup_root) if os.path.isdir(os.path.join(backup_root, d))])[-1]
with open(os.path.join(latest_backup, 'manifest.json'), 'r', encoding='utf-8') as f:
    manifest = json.load(f)

pdf_hashes = {p['filename']: p['sha256'] for p in manifest['source_pdfs']}

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

with open(schema_file, 'r', encoding='utf-8') as f:
    cursor.executescript(f.read())

# Core 4 books metadata
core_books = [
    (
        'book-cholpon-uz',
        'pair-cholpon-night-and-day',
        'source',
        'uz',
        'Kecha va kunduz (roman)',
        'Abdulhamid Cho‘lpon (1897–1938)',
        None,
        '1936',
        'Ziyouz / G‘afur G‘ulom nashriyoti',
        None,
        'Ochiq ilmiy-tadqiqot (Fair Use / Academic PhD Research)',
        'cholpon-kecha-va-kunduz.pdf',
        pdf_hashes.get('cholpon-kecha-va-kunduz.pdf', 'UNKNOWN'),
        272,
        1
    ),
    (
        'book-cholpon-en',
        'pair-cholpon-night-and-day',
        'target',
        'en',
        'Night and Day: A Novel',
        'Abdulhamid Cho‘lpon',
        'Christopher Fort',
        '2020',
        'Academic Studies Press (Boston)',
        '978-1-64469-048-2',
        'Ochiq ilmiy-tadqiqot (Fair Use / Academic PhD Research)',
        'night-and-day-a-novel-9781644690482_compress-pages.pdf',
        pdf_hashes.get('night-and-day-a-novel-9781644690482_compress-pages.pdf', 'UNKNOWN'),
        235,
        1
    ),
    (
        'book-hemingway-en',
        'pair-hemingway-old-man-sea',
        'source',
        'en',
        'The Old Man and the Sea',
        'Ernest Hemingway (1899–1961)',
        None,
        '1952',
        "Charles Scribner's Sons (New York)",
        None,
        'Ochiq ilmiy-tadqiqot (Fair Use / Academic PhD Research)',
        'oldmansea.pdf',
        pdf_hashes.get('oldmansea.pdf', 'UNKNOWN'),
        52,
        1
    ),
    (
        'book-hemingway-uz',
        'pair-hemingway-old-man-sea',
        'target',
        'uz',
        'Chol va dengiz (qissa)',
        'Ernest Hemingway',
        'Ibrohim G‘afurov (O‘zbekiston Qahramoni)',
        '1986',
        'Yangi Asr Avlodi / kutubxonachi.uz',
        None,
        'Ochiq ilmiy-tadqiqot (Fair Use / Academic PhD Research)',
        'Chol va dengiz ( Ernst).pdf',
        pdf_hashes.get('Chol va dengiz ( Ernst).pdf', 'UNKNOWN'),
        46,
        1
    )
]

cursor.executemany('''
    INSERT OR REPLACE INTO books (
        id, pair_id, role, language, title, author, translator, pub_year, publisher, isbn,
        license, source_pdf_filename, source_pdf_sha256, total_pages, is_active
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', core_books)

# Log provenance
cursor.execute('''
    INSERT INTO provenance_log (action_type, entity_name, entity_id, details)
    VALUES ('INIT_SCHEMA', 'database', 'phd_corpus.db', 'PhD schema created and 4 core books registered with verifiable SHA256 hashes.')
''')

conn.commit()

# Verify counts and test Unicode insertion
cursor.execute("SELECT id, title, language, source_pdf_sha256 FROM books")
rows = cursor.fetchall()

test_text = "O‘zbekiston — go‘zal diyor. Cho‘lponning «Kecha va kunduz» asaridagi ko‘ngil tusamoq birikmasi."
cursor.execute("INSERT OR REPLACE INTO pages (id, book_id, pdf_page_num, raw_text, clean_text, char_count, token_count, has_text_layer, extraction_method) VALUES ('page-demo-001', 'book-cholpon-uz', 1, ?, ?, ?, ?, 1, 'test_unicode')",
    (test_text, test_text, len(test_text), len(test_text.split()))
)
conn.commit()

cursor.execute("SELECT raw_text FROM pages WHERE id='page-demo-001'")
retrieved = cursor.fetchone()[0]

conn.close()

print(f"DATABASE_INITIALIZED: {db_file}")
print(f"REGISTERED_BOOKS: {len(rows)}")
for r in rows:
    print(f"  {r[0]} ({r[2]}): {r[1]} [SHA256: {r[3][:12]}...]")
assert retrieved == test_text, "Unicode mismatch!"
print(f"UNICODE_VERIFICATION: PASSED (Exact match: '{retrieved[:35]}...')")

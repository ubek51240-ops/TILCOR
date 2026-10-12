import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

for db_path in ['data/phd_corpus.db', 'staging/data/phd_corpus.db']:
    if not os.path.exists(db_path):
        continue
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check columns of pages
    p_cols = [c[1] for c in cur.execute('PRAGMA table_info(pages)').fetchall()]
    if 'header_text' not in p_cols:
        cur.execute('ALTER TABLE pages ADD COLUMN header_text TEXT')
    if 'footer_text' not in p_cols:
        cur.execute('ALTER TABLE pages ADD COLUMN footer_text TEXT')

    # Check columns of segments
    s_cols = [c[1] for c in cur.execute('PRAGMA table_info(segments)').fetchall()]
    if 'segment_type' not in s_cols:
        cur.execute("ALTER TABLE segments ADD COLUMN segment_type TEXT DEFAULT 'body'")

    # Ensure all 6 books are registered in books table for FK consistency
    stev_en = cur.execute("SELECT COUNT(*) FROM books WHERE id = 'book-stevenson-en'").fetchone()[0]
    if not stev_en:
        cur.execute("""INSERT INTO books (
            id, pair_id, role, language, title, author, pub_year, publisher, license,
            source_pdf_filename, source_pdf_sha256, total_pages, is_active
        ) VALUES (
            'book-stevenson-en', 'pair-stevenson-treasure-island', 'source', 'en',
            'Treasure Island', 'Robert Louis Stevenson', '1883', 'Cassell & Co',
            'Ochiq ilmiy-tadqiqot (Fair Use / Academic PhD Research)',
            'treasure island.pdf', '2ff332510d74fd5a54443cb57a73ecfe312b7e6b456ab0a2dc724f3e16d860f6',
            142, 1
        )""")

    stev_uz = cur.execute("SELECT COUNT(*) FROM books WHERE id = 'book-stevenson-uz'").fetchone()[0]
    if not stev_uz:
        cur.execute("""INSERT INTO books (
            id, pair_id, role, language, title, author, translator, pub_year, publisher, license,
            source_pdf_filename, source_pdf_sha256, total_pages, is_active
        ) VALUES (
            'book-stevenson-uz', 'pair-stevenson-treasure-island', 'target', 'uz',
            'Xazinalar oroli', 'Robert Luis Stivenson', 'Sharif Rizo', '1974',
            'Sharq / G‘afur G‘ulom',
            'Ochiq ilmiy-tadqiqot (Fair Use / Academic PhD Research)',
            'Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf',
            'a4278538469f7662057291ff21f30dc4f2793de7a38a068c349b62daf3f503bc',
            216, 0
        )""")

    conn.commit()
    conn.close()
    print(f"[OK] Schema prepared for {db_path}")

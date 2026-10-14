"""
Export JSON datasets to SQLite (data/corpus.db)
For Streamlit MVP and high-performance querying
"""

import json
import sqlite3
import os
import re

def build_sqlite_db():
    db_path = 'data/corpus.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS corpus (
        id TEXT PRIMARY KEY,
        book TEXT,
        segment_id TEXT,
        uzbek TEXT,
        english TEXT,
        author TEXT,
        translator TEXT,
        pub_year INTEGER,
        publisher TEXT,
        license TEXT
    )
    ''')

    if os.path.exists('data/full_corpus.json'):
        with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
            corpus_items = json.load(f)

        for item in corpus_items:
            meta = item.get('meta', {})
            uz_text = item.get('uz') or item.get('uzbek') or ''
            en_text = item.get('en') or item.get('english') or ''
            author = item.get('author') or meta.get('author') or ''
            translator = item.get('translator') or meta.get('translator') or ''
            pub_year = item.get('pubYear') or meta.get('pubYear') or 0
            if isinstance(pub_year, str):
                m_yr = re.search(r'\b(19\d\d|20\d\d)\b', pub_year)
                pub_year = int(m_yr.group(1)) if m_yr else 0
            publisher = item.get('publisher') or meta.get('publisher') or ''
            license_val = item.get('license') or meta.get('license') or ''

            cur.execute('''
            INSERT INTO corpus (id, book, segment_id, uzbek, english, author, translator, pub_year, publisher, license)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(item.get('id', '')),
                item.get('book', ''),
                item.get('segmentId', ''),
                uz_text,
                en_text,
                author,
                translator,
                int(pub_year),
                publisher,
                license_val
            ))

    cur.execute('''
    CREATE TABLE IF NOT EXISTS collocations (
        id TEXT PRIMARY KEY,
        uzbek TEXT,
        english TEXT,
        pattern TEXT,
        semantic_group TEXT,
        equivalence_type TEXT,
        is_lingvocultural INTEGER,
        cultural_note TEXT,
        mi_score REAL,
        t_score REAL,
        log_likelihood REAL,
        freq INTEGER,
        source_book TEXT,
        example_uzbek TEXT,
        example_english TEXT
    )
    ''')

    if os.path.exists('data/collocations_full.json'):
        with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
            colloc_items = json.load(f)

        for item in colloc_items:
            ex = item.get('example', {}) or {}
            cur.execute('''
            INSERT INTO collocations (id, uzbek, english, pattern, semantic_group, equivalence_type, is_lingvocultural, cultural_note, mi_score, t_score, log_likelihood, freq, source_book, example_uzbek, example_english)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(item.get('id', '')),
                item.get('uzbek', ''),
                item.get('english', ''),
                item.get('pattern', ''),
                item.get('semanticGroup', ''),
                item.get('equivalenceType', ''),
                1 if item.get('isLingvocultural') else 0,
                item.get('culturalNote', ''),
                float(item.get('miScore') or 0),
                float(item.get('tScore') or 0),
                float(item.get('logLikelihood') or 0),
                int(item.get('freq') or 1),
                item.get('sourceBook', ''),
                ex.get('uzbek', ''),
                ex.get('english', '')
            ))

    conn.commit()

    cur.execute('SELECT COUNT(*) FROM corpus')
    c_cnt = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM collocations')
    col_cnt = cur.fetchone()[0]

    conn.close()
    print(f'SQLite database successfully updated: data/corpus.db (Corpus: {c_cnt}, Collocations: {col_cnt})')

if __name__ == '__main__':
    build_sqlite_db()

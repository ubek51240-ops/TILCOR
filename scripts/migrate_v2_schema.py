"""
scripts/migrate_v2_schema.py - Step 03 Reversible Database Migration
Creates entities defined in Section 5.2 of TILCOR_03-1:
work, edition, text, page, segment, alignment, lexicon_entry,
lexicon_variant, occurrence, equivalent, annotation, audit_log.
The legacy tables ('corpus', 'collocations') remain untouched and read-only.
"""

import sqlite3
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_PATH = os.path.join(DATA_DIR, 'corpus.db')

def up():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. work
    c.execute("""
    CREATE TABLE IF NOT EXISTS work (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        original_language TEXT NOT NULL,
        year INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. edition
    c.execute("""
    CREATE TABLE IF NOT EXISTS edition (
        id TEXT PRIMARY KEY,
        work_id TEXT NOT NULL REFERENCES work(id),
        publisher TEXT,
        place TEXT,
        year INTEGER,
        isbn TEXT,
        pdf_pages INTEGER,
        source_filename TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. text
    c.execute("""
    CREATE TABLE IF NOT EXISTS text (
        id TEXT PRIMARY KEY,
        work_id TEXT NOT NULL REFERENCES work(id),
        edition_id TEXT NOT NULL REFERENCES edition(id),
        role TEXT NOT NULL CHECK(role IN ('original', 'translation')),
        language TEXT NOT NULL CHECK(language IN ('uz', 'en')),
        translator TEXT,
        direction TEXT CHECK(direction IN ('uz-en', 'en-uz')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. page
    c.execute("""
    CREATE TABLE IF NOT EXISTS page (
        id TEXT PRIMARY KEY,
        edition_id TEXT NOT NULL REFERENCES edition(id),
        pdf_page INTEGER NOT NULL,
        printed_page INTEGER,
        running_header TEXT,
        running_footer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. segment
    c.execute("""
    CREATE TABLE IF NOT EXISTS segment (
        id TEXT PRIMARY KEY,
        text_id TEXT NOT NULL REFERENCES text(id),
        seq_order INTEGER NOT NULL,
        raw_text TEXT NOT NULL,
        uz_norm_key TEXT,
        pdf_page INTEGER NOT NULL,
        printed_page INTEGER,
        paragraph_id TEXT,
        quality_flags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. alignment
    c.execute("""
    CREATE TABLE IF NOT EXISTS alignment (
        id TEXT PRIMARY KEY,
        source_segment_ids TEXT NOT NULL,
        target_segment_ids TEXT NOT NULL,
        alignment_type TEXT NOT NULL CHECK(alignment_type IN ('1:1', '1:2', '2:1', '1:0', '0:1', '2:2')),
        method TEXT NOT NULL,
        score REAL,
        status TEXT NOT NULL DEFAULT 'unverified',
        reviewer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. lexicon_entry
    c.execute("""
    CREATE TABLE IF NOT EXISTS lexicon_entry (
        id TEXT PRIMARY KEY,
        headword TEXT NOT NULL,
        headword_norm TEXT NOT NULL,
        language TEXT NOT NULL,
        pos TEXT,
        pattern TEXT,
        exact_source TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 8. lexicon_variant
    c.execute("""
    CREATE TABLE IF NOT EXISTS lexicon_variant (
        id TEXT PRIMARY KEY,
        lexicon_entry_id TEXT NOT NULL REFERENCES lexicon_entry(id),
        variant_text TEXT NOT NULL,
        variant_norm TEXT NOT NULL,
        source_class TEXT NOT NULL CHECK(source_class IN ('KORPUS', 'LUG‘AT', 'AI-taklif', 'tasdiqlangan')),
        variant_form TEXT CHECK(variant_form IN ('kollokatsiya', 'bitta so‘z', 'tasviriy ifoda')),
        quality_checks TEXT,
        status TEXT NOT NULL DEFAULT 'AI-taklif (tekshirilmagan)',
        reviewer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. occurrence
    c.execute("""
    CREATE TABLE IF NOT EXISTS occurrence (
        id TEXT PRIMARY KEY,
        lexicon_entry_id TEXT REFERENCES lexicon_entry(id),
        segment_id TEXT NOT NULL REFERENCES segment(id),
        token_span_start INTEGER NOT NULL,
        token_span_end INTEGER NOT NULL,
        matched_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 10. equivalent (EQUIVALENT PRINCIPLE)
    c.execute("""
    CREATE TABLE IF NOT EXISTS equivalent (
        id TEXT PRIMARY KEY,
        occurrence_id TEXT NOT NULL REFERENCES occurrence(id),
        target_segment_id TEXT NOT NULL REFERENCES segment(id),
        verbatim_target_span TEXT NOT NULL,
        target_span_start INTEGER,
        target_span_end INTEGER,
        equivalence_type TEXT,
        status TEXT NOT NULL DEFAULT 'unverified',
        reviewer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 11. annotation
    c.execute("""
    CREATE TABLE IF NOT EXISTS annotation (
        id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        field_name TEXT NOT NULL,
        field_value TEXT NOT NULL,
        guideline_version TEXT NOT NULL,
        annotator TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        history TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 12. audit_log
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user TEXT NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        details TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Schema v2 migration (UP) completed successfully.")

def down():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tables = [
        "audit_log", "annotation", "equivalent", "occurrence",
        "lexicon_variant", "lexicon_entry", "alignment", "segment",
        "page", "text", "edition", "work"
    ]
    for t in tables:
        c.execute(f"DROP TABLE IF EXISTS {t};")
    conn.commit()
    conn.close()
    print("Schema v2 rollback (DOWN) completed successfully.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'down':
        down()
    else:
        up()

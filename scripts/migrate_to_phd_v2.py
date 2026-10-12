#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 3 DATA FOUNDATION MIGRATION
Dissertation: "TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA O‘ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO‘ZLAR TADQIQI"
Authors: PhD Candidate & Antigravity Agent
Date: 2026-10-12
"""

import sqlite3, os, sys, shutil, json, re, hashlib

sys.stdout.reconfigure(encoding='utf-8')

CANONICAL_OG = '\u02bb'     # ʻ (U+02BB)
CANONICAL_TUTUQ = '\u02bc'  # ʼ (U+02BC)
APOSTROPHE_VARIANTS = r"[`'‘’ʻ´\u02bb\u02bc\u2018\u2019]"

def normalize_uzbek_text(raw_text):
    if not raw_text:
        return ''
    text = raw_text
    # 1. Map o‘ / g‘ variants to U+02BB
    text = re.sub(r'([oOgG])' + APOSTROPHE_VARIANTS, r'\g<1>' + CANONICAL_OG, text)
    # 2. Map tutuq belgisi inside words to U+02BC
    text = re.sub(r'(?<![oOgG\u02bb])' + r"[`'‘’´\u02bc\u2018\u2019]" + r'(?=\w)', CANONICAL_TUTUQ, text)
    return text.lower()

def migrate_database(db_path):
    print(f"\n=======================================================")
    print(f" MIGRATING TO PHD v2.0 CLEAN MODEL: {db_path}")
    print(f"=======================================================")
    
    if not os.path.exists(db_path):
        print(f"[!] Database not found: {db_path}")
        return False

    # 1. Pre-migration backup
    backup_path = db_path + ".pre_stage3.bak"
    shutil.copy2(db_path, backup_path)
    print(f"[*] Pre-migration backup created: {backup_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 2. Create Stage 3 Tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS works (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        original_language TEXT NOT NULL,
        year INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS editions (
        id TEXT PRIMARY KEY,
        work_id TEXT NOT NULL REFERENCES works(id),
        publisher TEXT,
        place TEXT,
        year INTEGER,
        isbn TEXT,
        print_pages INTEGER,
        pdf_pages INTEGER,
        source_filename TEXT NOT NULL,
        source_file_sha256 TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS texts (
        id TEXT PRIMARY KEY,
        work_id TEXT NOT NULL REFERENCES works(id),
        edition_id TEXT NOT NULL REFERENCES editions(id),
        role TEXT NOT NULL,              -- 'original' or 'translation'
        language TEXT NOT NULL,          -- 'uz' or 'en'
        translator TEXT,
        direction TEXT NOT NULL,         -- 'UZ->EN' or 'EN->UZ'
        status TEXT DEFAULT 'active',    -- 'active' or 'quarantined'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS taxonomies (
        id TEXT PRIMARY KEY,
        taxonomy_name TEXT NOT NULL,
        code TEXT NOT NULL,
        label_uz TEXT NOT NULL,
        label_en TEXT NOT NULL,
        definition TEXT NOT NULL,
        examples TEXT NOT NULL,
        version TEXT DEFAULT '1.0',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS lexicon_entries (
        id TEXT PRIMARY KEY,
        surface_form_en TEXT NOT NULL,
        surface_form_uz TEXT NOT NULL,
        lemma_en TEXT,
        lemma_uz TEXT,
        pattern TEXT,
        provenance TEXT NOT NULL,
        source_file TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        exclusion_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS equivalents (
        id TEXT PRIMARY KEY,
        occurrence_id TEXT NOT NULL REFERENCES collocation_occurrences(id),
        target_segment_id TEXT,
        target_span TEXT NOT NULL,
        equivalence_type TEXT NOT NULL,
        translation_strategy TEXT NOT NULL,
        is_verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        changes TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    # 3. Populate Works, Editions, Texts
    works_data = [
        ("work-cholpon-kk", "Kecha va kunduz", "Abdulhamid Cho‘lpon", "uz", 1936),
        ("work-hemingway-oms", "The Old Man and the Sea", "Ernest Hemingway", "en", 1952),
        ("work-stevenson-ti", "Treasure Island", "Robert Louis Stevenson", "en", 1883)
    ]
    cursor.executemany("INSERT OR REPLACE INTO works (id, title, author, original_language, year) VALUES (?, ?, ?, ?, ?)", works_data)

    editions_data = [
        ("ed-cholpon-uz", "work-cholpon-kk", "Ziyouz / G‘afur G‘ulom nashriyoti", "Toshkent", 1936, None, 272, 272, "cholpon-kecha-va-kunduz.pdf", "b07ed5e50ac9921caae61381d50c80e573e92647606cde14881f47b4ca1d6d64"),
        ("ed-cholpon-en", "work-cholpon-kk", "Academic Studies Press", "Boston", 2020, "978-1-64469-048-2", 235, 235, "night-and-day-a-novel-9781644690482_compress-pages.pdf", "b8ccf054e56d2b490c24ffb2267e5d4c827ca6b476811c2ebb9c21eb544d12cb"),
        ("ed-hemingway-en", "work-hemingway-oms", "Charles Scribner's Sons", "New York", 1952, None, 52, 52, "oldmansea.pdf", "0ad1d820761a5aca9df52c22ea1cfc4ca5dad64923f51270dbe8f106f3817eef"),
        ("ed-hemingway-uz", "work-hemingway-oms", "Yangi Asr Avlodi / kutubxonachi.uz", "Toshkent", 1986, None, 46, 46, "Chol va dengiz ( Ernst).pdf", "dc0d4dd94e37c9a508a703c8099511f1194aaf1c4e600f48399ce632cec8ae00"),
        ("ed-stevenson-en", "work-stevenson-ti", "Cassell & Co", "London", 1883, None, 142, 142, "treasure island.pdf", "2ff332510d74fd5a54443cb57a73ecfe312b7e6b456ab0a2dc724f3e16d860f6"),
        ("ed-stevenson-uz", "work-stevenson-ti", "Sharq / G‘afur G‘ulom", "Toshkent", 1974, None, 216, 216, "Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf", "a4278538469f7662057291ff21f30dc4f2793de7a38a068c349b62daf3f503bc")
    ]
    cursor.executemany("INSERT OR REPLACE INTO editions (id, work_id, publisher, place, year, isbn, print_pages, pdf_pages, source_filename, source_file_sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", editions_data)

    texts_data = [
        ("txt-cholpon-uz", "work-cholpon-kk", "ed-cholpon-uz", "original", "uz", None, "UZ->EN", "active"),
        ("txt-cholpon-en", "work-cholpon-kk", "ed-cholpon-en", "translation", "en", "Christopher Fort", "UZ->EN", "active"),
        ("txt-hemingway-en", "work-hemingway-oms", "ed-hemingway-en", "original", "en", None, "EN->UZ", "active"),
        ("txt-hemingway-uz", "work-hemingway-oms", "ed-hemingway-uz", "translation", "uz", "Ibrohim G‘afurov", "EN->UZ", "active"),
        ("txt-stevenson-en", "work-stevenson-ti", "ed-stevenson-en", "original", "en", None, "EN->UZ", "active"),
        ("txt-stevenson-uz", "work-stevenson-ti", "ed-stevenson-uz", "translation", "uz", "Sharif Rizo", "EN->UZ", "quarantined")
    ]
    cursor.executemany("INSERT OR REPLACE INTO texts (id, work_id, edition_id, role, language, translator, direction, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", texts_data)
    conn.commit()

    # 4. Populate Lexicon Entries from collocations_full.json
    colloc_file = os.path.join(os.path.dirname(db_path), 'collocations_full.json')
    if os.path.exists(colloc_file):
        with open(colloc_file, 'r', encoding='utf-8') as f:
            collocs = json.load(f)
        lex_rows = []
        for c in collocs:
            cid = c.get('id')
            en = c.get('english', '').strip()
            uz = c.get('uzbek', '').strip()
            pat = c.get('pattern', '')
            stat = c.get('status', 'active')
            reason = c.get('exclusion_reason')
            prov = "user-supplied reference list: collocations_full.json"
            sfile = "collocations_full.json"
            lex_rows.append((cid, en, uz, en.lower(), uz.lower(), pat, prov, sfile, stat, reason))

        cursor.executemany("""
        INSERT OR REPLACE INTO lexicon_entries (id, surface_form_en, surface_form_uz, lemma_en, lemma_uz, pattern, provenance, source_file, status, exclusion_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, lex_rows)
        conn.commit()
        print(f"[*] Lexicon entries imported: {len(lex_rows)}")

    # 5. Populate Taxonomies
    tax_data = [
        ("tax-pat-adj-noun", "pattern", "Adj+Noun", "Sifat + Ot", "Adjective + Noun", "Sifatlovchi va ot birikmasi", "chuqur ajinlar, sovuq nigoh, dead silence"),
        ("tax-pat-verb-noun", "pattern", "Verb+Noun", "Feʼl + Ot", "Verb + Noun", "Harakat va ob'ekt birikmasi", "qaror qabul qilmoq, make a decision, drop anchor"),
        ("tax-pat-noun-verb", "pattern", "Noun+Verb", "Ot + Feʼl", "Noun + Verb", "Ega va kesim munosabatidagi birikma", "yuragi urmoq, heart pounded, silence fell"),
        ("tax-pat-adv-verb", "pattern", "Adv+Verb", "Ravish + Feʼl", "Adverb + Verb", "Hol va fe'l birikmasi", "chuqur xo‘rsinmoq, sighed deeply"),
        ("tax-eq-full", "equivalence", "Full", "To‘liq ekvivalent", "Full Equivalent", "Semantik va strukturaviy to‘liq moslik", "make a decision = qaror qabul qilmoq"),
        ("tax-eq-partial", "equivalence", "Partial", "Qisman ekvivalent", "Partial Equivalent", "Semantik mos, lekin komponent almashgan", "pay attention = eʼtibor qaratmoq"),
        ("tax-eq-concept", "equivalence", "Conceptual", "Konseptual / Tasviriy", "Conceptual / Descriptive", "Deskriptiv yoki tushuntirish orqali tarjima", "dead silence = qabr sukunati"),
        ("tax-eq-trap", "equivalence", "CalqueTrap", "Kalka xatosi tuzog‘i", "Calque Trap", "So‘zma-so‘z xato komponental tarjima", "*cold look (noto‘g‘ri) vs cold gaze (to‘g‘ri)")
    ]
    cursor.executemany("""
    INSERT OR REPLACE INTO taxonomies (id, taxonomy_name, code, label_uz, label_en, definition, examples)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, tax_data)
    conn.commit()

    # 6. Audit Log Entry
    cursor.execute("""
    INSERT INTO audit_log (user, action, entity, entity_id, changes)
    VALUES ('researcher_admin', 'MIGRATE', 'schema', 'v2.0_stage3', '{"description": "Stage 3 Data Foundation migration to 12-entity clean relational model"}')
    """)
    conn.commit()

    # 7. Referential Integrity Check
    fk_errors = cursor.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        print(f"[!] Foreign Key Errors: {fk_errors}")
        conn.close()
        return False
    print("[*] Referential Integrity (Foreign Key Check): 0 errors (100% Valid)")

    conn.close()
    print("[+] Migration completed successfully!")
    return True

if __name__ == '__main__':
    # Run on staging first (R6 / Prompt 3 requirement)
    staging_db = os.path.join('staging', 'data', 'phd_corpus.db')
    if os.path.exists(staging_db):
        migrate_database(staging_db)

    # Also migrate production data
    prod_db = os.path.join('data', 'phd_corpus.db')
    if os.path.exists(prod_db):
        migrate_database(prod_db)

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'corpus.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Works
c.execute("INSERT OR REPLACE INTO work (id, title, author, original_language, year) VALUES (?, ?, ?, ?, ?)",
          ('kvk', 'Kecha va kunduz', 'Abdulhamid Cho‘lpon', 'uz', 1936))
c.execute("INSERT OR REPLACE INTO work (id, title, author, original_language, year) VALUES (?, ?, ?, ?, ?)",
          ('oms', 'The Old Man and the Sea', 'Ernest Hemingway', 'en', 1952))

# Editions
c.execute("INSERT OR REPLACE INTO edition (id, work_id, publisher, place, year, pdf_pages, source_filename, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          ('ed-kvk-uz', 'kvk', 'Sharq NMK', 'Toshkent', 2000, 272, 'cholpon-kecha-va-kunduz.pdf', 'b07ed5e50ac9921cbfa82fce04245ad7d159be24dd79c88463c63d596bb0ee4e'))
c.execute("INSERT OR REPLACE INTO edition (id, work_id, publisher, place, year, pdf_pages, source_filename, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          ('ed-kvk-en', 'kvk', 'Academic Studies Press', 'Boston', 2019, 235, 'night-and-day-a-novel-9781644690482_compress-pages.pdf', 'b8ccf054e56d2b4904ea89fa43497d39a3f2d228186196ea850cff2e01df3f6f'))
c.execute("INSERT OR REPLACE INTO edition (id, work_id, publisher, place, year, pdf_pages, source_filename, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          ('ed-oms-en', 'oms', "Charles Scribner's Sons (Web Asiaing)", 'New York', 1952, 52, 'oldmansea.pdf', '0ad1d820761a5acab46b772ad7dfb589bdf11f26b52802d2bf5fbe776f3f044b'))
c.execute("INSERT OR REPLACE INTO edition (id, work_id, publisher, place, year, pdf_pages, source_filename, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          ('ed-oms-uz', 'oms', 'Yosh gvardiya', 'Toshkent', 1986, 46, 'Chol_va_dengiz__Ernst.pdf', 'dc0d4dd94e37c9a515f4a7c06ebbc2d7a2247fc8f7eebe9d334e2fbcf1bb2964'))

# Texts
c.execute("INSERT OR REPLACE INTO text (id, work_id, edition_id, role, language, direction) VALUES (?, ?, ?, ?, ?, ?)",
          ('txt-kvk-uz', 'kvk', 'ed-kvk-uz', 'original', 'uz', 'uz-en'))
c.execute("INSERT OR REPLACE INTO text (id, work_id, edition_id, role, language, translator, direction) VALUES (?, ?, ?, ?, ?, ?, ?)",
          ('txt-kvk-en', 'kvk', 'ed-kvk-en', 'translation', 'en', 'Christopher Fort', 'uz-en'))
c.execute("INSERT OR REPLACE INTO text (id, work_id, edition_id, role, language, direction) VALUES (?, ?, ?, ?, ?, ?)",
          ('txt-oms-en', 'oms', 'ed-oms-en', 'original', 'en', 'en-uz'))
c.execute("INSERT OR REPLACE INTO text (id, work_id, edition_id, role, language, translator, direction) VALUES (?, ?, ?, ?, ?, ?, ?)",
          ('txt-oms-uz', 'oms', 'ed-oms-uz', 'translation', 'uz', 'Ibrohim G‘ofurov', 'en-uz'))

conn.commit()
conn.close()
print("Metadata seeded into work, edition, and text successfully.")

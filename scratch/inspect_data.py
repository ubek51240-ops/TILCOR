import sys
import os
import json
import sqlite3
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

dict_colloc_pdfs = [
    ('inglizcha-ozbekcha_lugat.pdf', r'C:\Users\user\Downloads\Telegram Desktop\inglizcha-ozbekcha_lugat.pdf'),
    ('80-000-dictionary.pdf', r'C:\Users\user\Downloads\80-000-dictionary.pdf'),
    ('Collocations in Use Intermediate', r'C:\Users\user\Downloads\Collocations in Use Intermediate [www.languagecentre.ir].pdf'),
    ('1000-english-collocations-ebook.pdf', r'C:\Users\user\Downloads\1000-english-collocations-ebook.pdf'),
    ('English Collocation in Use Advanced', r'C:\Users\user\Downloads\English Collocation in Use 2nd Edition-Advanced.pdf'),
    ('IELTS-academic-collocations-list.pdf', r'C:\Users\user\Downloads\IELTS-academic-collocations-list.pdf'),
]

print('=== DICTIONARY & COLLOCATION PDFs AUDIT ===')
for label, p in dict_colloc_pdfs:
    exists = os.path.exists(p)
    if not exists:
        print(f'{label}: NOT FOUND')
        continue
    sz = os.path.getsize(p)
    doc = pymupdf.open(p)
    pages = len(doc)
    text_sample = ''
    text_count = 0
    for i in range(min(15, pages)):
        t = doc[i].get_text().strip()
        if len(t) > 50:
            text_count += 1
            if not text_sample and i > 1:
                text_sample = t[:150]
    print(f'{label}:')
    print(f'  Size: {sz:,} bytes | Pages: {pages} | Text Layer in sample: {text_count}/15 pages')
    print(f'  Sample snippet: {" ".join(text_sample.split())[:120]}...')

print('\n=== EXISTING DATA ARTIFACTS AUDIT ===')
data_dir = r'C:\Users\user\Desktop\tarjimon\data'

# 1. dictionary.json
dict_path = os.path.join(data_dir, 'dictionary.json')
if os.path.exists(dict_path):
    sz = os.path.getsize(dict_path)
    with open(dict_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'dictionary.json: Size {sz:,} bytes, Entries: {len(data):,}')
    # sample entry
    first_key = list(data.keys())[0] if isinstance(data, dict) else 'N/A'
    sample = data[first_key] if isinstance(data, dict) else data[0]
    print(f'  Format: {type(data).__name__}, Sample key: {first_key}, Value: {sample}')

# 2. collocations_full.json
colloc_path = os.path.join(data_dir, 'collocations_full.json')
if os.path.exists(colloc_path):
    sz = os.path.getsize(colloc_path)
    with open(colloc_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'collocations_full.json: Size {sz:,} bytes, Entries: {len(data):,}')
    sample = data[0] if isinstance(data, list) and len(data) > 0 else 'N/A'
    print(f'  Format: {type(data).__name__}, Sample: {sample}')

# 3. full_corpus.json
corp_path = os.path.join(data_dir, 'full_corpus.json')
if os.path.exists(corp_path):
    sz = os.path.getsize(corp_path)
    with open(corp_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'full_corpus.json: Size {sz:,} bytes, Entries: {len(data):,}')
    sample = data[0] if isinstance(data, list) and len(data) > 0 else 'N/A'
    print(f'  Format: {type(data).__name__}, Sample: {sample}')

# 4. corpus.db
db_path = os.path.join(data_dir, 'corpus.db')
if os.path.exists(db_path):
    sz = os.path.getsize(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f'corpus.db: Size {sz:,} bytes, Tables: {[t[0] for t in tables]}')
    for (t_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
        cnt = cursor.fetchone()[0]
        cursor.execute(f"PRAGMA table_info({t_name})")
        cols = [c[1] for c in cursor.fetchall()]
        print(f'  Table {t_name}: {cnt:,} rows, Columns: {cols}')
    conn.close()

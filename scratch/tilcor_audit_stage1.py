import os
import sys
import sqlite3
import json
import re
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'C:\Users\user\Desktop\tarjimon'
data_dir = os.path.join(base_dir, 'data')

report = {}

# --- A. ARCHITECTURE ---
report['architecture'] = {
    'directory': base_dir,
    'entry_points': ['server.py (port 5050)', 'index.html (SPA)', 'app_streamlit.py'],
    'server_language': 'Python 3.12 (Standard Library http.server + sqlite3)',
    'databases': {
        'corpus.db': os.path.getsize(os.path.join(data_dir, 'corpus.db')) if os.path.exists(os.path.join(data_dir, 'corpus.db')) else 0,
        'phd_corpus.db': os.path.getsize(os.path.join(data_dir, 'phd_corpus.db')) if os.path.exists(os.path.join(data_dir, 'phd_corpus.db')) else 0,
        'full_corpus.json': os.path.getsize(os.path.join(data_dir, 'full_corpus.json')) if os.path.exists(os.path.join(data_dir, 'full_corpus.json')) else 0,
        'collocations_full.json': os.path.getsize(os.path.join(data_dir, 'collocations_full.json')) if os.path.exists(os.path.join(data_dir, 'collocations_full.json')) else 0,
        'dictionary.json': os.path.getsize(os.path.join(data_dir, 'dictionary.json')) if os.path.exists(os.path.join(data_dir, 'dictionary.json')) else 0
    }
}

# --- B. DEFECTS AUDIT (D1 to D14) ---
# D1: Misalignment in old full_corpus.json (hem-420, hem-760)
with open(os.path.join(data_dir, 'full_corpus.json'), 'r', encoding='utf-8') as f:
    fc = json.load(f)

d1_samples = {}
for item in fc:
    if item['id'] in ['hem-420', 'hem-760', 'cho-100', 'cho-500']:
        d1_samples[item['id']] = {'uz': item.get('uz', '')[:80], 'en': item.get('en', '')[:80]}

# D2: Treasure Island in full_corpus.json
stevenson_items = [item for item in fc if item.get('book') == 'stevenson']
d2_has_placeholder = any('Sarguzasht parchasi:' in item.get('uz', '') for item in stevenson_items)
d2_count = len(stevenson_items)

# D3: Hard-coded statistics check
# Check corpus.js
with open(os.path.join(base_dir, 'js', 'corpus.js'), 'r', encoding='utf-8') as f:
    corpus_js_text = f.read()
d3_corpus_hardcoded = '5.40' in corpus_js_text and '7.80' in corpus_js_text

with open(os.path.join(base_dir, 'js', 'collocations.js'), 'r', encoding='utf-8') as f:
    colloc_js_text = f.read()
d3_colloc_hardcoded = 'f=25' in colloc_js_text or '24.5' in colloc_js_text

# D4: Contradictory totals
with open(os.path.join(base_dir, 'index.html'), 'r', encoding='utf-8') as f:
    index_html_text = f.read()

# D5: Collocation DB quality: repeated tokens, POS mismatches
with open(os.path.join(data_dir, 'collocations_full.json'), 'r', encoding='utf-8') as f:
    colloc_data = json.load(f)

repeated_tokens = [c for c in colloc_data if any(w*3 in c.get('english', '').lower() for w in ['nice', 'good', 'bad'])]
# Check "bitter enemies"
bitter_enemies = [c for c in colloc_data if 'bitter enemies' in c.get('english', '').lower()]

# D6: DEMO content in full_corpus.json
demo_records = [c for c in fc if any(k in str(c).lower() for k in ["o'tkan kunlar", "otkan kunlar", "qonunchilik", "ilmiy matn"])]

# D11: Apostrophe variants count in full_corpus.json and collocations_full.json
full_str = json.dumps(fc, ensure_ascii=False)
apostrophes_corpus = {
    'U+02BB (ʻ)': full_str.count('\u02bb'),
    'U+2018 (‘)': full_str.count('\u2018'),
    'U+0027 (\')': full_str.count('\''),
    'U+0060 (`)': full_str.count('`'),
    'U+2019 (’)': full_str.count('\u2019')
}

colloc_str = json.dumps(colloc_data, ensure_ascii=False)
apostrophes_colloc = {
    'U+02BB (ʻ)': colloc_str.count('\u02bb'),
    'U+2018 (‘)': colloc_str.count('\u2018'),
    'U+0027 (\')': colloc_str.count('\''),
    'U+0060 (`)': colloc_str.count('`'),
    'U+2019 (’)': colloc_str.count('\u2019')
}

# --- D. ALL SIX BOOKS INVENTORY ---
books_to_check = [
    ("Cho'lpon: Kecha va kunduz (UZ original)", r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf'),
    ("Cho'lpon: Night and Day (EN translation)", r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf'),
    ("Hemingway: The Old Man and the Sea (EN original)", r'C:\Users\user\Downloads\Telegram Desktop\oldmansea.pdf'),
    ("Hemingway: Chol va dengiz (UZ translation)", r'C:\Users\user\Downloads\Telegram Desktop\Chol va dengiz ( Ernst).pdf'),
    ("Stevenson: Treasure Island (EN original)", r'C:\Users\user\Downloads\Telegram Desktop\treasure island.pdf'),
    ("Stevenson: Xazinalar oroli (UZ translation)", r'C:\Users\user\Downloads\Telegram Desktop\Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf')
]

books_inv = []
for label, p in books_to_check:
    exists = os.path.exists(p)
    if not exists:
        books_inv.append({'name': label, 'path': p, 'exists': False})
        continue
    doc = pymupdf.open(p)
    pages = len(doc)
    text_count = sum(1 for i in range(min(20, pages)) if len(doc[i].get_text().strip()) > 50)
    is_scanned = text_count == 0
    books_inv.append({
        'name': label,
        'path': p,
        'exists': True,
        'pages': pages,
        'size': os.path.getsize(p),
        'is_scanned': is_scanned,
        'has_text_layer': not is_scanned
    })

# Output summary
print("=== A. ARCHITECTURE ===")
print(json.dumps(report['architecture'], indent=2))

print("\n=== B. DEFECTS AUDIT RESULTS ===")
print("D1 (Misalignment):", d1_samples)
print(f"D2 (Treasure Island placeholder): Found placeholder={d2_has_placeholder}, total stevenson items={d2_count}")
print(f"D3 (Hardcoded stats in JS): corpus.js={d3_corpus_hardcoded}, collocations.js={d3_colloc_hardcoded}")
print(f"D5 (Quality defects): repeated tokens={len(repeated_tokens)}, bitter enemies={bitter_enemies}")
print(f"D6 (Demo records in corpus): {len(demo_records)}")
print("D11 (Apostrophe counts in corpus):", apostrophes_corpus)
print("D11 (Apostrophe counts in collocations):", apostrophes_colloc)

print("\n=== D. BOOKS INVENTORY ===")
for b in books_inv:
    print(f"* {b['name']}: Exists={b['exists']}, Pages={b.get('pages', 0)}, Scanned={b.get('is_scanned', 'N/A')}")

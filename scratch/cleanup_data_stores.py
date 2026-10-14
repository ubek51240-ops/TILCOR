import json
import sqlite3
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = 'data'

print("=== 1. CLEANING FULL_CORPUS.JSON & CORPUS.DB ===")
with open(os.path.join(DATA_DIR, 'full_corpus.json'), 'r', encoding='utf-8') as f:
    corpus = json.load(f)

cleaned_corpus = []
active_corpus_count = 0
archived_stevenson_count = 0

for item in corpus:
    c = dict(item)
    book = c.get('book', '').lower()
    
    # Remove score and moslik
    c.pop('score', None)
    c.pop('moslik', None)
    c.pop('alignmentScore', None)
    
    if book == 'stevenson':
        c['status'] = 'removed_by_researcher'
        c['excluded'] = True
        c['bookTitle'] = "R. L. Stevenson: «Treasure Island»"
        c['author'] = "Robert Louis Stevenson"
        c['translator'] = "Sharif Rizo"
        c['license'] = "Tadqiqotchi tomonidan chiqarilgan (arxovlangan)"
        archived_stevenson_count += 1
    elif book == 'cholpon':
        c['status'] = 'active'
        c['excluded'] = False
        c['bookTitle'] = "Abdulhamid Cho‘lpon: «Kecha va kunduz»"
        c['author'] = "Abdulhamid Cho‘lpon"
        c['translator'] = "Christopher Fort"
        c['pubYear'] = "UZ: 2000 / EN: 2019"
        c['publisher'] = "UZ: «Sharq» NMK / EN: Academic Studies Press"
        c['license'] = "Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha."
        c['direction'] = "UZ → EN"
        active_corpus_count += 1
    elif book == 'hemingway':
        c['status'] = 'active'
        c['excluded'] = False
        c['bookTitle'] = "Ernest Hemingway: «Chol va dengiz»"
        c['author'] = "Ernest Hemingway"
        c['translator'] = "Ibrohim G‘ofurov"
        c['pubYear'] = "EN: 1952 / UZ: 1986"
        c['publisher'] = "EN: Charles Scribner's Sons / UZ: «Yosh gvardiya»"
        c['license'] = "Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha."
        c['direction'] = "EN → UZ"
        active_corpus_count += 1
    else:
        c['status'] = 'archived'
        c['excluded'] = True
    
    cleaned_corpus.append(c)

with open(os.path.join(DATA_DIR, 'full_corpus.json'), 'w', encoding='utf-8') as f:
    json.dump(cleaned_corpus, f, ensure_ascii=False, indent=2)

print(f"full_corpus.json updated: Total={len(cleaned_corpus)}, Active={active_corpus_count}, Archived Stevenson={archived_stevenson_count}")

# Update SQLite corpus.db
db_path = os.path.join(DATA_DIR, 'corpus.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if status column exists in corpus table
    cur.execute("PRAGMA table_info(corpus)")
    cols = [col[1] for col in cur.fetchall()]
    if 'status' not in cols:
        cur.execute("ALTER TABLE corpus ADD COLUMN status TEXT")
    if 'license' not in cols:
        cur.execute("ALTER TABLE corpus ADD COLUMN license TEXT")
    if 'author' not in cols:
        cur.execute("ALTER TABLE corpus ADD COLUMN author TEXT")
    if 'translator' not in cols:
        cur.execute("ALTER TABLE corpus ADD COLUMN translator TEXT")
    
    for c in cleaned_corpus:
        cur.execute("""
            UPDATE corpus 
            SET status=?, license=?, author=?, translator=?
            WHERE id=?
        """, (c['status'], c['license'], c['author'], c['translator'], c['id']))
    
    conn.commit()
    conn.close()
    print("corpus.db updated successfully.")


print("\n=== 2. CLEANING COLLOCATIONS_FULL.JSON & JS ===")
with open(os.path.join(DATA_DIR, 'collocations_full.json'), 'r', encoding='utf-8') as f:
    collocs = json.load(f)

cleaned_collocs = []
rejected_collocs = 0
ai_collocs = 0

SOURCE_MAP = {
    'IELTS Academic Collocations List': 'Academic Collocation List (K. Ackermann & Y.-H. Chen, Pearson, 2013)',
    'Cambridge Collocations (Intermediate)': 'English Collocations in Use (Intermediate; M. McCarthy & F. O’Dell, Cambridge University Press)',
    'Cambridge Collocations (Advanced)': 'English Collocations in Use (Advanced; M. McCarthy & F. O’Dell, Cambridge University Press)',
    '1000 English Collocations Ebook': '1000 English Collocations (Espresso English)',
    'Choʻlpon: «Kecha va kunduz»': 'Abdulhamid Cho‘lpon: «Kecha va kunduz»',
    'E. Xeminguey: «Chol va dengiz»': 'Ernest Hemingway: «Chol va dengiz»',
    'R. L. Stivenson: «Xazinalar oroli»': 'removed_by_researcher'
}

for item in collocs:
    c = dict(item)
    en = c.get('english', '').strip()
    uz = c.get('uzbek', '').strip()
    en_lower = en.lower()
    uz_lower = uz.lower()
    
    words = en_lower.split()
    
    # Check for rejection:
    # 1. Repeated tokens e.g. "nice nice nice", "good good good"
    is_repeated = len(words) >= 2 and len(set(words)) == 1
    # 2. Nonsense / non-uzbek / MT garbage
    has_garbage = any(g in uz_lower for g in ['güveç', 'ostiga keling yurak bor', 'oling yaxshi go‘zal go‘zal'])
    # 3. Wrong patterns like "adhere economy" tagged Adj+Noun
    is_wrong_pattern = (en_lower == 'adhere economy')
    # 4. Stevenson origin
    is_stevenson = any('stivenson' in str(s).lower() or 'stevenson' in str(s).lower() for s in c.get('sources', [])) or ('stevenson' in str(c.get('sourceBook', '')).lower())

    if is_repeated or has_garbage or is_wrong_pattern:
        c['status'] = 'rejected'
        c['class'] = 'TO‘QIMA'
        c['public_visible'] = False
        rejected_collocs += 1
    elif is_stevenson:
        c['status'] = 'removed_by_researcher'
        c['class'] = 'TO‘QIMA'
        c['public_visible'] = False
        rejected_collocs += 1
    else:
        c['status'] = 'active'
        c['class'] = 'AI-TAKLIF'
        c['review_status'] = 'AI-taklif (tekshirilmagan)'
        c['public_visible'] = True
        ai_collocs += 1

    # Map sources
    raw_sources = c.get('sources', [])
    new_sources = []
    for s in raw_sources:
        if s in SOURCE_MAP:
            mapped = SOURCE_MAP[s]
            if mapped != 'removed_by_researcher':
                new_sources.append(mapped)
        elif 'Pearson' in s or 'IELTS' in s:
            new_sources.append('Academic Collocation List (K. Ackermann & Y.-H. Chen, Pearson, 2013)')
        elif 'Cambridge' in s:
            new_sources.append('English Collocations in Use (M. McCarthy & F. O’Dell, Cambridge University Press)')
        else:
            new_sources.append('manba aniqlanmagan')
    
    if not new_sources:
        new_sources = ['manba aniqlanmagan']
        if c['status'] == 'active':
            c['public_visible'] = False
            
    c['sources'] = new_sources
    c['sourceMeta'] = ', '.join(new_sources)

    # Clean template examples
    ex = c.get('example', {})
    if isinstance(ex, dict):
        ex_en = ex.get('en', '')
        if 'plays a vital semantic role' in ex_en or 'high collocational strength' in ex_en:
            c['example'] = None
    elif isinstance(ex, str):
        if 'plays a vital semantic role' in ex or 'high collocational strength' in ex:
            c['example'] = None

    # Hide raw statistics until step 10
    c['miScore_display'] = None
    c['tScore_display'] = None
    c['freq_display'] = None
    c['logLikelihood_display'] = None

    cleaned_collocs.append(c)

with open(os.path.join(DATA_DIR, 'collocations_full.json'), 'w', encoding='utf-8') as f:
    json.dump(cleaned_collocs, f, ensure_ascii=False, indent=2)

print(f"collocations_full.json updated: Total={len(cleaned_collocs)}, Active={ai_collocs}, Rejected/Removed={rejected_collocs}")

# Write sanitized bundle to js/collocations_list.js
public_collocs = [c for c in cleaned_collocs if c.get('public_visible') and c.get('status') == 'active']
with open('js/collocations_list.js', 'w', encoding='utf-8') as f:
    f.write("// TILCOR Sanitized Collocations Database (Active Verified Entries)\n")
    f.write("const collocationsDatabase = ")
    json.dump(public_collocs, f, ensure_ascii=False)
    f.write(";\n")
print(f"js/collocations_list.js written with {len(public_collocs)} active entries.")


print("\n=== 3. CLEANING DICTIONARY.JSON ===")
with open(os.path.join(DATA_DIR, 'dictionary.json'), 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

cleaned_dict = []
clean_count = 0
damaged_count = 0

for item in dictionary:
    d = dict(item)
    w = d.get('word', '').strip()
    tr = d.get('translation', '').strip()
    
    # Damage detection heuristics
    is_damaged = False
    if w in ['rim', 'tomir', 'va yuzdan yurakka']:
        is_damaged = True
    elif re.search(r'\b(adj\.|n\.|v\.|adv\.|prep\.)', w):
        is_damaged = True
    elif tr.startswith('gan-') or 'qo‘rqoq, yurak-' in tr or tr.endswith('-') and len(tr) < 8:
        is_damaged = True
    elif len(w) <= 1 or len(tr) <= 1 or not re.match(r'^[a-zA-Z\s\-\']+$', w):
        is_damaged = True
    elif '\ufffd' in w or '\ufffd' in tr:
        is_damaged = True
        
    if is_damaged:
        d['status'] = 'needs_repair'
        d['public_visible'] = False
        damaged_count += 1
    else:
        d['status'] = 'active'
        d['public_visible'] = True
        clean_count += 1
        
    d['source'] = "80,000 so‘zli Katta Lug‘at (881 bet) & 816 betlik Lug‘at (BuxDU)"
    # Remove any attached templated example
    d.pop('example', None)
    
    cleaned_dict.append(d)

with open(os.path.join(DATA_DIR, 'dictionary.json'), 'w', encoding='utf-8') as f:
    json.dump(cleaned_dict, f, ensure_ascii=False, indent=2)

print(f"dictionary.json updated: Total={len(cleaned_dict)}, Active clean={clean_count}, needs_repair={damaged_count}")

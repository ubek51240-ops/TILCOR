import os
import sys
import re
import sqlite3
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'C:\Users\user\Desktop\tarjimon'
db_path = os.path.join(base_dir, 'data', 'phd_corpus.db')

uz_pdf_path = r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf'
en_pdf_path = r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf'

def parse_uz_page_lines(raw_text):
    lines = [l.strip() for l in raw_text.splitlines()]
    printed_page = None
    body_lines = []
    flags = []
    
    for idx, l in enumerate(lines):
        if not l:
            continue
        # Check Ziyouz header
        if 'ziyouz.com' in l or 'Abdulhamid Cho‘lpon' in l or 'Kecha va kunduz (roman)' in l:
            flags.append('HEADER_STRIPPED')
            continue
        # Check page number line
        if re.match(r'^\d+$', l):
            num = int(l)
            if num < 500: # sanity check
                printed_page = num
                flags.append('PAGE_NUM_CAPTURED')
                continue
        body_lines.append(l)
        
    full_text = ' '.join(body_lines)
    # Join line-wrap hyphens: e.g. "boshlan- gich" -> "boshlang'ich", but leave "dala-tuz"
    hyphen_fixed = re.sub(r'(\b[a-zA-Z\u0400-\u04FF\u02BB\u02BC\']+)-\s+([a-zA-Z\u0400-\u04FF\u02BB\u02BC\']+)', r'\1\2', full_text)
    if hyphen_fixed != full_text:
        flags.append('HYPHEN_JOINED')
        
    clean_text = re.sub(r'\s+', ' ', hyphen_fixed).strip()
    return printed_page, clean_text, ','.join(sorted(list(set(flags)))) if flags else 'OK'

def parse_en_page_lines(raw_text):
    lines = [l.strip() for l in raw_text.splitlines()]
    printed_page = None
    body_lines = []
    flags = []
    
    # In English, top 1-2 lines often have 'Night and Day', 'Night', and page number '46', '47'
    for idx, l in enumerate(lines):
        if not l:
            continue
        if idx < 3:
            if re.match(r'^(?:Night\s+and\s+Day|Night)$', l, re.I):
                flags.append('HEADER_STRIPPED')
                continue
            if re.match(r'^\d+$', l):
                printed_page = int(l)
                flags.append('PAGE_NUM_CAPTURED')
                continue
        # Section separator dots
        if re.match(r'^\.{5,}$', l):
            body_lines.append('—') # section break marker
            continue
        body_lines.append(l)
        
    full_text = ' '.join(body_lines)
    # Fix broken English hyphens: e.g. "flow- er" -> "flower", "revela- tion" -> "revelation"
    hyphen_fixed = re.sub(r'(\b[a-zA-Z]+)-\s+([a-zA-Z]+)', r'\1\2', full_text)
    if hyphen_fixed != full_text:
        flags.append('HYPHEN_JOINED')
        
    clean_text = re.sub(r'\s+', ' ', hyphen_fixed).strip()
    return printed_page, clean_text, ','.join(sorted(list(set(flags)))) if flags else 'OK'

def split_sentences_strict(text):
    abbrs = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'vs.', 'No.', 'Vol.', 'p.', 'pp.', 'sh.k.', 'v.b.', 'va h.k.', 'mas.', 'b.n.']
    temp = text
    for i, a in enumerate(abbrs):
        temp = temp.replace(a, f'__ABBR_{i}__')
        
    # Split on terminal punctuation followed by space and Capital / Quote / Dash
    raw_sents = re.split(r'(?<=[.!?…])\s+(?=[A-Z\u0410-\u042F«"“\'—])', temp)
    
    clean_sents = []
    for s in raw_sents:
        for i, a in enumerate(abbrs):
            s = s.replace(f'__ABBR_{i}__', a)
        s = s.strip()
        if len(s) > 2 and s != '—':
            clean_sents.append(s)
            
    return clean_sents

def run_extraction_prototype():
    doc_uz = pymupdf.open(uz_pdf_path)
    doc_en = pymupdf.open(en_pdf_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Extracting pages 3 to 15 (including Chapter 1 start)...")
    uz_pages = []
    en_pages = []
    
    for p in range(3, 16):
        # UZ
        uz_raw = doc_uz[p-1].get_text()
        uz_p_num, uz_clean, uz_flags = parse_uz_page_lines(uz_raw)
        uz_page_id = f"page-book-cholpon-uz-p{p:03d}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO pages (
                id, book_id, pdf_page_num, printed_page_num, raw_text, clean_text,
                char_count, token_count, has_text_layer, extraction_method, quality_flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            uz_page_id, 'book-cholpon-uz', p, uz_p_num, uz_raw, uz_clean,
            len(uz_clean), len(uz_clean.split()), 1, 'pymupdf_v1.24_gate2', uz_flags
        ))
        
        uz_sents = split_sentences_strict(uz_clean)
        for s_idx, s in enumerate(uz_sents):
            seg_id = f"seg-cholpon-uz-p{p:03d}-s{s_idx+1:03d}"
            cursor.execute('''
                INSERT OR REPLACE INTO segments (
                    id, book_id, page_id, pdf_page_num, segment_order, raw_text, clean_text, token_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (seg_id, 'book-cholpon-uz', uz_page_id, p, s_idx+1, s, s, len(s.split())))
            
        uz_pages.append({'pdf': p, 'printed': uz_p_num, 'clean': uz_clean, 'sents': len(uz_sents), 'flags': uz_flags, 'first': uz_sents[0] if uz_sents else ''})
        
        # EN
        en_raw = doc_en[p-1].get_text()
        en_p_num, en_clean, en_flags = parse_en_page_lines(en_raw)
        en_page_id = f"page-book-cholpon-en-p{p:03d}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO pages (
                id, book_id, pdf_page_num, printed_page_num, raw_text, clean_text,
                char_count, token_count, has_text_layer, extraction_method, quality_flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            en_page_id, 'book-cholpon-en', p, en_p_num, en_raw, en_clean,
            len(en_clean), len(en_clean.split()), 1, 'pymupdf_v1.24_gate2', en_flags
        ))
        
        en_sents = split_sentences_strict(en_clean)
        for s_idx, s in enumerate(en_sents):
            seg_id = f"seg-cholpon-en-p{p:03d}-s{s_idx+1:03d}"
            cursor.execute('''
                INSERT OR REPLACE INTO segments (
                    id, book_id, page_id, pdf_page_num, segment_order, raw_text, clean_text, token_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (seg_id, 'book-cholpon-en', en_page_id, p, s_idx+1, s, s, len(s.split())))
            
        en_pages.append({'pdf': p, 'printed': en_p_num, 'clean': en_clean, 'sents': len(en_sents), 'flags': en_flags, 'first': en_sents[0] if en_sents else ''})
        
    conn.commit()
    conn.close()
    
    return uz_pages, en_pages

uz_pages, en_pages = run_extraction_prototype()

print("\n=== GATE 2 EXTRACTION VERIFICATION RESULTS ===")
for i in range(len(uz_pages)):
    uz = uz_pages[i]
    en = en_pages[i]
    print(f"\n--- [PAGE COMPARISON: PDF Page {uz['pdf']}] ---")
    print(f"UZ (Kitob beti: {uz['printed']}): {uz['sents']} jumlalar, Flags: [{uz['flags']}]")
    print(f"   Matn boshlanishi: {uz['first'][:120]}...")
    print(f"EN (Book page: {en['printed']}): {en['sents']} sentences, Flags: [{en['flags']}]")
    print(f"   Text beginning:  {en['first'][:120]}...")

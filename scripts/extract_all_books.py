import os
import sys
import re
import sqlite3
import pymupdf
import time

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'C:\Users\user\Desktop\tarjimon'
db_path = os.path.join(base_dir, 'data', 'phd_corpus.db')

book_configs = [
    {
        'id': 'book-cholpon-uz',
        'path': r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf',
        'lang': 'uz',
        'start_page': 3, # pages 1-2 are title/cover
        'end_page': 272,
        'title': "Cho'lpon: «Kecha va kunduz» (UZ)"
    },
    {
        'id': 'book-cholpon-en',
        'path': r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf',
        'lang': 'en',
        'start_page': 3, # novel starts on page 3
        'end_page': 235,
        'title': "Cho'lpon: «Night and Day» (EN, Ch. Fort)"
    },
    {
        'id': 'book-hemingway-en',
        'path': r'C:\Users\user\Downloads\Telegram Desktop\oldmansea.pdf',
        'lang': 'en',
        'start_page': 2, # page 1 is title cover
        'end_page': 52,
        'title': "Hemingway: «The Old Man and the Sea» (EN)"
    },
    {
        'id': 'book-hemingway-uz',
        'path': r'C:\Users\user\Downloads\Telegram Desktop\Chol va dengiz ( Ernst).pdf',
        'lang': 'uz',
        'start_page': 1, # body text starts immediately on page 1 below title
        'end_page': 46,
        'title': "Hemingway: «Chol va dengiz» (UZ, I. G'afurov)"
    }
]

def clean_page(raw_text, book_id):
    lines = [l.strip() for l in raw_text.splitlines()]
    printed_page = None
    body_lines = []
    flags = []

    if not lines or len(raw_text.strip()) < 10:
        return None, "", "EMPTY"

    for idx, l in enumerate(lines):
        if not l:
            continue

        # Header filters by book
        if book_id == 'book-cholpon-uz':
            if 'ziyouz.com' in l or 'Abdulhamid Cho‘lpon' in l or 'Kecha va kunduz (roman)' in l:
                flags.append('HEADER_STRIPPED')
                continue
            if re.match(r'^\d+$', l):
                num = int(l)
                if num < 500:
                    printed_page = num
                    flags.append('PAGE_NUM_CAPTURED')
                    continue

        elif book_id == 'book-cholpon-en':
            if idx < 3:
                if re.match(r'^(?:Night\s+and\s+Day|Night)$', l, re.I):
                    flags.append('HEADER_STRIPPED')
                    continue
                if re.match(r'^\d+$', l):
                    printed_page = int(l)
                    flags.append('PAGE_NUM_CAPTURED')
                    continue
            if re.match(r'^\.{5,}$', l):
                body_lines.append('—')
                continue

        elif book_id == 'book-hemingway-en':
            # e.g. "The Old Man and the Sea Asiaing.com - 3 -"
            if 'Asiaing.com' in l or 'The Old Man and the Sea' in l:
                flags.append('HEADER_STRIPPED')
                m_p = re.search(r'-\s*(\d+)\s*-', l)
                if m_p:
                    printed_page = int(m_p.group(1))
                    flags.append('PAGE_NUM_CAPTURED')
                continue

        elif book_id == 'book-hemingway-uz':
            # e.g. "Ernest Xeminguey. Chol va dengiz (qissa) kutubxonachi.uz ... 4"
            if 'kutubxonachi.uz' in l or 'Ernest Xeminguey' in l or 'Chol va dengiz (qissa)' in l:
                flags.append('HEADER_STRIPPED')
                m_p = re.search(r'\b(\d+)\s*$', l)
                if m_p:
                    printed_page = int(m_p.group(1))
                    flags.append('PAGE_NUM_CAPTURED')
                continue
            if re.match(r'^\d+$', l):
                printed_page = int(l)
                flags.append('PAGE_NUM_CAPTURED')
                continue

        body_lines.append(l)

    full_text = ' '.join(body_lines)
    # Join broken line-end hyphens
    hyphen_fixed = re.sub(r'(\b[a-zA-Z\u0400-\u04FF\u02BB\u02BC\']+)-\s+([a-zA-Z\u0400-\u04FF\u02BB\u02BC\']+)', r'\1\2', full_text)
    if hyphen_fixed != full_text:
        flags.append('HYPHEN_JOINED')

    clean_text = re.sub(r'\s+', ' ', hyphen_fixed).strip()
    flag_str = ','.join(sorted(list(set(flags)))) if flags else 'OK'
    return printed_page, clean_text, flag_str

def split_sentences(text):
    if not text:
        return []
    abbrs = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'vs.', 'No.', 'Vol.', 'p.', 'pp.', 'sh.k.', 'v.b.', 'va h.k.', 'mas.', 'b.n.', 'Q.', 'St.']
    temp = text
    for i, a in enumerate(abbrs):
        temp = temp.replace(a, f'__ABBR_{i}__')

    raw_sents = re.split(r'(?<=[.!?…])\s+(?=[A-Z\u0410-\u042F«"“\'—])', temp)

    clean_sents = []
    for s in raw_sents:
        for i, a in enumerate(abbrs):
            s = s.replace(f'__ABBR_{i}__', a)
        s = s.strip()
        if len(s) > 2 and s != '—':
            clean_sents.append(s)

    return clean_sents

def run_full_extraction():
    start_time = time.time()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    overall_stats = []

    for cfg in book_configs:
        b_id = cfg['id']
        b_path = cfg['path']
        b_title = cfg['title']
        start_p = cfg['start_page']
        end_p = cfg['end_page']

        print(f"\nProcessing: {b_title}...")
        doc = pymupdf.open(b_path)
        actual_total = len(doc)
        end_p = min(end_p, actual_total)

        b_pages = 0
        b_tokens = 0
        b_chars = 0
        b_segments = 0
        flag_counts = {}

        for p in range(1, actual_total + 1):
            page_obj = doc[p - 1]
            raw_text = page_obj.get_text()
            has_text = 1 if len(raw_text.strip()) > 30 else 0

            # If before body text (covers/TOC), mark as FRONT_MATTER
            if p < start_p:
                clean_t = re.sub(r'\s+', ' ', raw_text).strip()
                p_flag = 'FRONT_MATTER'
                p_num = None
            else:
                p_num, clean_t, p_flag = clean_page(raw_text, b_id)

            flag_counts[p_flag] = flag_counts.get(p_flag, 0) + 1

            page_id = f"page-{b_id}-p{p:03d}"
            char_cnt = len(clean_t)
            tok_cnt = len(clean_t.split())

            b_pages += 1
            b_chars += char_cnt
            b_tokens += tok_cnt

            cursor.execute('''
                INSERT OR REPLACE INTO pages (
                    id, book_id, pdf_page_num, printed_page_num, raw_text, clean_text,
                    char_count, token_count, has_text_layer, extraction_method, quality_flag
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                page_id, b_id, p, p_num, raw_text, clean_t,
                char_cnt, tok_cnt, has_text, 'pymupdf_v1.24_gate3', p_flag
            ))

            # Segment sentences (only for main text)
            if p >= start_p and clean_t:
                sents = split_sentences(clean_t)
                for s_idx, s in enumerate(sents):
                    seg_id = f"seg-{b_id}-p{p:03d}-s{s_idx+1:03d}"
                    cursor.execute('''
                        INSERT OR REPLACE INTO segments (
                            id, book_id, page_id, pdf_page_num, segment_order, raw_text, clean_text, token_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (seg_id, b_id, page_id, p, s_idx + 1, s, s, len(s.split())))
                b_segments += len(sents)

        conn.commit()

        # Update total pages in books table
        cursor.execute("UPDATE books SET total_pages = ? WHERE id = ?", (actual_total, b_id))

        stat_record = {
            'id': b_id,
            'title': b_title,
            'total_pages': actual_total,
            'processed_pages': b_pages,
            'tokens': b_tokens,
            'characters': b_chars,
            'segments': b_segments,
            'flags': flag_counts
        }
        overall_stats.append(stat_record)
        print(f"  -> Done: {b_pages} pages, {b_tokens:,} tokens, {b_segments:,} segments.")

    # Record provenance
    cursor.execute('''
        INSERT INTO provenance_log (action_type, entity_name, entity_id, details)
        VALUES ('FULL_EXTRACTION', 'books', 'ALL_4_BOOKS', 'Full extraction completed across all 4 core books (Cho''lpon UZ/EN, Hemingway UZ/EN).')
    ''')
    conn.commit()
    conn.close()

    elapsed = time.time() - start_time
    print(f"\nExtraction completed in {elapsed:.2f} seconds.")
    return overall_stats

if __name__ == '__main__':
    stats = run_full_extraction()
    print("\n================ FULL EXTRACTION STATS ================")
    total_tokens = sum(s['tokens'] for s in stats)
    total_segments = sum(s['segments'] for s in stats)
    total_pages = sum(s['total_pages'] for s in stats)
    print(f"Total Books: {len(stats)}")
    print(f"Total Pages Processed: {total_pages:,}")
    print(f"Total Words (Tokens): {total_tokens:,}")
    print(f"Total Sentence Segments: {total_segments:,}")
    for s in stats:
        print(f"\n* {s['title']}:")
        print(f"  Pages: {s['total_pages']} | Words: {s['tokens']:,} | Segments: {s['segments']:,}")
        print(f"  Quality Flags: {s['flags']}")

#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 4 FULL TEXT EXTRACTION & QUALITY CONTROL PIPELINE
Dissertation: "TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA O‘ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO‘ZLAR TADQIQI"
Rebuilds all 6 texts from original pristine PDF sources.
Follows all PhD rigor rules (R1-R10, Prompt 4):
- Header/footer/page number separation into dedicated columns
- Dehyphenation across line breaks
- Dialogue dash and quote preservation
- Footnotes extracted and flagged as segment_type='footnote'
- Robust sentence segmentation per language with abbreviation & initial protection
- Documented quality flags
- Stevenson UZ strictly recorded as missing text layer (0 hallucination)
- Idempotent execution
"""

import os
import sys
import re
import sqlite3
import pymupdf
import time
import hashlib

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r'C:\Users\user\Desktop\tarjimon'
PDF_DIR = r'C:\Users\user\Downloads\Telegram Desktop'

CANONICAL_OG = '\u02bb'     # ʻ (U+02BB)
CANONICAL_TUTUQ = '\u02bc'  # ʼ (U+02BC)
APOSTROPHE_VARIANTS = r"[`'‘’ʻ´\u02bb\u02bc\u2018\u2019]"

UZ_ABBREVIATIONS = {
    'h.k.', 'sh.k.', 'q.', 'b.', 'prof.', 'dots.', 'akadem.', 'filol.', 'fan.',
    'v.b.', 'mas.', 'e.g.', 'i.e.', 'v.h.', 'b.n.', 'j.', 'san.', 'mil.'
}
EN_ABBREVIATIONS = {
    'mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'st.', 'vs.', 'etc.', 'i.e.', 'e.g.',
    'no.', 'vol.', 'p.', 'pp.', 'jr.', 'sr.', 'co.', 'ltd.', 'inc.', 'capt.', 'gen.'
}

def normalize_uzbek_text(raw_text):
    if not raw_text:
        return ''
    text = raw_text
    # 1. Map o‘ / g‘ variants to U+02BB
    text = re.sub(r'([oOgG])' + APOSTROPHE_VARIANTS, r'\g<1>' + CANONICAL_OG, text)
    # 2. Map tutuq belgisi inside words to U+02BC
    text = re.sub(r'(?<![oOgG\u02bb])' + r"[`'‘’´\u02bc\u2018\u2019]" + r'(?=\w)', CANONICAL_TUTUQ, text)
    return text.lower()

def count_tokens(text):
    if not text:
        return 0
    # Standard word tokenizer matching word characters and internal apostrophes/hyphens
    tokens = re.findall(r"\b[\w\u02bb\u02bc'-]+\b", text)
    return len(tokens)

def is_initial(word):
    """Checks if a word is a single-letter initial like 'A.', 'N.', 'I.'"""
    return bool(re.match(r'^[A-ZА-ЯЎҚҒҲ]\.$', word))

def segment_sentences(text, lang='uz'):
    """
    Sentence segmentation preserving dialogue, abbreviations, and initials.
    """
    if not text or not text.strip():
        return []

    # Normalize paragraph splits
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    abbr_set = UZ_ABBREVIATIONS if lang == 'uz' else EN_ABBREVIATIONS
    result_segments = []

    for para in paragraphs:
        # Check if entire paragraph is a footnote or dialogue
        p_clean = re.sub(r'[ \t]+', ' ', para).strip()
        if not p_clean:
            continue

        # Split on sentence terminals followed by space and uppercase letter / quote / dash
        pattern = r'(?<=[.!?…])\s+(?=[A-ZА-ЯЎҚҒҲ“"«—–])'
        raw_parts = re.split(pattern, p_clean)

        merged_parts = []
        for part in raw_parts:
            part = part.strip()
            if not part:
                continue
            if merged_parts:
                last_part = merged_parts[-1].strip()
                last_word = last_part.split()[-1].lower() if last_part.split() else ''
                # If last word was an abbreviation or single letter initial or footnote marker or next part starts with parenthesis/lowercase
                if (last_word in abbr_set or
                    is_initial(last_part.split()[-1]) or
                    (len(last_word) == 2 and last_word.endswith('.')) or
                    re.search(r'\.\d+$', last_part) or
                    part.startswith(('(', '[', '{')) or
                    re.match(r'^[a-zа-яўқғҳ]', part)):
                    merged_parts[-1] += ' ' + part
                    continue
            merged_parts.append(part)

        for s in merged_parts:
            s_clean = s.strip()
            if s_clean and len(s_clean) > 1:
                # Classify segment type
                seg_type = 'body'
                if re.match(r'^[—–-]\s+', s_clean) or s_clean.startswith(('“', '"', '«')):
                    seg_type = 'dialogue'
                elif len(s_clean) < 60 and not s_clean.endswith(('.', '!', '?', '…', '"', '”', '»')):
                    seg_type = 'heading'
                result_segments.append((s_clean, seg_type))

    return result_segments

def dehyphenate_lines(lines):
    """
    Joins line breaks with hyphenation detection.
    """
    joined_text = ""
    had_hyphen = False
    for l in lines:
        l_str = l.strip()
        if not l_str:
            continue
        if joined_text.endswith('-'):
            # Dehyphenate across line
            joined_text = joined_text[:-1] + l_str
            had_hyphen = True
        elif re.search(r'-\s*$', joined_text):
            joined_text = re.sub(r'-\s*$', '', joined_text) + l_str
            had_hyphen = True
        elif re.match(r'^[—–-]\s+', l_str):
            # Standalone dialogue turn
            joined_text += "\n\n" + l_str
        elif joined_text.endswith(('.', '!', '?', '…', ':')):
            joined_text += "\n\n" + l_str
        else:
            joined_text += " " + l_str

    # Post-process unjoined mid-word hyphen-space artifacts like "tree- tops" -> "tree-tops"
    sub_text = re.sub(r'(\b\w+)-\s+(\w+\b)', r'\1-\2', joined_text)
    if sub_text != joined_text:
        had_hyphen = True
        joined_text = sub_text

    return joined_text.strip(), had_hyphen

# Book configurations
BOOK_CONFIGS = [
    {
        'book_id': 'book-cholpon-uz',
        'text_id': 'txt-cholpon-uz',
        'pdf_filename': 'cholpon-kecha-va-kunduz.pdf',
        'lang': 'uz',
        'title': "Cho'lpon: «Kecha va kunduz» (UZ)",
        'has_layer': True,
        'start_page': 3,
        'end_body_page': 265,
        'total_pages': 272
    },
    {
        'book_id': 'book-cholpon-en',
        'text_id': 'txt-cholpon-en',
        'pdf_filename': 'night-and-day-a-novel-9781644690482_compress-pages.pdf',
        'lang': 'en',
        'title': "Cho'lpon: «Night and Day» (EN, Ch. Fort)",
        'has_layer': True,
        'start_page': 3,
        'end_body_page': 229,
        'total_pages': 235
    },
    {
        'book_id': 'book-hemingway-en',
        'text_id': 'txt-hemingway-en',
        'pdf_filename': 'oldmansea.pdf',
        'lang': 'en',
        'title': "Hemingway: «The Old Man and the Sea» (EN)",
        'has_layer': True,
        'start_page': 2,
        'end_body_page': 50,
        'total_pages': 52
    },
    {
        'book_id': 'book-hemingway-uz',
        'text_id': 'txt-hemingway-uz',
        'pdf_filename': 'Chol va dengiz ( Ernst).pdf',
        'lang': 'uz',
        'title': "Hemingway: «Chol va dengiz» (UZ, I. G'afurov)",
        'has_layer': True,
        'start_page': 1,
        'end_body_page': 46,
        'total_pages': 46
    },
    {
        'book_id': 'book-stevenson-en',
        'text_id': 'txt-stevenson-en',
        'pdf_filename': 'treasure island.pdf',
        'lang': 'en',
        'title': "Stevenson: «Treasure Island» (EN)",
        'has_layer': True,
        'start_page': 3,
        'end_body_page': 142,
        'total_pages': 142
    },
    {
        'book_id': 'book-stevenson-uz',
        'text_id': 'txt-stevenson-uz',
        'pdf_filename': 'Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf',
        'lang': 'uz',
        'title': "Stevenson: «Xazinalar oroli» (UZ, Sh. Rizo) [SCANNED/MISSING]",
        'has_layer': False,
        'start_page': 1,
        'end_body_page': 216,
        'total_pages': 216
    }
]

def extract_page_content(cfg, pno, raw_text):
    """
    Extracts headers, footers, printed page numbers, body text, and footnotes for a given page.
    """
    b_id = cfg['book_id']
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    flags = []
    headers = []
    footers = []
    footnotes = []
    body_lines = []
    printed_page = None

    if not lines or len(raw_text.strip()) < 10:
        return {
            'header': '',
            'footer': '',
            'printed_page': None,
            'clean_text': '',
            'flags': ['EMPTY_PAGE'],
            'footnotes': [],
            'body_lines': []
        }

    # Section tag checks
    if pno < cfg['start_page']:
        flags.append('FRONT_MATTER')
    elif pno > cfg['end_body_page']:
        if b_id == 'book-cholpon-uz':
            flags.append('AFTERWORD')
        elif b_id == 'book-cholpon-en':
            flags.append('GLOSSARY')
        elif b_id == 'book-hemingway-en':
            flags.append('BIBLIOGRAPHY')

    # Specific parsing per book
    if b_id == 'book-cholpon-uz':
        idx = 0
        while idx < min(4, len(lines)):
            l = lines[idx]
            if 'Abdulhamid Cho‘lpon' in l or 'Kecha va kunduz' in l or 'ziyouz.com' in l:
                headers.append(l)
                idx += 1
            elif re.match(r'^\d+$', l):
                printed_page = int(l)
                idx += 1
            else:
                break
        cand_body = lines[idx:]
        # Check bottom lines for potential footnote
        b_idx = len(cand_body) - 1
        while b_idx >= max(0, len(cand_body) - 3):
            l = cand_body[b_idx]
            if re.match(r'^\d+\s+[A-ZА-ЯЎҚҒҲa-zа-яўқғҳ]', l):
                footnotes.insert(0, l)
                cand_body = cand_body[:b_idx]
                flags.append('FOOTNOTE_DETECTED')
                break
            b_idx -= 1
        body_lines = cand_body

    elif b_id == 'book-cholpon-en':
        idx = 0
        while idx < min(4, len(lines)):
            l = lines[idx]
            if re.match(r'^\d+$', l):
                printed_page = int(l)
                idx += 1
            elif l in ['Night and Day', 'Night and Day: Night', 'Night', 'First Book', 'Second Book', 'Glossary'] or re.match(r'^(?:Night and Day|Night|Glossary).*$', l):
                headers.append(l)
                idx += 1
            else:
                break
        cand_body = lines[idx:]
        # Check bottom for footnotes (lines starting with footnote numbers like 3\t, 4\t, 6\t)
        b_idx = len(cand_body) - 1
        found_fn_start = -1
        while b_idx >= max(0, len(cand_body) - 8):
            l = cand_body[b_idx]
            if re.match(r'^\d+[\t\s]+', l):
                found_fn_start = b_idx
                # keep going back in case multiple footnotes
            elif found_fn_start != -1 and not re.match(r'^[A-Z]', l):
                # Continuation line of previous footnote
                pass
            b_idx -= 1

        if found_fn_start != -1:
            fn_lines = cand_body[found_fn_start:]
            cand_body = cand_body[:found_fn_start]
            footnotes = fn_lines
            flags.append('FOOTNOTE_DETECTED')
        body_lines = cand_body

    elif b_id == 'book-hemingway-en':
        idx = 0
        while idx < min(6, len(lines)):
            l = lines[idx]
            l_low = l.lower()
            if any(term in l_low for term in ['asiaing.com', 'the old man and the sea', 'ernest hemingway', 'works novels/novellas']):
                headers.append(l)
                m_p = re.search(r'-\s*(\d+)\s*-', l)
                if m_p:
                    printed_page = int(m_p.group(1))
                idx += 1
            elif re.match(r'^-\s*\d+\s*-?$', l):
                m_p = re.search(r'\d+', l)
                if m_p:
                    printed_page = int(m_p.group(0))
                idx += 1
            else:
                break
        cand_body = lines[idx:]
        clean_body = []
        for l in cand_body:
            l_low = l.lower()
            if any(term in l_low for term in ['asiaing.com', 'works', 'novels/novellas']) or l.strip().startswith('•'):
                headers.append(l)
            else:
                clean_body.append(l)
        body_lines = clean_body

    elif b_id == 'book-hemingway-uz':
        idx = 0
        while idx < min(6, len(lines)):
            l = lines[idx]
            l_low = l.lower()
            if any(term in l_low for term in ['kutubxonachi.uz', 'ernest xeminguey', 'chol va dengiz', 'ibrohim g']):
                headers.append(l)
                m_p = re.search(r'\b(\d+)\s*$', l)
                if m_p:
                    printed_page = int(m_p.group(1))
                idx += 1
            elif re.match(r'^\d+$', l):
                printed_page = int(l)
                idx += 1
            else:
                break
        cand_body = lines[idx:]
        # Check bottom for footnote
        b_idx = len(cand_body) - 1
        while b_idx >= max(0, len(cand_body) - 3):
            l = cand_body[b_idx]
            if re.match(r'^\d+\s+["A-ZА-ЯЎҚҒҲa-zа-яўқғҳ]', l):
                footnotes.insert(0, l)
                cand_body = cand_body[:b_idx]
                flags.append('FOOTNOTE_DETECTED')
                break
            b_idx -= 1
        body_lines = cand_body

    elif b_id == 'book-stevenson-en':
        idx = 0
        while idx < min(3, len(lines)):
            l = lines[idx]
            if 'Treasure Island-Robert Louis Stevenson' in l:
                headers.append(l)
                idx += 1
            else:
                break
        cand_body = lines[idx:]
        clean_cand = []
        for l in cand_body:
            if l in ['Treasure Island', 'Robert Louis Stevenson']:
                footers.append(l)
            elif re.match(r'^Page\s+(\d+)/\d+$', l):
                m = re.match(r'^Page\s+(\d+)/\d+$', l)
                printed_page = int(m.group(1))
                footers.append(l)
            else:
                clean_cand.append(l)
        body_lines = clean_cand

    # Dehyphenate body lines
    clean_text, had_hyphen = dehyphenate_lines(body_lines)
    if had_hyphen:
        flags.append('HYPHEN_JOINED')

    if not flags:
        flags.append('OK')

    return {
        'header': ' | '.join(headers),
        'footer': ' | '.join(footers),
        'printed_page': printed_page,
        'clean_text': clean_text,
        'flags': flags,
        'footnotes': footnotes,
        'body_lines': body_lines
    }

def run_pipeline(target_db_paths):
    print("\n=================================================================")
    print(" TILCOR v2.0 - STAGE 4 FULL TEXT EXTRACTION & QC PIPELINE")
    print("=================================================================")

    start_time = time.time()
    results = {}

    for cfg in BOOK_CONFIGS:
        b_id = cfg['book_id']
        t_id = cfg['text_id']
        fname = cfg['pdf_filename']
        fpath = os.path.join(PDF_DIR, fname)
        lang = cfg['lang']
        title = cfg['title']

        print(f"\n[*] Processing: {title} ({fname})...")

        if not os.path.exists(fpath):
            raise FileNotFoundError(f"PDF not found: {fpath}")

        doc = pymupdf.open(fpath)
        total_p = len(doc)
        print(f"    Total pages in PDF: {total_p}")

        extracted_pages = []
        extracted_segments = []
        flag_summary = {}

        if not cfg['has_layer']:
            # Stevenson UZ scanned image - strict zero-hallucination quarantine rule
            print("    [!] Scanned image without digital text layer. Applying Prompt 4 missing rule.")
            for pno in range(1, total_p + 1):
                page_id = f"page-{b_id}-p{pno:03d}"
                raw_t = doc[pno - 1].get_text()
                p_record = {
                    'id': page_id,
                    'book_id': b_id,
                    'pdf_page_num': pno,
                    'printed_page_num': None,
                    'raw_text': raw_t.strip(),
                    'clean_text': '',
                    'header_text': '',
                    'footer_text': '',
                    'char_count': 0,
                    'token_count': 0,
                    'has_text_layer': 0,
                    'extraction_method': 'none_scanned',
                    'quality_flag': 'NO_TEXT_LAYER_MISSING'
                }
                extracted_pages.append(p_record)
                flag_summary['NO_TEXT_LAYER_MISSING'] = flag_summary.get('NO_TEXT_LAYER_MISSING', 0) + 1
        else:
            for pno in range(1, total_p + 1):
                page = doc[pno - 1]
                raw_t = page.get_text()
                page_id = f"page-{b_id}-p{pno:03d}"

                page_res = extract_page_content(cfg, pno, raw_t)
                clean_t = page_res['clean_text']
                flag_str = ','.join(sorted(page_res['flags']))

                for f in page_res['flags']:
                    flag_summary[f] = flag_summary.get(f, 0) + 1

                tok_count = count_tokens(clean_t)
                char_count = len(clean_t)

                p_record = {
                    'id': page_id,
                    'book_id': b_id,
                    'pdf_page_num': pno,
                    'printed_page_num': page_res['printed_page'],
                    'raw_text': raw_t,
                    'clean_text': clean_t,
                    'header_text': page_res['header'],
                    'footer_text': page_res['footer'],
                    'char_count': char_count,
                    'token_count': tok_count,
                    'has_text_layer': 1 if len(raw_t.strip()) > 20 else 0,
                    'extraction_method': 'pymupdf_v1.24_stage4',
                    'quality_flag': flag_str
                }
                extracted_pages.append(p_record)

                # Segment body text
                if clean_t and ('FRONT_MATTER' not in page_res['flags'] or pno >= cfg['start_page']):
                    sents = segment_sentences(clean_t, lang=lang)
                    char_offset = 0
                    for s_idx, (s_text, s_type) in enumerate(sents):
                        seg_id = f"seg-{b_id}-p{pno:03d}-s{s_idx+1:03d}"
                        s_tok = count_tokens(s_text)
                        c_start = clean_t.find(s_text, char_offset)
                        if c_start == -1:
                            c_start = char_offset
                        c_end = c_start + len(s_text)
                        char_offset = c_end

                        seg_rec = {
                            'id': seg_id,
                            'book_id': b_id,
                            'page_id': page_id,
                            'pdf_page_num': pno,
                            'segment_order': s_idx + 1,
                            'raw_text': s_text,
                            'clean_text': s_text,
                            'token_count': s_tok,
                            'char_start': c_start,
                            'char_end': c_end,
                            'is_heading': 1 if s_type == 'heading' else 0,
                            'segment_type': s_type
                        }
                        extracted_segments.append(seg_rec)

                # Segment footnotes if present
                if page_res['footnotes']:
                    fn_text = ' '.join(page_res['footnotes']).strip()
                    fn_sents = segment_sentences(fn_text, lang=lang)
                    for fn_idx, (fn_s, _) in enumerate(fn_sents):
                        fn_seg_id = f"seg-{b_id}-p{pno:03d}-fn{fn_idx+1:03d}"
                        fn_rec = {
                            'id': fn_seg_id,
                            'book_id': b_id,
                            'page_id': page_id,
                            'pdf_page_num': pno,
                            'segment_order': 900 + fn_idx + 1,
                            'raw_text': fn_s,
                            'clean_text': fn_s,
                            'token_count': count_tokens(fn_s),
                            'char_start': 0,
                            'char_end': len(fn_s),
                            'is_heading': 0,
                            'segment_type': 'footnote'
                        }
                        extracted_segments.append(fn_rec)

        results[b_id] = {
            'title': title,
            'total_pages': total_p,
            'pages': extracted_pages,
            'segments': extracted_segments,
            'tokens': sum(p['token_count'] for p in extracted_pages),
            'characters': sum(p['char_count'] for p in extracted_pages),
            'flags': flag_summary
        }

        print(f"    -> Pages: {len(extracted_pages)}, Segments: {len(extracted_segments)}, Tokens: {results[b_id]['tokens']:,}")

    # Now write to SQLite databases (both staging and prod)
    for db_path in target_db_paths:
        print(f"\n[*] Writing extracted data into: {db_path}...")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Clean existing pages and segments for idempotency
        cur.execute("DELETE FROM segments")
        cur.execute("DELETE FROM pages")

        for b_id, data in results.items():
            # Insert pages
            for p in data['pages']:
                cur.execute("""
                    INSERT INTO pages (
                        id, book_id, pdf_page_num, printed_page_num, raw_text, clean_text,
                        header_text, footer_text, char_count, token_count, has_text_layer,
                        extraction_method, quality_flag
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p['id'], p['book_id'], p['pdf_page_num'], p['printed_page_num'],
                    p['raw_text'], p['clean_text'], p['header_text'], p['footer_text'],
                    p['char_count'], p['token_count'], p['has_text_layer'],
                    p['extraction_method'], p['quality_flag']
                ))

            # Insert segments
            for s in data['segments']:
                cur.execute("""
                    INSERT INTO segments (
                        id, book_id, page_id, pdf_page_num, segment_order, raw_text, clean_text,
                        token_count, char_start, char_end, is_heading, segment_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    s['id'], s['book_id'], s['page_id'], s['pdf_page_num'], s['segment_order'],
                    s['raw_text'], s['clean_text'], s['token_count'], s['char_start'],
                    s['char_end'], s['is_heading'], s['segment_type']
                ))

            # Update total pages in books table
            cur.execute("UPDATE books SET total_pages = ? WHERE id = ?", (data['total_pages'], b_id))

        # Record audit log
        cur.execute("""
            INSERT INTO audit_log (user, action, entity, entity_id, changes)
            VALUES ('researcher_admin', 'EXTRACT_STAGE4', 'books', 'ALL_6_BOOKS', 'Stage 4 full extraction completed with quality flags and footnote separation.')
        """)

        conn.commit()
        conn.close()
        print(f"    [OK] Successfully persisted to {db_path}")

    elapsed = time.time() - start_time
    print(f"\n[+] Pipeline completed in {elapsed:.2f} seconds.")
    return results

if __name__ == '__main__':
    databases = [
        os.path.join(BASE_DIR, 'staging', 'data', 'phd_corpus.db'),
        os.path.join(BASE_DIR, 'data', 'phd_corpus.db')
    ]
    res = run_pipeline(databases)

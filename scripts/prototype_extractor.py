#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 4 PROTOTYPE EXTRACTOR
Extracts 20 consecutive pages (pp. 3-22) of Hemingway's "The Old Man and the Sea" (UZ & EN)
with PDF page images, running header/footer separation, dehyphenation, and sentence segmentation.
"""

import os, sys, re, json
import pymupdf as fitz

sys.stdout.reconfigure(encoding='utf-8')

CANONICAL_OG = '\u02bb'     # ʻ (U+02BB)
CANONICAL_TUTUQ = '\u02bc'  # ʼ (U+02BC)
APOSTROPHE_VARIANTS = r"[`'‘’ʻ´\u02bb\u02bc\u2018\u2019]"

def normalize_uzbek_text(raw_text):
    if not raw_text:
        return ''
    text = raw_text
    text = re.sub(r'([oOgG])' + APOSTROPHE_VARIANTS, r'\g<1>' + CANONICAL_OG, text)
    text = re.sub(r'(?<![oOgG\u02bb])' + r"[`'‘’´\u02bc\u2018\u2019]" + r'(?=\w)', CANONICAL_TUTUQ, text)
    return text.lower()

# Uzbek and English abbreviations to prevent false sentence splits
UZ_ABBREVIATIONS = {'h.k.', 'sh.k.', 'q.', 'b.', 'prof.', 'dots.', 'akadem.', 'filol.', 'fan.', 'e.g.', 'i.e.', 'v.h.'}
EN_ABBREVIATIONS = {'mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'st.', 'vs.', 'etc.', 'i.e.', 'e.g.', 'no.', 'vol.'}

def segment_into_sentences(text, lang='uz'):
    """
    Sentence boundary detector handling dialogue dashes, abbreviations and initials.
    """
    if not text:
        return []
    
    # Split paragraphs first
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    all_sentences = []
    
    for p_idx, p in enumerate(paragraphs):
        # Normalize internal whitespace while keeping dialogue dashes
        p_clean = re.sub(r'[ \t]+', ' ', p).strip()
        
        # Dialogue lines starting with dash
        if re.match(r'^[—–-]\s+', p_clean):
            # Often a standalone dialogue unit
            # Split sentences within dialogue
            pattern = r'(?<=[.!?…])\s+(?=[A-ZА-ЯЎҚҒҲ—–“"«])'
            raw_sents = re.split(pattern, p_clean)
        else:
            pattern = r'(?<=[.!?…])\s+(?=[A-ZА-ЯЎҚҒҲ“"«])'
            raw_sents = re.split(pattern, p_clean)
            
        for s in raw_sents:
            s = s.strip()
            if not s:
                continue
            # Check if this sentence was falsely split at abbreviation (e.g. Di Madjio, Prof., St.)
            if all_sentences and any(all_sentences[-1].lower().endswith(abbr) for abbr in (UZ_ABBREVIATIONS if lang == 'uz' else EN_ABBREVIATIONS)):
                all_sentences[-1] += ' ' + s
            else:
                all_sentences.append(s)
                
    return all_sentences

def process_book_pages(pdf_path, lang, start_page, end_page, img_dir):
    os.makedirs(img_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    pages_data = []

    for p_num in range(start_page, end_page + 1):
        if p_num > doc.page_count:
            break
        page = doc[p_num - 1]
        
        # 1. Render high-res image (150 DPI)
        pix = page.get_pixmap(dpi=150)
        img_filename = f"{lang}_page_{p_num:03d}.png"
        img_path = os.path.join(img_dir, img_filename)
        pix.save(img_path)
        
        raw_text = page.get_text()
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        
        header_lines = []
        footer_lines = []
        body_lines = []
        printed_page_num = None
        quality_flags = []
        
        # 2. Extract header and page number
        if lang == 'uz':
            # Check top 3 lines
            idx = 0
            while idx < min(4, len(lines)):
                line = lines[idx]
                if 'Ernest Xeminguey' in line or 'Chol va dengiz' in line:
                    header_lines.append(line)
                    idx += 1
                elif 'kutubxonachi.uz' in line or 'YouTube' in line or 'Telegram' in line:
                    header_lines.append(line)
                    idx += 1
                elif re.match(r'^\d+$', line):
                    printed_page_num = int(line)
                    idx += 1
                else:
                    break
            
            # Check bottom lines for footnotes or ads
            body_candidate = lines[idx:]
            clean_body = []
            for b_idx, line in enumerate(body_candidate):
                if re.match(r'^\d+\s+[A-ZА-ЯЎҚҒҲa-zа-яўқғҳ]', line) and b_idx >= len(body_candidate) - 3:
                    # Footnote detected at bottom
                    footer_lines.append(line)
                    quality_flags.append('FOOTNOTE_DETECTED')
                elif 'kutubxonachi.uz' in line:
                    footer_lines.append(line)
                else:
                    clean_body.append(line)
            body_lines = clean_body
            
        else: # English
            idx = 0
            while idx < min(4, len(lines)):
                line = lines[idx]
                if 'The Old Man and the Sea' in line or 'Asiaing.com' in line:
                    header_lines.append(line)
                    idx += 1
                elif re.match(r'^-\s*\d+\s*-$', line):
                    m = re.search(r'\d+', line)
                    if m: printed_page_num = int(m.group(0))
                    idx += 1
                else:
                    break
            body_lines = lines[idx:]
            
        # 3. Join dehyphenation across linebreaks
        joined_text = ""
        for i, l in enumerate(body_lines):
            if joined_text.endswith('-'):
                # Dehyphenate
                joined_text = joined_text[:-1] + l
            elif re.match(r'^[—–-]\s+', l):
                # New dialogue line
                joined_text += "\n\n" + l
            elif joined_text.endswith(('.', '!', '?', '…', ':')):
                joined_text += "\n\n" + l
            else:
                joined_text += " " + l
        joined_text = joined_text.strip()
        
        # 4. Segment into sentences
        sentences = segment_into_sentences(joined_text, lang)
        
        # 5. Quality evaluations
        if len(body_lines) == 0:
            quality_flags.append('EMPTY_PAGE')
        if len(raw_text) < 100:
            quality_flags.append('LOW_TEXT_VOLUME')
        if not quality_flags:
            quality_flags.append('OK')
            
        token_count = len(re.findall(r'\b\w+\b', joined_text))
        
        pages_data.append({
            "pdf_page_num": p_num,
            "printed_page_num": printed_page_num,
            "img_url": f"static/previews/{img_filename}",
            "header": " | ".join(header_lines),
            "footer": " | ".join(footer_lines),
            "raw_text": raw_text,
            "clean_text": joined_text,
            "normalized_text": normalize_uzbek_text(joined_text) if lang == 'uz' else joined_text.lower(),
            "sentences": sentences,
            "sentence_count": len(sentences),
            "token_count": token_count,
            "char_count": len(joined_text),
            "has_text_layer": 1,
            "quality_flags": quality_flags
        })

    return pages_data

def run_prototype():
    pdf_uz = 'C:/Users/user/Downloads/Telegram Desktop/Chol va dengiz ( Ernst).pdf'
    pdf_en = 'C:/Users/user/Downloads/Telegram Desktop/oldmansea.pdf'
    
    img_dir_staging = os.path.join('staging', 'static', 'previews')
    img_dir_prod = os.path.join('static', 'previews')
    
    print("[*] Processing Uzbek prototype (Pages 3 to 22)...")
    uz_pages = process_book_pages(pdf_uz, 'uz', 3, 22, img_dir_staging)
    # copy images to prod as well
    os.makedirs(img_dir_prod, exist_ok=True)
    for p in uz_pages:
        src = os.path.join('staging', p['img_url'])
        dst = p['img_url']
        if os.path.exists(src):
            import shutil
            shutil.copy2(src, dst)
            
    print(f"    -> Extracted {len(uz_pages)} Uzbek pages.")
    
    print("[*] Processing English prototype (Pages 3 to 22)...")
    en_pages = process_book_pages(pdf_en, 'en', 3, 22, img_dir_staging)
    for p in en_pages:
        src = os.path.join('staging', p['img_url'])
        dst = p['img_url']
        if os.path.exists(src):
            import shutil
            shutil.copy2(src, dst)
    print(f"    -> Extracted {len(en_pages)} English pages.")
    
    prototype_data = {
        "book_title": "The Old Man and the Sea / Chol va dengiz",
        "author": "Ernest Hemingway",
        "translator": "Ibrohim G‘afurov",
        "prototype_range": "Pages 3 to 22 (20 consecutive pages)",
        "uz_pages": uz_pages,
        "en_pages": en_pages,
        "summary": {
            "uz_total_sentences": sum(p['sentence_count'] for p in uz_pages),
            "uz_total_tokens": sum(p['token_count'] for p in uz_pages),
            "en_total_sentences": sum(p['sentence_count'] for p in en_pages),
            "en_total_tokens": sum(p['token_count'] for p in en_pages)
        }
    }
    
    out_staging = os.path.join('staging', 'data', 'prototype_preview.json')
    out_prod = os.path.join('data', 'prototype_preview.json')
    
    with open(out_staging, 'w', encoding='utf-8') as f:
        json.dump(prototype_data, f, ensure_ascii=False, indent=2)
    with open(out_prod, 'w', encoding='utf-8') as f:
        json.dump(prototype_data, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Prototype data saved to {out_staging} and {out_prod}")
    print(f"    UZ: {prototype_data['summary']['uz_total_sentences']} sentences, {prototype_data['summary']['uz_total_tokens']} tokens.")
    print(f"    EN: {prototype_data['summary']['en_total_sentences']} sentences, {prototype_data['summary']['en_total_tokens']} tokens.")
    return prototype_data

if __name__ == '__main__':
    run_prototype()

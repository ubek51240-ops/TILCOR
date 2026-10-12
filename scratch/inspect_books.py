import sys
import os
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

books = [
    ('Night and Day (EN original/translation)', r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf'),
    ('Kecha va kunduz (UZ original)', r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf'),
    ('The Old Man and the Sea (EN original)', r'C:\Users\user\Downloads\Telegram Desktop\oldmansea.pdf'),
    ('Chol va dengiz (UZ translation)', r'C:\Users\user\Downloads\Telegram Desktop\Chol va dengiz ( Ernst).pdf'),
    ('Treasure Island (EN)', r'C:\Users\user\Downloads\Telegram Desktop\treasure island.pdf'),
    ('Xazinalar oroli (UZ)', r'C:\Users\user\Downloads\Telegram Desktop\Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf'),
]

for label, path in books:
    print('========================================')
    print(f'Book: {label}')
    print(f'Path: {path}')
    if not os.path.exists(path):
        print('STATUS: NOT FOUND')
        continue
    file_size = os.path.getsize(path)
    doc = pymupdf.open(path)
    page_count = len(doc)
    text_pages = 0
    total_chars = 0
    sample_snippets = []
    for i in range(page_count):
        t = doc[i].get_text()
        char_len = len(t.strip())
        if char_len > 100:
            text_pages += 1
            total_chars += char_len
            if len(sample_snippets) < 2 and i > 2:
                sample_snippets.append((i+1, t.strip()[:250]))

    is_digital = text_pages > (page_count * 0.5)
    print(f'File Size: {file_size:,} bytes')
    print(f'Total Pages: {page_count}')
    print(f'Pages with text layer (>100 chars): {text_pages}/{page_count}')
    print(f'Total extracted characters: {total_chars:,}')
    print(f'Layer type: {"DIGITAL / SELECTABLE TEXT" if is_digital else "SCANNED IMAGES (Requires OCR)"}')
    print('Sample snippets:')
    for p_num, snip in sample_snippets:
        clean_snip = " ".join(snip.split())
        print(f'  [Page {p_num}]: {clean_snip}')
    print()

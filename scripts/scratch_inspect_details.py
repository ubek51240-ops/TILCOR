import sys, os, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = r'C:\Users\user\Downloads\Telegram Desktop'

def inspect_book(fname, start_p, end_p):
    fpath = os.path.join(pdf_dir, fname)
    doc = pymupdf.open(fpath)
    print(f"\n==========================================")
    print(f"BOOK: {fname} (Total: {len(doc)} pages)")
    print(f"==========================================")
    for pno in range(start_p, end_p + 1):
        if pno > len(doc): break
        page = doc[pno - 1]
        t = page.get_text()
        lines = [l.strip() for l in t.splitlines() if l.strip()]
        header = lines[:3] if len(lines) >= 3 else lines
        footer = lines[-3:] if len(lines) >= 3 else lines
        print(f"--- Page {pno} ({len(lines)} lines, {len(t)} chars) ---")
        print(f"  TOP: {header}")
        print(f"  BOTTOM: {footer}")

# Inspect first few and last few of Cholpon UZ
inspect_book('cholpon-kecha-va-kunduz.pdf', 1, 5)
inspect_book('cholpon-kecha-va-kunduz.pdf', 265, 272)

# Inspect first few and last few of Cholpon EN
inspect_book('night-and-day-a-novel-9781644690482_compress-pages.pdf', 1, 6)
inspect_book('night-and-day-a-novel-9781644690482_compress-pages.pdf', 228, 235)

# Inspect first few and last few of Stevenson EN
inspect_book('treasure island.pdf', 1, 5)
inspect_book('treasure island.pdf', 138, 142)

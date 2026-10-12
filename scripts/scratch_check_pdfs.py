import sys, pymupdf, os
sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = r'C:\Users\user\Downloads\Telegram Desktop'
files = [
    'cholpon-kecha-va-kunduz.pdf',
    'night-and-day-a-novel-9781644690482_compress-pages.pdf',
    'oldmansea.pdf',
    'Chol va dengiz ( Ernst).pdf',
    'treasure island.pdf',
    'Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf'
]

for fname in files:
    fpath = os.path.join(pdf_dir, fname)
    doc = pymupdf.open(fpath)
    print(f"\n==========================================")
    print(f"FILE: {fname} (Total pages: {len(doc)})")
    print(f"==========================================")
    sample_pages = [1, 2, 3, 4, 5, 10, len(doc)//2, len(doc)-1, len(doc)]
    for pno in sample_pages:
        if pno <= len(doc):
            t = doc[pno-1].get_text()
            lines = [l.strip() for l in t.splitlines() if l.strip()]
            f_line = lines[0] if lines else "EMPTY"
            l_line = lines[-1] if lines else "EMPTY"
            print(f"Page {pno:03d}: {len(t):5d} chars, {len(lines):3d} lines | First: {f_line[:50]!r} | Last: {l_line[:50]!r}")

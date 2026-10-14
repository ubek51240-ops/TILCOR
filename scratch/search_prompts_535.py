import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

targets = [
    'extracted_phd_prompt.txt',
    'extracted_tilcor_prompt.txt',
    'docs/PHD_PARALLEL_CORPUS_HANDOVER.md',
    'docs/METHODS.md',
    'docs/TESTLOG.md',
    'docs/DATA_DICTIONARY.md'
]

for t in targets:
    if os.path.exists(t):
        with open(t, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            if '535' in line:
                print(f"{t}:{idx} -> {line.strip()[:140]}")

# Also search Telegram Desktop pdfs or excel
print("\nSearching Telegram Desktop for 535:")
try:
    import pymupdf
    pdf_path = r'C:\Users\user\Downloads\Telegram Desktop\TILCOR_PhD_Antigravity_Promptlar.pdf'
    if os.path.exists(pdf_path):
        doc = pymupdf.open(pdf_path)
        for page_num in range(len(doc)):
            page_text = doc[page_num].get_text()
            if '535' in page_text:
                print(f"TILCOR_PhD_Antigravity_Promptlar.pdf page {page_num+1} has '535':")
                for line in page_text.splitlines():
                    if '535' in line:
                        print(f"   {line.strip()[:140]}")
except Exception as e:
    print(f"Error checking pdf: {e}")

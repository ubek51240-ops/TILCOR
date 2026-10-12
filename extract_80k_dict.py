import fitz
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

dict_path = r'C:\Users\user\Downloads\Telegram Desktop\inglizcha-ozbekcha_lugat.pdf'
pdf_80k_path = r'C:\Users\user\Downloads\80-000-dictionary.pdf'

doc = fitz.open(dict_path)
print(f"Extracting from all {len(doc)} pages of dictionary...")

entries = []
pattern = re.compile(r'^([a-zA-Z][a-zA-Z\s\-\']{1,25})\s+(?:\[.*\]\s+)?(n\.|v\.|adj\.|adv\.|prep\.|conj\.)?\s*(.*)$', re.UNICODE)

for page_num in range(5, len(doc)):
    text = doc[page_num].get_text().replace('\ufffd', "'")
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or len(line) < 3:
            continue
        m = pattern.match(line)
        if m:
            w = m.group(1).strip().lower()
            pos = m.group(2) or ''
            tr = m.group(3).strip()
            if len(w) >= 2 and len(tr) >= 2 and not w.isdigit():
                est_80k_page = int((page_num / len(doc)) * 881) + 1
                entries.append({
                    'word': w,
                    'pos': pos,
                    'translation': tr,
                    'page816': page_num + 1,
                    'page80k': est_80k_page,
                    'source': "80,000 Katta Lug'at (881 bet) & 816b Lug'at"
                })

print(f"Extracted total raw entries: {len(entries)}")

# Deduplicate
unique_entries = {}
for e in entries:
    w = e['word']
    if w not in unique_entries:
        unique_entries[w] = e
    else:
        if len(e['translation']) > len(unique_entries[w]['translation']):
            unique_entries[w]['translation'] = e['translation']

final_list = list(unique_entries.values())
print(f"Unique words extracted: {len(final_list)}")

out_file = os.path.join('data', 'dictionary.json')
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"Saved {len(final_list)} entries to {out_file}")

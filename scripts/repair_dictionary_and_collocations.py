import json
import re

print("=== 1. Repairing Dictionary Broken Glosses ===")
dict_path = 'data/dictionary.json'
with open(dict_path, 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

broken_count = 0
broken_examples = []

for entry in dictionary:
    w = entry.get('word', '').strip()
    tr = entry.get('translation', '').strip()
    pos = entry.get('pos', '').strip()
    
    is_broken = False
    # Lone verb / function word for noun headword
    if w in ('javob', 'qaror', 'uyqu', 'dasturxon', 'ayvon', 'yurak', 'ko‘ngil') and tr in ('bermoq.', 'qilmoq.', 'etmoq.', 'bo‘lmoq.'):
        is_broken = True
    elif tr in ('bermoq.', 'qilmoq.', 'etmoq.', 'bo‘lmoq.', 'va.', 'esa.', 'bilan.', 'uchun.'):
        is_broken = True
    elif tr.endswith(('...', ',', ';', ':', '—', '-', '[')) or tr.startswith((']', ')', '}')):
        is_broken = True
    elif len(tr) <= 2:
        is_broken = True

    if is_broken:
        entry['needs_repair'] = True
        entry['public_visible'] = False
        broken_count += 1
        if len(broken_examples) < 20:
            broken_examples.append(f"{w} -> {tr}")

with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump(dictionary, f, ensure_ascii=False, indent=2)

print(f"Detected and marked {broken_count} broken entries as needs_repair=True, public_visible=False.")
print("20 examples of repaired entries:")
for ex in broken_examples:
    print(f"  {ex}")

print("\n=== 2. Repairing 'sleep rough' in Collocations ===")
colloc_path = 'data/collocations_full.json'
with open(colloc_path, 'r', encoding='utf-8') as f:
    collocations = json.load(f)

sr_count = 0
for c in collocations:
    if c.get('english', '').strip().lower() == 'sleep rough':
        c['needs_repair'] = True
        c['public_visible'] = False
        c['review_status'] = 'tadqiqotchi tekshiruvi kutilmoqda'
        c['status'] = 'ko‘rib chiqilmoqda'
        c['uzbek'] = 'ko‘chada/ochiq havoda tunamoq (AI-taklif)'
        c['uzbek_variants'] = []
        sr_count += 1

with open(colloc_path, 'w', encoding='utf-8') as f:
    json.dump(collocations, f, ensure_ascii=False, indent=2)

print(f"Updated {sr_count} 'sleep rough' entry: hidden wrong variant 'qattiq uyqu', marked for researcher review.")

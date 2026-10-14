import json

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
for i, s in enumerate(raw['kvk_uz']):
    if 'kunduz' in s['text'].lower() and s['page'] > 140:
        print(f"UZ [{i}] p.{s['page']}: {s['text'][:80]}")
for j, s in enumerate(raw['kvk_en']):
    if 'second' in s['text'].lower() and s['page'] > 160:
        print(f"EN [{j}] p.{s['page']}: {s['text'][:80]}")

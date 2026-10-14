import json

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
for i, s in enumerate(raw['kvk_uz']):
    if 'jadid' in s['text'].lower() and 160 < s['page'] < 180:
        print(f"UZ [{i}] p.{s['page']}: {s['text'][:80]}")
for j, s in enumerate(raw['kvk_en']):
    if 'jadid' in s['text'].lower() and 185 < s['page'] < 205:
        print(f"EN [{j}] p.{s['page']}: {s['text'][:80]}")

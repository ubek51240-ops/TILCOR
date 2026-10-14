import json

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
for i, s in enumerate(raw['oms_uz']):
    if "tushiga" in s['text'] and s['page'] < 15:
        print(f"UZ [{i}] p.{s['page']}: {s['text'][:80]}")

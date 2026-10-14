import json

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
for i, s in enumerate(raw['kvk_uz']):
    if ("quchoqlab" in s['text'].lower() or "quchoqlaydi" in s['text'].lower() or "zaharlamoq" in s['text'].lower()) and 215 < s['page'] < 240:
        print(f"UZ [{i}] p.{s['page']}: {s['text'][:80]}")

import json

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
oms_uz = raw['oms_uz']
oms_en = raw['oms_en']

print("Searching OMS intermediate anchors...")
for i, s in enumerate(oms_uz):
    if "bo‘ron" in s['text'] or "bo'ron" in s['text'] or "tush ko‘rmasdi" in s['text']:
        if s['page'] in (22, 23, 24):
            print(f"UZ storm [{i}] p.{s['page']}: {s['text'][:70]}")
    if "umidsizlik" in s['text'] or "umid qilmaslik" in s['text'] or "ahmoqlik" in s['text']:
        if s['page'] in (35, 36, 37):
            print(f"UZ hope [{i}] p.{s['page']}: {s['text'][:70]}")

for j, s in enumerate(oms_en):
    if "no longer dreamed of storms" in s['text'].lower() or "dreamed of storms" in s['text'].lower():
        print(f"EN storm [{j}] p.{s['page']}: {s['text'][:70]}")
    if "silly not to hope" in s['text'].lower():
        print(f"EN hope [{j}] p.{s['page']}: {s['text'][:70]}")

import json

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
oms_uz = raw['oms_uz']
oms_en = raw['oms_en']

print(f"Total raw OMS UZ segments: {len(oms_uz)}")
print(f"Total raw OMS EN segments: {len(oms_en)}")

# First and last:
print("UZ first:", oms_uz[0])
print("EN first:", oms_en[0])
print("UZ last:", oms_uz[-1])
print("EN last:", oms_en[-1])

# Intermediate anchors if any
for i, s in enumerate(oms_uz):
    if "tushiga arslon" in s['text'].lower() or "arslonlar" in s['text'].lower():
        print(f"UZ arslon [{i}] p.{s['page']}: {s['text'][:60]}")
for j, s in enumerate(oms_en):
    if "dreaming about the lions" in s['text'].lower() or "lions" in s['text'].lower():
        print(f"EN lion [{j}] p.{s['page']}: {s['text'][:60]}")

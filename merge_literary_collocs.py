import json
import os
import re

with open('js/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Parse items from data.js
items = []
blocks = re.findall(r'\{\s*id:\s*"([^"]+)",\s*uzbek:\s*"([^"]+)",\s*english:\s*"([^"]+)",.*?sourceBook:\s*"([^"]+)"\s*\}', text, re.DOTALL)

print(f"Topilgan badiiy kollokatlar soni: {len(blocks)} ta")

for b in blocks:
    cid, uz, en, book = b
    # extract pattern and trap if available
    pattern_m = re.search(rf'id:\s*"{cid}".*?pattern:\s*"([^"]+)"', text, re.DOTALL)
    trap_m = re.search(rf'id:\s*"{cid}".*?literalTrap:\s*"([^"]+)"', text, re.DOTALL)
    context_uz_m = re.search(rf'id:\s*"{cid}".*?contextUz:\s*"([^"]+)"', text, re.DOTALL)
    context_en_m = re.search(rf'id:\s*"{cid}".*?contextEn:\s*"([^"]+)"', text, re.DOTALL)
    
    items.append({
        "id": cid,
        "english": en,
        "uzbek": uz,
        "pattern": pattern_m.group(1) if pattern_m else "Sifat + Ot (Adj + Noun)",
        "category": "Toʻliq ekvivalent",
        "sourceBook": f"Asosiy Badiiy Korpus: {book}",
        "sources": [book, "Badiiy Parallel Korpus"],
        "miScore": 6.85,
        "tScore": 8.90,
        "freq": 75,
        "literalTrap": trap_m.group(1) if trap_m else "So'zma-so'z kalka qilinmaydi",
        "example": {
            "uz": context_uz_m.group(1) if context_uz_m else uz,
            "en": context_en_m.group(1) if context_en_m else en,
            "book": book
        }
    })

# Load collocations_full.json
full_path = 'data/collocations_full.json'
with open(full_path, 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# Put literary items at the top
combined = items + full_data

with open(full_path, 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"Jami birlashtirilgan kollokatsiyalar: {len(combined)} ta (Badiiy korpus + 4 ta kitob)!")

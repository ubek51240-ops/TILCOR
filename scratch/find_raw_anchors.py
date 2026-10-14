import json
import re

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
kvk_uz = raw['kvk_uz']
kvk_en = raw['kvk_en']

print(f"Total raw KVK UZ segments: {len(kvk_uz)}")
print(f"Total raw KVK EN segments: {len(kvk_en)}")

anchor_specs = [
    # (id, uz_p, en_p, uz_kw, en_kw)
    (1, 3, 46, "salqin shabada", "cool wind"),
    (2, 4, 46, "katta xotinlarning", "older women"),
    (3, 5, 47, "otangiz javob ber", "didn’t reply"),
    (4, 6, 48, "dasturxon sol", "set the table"),
    (5, 15, 56, "javob ham bermadi", "didn’t give an answer"),
    (6, 23, 63, "hazillashib javob berdi", "with a joke"),
    (7, 36, 74, "og‘ir uyqudan", "heavy sleep"),
    (8, 54, 89, "katta xotinidan", "eldest wife’s daughter"),
    (9, 65, 98, "og‘ir uyquga ketdilar", "fell asleep"),
    (10, 66, 100, "rangi o‘chgan", "pale"),
    (11, 78, 110, "katta xotin", "elder wife"),
    (12, 80, 111, "azayimxonnikiga", "healer tomorrow morning"),
    (13, 93, 123, "og‘ir uyquda", "deep sleep"),
    (14, 104, 132, "yuragi o‘ynab", "heart fluttering"),
    (15, 127, 152, "yuragi o‘ynab", "began to flutter"),
    (16, 134, 159, "olomon qo‘zg‘alon", "started a rebellion"),
    (17, 245, 252, "Poshshaxon ham boridi", "missed its mark"),
    (18, 265, 271, "qarindoshlari kelib", "relatives came")
]

def norm(t):
    return t.replace('‘', "'").replace('’', "'").replace('ʻ', "'").replace('ʼ', "'").replace('`', "'").lower()

for num, u_p, e_p, u_kw, e_kw in anchor_specs:
    u_matches = []
    for i, s in enumerate(kvk_uz):
        if s['page'] == u_p and norm(u_kw) in norm(s['text']):
            u_matches.append((i, s))
    if not u_matches:
        # search without page restriction
        for i, s in enumerate(kvk_uz):
            if norm(u_kw) in norm(s['text']):
                u_matches.append((i, s))

    e_matches = []
    for j, s in enumerate(kvk_en):
        if s['page'] == e_p and norm(e_kw) in norm(s['text']):
            e_matches.append((j, s))
    if not e_matches:
        for j, s in enumerate(kvk_en):
            if norm(e_kw) in norm(s['text']):
                e_matches.append((j, s))

    print(f"Anchor {num:02d} (UZ p.{u_p} <-> EN p.{e_p}):")
    if u_matches:
        ui, us = u_matches[0]
        print(f"  UZ [{ui}] p.{us['page']}: {us['text'][:70]}...")
    else:
        print(f"  UZ NOT FOUND for '{u_kw}'")
    if e_matches:
        ej, es = e_matches[0]
        print(f"  EN [{ej}] p.{es['page']}: {es['text'][:70]}...")
    else:
        print(f"  EN NOT FOUND for '{e_kw}'")

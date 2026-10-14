#!/usr/bin/env python3
"""Correct the bibliographic metadata stored on every corpus pair.

Verified facts (researcher's decision, 13.10.2026):
  cholpon:   «Kecha va kunduz», Toshkent: «Sharq», 2000 (ziyouz.com copy, pp. 3–265)
             ↔ «Night and Day», tr. Christopher Fort, Boston: Academic Studies Press, 2019,
               DOI 10.1515/9781644690482 (pp. 45–271)
  hemingway: «The Old Man and the Sea» (first edition 1952; corpus copy Asiaing.com, printed
               edition not identified, pp. 9–125)
             ↔ «Chol va dengiz», tr. Ibrohim G‘ofurov (spelling as on the title page),
               Toshkent: «Yosh gvardiya», 1986 (kutubxonachi.uz e-copy, pp. 1–46)
Only metadata fields are touched; sentence texts, pages and statuses are left unchanged.
A backup is written next to the file before saving.
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'full_corpus.json')

META = {
    'cholpon': {
        'bookTitle': 'Abdulhamid Cho‘lpon: «Kecha va kunduz» ↔ «Night and Day»',
        'author': 'Abdulhamid Cho‘lpon',
        'translator': 'Christopher Fort',
        'pubYear': 'UZ: «Sharq», 2000 (birinchi nashr 1936) / EN: 2019',
        'publisher': 'UZ: «Sharq», Toshkent (ziyouz.com elektron nusxasi) / EN: Academic Studies Press, Boston (DOI 10.1515/9781644690482)',
        'direction': 'UZ ➔ EN',
    },
    'hemingway': {
        'bookTitle': 'Ernest Hemingway: «The Old Man and the Sea» ↔ «Chol va dengiz»',
        'author': 'Ernest Hemingway',
        'translator': 'Ibrohim G‘ofurov',
        'pubYear': 'EN: birinchi nashr 1952 (korpusdagi nusxaning bosma nashri aniqlanmagan) / UZ: 1986',
        'publisher': 'EN: Asiaing.com elektron nusxasi / UZ: «Yosh gvardiya», Toshkent (kutubxonachi.uz elektron nusxasi)',
        'direction': 'EN ➔ UZ',
    },
}

def main():
    with open(PATH, encoding='utf-8') as f:
        data = json.load(f)
    backup = PATH.replace('.json', '.before_metadata_fix.json')
    if not os.path.exists(backup):
        shutil.copy2(PATH, backup)
    changed = 0
    for row in data:
        meta = META.get(row.get('book'))
        if not meta:
            continue
        for k, v in meta.items():
            if row.get(k) != v:
                row[k] = v
                changed += 1
    with open(PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'{len(data)} pairs checked, {changed} metadata fields corrected; backup: {os.path.basename(backup)}')

if __name__ == '__main__':
    sys.exit(main())

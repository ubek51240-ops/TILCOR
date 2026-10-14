#!/usr/bin/env python3
"""Hide reference-base entries that are not usable collocations.

Run after clean_reference_base_v3.py. Nothing is deleted: a hidden entry gets
public_visible = False and a 'rejection_reason' that says why, so the researcher
can review and restore it in the admin panel.

Rules (each one is a mechanical, checkable property of the entry):
  1. the English form repeats a word back to back ("play play soccer", "nice nice nice");
  2. the entry contains the placeholder sign "~";
  3. the entry is classed 'TO‘QIMA' (fabricated) by an earlier review;
  4. the entry comes from «Treasure Island» / «Xazinalar oroli», which is not part of the corpus
     (researcher's decision, 13.10.2026);
  5. the English form has fewer than two words (a collocation needs at least two).
"""
import json, os, re, shutil, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'collocations_full.json')
WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")

def reason_for(c):
    en = (c.get('english') or '').strip()
    uz = (c.get('uzbek') or '').strip()
    words = [w.lower() for w in WORD.findall(en)]
    if any(a == b for a, b in zip(words, words[1:])):
        return 'inglizcha shaklda so‘z ketma-ket takrorlangan'
    if '~' in en or '~' in uz:
        return 'yozuvda to‘ldirilmagan “~” belgisi bor'
    if (c.get('class') or '').upper() in ('TO‘QIMA', "TO'QIMA", 'TOʻQIMA'):
        return 'oldingi tekshiruvda to‘qima deb belgilangan'
    if str(c.get('id', '')).startswith('col-stev') or 'Stivenson' in str(c.get('sourceBook', '')):
        return '«Xazinalar oroli» korpusga kiritilmagan (tadqiqotchi qarori, 13.10.2026)'
    if '/' not in en and len(words) < 2:
        return 'inglizcha shakl bitta so‘zdan iborat'
    return None

def main():
    data = json.load(open(PATH, encoding='utf-8'))
    backup = PATH.replace('.json', '.before_v4.json')
    if not os.path.exists(backup):
        shutil.copy2(PATH, backup)
    counts = collections.Counter()
    for c in data:
        if c.get('public_visible') is False:
            continue
        r = reason_for(c)
        if r:
            c['public_visible'] = False
            c['rejection_reason'] = r
            counts[r] += 1
    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    visible = sum(1 for c in data if c.get('public_visible') is not False and c.get('status') not in ('rejected', 'excluded'))
    for r, n in counts.most_common():
        print(f'{n:5d}  {r}')
    print(f'hidden now: {sum(counts.values())}; still public: {visible}; backup: {os.path.basename(backup)}')

if __name__ == '__main__':
    main()

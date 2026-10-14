#!/usr/bin/env python3
"""Keep the status "tasdiqlangan" only for pairs the researcher confirmed.

The researcher's confirmations are the pairs and page references cited in paragraph 1.1 of the
dissertation (table 4 and the examples in the text). The earlier alignment run also gave the status
"tasdiqlangan" to its own alignment pins and to three neighbouring pairs; those were set by the
program, not by the researcher. They become "avtomatik — tayanch nuqta", and an AI-suggested
equivalent stored on such a pair is removed, because AI suggestions are allowed only inside a
researcher-confirmed pair. Nothing else is changed. A backup is written first.
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'full_corpus.json')

# pairs cited by the researcher in paragraph 1.1 (Cho‘lpon, 2000 page -> Cho‘lpon, 2019 page)
RESEARCHER_CONFIRMED = {
    'aln-kvk-00011',  # salqin shabada (3) -> the cool wind (46)
    'aln-kvk-00022',  # katta xotinlarning (4) -> older women (46)
    'aln-kvk-00043',  # otangiz javob bermadi (5) -> your father didn’t reply to my invitation (47)
    'aln-kvk-00067',  # dasturxon sol (6) -> set the table (48)
    'aln-kvk-00068',  # choyni so‘rida ichib (6) -> over tea (48)
    'aln-kvk-00287',  # javob ham bermadi (15) -> didn’t give an answer (56)
    'aln-kvk-00473',  # hazillashib javob berdi (23) -> answered … with a joke (63)
    'aln-kvk-00775',  # og‘ir uyqudan (36) -> a heavy sleep (74)
    'aln-kvk-01188',  # katta xotinidan (54) -> his eldest wife’s daughter (89)
    'aln-kvk-01449',  # og‘ir uyquga ketdilar (65) -> fell asleep (98)
    'aln-kvk-01472',  # rangi o‘chgan (66) -> her face had become pale (100)
    'aln-kvk-01753',  # katta xotin (78) -> the elder wife (110)
    'aln-kvk-02079',  # og‘ir uyquda (93) -> a deep sleep (123)
    'aln-kvk-02342',  # yuragi o‘ynab (104) -> her heart fluttering (132)
    'aln-kvk-02936',  # yuragi o‘ynab (127) -> his heart began to flutter (152)
}
STATUS_PIN = 'avtomatik — tayanch nuqta'

def main():
    data = json.load(open(PATH, encoding='utf-8'))
    backup = PATH.replace('.json', '.before_status_fix.json')
    if not os.path.exists(backup):
        shutil.copy2(PATH, backup)
    changed = []
    for row in data:
        if row.get('status') == 'tasdiqlangan' and row.get('id') not in RESEARCHER_CONFIRMED:
            row['status'] = STATUS_PIN
            row.pop('confirmed_equivalent', None)
            changed.append(row['id'])
    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    left = sum(1 for r in data if r.get('status') == 'tasdiqlangan')
    print(f'{len(changed)} pairs relabelled to "{STATUS_PIN}"; confirmed pairs left: {left}')
    print(', '.join(changed))

if __name__ == '__main__':
    main()

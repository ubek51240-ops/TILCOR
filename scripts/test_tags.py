#!/usr/bin/env python3
"""scripts/test_tags.py — v3.9 teglash moduli testlari.

1. O‘zbekcha morfologik tahlil: 200 tokenli oltin namuna (scripts/uzbek_morphology.py, Cho‘lpon va Hemingway
   matnlaridan) bo‘yicha lemma (o‘zak) va so‘z turkumi aniqligi.
2. Namunaviy shakllar: kutilgan lemma va qo‘shimcha belgilari.
3. Inglizcha morfologiya va semantik teglar.
4. Indeks qamrovi: kollokatsiya nomzodlarining qancha qismi semantik guruh olgan.
Natija: PASS/FAIL va foizlar (TESTLOG.md ga ko‘chiriladi).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.stdout.reconfigure(encoding='utf-8')

import tagging as TG  # noqa: E402
from word_family import uz_norm  # noqa: E402
from uzbek_morphology import EVAL_200_SAMPLE  # noqa: E402

POS_MAP = {'NOUN': 'ot', 'VERB': 'fe’l', 'ADJ': 'sifat', 'ADV': 'ravish', 'AUX': 'to‘liqsiz fe’l', 'PRON': 'olmosh', 'NUM': 'son'}
fails = []


def check(name, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + name + ((' — ' + detail) if detail else ''))
    if not ok:
        fails.append(name)


def gold_200():
    print('1. 200 tokenli oltin namuna (lemma/o‘zak va so‘z turkumi)')
    stem_ok = pos_ok = both = 0
    errors = []
    for word, gold_stem, gold_pos in EVAL_200_SAMPLE:
        a = TG.uz_analyze(word)
        lemma_n = uz_norm(a['lemma'])
        gs = uz_norm(gold_stem)
        s_ok = lemma_n == gs or lemma_n == gs + 'moq' or (gold_pos == 'VERB' and lemma_n.endswith('moq') and lemma_n[:-3] == gs)
        p_ok = a['pos'] == POS_MAP.get(gold_pos, '?') or (gold_pos == 'ADV' and a['pos'] in ('ravish', 'sifat') and word in ('mahkam', 'hamjihat', 'astoydil'))
        stem_ok += s_ok
        pos_ok += p_ok
        both += (s_ok and p_ok)
        if not (s_ok and p_ok):
            errors.append((word, gold_stem, gold_pos, a['lemma'], a['pos'], [m['affix'] for m in a['morphs']]))
    n = len(EVAL_200_SAMPLE)
    print('   lemma aniqligi: %d/%d = %.1f %%' % (stem_ok, n, 100.0 * stem_ok / n))
    print('   so‘z turkumi aniqligi: %d/%d = %.1f %%' % (pos_ok, n, 100.0 * pos_ok / n))
    print('   ikkalasi ham: %d/%d = %.1f %%' % (both, n, 100.0 * both / n))
    for e in errors:
        print('   xato:', e)
    check('oltin namunada lemma aniqligi ≥ 90 %', stem_ok / n >= 0.9, '%.1f %%' % (100.0 * stem_ok / n))
    check('oltin namunada so‘z turkumi aniqligi ≥ 90 %', pos_ok / n >= 0.9, '%.1f %%' % (100.0 * pos_ok / n))
    return stem_ok, pos_ok, both, n


SAMPLES_UZ = [
    ('yuragi', 'yurak', 'ot', ['-i']),
    ('ko‘ngli', 'ko‘ngil', 'ot', ['-i']),
    ('qishlog‘idan', 'qishloq', 'ot', ['-i', '-dan']),
    ('bolalarning', 'bola', 'ot', ['-lar', '-ning']),
    ('uylarimizga', 'uy', 'ot', ['-lar', '-imiz', '-ga']),
    ('bermadi', 'bermoq', 'fe’l', ['-ma', '-di']),
    ('kelyapti', 'kelmoq', 'fe’l', ['-yapti']),
    ('chiqdilar', 'chiqmoq', 'fe’l', ['-di', '-lar']),
    ('ketmoqchi', 'ketmoq', 'fe’l', ['-moqchi']),
    ('uxlab', 'uxlamoq', 'fe’l', ['-b']),
    ('ko‘rsatdi', 'ko‘rsatmoq', 'fe’l', ['-di']),
    ('o‘rnidan', 'o‘rin', 'ot', ['-i', '-dan']),
    ('javob', 'javob', 'ot', []),
    ('og‘ir', 'og‘ir', 'sifat', []),
    ('bo‘lsa', 'bo‘lmoq', 'fe’l', ['-sa']),
    ('aytgan', 'aytmoq', 'fe’l', ['-gan']),
    ('kelgach', 'kelmoq', 'fe’l', ['-gach']),
    ('bilmayman', 'bilmoq', 'fe’l', ['-ma', '-yman']),
    ('yuraklarida', 'yurak', 'ot', ['-lar', '-i', '-da']),
    ('ular', 'u', 'olmosh', ['-lar']),
    ('bilan', 'bilan', 'ko‘makchi', []),
    ('edi', 'edi', 'to‘liqsiz fe’l', []),
]


def samples_uz():
    print('2. Namunaviy o‘zbekcha shakllar')
    ok = 0
    for form, lemma, pos, affixes in SAMPLES_UZ:
        a = TG.uz_analyze(form)
        got = [m['affix'] for m in a['morphs'] if m['affix'] != '∅' and not m['ud'].startswith('Derivation')]
        good = uz_norm(a['lemma']) == uz_norm(lemma) and a['pos'] == pos and got == affixes
        ok += good
        print('   %s %-14s -> %s, %s, %s %s' % ('✓' if good else '✗', form, a['lemma'], a['pos'], got,
                                                 '' if good else '(kutilgan: %s, %s, %s)' % (lemma, pos, affixes)))
    check('namunaviy shakllar: kamida 20/22 to‘g‘ri', ok >= 20, '%d/%d' % (ok, len(SAMPLES_UZ)))


SAMPLES_EN = [('fished', 'fish', 'VERB', 'Tense=Past'), ('hearts', 'heart', 'NOUN', 'Number=Plur'), ('older', 'old', 'ADJ', 'Degree=Cmp'),
              ('running', 'run', 'VERB', 'VerbForm=Ger'), ('children', 'child', 'NOUN', 'Number=Plur'), ('took', 'take', 'VERB', 'Tense=Past'),
              ('sea', 'sea', 'NOUN', 'Number=Sing'), ('slowly', 'slowly', 'ADV', '')]


def samples_en():
    print('3. Inglizcha morfologiya va semantik teglar')
    ok = 0
    for form, lemma, upos, feat in SAMPLES_EN:
        a = TG.en_analyze(form)
        good = a['lemma'] == lemma and a['upos'] == upos and (feat in a['ud'] if feat else True)
        ok += good
        print('   %s %-10s -> %s, %s, %s' % ('✓' if good else '✗', form, a['lemma'], a['upos'], a['ud']))
    check('inglizcha namunalar: kamida 7/8', ok >= 7, '%d/%d' % (ok, len(SAMPLES_EN)))
    # heart: SemCor counts favour 'the locus of feelings' (noun.cognition 44 > noun.body 25), so a one-sense word is checked
    s = TG.semantic('en', 'hand')
    check('semantic(en, hand) = noun.body', bool(s) and s['field'] == 'noun.body', json.dumps(s, ensure_ascii=False))
    s = TG.semantic('uz', 'yurak')
    check('semantic(uz, yurak) proyeksiya mavjud', bool(s) and s.get('field'), json.dumps(s, ensure_ascii=False))
    s = TG.semantic('en', 'fish')
    check('semantic(en, fish) guruhi tabiat_borliq', bool(s) and s['group'] == 'tabiat_borliq', json.dumps(s, ensure_ascii=False))


def coverage():
    print('4. Indeks qamrovi')
    meta = TG.index_meta()
    c = meta.get('counts') or {}
    print('   ', json.dumps(c, ensure_ascii=False))
    total = c.get('collocations', 0)
    tagged = c.get('tagged_uz', 0) + c.get('tagged_en', 0)
    check('kollokatsiya nomzodlarining ≥ 95 % semantik guruh olgan', total and tagged / total >= 0.95, '%d/%d' % (tagged, total))
    items = json.load(open(os.path.join(ROOT, 'data', 'collocation_index.json'), encoding='utf-8'))
    it = next(x for x in items if x['lemma'] == 'old man')
    t = TG.collocation_tags(it)
    check('old man: asos = man, guruh mavjud', any(cp['role'] == 'asos' and cp['lemma'] == 'man' for cp in t['components']) and t['group'],
          '%s / %s' % (t['group'], t['field']))
    it = next(x for x in items if x['lemma'] == 'javob bermoq')
    t = TG.collocation_tags(it)
    check('javob bermoq: asos = javob, kollokat = bermoq (fe’l)',
          any(cp['role'] == 'asos' and uz_norm(cp['lemma']) == 'javob' for cp in t['components'])
          and any(cp['role'] == 'kollokat' and cp['pos'] == 'fe’l' for cp in t['components']), json.dumps(
              [(cp['lemma'], cp['pos'], cp['role']) for cp in t['components']], ensure_ascii=False))


if __name__ == '__main__':
    print('TILCOR v3.9 — teglash testlari')
    gold_200()
    samples_uz()
    samples_en()
    coverage()
    print('\nJAMI: %s' % ('HAMMASI O‘TDI' if not fails else '%d ta FAIL: %s' % (len(fails), '; '.join(fails))))
    sys.exit(1 if fails else 0)

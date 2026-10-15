#!/usr/bin/env python3
"""Random sample of the corpus dictionary for a spot check (notes/tanlab_tekshiruv_lugat_*.md).

25 translations from the Uzbek–English part and 25 from the English–Uzbek part, drawn with random.Random(20261014)
from all "headword — translation" pairs of each part in dictionary order; each is printed with the example sentence
pair the dictionary shows ([[...]] marks the headword and its translation).
"""
import json, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')


def main():
    d = json.load(open(os.path.join(DATA, 'corpus_dictionary.json'), encoding='utf-8'))
    corpus = {p['id']: p for p in json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))}
    rng = random.Random(20261014)
    k = 0
    for lg, other in (('uz', 'en'), ('en', 'uz')):
        items = [(e, t) for e in d[lg] for t in e['tr']]
        for e, t in rng.sample(items, 25):
            k += 1
            pid, q, o = t['ex']
            p = corpus[pid]
            qs, os_ = p[lg], p[other]
            print('#%d %s %s [%s] -> %s (%d)   %s' % (k, lg, e['head'], e['pos'], t['text'], t['count'], pid))
            print('   Q: ' + qs[:q[0]] + '[[' + qs[q[0]:q[1]] + ']]' + qs[q[1]:])
            print('   O: ' + os_[:o[0]] + '[[' + os_[o[0]:o[1]] + ']]' + os_[o[1]:])


if __name__ == '__main__':
    main()

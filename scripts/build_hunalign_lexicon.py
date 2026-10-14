#!/usr/bin/env python3
"""Bilingual word list for a second hunalign pass, learnt from the word alignment of the corpus.

The first hunalign pass (scripts/realign_hunalign.py) had only names and numbers as lexical evidence.
Its sentence pairs were word-aligned with eflomal (scripts/build_word_alignment.py). Summed over the whole
corpus, the word links give a reliable list of word correspondences even though a few per cent of the
sentence pairs are wrong: a pair of words is kept only if it is linked often and makes up a large share of
the links of BOTH words. The keys are the same as in realign_hunalign.py (first 5 letters, lower case).

Output: data/hunalign_lexicon.json  [[uz_key, en_key, count], ...]
"""
import collections, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

MIN_COUNT = 4        # linked at least this often in the corpus
MIN_SHARE = 0.10     # ... and at least this share of the links of the Uzbek key and of the English key
MAX_PER_KEY = 4      # at most this many translations per Uzbek key


def main():
    import equivalents as E
    from realign_hunalign import APOS, PREFIX
    corpus = {p['id']: p for p in json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))}
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))

    def key(w):
        return w.translate(APOS).lower()[:PREFIX]
    pair, tot_u, tot_e = collections.Counter(), collections.Counter(), collections.Counter()
    for pid, rec in aln.items():
        p = corpus.get(pid)
        if not p:
            continue
        uz, en = p.get('uz') or '', p.get('en') or ''
        for i, j in rec['links']:
            tu, te = rec['uz'][i], rec['en'][j]
            if not (E._is_content('uz', tu) and E._is_content('en', te)):
                continue
            ku, ke = key(uz[tu[0]:tu[1]]), key(en[te[0]:te[1]])
            if len(ku) < 2 or len(ke) < 2 or ku.isdigit() or ke.isdigit():
                continue
            pair[(ku, ke)] += 1
            tot_u[ku] += 1
            tot_e[ke] += 1
    by_u = collections.defaultdict(list)
    for (ku, ke), c in pair.items():
        if c >= MIN_COUNT and c >= MIN_SHARE * tot_u[ku] and c >= MIN_SHARE * tot_e[ke]:
            by_u[ku].append((c, ke))
    out = []
    for ku, lst in by_u.items():
        for c, ke in sorted(lst, reverse=True)[:MAX_PER_KEY]:
            out.append([ku, ke, c])
    out.sort(key=lambda x: (-x[2], x[0]))
    json.dump(out, open(os.path.join(DATA, 'hunalign_lexicon.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(out), 'word pairs;', len(by_u), 'Uzbek keys')
    print(out[:25])


if __name__ == '__main__':
    main()

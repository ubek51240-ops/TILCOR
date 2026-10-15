#!/usr/bin/env python3
"""Comparable ("teng") texts: original and translated language compared within each language, the design of
Bernardini (2007) that combines a parallel, a comparable and a reference corpus.

The corpus holds, in each language, one original and one translated text:
    English  original: Hemingway, The Old Man and the Sea      translated: Fort, Night and Day
    Uzbek    original: Cho‘lpon, Kecha va kunduz               translated: G‘ofurov, Chol va dengiz
For every text (the aligned part, tokens as in the word alignment):
  * tokens, standardised type/token ratio (mean TTR of consecutive 1 000-token chunks; the TTR of whole texts
    of different length is not comparable), lexical density (share of content words);
  * occurrences of the collocation candidates of the index (f >= 2 in the corpus) per 1 000 tokens;
  * English only, every occurrence of the dependency patterns (f >= 1) checked in the reference corpus
    (data/reference_en.json): share of occurrences whose word combination occurs at least 5 times there
    (paragraph 1.1.4, table 3) and share with reference logDice >= 7, and the share of combinations that occur
    only once in the text.
The original and the translated text of a language are compared with chi-square and G² (analysis.py).
Output: data/comparable_stats.json
"""
import collections, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

TEXTS = (('en', 'hemingway', 'original'), ('en', 'cholpon', 'translated'),
         ('uz', 'cholpon', 'original'), ('uz', 'hemingway', 'translated'))
CHUNK = 1000
LD_T = 7.0
MIN_REF = 5


def main():
    import equivalents as E
    import analysis as A
    from build_reference_en import en_pairs
    corpus = {p['id']: p for p in json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))}
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))
    idx = json.load(open(os.path.join(DATA, 'collocation_index.json'), encoding='utf-8'))
    ref = json.load(open(os.path.join(DATA, 'reference_en.json'), encoding='utf-8'))

    def ref_ld(key, comps):
        f = ref['pairs'].get(key, 0)
        if not f:
            return f, None
        f1, f2 = ref['lemma'].get(comps[0], 0), ref['lemma'].get(comps[1], 0)
        return f, 14 + math.log2(2 * f / (max(f1, f) + max(f2, f)))

    out = {'texts': [], 'tests': {}, 'params': {'chunk': CHUNK, 'logdice': LD_T, 'min_ref': MIN_REF, 'reference': ref['name'],
                                                'reference_tokens': ref['n']}}
    by = {}
    for lg, book, role in TEXTS:
        forms, content, n = [], 0, 0
        pair_occ = collections.Counter()
        pair_comps = {}
        for pid in sorted(aln):
            p = corpus.get(pid)
            if not p or p.get('book') != book:
                continue
            txt = p.get(lg) or ''
            toks = aln[pid][lg]
            for t in toks:
                forms.append(txt[t[0]:t[1]].lower())
                content += E._is_content(lg, t)
            n += len(toks)
            if lg == 'en':
                for pat, lemma, comps in en_pairs(toks):
                    k = pat + '|' + lemma
                    pair_occ[k] += 1
                    pair_comps[k] = comps
        chunks = [forms[i:i + CHUNK] for i in range(0, len(forms) - CHUNK + 1, CHUNK)]
        sttr = sum(len(set(c)) / CHUNK for c in chunks) / len(chunks) if chunks else None
        cand = sum((it.get('books') or {}).get(book, 0) for it in idx if it['lang'] == lg)
        row = {'lang': lg, 'book': book, 'role': role, 'tokens': n, 'sttr': sttr, 'density': content / n if n else None,
               'cand_occ': cand, 'cand_per_1000': 1000.0 * cand / n if n else None}
        if lg == 'en':
            occ = sum(pair_occ.values())
            att = sum(c for k, c in pair_occ.items() if ref_ld(k, pair_comps[k])[0] >= MIN_REF)
            hi = sum(c for k, c in pair_occ.items() if (ref_ld(k, pair_comps[k])[1] or -99) >= LD_T and ref_ld(k, pair_comps[k])[0] >= MIN_REF)
            once = sum(1 for c in pair_occ.values() if c == 1)
            row.update(pair_occ=occ, pair_types=len(pair_occ), pairs_per_1000=1000.0 * occ / n if n else None,
                       ref_attested=att, ref_typical=hi, once_types=once)
        by[(lg, role)] = row
        out['texts'].append(row)
    for lg in ('uz', 'en'):
        o, t = by[(lg, 'original')], by[(lg, 'translated')]
        tests = {'cand': A.contingency([[o['cand_occ'], o['tokens'] - o['cand_occ']], [t['cand_occ'], t['tokens'] - t['cand_occ']]]),
                 'density': A.contingency([[round(o['density'] * o['tokens']), o['tokens'] - round(o['density'] * o['tokens'])],
                                           [round(t['density'] * t['tokens']), t['tokens'] - round(t['density'] * t['tokens'])]])}
        if lg == 'en':
            tests['attested'] = A.contingency([[o['ref_attested'], o['pair_occ'] - o['ref_attested']], [t['ref_attested'], t['pair_occ'] - t['ref_attested']]])
            tests['typical'] = A.contingency([[o['ref_typical'], o['pair_occ'] - o['ref_typical']], [t['ref_typical'], t['pair_occ'] - t['ref_typical']]])
            tests['once'] = A.contingency([[o['once_types'], o['pair_types'] - o['once_types']], [t['once_types'], t['pair_types'] - t['once_types']]])
        out['tests'][lg] = tests
    json.dump(out, open(os.path.join(DATA, 'comparable_stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in out['texts']:
        print(r)
    for lg, tests in out['tests'].items():
        for k, v in tests.items():
            print(lg, k, v and {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()})


if __name__ == '__main__':
    main()

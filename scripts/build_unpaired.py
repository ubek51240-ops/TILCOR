#!/usr/bin/env python3
"""Sentences of the four texts that are not part of any sentence pair (hunalign 1-0 / 0-1 beads).

They are kept so that a search finds every occurrence of a word in the books. A sentence without a
counterpart is itself a translation fact (the translator left it out, merged it with a neighbour, or
added it), so it is shown with a note instead of a parallel sentence.

Sentences come from the same segmentation as the alignment (raw_extracted_v2.json, re-split with
realign_hunalign.resplit). A sentence counts as paired when its text is found, in order, in the
same side of the pairs of that book.

Output: data/unpaired_sentences.json  [{id, book, lang, text, page}]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))


def main():
    from realign_hunalign import resplit
    raw = json.load(open(os.path.join(DATA, 'raw_extracted_v2.json'), encoding='utf-8'))
    corpus = json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))
    out, report = [], {}
    for code, book in (('kvk', 'cholpon'), ('oms', 'hemingway')):
        for lang in ('uz', 'en'):
            sents = resplit(raw['%s_%s' % (code, lang)])[0]
            big = ' '.join((p.get(lang) or '').strip() for p in corpus if p['book'] == book)
            pos, n_un = 0, 0
            for k, snt in enumerate(sents):
                txt = (snt.get('text') or '').strip()
                if not txt:
                    continue
                i = big.find(txt, pos, pos + 4000 + len(txt))
                if i >= 0:
                    pos = i + len(txt)
                    continue
                if big.find(txt) >= 0:      # paired, only out of the expected order (a fixed point)
                    continue
                n_un += 1
                out.append({'id': 'solo-%s-%s-%04d' % (code, lang, n_un), 'book': book, 'lang': lang,
                            'text': txt, 'page': snt.get('page')})
            report['%s_%s' % (code, lang)] = {'sentences': len(sents), 'unpaired': n_un}
    json.dump(out, open(os.path.join(DATA, 'unpaired_sentences.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

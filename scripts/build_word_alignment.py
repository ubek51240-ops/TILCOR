#!/usr/bin/env python3
"""Word alignment inside every sentence pair of the corpus.

The translation equivalent of a word is always taken from the translator's own text: this script only
finds *which* words of the parallel sentence correspond to which words of the original.

Method
  * English sentences are parsed with spaCy (en_core_web_sm): token, lemma, part of speech, dependency.
  * Uzbek tokens are reduced to a conservative stem key (word_family.uz_align_stem).
  * eflomal (Östling & Tiedemann, 2016), a Bayesian IBM-type word aligner, is run in both directions on
    stems/lemmas; the two directions are combined with the grow-diag-final-and heuristic
    (fast_align's atools, Dyer et al., 2013).
  * From all links a lexical table is built: how often an Uzbek stem is linked to an English lemma. Search
    later uses only links that are supported by this table (the pair is linked at least twice in the
    corpus), so accidental links in a single sentence are not shown as equivalents.

Output: data/word_alignment.json  { pair_id: {"uz": [...], "en": [...], "links": [[i, j], ...]} }
        data/lexical_table.json   { "uz>en": {stem: {lemma: count}}, "en>uz": {...} }

Usage: python3 scripts/build_word_alignment.py --atools /path/to/atools
"""
import argparse, collections, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)

WORD = re.compile(r"[^\W\d_]+(?:[‘’'ʻʼ`][^\W\d_]+)*|\d+", re.UNICODE)


def uz_tokens(text, stem):
    out = []
    for m in WORD.finditer(text or ''):
        w = m.group(0)
        out.append([m.start(), m.end(), stem(w)])
    return out


def extend_final_apostrophe(text, tokens):
    """A word that ends in o‘ or g‘ (ulug‘, tog‘, yorug‘) loses its last sign to WORD; put it back into the
    highlighted span. Only the character offsets change, the stem used for the alignment stays as it was."""
    text = text or ''
    for t in tokens:
        e = t[1]
        if e < len(text) and text[e] in '‘ʻ\'’' and text[e - 1] in 'gGoO':
            t[1] = e + 1
    return tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--atools', required=True)
    args = ap.parse_args()

    import spacy
    import eflomal
    from word_family import uz_align_stem as stem

    corpus = json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))
    nlp = spacy.load('en_core_web_sm', disable=['ner'])

    pairs = []
    texts_en = [p.get('en') or '' for p in corpus]
    docs = nlp.pipe(texts_en, batch_size=256)
    for p, doc in zip(corpus, docs):
        en = []
        for t in doc:
            if t.is_punct or t.is_space:
                continue
            en.append([t.idx, t.idx + len(t.text), t.lemma_.lower(), t.pos_, t.dep_, t.head.i, t.i])
        # map spaCy token index -> position in our filtered list (for heads)
        pos_of = {row[6]: k for k, row in enumerate(en)}
        for row in en:
            row[5] = pos_of.get(row[5], -1)
            row.pop()          # drop spaCy index
        uz = uz_tokens(p.get('uz') or '', stem)
        pairs.append((p['id'], uz, en))

    src = [' '.join(t[2] for t in uz) or '_' for _, uz, _ in pairs]
    trg = [' '.join(t[2] for t in en) or '_' for _, _, en in pairs]
    with tempfile.TemporaryDirectory() as d:
        fwd, rev, sym = (os.path.join(d, x) for x in ('fwd', 'rev', 'sym'))
        eflomal.Aligner().align(src, trg, links_filename_fwd=fwd, links_filename_rev=rev, quiet=True)
        with open(sym, 'w') as out:
            subprocess.run([args.atools, '-i', fwd, '-j', rev, '-c', 'grow-diag-final-and'], stdout=out, check=True)
        links = [ln.split() for ln in open(sym)]

    result, table_ue, table_eu = {}, collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for (pid, uz, en), ln in zip(pairs, links):
        lk = []
        for a in ln:
            i, j = a.split('-')
            i, j = int(i), int(j)
            if i < len(uz) and j < len(en):
                lk.append([i, j])
                table_ue[uz[i][2]][en[j][2]] += 1
                table_eu[en[j][2]][uz[i][2]] += 1
        result[pid] = {'uz': uz, 'en': en, 'links': lk}

    uz_by_id = {p['id']: p.get('uz') for p in corpus}
    for pid, rec in result.items():
        extend_final_apostrophe(uz_by_id.get(pid), rec['uz'])
    json.dump(result, open(os.path.join(DATA, 'word_alignment.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'uz>en': {k: dict(v) for k, v in table_ue.items()}, 'en>uz': {k: dict(v) for k, v in table_eu.items()}},
              open(os.path.join(DATA, 'lexical_table.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n_links = sum(len(v['links']) for v in result.values())
    print(f'{len(result)} pairs, {n_links} links; lexical table: {len(table_ue)} Uzbek stems, {len(table_eu)} English lemmas')


if __name__ == '__main__':
    main()

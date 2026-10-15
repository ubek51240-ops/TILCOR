#!/usr/bin/env python3
"""English reference corpus counts for the collocation candidates (the statistical step of paragraph 1.1.4).

The dissertation plans the British National Corpus (BNC) as the English reference corpus. Until the BNC is
available to the platform, an open reference corpus is assembled from corpora that are freely distributed with
NLTK (Bird, Klein & Loper, 2009):
  * Brown Corpus (Francis & Kučera, 1979): 500 samples of American English printed in 1961, 15 genres;
  * MASC, the Manually Annotated Sub-Corpus of the Open American National Corpus (Ide et al., 2010):
    written and spoken American English of the late 20th and early 21st century;
  * Project Gutenberg selection of NLTK, prose fiction only (Austen, Bryant, Burgess, Carroll, Chesterton,
    Edgeworth, Melville); the Bible, poetry and drama of the selection are left out.
The texts are parsed with the same spaCy model as the corpus (en_core_web_sm) and the same dependency patterns
are counted as in scripts/build_collocation_index.py, so the reference counts are comparable with the corpus
counts. With --bnc DIR the BNC XML edition can be used instead (the <w hw=... pos=...> words of its files are
read as sentences and parsed the same way).

Usage:  python3 scripts/build_reference_en.py --nltk-dir PATH_TO_nltk_data [--bnc PATH] [--workers 2]
Output: data/reference_en.json
  {"name", "parts": [{name, tokens}], "n": tokens, "lemma": {lemma: f} (lemmas of the corpus only),
   "pairs": {"pattern|lemma": f} (pairs that occur in the corpus only), "built": date}
"""
import argparse, collections, datetime, glob, json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_collocation_index import EN_SKIP_LEMMA, EN_SKIP_LEMMA_SOFT

GUTENBERG_PROSE = ('austen-emma.txt', 'austen-persuasion.txt', 'austen-sense.txt', 'bryant-stories.txt',
                   'burgess-busterbrown.txt', 'carroll-alice.txt', 'chesterton-ball.txt', 'chesterton-brown.txt',
                   'chesterton-thursday.txt', 'edgeworth-parents.txt', 'melville-moby_dick.txt')


def en_pairs(toks):
    """(pattern, lemma) of every dependency pattern in one sentence; toks = [s, e, lemma, pos, dep, head].
    The same rules as the English part of scripts/build_collocation_index.py."""
    out = []
    for k, (s, e, lem, pos, dep, head) in enumerate(toks):
        if head < 0 or head >= len(toks) or lem in EN_SKIP_LEMMA and dep != 'dobj':
            continue
        h = toks[head]
        hlem, hpos = h[2], h[3]
        if hlem in EN_SKIP_LEMMA and not (dep == 'dobj' and hlem in EN_SKIP_LEMMA_SOFT):
            continue
        if dep == 'amod' and pos == 'ADJ' and hpos == 'NOUN':
            out.append(('adjective + noun', f'{lem} {hlem}', (lem, hlem) if s < h[0] else (hlem, lem)))
        elif dep == 'dobj' and pos == 'NOUN' and hpos == 'VERB' and lem not in EN_SKIP_LEMMA:
            out.append(('verb + noun', f'{hlem} {lem}', (hlem, lem) if h[0] < s else (lem, hlem)))
        elif dep == 'nsubj' and pos == 'NOUN' and hpos == 'VERB':
            out.append(('noun + verb', f'{lem} {hlem}', (lem, hlem) if s < h[0] else (hlem, lem)))
        elif dep == 'advmod' and pos == 'ADV' and hpos == 'VERB':
            out.append(('verb + adverb', f'{hlem} {lem}', (hlem, lem) if h[0] < s else (lem, hlem)))
        elif dep == 'advmod' and pos == 'ADV' and hpos == 'ADJ':
            out.append(('adverb + adjective', f'{lem} {hlem}', (lem, hlem) if s < h[0] else (hlem, lem)))
        elif dep == 'compound' and pos == 'NOUN' and hpos == 'NOUN':
            out.append(('noun + noun', f'{lem} {hlem}', (lem, hlem) if s < h[0] else (hlem, lem)))
        elif dep == 'pobj' and pos == 'NOUN' and hpos == 'ADP':
            g = toks[h[5]] if 0 <= h[5] < len(toks) else None
            if g and g[3] == 'VERB' and g[2] not in EN_SKIP_LEMMA:
                out.append(('verb + preposition + noun', f'{g[2]} {hlem} {lem}', (g[2], lem)))
    return out


def doc_tokens(doc):
    toks = []
    for t in doc:
        if t.is_punct or t.is_space:
            continue
        toks.append([t.idx, t.idx + len(t.text), t.lemma_.lower(), t.pos_, t.dep_, t.head.i, t.i])
    pos_of = {row[6]: k for k, row in enumerate(toks)}
    for row in toks:
        row[5] = pos_of.get(row[5], -1)
        row.pop()
    return toks


def detok(words):
    s = ' '.join(w for w in words)
    s = s.replace('``', '"').replace("''", '"')
    s = re.sub(r' ([.,;:!?%)\]])', r'\1', s)
    s = re.sub(r'([(\[$]) ', r'\1', s)
    s = re.sub(r" (n't|'s|'re|'ve|'ll|'d|'m)\b", r'\1', s)
    return s


def nltk_parts(nltk_dir):
    import nltk
    nltk.data.path.insert(0, nltk_dir)
    from nltk.corpus import brown, gutenberg, masc_tagged
    parts = []
    parts.append(('Brown Corpus (1961)', (detok(s) for s in brown.sents())))
    parts.append(('MASC (OANC)', (detok(s) for s in masc_tagged.sents())))

    def gut():
        for f in GUTENBERG_PROSE:
            raw = gutenberg.raw(f)
            for para in re.split(r'\n\s*\n', raw):
                para = re.sub(r'\s+', ' ', para).strip()
                if len(para) > 1:
                    # long paragraphs are cut at sentence ends so that one text stays below the parser limit
                    while len(para) > 4000:
                        cut = para.rfind('. ', 0, 4000)
                        cut = cut + 1 if cut > 0 else 4000
                        yield para[:cut]
                        para = para[cut:].strip()
                    yield para
    parts.append(('Project Gutenberg, prose fiction (NLTK selection)', gut()))
    return parts


def bnc_parts(bnc_dir):
    def gen():
        for path in sorted(glob.glob(os.path.join(bnc_dir, '**', '*.xml'), recursive=True)):
            txt = open(path, encoding='utf-8', errors='replace').read()
            for sent in re.findall(r'<s\b[^>]*>(.*?)</s>', txt, re.S):
                words = re.findall(r'<(?:w|c)\b[^>]*>([^<]*)</(?:w|c)>', sent)
                if words:
                    yield detok([w.strip() for w in words if w.strip()])
    return [('British National Corpus (XML edition)', gen())]


def corpus_vocabulary():
    """English lemmas and pattern pairs of the parallel corpus (all occurrences, not only frequent ones)."""
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))
    lemmas, pairs = set(), set()
    for rec in aln.values():
        toks = rec['en']
        for t in toks:
            lemmas.add(t[2])
        for pat, lemma, comps in en_pairs(toks):
            pairs.add(pat + '|' + lemma)
            lemmas.update(comps)
    return lemmas, pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nltk-dir')
    ap.add_argument('--bnc')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--out', default=os.path.join(DATA, 'reference_en.json'))
    a = ap.parse_args()
    import spacy
    nlp = spacy.load('en_core_web_sm', disable=['ner'])
    nlp.max_length = 2_000_000
    parts = bnc_parts(a.bnc) if a.bnc else nltk_parts(a.nltk_dir)
    lemma_f, pair_f = collections.Counter(), collections.Counter()
    info, n_all, t0 = [], 0, time.time()
    for name, texts in parts:
        n_part = 0
        for k, doc in enumerate(nlp.pipe(texts, batch_size=400, n_process=a.workers)):
            toks = doc_tokens(doc)
            n_part += len(toks)
            for t in toks:
                lemma_f[t[2]] += 1
            for pat, lemma, comps in en_pairs(toks):
                pair_f[pat + '|' + lemma] += 1
            if k % 20000 == 0:
                print(f'{name}: {k} texts, {n_part} tokens, {time.time() - t0:.0f}s', flush=True)
        info.append({'name': name, 'tokens': n_part})
        n_all += n_part
    lemmas, pairs = corpus_vocabulary()
    out = {'name': 'BNC' if a.bnc else 'Brown + MASC + Gutenberg (NLTK)', 'parts': info, 'n': n_all,
           'lemma': {k: v for k, v in lemma_f.items() if k in lemmas},
           'pairs': {k: v for k, v in pair_f.items() if k in pairs},
           'pair_types_total': len(pair_f), 'built': datetime.date.today().isoformat(),
           'spacy_model': 'en_core_web_sm ' + nlp.meta.get('version', '')}
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('tokens', n_all, 'parts', info, 'corpus pairs found', len(out['pairs']), 'of', len(pairs), f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()

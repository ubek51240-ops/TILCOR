#!/usr/bin/env python3
"""Re-align the two book pairs with hunalign (Varga et al., 2007), keeping confirmed pairs fixed.

Why: the earlier alignment (scripts/align_corpus_v3.py) used sentence length and page position only.
A manual spot check showed that about half of its automatic pairs did not correspond at sentence level.
hunalign combines the Gale–Church length model with lexical evidence: a seed dictionary (here: names and
numbers that are written the same in both books) and a dictionary it learns from a first pass (-realign).

Method
  1. Sentences come from data/raw_extracted_v2.json (the same segmentation as before, with printed pages).
  2. Fixed points: every pair confirmed by the researcher and the alignment pins of align_corpus_v3.py.
     The text between two fixed points is aligned as one block, so an error cannot run past a fixed point.
  3. Tokens are lower-cased and cut to their first 5 letters, a common way to let agglutinative forms
     (Zebining, Zebiga -> zebi) and English inflections share one key.
  4. hunalign runs with -utf -realign on each block; its ladder output is turned into pairs.
  5. Status of an automatic pair:
       "avtomatik — ikki usul mos"  : the earlier length/page alignment also put all these sentences into one pair;
       "avtomatik — faqat hunalign" : the earlier alignment paired them differently (hunalign's pair is kept).
       "avtomatik — tayanch nuqta"  : an alignment pin of the earlier run, used as a fixed point.
     Confirmed pairs are copied unchanged (same id, text, pages, confirmed equivalent).

Usage:  python3 scripts/realign_hunalign.py --hunalign /path/to/hunalign [--write]
Without --write it only prints a report. With --write it backs up data/full_corpus.json first.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

WORD = re.compile(r"[^\W\d_]+(?:[‘’'ʻʼ`][^\W\d_]+)*|\d+", re.UNICODE)
APOS = str.maketrans({'‘': "'", '’': "'", 'ʻ': "'", 'ʼ': "'", '`': "'"})
PREFIX = 5

STATUS_AGREE = 'avtomatik — ikki usul mos'
STATUS_LOW = 'avtomatik — faqat hunalign'
STATUS_CONFIRMED = 'tasdiqlangan'
STATUS_PIN = 'avtomatik — tayanch nuqta'   # alignment pin of the earlier run, not confirmed by the researcher


SPLIT_RE = re.compile(r'(?<=[.!?…])([”"»]?)\s+(?=[“"«—]?\s?[A-ZÀ-ÝА-ЯЁ])')
NO_SPLIT_BEFORE = re.compile(r'(?:\b[A-ZА-Я]|\bMr|\bMrs|\bDr|\bSt)[.]$')


def resplit(segs):
    """Split segments that still hold more than one sentence (for example '…me.” The girls…').
    A split is not made after an initial or a short title (A. Qodiriy, Mr. Smith). Page numbers are kept."""
    out, spans = [], []
    for sgm in segs:
        text = sgm['text'] or ''
        pieces, last = [], 0
        for m in SPLIT_RE.finditer(text):
            left = text[last:m.start()] + m.group(1)
            if NO_SPLIT_BEFORE.search(left.rstrip('”"»')):
                continue
            pieces.append(left.strip()); last = m.end()
        pieces.append(text[last:].strip())
        start = len(out)
        for pc in pieces:
            if pc:
                out.append(dict(sgm, text=pc))
        spans.append((start, max(start + 1, len(out))) if len(out) > start else (start, start))
    return out, spans


def keys(text):
    return [w.translate(APOS).lower()[:PREFIX] for w in WORD.findall(text or '')]


def norm(text):
    return re.sub(r'\s+', ' ', (text or '').translate(APOS)).strip().lower()


def seed_dictionary(src_segs, tgt_segs):
    """Identical capitalised words and numbers in both books (names, places, figures)."""
    def caps(segs):
        out = collections.Counter()
        for s in segs:
            for i, w in enumerate(WORD.findall(s['text'] or '')):
                if w[0].isdigit() or (w[0].isupper() and len(w) >= 3):
                    out[w.translate(APOS).lower()[:PREFIX]] += 1
        return out
    a, b = caps(src_segs), caps(tgt_segs)
    common = [k for k in a if k in b and a[k] >= 2 and b[k] >= 2]
    return sorted(common)


def run_hunalign(binary, dic_path, src_lines, tgt_lines):
    with tempfile.TemporaryDirectory() as d:
        sp, tp = os.path.join(d, 's.txt'), os.path.join(d, 't.txt')
        open(sp, 'w', encoding='utf-8').write('\n'.join(src_lines) + '\n')
        open(tp, 'w', encoding='utf-8').write('\n'.join(tgt_lines) + '\n')
        out = subprocess.run([binary, '-utf', '-realign', dic_path, sp, tp], capture_output=True, text=True, timeout=600)
        if out.returncode != 0:
            raise RuntimeError(out.stderr[-500:])
    rungs = []
    for line in out.stdout.splitlines():
        parts = line.split('\t')
        if len(parts) >= 3:
            rungs.append((int(parts[0]), int(parts[1]), float(parts[2])))
    return rungs


def beads_from_rungs(rungs):
    beads = []
    for (i0, j0, sc), (i1, j1, _) in zip(rungs, rungs[1:]):
        beads.append((i0, i1, j0, j1, sc))
    return beads


def _letters(t):
    return re.sub(r'[\W_]+', '', norm(t))


def locate(segs, text, start=0):
    """Index range of 1–4 consecutive segments that make up `text`.
    Compared on letters only, with a small tolerance (a stored pair may carry an added ellipsis or a
    corrected character); the closest span with similarity of at least 0.95 is taken."""
    import difflib
    target = _letters(text)
    if not target:
        return None
    best, best_r = None, 0.0
    for i in range(start, len(segs)):
        head = _letters(segs[i]['text'])[:25]
        if not head or not target.startswith(head[:min(len(head), 15)]):
            continue
        acc = ''
        for j in range(i, min(i + 4, len(segs))):
            acc += _letters(segs[j]['text'])
            r = difflib.SequenceMatcher(None, acc, target, autojunk=False).ratio()
            if r > best_r:
                best, best_r = (i, j + 1), r
            if len(acc) > len(target) * 1.2:
                break
    return best if best_r >= 0.95 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hunalign', required=True)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--lexicon', help='data/hunalign_lexicon.json: word pairs learnt from the word alignment (second pass)')
    ap.add_argument('--base', default='full_corpus.json',
                    help='earlier alignment used for the "two methods agree" check and for the confirmed pairs '
                         '(second pass: full_corpus.before_hunalign.json, the length/page alignment)')
    args = ap.parse_args()

    raw = json.load(open(os.path.join(DATA, 'raw_extracted_v2.json'), encoding='utf-8'))
    corpus = json.load(open(os.path.join(DATA, args.base), encoding='utf-8'))
    lexicon = json.load(open(args.lexicon, encoding='utf-8')) if args.lexicon else []
    method = ('hunalign -realign (Varga et al., 2007); dictionary: identical names and numbers'
              + (' + %d word pairs learnt from the word alignment of the first pass' % len(lexicon) if lexicon else ''))
    src = open(os.path.join(ROOT, 'scripts', 'align_corpus_v3.py'), encoding='utf-8').read()
    pins = {
        'kvk': eval(re.search(r"kvk_anchors = (\[.*?\n    \])", src, re.S).group(1).replace('len(kvk_uz)', str(len(raw['kvk_uz']))).replace('len(kvk_en)', str(len(raw['kvk_en'])))),
        'oms': eval(re.search(r"oms_anchors = (\[.*?\n    \])", src, re.S).group(1)),
    }
    import fix_corpus_metadata as fm

    split = {k: resplit(raw[k]) for k in ('kvk_uz', 'kvk_en', 'oms_en', 'oms_uz')}
    books = {'kvk': ('cholpon', split['kvk_uz'][0], split['kvk_en'][0], 'uz', 'en'),
             'oms': ('hemingway', split['oms_en'][0], split['oms_uz'][0], 'en', 'uz')}
    # raw index -> (start, end) in the re-split list, used to move the pins of the earlier run
    spans = {'kvk': (split['kvk_uz'][1], split['kvk_en'][1]), 'oms': (split['oms_en'][1], split['oms_uz'][1])}
    # earlier pairs, for the "two methods agree" check: a sentence -> the earlier pair that contains it
    old_side = {'kvk': ([], []), 'oms': ([], [])}
    for p in corpus:
        b = 'kvk' if p['book'] == 'cholpon' else 'oms'
        o_src = p['uz'] if b == 'kvk' else p['en']
        o_tgt = p['en'] if b == 'kvk' else p['uz']
        old_side[b][0].append((_letters(o_src), p['id']))
        old_side[b][1].append((_letters(o_tgt), p['id']))
    old_index = {}

    def owner(b, side, sentence):
        """Ids of the earlier pairs whose text contains this sentence (letters only)."""
        key = (b, side, sentence)
        if key not in old_index:
            needle = _letters(sentence)
            old_index[key] = {pid for txt, pid in old_side[b][side] if needle and needle in txt} if len(needle) >= 6 else None
        return old_index[key]
    confirmed = [p for p in corpus if p.get('status') == STATUS_CONFIRMED]

    new_corpus, report = [], {}
    for b, (book, S, T_, s_lang, t_lang) in books.items():
        # fixed points: pins (indices) + confirmed pairs (located by text)
        fixed = {}
        s_spans, t_spans = spans[b]
        for u, e, *_ in pins[b]:
            si_, ti_ = (u, e) if b == 'kvk' else (e, u)   # earlier run stored (uz index, en index)
            (a0, a1), (c0, c1) = s_spans[si_], t_spans[ti_]
            if a1 > a0 and c1 > c0:
                fixed[(a0, a1)] = (c0, c1, None)
        for p in confirmed:
            if (p['book'] == 'cholpon') != (b == 'kvk'):
                continue
            s_txt, t_txt = (p['uz'], p['en']) if b == 'kvk' else (p['en'], p['uz'])
            si, ti = locate(S, s_txt), locate(T_, t_txt)
            if not si or not ti:
                raise SystemExit(f'[!] confirmed pair {p["id"]} not located in the raw text; stopping so that it is not lost')
            fixed = {k: v for k, v in fixed.items() if not (k[0] < si[1] and si[0] < k[1])}
            fixed[si] = (ti[0], ti[1], p)
        points = sorted((s0, s1, t0, t1, p) for (s0, s1), (t0, t1, p) in fixed.items())
        # keep only monotone points
        mono, last_t = [], -1
        for pt in points:
            if pt[2] > last_t:
                mono.append(pt); last_t = pt[3] - 1
        dic_words = seed_dictionary(S, T_)
        with tempfile.NamedTemporaryFile('w', suffix='.dic', delete=False, encoding='utf-8') as df:
            for w in dic_words:
                df.write(f'{w} @ {w}\n')
            # hunalign wants "target @ source"; the source text is Uzbek for kvk and English for oms
            for ku, ke, _c in lexicon:
                df.write(f'{ke} @ {ku}\n' if s_lang == 'uz' else f'{ku} @ {ke}\n')
            dic_path = df.name
        counter = 0
        stats = collections.Counter()

        def emit(s0, s1, t0, t1, status, conf=None, score=None):
            nonlocal counter
            if conf is not None:
                new_corpus.append(conf); stats['confirmed'] += 1
                return
            if s1 <= s0 or t1 <= t0:
                stats['unpaired'] += 1
                return
            counter += 1
            s_txt = ' '.join(x['text'] for x in S[s0:s1]).strip()
            t_txt = ' '.join(x['text'] for x in T_[t0:t1]).strip()
            uz_txt, en_txt = (s_txt, t_txt) if s_lang == 'uz' else (t_txt, s_txt)
            uz_page = (S[s0] if s_lang == 'uz' else T_[t0])['page']
            en_page = (S[s0] if s_lang == 'en' else T_[t0])['page']
            owners = [owner(b, 0, x['text']) for x in S[s0:s1]] + [owner(b, 1, x['text']) for x in T_[t0:t1]]
            owners = [o for o in owners if o is not None]
            agree = bool(owners) and bool(set.intersection(*owners))
            st = status or (STATUS_AGREE if agree else STATUS_LOW)
            stats[st] += 1
            row = {
                'id': f'aln2-{b}-{counter:05d}', 'book': book,
                'uz': uz_txt, 'en': en_txt,
                'segmentId': f'{b}-h{counter}',
                'uz_page': uz_page, 'en_page': en_page,
                'page_source': (f'{uz_page}-bet (ziyouz.com)' if b == 'kvk' else f'{en_page}-bet'),
                'page_target': (f'{en_page}-bet' if b == 'kvk' else f'elektron nusxa, {uz_page}-bet'),
                'type': f'{s1 - s0}:{t1 - t0}', 'status': st,
                'cost': None if score is None else round(score, 3), 'agrees': agree,
                'method': method,
                'excluded': False,
                'license': 'Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha.',
            }
            row.update(fm.META[book])
            new_corpus.append(row)

        prev_s, prev_t = 0, 0
        for s0, s1, t0, t1, conf in mono + [(len(S), len(S), len(T_), len(T_), None)]:
            if s0 > prev_s or t0 > prev_t:
                blk_s = [' '.join(keys(x['text'])) or '.' for x in S[prev_s:s0]]
                blk_t = [' '.join(keys(x['text'])) or '.' for x in T_[prev_t:t0]]
                if blk_s and blk_t:
                    for a0, a1, c0, c1, sc in beads_from_rungs(run_hunalign(args.hunalign, dic_path, blk_s, blk_t)):
                        emit(prev_s + a0, prev_s + a1, prev_t + c0, prev_t + c1, None, score=sc)
                else:
                    stats['unpaired'] += max(len(blk_s), len(blk_t))
            if s1 > s0:
                emit(s0, s1, t0, t1, STATUS_PIN if conf is None else None, conf=conf)
            prev_s, prev_t = max(prev_s, s1), max(prev_t, t1)
        os.unlink(dic_path)
        report[b] = dict(stats, seed_dictionary=len(dic_words), fixed_points=len(mono))

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('pairs:', len(new_corpus), '(before:', len(corpus), ')')
    if args.write:
        path = os.path.join(DATA, 'full_corpus.json')
        backup = path.replace('.json', '.before_hunalign.json')
        if not os.path.exists(backup):
            shutil.copy2(path, backup)
        json.dump(new_corpus, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('written; backup:', os.path.basename(backup))
    else:
        out = os.path.join(DATA, 'full_corpus.hunalign_preview.json')
        json.dump(new_corpus, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('preview written to', os.path.basename(out))


if __name__ == '__main__':
    main()

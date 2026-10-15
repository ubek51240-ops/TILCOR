#!/usr/bin/env python3
"""Fixed random samples for the human evaluation of the platform (paragraph 1.1.4 of the dissertation).

Every task has a training set of 50 items (the annotation guide is tried out on it) and a main set of 200 items.
The samples are drawn with a fixed seed, so they can be rebuilt and cited; they are drawn again only when the
data they come from is rebuilt.

Tasks
  pairs     sentence alignment: automatically aligned pairs (the 15 pairs of paragraph 1.1 are left out),
            stratified by book and by position in the book (ten equal parts, a stand-in for chapters),
            proportional allocation;
  equiv     word-level translation equivalents as the search page shows them: a content word of a pair and the
            translator's word linked to it; half Uzbek, half English query words;
  colloc_uz Uzbek collocation candidates, colloc_en English collocation candidates: candidate types stratified
            by structural pattern (proportional), each shown in one randomly chosen occurrence;
  dict      translations of the corpus dictionary, half from each part.

Output: data/validation/samples.json  {"built", "seed", "tasks": {task: [item, ...]}}
item = {"id", "set": "train"|"main", "stratum", ...task fields}
"""
import collections, datetime, json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)

SEED = 20261015
N_TRAIN, N_MAIN = 50, 200


def proportional(strata, n, rng):
    """Draw n items from {stratum: [items]} with allocation proportional to stratum size (largest remainder)."""
    total = sum(len(v) for v in strata.values())
    quota = {k: n * len(v) / total for k, v in strata.items()}
    alloc = {k: int(q) for k, q in quota.items()}
    for k in sorted(quota, key=lambda k: -(quota[k] - alloc[k]))[:n - sum(alloc.values())]:
        alloc[k] += 1
    out = []
    for k, items in strata.items():
        out += [(k, x) for x in rng.sample(items, min(alloc[k], len(items)))]
    rng.shuffle(out)
    return out


def split(drawn):
    """The first N_TRAIN drawn items form the training set, the next N_MAIN the main set."""
    out = []
    for i, (stratum, x) in enumerate(drawn[:N_TRAIN + N_MAIN]):
        x = dict(x, set='train' if i < N_TRAIN else 'main', stratum=stratum)
        out.append(x)
    return out


def main():
    import equivalents as E
    ann = os.path.join(DATA, 'validation', 'annotations.json')
    if os.path.exists(ann) and '--force' not in sys.argv:
        try:
            n = sum(len(v) for v in json.load(open(ann, encoding='utf-8')).get('records', {}).values())
        except Exception:
            n = -1
        if n:
            raise SystemExit('[!] %s holds annotations; new samples would no longer match them. '
                             'Copy the file away first, or run with --force.' % ann)
    rng = random.Random(SEED)
    corpus = json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))
    by_id = {p['id']: p for p in corpus}
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))
    tasks = {}

    # ---- sentence alignment
    strata = collections.defaultdict(list)
    for book in ('cholpon', 'hemingway'):
        rows = [p for p in corpus if p.get('book') == book and p.get('status') != 'tasdiqlangan' and p.get('uz') and p.get('en')]
        for i, p in enumerate(rows):
            strata['%s-%d' % (book, i * 10 // len(rows) + 1)].append({'id': 'p:' + p['id'], 'pid': p['id']})
    tasks['pairs'] = split(proportional(strata, N_TRAIN + N_MAIN, rng))

    # ---- word equivalents
    items = {'uz': [], 'en': []}
    pids = sorted(aln)
    rng.shuffle(pids)
    seen = set()
    for pid in pids:
        if pid not in by_id:
            continue
        rec = aln[pid]
        for lg in ('uz', 'en'):
            if len(items[lg]) >= 140:
                continue
            toks = [t for t in rec[lg] if E._is_content(lg, t)]
            if not toks:
                continue
            t = rng.choice(toks)
            o_spans, key = E.equivalent_spans(pid, lg, [(t[0], t[1])])
            if not o_spans or (pid, lg) in seen:
                continue
            seen.add((pid, lg))
            items[lg].append({'id': 'e:%s:%s:%d' % (pid, lg, t[0]), 'pid': pid, 'lang': lg, 'q': [t[0], t[1]],
                              'o': [list(x) for x in o_spans], 'key': key})
        if all(len(v) >= 140 for v in items.values()):
            break
    tasks['equiv'] = split(proportional({'uz': items['uz'], 'en': items['en']}, N_TRAIN + N_MAIN, rng))

    # ---- collocation candidates
    idx = json.load(open(os.path.join(DATA, 'collocation_index.json'), encoding='utf-8'))
    for lg in ('uz', 'en'):
        strata = collections.defaultdict(list)
        for it in idx:
            if it['lang'] != lg or not it.get('occ'):
                continue
            strata[it['pattern']].append(it)
        drawn = proportional(strata, N_TRAIN + N_MAIN, rng)
        out = []
        for st, it in drawn:
            occ = rng.choice(it['occ'])
            out.append((st, {'id': 'c:%s:%s' % (it['id'], occ[0]), 'cid': it['id'], 'pid': occ[0], 'spans': occ[1],
                             'eqkey': occ[2] if len(occ) > 2 else None}))
        tasks['colloc_' + lg] = split(out)

    # ---- corpus dictionary
    d = json.load(open(os.path.join(DATA, 'corpus_dictionary.json'), encoding='utf-8'))
    strata = {}
    for lg in ('uz', 'en'):
        strata[lg] = [{'id': 'd:%s:%s:%s' % (lg, e['head'], t['text']), 'lang': lg, 'head': e['head'], 'text': t['text'],
                       'count': t['count'], 'pid': t['ex'][0], 'q': t['ex'][1], 'o': t['ex'][2]} for e in d[lg] for t in e['tr']]
    tasks['dict'] = split(proportional(strata, N_TRAIN + N_MAIN, rng))

    os.makedirs(os.path.join(DATA, 'validation'), exist_ok=True)
    out = {'built': datetime.date.today().isoformat(), 'seed': SEED, 'n_train': N_TRAIN, 'n_main': N_MAIN, 'tasks': tasks}
    json.dump(out, open(os.path.join(DATA, 'validation', 'samples.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for k, v in tasks.items():
        print(k, len(v), collections.Counter(x['stratum'].split('-')[0] for x in v).most_common(8))


if __name__ == '__main__':
    main()

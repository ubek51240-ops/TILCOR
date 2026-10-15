"""Human evaluation of the platform (paragraph 1.1.4 of the dissertation): fixed samples, the annotations of two
annotators, and the measures computed from them.

Samples: data/validation/samples.json (scripts/build_validation_samples.py).
Annotations: data/validation/annotations.json, written by the platform; it is never shipped in an update archive,
so an update does not overwrite the researcher's work.
Annotator A is the researcher (user "admin"), annotator B the second philologist (user "annotator").

Measures: share of correct items with a Wilson 95 % interval (Wilson, 1927; Newcombe, 1998); agreement of the
two annotators as observed agreement and Cohen's kappa (Cohen, 1960), read with the thresholds of Artstein and
Poesio (2008, p. 576) that paragraph 1.1.4 adopts; calibration of the reference-corpus threshold of logDice on
the researcher's labels (precision, recall, F1), because paragraph 1.1.4 does not fix the threshold in advance.
"""
import collections
import json
import math
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VDIR = os.path.join(BASE_DIR, 'data', 'validation')
SAMPLES = os.path.join(VDIR, 'samples.json')
ANNOTATIONS = os.path.join(VDIR, 'annotations.json')

ANNOTATORS = {'admin': 'A', 'annotator': 'B'}
TASKS = ('pairs', 'equiv', 'colloc_uz', 'colloc_en', 'dict')
VERDICTS = ('correct', 'partial', 'wrong')
# the decision procedure of paragraph 1.1.4 (questions 1-4 and 6; question 5 is the reference corpus)
COLLOC_FIELDS = {
    'q1': ('yes', 'no'),
    'q2': ('none', 'proverb', 'sentence', 'simile', 'formula', 'name', 'paired', 'auxiliary'),
    'q3': ('no', 'yes'),
    'q4': ('yes', 'no', 'disputed'),
    'q4b': ('no', 'yes'),
    'q6': ('collocation', 'single', 'descriptive', 'omitted'),
    'eq': ('correct', 'partial', 'wrong', 'none'),
}
CATEGORIES = ('collocation', 'borderline', 'stable_free', 'free', 'phraseological', 'excluded', 'not_unit')

_lock = threading.Lock()
_cache = {}


def samples():
    if 'samples' not in _cache:
        try:
            _cache['samples'] = json.load(open(SAMPLES, encoding='utf-8'))
        except Exception as e:
            print(f"[!] validation samples not loaded: {e}")
            _cache['samples'] = {'tasks': {}}
    return _cache['samples']


def items(task, which=None):
    rows = samples().get('tasks', {}).get(task, [])
    return [r for r in rows if which in (None, r['set'])]


def item(task, item_id):
    return next((r for r in items(task) if r['id'] == item_id), None)


def _load():
    try:
        return json.load(open(ANNOTATIONS, encoding='utf-8'))
    except FileNotFoundError:
        return {'version': 1, 'records': {}}
    except Exception as e:
        print(f"[!] annotations not loaded: {e}")
        return {'version': 1, 'records': {}}


def annotations():
    with _lock:
        return _load()


def save(task, item_id, user, labels, note=''):
    """Store one annotation; the later one of the same annotator replaces the earlier."""
    who = ANNOTATORS.get(user)
    if not who or task not in TASKS or not item(task, item_id):
        return False, 'bad request'
    clean = {}
    if task.startswith('colloc'):
        for k, allowed in COLLOC_FIELDS.items():
            v = labels.get(k)
            if v in allowed:
                clean[k] = v
        if 'q1' not in clean:
            return False, 'q1 required'
        clean['category'] = category(clean)
    else:
        v = labels.get('verdict')
        if v not in VERDICTS:
            return False, 'verdict required'
        clean['verdict'] = v
    with _lock:
        data = _load()
        data['records'].setdefault(task, {}).setdefault(item_id, {})[who] = {
            'labels': clean, 'note': (note or '')[:500], 'ts': time.strftime('%Y-%m-%d %H:%M:%S')}
        os.makedirs(VDIR, exist_ok=True)
        tmp = ANNOTATIONS + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=0)
        os.replace(tmp, ANNOTATIONS)
    return True, clean


def category(l):
    """The status of a collocation candidate occurrence by the decision procedure of paragraph 1.1.4."""
    if l.get('q1') == 'no':
        return 'not_unit'
    if l.get('q2', 'none') != 'none':
        return 'excluded'
    if l.get('q3') == 'yes':
        return 'phraseological'
    if l.get('q4') == 'no':
        return 'stable_free' if l.get('q4b') == 'yes' else 'free'
    if l.get('q4') == 'disputed':
        return 'borderline'
    if l.get('q4') == 'yes':
        return 'collocation'
    return None


def next_item(task, user, which=None):
    who = ANNOTATORS.get(user)
    done = annotations()['records'].get(task, {})
    for r in items(task):
        if which and r['set'] != which:
            continue
        if who not in done.get(r['id'], {}):
            return r
    return None


def progress():
    rec = annotations()['records']
    out = {}
    for t in TASKS:
        rows = items(t)
        d = rec.get(t, {})
        out[t] = {'train': sum(1 for r in rows if r['set'] == 'train'), 'main': sum(1 for r in rows if r['set'] == 'main')}
        for who in ('A', 'B'):
            out[t][who] = {s: sum(1 for r in rows if r['set'] == s and who in d.get(r['id'], {})) for s in ('train', 'main')}
    return out


# ------------------------------------------------------------------ measures
def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return round(p, 4), round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)


def kappa(pairs_):
    """Cohen's kappa for a list of (label A, label B)."""
    n = len(pairs_)
    if n < 2:
        return None
    po = sum(1 for a, b in pairs_ if a == b) / n
    ca = collections.Counter(a for a, _ in pairs_)
    cb = collections.Counter(b for _, b in pairs_)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return {'n': n, 'po': round(po, 4), 'kappa': round(k, 4)}


def label_of(task, ann):
    l = ann['labels']
    return l.get('category') if task.startswith('colloc') else l.get('verdict')


def results(which='main'):
    """Measures per task: distribution and share correct for each annotator, agreement on shared items."""
    rec = annotations()['records']
    out = {}
    for t in TASKS:
        ids = {r['id'] for r in items(t, which)}
        d = {i: v for i, v in rec.get(t, {}).items() if i in ids}
        res = {'n_items': len(ids)}
        for who in ('A', 'B'):
            labs = [label_of(t, v[who]) for v in d.values() if who in v]
            dist = collections.Counter(labs)
            r = {'n': len(labs), 'dist': dict(dist)}
            if t.startswith('colloc'):
                r['collocation'] = wilson(dist.get('collocation', 0), len(labs))
                eq = collections.Counter(v[who]['labels'].get('eq') for v in d.values() if who in v and v[who]['labels'].get('eq'))
                r['eq'] = dict(eq)
                n_eq = sum(c for k, c in eq.items() if k != 'none')
                r['eq_correct'] = wilson(eq.get('correct', 0), n_eq)
            else:
                r['correct'] = wilson(dist.get('correct', 0), len(labs))
                r['correct_or_partial'] = wilson(dist.get('correct', 0) + dist.get('partial', 0), len(labs))
            res[who] = r
        shared = [(label_of(t, v['A']), label_of(t, v['B'])) for v in d.values() if 'A' in v and 'B' in v]
        res['agreement'] = kappa(shared)
        if shared:
            res['confusion'] = collections.Counter('%s|%s' % p for p in shared)
        out[t] = res
    return out


def calibration(index_items, which='main', min_f=5):
    """Precision, recall and F1 of 'reference logDice >= t (and reference frequency >= min_f)' against the
    researcher's category 'collocation', for the English candidates of the sample."""
    rec = annotations()['records'].get('colloc_en', {})
    by_id = {it['id']: it for it in index_items}
    gold = []
    for r in items('colloc_en', which):
        a = rec.get(r['id'], {}).get('A')
        it = by_id.get(r['cid'])
        if not a or not it:
            continue
        ref = it.get('ref') or {}
        gold.append((a['labels'].get('category') == 'collocation', ref.get('f', 0), ref.get('log_dice')))
    if len(gold) < 20:
        return None
    rows = []
    pos = sum(1 for g, _, _ in gold if g)
    for t10 in range(0, 135, 5):
        t = t10 / 10
        pred = [(g, f >= min_f and ld is not None and ld >= t) for g, f, ld in gold]
        tp = sum(1 for g, p in pred if g and p)
        fp = sum(1 for g, p in pred if not g and p)
        prec = tp / (tp + fp) if tp + fp else None
        rec_ = tp / pos if pos else None
        f1 = 2 * prec * rec_ / (prec + rec_) if prec and rec_ else 0.0
        rows.append({'t': t, 'tp': tp, 'fp': fp, 'precision': prec, 'recall': rec_, 'f1': f1})
    best = max(rows, key=lambda r: (r['f1'], r['t']))
    return {'n': len(gold), 'positives': pos, 'min_f': min_f, 'rows': rows, 'best': best}


def export_rows():
    """All annotations as table rows (for CSV)."""
    rec = annotations()['records']
    head = ['task', 'set', 'item_id', 'annotator', 'label', 'q1', 'q2', 'q3', 'q4', 'q4b', 'q6', 'eq', 'note', 'time']
    rows = [head]
    for t in TASKS:
        sets = {r['id']: r['set'] for r in items(t)}
        for iid, v in sorted(rec.get(t, {}).items()):
            for who, a in sorted(v.items()):
                l = a['labels']
                rows.append([t, sets.get(iid, ''), iid, who, label_of(t, a) or '', l.get('q1', ''), l.get('q2', ''), l.get('q3', ''),
                             l.get('q4', ''), l.get('q4b', ''), l.get('q6', ''), l.get('eq', ''), a.get('note', ''), a.get('ts', '')])
    return rows

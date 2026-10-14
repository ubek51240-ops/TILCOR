"""Second stage of the search: translation equivalents, word-form equivalents and collocations from the
word alignment and the collocation index. Works on the result of search_engine.execute_unified_search.

Everything shown as an equivalent is a piece of the translator's text, located by the word alignment
(equivalents.py). Pairs that the researcher analysed in paragraph 1.1 are marked as such.
"""
import collections
import html
import json
import os
import re
import threading

import equivalents as E
from word_family import uz_align_stem, uz_norm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EQUIV_CLASS = 'equiv-mark'
QUERY_CLASS = 'query-match'

_lock = threading.Lock()
_index = {}


def _load_index():
    with _lock:
        if 'items' not in _index:
            try:
                items = json.load(open(os.path.join(DATA_DIR, 'collocation_index.json'), encoding='utf-8'))
            except Exception as e:
                print(f"[!] collocation index not loaded: {e}")
                items = []
            by_key = collections.defaultdict(list)
            for it in items:
                for k in component_keys(it['lang'], it['lemma']):
                    by_key[(it['lang'], k)].append(it)
            _index.update(items=items, by_key=by_key)
    return _index


def component_keys(lang, lemma):
    keys = set()
    for w in lemma.split():
        if lang == 'en':
            keys.add(w.lower())
        else:
            w = uz_norm(w.lower())
            if w.endswith('moq') and len(w) > 5:
                w = w[:-3]
            keys.add(uz_align_stem(w))
            keys.add(w)
    return keys


def highlight(text, spans, cls):
    """Wrap the given character spans; everything else is escaped."""
    spans = sorted((max(0, a), min(len(text), b)) for a, b in spans if b > a)
    out, pos = [], 0
    for a, b in spans:
        if a < pos:
            continue
        out.append(html.escape(text[pos:a]))
        out.append(f'<mark class="{cls}">{html.escape(text[a:b])}</mark>')
        pos = b
    out.append(html.escape(text[pos:]))
    return ''.join(out)


def _display(texts):
    """Most frequent surface form; lower-cased unless every occurrence is capitalised (a name)."""
    form, _ = texts.most_common(1)[0]
    if all(t[:1].isupper() for t in texts) and len(texts) > 1:
        return form
    return form[:1].lower() + form[1:] if form[:1].isupper() and not form.isupper() else form


def enrich(res, corpus_by_id, page=1, per_page=20):
    """Add 'equivalents', per-form 'translations', 'corpus_collocations' and paginate the sentences."""
    q_lang = res.get('selected_lang') or 'uz'
    sentences = res.get('corpus_sentences') or []
    eq_groups = {}
    form_eq = collections.defaultdict(collections.Counter)
    form_eq_text = collections.defaultdict(dict)

    for s in sentences:
        pid = s.get('id')
        spans = [tuple(x) for x in (s.get('match_spans') or [])]
        other = s.get('other_raw') or ''
        researcher = bool(s.get('equiv_confirmed'))
        o_spans, key = E.equivalent_spans(pid, q_lang, spans)
        if researcher:
            # keep the researcher's own marking of the equivalent; group it with the alignment key if any
            text_html = s.get('other_highlighted') or html.escape(other)
            m = re.search(r'<span class="equiv-confirmed[^>]*>(.*?)</span>', text_html)
            eq_text = html.unescape(re.sub('<[^>]+>', '', m.group(1))) if m else None
            s['other_highlighted'] = re.sub(r'<span class="equiv-confirmed[^>]*>(.*?)</span>',
                                            rf'<mark class="{EQUIV_CLASS} researcher">\1</mark>', text_html)
            if eq_text:
                key = key or eq_text.lower()
        else:
            eq_text = other[o_spans[0][0]:o_spans[0][1]] if o_spans else None
            s['other_highlighted'] = highlight(other, o_spans, EQUIV_CLASS)
        s['equivalent_text'] = eq_text
        s['is_open'] = True
        if eq_text and key:
            g = eq_groups.setdefault(key, {'key': key, 'count': 0, 'texts': collections.Counter(), 'books': collections.Counter(),
                                           'example': None, 'researcher': False})
            g['count'] += 1
            g['texts'][eq_text] += 1
            g['books'][s.get('book')] += 1
            if researcher and not g['researcher']:
                g['researcher'] = True
                g['example'] = s
            elif g['example'] is None:
                g['example'] = s
        # per word form (for the "word forms" table)
        q_text = s.get('query_raw') or ''
        for a, b in spans:
            form = q_text[a:b]
            nf = uz_norm(form.lower()) if q_lang == 'uz' else form.lower()
            sp1, k1 = E.equivalent_spans(pid, q_lang, [(a, b)])
            if sp1 and k1:
                form_eq[nf][k1] += 1
                form_eq_text[nf].setdefault(k1, collections.Counter())[other[sp1[0][0]:sp1[0][1]]] += 1

    total_with = sum(g['count'] for g in eq_groups.values())
    equivalents = []
    for g in sorted(eq_groups.values(), key=lambda g: (-g['count'], g['key'])):
        equivalents.append({
            'key': g['key'], 'text': _display(g['texts']), 'count': g['count'],
            'share': round(100 * g['count'] / total_with) if total_with else 0,
            'forms': [t for t, _ in g['texts'].most_common(5)],
            'books': dict(g['books']), 'researcher': g['researcher'], 'example': g['example'],
        })
    res['equivalents'] = equivalents
    res['equivalent_coverage'] = {'with': total_with, 'total': len(sentences)}

    for w in res.get('words') or []:
        nf = uz_norm(w['word'].lower()) if q_lang == 'uz' else w['word'].lower()
        c = form_eq.get(nf)
        w['translations'] = [{'text': _display(form_eq_text[nf][k]), 'count': n} for k, n in c.most_common(4)] if c else []

    res['corpus_collocations'] = find_collocations(res, q_lang, corpus_by_id)

    total = len(sentences)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    res['all_sentence_count'] = total
    res['corpus_sentences'] = sentences[(page - 1) * per_page: page * per_page]
    res['pagination'] = {'page': page, 'limit': per_page, 'total_sentences': total, 'total_pages': pages}
    return res


def find_collocations(res, q_lang, corpus_by_id, limit=60):
    idx = _load_index()
    query = (res.get('query') or '').strip()
    keys = set()
    if res.get('is_collocation_query'):
        wanted = component_keys(q_lang, query if q_lang == 'en' else ' '.join(query.split()))
        found = []
        for it in idx['items']:
            if it['lang'] != q_lang:
                continue
            ck = component_keys(q_lang, it['lemma'])
            # every content word of the query must be in the collocation
            content = [w for w in query.lower().split() if w not in ('the', 'a', 'an', 'to', 'of')]
            if all(component_keys(q_lang, w) & ck for w in content):
                found.append(it)
        items = found
    else:
        for w in res.get('words') or []:
            form = w['word']
            if q_lang == 'en':
                keys.add(form.lower())
                try:
                    from search_engine import resolve_english
                    lem, _ = resolve_english(form.lower())
                    if lem:
                        keys.add(lem)
                except Exception:
                    pass
            else:
                keys.add(uz_align_stem(form))
        seen, items = set(), []
        for k in keys:
            for it in idx['by_key'].get((q_lang, k), []):
                if it['id'] not in seen:
                    seen.add(it['id'])
                    items.append(it)
    items.sort(key=lambda it: (-it['freq'], -(it.get('log_dice') or 0), it['lemma']))
    out = []
    for it in items[:limit]:
        ex = None
        for o in it.get('occ') or []:
            pid, spans = o[0], o[1]
            p = corpus_by_id.get(pid)
            if not p:
                continue
            q_text = p.get(q_lang) or ''
            o_lang = 'en' if q_lang == 'uz' else 'uz'
            o_text = p.get(o_lang) or ''
            o_spans, _ = E.equivalent_spans(pid, q_lang, [tuple(x) for x in spans])
            ex = {'pair_id': pid, 'book': p.get('book'),
                  'query_html': highlight(q_text, [tuple(x) for x in spans], QUERY_CLASS),
                  'other_html': highlight(o_text, o_spans, EQUIV_CLASS),
                  'query_page': p.get('uz_page') if q_lang == 'uz' else p.get('en_page'),
                  'other_page': p.get('en_page') if q_lang == 'uz' else p.get('uz_page'),
                  'query_lang': q_lang}
            break
        out.append(dict(it, example=ex, occ=None))
    return out


def occurrence_pairs(item, corpus_by_id):
    """Every stored occurrence of a collocation as a sentence pair with both sides highlighted."""
    q_lang = item['lang']
    o_lang = 'en' if q_lang == 'uz' else 'uz'
    out = []
    for o in item.get('occ') or []:
        pid, spans = o[0], o[1]
        p = corpus_by_id.get(pid)
        if not p:
            continue
        sp = [tuple(x) for x in spans]
        o_spans, _ = E.equivalent_spans(pid, q_lang, sp)
        out.append({'pair_id': pid, 'book': p.get('book'),
                    'query_html': highlight(p.get(q_lang) or '', sp, QUERY_CLASS),
                    'other_html': highlight(p.get(o_lang) or '', o_spans, EQUIV_CLASS),
                    'query_page': p.get('uz_page') if q_lang == 'uz' else p.get('en_page'),
                    'other_page': p.get('en_page') if q_lang == 'uz' else p.get('uz_page')})
    return out

"""The corpus dictionary (Uzbek–English and English–Uzbek) of the platform.

Data: data/corpus_dictionary.json, built by scripts/build_corpus_dictionary.py from the word alignment of the
two books. Every translation is a word a translator used in the book, with the number of links in the corpus
and one example sentence pair. This module loads the data, finds entries and prepares what the page shows.
"""
import collections
import json
import os
import threading

from word_family import uz_norm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE_DIR, 'data', 'corpus_dictionary.json')

UZ_LETTERS = ('A', 'B', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
              'V', 'X', 'Y', 'Z', 'O‘', 'G‘', 'Sh', 'Ch')
EN_LETTERS = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
_UZ_RANK = {l.lower(): i for i, l in enumerate(UZ_LETTERS)}

_lock = threading.Lock()
_data = {}


def norm(lang, w):
    w = (w or '').strip()
    if lang == 'uz':
        return uz_norm(w.lower()).strip()
    return w.lower().replace('’', "'").replace('‘', "'")


def _uz_units(n):
    """Letters of the Uzbek alphabet in a normalised word (oʻ, gʻ, sh, ch count as one letter)."""
    out, i = [], 0
    while i < len(n):
        two = n[i:i + 2]
        if two in ('oʻ', 'gʻ'):
            out.append(two[0] + '‘')
            i += 2
        elif two in ('sh', 'ch'):
            out.append(two)
            i += 2
        else:
            out.append(n[i])
            i += 1
    return out


def letter_of(lang, head):
    n = norm(lang, head)
    if not n:
        return ''
    if lang == 'uz':
        u = _uz_units(n)[0]
        return u[0].upper() + u[1:]
    return n[0].upper()


def sort_key(lang, head):
    n = norm(lang, head)
    if lang == 'uz':
        return [_UZ_RANK.get(u, 90 + ord(u[0]) % 50) for u in _uz_units(n)]
    return [ord(c) for c in n]


def _load():
    with _lock:
        if 'uz' in _data:
            return _data
        try:
            raw = json.load(open(PATH, encoding='utf-8'))
        except Exception as e:
            print(f"[!] corpus dictionary not loaded: {e}")
            raw = {'uz': [], 'en': []}
        for lg in ('uz', 'en'):
            entries = sorted(raw.get(lg) or [], key=lambda e: sort_key(lg, e['head']))
            by_head, by_form, by_letter = {}, collections.defaultdict(list), collections.defaultdict(list)
            for i, e in enumerate(entries):
                by_head.setdefault(norm(lg, e['head']), i)
                for f, c in (e.get('forms') or {}).items():
                    by_form[norm(lg, f)].append((c, i))
                by_letter[letter_of(lg, e['head'])].append(i)
            for k in by_form:
                by_form[k].sort(reverse=True)
            _data[lg] = {'entries': entries, 'by_head': by_head, 'by_form': by_form, 'by_letter': by_letter}
        return _data


def stats():
    d = _load()
    return {'uz': len(d['uz']['entries']), 'en': len(d['en']['entries']),
            'pairs': sum(len(e['tr']) for lg in ('uz', 'en') for e in d[lg]['entries'])}


def find(lang, q):
    """Indices of the entries for a query: the headword itself, else the entries that have it as a word form,
    else (Uzbek) the verb with -moq."""
    d = _load()[lang]
    n = norm(lang, q)
    if not n:
        return []
    if n in d['by_head']:
        return [d['by_head'][n]]
    if n in d['by_form']:
        seen = []
        for _, i in d['by_form'][n]:
            if i not in seen:
                seen.append(i)
        return seen[:3]
    if lang == 'uz' and not n.endswith('moq') and (n + 'moq') in d['by_head']:
        return [d['by_head'][n + 'moq']]
    return []


def suggestions(lang, q, limit=12):
    """Headwords that start with the query, then headwords that contain it (most frequent first)."""
    d = _load()[lang]
    n = norm(lang, q)
    if len(n) < 2:
        return []
    starts = [e for e in d['entries'] if norm(lang, e['head']).startswith(n)]
    if len(starts) < limit and len(n) >= 3:
        starts += [e for e in d['entries'] if n in norm(lang, e['head'])[1:] and e not in starts]
    if not starts and len(n) >= 4:
        starts = [e for e in d['entries'] if norm(lang, e['head']).startswith(n[:3])]
    return sorted(starts, key=lambda e: -e['freq'])[:limit]


def top(lang, limit=36):
    return sorted(_load()[lang]['entries'], key=lambda e: -e['freq'])[:limit]


def letter_entries(lang, letter):
    d = _load()[lang]
    return [d['entries'][i] for i in d['by_letter'].get(letter, [])]


def letters_present(lang):
    return set(_load()[lang]['by_letter'])


def has_head(lang, word):
    return norm(lang, word) in _load()[lang]['by_head']


UZ_DERIV = ('li', 'siz', 'chi', 'lik', 'cha', 'gi', 'kʻi', 'gʻi', 'ish', 'sh', 'in', 'il', 'gich', 'kor', 'dor', 'iy', 'viy',
            'la', 'lan', 'lash', 'loq', 'chan', 'ona', 'mon', 'ma', 'q', 'k', 'gin', 'ga', 'ni', 'ir', 'ar', 'kin', 'qin', 'gʻin',
            't', 'tir', 'dir', 'iz', 'ʼ', 'ki', 'qi', 'ov', 'uv', 'gan', 'mas', 'msira', 'imsira', 'i', 'ib', 'a', '-')
EN_DERIV = ('s', 'es', 'ed', 'd', 'ing', 'er', 'ers', 'r', 'ly', 'ily', 'ness', 'ful', 'less', 'ish', 'y', 'ment', 'tion', 'ion',
            'ter', 'en', 'al', 'ous', 'ity', 'ive', 'able', 'ible', 'ance', 'ence', 'ist', 'ism', '-')


def related(lang, entry, limit=10):
    """Other headwords of the same stem with a derivational ending: kulmoq -> kulgi, kulish, kulimsiramoq;
    laugh -> laughter. A word that merely begins with the same letters (heart -> hearth) is not taken."""
    head = norm(lang, entry['head'])
    stem = head[:-3] if lang == 'uz' and head.endswith('moq') and len(head) > 5 else head
    if lang == 'en':
        for sfx in ('ing', 'ed', 'es', 'e', 'y', 's'):
            if stem.endswith(sfx) and len(stem) - len(sfx) >= 4:
                stem = stem[:-len(sfx)]
                break
    if len(stem) < 3:
        return []
    deriv = UZ_DERIV if lang == 'uz' else EN_DERIV
    out = []
    for e in _load()[lang]['entries']:
        n = norm(lang, e['head'])
        if e is entry or not n.startswith(stem) or n == head:
            continue
        rest = n[len(stem):]
        if lang == 'uz' and rest.endswith('moq'):
            rest = rest[:-3]
        if not rest or len(rest) > 9 or not rest.startswith(deriv):
            continue
        out.append(e)
    return sorted(out, key=lambda e: -e['freq'])[:limit]


def collocations(lang, entry, limit=10):
    """Corpus collocations that have this word as one of their components."""
    import search_plus
    idx = search_plus._load_index()
    seen, out = set(), []
    for k in search_plus.component_keys(lang, entry['head']):
        for it in idx['by_key'].get((lang, k), []):
            if it['id'] not in seen:
                seen.add(it['id'])
                out.append(it)
    return sorted(out, key=lambda it: -it.get('freq', 0))[:limit]


def example_pair(lang, tr, corpus_by_id):
    """The example of one translation as a pair with the headword and the translation highlighted."""
    import search_plus
    pid, q_span, o_span = tr['ex']
    p = corpus_by_id.get(pid)
    if not p:
        return None
    o_lang = 'en' if lang == 'uz' else 'uz'
    return {'book': p.get('book'), 'researcher': p.get('status') == 'tasdiqlangan',
            'q_html': search_plus.highlight(p.get(lang) or '', [tuple(q_span)], search_plus.QUERY_CLASS),
            'o_html': search_plus.highlight(p.get(o_lang) or '', [tuple(o_span)], search_plus.EQUIV_CLASS),
            'q_page': p.get('uz_page') if lang == 'uz' else p.get('en_page'),
            'o_page': p.get('en_page') if lang == 'uz' else p.get('uz_page')}


def page_model(lang_dir, q, letter, corpus_by_id, page_no=1, per_page=90, explicit=False):
    """Everything the dictionary page shows. A word that is not in the chosen part but is in the other one
    is shown from the other part (the reader typed an English word with the Uzbek part open)."""
    lang_dir = lang_dir if lang_dir in ('uz', 'en') else 'uz'
    q = (q or '').strip()[:80]
    switched = False
    if q and not find(lang_dir, q) and find('en' if lang_dir == 'uz' else 'uz', q):
        lang_dir, switched = ('en' if lang_dir == 'uz' else 'uz'), True
    other = 'en' if lang_dir == 'uz' else 'uz'
    m = {'dir': lang_dir, 'q': q, 'letter': '', 'mode': 'home', 'stats': stats(), 'switched': switched, 'explicit': explicit,
         'letters': UZ_LETTERS if lang_dir == 'uz' else EN_LETTERS, 'present': letters_present(lang_dir)}
    if q:
        idx = find(lang_dir, q)
        if idx:
            entries = [_load()[lang_dir]['entries'][i] for i in idx]
            m['mode'] = 'entry'
            m['entries'] = []
            for e in entries:
                trs = []
                for t in e['tr']:
                    trs.append(dict(t, pair=example_pair(lang_dir, t, corpus_by_id), reverse=has_head(other, t['text'])))
                m['entries'].append({'e': e, 'tr': trs, 'colls': collocations(lang_dir, e), 'related': related(lang_dir, e)})
            m['other_hit'] = bool(find(other, q))
        else:
            m['mode'] = 'notfound'
            m['suggest'] = suggestions(lang_dir, q)
            m['other_hit'] = bool(find(other, q))
        return m
    if letter and letter in m['letters']:
        items = letter_entries(lang_dir, letter)
        total_pages = max(1, (len(items) + per_page - 1) // per_page)
        page_no = max(1, min(int(page_no or 1), total_pages))
        m.update(mode='letter', letter=letter, items=items[(page_no - 1) * per_page: page_no * per_page], n_items=len(items),
                 page=page_no, total_pages=total_pages)
        return m
    m['top'] = [e for e in top(lang_dir, 120) if e.get('pos')][:40]
    return m


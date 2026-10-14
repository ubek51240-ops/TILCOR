"""Translation equivalents from the word alignment of the corpus.

Given a sentence pair and the character spans of the searched word(s) on one side, return the words of
the other side that the translator used for them. The text returned is always a piece of the book's
translation, cut out at word boundaries; nothing is generated.

A link is used only if the same stem/lemma pair is linked at least MIN_LINK times in the whole corpus
(data/lexical_table.json), so a link that occurs once by accident is not shown.
"""
import json
import os
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MIN_LINK = 3          # the stem/lemma pair must be linked at least this often in the corpus
MIN_SHARE = 0.03      # ... and make up at least this share of all links of the searched word
MAX_GAP = 2           # words allowed between two linked words of one equivalent

PARTICLES = {'asleep', 'awake', 'away', 'up', 'down', 'out', 'off', 'back', 'over', 'on', 'in', 'apart', 'aside'}
EN_FUNCTION_POS = {'DET', 'PRON', 'AUX', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'PUNCT', 'SPACE', 'NUM', 'SYM', 'X', 'INTJ'}
UZ_FUNCTION = {'va', 'ham', 'bilan', 'uchun', 'esa', 'deb', 'bu', 'shu', 'u', 'ul', 'o‘sha', 'oʻsha', 'bir', 'yana',
               'endi', 'lekin', 'ammo', 'biroq', 'chunki', 'agar', 'kabi', 'qadar', 'uning', 'unga', 'uni', 'ular',
               'men', 'sen', 'biz', 'siz', 'mening', 'sening', 'ning', 'da', 'ga', 'ni', 'emas', 'edi', 'ekan', 'har',
               'hech', 'nima', 'kim', 'qanday', 'bo‘lsa', 'boʻlsa', 'yo', 'yoki', 'na', 'ko‘p', 'koʻp', 'juda'}

_lock = threading.Lock()
_cache = {}


def _load():
    with _lock:
        if 'aln' not in _cache:
            try:
                _cache['aln'] = json.load(open(os.path.join(DATA_DIR, 'word_alignment.json'), encoding='utf-8'))
                _cache['lex'] = json.load(open(os.path.join(DATA_DIR, 'lexical_table.json'), encoding='utf-8'))
            except Exception as e:  # missing files: the platform still works, without equivalents
                print(f"[!] word alignment not loaded: {e}")
                _cache['aln'], _cache['lex'] = {}, {'uz>en': {}, 'en>uz': {}}
    return _cache['aln'], _cache['lex']


def available() -> bool:
    aln, _ = _load()
    return bool(aln)


_totals = {}


def _row_total(table, key):
    tk = (id(table), key)
    if tk not in _totals:
        _totals[tk] = sum(table.get(key, {}).values())
    return _totals[tk]


def _tokens_in_spans(tokens, spans):
    out = []
    for k, tok in enumerate(tokens):
        s, e = tok[0], tok[1]
        if any(s < b and a < e for a, b in spans):
            out.append(k)
    return out


def _is_content(lang, tok):
    if lang == 'en':
        return tok[3] not in EN_FUNCTION_POS
    return tok[2] not in UZ_FUNCTION and len(tok[2]) > 1


def equivalent_spans(pair_id: str, query_lang: str, spans):
    """Return (spans_in_other_text, key) for the searched words; ([], None) when no reliable link exists.
    `spans` are character spans in the query-side text (uz text for an Uzbek query, en text for English)."""
    aln, lex = _load()
    rec = aln.get(pair_id)
    if not rec or not spans:
        return [], None
    other_lang = 'en' if query_lang == 'uz' else 'uz'
    q_toks, o_toks = rec[query_lang], rec[other_lang]
    q_idx = _tokens_in_spans(q_toks, spans)
    if not q_idx:
        return [], None
    table = lex['uz>en'] if query_lang == 'uz' else lex['en>uz']
    linked = set()
    for i, j in rec['links']:
        qi, oj = (i, j) if query_lang == 'uz' else (j, i)
        if qi in q_idx:
            q_key, o_key = q_toks[qi][2], o_toks[oj][2]
            row = table.get(q_key, {})
            n_link = row.get(o_key, 0)
            if n_link >= MIN_LINK and n_link >= MIN_SHARE * _row_total(table, q_key) and _is_content(other_lang, o_toks[oj]):
                linked.add(oj)
    if not linked:
        return [], None
    # group linked words that are close to each other into one equivalent; keep the largest group
    order = sorted(linked)
    groups, cur = [], [order[0]]
    for k in order[1:]:
        if k - cur[-1] <= MAX_GAP + 1:
            cur.append(k)
        else:
            groups.append(cur)
            cur = [k]
    groups.append(cur)
    best = max(groups, key=len)
    if other_lang == 'en':
        # complete a phrasal verb or a verb with its complement: fell asleep, woke up, turned pale
        last = best[-1]
        while last + 1 < len(o_toks):
            nxt = o_toks[last + 1]
            if nxt[5] in best and (nxt[4] in ('prt', 'acomp', 'oprd') or
                                   (nxt[4] == 'advmod' and nxt[2] in PARTICLES)):
                last += 1
                best = best + [last]
            else:
                break
    start, end = o_toks[best[0]][0], o_toks[best[-1]][1]
    key = ' '.join(o_toks[k][2] for k in range(best[0], best[-1] + 1) if _is_content(other_lang, o_toks[k]))
    return [(start, end)], key or None


def lexical_candidates(query_lang: str, key: str, limit: int = 8):
    """Most frequent translation keys of a stem/lemma in the whole corpus (for diagnostics and admin)."""
    _, lex = _load()
    table = lex['uz>en'] if query_lang == 'uz' else lex['en>uz']
    row = table.get(key, {})
    return sorted(((k, v) for k, v in row.items() if v >= MIN_LINK), key=lambda kv: -kv[1])[:limit]

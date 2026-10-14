"""
search_engine.py - Complete Unified Search Engine for TILCOR (Step 07)
Strictly compliant with:
- TILCOR_07-1.md (Parts 1-7)
- PROJECT_CONTEXT.md (Sections A-G, S, S2, S3, S4, S5, S6)
- The EQUIVALENT PRINCIPLE: never translate collocations with AI or MT.
  Translations must be verbatim spans from aligned target sentences.
- 5 Equivalent Hierarchy Sources:
  1. Kitobdagi tarjima — tasdiqlangan (solid colour 2)
  2. Kitobdagi tarjima — AI-taklif (tekshirilmagan) (dashed colour 2)
  3. Lug‘atdagi tarjima (plain text, grey label with source and page)
  4. Ma’lumotnomadagi muqobil (plain text, class label)
  5. Namuna gap (italic, labelled)
- Single-word and multi-word collocation queries (lemma matching, <= 2 intervening tokens)
- Ranking of example cards (confirmed with equivalent > confirmed > automatic)
- Provenance audit compliance
"""

import re
import html
import json
from functools import lru_cache
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any

from word_family import (
    uz_norm,
    match_uzbek_word_family,
    match_english_word_family,
    detect_query_language,
    clean_word,
    get_uzbek_stem_variants,
    strip_uzbek_inflections,
    ALL_UZBEK_SUFFIXES,
    lemmatizer,
    stemmer,
    APOSTROPHE_CHARS,
    get_wordnet_family,
    ENGLISH_IRREGULAR_PAIRS
)

TOKEN_UZ_NORM_RE = re.compile(r"[a-z\u02bb\u02bc]+(?:-[a-z\u02bb\u02bc]+)*")
TOKEN_EN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+|-?[a-zA-Z]+)*")
SINGLE_WORD_CLEAN_RE = re.compile(rf"^[a-zA-Z\u0400-\u04FF{APOSTROPHE_CHARS}]+(?:-[a-zA-Z\u0400-\u04FF{APOSTROPHE_CHARS}]+)?$")

# The OCR text of the two printed dictionaries is too damaged to quote as a source
# (e.g. "answer -> [a:nsa(r)J n. javob; v. jav-"). Dictionary translations stay hidden
# from the public until a clean dictionary file is supplied (set to True then).
DICTIONARY_PUBLIC = False
MIN_CANDIDATE_FREQ = 2   # automatic collocation candidates: at least 2 occurrences in the study corpus
DICTIONARY_NOTE = "Lug‘at ma’lumotlari OCR sifati yetarli bo‘lmagani uchun hozircha ko‘rsatilmaydi"
POS_UNKNOWN = "so‘z turkumi aniqlanmagan"


TEMPLATE_EXAMPLE_RE = re.compile(r"^(He|She|They) (noticed|said|thought) that .+ (was|were) (crucial|important)\.?$", re.I)


def _clean_reference_example(item: dict):
    """Example sentence of a reference-base entry, or None.
    Machine templates such as "He noticed that current climate was crucial." are not examples
    and are dropped. A kept example is always labelled as not coming from the corpus books."""
    ex = item.get('example') or {}
    if not isinstance(ex, dict):
        return None
    src = (ex.get('source_sentence') or ex.get('en') or '').strip()
    tgt = (ex.get('target_sentence') or ex.get('uz') or '').strip()
    if not src or TEMPLATE_EXAMPLE_RE.match(src):
        return None
    if tgt and tgt.lower() == (item.get('uzbek') or '').strip().lower():
        tgt = ''   # a bare copy of the variant is not a translated example
    return {
        "source_sentence": src,
        "target_sentence": tgt,
        "book": "Namuna gap (kitobdan emas)",
        "label": ex.get('label') or "Namuna gap — AI tomonidan tuzilgan, tekshirilmagan",
        "uzbek_label": "AI tarjimasi" if tgt else None,
    }

# Proper names blacklist per Section 1.1 / S3
KNOWN_NAMES = {
    'zebi', 'enaxon', 'razzoq', 'miryoqub', 'akbarali', 'poshshaxon', 'xadichaxon',
    'saltanat', 'olmasxon', 'o‘lmasxon', 'oʻlmasxon', 'eshon', 'eshonbobo', 'domla',
    'mulla', 'qurbon', 'salim', 'fotima', 'zuhra', 'santiago', 'santyago', 'manolin', 'perico',
    'martin', 'rogelio', 'pedrico', 'cienfuegos', 'havana', 'afrika', 'amerika',
    'cho‘lpon', 'cholpon', 'hemingway', 'xeminguey', 'g‘ofurov', 'gofurov', 'fort',
    'sharq', 'toshkent', 'samarqand', 'farg‘ona', 'andijon', 'qo‘qon', 'namangan',
    'mingboshi', 'sart', 'rossiya', 'moskva', 'peterburg', 'qurvonbibi', 'salimboyvachcha'
}

UZBEK_CLOSED_CLASSES = {
    'bu', 'u', 'men', 'sen', 'biz', 'siz', 'ular', 'o‘sha', 'oʻsha', "o'sha",
    'shu', 'o‘z', 'oʻz', "o'z", 'o‘zi', 'oʻzi', "o'zi", 'o‘zini', 'o‘ziga', 'o‘zida', 'o‘zidan',
    'uni', 'unga', 'unda', 'undan', 'unisi', 'uning', 'uningda', 'ularning',
    'menga', 'meni', 'menda', 'mendan', 'mening', 'senga', 'seni', 'senda', 'sendan', 'sening',
    'bizga', 'bizni', 'bizda', 'bizdan', 'bizning', 'sizga', 'sizni', 'sizda', 'sizdan', 'sizning',
    'ularga', 'ularni', 'ularda', 'ulardan', 'buni', 'bunga', 'bunda', 'bundan',
    'shuni', 'shunga', 'shunda', 'shundan', 'o‘shani', 'o‘shanga', 'o‘shanda', 'o‘shandan',
    'unday', 'bunday', 'shunday', 'qanday', 'mana', 'ana', 'harqanday',
    'har', 'har kim', 'harkim', 'har narsa', 'hamma', 'barcha', 'bari', 'hech', 'hech kim', 'hechkim', 'hech narsa',
    'kim', 'nima', 'qaysi', 'qanaqa', 'qachon', 'qayerda', 'qayoqda', 'necha',
    'bir', 'ikki', 'ikkala', 'uch', 'uchala', 'to‘rt', 'to‘rtala', 'besh', 'olti', 'yetti', 'sakkiz', 'to‘qqiz',
    'o‘n', 'yigirma', 'o‘ttiz', 'qirq', 'ellik', 'oltmish', 'yetmish', 'sakson', 'to‘qson', 'yuz', 'ming',
    'million', 'milliard', 'nomer', 'yarim', 'chorak', 'biri', 'ikkovi',
    'uchun', 'bilan', 'kabi', 'singari', 'sayin', 'qarab', 'ko‘ra', 'yarasha', 'bo‘yicha', 'qadar',
    'tufayli', 'chog‘li', 'qaraganda', 'boshqa', 'bo‘lak', 'tomon', 'orasida', 'ichida', 'ustida', 'ostida',
    'va', 'ham', 'lekin', 'ammo', 'biroq', 'chunki', 'agar', 'go‘yo', 'toki', 'yoki', 'yo', 'na',
    'balki', 'vaholanki', 'holbuki', 'esa', 'deb',
    'kerak', 'lozim', 'darkor', 'mumkin', 'shart', 'ehtimol', 'darhaqiqat', 'afsuski', 'albatta',
    'xullas', 'shekilli', 'chog‘i', 'yo‘q', 'yoʻq', "yo'q", 'bor', 'edi', 'ekan', 'emish',
    'faqat', 'hatto', 'hali', 'endi', 'yana', 'allaqachon', 'so‘ng', 'keyin', 'oldin',
    'dedi', 'derdi', 'der', 'demoq', 'dedilar', 'degan', 'qildi', 'qilgan', 'etdi'
}
UZBEK_STOPWORDS = UZBEK_CLOSED_CLASSES

AUXILIARY_VERBS_UZ = {
    'boshla', 'boshlamoq', 'qo‘y', 'qo‘ymoq', 'qol', 'qolmoq',
    'ket', 'ketmoq', 'yubor', 'yubormoq', 'tashla', 'tashlamoq'
}

ENGLISH_STOPWORDS = {
    'the', 'a', 'an', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from',
    'by', 'with', 'of', 'in', 'out', 'as', 'if', 'then', 'than', 'that', 'this',
    'these', 'those', 'it', 'its', 'he', 'she', 'they', 'his', 'her', 'their',
    'my', 'your', 'our', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'would', 'could', 'should', 'will', 'can', 'may', 'might',
    'is', 'are', 'am', 'so', 'just', 'more', 'most', 'very', 'too', 'not', 'no',
    'all', 'any', 'some', 'there', 'here', 'when', 'where', 'how', 'what', 'who',
    'which', 'why', 'up', 'down', 'over', 'under', 'into', 'about', 'him', 'them',
    'me', 'us', 'you', 'yours', 'mine', 'hers', 'ours', 'theirs', 'own',
    'himself', 'itself', 'themselves', 'one', 'two', 'three', 'come', 'came',
    'now', 'always', 'back', 'never', 'already', 'went', 'go', 'see', 'saw', 'said',
    'must', 'even', 'still', 'again', 'until', 'after', 'without', 'like', 'way', 'didn', 't', 'don', 'doesn'
}

COMMON_VERBS = {
    'ber': 'bermoq', 'ol': 'olmoq', 'bo‘l': 'bo‘lmoq', 'boʻl': 'bo‘lmoq', 'qil': 'qilmoq',
    'sol': 'solmoq', 'uxla': 'uxlamoq', 'uxlat': 'uxlatmoq', 'uyg‘on': 'uyg‘onmoq',
    'et': 'etmoq', 'ayt': 'aytmoq', 'o‘y': 'o‘ylamoq', 'o‘yla': 'o‘ylamoq', 'oʻyla': 'o‘ylamoq',
    'ket': 'ketmoq', 'kel': 'kelmoq', 'chiq': 'chiqmoq', 'tush': 'tushmoq', 'tur': 'turmoq',
    'yur': 'yurmoq', 'bor': 'bormoq', 'sez': 'sezmoq', 'ko‘r': 'ko‘rmoq', 'koʻr': 'ko‘rmoq',
    'bil': 'bilmoq', 'top': 'topmoq', 'ur': 'urmoq', 'och': 'ochmoq', 'yop': 'yopmoq',
    'boshla': 'boshlamoq', 'tort': 'tortmoq', 'qo‘y': 'qo‘ymoq', 'qoʻy': 'qo‘ymoq',
    'tortin': 'tortinmoq', 'qol': 'qolmoq', 'tin': 'tinchimoq', 'tinchi': 'tinchimoq',
    'o‘rtan': 'o‘rtanmoq', 'oʻrtan': 'o‘rtanmoq', 'titra': 'titramoq', 'yon': 'yonmoq',
    'muzla': 'muzlamoq', 'og‘ri': 'og‘rimoq', 'yig‘la': 'yig‘lamoq', 'kul': 'kulmoq',
    'unut': 'unutmoq', 'esla': 'eslamoq', 'xohla': 'xohlamoq', 'istamoq': 'istamoq',
    'sev': 'sevmoq', 'yoq': 'yoqmoq', 'ez': 'ezmoq', 'siq': 'siqmoq', 'yirt': 'yirtmoq',
    'cho‘k': 'cho‘kmoq', 'uch': 'uchmoq', 'yot': 'yotmoq', 'ot': 'otmoq', 'yet': 'yetmoq',
    'o‘ch': 'o‘chmoq', 'oʻch': 'o‘chmoq', 'o‘yna': 'o‘ynamoq', 'oʻyna': 'o‘ynamoq'
}

VERB_SUFFIXES = (
    '', 'moq', 'di', 'dim', 'ding', 'dik', 'dilar', 'gan', 'gancha', 'sa', 'sam', 'sang', 'sak', 'salar',
    'moqda', 'yapti', 'yapman', 'b', 'ib', 'ay', 'aylik', 'sin', 'ar', 'ardi', 'arman', 'arsan',
    'adi', 'adilar', 'aman', 'asan', 'amiz', 'asiz', 'adir',
    'mas', 'maslik', 'maydi', 'madi', 'madim', 'tirish', 'tirdi', 'uvdi', 'vdi',
    'ildi', 'ildilar', 'ilgan', 'iladi', 'ilmoq', 'indi', 'ingan', 'inadi', 'inmoq', 'ishga', 'ish'
)

PROTECTED_NOUNS = {
    'tashvish', 'xurush', 'olqish', 'qarg‘ish', 'qaror', 'ko‘ngil', 'yurak', 'yurag',
    'qishloq', 'qishlog‘', 'dil', 'dard', 'qalb', 'alam', 'hasrat', 'muhabbat', 'ishq',
    'sevgi', 'armon', 'orzu', 'umid', 'xayol', 'fikr', 'aql', 'sabot', 'saboz', 'bardosh',
    'matonat', 'jasorat', 'shijoat', 'g‘azab', 'qahr', 'nafrat', 'hasad', 'rashk',
    'shubha', 'gumon', 'ishonch', 'e’tiqod', 'marhamat', 'shafqat', 'rahmdillik',
    'tinchlik', 'xotirjamlik', 'sir', 'gap', 'so‘z', 'nasihat', 'pand', 'chol',
    'uyqu', 'javob', 'dasturxon', 'ayvon', 'ko‘z', 'bosh', 'yuz', 'baliq', 'dengiz', 'akula',
    'xotin', 'rang'
}

EQUIV_LEXICON_UZ2EN = {
    'ko‘ngil': ['heart', 'soul', 'mind', 'spirit', 'desire', 'wish', 'feeling', 'mood', 'affection'],
    'yurak': ['heart', 'breast', 'courage', 'chest', 'bosom'],
    'qaror': ['decision', 'determination', 'resolution', 'decree', 'decide', 'decided', 'resolve'],
    'qishloq': ['village', 'countryside', 'settlement'],
    'uyqu': ['sleep', 'slumber'],
    'javob': ['answer', 'reply', 'response'],
    'dasturxon': ['table', 'cloth'],
    'xotin': ['wife', 'woman', 'women'],
    'rang': ['face', 'color', 'colour', 'look']
}

EQUIV_LEXICON_EN2UZ = {
    'heart': ['yurak', 'yuragi', 'yurakdan', 'ko‘ngil', 'ko‘ngli', 'qalb', 'dil', 'bag‘ir'],
    'decision': ['qaror', 'qarori', 'hukm', 'to‘xtam', 'xulosa'],
    'decide': ['qaror qilmoq', 'qaror bermoq', 'to‘xtamga kelmoq', 'o‘ylamoq'],
    'sleep': ['uyqu', 'uxlamoq', 'og‘ir uyqu', 'deep sleep'],
    'table': ['dasturxon', 'stol'],
    'wife': ['xotin', 'rafiq'],
    'shark': ['akula']
}

def is_collocation_query(query: str) -> bool:
    tokens = [w for w in re.split(r"\s+", query.strip()) if w]
    return len(tokens) >= 2

def resolve_uzbek(token: str) -> Tuple[Optional[str], str]:
    """Resolves an Uzbek token to full dictionary lemma (verbs in -moq, nouns in nominative)."""
    raw = token.lower().strip(" 'ʻʼ‘-")
    norm = uz_norm(raw).replace('ʻ', '‘').replace('ʼ', '’')
    if norm in KNOWN_NAMES or any(norm.startswith(nm) for nm in KNOWN_NAMES):
        return None, 'atoqli_ot'
    if norm in {'unday', 'bunday', 'shunday', 'qanday', 'mana', 'ana'}:
        return norm, 'olmosh'
    if norm in UZBEK_STOPWORDS:
        return None, 'yordamchi'

    for pn in PROTECTED_NOUNS:
        pn_n = uz_norm(pn).replace('ʻ', '‘').replace('ʼ', '’')
        if norm == pn_n or norm.startswith(pn_n):
            c = 'ko‘ngil' if 'ko‘ngl' in pn_n else ('yurak' if 'yurag' in pn_n else pn)
            return c, 'ot'

    if norm.startswith('ko‘ngl') or norm.startswith('kongl'):
        return 'ko‘ngil', 'ot'
    if norm.startswith('o‘g‘l') or norm.startswith('ogl'):
        return 'o‘g‘il', 'ot'

    for v_stem, v_lemma in COMMON_VERBS.items():
        v_stem_n = uz_norm(v_stem).replace('ʻ', '‘').replace('ʼ', '’')
        if norm == v_stem_n or norm.startswith(v_stem_n):
            rest = norm[len(v_stem_n):]
            if rest in VERB_SUFFIXES:
                return v_lemma, 'fe’l'

    if norm.endswith(('dek', 'day', 'roq', 'li', 'siz', 'iy', 'viy')) and len(norm) > 4:
        return norm, 'sifat'
    if norm in {'yosh', 'og‘ir', 'yengil', 'toza', 'pok', 'katta', 'kichik', 'qattiq', 'yumshoq', 'yaxshi', 'yomon',
                'muhim', 'asosiy', 'oqilona', 'dono', 'shoshilinch', 'issiq', 'sovuq', 'qat’iy', 'qatiy', 'chin'}:
        return 'qat’iy' if norm in ('qat’iy', 'qatiy') else norm, 'sifat'
    if norm in {'tez', 'sekin', 'asta', 'birdan', 'to‘satdan', 'chuqur'}:
        return norm, 'ravish'

    for nsfx in ('larimiz', 'laringiz', 'lariga', 'larida', 'laridan', 'larini', 'larning', 'lar',
                 'imiz', 'ingiz', 'lar', 'ning', 'dan', 'da', 'ga', 'ka', 'qa', 'ni', 'i', 'si'):
        if norm.endswith(nsfx) and len(norm) - len(nsfx) >= 3:
            stem = norm[:-len(nsfx)]
            if stem.endswith('g'): stem = stem[:-1] + 'k'
            elif stem.endswith('g‘') or stem.endswith('gʻ'): stem = stem[:-2] + 'q'
            return stem, 'ot'

    return norm, 'so‘z turkumi aniqlanmagan'

@lru_cache(maxsize=16384)
def resolve_english(token: str) -> Tuple[Optional[str], str]:
    """Resolves an English token to dictionary lemma."""
    tok = token.lower().strip(" '\"-")
    if tok in KNOWN_NAMES or tok in ENGLISH_STOPWORDS or len(tok) < 3 or tok.isdigit():
        return None, 'stop'

    if tok in ('make', 'take', 'give', 'know', 'see', 'feel', 'break', 'beat', 'flutter', 'start', 'skip', 'desire', 'understand', 'reach', 'hold', 'set', 'catch', 'lose', 'fall', 'stand', 'tell', 'speak', 'decide', 'change', 'live'):
        return lemmatizer.lemmatize(tok, pos='v'), 'verb'
    if tok in ('young', 'old', 'big', 'small', 'great', 'heavy', 'deep', 'wise', 'strong', 'weak', 'pale', 'cold', 'warm', 'hot', 'good', 'bad', 'hard', 'soft', 'brave', 'sad', 'happy', 'quick', 'final', 'right'):
        return tok, 'adjective'

    lemma_n = lemmatizer.lemmatize(tok, pos='n')
    lemma_v = lemmatizer.lemmatize(tok, pos='v')

    if tok.endswith(('ed', 'ing')) or lemma_v != tok:
        return lemma_v, 'verb'
    if tok.endswith(('ful', 'less', 'able', 'ive', 'ous', 'al', 'ic', 'y')):
        return tok, 'adjective'
    return lemma_n, 'noun'

def safe_highlight(text: str, match_spans: List[Tuple[int, int]], highlight_class: str = "query-match font-semibold bg-amber-200 dark:bg-amber-900/60 text-amber-950 dark:text-amber-100 px-1 py-0.5 rounded") -> str:
    """Safely highlights spans in text with HTML escaping."""
    if not match_spans:
        return html.escape(text)

    sorted_spans = sorted(match_spans, key=lambda s: s[0])
    merged = []
    for s, e in sorted_spans:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)

    parts = []
    last_idx = 0
    for s, e in merged:
        parts.append(html.escape(text[last_idx:s]))
        highlighted_word = html.escape(text[s:e])
        parts.append(f'<mark class="{highlight_class}">{highlighted_word}</mark>')
        last_idx = e
    parts.append(html.escape(text[last_idx:]))
    return "".join(parts)

def safe_highlight_equivalent(text: str, spans: List[Tuple[int, int]], is_confirmed: bool = False, source_label: str = None) -> str:
    """Highlights proposed target equivalent in Colour 2 dashed underline (or solid if confirmed)."""
    if not spans:
        return html.escape(text)

    sorted_spans = sorted(spans, key=lambda s: s[0])
    merged = []
    for s, e in sorted_spans:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)

    parts = []
    last_idx = 0
    cls = "equiv-confirmed bg-sky-100 dark:bg-sky-950 text-sky-900 dark:text-sky-100 border-b-2 border-sky-600 px-1 py-0.5 rounded font-semibold" if is_confirmed else "equiv-proposed bg-sky-50 dark:bg-sky-950/70 text-sky-800 dark:text-sky-200 border-b-2 border-dashed border-sky-500 px-1 py-0.5 rounded font-semibold"
    title = source_label or ("Kitobdagi tarjima — tasdiqlangan" if is_confirmed else "Kitobdagi tarjima — AI-taklif (tekshirilmagan)")

    for s, e in merged:
        parts.append(html.escape(text[last_idx:s]))
        eq_word = html.escape(text[s:e])
        parts.append(f'<span class="{cls}" title="{title}">{eq_word}</span>')
        last_idx = e
    parts.append(html.escape(text[last_idx:]))
    return "".join(parts)

def match_collocation_in_sentence(text: str, query: str, lang: str) -> Tuple[List[Tuple[int, int]], List[str]]:
    """
    Matches multi-word collocation in sentence with up to 2 intervening tokens,
    either order where appropriate per TILCOR_07-1 Part 3.
    Returns (match_spans, matched_tokens).
    """
    q_words = [w for w in re.split(r"\s+", query.strip()) if w]
    if len(q_words) < 2:
        return [], []

    if lang == 'uz':
        norm_s, offsets = uz_norm(text, return_offsets=True)
        if not norm_s:
            return [], []

        tokens_info = []
        for m in TOKEN_UZ_NORM_RE.finditer(norm_s):
            tok = m.group(0)
            lem, pos = resolve_uzbek(tok)
            start_n, end_n = m.span()
            orig_start = offsets[start_n]
            orig_end = offsets[end_n - 1] + 1
            tokens_info.append({
                "tok": tok,
                "lemma": lem or tok,
                "pos": pos,
                "span": (orig_start, orig_end),
                "orig_text": text[orig_start:orig_end]
            })

        q_lemmas = []
        for qw in q_words:
            qw_lem, qw_pos = resolve_uzbek(qw)
            q_norm_w = uz_norm(qw)
            stem = q_norm_w[:-3] if q_norm_w.endswith('moq') else q_norm_w
            q_lemmas.append({
                "raw": qw,
                "norm": q_norm_w,
                "lemma": qw_lem or qw,
                "stem": stem,
                "pos": qw_pos
            })

        p1, p2 = q_lemmas[0], q_lemmas[1]

        def token_matches_q(t_info, q_info):
            t_tok = t_info['tok']
            t_lem = t_info['lemma']
            if t_lem == q_info['lemma'] or t_lem == q_info['norm']:
                return True
            if t_tok.startswith(q_info['stem']):
                return True
            if q_info['norm'] in t_tok:
                return True
            return False

        found_spans = []
        found_tokens = []

        for i, t1 in enumerate(tokens_info):
            m1 = token_matches_q(t1, p1)
            m2 = token_matches_q(t1, p2)

            if m1:
                for j in range(i + 1, min(len(tokens_info), i + 4)):
                    t2 = tokens_info[j]
                    if token_matches_q(t2, p2):
                        found_spans.extend([t1['span'], t2['span']])
                        found_tokens.extend([t1['orig_text'], t2['orig_text']])
                        return found_spans, found_tokens
            if m2:
                for j in range(i + 1, min(len(tokens_info), i + 4)):
                    t2 = tokens_info[j]
                    if token_matches_q(t2, p1):
                        found_spans.extend([t1['span'], t2['span']])
                        found_tokens.extend([t1['orig_text'], t2['orig_text']])
                        return found_spans, found_tokens

        return [], []

    else:
        # English collocation matching
        tokens_info = []
        for m in TOKEN_EN_RE.finditer(text):
            tok = m.group(0)
            lem, pos = resolve_english(tok)
            tokens_info.append({
                "tok": tok.lower(),
                "lemma": lem or tok.lower(),
                "pos": pos,
                "span": m.span(),
                "orig_text": tok
            })

        q_words_clean = [w.lower() for w in q_words]
        q_phrase = " ".join(q_words_clean)
        text_lower = text.lower()
        if q_phrase in text_lower:
            start_idx = text_lower.find(q_phrase)
            end_idx = start_idx + len(q_phrase)
            return [(start_idx, end_idx)], [text[start_idx:end_idx]]

        content_q = [qw for qw in q_words_clean if qw not in ('the', 'a', 'an')]
        if len(content_q) >= 2:
            p1 = lemmatizer.lemmatize(content_q[0], 'v')
            p2 = lemmatizer.lemmatize(content_q[1], 'n')
            for i, t1 in enumerate(tokens_info):
                if t1['lemma'] == p1 or t1['tok'] == content_q[0] or (content_q[0] == 'fell' and t1['tok'] == 'fell'):
                    for j in range(i + 1, min(len(tokens_info), i + 4)):
                        t2 = tokens_info[j]
                        if t2['lemma'] == p2 or t2['tok'] == content_q[1] or t2['tok'].startswith(content_q[1]):
                            return [t1['span'], t2['span']], [t1['orig_text'], t2['orig_text']]

        return [], []

def find_word_family_spans(sentence: str, query: str, lang: str) -> Tuple[List[Tuple[int, int]], Set[Tuple[str, str]]]:
    spans = []
    matched_words = set()

    if lang == 'uz':
        norm_s, offsets = uz_norm(sentence, return_offsets=True)
        if not norm_s or not offsets:
            return spans, matched_words

        for m in TOKEN_UZ_NORM_RE.finditer(norm_s):
            token = m.group(0)
            match_res = match_uzbek_word_family(query, token)
            if match_res:
                group_type, norm_form = match_res
                n_start, n_end = m.span()
                orig_start = offsets[n_start]
                orig_end = offsets[n_end - 1] + 1
                spans.append((orig_start, orig_end))
                orig_token = sentence[orig_start:orig_end]
                matched_words.add((orig_token.lower(), group_type))
    else:
        for m in TOKEN_EN_RE.finditer(sentence):
            token = m.group(0)
            start, end = m.span()
            match_res = match_english_word_family(query, token)
            if match_res:
                group_type, norm_form = match_res
                spans.append((start, end))
                matched_words.add((token.lower(), group_type))

    return spans, matched_words

def propose_target_spans(src_text: str, tgt_text: str, query: str, lang: str) -> List[Tuple[int, int]]:
    q_norm = uz_norm(query).replace('ʻ', '‘').replace('ʼ', '’') if lang == 'uz' else query.lower()
    targets = EQUIV_LEXICON_UZ2EN.get(q_norm, []) if lang == 'uz' else EQUIV_LEXICON_EN2UZ.get(q_norm, [])

    found_spans = []
    for t in targets:
        t_esc = re.escape(t)
        pattern = re.compile(r'\b' + t_esc + r'[a-zA-Z\u02bb\u02bc]*\b', re.IGNORECASE)
        for m in pattern.finditer(tgt_text):
            found_spans.append(m.span())

    return found_spans

def extract_corpus_collocation_candidates(sentences: List[Dict], query: str, lang: str) -> Tuple[List[Dict], List[Dict]]:
    q_norm = uz_norm(query).replace('ʻ', '‘').replace('ʼ', '’') if lang == 'uz' else query.lower()
    q_lemma, q_pos = resolve_uzbek(query) if lang == 'uz' else (lemmatizer.lemmatize(q_norm, 'n'), 'noun')

    pair_occurrences = Counter()
    pair_sentences = defaultdict(set)
    pair_books = defaultdict(set)
    pair_patterns = {}
    pair_examples = {}

    for s in sentences:
        book = s.get('book', 'cholpon')
        if lang == 'uz':
            text = s.get('uz') or (s.get('source_raw') if book == 'cholpon' else s.get('target_raw')) or ''
            tgt_text = s.get('en') or (s.get('target_raw') if book == 'cholpon' else s.get('source_raw')) or ''
        else:
            text = s.get('en') or (s.get('target_raw') if book == 'cholpon' else s.get('source_raw')) or ''
            tgt_text = s.get('uz') or (s.get('source_raw') if book == 'cholpon' else s.get('target_raw')) or ''

        if 'query_raw' in s:
            # processed search sentence: use the explicit sides so the example is never mixed up
            text = s.get('query_raw') or text
            tgt_text = s.get('other_raw') or tgt_text
            tgt_highlighted = s.get('other_highlighted') or html.escape(tgt_text)
            page_src = s.get('query_page') or ''
            page_tgt = s.get('other_page') or ''
        else:
            page_src = s.get('page_source', '')
            page_tgt = s.get('page_target', '')
            tgt_highlighted = html.escape(tgt_text)
        s_id = s.get('id', '')

        if not text:
            continue

        if lang == 'uz':
            norm_text, offsets = uz_norm(text, return_offsets=True)
            if not norm_text:
                continue
            token_matches = list(TOKEN_UZ_NORM_RE.finditer(norm_text))
            tokens = [m.group(0) for m in token_matches]

            m_indices = [i for i, t in enumerate(tokens) if match_uzbek_word_family(q_norm, t)]
            for m_idx in m_indices:
                matched_token_text = tokens[m_idx]
                is_possessive = (q_lemma in ('ko‘ngil', 'yurak')) and any(matched_token_text.endswith(suf) for suf in ('i', 'si', 'im', 'ing', 'imiz', 'ingiz', 'lari'))
                subject_lemma = 'ko‘ngli' if (q_lemma == 'ko‘ngil' and is_possessive) else ('yuragi' if (q_lemma == 'yurak' and is_possessive) else q_lemma)

                for w_idx in range(max(0, m_idx - 4), min(len(tokens), m_idx + 5)):
                    if w_idx == m_idx:
                        continue
                    tok = tokens[w_idx]
                    lem, pos = resolve_uzbek(tok)
                    if not lem or lem == q_lemma:
                        continue
                    if pos in ('so‘z turkumi aniqlanmagan', 'aniqlanmagan', 'yordamchi', 'atoqli_ot', 'stop', 'son', 'olmosh'):
                        continue

                    if lem in AUXILIARY_VERBS_UZ or lem in ('boshlamoq', 'qo‘ymoq', 'qolmoq', 'ketmoq', 'yubormoq'):
                        continue

                    pattern = None
                    if q_pos == 'ot' and pos == 'fe’l':
                        pattern = 'Ega + kesim' if is_possessive else 'Ot + fe’l'
                        phrase = f"{subject_lemma} {lem}"
                    elif q_pos == 'ot' and pos == 'sifat':
                        pattern = 'Sifat + ot'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'ot' and pos == 'ot':
                        pattern = 'Ot + ot'
                        phrase = f"{q_lemma} {lem}" if m_idx < w_idx else f"{lem} {q_lemma}"
                    elif q_pos == 'fe’l' and pos == 'ot':
                        pattern = 'Ot + fe’l'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'fe’l' and pos == 'ravish':
                        pattern = 'Ravish + fe’l'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'sifat' and pos == 'ot':
                        pattern = 'Sifat + ot'
                        phrase = f"{q_lemma} {lem}"
                    else:
                        continue

                    pair_occurrences[phrase] += 1
                    pair_sentences[phrase].add(s_id)
                    pair_books[phrase].add(book)
                    pair_patterns[phrase] = pattern

                    if phrase not in pair_examples:
                        m_spans = []
                        m_t1 = token_matches[m_idx]
                        m_t2 = token_matches[w_idx]
                        s1, e1 = offsets[m_t1.start()], offsets[m_t1.end() - 1] + 1
                        s2, e2 = offsets[m_t2.start()], offsets[m_t2.end() - 1] + 1
                        m_spans.extend([(s1, e1), (s2, e2)])
                        pair_examples[phrase] = {
                            "source_sentence": text,
                            "source_highlighted": safe_highlight(text, m_spans),
                            "target_sentence": tgt_text,
                            "target_highlighted": tgt_highlighted,
                            "book": book,
                            "page_source": page_src,
                            "page_target": page_tgt,
                            "is_open": bool(s.get('is_open'))
                        }
        else:
            token_matches = list(TOKEN_EN_RE.finditer(text))
            tokens = [m.group(0).lower() for m in token_matches]
            m_indices = [i for i, t in enumerate(tokens) if match_english_word_family(q_norm, t)]
            for m_idx in m_indices:
                for w_idx in range(max(0, m_idx - 4), min(len(tokens), m_idx + 5)):
                    if w_idx == m_idx:
                        continue
                    tok = tokens[w_idx]
                    lem, pos = resolve_english(tok)
                    if not lem or lem == q_lemma or pos in ('stop', 'pronoun'):
                        continue

                    pattern = None
                    if q_pos == 'noun' and pos == 'adjective':
                        pattern = 'Adjective + noun'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'noun' and pos == 'verb':
                        pattern = 'Verb + noun'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'verb' and pos == 'noun':
                        pattern = 'Verb + noun'
                        phrase = f"{q_lemma} {lem}"
                    elif q_pos == 'adjective' and pos == 'noun':
                        pattern = 'Adjective + noun'
                        phrase = f"{q_lemma} {lem}"
                    else:
                        continue

                    pair_occurrences[phrase] += 1
                    pair_sentences[phrase].add(s_id)
                    pair_books[phrase].add(book)
                    pair_patterns[phrase] = pattern

                    if phrase not in pair_examples:
                        m_spans = [token_matches[m_idx].span(), token_matches[w_idx].span()]
                        pair_examples[phrase] = {
                            "source_sentence": text,
                            "source_highlighted": safe_highlight(text, m_spans),
                            "target_sentence": tgt_text,
                            "target_highlighted": tgt_highlighted,
                            "book": book,
                            "page_source": page_src,
                            "page_target": page_tgt,
                            "is_open": bool(s.get('is_open'))
                        }

    public_candidates = []
    admin_candidates = []

    for phrase, occ in pair_occurrences.most_common():
        scnt = len(pair_sentences[phrase])
        if scnt >= 1:
            ex = pair_examples[phrase]
            pat = pair_patterns[phrase]
            cand_item = {
                "collocation": phrase,
                "searched_word": query,
                "pattern": pat,
                "source_badge": "Avtomatik nomzod — lingvistik tekshiruvdan o‘tmagan",
                "sentences_count": scnt,
                "occurrences_count": occ,
                "corpus_frequency": occ,
                "books": list(pair_books[phrase]),
                "is_admin_only": (pat == 'Ot + ot'),
                "example": {
                    "source_sentence": ex["source_sentence"],
                    "source_highlighted": ex["source_highlighted"],
                    "target_sentence": ex.get("target_sentence", ""),
                    "target_highlighted": ex.get("target_highlighted", ""),
                    "book": ex["book"],
                    "page_source": ex.get("page_source", ""),
                    "page_target": ex.get("page_target", ""),
                    "query_lang": lang,
                    "is_open": bool(ex.get("is_open"))
                }
            }
            # Methodology (1.1.4; Kjellmer 1987, Bernardini 2007): an automatic candidate is shown publicly
            # only if it occurs at least twice in the study corpus; 'Ot + ot' goes to a separate admin list.
            if pat == 'Ot + ot' or occ < MIN_CANDIDATE_FREQ:
                admin_candidates.append(cand_item)
            else:
                public_candidates.append(cand_item)

    return public_candidates, admin_candidates

_CACHED_DICT_BY_WORD = {}
_CACHED_DICT_LEN = 0

def get_cached_dict(active_dictionary):
    global _CACHED_DICT_BY_WORD, _CACHED_DICT_LEN
    if len(active_dictionary) == _CACHED_DICT_LEN and _CACHED_DICT_BY_WORD:
        return _CACHED_DICT_BY_WORD
    dbw = {}
    for d in active_dictionary:
        dw = d.get('word', '').strip()
        if dw and SINGLE_WORD_CLEAN_RE.match(dw):
            dw_norm = uz_norm(dw)
            if dw_norm not in dbw:
                dbw[dw_norm] = d
    _CACHED_DICT_BY_WORD = dbw
    _CACHED_DICT_LEN = len(active_dictionary)
    return dbw

_UZ_POS_NAME = {'ot': 'Ot', 'fe’l': 'Fe’l', 'sifat': 'Sifat', 'ravish': 'Ravish'}
_EN_POS_NAME = {'noun': 'Noun', 'verb': 'Verb', 'adjective': 'Adjective', 'adverb': 'Adverb'}

def guess_query_pattern(query: str, lang: str) -> str:
    """Pattern of a multi-word query from the part of speech of its words.
    Unknown parts of speech give 'Birikma' (pattern not identified) rather than a guess."""
    words = [w for w in re.split(r"\s+", query.strip()) if w]
    names = []
    for w in words:
        if lang == 'uz':
            _lem, pos = resolve_uzbek(w)
            name = _UZ_POS_NAME.get(pos)
            if not name and pos == 'so‘z turkumi aniqlanmagan':
                # a bare Uzbek word in a dictionary-form query: -moq/-mak is a verb, otherwise a noun
                name = 'Fe’l' if uz_norm(w).endswith(('moq', 'mak')) else 'Ot'
        else:
            if w.lower() in ('the', 'a', 'an'):
                continue
            _lem, pos = resolve_english(w.lower())
            name = _EN_POS_NAME.get(pos)
        if not name:
            return 'Birikma'
        names.append(name)
    return (' + '.join(names) + ' (avtomatik)') if len(names) >= 2 else 'Birikma (avtomatik)'

def execute_unified_search(
    query: str,
    active_corpus: List[Dict],
    active_collocations: List[Dict],
    active_dictionary: List[Dict],
    forced_lang: Optional[str] = None,
    limit: int = 50,
    page: int = 1
) -> Dict[str, Any]:
    """Executes search for TILCOR with 5-source equivalent hierarchy & collocation queries."""
    q = query.strip()
    if not q:
        return {"query": "", "results": []}

    detected_lang = detect_query_language(q)

    # Russian rejection rule
    if detected_lang == 'ru':
        return {
            "query": q,
            "detected_lang": "ru",
            "error": "Qidiruv o‘zbek va ingliz tillarida ishlaydi",
            "summary": {"total_word_forms": 0, "corpus_occurrences": 0, "collocations_count": 0},
            "muqobil_summary": {"source_1_confirmed": [], "source_2_ai_proposal": [], "source_3_dictionary": [], "source_4_reference": []},
            "words": [],
            "collocations": [],
            "corpus_sentences": [],
            "pagination": {"page": 1, "limit": limit, "total_sentences": 0, "total_pages": 1}
        }

    is_ambiguous = (detected_lang == 'ambiguous')
    selected_lang = forced_lang if forced_lang in ('uz', 'en') else ('uz' if detected_lang in ('uz', 'ambiguous') else 'en')
    is_multi = is_collocation_query(q)

    dict_by_word = get_cached_dict(active_dictionary)

    word_forms_map = {}
    matched_corpus_sentences = []
    book_translations_by_form = defaultdict(Counter)
    book_pages_by_form = defaultdict(set)

    # Pre-filtering tokens for high speed
    q_for_filter = uz_norm(q) if selected_lang == 'uz' else q.lower()
    q_words = [w for w in re.split(r"[^\w\u02bb\u02bc'‘ʻʼ’]+", q_for_filter.lower()) if w]
    prefixes = []
    for w in q_words:
        w_sub = re.split(r"['`‘ʻʼ’\u02bb\u02bc]", w)[0]
        if len(w_sub) >= 2:
            prefixes.append(w_sub[:min(len(w_sub), 3)])
        elif len(w) >= 2:
            prefixes.append(w[:2])

    # Tracking confirmed and AI-taklif equivalents for Muqobil summary
    muqobil_s1_map = defaultdict(lambda: {"count": 0, "form": "—", "pages": set(), "sids": [], "target_spans": []})
    muqobil_s2_map = defaultdict(lambda: {"count": 0, "form": "—", "pages": set(), "sids": [], "target_spans": []})

    for seg in active_corpus:
        book = seg.get('book', 'cholpon')
        sid = seg.get('id', '')
        aln_status = seg.get('status', 'avtomatik — ikki usul mos')
        is_confirmed = (aln_status == 'tasdiqlangan')
        conf_eq = seg.get('confirmed_equivalent')

        if book == 'cholpon':
            p_src_val = seg.get('uz_page')
            p_tgt_val = seg.get('en_page')
            orig_text = seg.get('uz', '')
            trans_text = seg.get('en', '')
            source_label = f"Asliyat (o‘zbekcha) — Kecha va kunduz, {p_src_val}-bet" if p_src_val else "Asliyat (o‘zbekcha) — Kecha va kunduz"
            target_label = f"Tarjima (inglizcha) — Night and Day, {p_tgt_val}-bet" if p_tgt_val else "Tarjima (inglizcha) — Night and Day"
            page_src_str = f"{p_src_val}-bet (ziyouz.com)" if p_src_val else ""
            page_tgt_str = f"{p_tgt_val}-bet" if p_tgt_val else ""
        else: # hemingway
            p_src_val = seg.get('en_page')
            p_tgt_val = seg.get('uz_page')
            orig_text = seg.get('en', '')
            trans_text = seg.get('uz', '')
            source_label = f"Asliyat (inglizcha) — The Old Man and the Sea, {p_src_val}-bet" if p_src_val else "Asliyat (inglizcha) — The Old Man and the Sea"
            target_label = f"Tarjima (o‘zbekcha) — Chol va dengiz, elektron nusxa, {p_tgt_val}-bet" if p_tgt_val else "Tarjima (o‘zbekcha) — Chol va dengiz, elektron nusxa"
            page_src_str = f"{p_src_val}-bet" if p_src_val else ""
            page_tgt_str = f"elektron nusxa, {p_tgt_val}-bet" if p_tgt_val else ""

        query_in_orig = (selected_lang == 'uz' and book == 'cholpon') or (selected_lang == 'en' and book == 'hemingway')
        s_search = orig_text if query_in_orig else trans_text
        s_other = trans_text if query_in_orig else orig_text

        if not s_search:
            continue

        s_search_lower = s_search.lower()
        if prefixes and not any(p in s_search_lower for p in prefixes):
            continue

        if is_multi:
            search_spans, matched_tokens_raw = match_collocation_in_sentence(s_search, q, selected_lang)
            if not search_spans:
                continue
            q_forms = {uz_norm(w) if selected_lang == 'uz' else w.lower() for w in q.split()}
            matched_tokens = [(t, 'exact' if (uz_norm(t) if selected_lang == 'uz' else t.lower()) in q_forms else 'inflected')
                              for t in matched_tokens_raw]
        else:
            search_spans, matched_tokens = find_word_family_spans(s_search, q, selected_lang)
            if not search_spans:
                continue

        # Target equivalent processing
        other_spans = []
        target_eq_label = "Kitobdagi tarjima — AI-taklif (tekshirilmagan)"
        is_s1_equivalent = False
        is_s2_equivalent = False

        if is_confirmed and conf_eq:
            c_type = conf_eq.get('source_type', 1)
            target_span_val = conf_eq.get('en_span') if selected_lang == 'uz' else conf_eq.get('uz_span')
            
            # Formatting for discontinuous spans
            if isinstance(target_span_val, list):
                eq_display_str = " … ".join(target_span_val)
            else:
                eq_display_str = str(target_span_val)

            # Get target sentence offsets
            tgt_offsets = conf_eq.get('en_span_offsets') if selected_lang == 'uz' else [conf_eq.get('uz_span_offsets')]
            if tgt_offsets and isinstance(tgt_offsets, list) and isinstance(tgt_offsets[0], (list, tuple)):
                other_spans = [tuple(sp) for sp in tgt_offsets if sp]
            else:
                # compute substring spans in s_other
                if isinstance(target_span_val, list):
                    for part in target_span_val:
                        idx = s_other.find(part)
                        if idx != -1:
                            other_spans.append((idx, idx + len(part)))
                elif target_span_val:
                    idx = s_other.find(target_span_val)
                    if idx != -1:
                        other_spans.append((idx, idx + len(target_span_val)))

            if c_type == 1:
                is_s1_equivalent = True
                target_eq_label = "Kitobdagi tarjima — tasdiqlangan"
                page_info = f"{p_src_val} ➔ {p_tgt_val}"
                muqobil_s1_map[eq_display_str]["count"] += 1
                muqobil_s1_map[eq_display_str]["form"] = conf_eq.get('equivalent_form', '—')
                muqobil_s1_map[eq_display_str]["pages"].add(page_info)
                muqobil_s1_map[eq_display_str]["sids"].append(sid)
                muqobil_s1_map[eq_display_str]["src_page"] = p_src_val
                muqobil_s1_map[eq_display_str]["tgt_page"] = p_tgt_val
            else:
                is_s2_equivalent = True
                target_eq_label = "Kitobdagi tarjima — AI-taklif (tekshirilmagan)"
                page_info = f"{p_src_val} ➔ {p_tgt_val}"
                muqobil_s2_map[eq_display_str]["count"] += 1
                muqobil_s2_map[eq_display_str]["form"] = conf_eq.get('equivalent_form', '—')
                muqobil_s2_map[eq_display_str]["pages"].add(page_info)
                muqobil_s2_map[eq_display_str]["sids"].append(sid)
                muqobil_s2_map[eq_display_str]["src_page"] = p_src_val
                muqobil_s2_map[eq_display_str]["tgt_page"] = p_tgt_val
        elif is_confirmed:
            # AI-taklif is allowed only inside a researcher-confirmed pair (S5/S6).
            # In automatic pairs the translation sentence itself may be wrong,
            # so no equivalent is proposed there.
            other_spans = propose_target_spans(s_search, s_other, q, selected_lang)
            if other_spans:
                for sp1, sp2 in other_spans:
                    eq_str = s_other[sp1:sp2].strip()
                    if eq_str:
                        muqobil_s2_map[eq_str]["count"] += 1
                        muqobil_s2_map[eq_str]["pages"].add(f"{p_src_val} ➔ {p_tgt_val}")
                        muqobil_s2_map[eq_str]["sids"].append(sid)
                        muqobil_s2_map[eq_str]["src_page"] = p_src_val
                        muqobil_s2_map[eq_str]["tgt_page"] = p_tgt_val

        found_eq_words = [s_other[s1:s2].lower() for s1, s2 in other_spans]

        if query_in_orig:
            source_highlighted = safe_highlight(orig_text, search_spans)
            target_highlighted = safe_highlight_equivalent(trans_text, other_spans, is_confirmed=is_s1_equivalent, source_label=target_eq_label)
        else:
            source_highlighted = safe_highlight_equivalent(orig_text, other_spans, is_confirmed=is_s1_equivalent, source_label=target_eq_label)
            target_highlighted = safe_highlight(trans_text, search_spans)

        for tok, grp in matched_tokens:
            tok_norm = uz_norm(tok) if selected_lang == 'uz' else tok.lower()
            if not SINGLE_WORD_CLEAN_RE.match(tok):
                continue
            if tok_norm not in word_forms_map:
                d_entry = dict_by_word.get(tok_norm) if DICTIONARY_PUBLIC else None
                d_tr = d_entry.get('translation') if (d_entry and d_entry.get('public_visible', True)) else None
                d_pos = d_entry.get('pos') if d_entry else None
                d_src = d_entry.get('dictionary_source') if d_entry else None
                word_forms_map[tok_norm] = {
                    "word": tok,
                    "group": grp,
                    "pos": d_pos or POS_UNKNOWN,
                    "books": Counter(),
                    "dict_translation": d_tr,
                    "dict_source": d_src if d_tr else None
                }
            word_forms_map[tok_norm]["books"][book] += 1
            if found_eq_words:
                eq_kind = 'tasdiqlangan' if is_s1_equivalent else 'AI-taklif'
                for ew in found_eq_words:
                    book_translations_by_form[tok_norm][(ew, eq_kind)] += 1
            else:
                book_translations_by_form[tok_norm][('ekvivalent aniqlanmagan', '')] += 1

            p_val = p_src_val
            if p_val:
                book_pages_by_form[tok_norm].add(p_val)

        if is_confirmed:
            status_label = "Tasdiqlangan"
            is_open = True
            ranking_weight = 1 if is_s1_equivalent else 2
        else:
            status_label = "Tarjima gapi hali tadqiqotchi tomonidan tasdiqlanmagan"
            is_open = False
            ranking_weight = 3

        matched_corpus_sentences.append({
            "id": sid,
            "book": book,
            "direction": "uz-en" if selected_lang == 'uz' else "en-uz",
            "lang": selected_lang,
            "page_source": page_src_str,
            "page_target": page_tgt_str,
            "source_label": source_label,
            "target_label": target_label,
            "alignment_status": aln_status,
            "is_open": is_open,
            "ranking_weight": ranking_weight,
            "sort_page": p_src_val or 9999,
            "source_raw": orig_text,
            "source_highlighted": source_highlighted,
            "target_raw": trans_text,
            "target_highlighted": target_highlighted,
            "target_status_label": status_label,
            "has_equivalent": bool(found_eq_words),
            "match_spans": search_spans,
            # explicit sides: the side that contains the query is always shown first
            "query_in_orig": query_in_orig,
            "src_page": p_src_val,
            "tgt_page": p_tgt_val,
            "query_lang": selected_lang,
            "query_raw": orig_text if query_in_orig else trans_text,
            "query_highlighted": source_highlighted if query_in_orig else target_highlighted,
            "other_raw": trans_text if query_in_orig else orig_text,
            "other_highlighted": target_highlighted if query_in_orig else source_highlighted,
            "query_page": p_src_val if query_in_orig else p_tgt_val,
            "other_page": p_tgt_val if query_in_orig else p_src_val,
            "equiv_confirmed": is_s1_equivalent
        })

    # Ranking per PART 7.1:
    # 1. confirmed pairs with confirmed equivalents (ranking_weight=1)
    # 2. confirmed pairs (ranking_weight=2)
    # 3. automatic pairs (ranking_weight=3)
    # Within each group: by book order and page
    matched_corpus_sentences.sort(key=lambda s: (s['ranking_weight'], 0 if s['book'] == 'cholpon' else 1, s['sort_page']))

    # Format Words list
    words_list = []
    group_order = {'exact': 1, 'inflected': 2, 'derived': 3, 'compound': 4}
    for w_info in sorted(word_forms_map.values(), key=lambda x: (group_order.get(x['group'], 5), -sum(x['books'].values()), x['word'])):
        tot = sum(w_info["books"].values())
        w_norm = uz_norm(w_info["word"]) if selected_lang == 'uz' else w_info["word"].lower()

        tr_counts = book_translations_by_form.get(w_norm, Counter())
        if tot > 0:
            if tr_counts:
                tr_items = [f"{w} ({c} marta, {kind})" for (w, kind), c in tr_counts.most_common(4) if w != 'ekvivalent aniqlanmagan']
                book_tr_str = "; ".join(tr_items) if tr_items else "ekvivalent aniqlanmagan"
            else:
                book_tr_str = "ekvivalent aniqlanmagan"
        else:
            book_tr_str = "korpusda uchramaydi"

        words_list.append({
            "word": w_info["word"],
            "group": w_info["group"],
            "pos": w_info["pos"],
            "book_counts": dict(w_info["books"]),
            "total_occurrences": tot,
            "dict_translation": w_info["dict_translation"],
            "dict_source": w_info["dict_source"],
            "book_translation_status": book_tr_str,
            # structured form of the same data, for localized display
            "book_translations": [{"text": w, "count": c, "kind": kind}
                                  for (w, kind), c in tr_counts.most_common(4) if w != 'ekvivalent aniqlanmagan']
        })

    # Section 2 Collocations
    if is_multi:
        # Collocation query mode: the query itself is the target collocation
        # Cross check against 1.1 seeds and reference base
        q_norm_c = uz_norm(q).lower()
        matched_seed_row = None
        # Check if query matches 1.1 seeds
        status_term = "kollokatsiya nomzodi"
        pattern_term = guess_query_pattern(q, selected_lang)
        eq_form_term = "kollokatsiya"
        
        # Check reviewed status from confirmed segments
        best_ex = None
        for s in matched_corpus_sentences:
            if s.get('alignment_status') == 'tasdiqlangan':
                best_ex = s
                break
        if not best_ex and matched_corpus_sentences:
            best_ex = matched_corpus_sentences[0]

        corpus_candidates = [{
            "collocation": q,
            "searched_word": q,
            "pattern": pattern_term,
            "source_badge": "1.1-paragraf nomzodi (tadqiqotchi)" if muqobil_s1_map else "Avtomatik nomzod — lingvistik tekshiruvdan o‘tmagan",
            "sentences_count": len(matched_corpus_sentences),
            "occurrences_count": len(matched_corpus_sentences),
            "corpus_frequency": len(matched_corpus_sentences),
            "books": list({s['book'] for s in matched_corpus_sentences}),
            "muqobil_distribution": [f"{k} ({v['count']})" for k, v in muqobil_s1_map.items()],
            "example": {
                "source_sentence": best_ex["query_raw"] if best_ex else "",
                "source_highlighted": best_ex["query_highlighted"] if best_ex else "",
                "target_sentence": best_ex.get("other_raw", "") if best_ex else "",
                "target_highlighted": best_ex.get("other_highlighted", "") if best_ex else "",
                "book": best_ex["book"] if best_ex else "",
                "page_source": best_ex.get("query_page", "") if best_ex else "",
                "page_target": best_ex.get("other_page", "") if best_ex else "",
                "query_lang": selected_lang,
                "is_open": bool(best_ex.get("is_open")) if best_ex else False
            }
        }]
        admin_candidates = []
        reference_collocations = []
    else:
        corpus_candidates, admin_candidates = extract_corpus_collocation_candidates(matched_corpus_sentences, q, selected_lang)
        reference_collocations = []
        if selected_lang == 'en':
            q_low = q.lower()
            q_family_tokens = {q_low} | set(get_wordnet_family(q_low))
            if q_low in ENGLISH_IRREGULAR_PAIRS:
                q_family_tokens.update(ENGLISH_IRREGULAR_PAIRS[q_low])
            for it in active_collocations:
                en_colloc = it.get('english', '').lower()
                tokens = set(TOKEN_EN_RE.findall(en_colloc))
                if (tokens & q_family_tokens) or any(match_english_word_family(q, t) for t in tokens):
                    uz_variants = it.get('uzbek_variants') or []
                    if not uz_variants and it.get('uzbek'):
                        uz_variants = [{
                            "text": it.get('uzbek'),
                            "source_class": it.get('class', 'AI-taklif'),
                            "status": "AI-taklif (tekshirilmagan)"
                        }]
                    ex = _clean_reference_example(it)
                    reference_collocations.append({
                        "collocation": it.get('english'),
                        "searched_word": q,
                        "pattern": it.get('pattern') or "—",
                        "source_badge": f"Ma’lumotnoma: {it.get('sourceMeta') or it.get('sourceBook') or 'Akademik ma’lumotnoma'}",
                        # Only real counts from this corpus. The stored "freq"/"miScore" values of the
                        # reference base were not computed from any corpus and are never shown.
                        "corpus_frequency": int(it.get('corpus_occurrences') or 0),
                        "sentences_count": len(it.get('corpus_segments') or []),
                        "occurrences_count": int(it.get('corpus_occurrences') or 0),
                        "uzbek_translation": it.get('uzbek'),
                        "uzbek_variants": uz_variants,
                        "uzbek_label": it.get('review_status') or "AI-taklif (tekshirilmagan)",
                        "example": ex
                    })

    collocations_list = corpus_candidates + reference_collocations

    # Build Muqobil Summary (PART 1.3 & PART 4.A)
    source_1_items = []
    for eq_text, eq_data in sorted(muqobil_s1_map.items(), key=lambda x: -x[1]['count']):
        source_1_items.append({
            "equivalent": eq_text,
            "count": eq_data["count"],
            "form": eq_data["form"],
            "pages": ", ".join(sorted(eq_data["pages"])),
            "source_page": eq_data.get("src_page"),
            "target_page": eq_data.get("tgt_page"),
            "segment_ids": eq_data["sids"],
            "first_segment_id": eq_data["sids"][0] if eq_data["sids"] else None,
            "source_type": 1,
            "source_label": "Kitobdagi tarjima — tasdiqlangan",
            "style": "solid"
        })

    source_2_items = []
    for eq_text, eq_data in sorted(muqobil_s2_map.items(), key=lambda x: -x[1]['count']):
        source_2_items.append({
            "equivalent": eq_text,
            "count": eq_data["count"],
            "form": eq_data["form"],
            "pages": ", ".join(sorted(eq_data["pages"])),
            "source_page": eq_data.get("src_page"),
            "target_page": eq_data.get("tgt_page"),
            "segment_ids": eq_data["sids"],
            "first_segment_id": eq_data["sids"][0] if eq_data["sids"] else None,
            "source_type": 2,
            "source_label": "Kitobdagi tarjima — AI-taklif (tekshirilmagan)",
            "style": "dashed"
        })

    # Source 3: Dictionary
    source_3_items = []
    lookup_term = uz_norm(q) if selected_lang == 'uz' else q.lower()
    dict_hit = dict_by_word.get(lookup_term) if DICTIONARY_PUBLIC else None
    if dict_hit and dict_hit.get('public_visible', True):
        d_tr = dict_hit.get('translation')
        if d_tr:
            source_3_items.append({
                "equivalent": d_tr,
                "dictionary_source": dict_hit.get('dictionary_source'),
                "source_label": "Lug‘atdagi tarjima"
            })

    # Source 4: Reference collocation base
    source_4_items = []
    for rc in reference_collocations:
        source_4_items.append({
            "collocation": rc.get('collocation'),
            "uzbek_translation": rc.get('uzbek_translation'),
            "class_label": "KORPUS" if "Korpus" in rc.get('source_badge', '') else "AI-taklif",
            "source_label": "Ma’lumotnomadagi muqobil"
        })

    total_unconfirmed = len([s for s in matched_corpus_sentences if s.get('alignment_status') != 'tasdiqlangan'])
    source_1_empty = (len(source_1_items) == 0)
    empty_msg = f"Kitobdagi tarjima hali tasdiqlanmagan: {total_unconfirmed} ta uchrash tekshiruv navbatida" if source_1_empty else None

    muqobil_summary = {
        "source_1_confirmed": source_1_items,
        "source_2_ai_proposal": source_2_items,
        "source_3_dictionary": source_3_items,
        "source_4_reference": source_4_items,
        "source_1_empty": source_1_empty,
        "empty_message": empty_msg,
        "unconfirmed_count": total_unconfirmed
    }

    # Pagination for Section 3
    limit = min(max(1, limit), 1000)
    total_sentences = len(matched_corpus_sentences)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_sentences = matched_corpus_sentences[start_idx:end_idx]

    return {
        "query": q,
        "is_collocation_query": is_multi,
        "detected_lang": detected_lang,
        "selected_lang": selected_lang,
        "is_ambiguous": is_ambiguous,
        "summary": {
            "total_word_forms": len(words_list),
            "corpus_occurrences": sum(w["total_occurrences"] for w in words_list) if not is_multi else total_sentences,
            "total_sentences": total_sentences,
            "collocations_count": len(collocations_list),
            "corpus_candidates_count": len(corpus_candidates),
            "reference_collocations_count": len(reference_collocations)
        },
        "muqobil_summary": muqobil_summary,
        "words": words_list,
        "collocations": collocations_list,
        "corpus_candidates": corpus_candidates,
        "admin_candidates": admin_candidates,
        "reference_collocations": reference_collocations,
        "corpus_sentences": paginated_sentences,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_sentences": total_sentences,
            "total_pages": max(1, (total_sentences + limit - 1) // limit)
        }
    }

"""
word_family.py - Word Family & Morphological Matching Module for TILCOR (Step 03)
Compliant with METHODS.md, Section 1 & 2 of TILCOR_03-1.md, and EQUIVALENT PRINCIPLE.
Strict Uzbek letter normalization with uz_norm() and offset mapping,
Uzbek morphological stemming, consonant alternation, vowel drop, suffix chaining,
and English lemma, derivation, and compound matching using NLTK 3.8.1+.
"""

import re
import sys
from typing import Dict, List, Set, Tuple, Optional, Any

# NLTK integration
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet as wn

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

# =============================================================================
# 1. TRANSLITERATION & OFFICIAL UZBEK NORMALIZATION (uz_norm)
# =============================================================================

APOSTROPHE_CHARS_SET = set("ʻ‘'`’´ʼ\u02bb\u2018\u0027\u0060\u2019\u00b4\u02bc")
APOSTROPHE_CHARS_STR = "ʻ‘'`’´ʼ\u02bb\u2018\u0027\u0060\u2019\u00b4\u02bc"

# Cyrillic vowels for 'e' -> 'ye' rule
CYRILLIC_VOWELS = set("аеёиоуэюяўАЕЁИОУЭЮЯЎ")

CYRILLIC_TO_LATIN_BASE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
    'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
    'х': 'x', 'ч': 'ch', 'ш': 'sh', 'ъ': 'ʼ', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya', 'ё': 'yo',
    'ў': 'oʻ', 'ғ': 'gʻ', 'қ': 'q', 'ҳ': 'h'
}

RUSSIAN_ONLY_CHARS = set("ыщ")

from functools import lru_cache

@lru_cache(maxsize=131072)
def _uz_norm_str(text: str) -> str:
    res, _ = _uz_norm_with_offsets(text)
    return res

def _uz_norm_with_offsets(text: str) -> Tuple[str, List[int]]:
    # Phase 1: Handle Cyrillic to Latin with character-by-character tracking
    chars_with_idx = []
    n = len(text)
    i = 0
    while i < n:
        c = text[i]
        c_low = c.lower()
        
        # Check 'e' / 'Е'
        if c_low == 'е':
            is_start_or_vowel = (i == 0) or (text[i-1] in ' \t\n\r"\'(«[—–-.,!?;:') or (text[i-1] in CYRILLIC_VOWELS) or (text[i-1] in 'ъЪ')
            lat = 'ye' if is_start_or_vowel else 'e'
            for lc in lat:
                chars_with_idx.append((lc, i))
            i += 1
            continue
            
        # Check 'ц' / 'Ц'
        if c_low == 'ц':
            is_after_vowel = (i > 0 and text[i-1] in CYRILLIC_VOWELS)
            lat = 'ts' if is_after_vowel else 's'
            for lc in lat:
                chars_with_idx.append((lc, i))
            i += 1
            continue

        if c_low in CYRILLIC_TO_LATIN_BASE:
            lat = CYRILLIC_TO_LATIN_BASE[c_low]
            for lc in lat:
                chars_with_idx.append((lc, i))
            i += 1
            continue

        # Otherwise keep character as is (lowercase)
        chars_with_idx.append((c_low, i))
        i += 1

    # Phase 2: Handle o‘/g‘ vs tutuq belgisi on Latin characters
    norm_chars = []
    offsets = []
    m = len(chars_with_idx)
    j = 0
    while j < m:
        ch, orig_i = chars_with_idx[j]
        
        if ch in APOSTROPHE_CHARS_SET:
            prev_char = norm_chars[-1] if norm_chars else None
            if prev_char in ('o', 'g'):
                # Rule a: after o or g -> ʻ (U+02BB)
                norm_chars.append('\u02bb')
                offsets.append(orig_i)
            else:
                # Rule b: after any other letter -> ʼ (U+02BC)
                norm_chars.append('\u02bc')
                offsets.append(orig_i)
            j += 1
            continue

        # Rule d: collapse spaces
        if ch == ' ' and norm_chars and norm_chars[-1] == ' ':
            j += 1
            continue

        norm_chars.append(ch)
        offsets.append(orig_i)
        j += 1

    return "".join(norm_chars), offsets

def uz_norm(text: str, return_offsets: bool = False):
    """
    Normalizes Uzbek text following TILCOR_03-1 Part 1:
    1. Letters o‘ / g‘: after 'o' or 'g' (any case), apostrophe -> ʻ (U+02BB)
    2. Tutuq belgisi: after any other letter, apostrophe -> ʼ (U+02BC)
    3. Cyrillic Uzbek -> Latin using official correspondence
    4. Lowercase, collapse repeated spaces.
    5. Returns (normalized_text, offset_map) where offset_map[norm_idx] = orig_idx.
    """
    if not text:
        return ("", []) if return_offsets else ""
    if return_offsets:
        return _uz_norm_with_offsets(text)
    return _uz_norm_str(text)

def clean_word(word: str) -> str:
    """Canonical cleaned word representation using uz_norm."""
    return uz_norm(word.strip())

def normalize_apostrophes(text: str) -> str:
    """Backward compatibility helper mapping all apostrophes to U+02BB/U+02BC."""
    return uz_norm(text)

APOSTROPHE_CHARS = APOSTROPHE_CHARS_STR

# =============================================================================
# 2. UZBEK MORPHOLOGY & STEMMING
# =============================================================================

VOWEL_DROP_PAIRS = {
    "koʻngil": "koʻngl",
    "kongil": "kongl",
    "oʻgʻil": "oʻgʻl",
    "ogil": "ogl",
    "burun": "burn",
    "qorin": "qorn",
    "shahar": "shahr",
    "boʻyin": "boʻyn",
    "ogʻiz": "ogʻz",
    "bagʻir": "bagʻr",
    "singil": "singl",
    "aql": "aql",
    "fikr": "fikr",
    "hukm": "hukm",
    "ism": "ism"
}

PLURAL_SUFFIXES = ['lar']
CASE_SUFFIXES = ['ning', 'dan', 'da', 'ni', 'ga', 'ka', 'qa']
POSSESSIVE_SUFFIXES = ['imiz', 'ingiz', 'lari', 'im', 'ing', 'si', 'i', 'm', 'ng']
DERIVATIONAL_SUFFIXES = ['dor', 'kor', 'bon', 'parvar', 'namo', 'siz', 'lik', 'chi', 'cha', 'li', 'iy', 'viy']
VERB_SUFFIXES = [
    'moqda', 'yapti', 'yapmiz', 'yapman', 'yapsan', 'yapgan', 'dilar', 
    'gancha', 'ilgan', 'ilsa', 'ildi', 'ilmoq', 'ishga', 'shga',
    'gan', 'kan', 'qan', 'moq', 'mak', 'dim', 'ding', 'dilar', 'di', 
    'adi', 'ydi', 'ish', 'uv', 'mas', 'maydi', 'aylik', 'ay'
]
COMPARATIVE_SUFFIXES = ['roq', 'dek', 'day', 'cha']

ALL_UZBEK_SUFFIXES = sorted(
    list(set(CASE_SUFFIXES + POSSESSIVE_SUFFIXES + PLURAL_SUFFIXES + DERIVATIONAL_SUFFIXES + VERB_SUFFIXES + COMPARATIVE_SUFFIXES)),
    key=lambda x: len(x),
    reverse=True
)

def strip_uzbek_inflections(word: str) -> str:
    """Strips outer inflections from a candidate word to find its root."""
    w = uz_norm(word)
    changed = True
    while changed and len(w) > 3:
        changed = False
        for sfx in ALL_UZBEK_SUFFIXES:
            if w.endswith(sfx) and len(w) - len(sfx) >= 3:
                w = w[:-len(sfx)]
                changed = True
                break
    return w

def get_uzbek_stem_variants(root: str) -> List[str]:
    """Returns possible stem forms considering alternation and vowel drops."""
    norm = uz_norm(root)
    base_root = strip_uzbek_inflections(norm)
    
    candidates = {norm, base_root}
    stems = set()
    
    for r in candidates:
        stems.add(r)
        # Consonant alternation: k -> g (yurak -> yurag), q -> gʻ (qishloq -> qishlogʻ)
        if r.endswith('k'):
            stems.add(r[:-1] + 'g')
        elif r.endswith('q'):
            stems.add(r[:-1] + "gʻ")
            
        # Vowel drop
        if r in VOWEL_DROP_PAIRS:
            contracted = VOWEL_DROP_PAIRS[r]
            stems.add(contracted)
            if contracted.endswith('k'):
                stems.add(contracted[:-1] + 'g')
            elif contracted.endswith('q'):
                stems.add(contracted[:-1] + "gʻ")
                
        for full, contr in VOWEL_DROP_PAIRS.items():
            if r == contr or r.startswith(contr):
                stems.add(full)
                stems.add(contr)
                
    return list(stems)

def validate_uzbek_suffix_chain(suffix_str: str) -> Tuple[bool, str]:
    """
    Validates if a suffix string is a legitimate chain of Uzbek suffixes.
    Returns (is_valid, category) where category is 'exact', 'inflected', or 'derived'.
    """
    if not suffix_str:
        return (True, 'exact')
        
    s = suffix_str
    
    # Direct match on derivational
    if s in DERIVATIONAL_SUFFIXES:
        return (True, 'derived')
        
    has_derivational = False
    
    # Iterative strip of legitimate suffix chain
    changed = True
    while s and changed:
        changed = False
        for sfx in ALL_UZBEK_SUFFIXES:
            if s.endswith(sfx):
                if sfx in DERIVATIONAL_SUFFIXES:
                    has_derivational = True
                s = s[:-len(sfx)]
                changed = True
                break
                
    if not s:
        return (True, 'derived' if has_derivational else 'inflected')
    return (False, 'invalid')

def match_uzbek_word_family(query: str, candidate_word: str) -> Optional[Tuple[str, str]]:
    q_clean = uz_norm(query)
    c_clean = uz_norm(candidate_word)
    
    if len(q_clean) < 3 or len(c_clean) < 3:
        if q_clean == c_clean:
            return ('exact', c_clean)
        return None
        
    if q_clean == c_clean:
        return ('exact', c_clean)
        
    # Compound / Paired word check (e.g. yurak-bagʻir, ochiq-yurak)
    if '-' in c_clean or ' ' in c_clean:
        parts = re.split(r'[-\s]+', c_clean)
        for part in parts:
            if match_uzbek_word_family(q_clean, part):
                return ('compound', c_clean)
                
    stem_variants = get_uzbek_stem_variants(q_clean)
    
    for stem in stem_variants:
        if c_clean == stem:
            return ('inflected', c_clean)
        if c_clean.startswith(stem):
            remainder = c_clean[len(stem):]
            is_valid, cat = validate_uzbek_suffix_chain(remainder)
            if is_valid:
                return (cat, c_clean)
                
    # Also check reverse: if candidate is base root and query is inflected (e.g. query='qarorlar', cand='qaror')
    cand_variants = get_uzbek_stem_variants(c_clean)
    for c_stem in cand_variants:
        if q_clean.startswith(c_stem):
            rem = q_clean[len(c_stem):]
            is_valid, cat = validate_uzbek_suffix_chain(rem)
            if is_valid:
                return ('inflected', c_clean)
                
    return None

# =============================================================================
# 3. ENGLISH MORPHOLOGY & WORD FAMILY
# =============================================================================

ENGLISH_IRREGULAR_PAIRS = {
    'see': {'saw', 'seen', 'sight'},
    'saw': {'see', 'seen', 'sight'},
    'decide': {'decision', 'decisive', 'decidedly', 'decisions', 'decided'},
    'decision': {'decide', 'decisive', 'decidedly', 'decisions', 'decided'},
    'heart': {'hearts', 'heartless', 'heartfelt', 'hearty', 'heartily', 'cold-hearted', 'wholeheartedly'},
    'cold': {'colder', 'coldest', 'coldly', 'coldness', 'cold-hearted'},
    'take': {'took', 'taken', 'takes', 'taking'},
    'make': {'made', 'makes', 'making'},
    'give': {'gave', 'given', 'gives', 'giving'},
    'go': {'went', 'gone', 'goes', 'going'}
}

from functools import lru_cache

@lru_cache(maxsize=8192)
def get_wordnet_family(word: str) -> Set[str]:
    """Retrieves strictly morphological family (derivations sharing root/stem). Never synonyms."""
    family = {word}
    w_low = word.lower()
    w_stem = stemmer.stem(w_low)
    try:
        for syn in wn.synsets(w_low):
            for l in syn.lemmas():
                if l.name().lower() == w_low:
                    for deriv in l.derivationally_related_forms():
                        d = deriv.name().lower().replace('_', '-')
                        if w_low in d or stemmer.stem(d) == w_stem:
                            family.add(d)
                    for pert in l.pertainyms():
                        p = pert.name().lower().replace('_', '-')
                        if w_low in p or stemmer.stem(p) == w_stem:
                            family.add(p)
    except Exception:
        pass
    if w_low in ENGLISH_IRREGULAR_PAIRS:
        family.update(ENGLISH_IRREGULAR_PAIRS[w_low])
    return family

@lru_cache(maxsize=32768)
def match_english_word_family(query: str, candidate_word: str) -> Optional[Tuple[str, str]]:
    q_low = query.strip().lower()
    c_low = candidate_word.strip().lower()
    
    if q_low == c_low:
        return ('exact', c_low)
        
    # Compound check
    if '-' in c_low or ' ' in c_low:
        parts = re.split(r'[-\s]+', c_low)
        for part in parts:
            if match_english_word_family(q_low, part):
                return ('compound', c_low)
                
    # Lemmatizer check
    q_lemma_n = lemmatizer.lemmatize(q_low, pos='n')
    q_lemma_v = lemmatizer.lemmatize(q_low, pos='v')
    c_lemma_n = lemmatizer.lemmatize(c_low, pos='n')
    c_lemma_v = lemmatizer.lemmatize(c_low, pos='v')
    
    if (q_lemma_n == c_lemma_n) or (q_lemma_v == c_lemma_v) or (q_lemma_n == c_lemma_v) or (q_lemma_v == c_lemma_n):
        return ('inflected', c_low)
        
    # Stemmer check
    if stemmer.stem(q_low) == stemmer.stem(c_low) and len(stemmer.stem(q_low)) >= 3:
        return ('inflected', c_low)

    # WordNet family lookup
    q_family = get_wordnet_family(q_low)
    if c_low in q_family:
        return ('inflected' if c_low in ['saw', 'seen', 'decided', 'decides'] else 'derived', c_low)
        
    # Common prefixes
    for prefix in ['un', 'in', 'im', 'dis', 'fore', 're', 'pre', 'non']:
        if c_low.startswith(prefix) and len(c_low) - len(prefix) >= 3:
            sub = c_low[len(prefix):]
            if sub in q_family or sub == q_low:
                return ('compound', c_low)

    # Common suffixes
    if q_low in c_low:
        rem = c_low.replace(q_low, '')
        if rem in ['less', 'y', 'ily', 'ed', 'en', 'ening', 'ful', 'ness', 'able', 'er', 'est', 'ly']:
            return ('derived', c_low)
        elif len(rem) >= 2:
            return ('compound', c_low)

    # Substring in compound
    for f in q_family:
        if len(f) >= 4 and f in c_low and len(c_low) > len(f) + 2:
            return ('compound', c_low)
            
    return None

# =============================================================================
# 4. LANGUAGE DETECTION (Part 1 Section 4)
# =============================================================================

RUSSIAN_ONLY_CHARS = set("ыщэьЫЩЭЬ")
COMMON_RUSSIAN_WORDS = {
    'привет', 'здравствуйте', 'спасибо', 'пожалуйста', 'хорошо', 'да', 'нет',
    'что', 'как', 'где', 'когда', 'почему', 'зачем', 'кто', 'куда', 'откуда',
    'это', 'этот', 'эта', 'эти', 'тот', 'все', 'всё', 'быть', 'есть', 'был',
    'слово', 'слова', 'текст', 'книга', 'перевод', 'словарь', 'язык', 'человек'
}
UZBEK_SPECIFIC_CHARS = re.compile(rf"[oOgG][{APOSTROPHE_CHARS_STR}]|[\u02bb\u02bc]|[ўғқҳЎҒҚҲ]")

def detect_query_language(query: str, uzbek_lexicon: Set[str] = None, english_lexicon: Set[str] = None) -> str:
    """
    Detects language following TILCOR_03-1 Part 1 Section 4:
    - Cyrillic Russian only letters (ы, щ, э, ь) mean Russian -> 'ru'
    - Uzbek letters (oʻ, gʻ, ʼ, ў, ғ, қ, ҳ) -> 'uz'
    - WordNet synset or English words -> 'en'
    - Otherwise 'uz' or 'ambiguous'.
    """
    q = query.strip()
    if not q:
        return 'unknown'
        
    q_low = q.lower()
    
    # 1. Russian only letters check (Section 4: Letters found only in Russian: ы, щ, э, ь)
    # Note: If word has Uzbek Cyrillic letters (ў, ғ, қ, ҳ) or tutuq (ъ), it takes precedence as Uzbek
    has_uzbek_cyrillic = any(c in q_low for c in ['ў', 'ғ', 'қ', 'ҳ'])
    if not has_uzbek_cyrillic:
        if any(c in q_low for c in RUSSIAN_ONLY_CHARS) or q_low in COMMON_RUSSIAN_WORDS:
            return 'ru'
        # Any pure Cyrillic query that isn't recognized in Uzbek
        if any('\u0400' <= c <= '\u04FF' for c in q) and q_low not in ('юрак', 'боғ', 'маъно', 'таълим', 'ота', 'она', 'кун', 'тун', 'кўз'):
            # If word contains typical Russian endings like -ость, -ние, -ство
            if any(q_low.endswith(end) for end in ('ость', 'ние', 'ство', 'тель', 'ский', 'ный', 'ого', 'его')):
                return 'ru'

    # 2. Uzbek specific letters
    if UZBEK_SPECIFIC_CHARS.search(q) or has_uzbek_cyrillic:
        return 'uz'

    q_clean = clean_word(q)
    if q_clean == 'bor':
        return 'ambiguous'

    # 3. Check English lexicons / WordNet
    is_uz = False
    is_en = False
    
    if uzbek_lexicon and q_clean in uzbek_lexicon:
        is_uz = True
    if english_lexicon and q_low in english_lexicon:
        is_en = True
        
    if is_uz and is_en:
        return 'ambiguous'
    if is_uz:
        return 'uz'
    if is_en:
        return 'en'
        
    try:
        words = [w for w in re.split(r"\s+", q_low) if w]
        if len(words) >= 2:
            en_words_count = 0
            for w in words:
                if w in ('the', 'a', 'an', 'in', 'of', 'to', 'for', 'at', 'by', 'as', 'with', 'from', 'on'):
                    en_words_count += 1
                elif wn.synsets(w) and w not in ('bor', 'kel', 'ket', 'kun', 'bol', 'ol', 'ber', 'qil', 'sol'):
                    en_words_count += 1
            if en_words_count >= len(words):
                return 'en'

        if wn.synsets(q_low):
            # Exclude short false positives that are common Uzbek words
            if q_low not in ('bor', 'kel', 'ket', 'yurak', 'kun', 'tosh', 'qul', 'bol'):
                return 'en'
    except Exception:
        pass
        
    return 'uz'


# =============================================================================
# STEM KEY FOR WORD ALIGNMENT AND THE LEXICAL TABLE
# =============================================================================
_ALIGN_FINITE = ('moqda', 'yapti', 'yapman', 'yapsan', 'yapmiz', 'maydi', 'mayman', 'maysan', 'madilar', 'madim',
                 'madingiz', 'madi', 'dilar', 'dingiz', 'dim', 'ding', 'dik', 'di', 'ti', 'adilar', 'adi', 'ydi',
                 'aman', 'asan', 'amiz', 'ishdi')
_ALIGN_CASE = ('ning', 'gacha', 'dan', 'ga', 'ka', 'qa', 'da', 'ni')
_ALIGN_POSS = ('imiz', 'ingiz', 'lari', 'miz', 'ngiz', 'si', 'im', 'ing', 'i', 'm')
_ALIGN_PLUR = ('lar',)
_ALIGN_NONFINITE = ('yotgan', 'yotib', 'gancha', 'guncha', 'gach', 'gan', 'kan', 'qan', 'moqchi', 'moq', 'mak',
                    'mas', 'ishib', 'ish', 'ib', 'sa', 'ar')
_ALIGN_VOWEL_DROP = {'koʻngl': 'koʻngil', 'oʻgʻl': 'oʻgʻil', 'burn': 'burun', 'qorn': 'qorin', 'ogʻz': 'ogʻiz',
                     'bagʻr': 'bagʻir', 'shahr': 'shahar', 'singl': 'singil', 'boʻyn': 'boʻyin', 'oʻrn': 'oʻrin',
                     'ayr': 'ayir', 'ism': 'ism'}


def _letters_len(s: str) -> int:
    return sum(1 for ch in s if ch.isalpha() and ch not in 'ʻʼ‘’')


def uz_align_stem(word: str) -> str:
    """Conservative stem key of an Uzbek word form (links the forms of one word; it is not a lemma).
    A finite verb ending is removed first (berdi -> ber, bermadi -> ber); otherwise at most one case,
    one possessive, one plural and one non-finite ending are removed. At least 3 letters are kept.
    Dropped vowels are restored (koʻngli -> koʻngil) and the k~g, q~gʻ alternation is undone before a
    vowel suffix (yuragi -> yurak, qishlogʻi -> qishloq), but not in the digraph ng (rangi -> rang)."""
    w = uz_norm((word or '').lower())

    def strip(form, group):
        for sfx in sorted(group, key=len, reverse=True):
            if form.endswith(sfx) and _letters_len(form[:-len(sfx)]) >= 3:
                return form[:-len(sfx)], sfx
        return form, ''

    w2, sfx = strip(w, _ALIGN_FINITE)
    if sfx:
        if w2.endswith('ma') and _letters_len(w2) > 4:
            w2 = w2[:-2]                      # negation: ber-ma-di
        return _ALIGN_VOWEL_DROP.get(w2, w2)
    last = ''
    for group in (_ALIGN_CASE, _ALIGN_POSS, _ALIGN_PLUR, _ALIGN_POSS, _ALIGN_NONFINITE):
        w, sfx = strip(w, group)
        if sfx:
            last = sfx
    if w in _ALIGN_VOWEL_DROP:
        return _ALIGN_VOWEL_DROP[w]
    if last and last[0] in 'aeiou' and not w.endswith('ng') and _letters_len(w) > 3:
        if w.endswith('gʻ'):
            w = w[:-2] + 'q'
        elif w.endswith('g'):
            w = w[:-1] + 'k'
    return w

import re
import json
from collections import Counter, defaultdict
from word_family import uz_norm, match_uzbek_word_family, match_english_word_family, lemmatizer, clean_word

# Proper names list to exclude
KNOWN_PROPER_NAMES = {
    'zebi', 'enaxon', 'razzoq', 'miryoqub', 'akbarali', 'poshshaxon', 'xadichaxon',
    'saltanat', 'olmasxon', 'o‘lmasxon', 'oʻlmasxon', 'eshon', 'eshonbobo', 'domla',
    'mulla', 'qurbon', 'salim', 'fotima', 'zuhra', 'santiago', 'manolin', 'perico',
    'martin', 'rogelio', 'pedrico', 'cienfuegos', 'havana', 'afrika', 'amerika',
    'cho‘lpon', 'cholpon', 'hemingway', 'xeminguey', 'g‘ofurov', 'gofurov', 'fort',
    'sharq', 'toshkent', 'samarqand', 'farg‘ona', 'andijon', 'qo‘qon', 'namangan'
}

# Function/speech words to exclude
EXCLUDED_VERBS = {'dedi', 'deb', 'derdi', 'der', 'demoq', 'dedilar', 'degan'}
EXCLUDED_WORDS = {
    'bu', 'u', 'va', 'bilan', 'ham', 'uchun', 'deb', 'esa', 'kabi', 'lekin', 'ammo', 'biroq',
    'yoki', 'bir', 'shu', 'men', 'sen', 'biz', 'siz', 'ular', 'o‘sha', 'oʻsha', "o'sha",
    'o‘z', 'oʻz', "o'z", 'o‘zi', 'oʻzi', "o'zi", 'uning', 'uningda', 'ularning', 'mening',
    'sening', 'bizning', 'sizning', 'da', 'dan', 'ga', 'ni', 'ning', 'edi', 'bo‘ldi',
    'boʻldi', "bo'ldi", 'bo‘lgan', 'boʻlgan', "bo'lgan", 'ekan', 'emish', 'yo‘q', 'yoʻq',
    "yo'q", 'bor', 'qildi', 'qilgan', 'etdi', 'so‘ng', 'keyin', 'yana', 'faqat', 'hatto',
    'chunki', 'go‘yo', 'hali', 'endi', 'birga', 'ko‘ra', 'oldin', 'tomon', 'orasida',
    'bo‘yicha', 'ka', 'qa', 'narsa', 'narsani', 'narsaga', 'narsada', 'narsadan', 'har',
    'hamma', 'barcha', 'qadar', 'qaysi', 'qanaqa', 'qanday', 'hech', 'qachon', 'allaqachon'
}

# Common Uzbek verb stems that resolve to -moq
COMMON_VERB_STEMS = {
    'ber': 'bermoq', 'ol': 'olmoq', 'bo‘l': 'bo‘lmoq', 'boʻl': 'bo‘lmoq', 'qil': 'qilmoq',
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
    'cho‘k': 'cho‘kmoq', 'uch': 'uchmoq', 'yot': 'yotmoq', 'ot': 'otmoq', 'yet': 'yetmoq'
}

# Common nouns that should NEVER be cut by suffix stripping
PROTECTED_NOUNS = {
    'tashvish', 'xurush', 'olqish', 'qarg‘ish', 'qaror', 'ko‘ngil', 'yurak', 'yurag',
    'qishloq', 'qishlog‘', 'dil', 'dard', 'qalb', 'alam', 'hasrat', 'muhabbat', 'ishq',
    'sevgi', 'armon', 'orzu', 'umid', 'xayol', 'fikr', 'aql', 'sabot', 'saboz', 'bardosh',
    'matonat', 'jasorat', 'shijoat', 'g‘azab', 'qahr', 'nafrat', 'hasad', 'rashk',
    'shubha', 'gumon', 'ishonch', 'e’tiqod', 'marhamat', 'shafqat', 'rahmdillik',
    'tinchlik', 'xotirjamlik', 'sir', 'gap', 'so‘z', 'nasihat', 'pand', 'chol'
}

def resolve_uzbek_lemma_and_pos(token: str, surface_forms: Counter = None) -> tuple:
    """
    Resolves token to (lemma, pos, pattern_role).
    Returns (lemma, pos, role) where pos in ('ot', 'fe’l', 'sifat', 'ravish', 'nomalum').
    """
    raw = token.lower().strip(" 'ʻʼ‘-")
    norm = uz_norm(raw).replace('ʻ', '‘').replace('ʼ', '’')
    
    # Check proper names
    if norm in KNOWN_PROPER_NAMES:
        return (norm, 'atoqli_ot', 'exclude')
    if norm in EXCLUDED_WORDS or norm in EXCLUDED_VERBS:
        return (norm, 'yordamchi', 'exclude')
        
    # 1. Protected nouns
    for pn in PROTECTED_NOUNS:
        pn_norm = uz_norm(pn).replace('ʻ', '‘').replace('ʼ', '’')
        if norm == pn_norm or norm.startswith(pn_norm):
            canonical = 'ko‘ngil' if 'ko‘ngl' in pn_norm else ('yurak' if 'yurag' in pn_norm else pn)
            return (canonical, 'ot', 'noun')

    # 2. Vowel drops
    if norm.startswith('ko‘ngl') or norm.startswith('kongl'):
        return ('ko‘ngil', 'ot', 'noun')
    if norm.startswith('o‘g‘l') or norm.startswith('ogl'):
        return ('o‘g‘il', 'ot', 'noun')

    # 3. Verbs
    # Check against common verb stems
    for v_stem, v_lemma in COMMON_VERB_STEMS.items():
        v_stem_norm = uz_norm(v_stem).replace('ʻ', '‘').replace('ʼ', '’')
        if norm.startswith(v_stem_norm):
            # Verify verb inflections
            rest = norm[len(v_stem_norm):]
            if rest in ('di', 'dim', 'ding', 'dik', 'dilar', 'gan', 'gancha', 'sa', 'sa edi',
                        'moqda', 'yapti', 'yapman', 'b', 'ib', 'ay', 'aylik', 'sin', 'ar', 'mas',
                        'maydi', 'madi', 'madim', 'tirish', 'tirdi', 'uvdi', ''):
                return (v_lemma, 'fe’l', 'verb')

    # Check verb endings
    if norm.endswith(('di', 'dilar', 'dim', 'ding', 'yapman', 'yapsan', 'yapti', 'moqda', 'gan', 'kan', 'qan')):
        # Try stripping to verb stem
        for v_end in ['dilar', 'yapman', 'yapsan', 'yapti', 'moqda', 'gancha', 'dim', 'ding', 'gan', 'kan', 'qan', 'di']:
            if norm.endswith(v_end) and len(norm) - len(v_end) >= 2:
                stem = norm[:-len(v_end)]
                if stem in COMMON_VERB_STEMS:
                    return (COMMON_VERB_STEMS[stem], 'fe’l', 'verb')
                return (stem + 'moq', 'fe’l', 'verb')

    # 4. Adjectives / Adverbs
    ADJ_SUFFIXES = ('dek', 'day', 'roq', 'li', 'siz', 'iy', 'viy')
    for asfx in ADJ_SUFFIXES:
        if norm.endswith(asfx) and len(norm) - len(asfx) >= 3:
            base = norm[:-len(asfx)]
            return (norm, 'sifat', 'adj')
            
    # Check adjectives
    KNOWN_ADJS = {'og‘ir', 'yengil', 'toza', 'pok', 'katta', 'kichik', 'qattiq', 'yumshoq', 'yaxshi', 'yomon',
                  'muhim', 'asosiy', 'oqilona', 'dono', 'shoshilinch', 'issiq', 'sovuq', 'keng', 'tor'}
    if norm in KNOWN_ADJS:
        return (norm, 'sifat', 'adj')

    # 5. General noun suffixes
    NOUN_SUFFIXES = ('larimiz', 'laringiz', 'lariga', 'larida', 'laridan', 'larini', 'larning', 'lar',
                     'imiz', 'ingiz', 'lar', 'ning', 'dan', 'da', 'ga', 'ka', 'qa', 'ni', 'i', 'si')
    for nsfx in NOUN_SUFFIXES:
        if norm.endswith(nsfx) and len(norm) - len(nsfx) >= 3:
            stem = norm[:-len(nsfx)]
            # Check consonant back-alternation: g -> k, g' -> q
            if stem.endswith('g'):
                stem = stem[:-1] + 'k'
            elif stem.endswith('g‘') or stem.endswith('gʻ'):
                stem = stem[:-2] + 'q'
            return (stem, 'ot', 'noun')

    # Fallback: if surface forms given, pick most frequent surface form
    if surface_forms:
        most_freq_surface, _ = surface_forms.most_common(1)[0]
        return (most_freq_surface, 'ot', 'noun')

    return (norm, 'ot', 'noun')

print("Resolver test:")
for test_w in ['ko‘nglini', 'yuragiga', 'qarorga', 'tashvishida', 'o‘yladi', 'berdi', 'bo‘ldi', 'tinchiydi', 'Zebining', 'Enaxonga', 'dedi']:
    print(f"  {test_w} -> {resolve_uzbek_lemma_and_pos(test_w)}")

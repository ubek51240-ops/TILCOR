import sys
import os
import json
import re
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from word_family import uz_norm, match_uzbek_word_family, match_english_word_family, lemmatizer, clean_word

# Load corpus and dictionary
corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))
print(f"Loaded corpus: {len(corpus)}")

TOKEN_UZ_RE = re.compile(r"[a-z\u02bb\u02bc]+(?:-[a-z\u02bb\u02bc]+)*")
TOKEN_EN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+|-?[a-zA-Z]+)*")

KNOWN_NAMES = {
    'zebi', 'enaxon', 'razzoq', 'miryoqub', 'akbarali', 'poshshaxon', 'xadichaxon',
    'saltanat', 'olmasxon', 'o‘lmasxon', 'oʻlmasxon', 'eshon', 'eshonbobo', 'domla',
    'mulla', 'qurbon', 'salim', 'fotima', 'zuhra', 'santiago', 'manolin', 'perico',
    'martin', 'rogelio', 'pedrico', 'cienfuegos', 'havana', 'afrika', 'amerika',
    'cho‘lpon', 'cholpon', 'hemingway', 'xeminguey', 'g‘ofurov', 'gofurov', 'fort',
    'sharq', 'toshkent', 'samarqand', 'farg‘ona', 'andijon', 'qo‘qon', 'namangan'
}

STOPWORDS_UZ = {
    'bu', 'u', 'va', 'bilan', 'ham', 'uchun', 'deb', 'esa', 'kabi', 'lekin', 'ammo', 'biroq',
    'yoki', 'bir', 'shu', 'men', 'sen', 'biz', 'siz', 'ular', 'o‘sha', 'oʻsha', "o'sha",
    'o‘z', 'oʻz', "o'z", 'o‘zi', 'oʻzi', "o'zi", 'uning', 'uningda', 'ularning', 'mening',
    'sening', 'bizning', 'sizning', 'da', 'dan', 'ga', 'ni', 'ning', 'edi', 'bo‘ldi',
    'boʻldi', "bo'ldi", 'bo‘lgan', 'boʻlgan', "bo'lgan", 'ekan', 'emish', 'yo‘q', 'yoʻq',
    "yo'q", 'bor', 'qildi', 'qilgan', 'etdi', 'so‘ng', 'keyin', 'yana', 'faqat', 'hatto',
    'chunki', 'go‘yo', 'hali', 'endi', 'birga', 'ko‘ra', 'oldin', 'tomon', 'orasida',
    'bo‘yicha', 'ka', 'qa', 'narsa', 'narsani', 'narsaga', 'narsada', 'narsadan', 'har',
    'hamma', 'barcha', 'qadar', 'qaysi', 'qanaqa', 'qanday', 'hech', 'qachon', 'allaqachon',
    'dedi', 'deb', 'derdi', 'der', 'demoq', 'dedilar', 'degan', 'qildilar', 'qilmoqchi', 'edi'
}

COMMON_VERBS = {
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

PROTECTED_NOUNS = {
    'tashvish', 'xurush', 'olqish', 'qarg‘ish', 'qaror', 'ko‘ngil', 'yurak', 'yurag',
    'qishloq', 'qishlog‘', 'dil', 'dard', 'qalb', 'alam', 'hasrat', 'muhabbat', 'ishq',
    'sevgi', 'armon', 'orzu', 'umid', 'xayol', 'fikr', 'aql', 'sabot', 'saboz', 'bardosh',
    'matonat', 'jasorat', 'shijoat', 'g‘azab', 'qahr', 'nafrat', 'hasad', 'rashk',
    'shubha', 'gumon', 'ishonch', 'e’tiqod', 'marhamat', 'shafqat', 'rahmdillik',
    'tinchlik', 'xotirjamlik', 'sir', 'gap', 'so‘z', 'nasihat', 'pand', 'chol'
}

def resolve_uzbek(token: str):
    raw = token.lower().strip(" 'ʻʼ‘-")
    norm = uz_norm(raw).replace('ʻ', '‘').replace('ʼ', '’')
    if norm in KNOWN_NAMES or any(norm.startswith(nm) for nm in KNOWN_NAMES):
        return None, 'atoqli_ot'
    if norm in STOPWORDS_UZ:
        return None, 'yordamchi'

    # Protected nouns
    for pn in PROTECTED_NOUNS:
        pn_n = uz_norm(pn).replace('ʻ', '‘').replace('ʼ', '’')
        if norm == pn_n or norm.startswith(pn_n):
            c = 'ko‘ngil' if 'ko‘ngl' in pn_n else ('yurak' if 'yurag' in pn_n else pn)
            return c, 'ot'

    if norm.startswith('ko‘ngl') or norm.startswith('kongl'):
        return 'ko‘ngil', 'ot'
    if norm.startswith('o‘g‘l') or norm.startswith('ogl'):
        return 'o‘g‘il', 'ot'

    # Verbs
    for v_stem, v_lemma in COMMON_VERBS.items():
        v_stem_n = uz_norm(v_stem).replace('ʻ', '‘').replace('ʼ', '’')
        if norm.startswith(v_stem_n):
            rest = norm[len(v_stem_n):]
            if rest in ('di', 'dim', 'ding', 'dik', 'dilar', 'gan', 'gancha', 'sa',
                        'moqda', 'yapti', 'yapman', 'b', 'ib', 'ay', 'aylik', 'sin', 'ar', 'mas',
                        'maydi', 'madi', 'madim', 'tirish', 'tirdi', 'uvdi', ''):
                return v_lemma, 'fe’l'

    if norm.endswith(('di', 'dilar', 'dim', 'ding', 'yapman', 'yapsan', 'yapti', 'moqda', 'gan', 'kan', 'qan')):
        for v_end in ['dilar', 'yapman', 'yapsan', 'yapti', 'moqda', 'gancha', 'dim', 'ding', 'gan', 'kan', 'qan', 'di']:
            if norm.endswith(v_end) and len(norm) - len(v_end) >= 2:
                stem = norm[:-len(v_end)]
                if stem in COMMON_VERBS:
                    return COMMON_VERBS[stem], 'fe’l'
                return stem + 'moq', 'fe’l'

    # Sifat / Ravish
    if norm.endswith(('dek', 'day', 'roq', 'li', 'siz', 'iy', 'viy')) and len(norm) > 4:
        return norm, 'sifat'
    if norm in {'og‘ir', 'yengil', 'toza', 'pok', 'katta', 'kichik', 'qattiq', 'yumshoq', 'yaxshi', 'yomon',
                'muhim', 'asosiy', 'oqilona', 'dono', 'shoshilinch', 'issiq', 'sovuq'}:
        return norm, 'sifat'
    if norm in {'tez', 'sekin', 'asta', 'birdan', 'to‘satdan', 'chuqur'}:
        return norm, 'ravish'

    # Noun suffixes
    for nsfx in ('larimiz', 'laringiz', 'lariga', 'larida', 'laridan', 'larini', 'larning', 'lar',
                 'imiz', 'ingiz', 'lar', 'ning', 'dan', 'da', 'ga', 'ka', 'qa', 'ni', 'i', 'si'):
        if norm.endswith(nsfx) and len(norm) - len(nsfx) >= 3:
            stem = norm[:-len(nsfx)]
            if stem.endswith('g'): stem = stem[:-1] + 'k'
            elif stem.endswith('g‘') or stem.endswith('gʻ'): stem = stem[:-2] + 'q'
            return stem, 'ot'

    return norm, 'ot'

def test_query(q, lang='uz'):
    q_norm = uz_norm(q) if lang == 'uz' else q.lower()
    q_lemma, q_pos = resolve_uzbek(q) if lang == 'uz' else (lemmatizer.lemmatize(q_norm, 'n'), 'noun')

    pair_occurrences = Counter()
    pair_sentences = defaultdict(set)
    pair_patterns = {}
    pair_examples = {}

    if lang == 'uz':
        for s_idx, s in enumerate(corpus):
            text = s.get('uz', '')
            if not text: continue
            norm_text, offsets = uz_norm(text, return_offsets=True)
            if not norm_text: continue
            tokens = [m.group(0) for m in TOKEN_UZ_RE.finditer(norm_text)]
            m_indices = [i for i, t in enumerate(tokens) if match_uzbek_word_family(q_norm, t)]
            for m_idx in m_indices:
                for w_idx in range(max(0, m_idx - 4), min(len(tokens), m_idx + 5)):
                    if w_idx == m_idx: continue
                    tok = tokens[w_idx]
                    lem, pos = resolve_uzbek(tok)
                    if not lem or lem == q_lemma: continue

                    # 1.1 Patterns
                    pattern = None
                    if q_pos == 'ot' and pos == 'fe’l':
                        pattern = 'Ot + fe’l'
                        phrase = f"{q_lemma} {lem}"
                    elif q_pos == 'fe’l' and pos == 'ot':
                        pattern = 'Ot + fe’l'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'ot' and pos == 'sifat':
                        pattern = 'Sifat + ot'
                        phrase = f"{lem} {q_lemma}"
                    elif q_pos == 'ot' and pos == 'ot':
                        pattern = 'Ot + ot'
                        phrase = f"{q_lemma} {lem}" if m_idx < w_idx else f"{lem} {q_lemma}"
                    elif q_pos == 'fe’l' and pos == 'ravish':
                        pattern = 'Ravish + fe’l'
                        phrase = f"{lem} {q_lemma}"
                    
                    if not pattern: continue

                    pair_occurrences[phrase] += 1
                    pair_sentences[phrase].add(s_idx)
                    pair_patterns[phrase] = pattern
                    if phrase not in pair_examples:
                        pair_examples[phrase] = text
    elif lang == 'en':
        for s_idx, s in enumerate(corpus):
            text = s.get('en', '')
            if not text: continue
            tokens = [m.group(0).lower() for m in TOKEN_EN_RE.finditer(text)]
            m_indices = [i for i, t in enumerate(tokens) if match_english_word_family(q_norm, t)]
            for m_idx in m_indices:
                for w_idx in range(max(0, m_idx - 4), min(len(tokens), m_idx + 5)):
                    if w_idx == m_idx: continue
                    tok = tokens[w_idx]
                    if tok in {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'from', 'as', 'is', 'was', 'were', 'it', 'he', 'she', 'they', 'i', 'you', 'we', 'his', 'her', 'my', 'their', 'our', 'that', 'this', 'had', 'have', 'has', 'but', 'not', 'no', 'did', 'do', 'does', 'would', 'could', 'should', 'all', 'any', 'some', 'there', 'here', 'when', 'what', 'who', 'how', 'out', 'up', 'down', 'into', 'him', 'them', 'me', 'us'} or len(tok) < 3 or tok.isdigit():
                        continue
                    
                    lemma_n = lemmatizer.lemmatize(tok, 'n')
                    lemma_v = lemmatizer.lemmatize(tok, 'v')
                    lem = lemma_v if lemma_v != tok else lemma_n
                    if lem == q_norm: continue

                    if tok.endswith(('ed', 'ing')) or lemma_v != tok:
                        pattern = 'Verb + noun' if w_idx < m_idx else 'Noun + verb'
                        phrase = f"{lemma_v} {q_norm}" if w_idx < m_idx else f"{q_norm} {lemma_v}"
                    elif tok.endswith(('ful', 'less', 'able', 'ive', 'ous', 'al', 'ic', 'y', 'great', 'deep', 'hard', 'good', 'bad', 'little', 'big', 'old')):
                        pattern = 'Adjective + noun'
                        phrase = f"{tok} {q_norm}"
                    else:
                        pattern = 'Noun + noun'
                        phrase = f"{tok} {q_norm}" if w_idx < m_idx else f"{q_norm} {tok}"

                    pair_occurrences[phrase] += 1
                    pair_sentences[phrase].add(s_idx)
                    pair_patterns[phrase] = pattern
                    if phrase not in pair_examples:
                        pair_examples[phrase] = text

    print(f"\n================ TOP 15 CANDIDATES FOR '{q}' ================")
    top = pair_occurrences.most_common(15)
    for rank, (phrase, occ) in enumerate(top, 1):
        scnt = len(pair_sentences[phrase])
        pat = pair_patterns[phrase]
        print(f"{rank:2d}. {phrase:<25} | Qolip: {pat:<16} | {scnt} gapda | {occ} marta")

for q in ['yurak', 'ko‘ngil', 'qaror']:
    test_query(q, 'uz')

for q in ['heart', 'decision']:
    test_query(q, 'en')

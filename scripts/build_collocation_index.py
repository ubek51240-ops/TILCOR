#!/usr/bin/env python3
"""Collocation index of the corpus: every lexical word combination that matches a structural pattern,
in both languages, with frequency, examples and its translation in the parallel book.

English (both English texts): dependency relations of spaCy en_core_web_sm, as recommended for
collocation extraction by Uhrig & Proisl (2012):
    amod  -> adjective + noun        dobj  -> verb + noun        nsubj -> noun + verb
    advmod(ADV->VERB) -> verb + adverb     advmod(ADV->ADJ) -> adverb + adjective
    pobj under a verb's preposition -> verb + preposition + noun     compound -> noun + noun
Uzbek (both Uzbek texts): Uzbek is head-final, so the patterns are read on adjacent words
(one particle such as "ham" may stand between a noun and its verb):
    sifat + ot, ot + fe’l, ega + kesim (possessive noun + verb), ravish + fe’l, ot + ot.
    Part of speech comes from (1) verb endings, (2) projection from the aligned English words
    (Yarowsky, Ngai & Wicentowski, 2001): the majority part of speech of the English words an Uzbek stem is
    linked to across the corpus, (3) the closed word lists of search_engine.py.
Only combinations that occur at least twice are kept (the platform's threshold for public candidates).
Translations come from the word alignment (equivalents.py): the translator's own words.

Output: data/collocation_index.json
"""
import collections, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

MIN_FREQ = 2
MAX_OCC_STORED = 60

EN_SKIP_LEMMA = {'be', 'have', 'do', 'get', 'go', 'say', 'make', 'can', 'will', 'would', 'could', 'should',
                 'one', 'thing', 'something', 'anything', 'nothing', 'everything', 'way', 'time', 'other', 'such',
                 'own', 'same', 'more', 'most', 'much', 'many', 'few', 'little', 'then', 'there', 'here', 'so',
                 'very', 'too', 'also', 'just', 'now', 'not', 'never', 'ever', 'again', 'even', 'only', 'still',
                 'how', 'when', 'where', 'why', 'what', 'all', 'some', 'any', 'no', 'each', 'every', 'this', 'that'}
EN_SKIP_LEMMA_SOFT = {'make', 'go', 'get', 'do', 'have'}   # allowed as the verb of verb + noun (make a decision)

UZ_VERB_ENDINGS = sorted({
    'moqda', 'yapti', 'yapman', 'yapsan', 'yapmiz', 'yotgan', 'yotib', 'yotardi', 'maydi', 'mayman', 'madi',
    'madim', 'madilar', 'dilar', 'dingiz', 'dim', 'ding', 'dik', 'di', 'ti', 'adilar', 'adi', 'ydi', 'aman',
    'asan', 'amiz', 'ardi', 'arkan', 'ar', 'gancha', 'guncha', 'gach', 'gani', 'gan', 'kan', 'qan', 'moqchi',
    'moq', 'mas', 'masdan', 'ib', 'sa', 'sin', 'singlar', 'ing', 'inglar', 'ishdi', 'ishib', 'ishdi'}, key=len, reverse=True)


def main():
    import equivalents as E
    from word_family import uz_align_stem, uz_norm
    import search_engine as SE

    corpus = {p['id']: p for p in json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))}
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))
    lex = json.load(open(os.path.join(DATA, 'lexical_table.json'), encoding='utf-8'))

    # ---- projected part of speech for Uzbek stems
    proj = collections.defaultdict(collections.Counter)
    for pid, rec in aln.items():
        for i, j in rec['links']:
            proj[rec['uz'][i][2]][rec['en'][j][3]] += 1

    # ---- surface vocabulary of the Uzbek texts (a lemma must be an attested word)
    vocab = collections.Counter()
    for pid, rec in aln.items():
        txt = corpus.get(pid, {}).get('uz') or ''
        for s_, e_, _st in rec['uz']:
            vocab[uz_norm(txt[s_:e_].lower())] += 1

    CASES = ('ning', 'gacha', 'dan', 'ga', 'ka', 'qa', 'da', 'ni')
    POSS = ('imiz', 'ingiz', 'lari', 'si', 'im', 'ing', 'i', 'm')
    DROP = {'koʻngl': 'koʻngil', 'oʻgʻl': 'oʻgʻil', 'burn': 'burun', 'qorn': 'qorin', 'ogʻz': 'ogʻiz',
            'bagʻr': 'bagʻir', 'shahr': 'shahar', 'singl': 'singil', 'boʻyn': 'boʻyin', 'oʻrn': 'oʻrin'}

    def letters(x):
        return sum(1 for ch in x if ch.isalpha() and ch not in 'ʻʼ‘’')

    def noun_lemma(surface):
        """Nominative form: remove one case, one possessive and one plural ending, but only as far as the
        result is a word attested in the corpus (tashqari stays tashqari, odam stays odam)."""
        w = uz_norm(surface.lower())
        best = w
        cur = w
        for group in (CASES, POSS, ('lar',), POSS):
            for sfx in sorted(group, key=len, reverse=True):
                if cur.endswith(sfx) and letters(cur[:-len(sfx)]) >= 2:
                    cand = cur[:-len(sfx)]
                    cand_alt = cand
                    if sfx[0] in 'aeiou' and not cand.endswith('ng') and letters(cand) > 3:
                        if cand.endswith('gʻ'):
                            cand_alt = cand[:-2] + 'q'
                        elif cand.endswith('g'):
                            cand_alt = cand[:-1] + 'k'
                    cand_alt = DROP.get(cand_alt, cand_alt)
                    for c in (cand_alt, cand):
                        # a first-person ending (-m, -im) is accepted only if the shorter word is at least as
                        # frequent as the longer one: akam -> aka, but qadam stays qadam (not "qada")
                        if sfx in ('m', 'im') and vocab.get(c, 0) < vocab.get(cur, 0):
                            continue
                        if vocab.get(c, 0) >= 1:
                            best = c
                            break
                    cur = cand_alt
                    break
        return best

    def has_possessive(surface):
        w = uz_norm(surface.lower())
        base = noun_lemma(w)
        return base != w and w.endswith(('i', 'si')) and not w.endswith(('ni', 'dagi'))

    def uz_pos(surface, stem):
        low = uz_norm(surface.lower())
        if low in SE.UZBEK_STOPWORDS or low in E.UZ_FUNCTION:
            return 'FUNC'
        if surface[:1].isupper() and (low in SE.KNOWN_NAMES or any(low.startswith(n) for n in SE.KNOWN_NAMES)):
            return 'PROPN'
        c = proj.get(stem)
        top = None
        if c:
            tot = sum(v for k, v in c.items() if k in ('NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN'))
            if tot >= 2:
                top, cnt = max(((k, v) for k, v in c.items() if k in ('NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN')), key=lambda kv: kv[1])
                if cnt / tot < 0.5:
                    top = None
        finite = ('di', 'dilar', 'dim', 'ding', 'dik', 'madi', 'maydi', 'yapti', 'moqda', 'adi', 'ydi', 'ardi', 'arkan', 'ishdi')
        if any(low.endswith(e) and len(low) - len(e) >= 3 for e in finite):
            return 'VERB'                       # a finite ending is decisive
        if has_possessive(surface) and top not in ('VERB',):
            return 'NOUN'                       # possessive ending: a nominal (rangi, yuragi)
        has_verb_end = any(low.endswith(e) and len(low) - len(e) >= 2 for e in UZ_VERB_ENDINGS)
        if has_verb_end and low.endswith(('gan', 'ib', 'gach', 'sa')) and top == 'ADJ':
            top = 'VERB'                        # participle/converb (o‘chgan, o‘chib)
        if not has_verb_end and low.endswith('b') and len(low) > 3 and low[-2] in 'aeiou' and top in (None, 'VERB'):
            has_verb_end = vocab.get(low[:-1] + 'di', 0) + vocab.get(low[:-1] + 'gan', 0) > 0   # o‘ynab: o‘ynadi exists
        if not has_verb_end and low.endswith(('ning', 'dan', 'ga', 'da', 'ni', 'ka', 'qa', 'lar', 'gacha')):
            return 'NOUN' if top in (None, 'NOUN', 'VERB', 'PROPN') else top
        if top == 'ADJ' and c and c.get('NOUN', 0) >= 0.4 * (c.get('NOUN', 0) + c.get('ADJ', 0)):
            top = 'NOUN'            # chol: linked to "old" and to "man
        if has_verb_end and top in (None, 'VERB'):
            return 'VERB'
        if top:
            return top
        _lem, p = SE.resolve_uzbek(surface)
        return {'ot': 'NOUN', 'fe’l': 'VERB', 'sifat': 'ADJ', 'ravish': 'ADV', 'atoqli_ot': 'PROPN'}.get(p, 'X')

    def uz_verb_lemma(surface):
        low = uz_norm(surface.lower())
        for c_ in ('ning', 'dan', 'ga', 'da', 'ni'):
            if low.endswith(c_) and low[:-len(c_)].endswith(('gan', 'kan', 'qan', 'ish', 'uv', 'moq', 'gani', 'ganlari')):
                low = low[:-len(c_)]
                break
        for e in UZ_VERB_ENDINGS:
            if low.endswith(e) and len(low) - len(e) >= 2:
                low = low[:-len(e)]
                break
        else:
            if low.endswith('b') and len(low) > 3 and low[-2] in 'aeiou':
                low = low[:-1]
        if low.endswith('ma') and len(low) > 4:
            low = low[:-2]
        for stem_, lemma_ in SE.COMMON_VERBS.items():
            if uz_norm(stem_) == low:
                return lemma_
        return low + 'moq'

    verb_endings_seen = collections.defaultdict(set)
    for form in vocab:
        for e_ in UZ_VERB_ENDINGS:
            if form.endswith(e_) and len(form) - len(e_) >= 2:
                verb_endings_seen[form[:-len(e_)]].add(e_)
                break

    def valid_verb(lemma_):
        lemma_ = uz_norm(lemma_)
        stem_ = lemma_[:-3] if lemma_.endswith('moq') else lemma_
        return len(verb_endings_seen.get(stem_, ())) >= 2 or any(uz_norm(v_) == lemma_ for v_ in SE.COMMON_VERBS.values())

    # auxiliary verbs of the "converb + auxiliary" constructions excluded by the methodology (1.1.4):
    # tutib turmoq, qila olmoq, ko‘tara tushmoq
    AUX = {uz_norm(v_) for v_ in ('tushmoq', 'qolmoq', 'ketmoq', 'olmoq', 'bermoq', 'ko‘rmoq', 'turmoq', 'yubormoq',
                                  'o‘tirmoq', 'yotmoq', 'chiqmoq', 'kelmoq', 'qo‘ymoq', 'tashlamoq', 'bo‘lmoq', 'bilmoq')}

    def is_converb(surface, verb_lemma):
        low = uz_norm(surface.lower())
        if low.endswith(('ib', 'ub')) and len(low) > 3 and valid_verb(low[:-2] + 'moq'):
            return True
        if low.endswith('b') and len(low) > 3 and low[-2] in 'aeiou' and valid_verb(low[:-1] + 'moq'):
            return True
        if low.endswith('may') and len(low) > 4 and valid_verb(low[:-3] + 'moq'):
            return True
        if low.endswith(('a', 'y')) and len(low) > 3 and verb_lemma in AUX and valid_verb(low[:-1] + 'moq'):
            return True
        return False

    # words that occur in lower case somewhere in the texts of each language (to tell names from sentence starts)
    lower_seen = {'uz': set(), 'en': set()}
    lower_stems = set()
    for pid_, rec_ in aln.items():
        for lg_ in ('uz', 'en'):
            txt_ = (corpus.get(pid_) or {}).get(lg_) or ''
            for t_ in rec_[lg_]:
                w_ = txt_[t_[0]:t_[1]]
                if w_ and w_[:1].islower():
                    lower_seen[lg_].add(w_)
                    if lg_ == 'uz':
                        lower_stems.add(t_[2])

    def is_name(lang_, word_):
        """A capitalised word whose lower-case form never occurs in the texts is a proper name (excluded, 1.1.4)."""
        if not word_[:1].isupper():
            return False
        if word_.lower() in lower_seen[lang_]:
            return False
        if lang_ == 'uz' and uz_align_stem(word_.lower()) in lower_stems:
            return False
        return True

    excluded = collections.Counter()
    entries = {}

    def add(lang, pattern, lemma, base, pid, spans, surface, comps=None):
        text_ = (corpus[pid].get(lang) or '')
        if any(is_name(lang, text_[a_:b_]) for a_, b_ in spans):
            excluded['atoqli ot'] += 1
            return
        if lang == 'uz':
            lemma, base = uz_norm(lemma), uz_norm(base)     # one key for o‘/oʻ spellings
        key = (lang, pattern, lemma)
        e = entries.get(key)
        if e is None:
            e = entries[key] = {'lang': lang, 'pattern': pattern, 'lemma': lemma, 'base': base, 'freq': 0,
                                'books': collections.Counter(), 'forms': collections.Counter(), 'occ': [],
                                'comps': collections.Counter()}
        e['freq'] += 1
        e['books'][corpus[pid]['book']] += 1
        e['forms'][surface] += 1
        if comps:
            e['comps'][comps] += 1      # the stems/lemmas of the first and the last component as they stand in the text
        e['occ'].append([pid, spans])   # all occurrences; only MAX_OCC_STORED are written out

    lemma_freq = {'en': collections.Counter(), 'uz': collections.Counter()}
    for pid, rec in aln.items():
        if pid not in corpus:
            continue
        en_text, uz_text = corpus[pid]['en'] or '', corpus[pid]['uz'] or ''
        toks = rec['en']
        for t in toks:
            lemma_freq['en'][t[2]] += 1
        # ---------------- English, dependency patterns
        for k, (s, e, lem, pos, dep, head) in enumerate(toks):
            if head < 0 or head >= len(toks) or lem in EN_SKIP_LEMMA and dep != 'dobj':
                continue
            h = toks[head]
            hs, he, hlem, hpos = h[0], h[1], h[2], h[3]
            if hlem in EN_SKIP_LEMMA and not (dep == 'dobj' and hlem in EN_SKIP_LEMMA_SOFT):
                continue
            pat = None
            if dep == 'amod' and pos == 'ADJ' and hpos == 'NOUN':
                pat, lemma, base = 'adjective + noun', f'{lem} {hlem}', hlem
            elif dep == 'dobj' and pos == 'NOUN' and hpos == 'VERB' and lem not in EN_SKIP_LEMMA:
                pat, lemma, base = 'verb + noun', f'{hlem} {lem}', lem
            elif dep == 'nsubj' and pos == 'NOUN' and hpos == 'VERB':
                pat, lemma, base = 'noun + verb', f'{lem} {hlem}', lem
            elif dep == 'advmod' and pos == 'ADV' and hpos == 'VERB':
                pat, lemma, base = 'verb + adverb', f'{hlem} {lem}', hlem
            elif dep == 'advmod' and pos == 'ADV' and hpos == 'ADJ':
                pat, lemma, base = 'adverb + adjective', f'{lem} {hlem}', hlem
            elif dep == 'compound' and pos == 'NOUN' and hpos == 'NOUN':
                pat, lemma, base = 'noun + noun', f'{lem} {hlem}', hlem
            elif dep == 'pobj' and pos == 'NOUN' and hpos == 'ADP':
                g = toks[h[5]] if 0 <= h[5] < len(toks) else None
                if g and g[3] == 'VERB' and g[2] not in EN_SKIP_LEMMA:
                    pat, lemma, base = 'verb + preposition + noun', f'{g[2]} {hlem} {lem}', lem
                    a, b = min(g[0], s), max(g[1], e)
                    add('en', pat, lemma, base, pid, [[g[0], g[1]], [hs, he], [s, e]], en_text[a:b] if b - a < 60 else lemma,
                        (g[2], lem))
                    continue
            if pat:
                a, b = min(s, hs), max(e, he)
                first, last = (lem, hlem) if s < hs else (hlem, lem)
                add('en', pat, lemma, base, pid, [[s, e], [hs, he]], en_text[a:b] if b - a < 60 else lemma, (first, last))
        # ---------------- Uzbek, adjacency patterns
        ut = rec['uz']
        info = []
        for (s, e, stem) in ut:
            surf = uz_text[s:e]
            info.append((s, e, stem, surf, uz_pos(surf, stem)))
            lemma_freq['uz'][stem] += 1
        for i in range(len(info) - 1):
            s1, e1, st1, w1, p1 = info[i]
            for gap in (1, 2):
                j = i + gap
                if j >= len(info):
                    break
                if gap == 2 and uz_norm(info[i + 1][3].lower()) not in ('ham', 'bir', 'juda', 'ancha', 'eng', 'hech'):
                    break
                s2, e2, st2, w2, p2 = info[j]
                if uz_text[e1:s2].strip(' ') and any(ch in uz_text[e1:s2] for ch in '.!?;:—«»"“”'):
                    break
                if gap == 1 and ('-' in uz_text[e1:s2] or '‐' in uz_text[e1:s2] or st1 == st2):
                    excluded['juft yoki takroriy so‘z'] += 1     # yonma-yon, ota-ona, sekin-sekin (1.1.4)
                    break
                pat = None
                if p1 == 'ADJ' and p2 == 'NOUN' and gap == 1:
                    pat, lemma, base = 'sifat + ot', f'{uz_norm(w1.lower())} {noun_lemma(w2)}', noun_lemma(w2)
                elif p1 == 'NOUN' and p2 == 'VERB':
                    v = uz_verb_lemma(w2)
                    if has_possessive(w1) and not uz_norm(w1.lower()).endswith(('ni', 'ga', 'da', 'dan', 'ning')):
                        pat, lemma, base = 'ega + kesim', f'{uz_norm(w1.lower())} {v}', noun_lemma(w1)
                    else:
                        # a governed noun keeps its case ending: uyga kirmoq, o‘rnidan turmoq (1.1.4: the case
                        # government is recorded as part of the model); a bare noun stays bare: javob bermoq
                        low1 = uz_norm(w1.lower())
                        case = next((c_ for c_ in ('dan', 'ga', 'ka', 'qa', 'da', 'ni') if low1.endswith(c_)), '')
                        noun_part = low1 if case else noun_lemma(w1)
                        pat, lemma, base = 'ot + fe’l', f'{noun_part} {v}', noun_lemma(w1)
                elif p1 == 'ADV' and p2 == 'VERB':
                    pat, lemma, base = 'ravish + fe’l', f'{uz_norm(w1.lower())} {uz_verb_lemma(w2)}', uz_verb_lemma(w2)
                elif p1 == 'NOUN' and p2 == 'NOUN' and gap == 1 and has_possessive(w2):
                    pat, lemma, base = 'ot + ot', f'{noun_lemma(w1)} {uz_norm(w2.lower())}', noun_lemma(w1)
                if pat and pat != 'sifat + ot' and pat != 'ot + ot' and not valid_verb(lemma.split()[-1]):
                    pat = None
                if pat in ('ot + fe’l', 'ravish + fe’l', 'ega + kesim') and is_converb(w1, lemma.split()[-1]):
                    excluded['ko‘makchi fe’lli qurilma'] += 1   # tutib turmoq, qila olmoq (1.1.4)
                    pat = None
                if pat:
                    add('uz', pat, lemma, base, pid, [[s1, e1], [s2, e2]], uz_text[s1:e2], (st1, st2))
                    break

    # ---- keep frequent ones; translations from the alignment over ALL occurrences; within-corpus association
    # measures from the real component frequencies (Evert, 2008; Gablasova et al., 2017). N is the number of
    # tokens of that language in the aligned part of the corpus.
    N_tok = {lg: sum(c.values()) for lg, c in lemma_freq.items()}

    def measures(o11, r1, c1, n_):
        if not (o11 and r1 and c1 and n_):
            return {}
        r1, c1 = max(r1, o11), max(c1, o11)
        e11 = r1 * c1 / n_
        cells = [(o11, e11), (r1 - o11, r1 * (n_ - c1) / n_), (c1 - o11, (n_ - r1) * c1 / n_),
                 (n_ - r1 - c1 + o11, (n_ - r1) * (n_ - c1) / n_)]
        g2 = 2 * sum(o * math.log(o / e) for o, e in cells if o > 0 and e > 0)
        return {'mi': round(math.log2(o11 / e11), 2), 't': round((o11 - e11) / math.sqrt(o11), 2),
                'log_dice': round(14 + math.log2(2 * o11 / (r1 + c1)), 2), 'g2': round(g2, 1),
                'f1': r1, 'f2': c1, 'n': n_}

    def display_form(texts, lg):
        # the most frequent form; a capital at the start is dropped when it only marks the start of a sentence
        form = texts.most_common(1)[0][0]
        m_ = re.match(r"[^\W\d_]+(?:[‘’'ʻʼ][^\W\d_]+)*", form)
        first = m_.group(0) if m_ else form
        if form[:1].isupper() and not form.isupper() and (first.lower() in lower_seen[lg] or
                                                          (lg == 'uz' and uz_align_stem(first.lower()) in lower_stems)):
            return form[:1].lower() + form[1:]
        return form

    def book_of(pid):
        return 'kvk' if '-kvk-' in pid else 'oms'

    out = []
    for (lang, pat, lemma), e in entries.items():
        if e['freq'] < MIN_FREQ:
            continue
        if e['comps']:
            c_first, c_last = e['comps'].most_common(1)[0][0]
        else:
            parts = lemma.split()
            c_first, c_last = (parts[0], parts[-1]) if lang == 'en' else (uz_align_stem(parts[0]), uz_align_stem(parts[-1]))
        f1 = lemma_freq[lang].get(c_first, 0)
        f2 = lemma_freq[lang].get(c_last, 0)
        assoc = measures(e['freq'], f1, f2, N_tok[lang])
        trans = collections.Counter()
        trans_text = {}
        per_book = {}
        for o in e['occ']:
            pid, spans = o[0], o[1]
            sp, key = E.equivalent_spans(pid, lang, [tuple(x) for x in spans])
            o.append(key if (sp and key) else None)      # [pair id, spans, equivalent key or None]
            st = per_book.setdefault(book_of(pid), {'occ': 0, 'eq': 0, 'single': 0, 'multi': 0})
            st['occ'] += 1
            if sp and key:
                other = corpus[pid]['en' if lang == 'uz' else 'uz'] or ''
                txt = other[sp[0][0]:sp[0][1]]
                trans[key] += 1
                trans_text.setdefault(key, collections.Counter())[txt] += 1
                st['eq'] += 1
                st['single' if len(key.split()) == 1 else 'multi'] += 1
        # a short, natural display form: the most frequent surface span if it is short, otherwise the lemma
        disp, _ = e['forms'].most_common(1)[0]
        if lang == 'uz':
            # shown with the apostrophes of the books (o‘, g‘, ’)
            lemma = lemma.replace('ʻ', '‘').replace('ʼ', '’')
            e['base'] = e['base'].replace('ʻ', '‘').replace('ʼ', '’')
            disp = lemma
        if len(disp.split()) > 4:
            disp = lemma
        out.append({
            'id': f"{lang}-" + __import__('hashlib').md5(f'{pat}|{lemma}'.encode('utf-8')).hexdigest()[:10],
            'lang': lang, 'pattern': pat, 'lemma': lemma, 'display': disp.lower() if lang == 'en' else disp,
            'base': e['base'], 'freq': e['freq'], 'books': dict(e['books']),
            'forms': dict(e['forms'].most_common(6)),
            'log_dice': assoc.get('log_dice'),
            'assoc': assoc,
            'eq_stats': per_book,
            'translations': [{'key': k, 'text': display_form(trans_text[k], 'en' if lang == 'uz' else 'uz'), 'count': c,
                              'forms': dict(trans_text[k].most_common(4))} for k, c in trans.most_common(6)],
            'occ': e['occ'][:MAX_OCC_STORED],
        })
    out.sort(key=lambda x: (-x['freq'], x['lemma']))
    json.dump(out, open(os.path.join(DATA, 'collocation_index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    by = collections.Counter((x['lang'], x['pattern']) for x in out)
    print(len(out), 'collocations (f >= 2)')
    print('excluded occurrences:', dict(excluded))
    for k, v in sorted(by.items()):
        print('  ', k, v)


if __name__ == '__main__':
    main()

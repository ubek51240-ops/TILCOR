#!/usr/bin/env python3
"""Corpus-based bilingual dictionary (Uzbek–English and English–Uzbek) from the word alignment of the corpus.

Each entry is a word of one language with the words the translators used for it in the two books, the number
of times each pair is linked, the word forms met in the texts, and one example sentence pair for every
translation. Nothing comes from a printed dictionary or from machine translation.

Steps
  1. Every Uzbek word form is brought to a dictionary form (lemma):
       * a verb form -> stem + -moq (dedi, degan, deb -> demoq; qaradi, qarab -> qaramoq; zerikdim -> zerikmoq).
         The stem must be a known verb (search_engine.COMMON_VERBS) or be met in the texts with several verb
         endings. An ending that can also be nominal (-di, -gan, -ar, -sa, -ing ...) is read as a verb ending only
         when the aligned English word is a verb (oldi "took" -> olmoq, oldi "front" -> oldi);
       * any other form -> the shortest form left after removing case, possessive and plural endings that is
         itself met in the texts (xotini -> xotin, yuragi -> yurak, oldida -> oldi, qarining -> qari);
       * a hyphenated word is kept whole (qah-qah, tez-tez, kula-kula).
     An English word is given by its lemma (spaCy), a hyphenated one as a whole (co-wives -> co-wife).
  2. The links of the word alignment (eflomal, grow-diag-final-and; data/word_alignment.json) are counted
     between these dictionary forms. Only content words on both sides are used.
  3. A translation is kept if the pair is linked at least MIN_LINK times, makes up at least MIN_SHARE of all
     links of the headword, and is associated in both directions: Dice = 2·n / (links of the headword + links
     of the translation) >= MIN_DICE, so a very frequent word (dedi, kelmoq, now) is not given as the
     translation of everything. Translations are ordered by n · Dice.
  4. Proper names are left out (a word written with a capital letter in most of its occurrences, or a pair of
     identical words).
  5. A grammatical adverb (never, here, very; hech, juda) is not given as the translation of a word that is not an
     adjective or an adverb, a light verb (have, make; qilmoq, bo‘lmoq) not as the translation of a word that is
     not a verb, and the other way round (never -> ko‘ngil):
     such a link belongs to a combination (ko‘nglim bormaydi -> I would never; bu yerda -> here; qo‘lga olmoq ->
     have), not to the word.
  6. The colloquial oyi "mother" (oyi, oyim, oyijon) is kept apart from oy "moon, month" by the translator's word.
The example of a translation is taken from the most reliable pair: a pair of paragraph 1.1 first, then a pair on
which both alignment passes agree and whose hunalign score is not low (>= 0.3), then by sentence length.
Part of speech comes from the aligned English words (annotation projection, Yarowsky et al., 2001), for an
Uzbek verb from step 1.

Output: data/corpus_dictionary.json  {"uz": [entry, ...], "en": [entry, ...]}
entry = {"head", "pos", "freq", "forms": {form: n}, "tr": [{"text", "count", "forms", "ex": [pair id, q span, o span]}]}
"""
import collections, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
sys.path.insert(0, ROOT)

MAX_TR = 6
MIN_DICE = 0.05
POS_MAP = {'NOUN': 'noun', 'VERB': 'verb', 'ADJ': 'adj', 'ADV': 'adv'}
# Words that are not given as the translation of a headword of another part of speech: grammatical adverbs
# (negation, degree, frequency, deixis) and light verbs. The word aligner links them to the noun of a combination
# (ko‘nglim bormaydi -> would never; bu yerda -> here; qo‘lga olmoq -> have), so they are links of the combination,
# not translations of the word.
GRAM_EN = {'never', 'not', 'ever', 'always', 'so', 'very', 'too', 'just', 'only', 'even', 'still', 'already', 'also',
           'again', 'yet', 'quite', 'rather', 'almost', 'really', 'much', 'more', 'most', 'often', 'sometimes',
           'perhaps', 'maybe', 'here', 'there', 'now', 'then'}
LIGHT_EN = {'have', 'be', 'do', 'get', 'make', 'take', 'give', 'let', 'go', 'come', 'put', 'keep', 'seem', 'become'}
GRAM_UZ = {'hech', 'juda', 'faqat', 'yana', 'hali', 'sira', 'aslo', 'asti', 'hatto', 'endi', 'doim', 'hamisha',
           'allaqachon', 'ham', 'hamon', 'eng', 'ortiq', 'xuddi', 'ba’zi', 'sari', 'tag‘in', 'ancha', 'sal'}
LIGHT_UZ = {'qilmoq', 'bo‘lmoq', 'etmoq', 'olmoq', 'bermoq', 'qolmoq', 'turmoq', 'yubormoq', 'qo‘ymoq', 'ketmoq',
            'kelmoq'}
# a form of oy "moon, month" that is the colloquial word for "mother" (oyi, oyim, oyijon) when the translator
# rendered it so
MOTHER_EN = {'mother', 'mom', 'mum', 'mama', 'mamma', 'ma', 'mommy', 'mummy'}
VOWELS = set('aeiou')

# verb endings; WEAK ones can also end a noun or an adjective (oldi, shahar, kitobing, kelgan)
STRONG = {'moqda', 'moqchi', 'moq', 'yapti', 'yapman', 'yapsan', 'yapmiz', 'yapsiz', 'yotgan', 'yotib', 'yotardi',
          'yotir', 'ayotir', 'maydi', 'mayman', 'maysan', 'may', 'madi', 'madim', 'madik', 'madilar', 'masdan',
          'dilar', 'dingiz', 'dim', 'ding', 'dik', 'adilar', 'adi', 'ydi', 'aman', 'asan', 'amiz', 'asiz', 'ardi',
          'arkan', 'gancha', 'guncha', 'gach', 'ganda', 'gandan', 'ganini', 'ganlar', 'ganidan', 'ib', 'sin',
          'singlar', 'inglar', 'ishdi', 'ishib', 'sam', 'sang', 'sak', 'sangiz', 'salar', 'yman', 'ysan', 'ymiz'}
WEAK = {'di', 'ti', 'ar', 'gan', 'kan', 'qan', 'mas', 'sa', 'ing', 'gani', 'a', 'y', 'ng'}
ENDINGS = sorted(STRONG | WEAK, key=len, reverse=True)
CASES = ('ning', 'dan', 'gacha', 'ga', 'ka', 'qa', 'dagi', 'da', 'ni', 'cha')
NO_BASE = {'shun', 'bun', 'mun', 'un', 'qan', 'man', 'sen', 'biz', 'siz'}      # shundan, bunga, unga: pronoun + case
POSS = ('imiz', 'ingiz', 'lari', 'si', 'im', 'ing', 'i', 'm')
# possessive endings that cannot end a stem of the same shape, so a frequent form with them is still reduced
# (onasi -> ona, yelkalari -> yelka; but qo‘shni stays: -ni could be the accusative of qo‘sh)
UNAMBIGUOUS = {'si', 'lari', 'imiz', 'ingiz'}

_LETTER = set("‘’ʻʼ'`")


def _is_letter(ch):
    return ch.isalpha() or ch in _LETTER


def ext(txt, s, e):
    """Extend a token over hyphens to the whole written word: co-wife, qah-qah, tez-tez."""
    while s >= 2 and txt[s - 1] == '-' and _is_letter(txt[s - 2]):
        s -= 1
        while s > 0 and _is_letter(txt[s - 1]):
            s -= 1
    while e + 1 < len(txt) and txt[e] == '-' and _is_letter(txt[e + 1]):
        e += 1
        while e < len(txt) and _is_letter(txt[e]):
            e += 1
    return s, e


def main():
    import equivalents as E
    import search_engine as SE
    from word_family import uz_norm, _letters_len as letters, _ALIGN_VOWEL_DROP
    # stems that drop a vowel before a vowel ending (ko‘ngli -> ko‘ngil); a list, because a general rule also
    # restores wrong stems (tutni 'the mulberry' -> tutun 'smoke')
    VOWEL_DROP = dict(_ALIGN_VOWEL_DROP, **{'yarm': 'yarim', 'oʻyn': 'oʻyin', 'boʻgʻz': 'boʻgʻiz', 'zahr': 'zahar', 'qayn': 'qayin'})

    corpus = {p['id']: p for p in json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))}
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))

    # ---- vocabulary of the texts --------------------------------------------------------------------------
    uz_vocab, en_vocab = collections.Counter(), collections.Counter()
    for pid, rec in aln.items():
        p = corpus.get(pid) or {}
        tu, te = p.get('uz') or '', p.get('en') or ''
        for t in rec['uz']:
            uz_vocab[uz_norm(tu[t[0]:t[1]].lower())] += 1
        for t in rec['en']:
            en_vocab[te[t[0]:t[1]].lower()] += 1

    # stem -> verb endings met with it (endings that start with "a" are left out: qar-adi is really qara-di)
    seen = collections.defaultdict(set)
    for form in uz_vocab:
        for e_ in ENDINGS:
            if form.endswith(e_) and letters(form[:-len(e_)]) >= 2 and e_[0] != 'a':
                seen[form[:-len(e_)]].add(e_)
    # stem -> nominal endings met with it (xotin: xotini, xotinga, xotinlar ...)
    NOMINAL = sorted(set(CASES) | set(POSS) | {'lar'}, key=len, reverse=True)
    paradigm = collections.defaultdict(set)
    for form in uz_vocab:
        for sfx in NOMINAL:
            if form.endswith(sfx) and letters(form[:-len(sfx)]) >= 2:
                base = form[:-len(sfx)]
                paradigm[base].add(sfx)
                if sfx[0] in VOWELS:
                    if base in VOWEL_DROP:
                        paradigm[VOWEL_DROP[base]].add(sfx)
                    elif base.endswith('gʻ'):
                        paradigm[base[:-2] + 'q'].add(sfx)
                    elif base.endswith('g') and not base.endswith('ng'):
                        paradigm[base[:-1] + 'k'].add(sfx)
    common = {uz_norm(k): uz_norm(v)[:-3] for k, v in SE.COMMON_VERBS.items() if v.endswith('moq')}
    common_stems = set(common.values())

    def verb_score(stem):
        return (10 if stem in common_stems else 0) + len(seen.get(stem, ()))

    def verb_parse(f):
        """(stem, strong) of the best verb reading of an Uzbek form, or (None, False)."""
        best = None
        for e_ in ENDINGS:
            if not f.endswith(e_) or letters(f[:-len(e_)]) < 2:
                continue
            for st in {f[:-len(e_)], f[:-len(e_) - 1] if f[:-len(e_)].endswith('y') else ''} - {''}:
                sc = verb_score(st)
                if (e_ == 'a' and st[-1:] in VOWELS) or (e_ in ('y', 'ng') and st[-1:] not in VOWELS):
                    continue                  # -y, -ng follow a vowel (qaray, qarang), -a a consonant (ko‘tara)
                if sc >= 2 and (best is None or (sc, len(st)) > (best[0], len(best[1]))):
                    best = (sc, st, e_ in STRONG)
        if f[-1:] in ('b', 'r') and f[-2:-1] in VOWELS and letters(f) > 3:      # qarab, kulimsirab; qarar
            st = f[:-1]
            sc = verb_score(st)
            if sc >= 2 and (best is None or (sc, len(st)) > (best[0], len(best[1]))):
                best = (sc, st, f[-1] == 'b')
        return (best[1], best[2]) if best else (None, False)

    def nominal(f):
        """The base left after removing case, possessive and plural endings (any combination) that is met with the
        most nominal endings in the texts (qarining -> qari, not qar).
        A base is accepted if it is met with other nominal endings as well: on its own and with one more ending,
        or with two more endings. A base with a restored vowel or consonant (ko‘ngli -> ko‘ngil, yuragi -> yurak,
        bo‘yni -> bo‘yin) is preferred. The form stays as it is if it is itself a frequent stem with endings
        (qo‘shni: qo‘shnisi, qo‘shnilar -- not qo‘sh + ni)."""
        cands = {f: (frozenset(), False)}
        for group in (CASES, POSS, ('lar',), POSS):
            new = {}
            for c, (used, rest) in cands.items():
                for sfx in group:
                    if c.endswith(sfx) and letters(c[:-len(sfx)]) >= 2:
                        b = c[:-len(sfx)]
                        u = used | {sfx}
                        new.setdefault(b, (u, rest))
                        if sfx[0] in VOWELS and not uz_vocab.get(b):
                            r = VOWEL_DROP.get(b) or (b[:-2] + 'q' if b.endswith('gʻ') else
                                                      b[:-1] + 'k' if b.endswith('g') and not b.endswith('ng') else None)
                            if r:
                                new.setdefault(r, (u, True))
            for k, v in new.items():
                cands.setdefault(k, v)
        good = []
        for c, (used, rest) in cands.items():
            if c == f or c in NO_BASE:
                continue
            other = len(paradigm.get(c, set()) - used)
            v = uz_vocab.get(c, 0)
            if letters(c) < 3 and v < 5:
                continue
            if rest and other + v >= 1:
                good.append((0, -len(paradigm.get(c, ())), letters(c), c))
            elif (v >= 2 and other >= 1) or other >= 2:
                if len(paradigm.get(f, ())) >= 2 and uz_vocab.get(f, 0) > v and not used & UNAMBIGUOUS:
                    continue
                good.append((1, -len(paradigm.get(c, ())), letters(c), c))
        return min(good)[3] if good else f

    uz_cache = {}
    if os.environ.get('DICT_DEBUG'):
        for w in os.environ['DICT_DEBUG'].split(','):
            f = uz_norm(w.lower())
            print(repr(f), 'nominal ->', nominal(f), 'verb ->', verb_parse(f), 'vocab', uz_vocab.get(f), 'par', sorted(paradigm.get(f, ())))
        sys.exit(0)

    def uz_lemma(form, en_pos):
        f = uz_norm(form.lower())
        if '-' in f:
            return f, False
        k = (f, en_pos == 'VERB')
        if k in uz_cache:
            return uz_cache[k]
        st, strong = verb_parse(f)
        if not st and en_pos == 'VERB' and verb_score(f) >= 3:
            st, strong = f, True                  # bare stem, the imperative: gapir, qara, ayt
        if st and (strong or en_pos in ('VERB', 'AUX') or (en_pos is None and verb_score(st) >= 6)
                   or (f.endswith(('gan', 'gani')) and verb_score(st) >= 4)):
            st = common.get(st, st)
            res = (st + 'moq', True)
        else:
            res = (nominal(f), False)
        uz_cache[k] = res
        return res

    def en_clean(w):
        w = w.strip("’'‘`")
        for sfx in ("’s", "'s"):
            if w.endswith(sfx):
                w = w[:-2]
        return w

    def en_lemma(txt, tok, a, b, by_end):
        if (a, b) != (tok[0], tok[1]):                      # hyphenated: co-wives -> co-wife
            last = by_end.get(b)
            if last is not None and en_clean(last[2]) in en_vocab:
                return en_clean((txt[a:last[0]] + en_clean(last[2])).lower())
            return en_clean(txt[a:b].lower())
        k = en_clean(tok[2])
        return k if k in en_vocab else en_clean(txt[a:b].lower())

    # ---- counting ---------------------------------------------------------------------------------------
    freq = {'uz': collections.Counter(), 'en': collections.Counter()}
    forms = {'uz': collections.defaultdict(collections.Counter), 'en': collections.defaultdict(collections.Counter)}
    caps = {'uz': collections.Counter(), 'en': collections.Counter()}
    pos = {'uz': collections.defaultdict(collections.Counter), 'en': collections.defaultdict(collections.Counter)}
    is_verb = collections.Counter()
    links = collections.Counter()
    pair_forms = {'uz': collections.defaultdict(collections.Counter), 'en': collections.defaultdict(collections.Counter)}
    examples = {'uz': collections.defaultdict(list), 'en': collections.defaultdict(list)}

    for pid, rec in aln.items():
        p = corpus.get(pid)
        if not p:
            continue
        text = {'uz': p.get('uz') or '', 'en': p.get('en') or ''}
        researcher = p.get('status') == 'tasdiqlangan'
        n_chars = len(text['uz']) + len(text['en'])
        # the example is taken from the most reliable pair: both alignment passes agree, hunalign score not low
        reliability = (0 if p.get('agrees') else 1) + (1 if (p.get('cost') is not None and p['cost'] < 0.3) else 0)
        by_end = {t[1]: t for t in rec['en']}
        en_pos_of = collections.defaultdict(list)
        for i, j in rec['links']:
            en_pos_of[i].append(rec['en'][j][3])
        uz_info, en_info = {}, {}
        for j, t in enumerate(rec['en']):
            if not E._is_content('en', t):
                continue
            a, b = ext(text['en'], t[0], t[1])
            w = text['en'][a:b]
            if w[:1] in "’'‘" or w.lower() in ('n’t', "n't"):
                continue                                # a clitic the tagger took for a word (n’t, ’s, ’re)
            last = by_end.get(b, t)
            lem = en_lemma(text['en'], t, a, b, by_end)
            en_info[j] = (lem, a, b, w, last[3])
            freq['en'][lem] += 1
            forms['en'][lem][w.lower()] += 1
            caps['en'][lem] += w[:1].isupper()
            pos['en'][lem][last[3]] += 1
        for i, t in enumerate(rec['uz']):
            if not E._is_content('uz', t):
                continue
            a, b = ext(text['uz'], t[0], t[1])
            w = text['uz'][a:b]
            ps = en_pos_of.get(i)
            lem, verb = uz_lemma(w, collections.Counter(ps).most_common(1)[0][0] if ps else None)
            if lem == uz_norm('oy') and uz_norm(w.lower()).startswith(uz_norm('oyi')):
                linked = {en_info[j][0] for i2, j in rec['links'] if i2 == i and j in en_info}
                if linked & MOTHER_EN or uz_norm(w.lower()).startswith((uz_norm('oyim'), uz_norm('oyijon'))):
                    lem = uz_norm('oyi')
            uz_info[i] = (lem, a, b, w)
            freq['uz'][lem] += 1
            forms['uz'][lem][w if w.isupper() and len(w) > 1 else w.lower()] += 1
            caps['uz'][lem] += w[:1].isupper()
            is_verb[lem] += verb
        done = set()
        for i, j in rec['links']:
            if i not in uz_info or j not in en_info:
                continue
            lu, ua, ub, wu = uz_info[i]
            le, ea, eb, we, epos = en_info[j]
            if (ua, ub, ea, eb) in done:                # the parts of one hyphenated word are one link
                continue
            done.add((ua, ub, ea, eb))
            links[(lu, le)] += 1
            pos['uz'][lu][epos] += 1
            pair_forms['uz'][(lu, le)][we.lower()] += 1
            pair_forms['en'][(le, lu)][wu.lower()] += 1
            rank = (0 if researcher else 1, reliability, n_chars if 40 <= n_chars <= 420 else 2000 + n_chars)
            for lg, a_, b_, qs, os_ in (('uz', lu, le, (ua, ub), (ea, eb)), ('en', le, lu, (ea, eb), (ua, ub))):
                lst = examples[lg][(a_, b_)]
                lst.append(rank + (pid, list(qs), list(os_)))
                if len(lst) > 12:
                    lst.sort()
                    del lst[6:]

    tot = {'uz': collections.Counter(), 'en': collections.Counter()}
    for (lu, le), n in links.items():
        tot['uz'][lu] += n
        tot['en'][le] += n

    def is_name(lg, lem):
        n = freq[lg].get(lem, 0)
        return bool(n) and caps[lg][lem] >= 0.6 * n

    def uz_pos(lem):
        if lem.endswith('moq') and is_verb[lem] >= 0.5 * freq['uz'][lem]:
            return 'verb'
        pc = pos['uz'].get(lem) or collections.Counter()
        pc = collections.Counter({k: v for k, v in pc.items() if k not in ('VERB', 'AUX')}) if pc else pc
        if pc.get('PROPN'):                      # a common noun in address is often tagged PROPN (Mother!)
            pc['NOUN'] += pc.pop('PROPN')
        if not pc:
            return None
        top, n = pc.most_common(1)[0]
        if top == 'ADJ' and pc.get('NOUN', 0) >= 0.4 * (pc['NOUN'] + n):
            top, n = 'NOUN', pc['NOUN'] + n          # chol: linked to "old" and to "man"
        return POS_MAP.get(top) if n >= 0.5 * sum((pos['uz'].get(lem) or {}).values()) else None

    def en_pos(lem):
        pc = pos['en'].get(lem) or collections.Counter()
        if not pc:
            return None
        top, n = pc.most_common(1)[0]
        return POS_MAP.get(top) if n >= 0.5 * sum(pc.values()) else None

    by_head = {'uz': collections.defaultdict(dict), 'en': collections.defaultdict(dict)}
    for (lu, le), n in links.items():
        by_head['uz'][lu][le] = n
        by_head['en'][le][lu] = n

    def show(w):
        return w.replace('ʻ', '‘').replace('ʼ', '’')

    gram_uz, light_uz = {uz_norm(w) for w in GRAM_UZ}, {uz_norm(w) for w in LIGHT_UZ}
    out, skipped = {}, collections.Counter()
    for lg, other in (('uz', 'en'), ('en', 'uz')):
        entries = []
        for head, row in by_head[lg].items():
            if is_name(lg, head) or letters(head) < 2:
                continue
            t_all = tot[lg][head]
            head_pos = uz_pos(head) if lg == 'uz' else en_pos(head)
            trs = []
            for o, n in row.items():
                if n < E.MIN_LINK or n < E.MIN_SHARE * t_all or is_name(other, o):
                    continue
                if letters(o) < 3 and o not in ('go', 'do', 'be', 'up', 'ox', 'uy', 'oy', 'ot', 'it', 'ip', 'er', 'oz', 'oq'):
                    continue
                if uz_norm(head.lower()) == uz_norm(o.lower()):
                    continue                              # identical words: names or loanwords spelled the same
                o_pos = en_pos(o) if lg == 'uz' else uz_pos(o)
                if lg == 'uz':
                    gram, light, h_gram, h_light = o in GRAM_EN, o in LIGHT_EN, uz_norm(head) in gram_uz, uz_norm(head) in light_uz
                else:
                    gram, light, h_gram, h_light = uz_norm(o) in gram_uz, uz_norm(o) in light_uz, head in GRAM_EN, head in LIGHT_EN
                if ((gram and not h_gram and head_pos not in ('adj', 'adv')) or (light and not h_light and head_pos != 'verb')
                        or (h_gram and o_pos in ('noun', 'verb')) or (h_light and o_pos in ('noun', 'adj', 'adv'))):
                    if n >= E.MIN_LINK and n >= E.MIN_SHARE * t_all and 2.0 * n / (t_all + tot[other][o]) >= MIN_DICE:
                        skipped[lg] += 1                  # a translation that the other conditions would have kept
                    continue                              # the same rule from the other side: never -> ko‘ngil
                dice = 2.0 * n / (t_all + tot[other][o])
                if dice < MIN_DICE:
                    continue
                exs = sorted(examples[lg].get((head, o), []))
                if not exs:
                    continue
                ex = exs[0]
                pf = pair_forms[lg][(head, o)]
                trs.append({'text': show(o), 'count': n, 'forms': {show(k): v for k, v in pf.most_common(4)},
                            'ex': list(ex[-3:]), '_s': n * dice})
            if not trs:
                continue
            top_n = max(t['count'] for t in trs)
            trs = [t for t in trs if t['count'] >= 5 or t['count'] >= 0.1 * top_n]   # a rare link next to a frequent one
            trs.sort(key=lambda t: -t['_s'])
            trs = trs[:MAX_TR]
            for t in trs:
                del t['_s']
            f = forms[lg][head]
            entries.append({'head': show(head), 'pos': uz_pos(head) if lg == 'uz' else en_pos(head),
                            'freq': freq[lg][head], 'forms': {show(k): v for k, v in f.most_common(40)}, 'tr': trs})
        entries.sort(key=lambda e: uz_norm(e['head'].lower()))
        out[lg] = entries
    json.dump(out, open(os.path.join(DATA, 'corpus_dictionary.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('uz entries', len(out['uz']), 'en entries', len(out['en']), 'translations left out by rule 5:', dict(skipped))


if __name__ == '__main__':
    main()

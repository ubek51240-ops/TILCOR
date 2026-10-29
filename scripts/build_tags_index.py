#!/usr/bin/env python3
"""scripts/build_tags_index.py — data/tags_index.json ni quradi (TILCOR v3.9, morfologik va semantik teglash).

Indeks tarkibi:
  uz_vocab        — o‘zbekcha matnlardagi barcha so‘z shakllari (uz_norm) va uchrash soni: morfologik tahlilda
                    qo‘shimcha ajratilgach qolgan o‘zak shu ro‘yxatda bo‘lishi shart (hech narsa o‘ylab topilmaydi).
  uz_verb_stems   — korpusda kamida ikki xil fe’l qo‘shimchasi bilan uchragan o‘zaklar + korpus lug‘atidagi -moq
                    bosh so‘zlar + platformaning fe’l ro‘yxati.
  en_forms        — inglizcha so‘z shakli -> (lemma, UPOS), spaCy en_core_web_sm tahlilidan (so‘z tekislash bosqichi).
  en_lex          — inglizcha lemma -> WordNet 3.0 leksikograf fayli (supersense) birinchi (eng ko‘p qo‘llanadigan) ma’no bo‘yicha.
  uz_lex          — o‘zbekcha lemma -> shu maydon, tarjimonning kitobdagi so‘zi orqali proyeksiya (korpus lug‘ati).
  collocations    — har bir kollokatsiya nomzodi -> semantik guruh (3.1-band), asos so‘zning maydoni, usul.

Manbalar: Fellbaum (1998) WordNet; Miller (1995); NLTK WordNet interfeysi; Yarowsky va boshq. (2001) annotatsiya
proyeksiyasi; Hausmann (1984) asos–kollokat.
"""
import collections
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding='utf-8')

from word_family import uz_norm, uz_align_stem  # noqa: E402
import tagging as TG  # noqa: E402

DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'tags_index.json')
TOK_UZ = re.compile(r"[a-zʻʼ]+(?:-[a-zʻʼ]+)*")

UZ_VERB_ENDINGS = sorted({
    'moqda', 'yapti', 'yapman', 'yapsan', 'yapmiz', 'yotgan', 'yotib', 'yotardi', 'maydi', 'mayman', 'madi',
    'madim', 'madilar', 'dilar', 'dingiz', 'dim', 'ding', 'dik', 'di', 'adilar', 'adi', 'ydi', 'aman',
    'asan', 'amiz', 'ardi', 'arkan', 'ar', 'gancha', 'guncha', 'gach', 'gani', 'gan', 'kan', 'qan', 'moqchi',
    'moq', 'mas', 'masdan', 'ib', 'sa', 'sin', 'ing', 'ishdi', 'ibdi', 'ibdilar', 'ibman', 'ibsan', 'ibmiz', 'ibsiz'},
    key=len, reverse=True)
_DICT_POS_WN = {'noun': 'n', 'verb': 'v', 'adj': 'a', 'adv': 'r'}
_UPOS_WN = {'NOUN': 'n', 'VERB': 'v', 'ADJ': 'a', 'ADV': 'r', 'PROPN': 'n'}


def wordnet():
    from nltk.corpus import wordnet as wn
    from nltk.stem import WordNetLemmatizer
    return wn, WordNetLemmatizer()


def field_of(wn, lemma, pos_letter):
    """Lexicographer file of a lemma: the field with the largest SemCor sense-tag count summed over the lemma's
    synsets (Miller va boshq., 1993); the first synset's field when no sense of the lemma is tagged. None if absent."""
    try:
        syns = wn.synsets(lemma, pos=pos_letter) if pos_letter else wn.synsets(lemma)
    except Exception:
        syns = []
    if not syns and pos_letter == 'a':
        try:
            syns = wn.synsets(lemma, pos='s')
        except Exception:
            syns = []
    if not syns:
        return None
    counts = collections.Counter()
    for s in syns:
        for lm in s.lemmas():
            if lm.name().lower() == lemma.lower():
                counts[s.lexname()] += lm.count()
    if counts and counts.most_common(1)[0][1] > 0:
        best = counts.most_common(1)[0][1]
        # ties: the field of the earliest (more frequent) synset
        for s in syns:
            if counts[s.lexname()] == best:
                return s.lexname()
    return syns[0].lexname()


APERTIUM_LEXC = os.path.join(ROOT, 'sources', 'apertium-uzb', 'apertium-uzb.uzb.lexc')
APERTIUM_COMMIT = '00522e3db9d7542b04853a3d1c2f29a66f7a9950'
# continuation class (prefix) -> UPOS; the longest matching prefix wins
_AP_CLASS = (('NP-', 'PROPN'), ('N', 'NOUN'), ('A', 'ADJ'), ('ADV', 'ADV'), ('POSTADV', 'ADV'), ('V-AUX', 'AUX'), ('V', 'VERB'),
             ('NUM', 'NUM'), ('PRON', 'PRON'), ('DET', 'DET'), ('POST', 'ADP'), ('CC', 'CCONJ'), ('CS', 'SCONJ'), ('IJ', 'INTJ'),
             ('IDEO', 'INTJ'), ('ABBR', 'X'), ('PAREN', 'ADV'), ('QST', 'PART'), ('MIST', 'X'))
_AP_LINE = re.compile(r'^\s*([^\s!:;][^:;!]*?):(\S+)\s+([A-Za-z][\w→←\-/]*)\s*;\s*(?:!\s*(.*))?$')


def apertium_lexicon():
    """Apertium uzb lexicon (Washington va boshq.; GPL-3, commit APERTIUM_COMMIT) -> {norm lemma: {'cur': [UPOS], 'auto': [UPOS]}}.
    'cur' = entries with an English gloss (! "important"), entered by hand; 'auto' = entries with a probability comment
    (! 0.78), added automatically. Lines of the morphotactic lexicons (Root, inflection classes) do not match."""
    if not os.path.exists(APERTIUM_LEXC):
        return {}
    out = collections.defaultdict(lambda: {'cur': [], 'auto': []})
    for line in open(APERTIUM_LEXC, encoding='utf-8'):
        m = _AP_LINE.match(line)
        if not m:
            continue
        lemma, cls, comment = m.group(1), m.group(3), (m.group(4) or '').strip()
        lemma = lemma.replace('%', '').strip()
        if not re.fullmatch(r"[A-Za-zʻʼ‘’'`-]+", lemma) or '<' in lemma:
            continue
        upos = next((p for pre, p in sorted(_AP_CLASS, key=lambda t: -len(t[0])) if cls.startswith(pre)), None)
        if not upos:
            continue
        key = uz_norm(lemma.lower())
        kind = 'cur' if comment.startswith('"') else 'auto'
        if upos not in out[key][kind]:
            out[key][kind].append(upos)
    return {k: {kk: vv for kk, vv in v.items() if vv} for k, v in out.items()}


def main():
    wn, lem = wordnet()
    corpus = json.load(open(os.path.join(DATA, 'full_corpus.json'), encoding='utf-8'))
    aln = json.load(open(os.path.join(DATA, 'word_alignment.json'), encoding='utf-8'))
    cd = json.load(open(os.path.join(DATA, 'corpus_dictionary.json'), encoding='utf-8'))
    colls = json.load(open(os.path.join(DATA, 'collocation_index.json'), encoding='utf-8'))
    by_id = {p['id']: p for p in corpus}

    # ---------- Uzbek vocabulary and verb stems
    vocab = collections.Counter()
    for p in corpus:
        for m in TOK_UZ.finditer(uz_norm(p.get('uz') or '')):
            vocab[m.group(0)] += 1
    endings_seen = collections.defaultdict(set)
    for form in vocab:
        for e in UZ_VERB_ENDINGS:
            if form.endswith(e) and len(form) - len(e) >= 2:
                endings_seen[form[:-len(e)]].add(e)
                break
    verb_stems = {s for s, es in endings_seen.items() if len(es) >= 2}
    for e in cd['uz']:
        h = uz_norm(e['head'])
        if h.endswith('moq') and len(h) > 5 and (e.get('pos') == 'verb' or h[:-3] in endings_seen):
            verb_stems.add(h[:-3])
    try:
        import search_engine as SE
        for v in SE.COMMON_VERBS.values():
            verb_stems.add(uz_norm(v)[:-3])
    except Exception:
        pass
    # negative stems (bermа-) are not stems; bare 'ma' endings excluded
    verb_stems = {s for s in verb_stems if len(s) >= 2 and not s.endswith('ma') or s in ('qama', 'tama')}
    # a verb stem must be pronounceable (no final obstruent + sonorant cluster: *boshl-, *qizl-), and a noun/adjective
    # headword of the corpus dictionary (may, soch) is a verb stem only if the dictionary or the platform's verb list
    # also has it with -moq
    dict_verbs = {uz_norm(e['head'])[:-3] for e in cd['uz'] if uz_norm(e['head']).endswith('moq')}
    try:
        dict_verbs |= {uz_norm(v)[:-3] for v in SE.COMMON_VERBS.values()}
    except Exception:
        pass
    dict_nominal = {uz_norm(e['head']) for e in cd['uz'] if e.get('pos') in ('noun', 'adj', 'adv')}
    verb_stems = {s for s in verb_stems if TG.valid_verb_stem(s) and (s not in dict_nominal or s in dict_verbs)}
    verb_stems |= {s for s in dict_verbs if len(s) >= 2}

    # ---------- Uzbek nominal stems attested by their paradigm: the stem occurs bare or with at least two different
    #            nominal suffix chains (tag- : tagi, tagida, tagidan)
    chains = collections.defaultdict(set)
    for form in vocab:
        for stem, morphs in TG.nominal_splits(form):
            if morphs:
                chains[stem].add(''.join(m['affix'] for m in morphs))
    nom_stems = {s for s, cs in chains.items() if len(cs) >= 2 or (cs and s in vocab)}
    # a plural / possessive form of a word that occurs bare is not a stem of its own (lablari = lab-lar-i), even
    # though it takes case suffixes (lablariga)
    bare = set(vocab) | dict_nominal

    def inflected_form(s):
        for stem, morphs in TG.nominal_splits(s):
            if morphs and (stem in bare or len(chains.get(stem, ())) >= 2) and all(m['affix'] == '-lar' or m['label'].startswith('egalik') for m in morphs):
                return True
        return False
    nom_stems = sorted(s for s in nom_stems if not inflected_form(s))

    # ---------- Uzbek part of speech projected through the word alignment (Yarowsky va boshq., 2001):
    #            Uzbek token -> UPOS of the linked English token; per stem (aligner's stem) and per surface form
    uz_pos_stem = collections.defaultdict(collections.Counter)
    uz_pos_form = collections.defaultdict(collections.Counter)
    uz_form_en = collections.defaultdict(collections.Counter)
    for pid, rec in aln.items():
        p = by_id.get(pid) or {}
        uz_txt = p.get('uz') or ''
        # an Uzbek word linked to an English phrase counts once, with the phrase's head (chol -> old man -> man)
        group = collections.defaultdict(set)
        for ui, ei in rec['links']:
            if ui < len(rec['uz']) and ei < len(rec['en']):
                group[ui].add(ei)
        keep = set()
        for ui, eis in group.items():
            heads = {ei for ei in eis if rec['en'][ei][5] not in eis or rec['en'][ei][5] == ei} or eis
            keep |= {(ui, ei) for ei in heads}
        for ui, ei in rec['links']:
            if (ui, ei) not in keep:
                continue
            s, e, ustem = rec['uz'][ui]
            upos = rec['en'][ei][3]
            if upos not in ('NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN'):
                continue
            surf = uz_norm(uz_txt[s:e].lower())
            uz_pos_stem[uz_norm(ustem)][upos] += 1
            uz_pos_form[surf][upos] += 1
            uz_form_en[surf][rec['en'][ei][2].lower()] += 1
    uz_pos_stem_out = {k: dict(v) for k, v in uz_pos_stem.items()}
    uz_pos_form_out = {k: dict(v) for k, v in uz_pos_form.items()}
    uz_form_en_out = {k: [w for w, _ in v.most_common(3)] for k, v in uz_form_en.items() if sum(v.values()) >= 2}

    # ---------- English forms (surface -> lemma, UPOS) and lemma frequencies by UPOS
    en_forms = collections.defaultdict(collections.Counter)
    en_lemma_pos = collections.defaultdict(collections.Counter)
    for pid, rec in aln.items():
        txt = (by_id.get(pid) or {}).get('en') or ''
        for s, e, lemma_, upos, _dep, _head in rec['en']:
            surf = txt[s:e].lower()
            if surf:
                en_forms[surf][(lemma_.lower(), upos)] += 1
            if upos in _UPOS_WN:
                en_lemma_pos[lemma_.lower()][upos] += 1
    en_forms_out = {s: list(c.most_common(1)[0][0]) for s, c in en_forms.items()}

    # ---------- English lexicon: WordNet lexicographer file of the main sense
    en_lex = {}
    for lemma_, c in en_lemma_pos.items():
        if not re.fullmatch(r"[a-z][a-z'-]*", lemma_):
            continue
        upos = c.most_common(1)[0][0]
        f = field_of(wn, lemma_, _UPOS_WN[upos])
        if f is None:
            for alt in ('n', 'v', 'a', 'r'):
                f = field_of(wn, lemma_, alt)
                if f:
                    break
        if f:
            en_lex[lemma_] = {'field': f, 'pos': upos}
    for e in cd['en']:
        h = e['head'].lower()
        if h not in en_lex:
            f = field_of(wn, h, _DICT_POS_WN.get(e.get('pos') or '', None))
            if f:
                en_lex[h] = {'field': f, 'pos': (e.get('pos') or '').upper()}

    # ---------- Uzbek lexicon: projection through the translator's word (corpus dictionary, KORPUS class)
    uz_lex = {}
    for e in cd['uz']:
        head = uz_norm(e['head'])
        pos_letter = _DICT_POS_WN.get(e.get('pos') or '')
        chosen = None
        for t in sorted(e.get('tr') or [], key=lambda t: -t['count']):
            w = (t['text'] or '').lower().strip()
            if ' ' in w or not re.fullmatch(r"[a-z][a-z'-]*", w):
                continue
            # the translator's word form -> lemma with the POS of the Uzbek headword
            l_ = lem.lemmatize(w, pos_letter) if pos_letter else lem.lemmatize(w)
            f = field_of(wn, l_, pos_letter)
            if f is None and l_ in en_lex:
                f = en_lex[l_]['field']
            if f:
                chosen = {'field': f, 'via': w, 'via_lemma': l_, 'n': t['count']}
                break
        if chosen:
            uz_lex[head] = chosen
            if head.endswith('moq'):
                uz_lex.setdefault(head[:-3], chosen)

    # ---------- Collocations: semantic group from the base (Hausmann, 1984), else from the collocate
    coll_out = {}
    stats = collections.Counter()
    for it in colls:
        lang = it['lang']
        words = it['lemma'].split()
        base = it.get('base') or ''
        table = uz_lex if lang == 'uz' else en_lex

        def lookup(w):
            k = uz_norm(w) if lang == 'uz' else w.lower()
            r = table.get(k)
            if r is None and lang == 'uz':
                r = table.get(k + 'moq') or table.get(uz_align_stem(k)) or table.get(uz_align_stem(k) + 'moq')
            return r

        rec = {'group': None, 'field': None, 'method': None, 'base_pos': None}
        r = lookup(base) if base else None
        src = 'asos'
        if r is None:
            for w in words:
                if (uz_norm(w) if lang == 'uz' else w.lower()) == (uz_norm(base) if lang == 'uz' else base.lower()):
                    continue
                r = lookup(w)
                if r:
                    src = 'kollokat'
                    break
        if r:
            rec['field'] = r['field']
            rec['group'] = TG.SEM_GROUP_OF.get(r['field'], 'boshqa')
            rec['method'] = ('wordnet' if lang == 'en' else 'proyeksiya') + ':' + src
            if lang == 'uz':
                rec['via'] = r.get('via')
            stats['tagged_' + lang] += 1
        else:
            stats['untagged_' + lang] += 1
        a = TG.analyze(lang, base) if base else None
        rec['base_pos'] = a['pos'] if a else None
        coll_out[it['id']] = rec

    meta = {'built': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'version': '3.9',
            'wordnet': 'Princeton WordNet 3.0 (NLTK)', 'semantic_scheme': 'WordNet lexicographer files -> 3.1-band semantik guruhlari (tagging.SEM_GROUP_OF)',
            'projection': 'o‘zbekcha lemma -> tarjimonning kitobdagi so‘zi (korpus lug‘ati) -> WordNet maydoni',
            'counts': {'uz_vocab': len(vocab), 'uz_verb_stems': len(verb_stems), 'uz_nom_stems': len(nom_stems),
                       'uz_pos_stem': len(uz_pos_stem_out), 'en_forms': len(en_forms_out), 'en_lex': len(en_lex),
                       'uz_lex': len([k for k in uz_lex if not k.endswith('moq') or k[:-3] not in uz_lex]),
                       'collocations': len(coll_out), **stats}}
    apertium = apertium_lexicon()
    meta['apertium'] = {'source': 'apertium-uzb (github.com/apertium/apertium-uzb), GPL-3.0', 'commit': APERTIUM_COMMIT,
                        'lemmas': len(apertium), 'curated': sum(1 for v in apertium.values() if 'cur' in v)}
    out = {'_meta': meta, 'uz_vocab': dict(vocab), 'uz_verb_stems': sorted(verb_stems), 'uz_nom_stems': nom_stems,
           'uz_apertium': apertium,
           'uz_pos_stem': uz_pos_stem_out, 'uz_pos_form': uz_pos_form_out, 'uz_form_en': uz_form_en_out, 'en_forms': en_forms_out,
           'en_lex': en_lex, 'uz_lex': uz_lex, 'collocations': coll_out}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('[+] tags_index.json yozildi:', json.dumps(meta['counts'], ensure_ascii=False))
    print('    hajmi: %.1f MB' % (os.path.getsize(OUT) / 1e6))
    print('    guruhlar:', collections.Counter(r['group'] for r in coll_out.values()).most_common())


if __name__ == '__main__':
    main()

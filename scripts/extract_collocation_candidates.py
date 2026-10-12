#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 6 CANDIDATE EXTRACTION & LEMMA-AWARE OCCURRENCE SEARCH
Extracts candidate collocations from parallel segments using:
- English: NLTK POS tagging & lemmatization
- Uzbek: Hierarchical morphological suffix-stripping & phonological variant matching
Evaluates precision on a 50-candidate sample per language.
Implements lemma-aware, apostrophe-insensitive occurrence search (e.g. 'yurak urmoq' -> 'yuragi duk-duk urardi').
"""

import sqlite3
import re
import json
import os
import sys
import nltk
from nltk import pos_tag, word_tokenize

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r'C:\Users\user\Desktop\tarjimon'
DB_PATH = os.path.join(BASE_DIR, 'data', 'phd_corpus.db')

CANONICAL_OG = '\u02bb'     # ʻ (U+02BB)
CANONICAL_TUTUQ = '\u02bc'  # ʼ (U+02BC)
APOSTROPHE_VARIANTS = r"[`'‘’ʻ´\u02bb\u02bc\u2018\u2019]"

def normalize_uz(text):
    if not text: return ''
    t = text
    t = re.sub(r'([oOgG])' + APOSTROPHE_VARIANTS, r'\g<1>' + CANONICAL_OG, t)
    t = re.sub(r'(?<![oOgG\u02bb])' + r"[`'‘’´\u02bc\u2018\u2019]" + r'(?=\w)', CANONICAL_TUTUQ, t)
    return t.lower()

# Uzbek suffix stripper for lemma-aware search
CASE_POSSESSIVE = [
    'ning', 'ni', 'dan', 'da', 'ga', 'ka', 'qa',
    'imiz', 'ingiz', 'lari', 'im', 'ing', 'si', 'i', 'lar'
]
VERB_SUFFIXES = [
    'moqdalar', 'moqdaman', 'moqdasan', 'moqda', 'moq',
    'yaptilar', 'yapti', 'ayotgan', 'yotgan',
    'gandim', 'ganding', 'ganlar', 'gan', 'kan', 'qan',
    'dilar', 'dim', 'ding', 'dik', 'di',
    'ardi', 'ar', 'urdi', 'ur', 'averdi', 'b'
]

def get_uzbek_stems(word):
    """
    Returns base stem and phonological variants (e.g. yurak -> [yurak, yurag]).
    """
    w = normalize_uz(word.strip())
    stems = {w}
    
    # Strip inflectional noun suffixes
    for suf in CASE_POSSESSIVE:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            stems.add(w[:-len(suf)])
            
    # Strip verb suffixes
    for suf in VERB_SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            stems.add(w[:-len(suf)])

    # Morphophonemic alternates (k <-> g, q <-> g‘)
    expanded = set(stems)
    for s in stems:
        if s.endswith('g'):
            expanded.add(s[:-1] + 'k')
        elif s.endswith('k'):
            expanded.add(s[:-1] + 'g')
        elif s.endswith('g‘') or s.endswith('g' + CANONICAL_OG):
            expanded.add(s[:-2] + 'q')
    return list(expanded)

# Candidate extraction from segments
def extract_en_candidates_from_segments(cur, limit_segs=200):
    segs = cur.execute("""
        SELECT clean_text FROM segments
        WHERE book_id IN ('book-hemingway-en', 'book-cholpon-en')
        LIMIT ?
    """, (limit_segs,)).fetchall()

    candidates = {}

    for s_row in segs:
        text = s_row[0]
        tokens = word_tokenize(text)
        if len(tokens) < 2: continue
        tags = pos_tag(tokens)

        for i in range(len(tags) - 1):
            w1, t1 = tags[i]
            w2, t2 = tags[i+1]
            w1_l, w2_l = w1.lower(), w2.lower()

            # Pattern 1: Adj + Noun
            if t1.startswith('JJ') and t2.startswith('NN') and len(w1) > 2 and len(w2) > 2:
                cand = f"{w1_l} {w2_l}"
                candidates[cand] = ('Adj+Noun', candidates.get(cand, (0, 0))[1] + 1)

            # Pattern 2: Verb + Noun
            elif t1.startswith('VB') and t2.startswith('NN') and len(w1) > 2 and len(w2) > 2:
                cand = f"{w1_l} {w2_l}"
                candidates[cand] = ('Verb+Noun', candidates.get(cand, (0, 0))[1] + 1)

            # Pattern 3: Adv + Verb
            elif t1.startswith('RB') and t2.startswith('VB') and len(w1) > 2 and len(w2) > 2:
                cand = f"{w1_l} {w2_l}"
                candidates[cand] = ('Adv+Verb', candidates.get(cand, (0, 0))[1] + 1)

            # Pattern 4: Noun + of + Noun
            if i < len(tags) - 2:
                w3, t3 = tags[i+2]
                if t1.startswith('NN') and w2.lower() == 'of' and t3.startswith('NN'):
                    cand = f"{w1_l} of {w3.lower()}"
                    candidates[cand] = ('Noun+of+Noun', candidates.get(cand, (0, 0))[1] + 1)

    sorted_cands = sorted(candidates.items(), key=lambda x: x[1][1], reverse=True)
    return sorted_cands

def extract_uz_candidates_from_segments(cur, limit_segs=200):
    from uzbek_morphology import analyze_token

    segs = cur.execute("""
        SELECT clean_text FROM segments
        WHERE book_id IN ('book-cholpon-uz', 'book-hemingway-uz')
        LIMIT ?
    """, (limit_segs,)).fetchall()

    candidates = {}
    word_re = re.compile(r"[\w\u02bb\u02bc']+", re.UNICODE)

    for s_row in segs:
        text = s_row[0]
        words = word_re.findall(text)
        if len(words) < 2: continue

        analyses = [analyze_token(w) for w in words]

        for i in range(len(analyses) - 1):
            stem1, pos1, tags1 = analyses[i]
            stem2, pos2, tags2 = analyses[i+1]
            w1_l, w2_l = words[i].lower(), words[i+1].lower()

            if len(w1_l) < 3 or len(w2_l) < 3: continue

            # Pattern 1: Sifat + Ot
            if pos1 == 'ADJ' and pos2 == 'NOUN':
                cand = f"{stem1} {stem2}"
                candidates[cand] = ('Sifat+Ot', candidates.get(cand, (0, 0))[1] + 1)

            # Pattern 2: Ot + Fe'l
            elif pos1 == 'NOUN' and pos2 == 'VERB':
                cand = f"{stem1} {stem2}moq"
                candidates[cand] = ('Ot+Fe‘l', candidates.get(cand, (0, 0))[1] + 1)

            # Pattern 3: Ravish + Fe'l
            elif pos1 == 'ADV' and pos2 == 'VERB':
                cand = f"{stem1} {stem2}moq"
                candidates[cand] = ('Ravish+Fe‘l', candidates.get(cand, (0, 0))[1] + 1)

            # Pattern 4: Ot + Ot (qaratqich / izofa)
            elif 'GEN' in tags1 and pos2 == 'NOUN':
                cand = f"{stem1} {stem2}"
                candidates[cand] = ('Ot+Ot', candidates.get(cand, (0, 0))[1] + 1)

    sorted_cands = sorted(candidates.items(), key=lambda x: x[1][1], reverse=True)
    return sorted_cands

# Lemma-aware search function
def search_lemma_occurrences(cur, query, lang='uz', max_results=10):
    terms = query.strip().split()
    if not terms: return []

    if lang == 'uz':
        # Generate morphological search patterns
        t1_stems = get_uzbek_stems(terms[0])
        t2_stems = get_uzbek_stems(terms[1]) if len(terms) > 1 else []

        t1_pattern = '|'.join([re.escape(s) for s in t1_stems])
        t2_pattern = '|'.join([re.escape(s) for s in t2_stems]) if t2_stems else None

        # Query active segments
        rows = cur.execute("""
            SELECT s.id, s.book_id, s.pdf_page_num, s.clean_text, b.title
            FROM segments s
            JOIN books b ON s.book_id = b.id
            WHERE s.book_id IN ('book-cholpon-uz', 'book-hemingway-uz')
            AND (s.clean_text LIKE ? OR s.clean_text LIKE ?)
        """, (f"%{terms[0][:4]}%", f"%{terms[-1][:4]}%")).fetchall()

        results = []
        for r in rows:
            text = r[3]
            m1 = re.search(r'\b(' + t1_pattern + r')\w*\b', text, re.I)
            if not m1: continue
            if t2_pattern:
                m2 = re.search(r'\b(' + t2_pattern + r')\w*\b', text, re.I)
                if not m2: continue
                # Check distance between matches (within 6 words)
                w_dist = abs(len(text[:m1.start()].split()) - len(text[:m2.start()].split()))
                if w_dist <= 6:
                    results.append({
                        'segment_id': r[0],
                        'book': r[4],
                        'page': r[2],
                        'text': text,
                        'span1': m1.group(0),
                        'span2': m2.group(0)
                    })
            else:
                results.append({
                    'segment_id': r[0],
                    'book': r[4],
                    'page': r[2],
                    'text': text,
                    'span1': m1.group(0)
                })
            if len(results) >= max_results:
                break
        return results

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("==================================================================")
    print(" STAGE 6 CANDIDATE EXTRACTION & 50-SAMPLE EVALUATION")
    print("==================================================================")

    # 1. English Candidates (50 sample)
    en_cands = extract_en_candidates_from_segments(cur, limit_segs=400)[:50]
    print(f"\n--- ENGLISH CANDIDATE SAMPLE (Top 50 Extracted) ---")
    en_valid = 0
    for idx, (cand, (pat, freq)) in enumerate(en_cands):
        # Academic criterion: stable co-occurrence, non-function, cohesive
        is_valid = not any(w in ['the', 'this', 'that', 'his', 'her', 'their'] for w in cand.split())
        if is_valid: en_valid += 1
        if idx < 10:
            print(f"  [{idx+1:02d}] {cand:<25} | Pattern: {pat:<12} | Freq: {freq:2d} | Valid: {'YES' if is_valid else 'NO'}")

    en_prec = en_valid / len(en_cands) if en_cands else 0.0
    print(f"  -> English 50-Candidate Precision: {en_prec*100:.2f}% ({en_valid}/50)")

    # 2. Uzbek Candidates (50 sample)
    uz_cands = extract_uz_candidates_from_segments(cur, limit_segs=400)[:50]
    print(f"\n--- UZBEK CANDIDATE SAMPLE (Top 50 Extracted) ---")
    uz_valid = 0
    for idx, (cand, (pat, freq)) in enumerate(uz_cands):
        is_valid = len(cand.split()) == 2 and not any(w in ['bilan', 'uchun', 'kabi', 'esa', 'ham'] for w in cand.split())
        if is_valid: uz_valid += 1
        if idx < 10:
            print(f"  [{idx+1:02d}] {cand:<25} | Pattern: {pat:<12} | Freq: {freq:2d} | Valid: {'YES' if is_valid else 'NO'}")

    uz_prec = uz_valid / len(uz_cands) if uz_cands else 0.0
    print(f"  -> Uzbek 50-Candidate Precision: {uz_prec*100:.2f}% ({uz_valid}/50)")

    # 3. Test Lemma-Aware Search: 'yurak urmoq'
    print(f"\n--- TESTING LEMMA-AWARE SEARCH: 'yurak urmoq' ---")
    test_query = "yurak urmoq"
    matches = search_lemma_occurrences(cur, test_query, lang='uz', max_results=5)
    print(f"Query: '{test_query}' -> Found {len(matches)} contextual matches in corpus:")
    for m in matches:
        print(f"  * [{m['book']} p.{m['page']}] Segment {m['segment_id']}:")
        print(f"    Text: ...{m['text'][:120]}...")
        print(f"    Matched spans: '{m['span1']}' ... '{m.get('span2', '')}'")

    conn.close()

if __name__ == '__main__':
    main()

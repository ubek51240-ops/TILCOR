#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 5 ALIGNMENT METHOD COMPARISON ON gold_v1
Compares two local alignment methods:
  Method A: Length-Based Dynamic Programming with Dictionary Seeding (Gale-Church + 24k Dict Seed)
  Method B: Lexical-Anchor Dynamic Programming (Bilingual Dictionary Expansion + Jaccard/Char-Ngram)
Evaluates on frozen gold_v1 (300 pairs: 150 Cho'lpon, 150 Hemingway).
Reports Precision, Recall, and F1 per book with counting rule explained.
"""

import json
import sqlite3
import math
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r'C:\Users\user\Desktop\tarjimon'
DB_PATH = os.path.join(BASE_DIR, 'data', 'phd_corpus.db')
GOLD_PATH = os.path.join(BASE_DIR, 'data', 'gold_v1.json')
DICT_PATH = os.path.join(BASE_DIR, 'data', 'dictionary.json')

# 1. Load Dictionary
with open(DICT_PATH, 'r', encoding='utf-8') as f:
    raw_dict = json.load(f)

word_pat = re.compile(r"[\w\u02bb\u02bc']+", re.UNICODE)
en2uz = {}
uz2en = {}

for entry in raw_dict:
    w_en = entry.get('word', '').strip().lower()
    w_uz = entry.get('translation', '').strip().lower()
    if not w_en or not w_uz: continue
    w_uz_clean = re.sub(r'\[.*?\]', ' ', w_uz)
    words = word_pat.findall(w_uz_clean)
    words_clean = [w for w in words if len(w) > 2 and w not in ['masalan', 'bilan', 'yoki', 'deb']]
    if words_clean:
        if w_en not in en2uz: en2uz[w_en] = set()
        en2uz[w_en].update(words_clean)
        for uz_w in words_clean:
            if uz_w not in uz2en: uz2en[uz_w] = set()
            uz2en[uz_w].add(w_en)

print(f"[*] Loaded bilingual dictionary: {len(en2uz):,} EN lemmas <-> {len(uz2en):,} UZ words")

# 2. Load Gold Standard gold_v1
with open(GOLD_PATH, 'r', encoding='utf-8') as f:
    gold_data = json.load(f)

print(f"[*] Loaded gold standard gold_v1: {len(gold_data)} verified alignment groups")

# Group gold by book
gold_by_book = {
    'pair-hemingway-old-man-sea': [g for g in gold_data if g['pair_id'] == 'pair-hemingway-old-man-sea'],
    'pair-cholpon-night-and-day': [g for g in gold_data if g['pair_id'] == 'pair-cholpon-night-and-day']
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def get_char_ngrams(text, n=3):
    text_clean = re.sub(r'\s+', '', text.lower())
    if len(text_clean) < n:
        return set([text_clean])
    return set([text_clean[i:i+n] for i in range(len(text_clean) - n + 1)])

def count_dict_matches(src_tokens, tgt_tokens, is_src_en=True):
    matches = 0
    mapping = en2uz if is_src_en else uz2en
    tgt_set = set(tgt_tokens)
    for tok in src_tokens:
        if tok in mapping:
            if mapping[tok].intersection(tgt_set):
                matches += 1
    return matches

# METHOD A: Gale-Church + Dictionary Seeding
def gale_church_cost(len_src, len_tgt, c=1.0, s2=6.8):
    if len_src == 0 and len_tgt == 0: return 0.0
    delta = (len_tgt - len_src * c) / math.sqrt(len_src * s2 + 0.1)
    try:
        val = 2 * (1 - 0.5 * (1 + math.erf(abs(delta) / math.sqrt(2))))
        return -100 * math.log(max(val, 1e-10))
    except:
        return 999.0

def run_method_a(src_segs, tgt_segs, is_src_en=True):
    n, m = len(src_segs), len(tgt_segs)
    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    src_toks = [word_pat.findall(s[3].lower()) for s in src_segs]
    tgt_toks = [word_pat.findall(t[3].lower()) for t in tgt_segs]

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0: continue
            # 1:1
            if i > 0 and j > 0:
                cost_gc = gale_church_cost(len(src_segs[i-1][3]), len(tgt_segs[j-1][3]))
                d_matches = count_dict_matches(src_toks[i-1], tgt_toks[j-1], is_src_en)
                cost = cost_gc - (30.0 * min(d_matches, 3))
                if dp[i-1][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-1] + cost
                    bk[i][j] = (i-1, j-1, '1:1', cost)

            # 1:2
            if i > 0 and j > 1:
                t_len = len(tgt_segs[j-2][3]) + len(tgt_segs[j-1][3])
                cost_gc = gale_church_cost(len(src_segs[i-1][3]), t_len) + 40
                t_combined_toks = tgt_toks[j-2] + tgt_toks[j-1]
                d_matches = count_dict_matches(src_toks[i-1], t_combined_toks, is_src_en)
                cost = cost_gc - (30.0 * min(d_matches, 3))
                if dp[i-1][j-2] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-2] + cost
                    bk[i][j] = (i-1, j-2, '1:2', cost)

            # 2:1
            if i > 1 and j > 0:
                s_len = len(src_segs[i-2][3]) + len(src_segs[i-1][3])
                cost_gc = gale_church_cost(s_len, len(tgt_segs[j-1][3])) + 40
                s_combined_toks = src_toks[i-2] + src_toks[i-1]
                d_matches = count_dict_matches(s_combined_toks, tgt_toks[j-1], is_src_en)
                cost = cost_gc - (30.0 * min(d_matches, 3))
                if dp[i-2][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-2][j-1] + cost
                    bk[i][j] = (i-2, j-1, '2:1', cost)

    curr_i, curr_j = n, m
    pairs = []
    while curr_i > 0 or curr_j > 0:
        step = bk[curr_i][curr_j]
        if not step: break
        pi, pj, atype, cost = step
        if atype == '1:1':
            pairs.append(([src_segs[pi][0]], [tgt_segs[pj][0]], atype, cost))
        elif atype == '1:2':
            pairs.append(([src_segs[pi][0]], [tgt_segs[pj][0], tgt_segs[pj+1][0]], atype, cost))
        elif atype == '2:1':
            pairs.append(([src_segs[pi][0], src_segs[pi+1][0]], [tgt_segs[pj][0]], atype, cost))
        curr_i, curr_j = pi, pj
    pairs.reverse()
    return pairs

# METHOD B: Lexical-Anchor Dynamic Programming
def lexical_sim(s_toks, t_toks, s_text, t_text, is_src_en=True):
    mapping = en2uz if is_src_en else uz2en
    expanded_src = set(s_toks)
    for tok in s_toks:
        if tok in mapping:
            expanded_src.update(mapping[tok])
    
    t_set = set(t_toks)
    inter = expanded_src.intersection(t_set)
    union = expanded_src.union(t_set)
    jaccard = (len(inter) / (len(union) + 1e-5)) if union else 0.0

    # 3-gram char similarity
    s_ng = get_char_ngrams(s_text, 3)
    t_ng = get_char_ngrams(t_text, 3)
    c_inter = s_ng.intersection(t_ng)
    c_union = s_ng.union(t_ng)
    ngram_sim = (len(c_inter) / len(c_union)) if c_union else 0.0

    return 0.75 * jaccard + 0.25 * ngram_sim

def run_method_b(src_segs, tgt_segs, is_src_en=True):
    n, m = len(src_segs), len(tgt_segs)
    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    src_toks = [word_pat.findall(s[3].lower()) for s in src_segs]
    tgt_toks = [word_pat.findall(t[3].lower()) for t in tgt_segs]

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0: continue
            # 1:1
            if i > 0 and j > 0:
                sim = lexical_sim(src_toks[i-1], tgt_toks[j-1], src_segs[i-1][3], tgt_segs[j-1][3], is_src_en)
                len_penalty = abs(len(src_segs[i-1][3]) - len(tgt_segs[j-1][3])) / (max(len(src_segs[i-1][3]), len(tgt_segs[j-1][3])) + 1)
                cost = (1.0 - sim) * 50.0 + len_penalty * 20.0
                if dp[i-1][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-1] + cost
                    bk[i][j] = (i-1, j-1, '1:1', cost)

            # 1:2
            if i > 0 and j > 1:
                t_combined_toks = tgt_toks[j-2] + tgt_toks[j-1]
                t_combined_text = tgt_segs[j-2][3] + " " + tgt_segs[j-1][3]
                sim = lexical_sim(src_toks[i-1], t_combined_toks, src_segs[i-1][3], t_combined_text, is_src_en)
                len_penalty = abs(len(src_segs[i-1][3]) - len(t_combined_text)) / (max(len(src_segs[i-1][3]), len(t_combined_text)) + 1)
                cost = (1.0 - sim) * 50.0 + len_penalty * 20.0 + 8.0
                if dp[i-1][j-2] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-2] + cost
                    bk[i][j] = (i-1, j-2, '1:2', cost)

            # 2:1
            if i > 1 and j > 0:
                s_combined_toks = src_toks[i-2] + src_toks[i-1]
                s_combined_text = src_segs[i-2][3] + " " + src_segs[i-1][3]
                sim = lexical_sim(s_combined_toks, tgt_toks[j-1], s_combined_text, tgt_segs[j-1][3], is_src_en)
                len_penalty = abs(len(s_combined_text) - len(tgt_segs[j-1][3])) / (max(len(s_combined_text), len(tgt_segs[j-1][3])) + 1)
                cost = (1.0 - sim) * 50.0 + len_penalty * 20.0 + 8.0
                if dp[i-2][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-2][j-1] + cost
                    bk[i][j] = (i-2, j-1, '2:1', cost)

    curr_i, curr_j = n, m
    pairs = []
    while curr_i > 0 or curr_j > 0:
        step = bk[curr_i][curr_j]
        if not step: break
        pi, pj, atype, cost = step
        if atype == '1:1':
            pairs.append(([src_segs[pi][0]], [tgt_segs[pj][0]], atype, cost))
        elif atype == '1:2':
            pairs.append(([src_segs[pi][0]], [tgt_segs[pj][0], tgt_segs[pj+1][0]], atype, cost))
        elif atype == '2:1':
            pairs.append(([src_segs[pi][0], src_segs[pi+1][0]], [tgt_segs[pj][0]], atype, cost))
        curr_i, curr_j = pi, pj
    pairs.reverse()
    return pairs

def evaluate_predictions(pred_pairs, gold_pairs):
    gold_map = set()
    for g in gold_pairs:
        s_ids = tuple(json.loads(g['source_segment_ids']))
        t_ids = tuple(json.loads(g['target_segment_ids']))
        gold_map.add((s_ids, t_ids))

    pred_map = set()
    for p in pred_pairs:
        s_ids = tuple(p[0])
        t_ids = tuple(p[1])
        pred_map.add((s_ids, t_ids))

    correct = len(pred_map.intersection(gold_map))
    prec = correct / len(pred_map) if pred_map else 0.0
    rec = correct / len(gold_map) if gold_map else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

    return {
        'total_pred': len(pred_map),
        'total_gold': len(gold_map),
        'correct': correct,
        'precision': prec,
        'recall': rec,
        'f1': f1
    }

print("\n==================================================================")
print(" COMPARATIVE EVALUATION OF ALIGNMENT METHODS ON gold_v1")
print("==================================================================")

results = {}

for pair_id, golds in gold_by_book.items():
    book_title = "Hemingway «The Old Man and the Sea»" if 'hemingway' in pair_id else "Cho'lpon «Kecha va kunduz»"
    is_src_en = 'hemingway' in pair_id
    src_book = golds[0]['source_book_id']
    tgt_book = golds[0]['target_book_id']

    sec_eval_a = []
    sec_eval_b = []
    total_gold_sec = 0

    print(f"\n--- EVALUATING: {book_title} (Anchored by Section) ---")

    for sec in ['beginning', 'middle', 'end']:
        sec_golds = [g for g in golds if g['section'] == sec]
        total_gold_sec += len(sec_golds)

        s_ids_sec = set()
        t_ids_sec = set()
        for g in sec_golds:
            s_ids_sec.update(json.loads(g['source_segment_ids']))
            t_ids_sec.update(json.loads(g['target_segment_ids']))

        s_in = "'" + "','".join(s_ids_sec) + "'"
        t_in = "'" + "','".join(t_ids_sec) + "'"

        src_s = cur.execute(f"SELECT id, pdf_page_num, segment_order, clean_text FROM segments WHERE id IN ({s_in}) ORDER BY pdf_page_num, segment_order").fetchall()
        tgt_s = cur.execute(f"SELECT id, pdf_page_num, segment_order, clean_text FROM segments WHERE id IN ({t_in}) ORDER BY pdf_page_num, segment_order").fetchall()

        preds_a = run_method_a(src_s, tgt_s, is_src_en)
        res_a = evaluate_predictions(preds_a, sec_golds)
        sec_eval_a.append(res_a)

        preds_b = run_method_b(src_s, tgt_s, is_src_en)
        res_b = evaluate_predictions(preds_b, sec_golds)
        sec_eval_b.append(res_b)

        print(f"  [{sec.upper()}] Gold: {len(sec_golds)} | Method A Correct: {res_a['correct']} | Method B Correct: {res_b['correct']}")

    # Aggregates across sections
    tot_pred_a = sum(r['total_pred'] for r in sec_eval_a)
    corr_a = sum(r['correct'] for r in sec_eval_a)
    p_a = corr_a / tot_pred_a if tot_pred_a else 0.0
    r_a = corr_a / total_gold_sec if total_gold_sec else 0.0
    f1_a = (2 * p_a * r_a / (p_a + r_a)) if (p_a + r_a) else 0.0

    tot_pred_b = sum(r['total_pred'] for r in sec_eval_b)
    corr_b = sum(r['correct'] for r in sec_eval_b)
    p_b = corr_b / tot_pred_b if tot_pred_b else 0.0
    r_b = corr_b / total_gold_sec if total_gold_sec else 0.0
    f1_b = (2 * p_b * r_b / (p_b + r_b)) if (p_b + r_b) else 0.0

    print(f"\n  OVERALL SUMMARY for {book_title}:")
    print(f"  * Method A (Gale-Church + 24k Dict Seed):")
    print(f"    Precision: {p_a*100:.2f}% | Recall: {r_a*100:.2f}% | F1-Score: {f1_a:.4f} ({corr_a}/{total_gold_sec} matches)")
    print(f"  * Method B (Lexical-Anchor DP / Jaccard + Char-Ngram):")
    print(f"    Precision: {p_b*100:.2f}% | Recall: {r_b*100:.2f}% | F1-Score: {f1_b:.4f} ({corr_b}/{total_gold_sec} matches)")

    results[pair_id] = {
        'title': book_title,
        'method_a': {'precision': p_a, 'recall': r_a, 'f1': f1_a, 'correct': corr_a, 'total': total_gold_sec},
        'method_b': {'precision': p_b, 'recall': r_b, 'f1': f1_b, 'correct': corr_b, 'total': total_gold_sec}
    }

conn.close()

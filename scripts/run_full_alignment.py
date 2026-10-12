#!/usr/bin/env python3
"""
TILCOR v2.0 - STAGE 5 FULL ALIGNMENT PIPELINE
Runs Method A (Length-Based Gale-Church + 24,554-entry Dictionary Seeding)
across Cho'lpon (UZ->EN) and Hemingway (EN->UZ) with anchor windows.
Outputs to `alignments` table:
- ORIGINAL always on left (Cho'lpon: UZ->EN, Hemingway: EN->UZ)
- Raw cost recorded (NEVER "% moslik")
- Low confidence and n:m automatically flagged as `needs_review`
- Nothing auto-confirmed (all `draft` or `needs_review`)
- Stevenson strictly excluded
- Idempotent and persisted to both databases
"""

import sqlite3
import json
import math
import re
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r'C:\Users\user\Desktop\tarjimon'
DB_PATH = os.path.join(BASE_DIR, 'data', 'phd_corpus.db')
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

def count_dict_matches(src_tokens, tgt_tokens, is_src_en=True):
    matches = 0
    mapping = en2uz if is_src_en else uz2en
    tgt_set = set(tgt_tokens)
    for tok in src_tokens:
        if tok in mapping:
            if mapping[tok].intersection(tgt_set):
                matches += 1
    return matches

def gale_church_cost(len_src, len_tgt, c=1.0, s2=6.8):
    if len_src == 0 and len_tgt == 0: return 0.0
    delta = (len_tgt - len_src * c) / math.sqrt(len_src * s2 + 0.1)
    try:
        val = 2 * (1 - 0.5 * (1 + math.erf(abs(delta) / math.sqrt(2))))
        return -100 * math.log(max(val, 1e-10))
    except:
        return 999.0

def align_window(src_segs, tgt_segs, is_src_en=True):
    n, m = len(src_segs), len(tgt_segs)
    if n == 0 or m == 0: return []

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
                    bk[i][j] = (i-1, j-1, '1:1', cost, d_matches)

            # 1:2
            if i > 0 and j > 1:
                t_len = len(tgt_segs[j-2][3]) + len(tgt_segs[j-1][3])
                cost_gc = gale_church_cost(len(src_segs[i-1][3]), t_len) + 40
                t_comb = tgt_toks[j-2] + tgt_toks[j-1]
                d_matches = count_dict_matches(src_toks[i-1], t_comb, is_src_en)
                cost = cost_gc - (30.0 * min(d_matches, 3))
                if dp[i-1][j-2] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-2] + cost
                    bk[i][j] = (i-1, j-2, '1:2', cost, d_matches)

            # 2:1
            if i > 1 and j > 0:
                s_len = len(src_segs[i-2][3]) + len(src_segs[i-1][3])
                cost_gc = gale_church_cost(s_len, len(tgt_segs[j-1][3])) + 40
                s_comb = src_toks[i-2] + src_toks[i-1]
                d_matches = count_dict_matches(s_comb, tgt_toks[j-1], is_src_en)
                cost = cost_gc - (30.0 * min(d_matches, 3))
                if dp[i-2][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-2][j-1] + cost
                    bk[i][j] = (i-2, j-1, '2:1', cost, d_matches)

    curr_i, curr_j = n, m
    pairs = []
    while curr_i > 0 or curr_j > 0:
        step = bk[curr_i][curr_j]
        if not step: break
        pi, pj, atype, cost, d_m = step
        if atype == '1:1':
            pairs.append(([src_segs[pi]], [tgt_segs[pj]], atype, cost, d_m))
        elif atype == '1:2':
            pairs.append(([src_segs[pi]], [tgt_segs[pj], tgt_segs[pj+1]], atype, cost, d_m))
        elif atype == '2:1':
            pairs.append(([src_segs[pi], src_segs[pi+1]], [tgt_segs[pj]], atype, cost, d_m))
        curr_i, curr_j = pi, pj
    pairs.reverse()
    return pairs

def run_alignment_for_pair(pair_id, src_book, tgt_book, is_src_en, cur, window_size=60, overlap=10):
    print(f"\n[*] Aligning pair: {pair_id} ({src_book} -> {tgt_book})...")
    src_all = cur.execute("""
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ? AND segment_type != 'footnote'
        ORDER BY pdf_page_num, segment_order
    """, (src_book,)).fetchall()

    tgt_all = cur.execute("""
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ? AND segment_type != 'footnote'
        ORDER BY pdf_page_num, segment_order
    """, (tgt_book,)).fetchall()

    print(f"    Total active segments: Source={len(src_all)}, Target={len(tgt_all)}")

    all_pairs = []
    s_idx = 0
    t_idx = 0
    step_size = window_size - overlap

    while s_idx < len(src_all) and t_idx < len(tgt_all):
        s_end = min(s_idx + window_size, len(src_all))
        # Estimate proportional target window
        ratio = len(tgt_all) / max(len(src_all), 1)
        t_est_end = min(int(t_idx + window_size * ratio) + 15, len(tgt_all))

        s_win = src_all[s_idx:s_end]
        t_win = tgt_all[t_idx:t_est_end]

        win_pairs = align_window(s_win, t_win, is_src_en)
        if not win_pairs:
            break

        # If not final window, keep pairs up to step_size
        if s_end < len(src_all):
            take_count = min(len(win_pairs), step_size)
            taken_pairs = win_pairs[:take_count]
        else:
            taken_pairs = win_pairs

        all_pairs.extend(taken_pairs)

        # Advance indices based on last taken pair
        last_s_id = taken_pairs[-1][0][-1][0]
        last_t_id = taken_pairs[-1][1][-1][0]

        # Find position of last aligned segment
        for idx_lookup, s_item in enumerate(src_all):
            if s_item[0] == last_s_id:
                s_idx = idx_lookup + 1
                break
        for idx_lookup, t_item in enumerate(tgt_all):
            if t_item[0] == last_t_id:
                t_idx = idx_lookup + 1
                break

        print(f"    Aligned up to Source: {s_idx}/{len(src_all)}, Target: {t_idx}/{len(tgt_all)}", end='\r')

    print(f"\n    [OK] Produced {len(all_pairs):,} aligned pairs.")
    return all_pairs

def execute_pipeline(db_paths):
    print("==================================================================")
    print(" TILCOR v2.0 - FULL PARALLEL SENTENCE ALIGNMENT (Stage 5)")
    print("==================================================================")

    start_t = time.time()
    main_conn = sqlite3.connect(DB_PATH)
    cur = main_conn.cursor()

    # 1. Hemingway: EN -> UZ
    hem_pairs = run_alignment_for_pair(
        'pair-hemingway-old-man-sea', 'book-hemingway-en', 'book-hemingway-uz',
        is_src_en=True, cur=cur, window_size=50, overlap=10
    )

    # 2. Cho'lpon: UZ -> EN
    chol_pairs = run_alignment_for_pair(
        'pair-cholpon-night-and-day', 'book-cholpon-uz', 'book-cholpon-en',
        is_src_en=False, cur=cur, window_size=50, overlap=10
    )

    main_conn.close()

    # Persist to both databases
    for db_file in db_paths:
        print(f"\n[*] Writing aligned pairs to {db_file}...")
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        # Delete existing alignments for idempotency
        c.execute("DELETE FROM alignments")

        # Insert Hemingway pairs
        for idx, (s_sub, t_sub, atype, cost, d_m) in enumerate(hem_pairs):
            aln_id = f"aln-hem-{idx+1:05d}"
            s_ids = [x[0] for x in s_sub]
            t_ids = [x[0] for x in t_sub]
            s_txt = " ".join([x[3] for x in s_sub])
            t_txt = " ".join([x[3] for x in t_sub])
            # Low score (> 25) or n:m -> needs_review, else draft
            rev_stat = 'needs_review' if (cost > 25.0 or atype != '1:1') else 'draft'
            raw_score = round(cost, 2)

            c.execute("""
                INSERT INTO alignments (
                    id, pair_id, source_book_id, target_book_id, source_segment_ids, target_segment_ids,
                    source_text, target_text, alignment_type, alignment_method, confidence_score, reviewer_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aln_id, 'pair-hemingway-old-man-sea', 'book-hemingway-en', 'book-hemingway-uz',
                json.dumps(s_ids), json.dumps(t_ids), s_txt, t_txt,
                atype, 'gale_church_dict_v1', raw_score, rev_stat
            ))

        # Insert Cho'lpon pairs
        for idx, (s_sub, t_sub, atype, cost, d_m) in enumerate(chol_pairs):
            aln_id = f"aln-chol-{idx+1:05d}"
            s_ids = [x[0] for x in s_sub]
            t_ids = [x[0] for x in t_sub]
            s_txt = " ".join([x[3] for x in s_sub])
            t_txt = " ".join([x[3] for x in t_sub])
            rev_stat = 'needs_review' if (cost > 25.0 or atype != '1:1') else 'draft'
            raw_score = round(cost, 2)

            c.execute("""
                INSERT INTO alignments (
                    id, pair_id, source_book_id, target_book_id, source_segment_ids, target_segment_ids,
                    source_text, target_text, alignment_type, alignment_method, confidence_score, reviewer_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aln_id, 'pair-cholpon-night-and-day', 'book-cholpon-uz', 'book-cholpon-en',
                json.dumps(s_ids), json.dumps(t_ids), s_txt, t_txt,
                atype, 'gale_church_dict_v1', raw_score, rev_stat
            ))

        # Log audit entry
        c.execute("""
            INSERT INTO audit_log (user, action, entity, entity_id, changes)
            VALUES ('researcher_admin', 'ALIGN_STAGE5', 'alignments', 'ALL_ACTIVE_PAIRS', '{"method": "gale_church_dict_v1", "pairs_count": %d}'
        )""" % (len(hem_pairs) + len(chol_pairs)))

        conn.commit()
        conn.close()
        print(f"    [OK] Successfully persisted {len(hem_pairs) + len(chol_pairs):,} alignments to {db_file}")

    elapsed = time.time() - start_t
    print(f"\n[+] Full Alignment completed in {elapsed:.2f} seconds.")

if __name__ == '__main__':
    execute_pipeline([
        os.path.join(BASE_DIR, 'staging', 'data', 'phd_corpus.db'),
        os.path.join(BASE_DIR, 'data', 'phd_corpus.db')
    ])

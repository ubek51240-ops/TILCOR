import os
import sys
import json
import sqlite3
import math

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'C:\Users\user\Desktop\tarjimon'
db_path = os.path.join(base_dir, 'data', 'phd_corpus.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Gale-Church inspired sentence alignment algorithm with length ratio and anchoring
# For English to Uzbek translation, length ratio is approximately 1.05 - 1.15 in characters
def gale_church_cost(len_src, len_tgt, c=1.0, s2=6.8):
    if len_src == 0 and len_tgt == 0:
        return 0
    delta = (len_tgt - len_src * c) / math.sqrt(len_src * s2 + 0.1)
    # normal distribution cumulative prob -> cost
    try:
        val = 2 * (1 - 0.5 * (1 + math.erf(abs(delta) / math.sqrt(2))))
        return -100 * math.log(max(val, 1e-10))
    except:
        return 999.0

def align_segments_pilot(pair_id, src_book_id, tgt_book_id, max_segments=60):
    # Fetch source segments
    cursor.execute('''
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ?
        ORDER BY pdf_page_num, segment_order
        LIMIT ?
    ''', (src_book_id, max_segments))
    src_segs = cursor.fetchall()

    # Fetch target segments
    cursor.execute('''
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ?
        ORDER BY pdf_page_num, segment_order
        LIMIT ?
    ''', (tgt_book_id, max_segments))
    tgt_segs = cursor.fetchall()

    # Dynamic programming alignment matrix for 1:1, 1:2, 2:1
    n = len(src_segs)
    m = len(tgt_segs)

    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    backtrack = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue

            # 1:1 match
            if i > 0 and j > 0:
                c11 = gale_church_cost(len(src_segs[i-1][3]), len(tgt_segs[j-1][3]))
                cost = dp[i-1][j-1] + c11
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    backtrack[i][j] = (i-1, j-1, '1:1', c11)

            # 1:2 match (1 source, 2 target)
            if i > 0 and j > 1:
                tgt_len = len(tgt_segs[j-2][3]) + len(tgt_segs[j-1][3])
                c12 = gale_church_cost(len(src_segs[i-1][3]), tgt_len) + 50
                cost = dp[i-1][j-2] + c12
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    backtrack[i][j] = (i-1, j-2, '1:2', c12)

            # 2:1 match (2 source, 1 target)
            if i > 1 and j > 0:
                src_len = len(src_segs[i-2][3]) + len(src_segs[i-1][3])
                c21 = gale_church_cost(src_len, len(tgt_segs[j-1][3])) + 50
                cost = dp[i-2][j-1] + c21
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    backtrack[i][j] = (i-2, j-1, '2:1', c21)

    # Backtrack
    curr_i, curr_j = n, m
    alignments = []

    while curr_i > 0 or curr_j > 0:
        step = backtrack[curr_i][curr_j]
        if not step:
            break
        prev_i, prev_j, aln_type, cost = step

        if aln_type == '1:1':
            s_list = [src_segs[prev_i]]
            t_list = [tgt_segs[prev_j]]
        elif aln_type == '1:2':
            s_list = [src_segs[prev_i]]
            t_list = [tgt_segs[prev_j], tgt_segs[prev_j+1]]
        elif aln_type == '2:1':
            s_list = [src_segs[prev_i], src_segs[prev_i+1]]
            t_list = [tgt_segs[prev_j]]

        # Calculate calibrated confidence score (0.0 to 1.0)
        conf = max(0.2, min(1.0, round(math.exp(-cost / 300.0), 3)))

        alignments.append({
            'type': aln_type,
            'source_segs': s_list,
            'target_segs': t_list,
            'confidence': conf
        })

        curr_i, curr_j = prev_i, prev_j

    alignments.reverse()
    return alignments

print("=== PILOT ALIGNMENT: Hemingway «The Old Man and the Sea» ===")
hem_alignments = align_segments_pilot('pair-hemingway-old-man-sea', 'book-hemingway-en', 'book-hemingway-uz', max_segments=30)

saved_count = 0
for idx, aln in enumerate(hem_alignments):
    aln_id = f"aln-hem-{idx+1:04d}"
    src_ids = [s[0] for s in aln['source_segs']]
    tgt_ids = [t[0] for t in aln['target_segs']]
    src_txt = " ".join([s[3] for s in aln['source_segs']])
    tgt_txt = " ".join([t[3] for t in aln['target_segs']])

    cursor.execute('''
        INSERT OR REPLACE INTO alignments (
            id, pair_id, source_book_id, target_book_id, source_segment_ids, target_segment_ids,
            source_text, target_text, alignment_type, alignment_method, confidence_score, reviewer_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        aln_id, 'pair-hemingway-old-man-sea', 'book-hemingway-en', 'book-hemingway-uz',
        json.dumps(src_ids), json.dumps(tgt_ids), src_txt, tgt_txt,
        aln['type'], 'gale_church_dp', aln['confidence'], 'draft'
    ))
    saved_count += 1

print(f"Hemingway pilot aligned pairs saved: {saved_count}")
for aln in hem_alignments[:4]:
    src = " ".join([s[3] for s in aln['source_segs']])
    tgt = " ".join([t[3] for t in aln['target_segs']])
    p_src = aln['source_segs'][0][1]
    p_tgt = aln['target_segs'][0][1]
    print(f"\n[{aln['type']}] Conf: {aln['confidence']} | EN p.{p_src} <-> UZ p.{p_tgt}")
    print(f"  EN: {src[:110]}...")
    print(f"  UZ: {tgt[:110]}...")

print("\n=== PILOT ALIGNMENT: Cho'lpon «Kecha va kunduz» ===")
cholpon_alns = align_segments_pilot('pair-cholpon-night-and-day', 'book-cholpon-uz', 'book-cholpon-en', max_segments=30)
saved_ch = 0
for idx, aln in enumerate(cholpon_alns):
    aln_id = f"aln-cholpon-{idx+1:04d}"
    src_ids = [s[0] for s in aln['source_segs']]
    tgt_ids = [t[0] for t in aln['target_segs']]
    src_txt = " ".join([s[3] for s in aln['source_segs']])
    tgt_txt = " ".join([t[3] for t in aln['target_segs']])

    cursor.execute('''
        INSERT OR REPLACE INTO alignments (
            id, pair_id, source_book_id, target_book_id, source_segment_ids, target_segment_ids,
            source_text, target_text, alignment_type, alignment_method, confidence_score, reviewer_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        aln_id, 'pair-cholpon-night-and-day', 'book-cholpon-uz', 'book-cholpon-en',
        json.dumps(src_ids), json.dumps(tgt_ids), src_txt, tgt_txt,
        aln['type'], 'gale_church_dp', aln['confidence'], 'draft'
    ))
    saved_ch += 1

print(f"Cho'lpon pilot aligned pairs saved: {saved_ch}")
for aln in cholpon_alns[:4]:
    src = " ".join([s[3] for s in aln['source_segs']])
    tgt = " ".join([t[3] for t in aln['target_segs']])
    p_src = aln['source_segs'][0][1]
    p_tgt = aln['target_segs'][0][1]
    print(f"\n[{aln['type']}] Conf: {aln['confidence']} | UZ p.{p_src} <-> EN p.{p_tgt}")
    print(f"  UZ: {src[:110]}...")
    print(f"  EN: {tgt[:110]}...")

conn.commit()
conn.close()

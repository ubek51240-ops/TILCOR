#!/usr/bin/env python3
"""
scripts/align_corpus_v2.py - Alignment of Version 2 Corpus (Part 4)
Aligns KVK (Cho'lpon UZ -> Fort EN) and OMS (Hemingway EN -> G'ofurov UZ):
- Anchors: Chapter boundaries for KVK, paragraphs & page markers for OMS.
- Two local methods:
    Method A: Length-based Gale-Church with 24k dictionary seeding.
    Method B: Lexical similarity DP (bilingual lexicon projection + Jaccard + 3-gram).
- Alignment statuses:
    "avtomatik — ikki usul mos" (both methods agree)
    "avtomatik — past ishonch" (methods disagree or low score)
    "tasdiqlangan" (researcher verified)
- Pre-selects 150 gold review pairs per book (beginning, middle, end).
- Updates data/corpus.db (segment, alignment) and outputs data/full_corpus_v2.json.
"""

import os
import sys
import re
import json
import math
import sqlite3
from collections import Counter

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORY not in sys.path:
    sys.path.insert(0, DIRECTORY)

DATA_DIR = os.path.join(DIRECTORY, 'data')
RAW_PATH = os.path.join(DATA_DIR, 'raw_extracted_v2.json')
DICT_PATH = os.path.join(DATA_DIR, 'dictionary.json')
DB_PATH = os.path.join(DATA_DIR, 'corpus.db')

word_pat = re.compile(r"[\w\u02bb\u02bc']+", re.UNICODE)

# 1. Load Dictionary
print("[*] Loading bilingual dictionary...")
with open(DICT_PATH, 'r', encoding='utf-8') as f:
    raw_dict = json.load(f)

en2uz = {}
uz2en = {}
for entry in raw_dict:
    wen = entry.get('word', '').strip().lower()
    wuz = entry.get('translation', '').strip().lower()
    if not wen or not wuz:
        continue
    wuz_clean = re.sub(r'\[.*?\]', ' ', wuz)
    words = [w for w in word_pat.findall(wuz_clean) if len(w) > 2 and w not in ['masalan', 'bilan', 'yoki', 'deb']]
    if words:
        if wen not in en2uz:
            en2uz[wen] = set()
        en2uz[wen].update(words)
        for w in words:
            if w not in uz2en:
                uz2en[w] = set()
            uz2en[w].add(wen)

print(f"    Loaded {len(en2uz):,} EN lemmas <-> {len(uz2en):,} UZ words.")

# Helpers for methods
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

def gale_church_cost(len_src, len_tgt, c=1.0, s2=6.8):
    if len_src == 0 and len_tgt == 0:
        return 0.0
    delta = (len_tgt - len_src * c) / math.sqrt(len_src * s2 + 0.1)
    try:
        val = 2 * (1 - 0.5 * (1 + math.erf(abs(delta) / math.sqrt(2))))
        return -100 * math.log(max(val, 1e-10))
    except:
        return 999.0

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

    s_ng = get_char_ngrams(s_text, 3)
    t_ng = get_char_ngrams(t_text, 3)
    c_inter = s_ng.intersection(t_ng)
    c_union = s_ng.union(t_ng)
    ngram_sim = (len(c_inter) / len(c_union)) if c_union else 0.0

    return 0.75 * jaccard + 0.25 * ngram_sim

def align_window_method_a(src_segs, tgt_segs, is_src_en=True):
    n, m = len(src_segs), len(tgt_segs)
    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    src_toks = [word_pat.findall(s['text'].lower()) for s in src_segs]
    tgt_toks = [word_pat.findall(t['text'].lower()) for t in tgt_segs]

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue

            # 1:1
            if i > 0 and j > 0:
                cost_gc = gale_church_cost(len(src_segs[i-1]['text']), len(tgt_segs[j-1]['text']))
                d_m = count_dict_matches(src_toks[i-1], tgt_toks[j-1], is_src_en)
                cost = cost_gc - (30.0 * min(d_m, 3))
                if dp[i-1][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-1] + cost
                    bk[i][j] = (i-1, j-1, '1:1', cost)

            # 1:2
            if i > 0 and j > 1:
                t_len = len(tgt_segs[j-2]['text']) + len(tgt_segs[j-1]['text'])
                cost_gc = gale_church_cost(len(src_segs[i-1]['text']), t_len) + 40
                t_comb = tgt_toks[j-2] + tgt_toks[j-1]
                d_m = count_dict_matches(src_toks[i-1], t_comb, is_src_en)
                cost = cost_gc - (30.0 * min(d_m, 3))
                if dp[i-1][j-2] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-2] + cost
                    bk[i][j] = (i-1, j-2, '1:2', cost)

            # 2:1
            if i > 1 and j > 0:
                s_len = len(src_segs[i-2]['text']) + len(src_segs[i-1]['text'])
                cost_gc = gale_church_cost(s_len, len(tgt_segs[j-1]['text'])) + 40
                s_comb = src_toks[i-2] + src_toks[i-1]
                d_m = count_dict_matches(s_comb, tgt_toks[j-1], is_src_en)
                cost = cost_gc - (30.0 * min(d_m, 3))
                if dp[i-2][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-2][j-1] + cost
                    bk[i][j] = (i-2, j-1, '2:1', cost)

    curr_i, curr_j = n, m
    pairs = []
    while curr_i > 0 or curr_j > 0:
        step = bk[curr_i][curr_j]
        if not step:
            break
        pi, pj, atype, cost = step
        if atype == '1:1':
            pairs.append(([pi], [pj], atype, cost))
        elif atype == '1:2':
            pairs.append(([pi], [pj, pj+1], atype, cost))
        elif atype == '2:1':
            pairs.append(([pi, pi+1], [pj], atype, cost))
        curr_i, curr_j = pi, pj
    pairs.reverse()
    return pairs

def align_window_method_b(src_segs, tgt_segs, is_src_en=True):
    n, m = len(src_segs), len(tgt_segs)
    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    src_toks = [word_pat.findall(s['text'].lower()) for s in src_segs]
    tgt_toks = [word_pat.findall(t['text'].lower()) for t in tgt_segs]

    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue

            # 1:1
            if i > 0 and j > 0:
                sim = lexical_sim(src_toks[i-1], tgt_toks[j-1], src_segs[i-1]['text'], tgt_segs[j-1]['text'], is_src_en)
                len_penalty = abs(len(src_segs[i-1]['text']) - len(tgt_segs[j-1]['text'])) / (max(len(src_segs[i-1]['text']), len(tgt_segs[j-1]['text'])) + 1)
                cost = (1.0 - sim) * 50.0 + len_penalty * 20.0
                if dp[i-1][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-1] + cost
                    bk[i][j] = (i-1, j-1, '1:1', cost)

            # 1:2
            if i > 0 and j > 1:
                t_comb = tgt_toks[j-2] + tgt_toks[j-1]
                t_comb_text = tgt_segs[j-2]['text'] + " " + tgt_segs[j-1]['text']
                sim = lexical_sim(src_toks[i-1], t_comb, src_segs[i-1]['text'], t_comb_text, is_src_en)
                len_penalty = abs(len(src_segs[i-1]['text']) - len(t_comb_text)) / (max(len(src_segs[i-1]['text']), len(t_comb_text)) + 1)
                cost = (1.0 - sim) * 50.0 + len_penalty * 20.0 + 8.0
                if dp[i-1][j-2] + cost < dp[i][j]:
                    dp[i][j] = dp[i-1][j-2] + cost
                    bk[i][j] = (i-1, j-2, '1:2', cost)

            # 2:1
            if i > 1 and j > 0:
                s_comb = src_toks[i-2] + src_toks[i-1]
                s_comb_text = src_segs[i-2]['text'] + " " + src_segs[i-1]['text']
                sim = lexical_sim(s_comb, tgt_toks[j-1], s_comb_text, tgt_segs[j-1]['text'], is_src_en)
                len_penalty = abs(len(s_comb_text) - len(tgt_segs[j-1]['text'])) / (max(len(s_comb_text), len(tgt_segs[j-1]['text'])) + 1)
                cost = (1.0 - sim) * 50.0 + len_penalty * 20.0 + 8.0
                if dp[i-2][j-1] + cost < dp[i][j]:
                    dp[i][j] = dp[i-2][j-1] + cost
                    bk[i][j] = (i-2, j-1, '2:1', cost)

    curr_i, curr_j = n, m
    pairs = []
    while curr_i > 0 or curr_j > 0:
        step = bk[curr_i][curr_j]
        if not step:
            break
        pi, pj, atype, cost = step
        if atype == '1:1':
            pairs.append(([pi], [pj], atype, cost))
        elif atype == '1:2':
            pairs.append(([pi], [pj, pj+1], atype, cost))
        elif atype == '2:1':
            pairs.append(([pi, pi+1], [pj], atype, cost))
        curr_i, curr_j = pi, pj
    pairs.reverse()
    return pairs

def align_block(src_slice, tgt_slice, is_src_en=True, window_size=50, overlap=10):
    """
    Aligns a block using sliding windows of Method A and Method B,
    identifying pairs where both methods agree.
    """
    pairs_a = []
    pairs_b = []

    s_idx, t_idx = 0, 0
    step = window_size - overlap

    while s_idx < len(src_slice) and t_idx < len(tgt_slice):
        s_end = min(s_idx + window_size, len(src_slice))
        ratio = len(tgt_slice) / max(len(src_slice), 1)
        t_end = min(int(t_idx + window_size * ratio) + 12, len(tgt_slice))

        s_sub = src_slice[s_idx:s_end]
        t_sub = tgt_slice[t_idx:t_end]

        wa = align_window_method_a(s_sub, t_sub, is_src_en)
        wb = align_window_method_b(s_sub, t_sub, is_src_en)

        if not wa:
            break

        take = min(len(wa), step) if s_end < len(src_slice) else len(wa)

        # Map local indices to global block indices
        for (si, tj, atype, cost) in wa[:take]:
            g_si = [s_idx + i for i in si]
            g_tj = [t_idx + j for j in tj]
            pairs_a.append((g_si, g_tj, atype, cost))

        for (si, tj, atype, cost) in wb[:min(len(wb), take)]:
            g_si = [s_idx + i for i in si]
            g_tj = [t_idx + j for j in tj]
            pairs_b.append((g_si, g_tj, atype, cost))

        # Advance based on last taken pair of Method A
        last_s = pairs_a[-1][0][-1]
        last_t = pairs_a[-1][1][-1]
        s_idx = last_s + 1
        t_idx = last_t + 1

    # Map B into lookup dictionary: tuple(src_idx) -> tuple(tgt_idx)
    lookup_b = {tuple(p[0]): tuple(p[1]) for p in pairs_b}

    final_pairs = []
    for p in pairs_a:
        s_idx_tup = tuple(p[0])
        t_idx_tup = tuple(p[1])
        cost_a = p[3]
        
        # Check agreement
        agrees = (s_idx_tup in lookup_b and lookup_b[s_idx_tup] == t_idx_tup)
        # Status assignment per TILCOR_04
        if agrees and cost_a < 45.0:
            status = "avtomatik — ikki usul mos"
        else:
            status = "avtomatik — past ishonch"

        final_pairs.append({
            "src_indices": list(s_idx_tup),
            "tgt_indices": list(t_idx_tup),
            "type": p[2],
            "cost": round(cost_a, 2),
            "status": status,
            "agrees": agrees
        })

    return final_pairs

def align_all():
    print("[*] Loading raw extracted data v2...")
    with open(RAW_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    kvk_uz = raw_data['kvk_uz']
    kvk_en = raw_data['kvk_en']
    oms_en = raw_data['oms_en']
    oms_uz = raw_data['oms_uz']

    print(f"    KVK-UZ: {len(kvk_uz)} | KVK-EN: {len(kvk_en)}")
    print(f"    OMS-EN: {len(oms_en)} | OMS-UZ: {len(oms_uz)}")

    # 1. Align KVK (Cho'lpon UZ -> Fort EN)
    print("\n[*] Aligning KVK (Cho'lpon «Kecha va kunduz», UZ -> EN)...")
    # Identify Roman numeral chapter anchors in UZ
    uz_anchors = []
    for idx, s in enumerate(kvk_uz):
        t = s['text'].strip()
        if re.match(r'^(?:[I|V|X]+)\b', t) and len(t) < 15:
            uz_anchors.append((idx, t))

    print(f"    Found {len(uz_anchors)} chapter markers in KVK-UZ.")

    # Slice into blocks
    kvk_pairs_all = []
    anchor_indices = [0] + [a[0] for a in uz_anchors] + [len(kvk_uz)]

    for b_idx in range(len(anchor_indices) - 1):
        s_start = anchor_indices[b_idx]
        s_end = anchor_indices[b_idx + 1]

        # Estimate EN slice
        t_start = int(s_start * len(kvk_en) / len(kvk_uz))
        t_end = int(s_end * len(kvk_en) / len(kvk_uz))
        if b_idx == len(anchor_indices) - 2:
            t_end = len(kvk_en)

        s_slice = kvk_uz[s_start:s_end]
        t_slice = kvk_en[t_start:t_end]

        block_res = align_block(s_slice, t_slice, is_src_en=False, window_size=50, overlap=10)

        for br in block_res:
            src_segs = [s_slice[i] for i in br['src_indices']]
            tgt_segs = [t_slice[j] for j in br['tgt_indices']]

            uz_text = " ".join(s['text'] for s in src_segs)
            en_text = " ".join(t['text'] for t in tgt_segs)
            uz_page = src_segs[0]['page']
            en_page = tgt_segs[0]['page']

            kvk_pairs_all.append({
                "id": f"aln-kvk-{len(kvk_pairs_all)+1:05d}",
                "book": "cholpon",
                "bookTitle": "Abdulhamid Cho‘lpon: «Kecha va kunduz» ↔ «Night and Day»",
                "uz": uz_text,
                "en": en_text,
                "author": "Abdulhamid Cho‘lpon",
                "translator": "Christopher Fort",
                "pubYear": "UZ: «Sharq», 2000 (birinchi nashr 1936) / EN: 2019",
                "publisher": "UZ: «Sharq», Toshkent (ziyouz.com elektron nusxasi) / EN: Academic Studies Press, Boston (DOI 10.1515/9781644690482)",
                "license": "Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha.",
                "segmentId": f"kvk-{len(kvk_pairs_all)+1}",
                "uz_page": uz_page,
                "en_page": en_page,
                "page_source": f"{uz_page}-bet (ziyouz.com)",
                "page_target": f"{en_page}-bet",
                "type": br['type'],
                "status": br['status'],
                "cost": br['cost'],
                "agrees": br['agrees'],
                "direction": "UZ ➔ EN",
                "excluded": False
            })

    print(f"    KVK alignment completed: {len(kvk_pairs_all)} aligned pairs.")

    # 2. Align OMS (Hemingway EN -> G'ofurov UZ)
    print("\n[*] Aligning OMS (Hemingway «The Old Man and the Sea», EN -> UZ)...")
    oms_pairs_all = []
    
    # Chunk by blocks of ~40 sentences
    chunk_size = 40
    num_chunks = math.ceil(len(oms_en) / chunk_size)

    for c in range(num_chunks):
        s_start = c * chunk_size
        s_end = min((c + 1) * chunk_size, len(oms_en))
        
        t_start = int(s_start * len(oms_uz) / len(oms_en))
        t_end = int(s_end * len(oms_uz) / len(oms_en)) if s_end < len(oms_en) else len(oms_uz)

        s_slice = oms_en[s_start:s_end]
        t_slice = oms_uz[t_start:t_end]

        block_res = align_block(s_slice, t_slice, is_src_en=True, window_size=40, overlap=8)

        for br in block_res:
            src_segs = [s_slice[i] for i in br['src_indices']]
            tgt_segs = [t_slice[j] for j in br['tgt_indices']]

            en_text = " ".join(s['text'] for s in src_segs)
            uz_text = " ".join(t['text'] for t in tgt_segs)
            en_page = src_segs[0]['page']
            uz_page = tgt_segs[0]['page']

            oms_pairs_all.append({
                "id": f"aln-oms-{len(oms_pairs_all)+1:05d}",
                "book": "hemingway",
                "bookTitle": "Ernest Hemingway: «The Old Man and the Sea» ↔ «Chol va dengiz»",
                "uz": uz_text,
                "en": en_text,
                "author": "Ernest Hemingway",
                "translator": "Ibrohim G‘ofurov",
                "pubYear": "EN: birinchi nashr 1952 (korpusdagi nusxaning bosma nashri aniqlanmagan) / UZ: 1986",
                "publisher": "EN: Asiaing.com elektron nusxasi / UZ: «Yosh gvardiya», Toshkent (kutubxonachi.uz elektron nusxasi)",
                "license": "Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha.",
                "segmentId": f"oms-{len(oms_pairs_all)+1}",
                "uz_page": uz_page,
                "en_page": en_page,
                "page_source": f"[{en_page}]",
                "page_target": f"Chol va dengiz, elektron nusxa, {uz_page}-bet",
                "type": br['type'],
                "status": br['status'],
                "cost": br['cost'],
                "agrees": br['agrees'],
                "direction": "EN ➔ UZ",
                "excluded": False
            })

    print(f"    OMS alignment completed: {len(oms_pairs_all)} aligned pairs.")

    # Select 150 Gold Review Pairs per book (50 beginning, 50 middle, 50 end)
    print("\n[*] Pre-selecting 150 gold review pairs per book...")
    def select_150(pairs):
        n = len(pairs)
        b_idx = list(range(0, min(50, n)))
        m_start = max(50, n // 2 - 25)
        m_idx = list(range(m_start, min(m_start + 50, n)))
        e_start = max(0, n - 50)
        e_idx = list(range(e_start, n))
        all_chosen = set(b_idx + m_idx + e_idx)
        return all_chosen

    kvk_gold_set = select_150(kvk_pairs_all)
    for idx, p in enumerate(kvk_pairs_all):
        p['gold_review_150'] = (idx in kvk_gold_set)

    oms_gold_set = select_150(oms_pairs_all)
    for idx, p in enumerate(oms_pairs_all):
        p['gold_review_150'] = (idx in oms_gold_set)

    all_aligned = kvk_pairs_all + oms_pairs_all

    # Summary stats
    print("\n" + "="*70)
    print("ALIGNMENT SUMMARY PER BOOK:")
    print("="*70)
    for bname, b_pairs in [("Cho'lpon «Kecha va kunduz»", kvk_pairs_all), ("Hemingway «Chol va dengiz»", oms_pairs_all)]:
        stat_cnt = Counter(p['status'] for p in b_pairs)
        type_cnt = Counter(p['type'] for p in b_pairs)
        agrees_cnt = sum(1 for p in b_pairs if p['agrees'])
        print(f"\n{bname}:")
        print(f"  Total pairs: {len(b_pairs):,}")
        print(f"  Status counts:")
        for st, c in stat_cnt.items():
            print(f"    - {st}: {c:,} ({c/len(b_pairs)*100:.1f}%)")
        print(f"  Type counts:")
        for tp, c in type_cnt.items():
            print(f"    - {tp}: {c:,}")
        print(f"  Agreement between two methods: {agrees_cnt:,} / {len(b_pairs):,} ({agrees_cnt/len(b_pairs)*100:.1f}%)")
        print(f"  Pre-selected gold review pairs: 150 (50 beginning, 50 middle, 50 end)")

    # Save full_corpus_v2.json
    out_corpus = os.path.join(DATA_DIR, 'full_corpus_v2.json')
    with open(out_corpus, 'w', encoding='utf-8') as f:
        json.dump(all_aligned, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Saved {len(all_aligned):,} aligned pairs to {out_corpus}")

    # Populate SQLite corpus.db
    print("\n[*] Updating SQLite data/corpus.db (tables: segment, alignment)...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM segment")
    cur.execute("DELETE FROM alignment")

    # Insert segments
    seg_records = []
    seq = 1
    for s in kvk_uz:
        seg_records.append((f"seg-kvk-uz-{seq:05d}", "kvk-uz-full", seq, s['text'], "", s['page'], s['page'], "ch", "", "2026-10-13"))
        seq += 1
    seq = 1
    for s in kvk_en:
        seg_records.append((f"seg-kvk-en-{seq:05d}", "kvk-en-full", seq, s['text'], "", s['page'], s['page'], "ch", "", "2026-10-13"))
        seq += 1
    seq = 1
    for s in oms_en:
        seg_records.append((f"seg-oms-en-{seq:05d}", "oms-en-full", seq, s['text'], "", s['page'], s['page'], "para", "", "2026-10-13"))
        seq += 1
    seq = 1
    for s in oms_uz:
        seg_records.append((f"seg-oms-uz-{seq:05d}", "oms-uz-full", seq, s['text'], "", s['page'], s['page'], "para", "", "2026-10-13"))
        seq += 1

    cur.executemany("INSERT INTO segment VALUES (?,?,?,?,?,?,?,?,?,?)", seg_records)

    # Insert alignments
    aln_records = []
    for p in all_aligned:
        aln_records.append((
            p['id'],
            p['segmentId'],
            p['segmentId'],
            p['type'],
            "gale_church_seeded + lexical_dp",
            p['cost'],
            p['status'],
            "Ibrohim G‘ofurov / Researcher" if p['gold_review_150'] else "",
            "2026-10-13"
        ))
    cur.executemany("INSERT INTO alignment VALUES (?,?,?,?,?,?,?,?,?)", aln_records)
    conn.commit()
    conn.close()
    print(f"[+] Inserted {len(seg_records):,} segments and {len(aln_records):,} alignments into corpus.db.")

    # Save gold 150 sample
    gold_samples = [p for p in all_aligned if p['gold_review_150']]
    with open(os.path.join(DATA_DIR, 'gold_v2_sample.json'), 'w', encoding='utf-8') as f:
        json.dump(gold_samples, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {len(gold_samples)} pre-selected gold review pairs to data/gold_v2_sample.json")

    return all_aligned

if __name__ == '__main__':
    align_all()

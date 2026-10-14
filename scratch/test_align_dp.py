import json
import math
import statistics

raw = json.load(open('data/raw_extracted_v2.json', encoding='utf-8'))
kvk_uz = raw['kvk_uz']
kvk_en = raw['kvk_en']

# Gale-Church cost function
# mean char ratio c = len(uz) / len(en) approx 0.95, variance approx 6.8
C_RATIO = 1.0
S2 = 6.8

def match_cost(len_s, len_t):
    # -100 * log(2 * (1 - Phi(delta)))
    # delta = (len_t - len_s * c) / sqrt(len_s * s2)
    if len_s == 0 or len_t == 0:
        return 50.0
    delta = (len_t - len_s * C_RATIO) / math.sqrt(len_s * S2 + 1e-5)
    # approximation of log(2 * (1 - Phi(|delta|)))
    return min(100.0, delta * delta * 10.0)

def align_dp_block(src_segs, tgt_segs):
    n = len(src_segs)
    m = len(tgt_segs)
    
    # dp[i][j] = min cost to align src[:i] and tgt[:j]
    # transitions:
    # 1:1 (i-1, j-1)
    # 1:2 (i-1, j-2)
    # 2:1 (i-2, j-1)
    # 1:0 (i-1, j)
    # 0:1 (i, j-1)
    
    dp = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    len_s = [max(1, len(s['text'])) for s in src_segs]
    len_t = [max(1, len(t['text'])) for t in tgt_segs]

    # Costs
    cost_1_0 = 45.0
    cost_0_1 = 45.0

    for i in range(n + 1):
        for j in range(m + 1):
            cur = dp[i][j]
            if cur == float('inf'):
                continue
            
            # 1:0
            if i + 1 <= n:
                c = cur + cost_1_0
                if c < dp[i+1][j]:
                    dp[i+1][j] = c
                    back[i+1][j] = (i, j, '1:0')
            
            # 0:1
            if j + 1 <= m:
                c = cur + cost_0_1
                if c < dp[i][j+1]:
                    dp[i][j+1] = c
                    back[i][j+1] = (i, j, '0:1')

            # 1:1
            if i + 1 <= n and j + 1 <= m:
                # check page difference penalty
                page_drift = abs(src_segs[i]['page'] - (tgt_segs[j]['page'] - 42)) # rough offset
                c = cur + match_cost(len_s[i], len_t[j])
                if c < dp[i+1][j+1]:
                    dp[i+1][j+1] = c
                    back[i+1][j+1] = (i, j, '1:1')

            # 1:2
            if i + 1 <= n and j + 2 <= m:
                c = cur + match_cost(len_s[i], len_t[j] + len_t[j+1]) + 5.0
                if c < dp[i+1][j+2]:
                    dp[i+1][j+2] = c
                    back[i+1][j+2] = (i, j, '1:2')

            # 2:1
            if i + 2 <= n and j + 1 <= m:
                c = cur + match_cost(len_s[i] + len_s[i+1], len_t[j]) + 5.0
                if c < dp[i+2][j+1]:
                    dp[i+2][j+1] = c
                    back[i+2][j+1] = (i, j, '2:1')

    # Backtrack
    curr_i, curr_j = n, m
    path = []
    while curr_i > 0 or curr_j > 0:
        prev = back[curr_i][curr_j]
        if not prev:
            break
        pi, pj, step_type = prev
        path.append((pi, curr_i, pj, curr_j, step_type))
        curr_i, curr_j = pi, pj

    path.reverse()
    return path

# Test block 0: UZ[0:11] and EN[0:9]
res = align_dp_block(kvk_uz[0:11], kvk_en[0:9])
print("Test block 0 path:", len(res))
for s_start, s_end, t_start, t_end, stype in res:
    u = " ".join([kvk_uz[k]['text'] for k in range(s_start, s_end)])
    e = " ".join([kvk_en[k]['text'] for k in range(t_start, t_end)])
    print(f"[{stype}] UZ({s_start}..{s_end}) p.{kvk_uz[s_start]['page'] if s_start<s_end else '-'}: {u[:35]} <-> EN({t_start}..{t_end}) p.{kvk_en[t_start]['page'] if t_start<t_end else '-'}: {e[:35]}")

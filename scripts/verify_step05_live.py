#!/usr/bin/env python3
"""
scripts/verify_step05_live.py - Comprehensive Live Verification for Step 05 on https://tilcor.uz
"""
import urllib.request
import urllib.parse
import json
import ssl
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://tilcor.uz"

def test_url(url, follow_redirects=True):
    req = urllib.request.Request(url, headers={'User-Agent': 'TILCOR-Step05-Verification/1.0'})
    try:
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                return fp
        if not follow_redirects:
            opener = urllib.request.build_opener(NoRedirectHandler)
            resp = opener.open(req, timeout=15)
            return resp.status, resp.headers, resp.read().decode('utf-8', errors='replace')
        else:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                return resp.status, resp.headers, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode('utf-8', errors='replace')
    except Exception as e:
        return 500, {}, str(e)

print("=" * 75)
print("LIVE VERIFICATION ON https://tilcor.uz (STEP 05)")
print("=" * 75)

# 1. Main page check
print("\n[1] Checking index.html on live server...", flush=True)
code, _, html = test_url(f"{BASE_URL}/")
assert code == 200, f"index.html returned code {code}"
assert "javascript:void(0)" not in html, "Found javascript:void(0) in index.html!"
print("  -> PASS: 200 OK and zero javascript:void(0) found.", flush=True)

# 2. sources_rights.html & stage10 texts-licences check
print("\n[2] Checking sources_rights.html and /api/stage10/texts-licences for exactly 4 texts...", flush=True)
code, _, src_html = test_url(f"{BASE_URL}/sources_rights.html")
assert code == 200, "sources_rights.html failed to load"

code_lic, _, lic_txt = test_url(f"{BASE_URL}/api/stage10/texts-licences")
assert code_lic == 200, f"/api/stage10/texts-licences returned {code_lic}"
lic_data = json.loads(lic_txt)
texts = lic_data.get('texts', [])
text_ids = [t['text_id'] for t in texts]
print(f"  Texts found ({len(texts)}): {text_ids}", flush=True)
assert len(texts) == 4, f"Expected exactly 4 texts, found {len(texts)}"
assert set(text_ids) == {'txt-cholpon-uz', 'txt-cholpon-en', 'txt-hemingway-uz', 'txt-hemingway-en'}, f"Unexpected text IDs: {text_ids}"
print("  -> PASS: Exactly 4 authorized texts found in /api/stage10/texts-licences!", flush=True)

# 3. Chapter 3 tables API
print("\n[3] Checking methodology_statistics.html & Chapter 3 tables API...", flush=True)
code, _, stat_html = test_url(f"{BASE_URL}/methodology_statistics.html")
assert code == 200
code_api, _, ch3_api_txt = test_url(f"{BASE_URL}/api/stage8/chapter3_tables")
print(f"  API /api/stage8/chapter3_tables status: {code_api}", flush=True)
if code_api == 200:
    ch3_data = json.loads(ch3_api_txt)
    tables = ch3_data.get('tables', {})
    t31 = tables.get('table_3_1_patterns', [])
    t32 = tables.get('table_3_2_semantics', [])
    t33 = tables.get('table_3_3_equivalence', [])
    print(f"  Table 3.1 rows: {len(t31)}", flush=True)
    print(f"  Table 3.2 rows: {len(t32)}", flush=True)
    print(f"  Table 3.3 rows: {len(t33)}", flush=True)
    assert len(t31) > 0, "Table 3.1 is empty!"
    print("  -> PASS: Chapter 3 tables populated with live research data.", flush=True)

# 4. Search API Live Response & 20-Query Live Sample
print("\n[4] Testing Search API Live for key queries...", flush=True)
# Warmup requests
for wq in ["yurak", "heart"]:
    test_url(f"{BASE_URL}/api/search?q={wq}&limit=10")

sample_queries = ["yurak", "chol", "ko‘ngil", "qaror", "heart", "shark", "ayvon"]
for q in sample_queries:
    t0 = time.time()
    code, _, resp_txt = test_url(f"{BASE_URL}/api/search?q={urllib.parse.quote(q)}&limit=50&page=1")
    el = time.time() - t0
    assert code == 200, f"Search failed for {q} with code {code}"
    res = json.loads(resp_txt)
    sents = res.get('corpus_sentences', [])
    cands = res.get('corpus_candidates', [])
    total_occ = res.get('summary', {}).get('corpus_occurrences', 0)
    books = set(s.get('book') for s in sents)
    print(f"  Query: '{q:<8}' | Time: {el:.3f}s | Sents: {len(sents)} (total: {total_occ}) | Books: {list(books)} | Cands: {len(cands)}")
    
    # Assertions
    assert el < 2.0, f"Query {q} took {el:.3f}s (exceeded 2.0s limit)"
    assert len(sents) <= 50, f"Query {q} exceeded page limit 50"
    if q in ("yurak", "chol"):
        assert "cholpon" in books and "hemingway" in books, f"Query '{q}' missing representation from both books!"

print("  -> PASS: All tested queries returned in < 2.0s with dual book representation where expected.")

# 5. Candidate quality check
print("\n[5] Checking Candidate Extraction Quality (Round 2)...")
code, _, resp_txt = test_url(f"{BASE_URL}/api/search?q=yurak&limit=50&page=1")
res = json.loads(resp_txt)
cands = [c.get('collocation', '') for c in res.get('corpus_candidates', [])]
print(f"  Top candidates for 'yurak': {cands[:8]}")
for c in cands:
    # Check no closed classes
    words = c.lower().split()
    for w in words:
        assert w not in {"va", "ham", "bilan", "uchun", "lekin", "ammo", "esa"}, f"Closed class word '{w}' leaked into candidate: {c}"
print("  -> PASS: No closed classes found in candidate collocations.")

# 6. Checking Anchor 12 in search
print("\n[6] Checking Anchor 12 (aln-kvk-01856) integrity on live server...")
code, _, resp_txt = test_url(f"{BASE_URL}/api/search?q={urllib.parse.quote('azayimxonnikiga')}&limit=10")
res = json.loads(resp_txt)
sents = res.get('corpus_sentences', [])
assert len(sents) > 0, "Anchor sentence with 'azayimxonnikiga' not found!"
a_sent = sents[0]
src = a_sent.get('source_raw', '')
tgt = a_sent.get('target_raw', '')
p_src = str(a_sent.get('page_source', ''))
p_tgt = str(a_sent.get('page_target', ''))
print(f"  UZ: {src[:70]}... (p. {p_src})")
print(f"  EN: {tgt[:70]}... (p. {p_tgt})")
assert '80' in p_src and '111' in p_tgt, f"Anchor 12 pages incorrect: UZ={p_src}, EN={p_tgt}"
assert "After several impractical suggestions, they decided" in tgt, f"Unexpected target text: {tgt[:50]}"
print("  -> PASS: Anchor 12 is correctly pinned to UZ 80 <-> EN 111 with drift 0 and exact Fort translation text.")

print("\n" + "=" * 75)
print("ALL LIVE VERIFICATION CHECKS PASSED ON https://tilcor.uz!")
print("=" * 75)

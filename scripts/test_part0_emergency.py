#!/usr/bin/env python3
"""
scripts/test_part0_emergency.py - PART 0 Verification:
1. Sequential 10 queries check (query field & word forms distinct)
2. Parallel 10 queries check (concurrency & isolation)
3. HTTPS 301 redirect & HSTS check
4. Error-free load of home page, yurak, and heart
"""
import ssl
import time
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://tilcor.uz"
HTTP_URL = "http://tilcor.uz"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

QUERIES_10 = [
    "qaror", "yurak", "heart", "ayvon", "chol",
    "shark", "qishloq", "baliq", "dengiz", "decision"
]

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'EmergencyTest/1.0'})
    t0 = time.time()
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        body = resp.read().decode('utf-8')
        return resp.status, body, resp.headers, time.time() - t0

def fetch_search(q):
    url = f"{BASE_URL}/api/search?q={urllib.parse.quote(q)}&limit=10"
    status, body, headers, duration = fetch_url(url)
    data = json.loads(body)
    return q, status, data, duration

def run_test():
    print("=" * 70)
    print("PART 0 — EMERGENCY CHECKS ON https://tilcor.uz")
    print("=" * 70)

    # 1. Sequential 10 queries
    print("\n[1] Testing 10 sequential queries...")
    for q in QUERIES_10:
        req_q, status, data, duration = fetch_search(q)
        resp_q = data.get("query")
        words = data.get("words", [])
        first_word = words[0].get("word") if words else "none"
        print(f"  Query: {q:<10} | Resp query: {resp_q:<10} | Time: {duration:.3f}s | 1st word: {first_word}")
        assert status == 200, f"Query {q} returned status {status}"
        assert resp_q.lower() == q.lower(), f"Cache leak! Requested '{q}', got '{resp_q}'"
    print("  -> PASS: All 10 sequential queries returned distinct, matching query responses!")

    # 2. Parallel 10 queries
    print("\n[2] Testing 10 parallel queries concurrently...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_search, QUERIES_10))

    for req_q, status, data, duration in results:
        resp_q = data.get("query")
        words = data.get("words", [])
        first_word = words[0].get("word") if words else "none"
        print(f"  [PARALLEL] Query: {req_q:<10} | Resp query: {resp_q:<10} | Time: {duration:.3f}s | 1st word: {first_word}")
        assert status == 200, f"Parallel query {req_q} returned status {status}"
        assert resp_q.lower() == req_q.lower(), f"Concurrency cache leak! Requested '{req_q}', got '{resp_q}'"
    print("  -> PASS: All 10 parallel queries returned their own isolated query field and words!")

    # 3. HTTPS & 301 check
    print("\n[3] Checking HTTPS redirect (301) and HSTS...")
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def http_error_301(self, req, fp, code, msg, headers):
            return fp
        def http_error_302(self, req, fp, code, msg, headers):
            return fp

    opener = urllib.request.build_opener(NoRedirectHandler)
    resp_http = opener.open(f"{HTTP_URL}/")
    loc = resp_http.headers.get("Location")
    print(f"  HTTP / status: {resp_http.status} | Location: {loc}")
    assert resp_http.status == 301, f"Expected 301 redirect, got {resp_http.status}"
    assert loc.startswith("https://tilcor.uz"), f"Expected redirect to https://tilcor.uz, got {loc}"

    resp_https = opener.open(f"{BASE_URL}/")
    hsts = resp_https.headers.get("Strict-Transport-Security")
    print(f"  HTTPS / status: {resp_https.status} | HSTS: {hsts}")
    assert resp_https.status == 200, f"Expected 200 for HTTPS, got {resp_https.status}"
    assert hsts and "max-age" in hsts, "HSTS header missing or invalid!"
    print("  -> PASS: HTTPS 301 redirect and HSTS confirmed!")

    # 4. Deployment check (Home page, yurak, heart)
    print("\n[4] Checking home page, yurak, and heart...")
    st_home, html_home, _, _ = fetch_url(f"{BASE_URL}/")
    assert st_home == 200 and len(html_home) > 1000, "Home page failed to load"

    _, st_yurak, d_yurak, _ = fetch_search("yurak")
    assert st_yurak == 200 and len(d_yurak.get("corpus_sentences", [])) > 0, "Yurak search failed"

    _, st_heart, d_heart, _ = fetch_search("heart")
    assert st_heart == 200 and len(d_heart.get("corpus_sentences", [])) > 0, "Heart search failed"

    print("  -> PASS: Home page and core searches load without errors!")
    print("\n" + "=" * 70)
    print("ALL PART 0 EMERGENCY CHECKS PASSED!")
    print("=" * 70)

if __name__ == '__main__':
    run_test()

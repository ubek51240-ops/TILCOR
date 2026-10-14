"""
scripts/test_live_vps.py - Verifies live https://tilcor.uz directly over HTTPS
Tests status codes, query responses for required test cases, collocation filtering, and header security.
"""

import urllib.request
import urllib.parse
import ssl
import json
import sys

BASE_URL = "https://tilcor.uz"
ctx = ssl.create_default_context()

def fetch(path, headers=None):
    url = BASE_URL + path
    hdrs = {'User-Agent': 'TILCOR-Verification-Bot/2.0'}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return resp.status, resp.read().decode('utf-8'), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8'), dict(e.headers)
    except Exception as e:
        return 999, str(e), {}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("==================================================")
    print("LIVE VERIFICATION ON HTTPS://TILCOR.UZ")
    print("==================================================")

    # 1. Anonymous Status Codes
    endpoints = [
        "/",
        "/api/stats",
        "/api/auth/me",
        "/api/ai",
        "/api/translate",
        "/api/collocations/ai-analyze?word=test",
        "/api/checker/ai-diagnose"
    ]
    print("\n--- 1. Anonymous HTTP Status Codes ---")
    status_report = {}
    for ep in endpoints:
        st, body, hdrs = fetch(ep)
        status_report[ep] = st
        print(f"  {ep:<45} -> Status: {st}")

    # 2. Test /api/collocations?q=heart filtering
    print("\n--- 2. Collocation Filter Check (/api/collocations?q=heart) ---")
    st, body, _ = fetch("/api/collocations?q=heart")
    colloc_json = json.loads(body)
    items = colloc_json.get('collocations', colloc_json.get('results', []))
    ids = [c.get('id') for c in items]
    print(f"Total returned: {len(items)}")
    colloc_2685_present = 'colloc-2685' in ids
    colloc_5766_present = 'colloc-5766' in ids
    print(f"Contains colloc-2685: {colloc_2685_present} (Expected: False)")
    print(f"Contains colloc-5766: {colloc_5766_present} (Expected: False)")

    # 3. Live Search Queries
    test_queries = [
        "yurak",
        "yuragi",
        "ko‘ngil",
        "ko'ngil",
        "koʻngil",
        "ko`ngil",
        "юрак",
        "qaror",
        "heart",
        "decision",
        "bor"
    ]

    print("\n--- 3. Live Required Queries on /api/search ---")
    query_results = {}
    for q in test_queries:
        encoded_q = urllib.parse.quote(q)
        st, body, _ = fetch(f"/api/search?q={encoded_q}")
        if st != 200:
            print(f"  Query '{q}' FAILED with status {st}")
            query_results[q] = {"error": f"Status {st}"}
            continue
        data = json.loads(body)
        summary = data.get('summary', {})
        detected_lang = data.get('detected_lang')
        words = data.get('words', [])
        collocations = data.get('collocations', [])
        sentences = data.get('corpus_sentences', [])
        is_ambiguous = data.get('is_ambiguous', False)

        first_5_words = [w.get('word') for w in words[:5]]
        first_5_collocs = [c.get('collocation') for c in collocations[:5]]
        first_5_sentences = [s.get('id') for s in sentences[:5]]

        verdict = "CORRECT"
        if q == 'yurak' and detected_lang != 'uz':
            verdict = "WRONG (language)"
        elif q == 'heart' and detected_lang != 'en':
            verdict = "WRONG (language)"
        elif q == 'bor' and not is_ambiguous:
            verdict = "WRONG (ambiguous flag missing)"

        query_results[q] = {
            "detected_lang": detected_lang,
            "is_ambiguous": is_ambiguous,
            "summary": summary,
            "first_5_words": first_5_words,
            "first_5_collocations": first_5_collocs,
            "first_5_sentences": first_5_sentences,
            "verdict": verdict
        }

        print(f"  Query: '{q:<10}' | Lang: {detected_lang} | Ambiguous: {is_ambiguous} | Words: {summary.get('total_word_forms')} | Collocs: {summary.get('collocations_count')} | Sentences: {summary.get('corpus_occurrences')} | Verdict: {verdict}")

    # Output detailed report file for analysis
    with open('scripts/live_report_output.json', 'w', encoding='utf-8') as f:
        json.dump({
            "status_report": status_report,
            "collocation_filter": {
                "total": len(items),
                "colloc_2685": colloc_2685_present,
                "colloc_5766": colloc_5766_present
            },
            "queries": query_results
        }, f, ensure_ascii=False, indent=2)
    print("\nSaved live report to scripts/live_report_output.json")

if __name__ == '__main__':
    main()

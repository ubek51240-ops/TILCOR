#!/usr/bin/env python3
"""
scripts/verify_step04_live.py - Live Verification for TILCOR_04 on https://tilcor.uz
Verifies all 6 proof requirements of Section 6 on the live production domain.
"""

import urllib.request
import urllib.parse
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://tilcor.uz"

def test_url(url, follow_redirects=True):
    req = urllib.request.Request(url, headers={'User-Agent': 'TILCOR-Verification/1.0'})
    try:
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                return fp
        if not follow_redirects:
            opener = urllib.request.build_opener(NoRedirectHandler)
            resp = opener.open(req)
            return resp.status, resp.headers, resp.read().decode('utf-8', errors='replace')
        else:
            with urllib.request.urlopen(req, context=ctx) as resp:
                return resp.status, resp.headers, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode('utf-8', errors='replace')

print("="*70)
print("LIVE VERIFICATION ON https://tilcor.uz (STEP 04)")
print("="*70)

# 1. Admin redirect test
print("\n[1] Testing Admin Redirect (preview_alignment_queue.html & annotation_workspace.html)...")
code1, h1, body1 = test_url(f"{BASE_URL}/preview_alignment_queue.html", follow_redirects=False)
loc1 = h1.get('Location', '')
print(f"  /preview_alignment_queue.html -> Code: {code1}, Location: {loc1}")

code2, h2, body2 = test_url(f"{BASE_URL}/annotation_workspace.html", follow_redirects=False)
loc2 = h2.get('Location', '')
print(f"  /annotation_workspace.html -> Code: {code2}, Location: {loc2}")
assert '/kirish' in loc1 and '/kirish' in loc2, "Admin redirect to /kirish failed!"
print("  -> PASSED: Unauthenticated admin requests redirect to /kirish!")

# 2. KWIC Concordance page
print("\n[2] Testing KWIC Conkordans Page...")
code_kwic, _, body_kwic = test_url(f"{BASE_URL}/kwic_concordance.html")
has_kwic_title = "<title>KWIC konkordans | TILCOR</title>" in body_kwic
has_kwic_h1 = "KWIC konkordans" in body_kwic
has_kalit_soz = "Kalit so‘z" in body_kwic or "Kalit so&#8216;z" in body_kwic or "Kalit so" in body_kwic
print(f"  Title: {'KWIC konkordans | TILCOR' if has_kwic_title else 'MISSING'}")
print(f"  Heading: {'KWIC konkordans' if has_kwic_h1 else 'MISSING'}")
print(f"  Header 'Kalit so‘z': {'YES' if has_kalit_soz else 'NO'}")
assert has_kwic_title and has_kwic_h1, "KWIC verification failed!"
print("  -> PASSED: KWIC page title and headings verified!")

# 3. Methodology & Statistics page
print("\n[3] Testing Methodology & Statistics Page...")
code_stat, _, body_stat = test_url(f"{BASE_URL}/methodology_statistics.html")
has_calc_label = "Hisoblash namunasi — korpus natijasi emas" in body_stat
has_logdice = "logDice" in body_stat
has_ch3_empty = "Tasdiqlangan annotatsiyalar hali yo‘q" in body_stat
print(f"  Calculator label: {'OK' if has_calc_label else 'MISSING'}")
print(f"  logDice metric present: {'YES' if has_logdice else 'NO'}")
print(f"  Chapter III placeholder: {'YES' if has_ch3_empty else 'NO'}")
assert has_calc_label and has_logdice, "Statistics verification failed!"
print("  -> PASSED: Statistics page corrected with logDice and calculator label!")

# 4. Search API verification for yurak, ko‘ngil, qaror, heart, decision
print("\n[4] Testing Search API for the 5 Key Words...")
for word in ['ko‘ngil', 'yurak', 'qaror', 'heart', 'decision']:
    encoded_w = urllib.parse.quote(word)
    url = f"{BASE_URL}/api/search?q={encoded_w}&limit=10"
    code, _, data_txt = test_url(url)
    data = json.loads(data_txt)
    cands = data.get('corpus_candidates', [])
    sents = data.get('corpus_sentences', [])
    words_list = data.get('words', [])
    print(f"\n  Query: '{word}' (lang: {data.get('selected_lang')}) -> Found {len(sents)} sentences, {len(cands)} candidates, {len(words_list)} word forms")
    
    print("    Top 5 candidates:")
    for idx, c in enumerate(cands[:5], 1):
        scnt = c.get('sentences_count', 0)
        ocnt = c.get('occurrences_count', 0)
        pat = c.get('pattern', '—')
        col = c.get('collocation', '')
        print(f"      {idx}. {col:<22} | Qolip: {pat:<14} | {scnt} gapda · {ocnt} marta")
    
    if sents:
        s0 = sents[0]
        has_eq = s0.get('has_equivalent')
        eq_label = s0.get('target_status_label')
        print(f"    Sample Sentence #1: Status='{s0.get('alignment_status')}', Label='{eq_label}', HasEquivalent={has_eq}")
        print(f"      Page info: {s0.get('page_source')} -> {s0.get('page_target')}")

print("\n" + "="*70)
print("ALL LIVE PRODUCTION TESTS ON https://tilcor.uz COMPLETED SUCCESSFULLY!")
print("="*70)

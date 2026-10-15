#!/usr/bin/env python3
"""
scripts/verify_v36_live.py - Section 3 verification tests from DEPLOY_v3.6_UZ.md
"""
import sys
import re
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')
BASE = "https://tilcor.uz"

def check_url(path, allow_redirect=False):
    url = f"{BASE}{path}"
    try:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
                
        opener = urllib.request.build_opener() if allow_redirect else urllib.request.build_opener(NoRedirect)
        req = urllib.request.Request(url)
        with opener.open(req, timeout=15) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR: {e}"

print("=== 1. Private files (Must return 404) ===")
private_paths = [
    "/server.py",
    "/data/full_corpus.json",
    "/data/corpus_dictionary.json",
    "/data/reference_en.json",
    "/data/validation/samples.json",
    "/data/validation/annotations.json",
    "/secrets/admin.password",
    "/secrets/annotator.password",
    "/.git/config",
    "/notes/tanlab_tekshiruv_lugat_2026-10-14.md"
]
p_pass = 0
for p in private_paths:
    code = check_url(p)
    ok = (code == 404)
    if ok: p_pass += 1
    print(f"[{code}] {p:45} {'PASS (404)' if ok else 'FAIL'}")

print(f"\nPrivate files check: {p_pass}/{len(private_paths)} PASS")

print("\n=== 2. Public routes (Must return 200) ===")
public_paths = [
    "/?lang=uz",
    "/?lang=en",
    "/?lang=ru",
    "/css/tilcor.css?v=3.6",
    "/lugat",
    "/lugat?q=yurak",
    "/lugat?q=heart",
    "/qidiruv?q=yurak",
    "/kwic?q=yurak",
    "/kollokatsiyalar",
    "/korpus",
    "/metodologiya",
    "/statistika"
]
pub_pass = 0
for p in public_paths:
    code = check_url(p)
    ok = (code == 200)
    if ok: pub_pass += 1
    print(f"[{code}] {p:30} {'PASS (200)' if ok else 'FAIL'}")

print(f"\nPublic routes check: {pub_pass}/{len(public_paths)} PASS")

print("\n=== 3. Baholash redirect check (Must return 302) ===")
baholash_code = check_url("/baholash")
print(f"[{baholash_code}] /baholash -> {'PASS (302)' if baholash_code == 302 else 'FAIL'}")

print("\n=== 4. Content checks ===")
req = urllib.request.Request(f"{BASE}/")
with urllib.request.urlopen(req, timeout=15) as resp:
    home_html = resp.read().decode('utf-8', 'replace')
    has_kontekst = "kontekstda" in home_html
    has_214 = bool(re.search(r"214.{1,2}244", home_html))
    print(f"Homepage contains 'kontekstda': {has_kontekst}")
    print(f"Homepage contains '214 244': {has_214}")

req_stat = urllib.request.Request(f"{BASE}/statistika")
with urllib.request.urlopen(req_stat, timeout=15) as resp:
    stat_html = resp.read().decode('utf-8', 'replace')
    has_tayanch = "Tayanch korpus" in stat_html
    print(f"Statistika contains 'Tayanch korpus': {has_tayanch}")

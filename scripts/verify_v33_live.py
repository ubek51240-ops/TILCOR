#!/usr/bin/env python3
"""
scripts/verify_v33_live.py - Section 4 verification tests from DEPLOY_v3.3_UZ.md
"""
import sys
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')
BASE = "https://tilcor.uz"

def check_url(path):
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR: {e}"

print("=== 1. Private files (Must return 404) ===")
private_paths = [
    "/server.py",
    "/data/full_corpus.json",
    "/data/word_alignment.json",
    "/secrets/admin.password",
    "/.git/config"
]
p_pass = 0
for p in private_paths:
    code = check_url(p)
    ok = (code == 404)
    if ok: p_pass += 1
    print(f"[{code}] {p:30} {'PASS (404)' if ok else 'FAIL'}")

print(f"\nPrivate files check: {p_pass}/{len(private_paths)} PASS")

print("\n=== 2. Public routes (Must return 200) ===")
public_paths = [
    "/?lang=uz",
    "/assets/tilcor-emblem.svg",
    "/css/tilcor.css?v=3.3",
    "/qidiruv?q=yurak",
    "/kollokatsiyalar",
    "/statistika",
    "/metodologiya",
    "/kwic?q=yurak"
]
pub_pass = 0
for p in public_paths:
    code = check_url(p)
    ok = (code == 200)
    if ok: pub_pass += 1
    print(f"[{code}] {p:30} {'PASS (200)' if ok else 'FAIL'}")

print(f"\nPublic routes check: {pub_pass}/{len(public_paths)} PASS")

print("\n=== 3. Search 'yurak' check ===")
req = urllib.request.Request(f"{BASE}/qidiruv?q=yurak")
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', 'replace')
    has_heart = "heart" in html.lower()
    has_28 = "28" in html
    print(f"Contains 'heart': {has_heart}")
    print(f"Contains '28 gapda': {has_28}")

print("\n=== 4. Kollokatsiyalar check ===")
req2 = urllib.request.Request(f"{BASE}/kollokatsiyalar")
with urllib.request.urlopen(req2, timeout=15) as resp:
    html_kolloc = resp.read().decode('utf-8', 'replace')
    print(f"Contains '967' kollokatsiya: {'967' in html_kolloc}")

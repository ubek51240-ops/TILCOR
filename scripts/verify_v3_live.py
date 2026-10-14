#!/usr/bin/env python3
"""
scripts/verify_v3_live.py - Section 4 verification tests from DEPLOY_v3_UZ.md
"""
import sys
import urllib.request
import urllib.error
import ssl

sys.stdout.reconfigure(encoding='utf-8')
BASE = "https://tilcor.uz"

# Ignore SSL self-signed if any, though tilcor has ECDSA
ctx = ssl.create_default_context()

def check_url(path, method="GET", headers=None, data=None):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data:
        req.data = data.encode('utf-8') if isinstance(data, str) else data
        
    try:
        # Don't follow redirects to check 302
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
                
        opener = urllib.request.build_opener(NoRedirect)
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
    "/data/word_alignment.json",
    "/data/phd_corpus.db",
    "/secrets/admin.password",
    "/.git/config",
    "/DEPLOY_v3_UZ.md"
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
    "/",
    "/qidiruv?q=yurak",
    "/qidiruv?q=heart&lang=en",
    "/kollokatsiyalar",
    "/kollokatsiyalar?til=en&tartib=log_dice",
    "/kwic?q=yurak",
    "/korpus",
    "/statistika",
    "/metodologiya",
    "/manbalar",
    "/loyiha-haqida",
    "/yoriqnoma",
    "/statistika?lang=ru",
    "/kirish"
]
pub_pass = 0
for p in public_paths:
    code = check_url(p)
    ok = (code == 200)
    if ok: pub_pass += 1
    print(f"[{code}] {p:42} {'PASS (200)' if ok else 'FAIL'}")

print(f"\nPublic routes check: {pub_pass}/{len(public_paths)} PASS")

print("\n=== 3. Security checks ===")
admin_cookie_code = check_url("/admin_collocations.html", headers={"Cookie": "tilcor_session=admin"})
print(f"[{admin_cookie_code}] Fake cookie admin check: {'PASS (302)' if admin_cookie_code == 302 else 'FAIL (Expected 302)'}")

unauth_post_code = check_url("/api/annotate", method="POST", data="{}")
print(f"[{unauth_post_code}] Unauthenticated annotation check: {'PASS (401)' if unauth_post_code == 401 else 'FAIL (Expected 401)'}")

print("\n=== 4. Search Content Verification ===")
req = urllib.request.Request(f"{BASE}/qidiruv?q=yurak")
with urllib.request.urlopen(req, timeout=15) as resp:
    html_yurak = resp.read().decode('utf-8', 'replace')
    has_heart = "heart" in html_yurak.lower()
    print(f"Search 'yurak' contains 'heart': {has_heart}")

req2 = urllib.request.Request(f"{BASE}/kollokatsiyalar")
with urllib.request.urlopen(req2, timeout=15) as resp:
    html_kolloc = resp.read().decode('utf-8', 'replace')
    print(f"Kollokatsiyalar page loaded ({len(html_kolloc)} chars)")

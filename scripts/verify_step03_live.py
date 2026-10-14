"""
scripts/verify_step03_live.py - Comprehensive verification against live tilcor.uz
Tests HTTPS, SSL certificate, anonymous status codes, search normalization,
candidate extraction, So'zlar section, and Russian query rejection.
"""

import urllib.request
import urllib.parse
import ssl
import socket
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://tilcor.uz"

# 1. SSL Certificate Inspection
print("=== 1. SSL Sertifikati Tekshiruvi ===")
hostname = "tilcor.uz"
context = ssl.create_default_context()
with socket.create_connection((hostname, 443), timeout=10) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        cert = ssock.getpeercert()
        issuer = dict(x[0] for x in cert['issuer'])
        subject = dict(x[0] for x in cert['subject'])
        not_before = cert['notBefore']
        not_after = cert['notAfter']
        print(f"Issuer: {issuer.get('organizationName', 'N/A')} ({issuer.get('commonName', 'N/A')})")
        print(f"Subject: {subject.get('commonName', 'N/A')}")
        print(f"Amal qilish muddati: {not_before} dan {not_after} gacha")

# 2. Anonymous HTTP Status Codes
print("\n=== 2. Anonim HTTP Status Kodlari ===")
endpoints = [
    ("/", 200),
    ("/kirish", 200),
    ("/methodology.html", 200),
    ("/sources_rights.html", 200),
    ("/preview_alignment_queue.html", 401),
    ("/platform_factsheet.html", 401),
    ("/admin/collocations", 401),
    ("/api/ai", 401),
    ("/api/translate", 401),
    ("/api/collocations/ai-analyze", 401),
    ("/api/checker/ai-diagnose", 401),
    ("/sources/source_register.json", 403)
]

for ep, expected_status in endpoints:
    url = f"{BASE_URL}{ep}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            print(f"{ep:35} -> {code} (Kutilgan: {expected_status}) {'PASS' if code == expected_status else 'FAIL'}")
    except urllib.error.HTTPError as e:
        print(f"{ep:35} -> {e.code} (Kutilgan: {expected_status}) {'PASS' if e.code == expected_status else 'FAIL'}")
    except Exception as e:
        print(f"{ep:35} -> Xatolik: {e}")

# 3. Live Search Engine & Russian Query Test
print("\n=== 3. Qidiruv va Ruscha so'rov tekshiruvi ===")
def fetch_search(q, lang="auto"):
    url = f"{BASE_URL}/api/search?q={urllib.parse.quote(q)}&lang={lang}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

res_ru = fetch_search("привет")
print("Ruscha 'привет' so'rovi xabari:", res_ru.get('error'))

res_yurak = fetch_search("yurak")
print(f"yurak: {res_yurak.get('summary', {}).get('corpus_occurrences')} occurrences, "
      f"{len(res_yurak.get('words', []))} words, "
      f"{len(res_yurak.get('collocations', []))} candidates")
print("  Top 5 candidates for yurak:", [c['collocation'] for c in res_yurak.get('collocations', [])[:5]])
print("  Top 5 words for yurak:", [w['word'] for w in res_yurak.get('words', [])[:5]])

res_kongil = fetch_search("ko‘ngil")
print(f"ko‘ngil: {res_kongil.get('summary', {}).get('corpus_occurrences')} occurrences, "
      f"{len(res_kongil.get('words', []))} words, "
      f"{len(res_kongil.get('collocations', []))} candidates")
print("  Top 5 candidates for ko‘ngil:", [c['collocation'] for c in res_kongil.get('collocations', [])[:5]])
print("  Top 5 words for ko‘ngil:", [w['word'] for w in res_kongil.get('words', [])[:5]])

# Save results for final report
results_summary = {
    "cert": {"issuer": issuer, "not_after": not_after},
    "yurak": res_yurak.get('summary'),
    "kongil": res_kongil.get('summary')
}
with open('scripts/live_report_output.json', 'w', encoding='utf-8') as f:
    json.dump(results_summary, f, ensure_ascii=False, indent=2)

print("\nJonli verifikatsiya yakunlandi!")

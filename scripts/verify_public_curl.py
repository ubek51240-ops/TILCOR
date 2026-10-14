import subprocess
import json
import re

print("=====================================================================")
print("1. curl -sI https://tilcor.uz/")
print("=====================================================================")
out1 = subprocess.check_output(["curl.exe", "-k", "-sI", "https://tilcor.uz/"]).decode('utf-8', errors='replace')
print(out1.strip())

print("\n=====================================================================")
print("2. curl \"https://tilcor.uz/api/search?q=yurak\" (first 300 chars)")
print("=====================================================================")
out2 = subprocess.check_output(["curl.exe", "-k", "-s", "https://tilcor.uz/api/search?q=yurak"]).decode('utf-8', errors='replace')
print(out2[:300])
try:
    d2 = json.loads(out2)
    print("Parsed JSON query:", d2.get('query'))
    print("Parsed JSON totalFound:", d2.get('totalFound'))
    print("Parsed JSON muqobil sources:", list(d2.get('muqobil_summary', {}).keys()))
except Exception as e:
    print("JSON parse error:", e)

print("\n=====================================================================")
print("3. curl \"https://tilcor.uz/api/search?q=heart\" (first 300 chars)")
print("=====================================================================")
out3 = subprocess.check_output(["curl.exe", "-k", "-s", "https://tilcor.uz/api/search?q=heart"]).decode('utf-8', errors='replace')
print(out3[:300])
try:
    d3 = json.loads(out3)
    print("Parsed JSON query:", d3.get('query'))
    print("Parsed JSON totalFound:", d3.get('totalFound'))
    print("Parsed JSON detected_lang:", d3.get('detected_lang'))
except Exception as e:
    print("JSON parse error:", e)

print("\n=====================================================================")
print("4. curl \"https://tilcor.uz/?lang=en\" (verifying English interface)")
print("=====================================================================")
out4 = subprocess.check_output(["curl.exe", "-k", "-s", "https://tilcor.uz/?lang=en"]).decode('utf-8', errors='replace')
title = re.search(r'<title>(.*?)</title>', out4)
h1 = re.search(r'<h1[^>]*>(.*?)</h1>', out4, flags=re.DOTALL)
html_lang = re.search(r'<html[^>]*lang=["\']([^"\']+)["\']', out4)
print("HTML lang attribute:", html_lang.group(1) if html_lang else "Not found")
print("Page Title:", title.group(1).strip() if title else "Not found")
print("Main Heading (H1):", " ".join(h1.group(1).split()) if h1 else "Not found")
nav_items = re.findall(r'<span data-i18n="[^"]+">([^<]+)</span>', out4)
print("Navigation items translated:", nav_items[:6])

print("\n=====================================================================")
print("5. curl \"https://tilcor.uz/api/kwic?q=yurak\" (verifying line count)")
print("=====================================================================")
out5 = subprocess.check_output(["curl.exe", "-k", "-s", "https://tilcor.uz/api/kwic?q=yurak"]).decode('utf-8', errors='replace')
try:
    d5 = json.loads(out5)
    print("Total KWIC lines returned:", len(d5.get('results', [])))
    print("Total count field:", d5.get('total'))
    print("First 3 KWIC lines:")
    for r in d5.get('results', [])[:3]:
        print(f"  #{r.get('id')} [{r.get('book')}, {r.get('page')}]: {r.get('left')[-25:]} <{r.get('node')}> {r.get('right')[:25]}")
except Exception as e:
    print("JSON error:", e)

print("\n=====================================================================")
print("6. ADDITIONAL CHECK: curl \"https://tilcor.uz/kollokatsiya/og‘ir%20uyqu\"")
print("=====================================================================")
out6 = subprocess.check_output(["curl.exe", "-k", "-s", "https://tilcor.uz/kollokatsiya/og%E2%80%98ir%20uyqu"]).decode('utf-8', errors='replace')
print("Contains 1. Kitobdagi tarjima — tasdiqlangan:", "1. Kitobdagi tarjima — tasdiqlangan" in out6)
print("Contains Korpusdagi Namunalar:", "Korpusdagi Namunalar" in out6)
m_eq = re.findall(r'«([^»]+)»\s*\(\d+\s*marta', out6)
print("Found equivalents in profile:", m_eq)

print("\n=====================================================================")
print("7. ADDITIONAL CHECK: curl \"https://tilcor.uz/methodology_statistics.html\"")
print("=====================================================================")
out7 = subprocess.check_output(["curl.exe", "-k", "-s", "https://tilcor.uz/methodology_statistics.html"]).decode('utf-8', errors='replace')
print("Contains 'Norm / 1M':", "Norm / 1M" in out7)
print("Contains 'Norm / 10k':", "Norm / 10k" in out7)
print("Contains '3.1-Jadval':", "3.1-Jadval" in out7)
print("Contains '3.2-Jadval':", "3.2-Jadval" in out7)
print("Contains '3.3-Jadval':", "3.3-Jadval" in out7)

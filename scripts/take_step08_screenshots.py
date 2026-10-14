import os, sys, urllib.parse
from playwright.sync_api import sync_playwright

BASE_URL = "https://tilcor.uz"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "screenshots", "step08")
os.makedirs(OUTPUT_DIR, exist_ok=True)

targets = [
    ("home", "/"),
    ("qidiruv_ogir_uyqu", "/qidiruv?q=" + urllib.parse.quote("og‘ir uyqu")),
    ("soz_heart", "/soz/heart")
]
languages = ["uz", "en", "ru"]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    
    for name, path in targets:
        for lang in languages:
            sep = "&" if "?" in path else "?"
            full_url = f"{BASE_URL}{path}{sep}lang={lang}"
            dest = os.path.join(OUTPUT_DIR, f"{name}_{lang}.png")
            print(f"Navigating to: {full_url}")
            try:
                page.goto(full_url, wait_until="networkidle", timeout=30000)
                page.screenshot(path=dest, full_page=False)
                print(f"[OK] Saved: {dest}")
            except Exception as e:
                print(f"[ERR] Failed {full_url}: {e}")
                
    browser.close()
print("All 9 screenshots taken successfully.")

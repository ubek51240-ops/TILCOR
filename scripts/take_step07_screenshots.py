import os
import time
from playwright.sync_api import sync_playwright

os.makedirs('data/screenshots/step07', exist_ok=True)

QUERIES = [
    ("og‘ir uyqu", "ogir_uyqu"),
    ("javob bermoq", "javob_bermoq"),
    ("heart", "heart"),
    ("set the table", "set_the_table")
]

LANGS = ['uz', 'en', 'ru']

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            ignore_https_errors=True
        )
        page = context.new_page()

        for q_text, q_slug in QUERIES:
            for lang in LANGS:
                url = f"https://tilcor.uz/?lang={lang}"
                print(f"Capturing: '{q_text}' [{lang}] -> {url}...")
                page.goto(url, wait_until="networkidle", timeout=30000)

                # Make view-corpus visible and trigger search
                page.evaluate(f"""() => {{
                    document.querySelectorAll('.tab-view').forEach(v => v.classList.add('hidden'));
                    const vCorpus = document.getElementById('view-corpus');
                    if (vCorpus) vCorpus.classList.remove('hidden');
                    
                    if (window.corpusManager) {{
                        window.corpusManager.search("{q_text}");
                    }}
                }}""")

                # Wait for muqobil section to be visible
                page.wait_for_selector('#results-section-muqobil', state='visible', timeout=15000)
                time.sleep(2.0)

                out_path = f"data/screenshots/step07/{q_slug}_{lang}.png"
                page.screenshot(path=out_path, full_page=False)
                print(f"  -> Saved: {out_path}")

        browser.close()
        print("\nAll 12 screenshots successfully captured and saved in data/screenshots/step07/!")

if __name__ == '__main__':
    capture_screenshots()

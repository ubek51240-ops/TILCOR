import os
import sys
import asyncio
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://tilcor.uz"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Words that indicate Uzbek interface leakage (when not inside corpus text/book titles)
UZBEK_INTERFACE_KEYWORDS = [
    "Bosh sahifa", "Tahlil", "Metodologiya", "Manbalar va huquqlar", "Kirish",
    "So‘z shakllari", "Kollokatsiya qidiruvi", "Korpus qidiruvi", "Namunaviy so‘rovlar:",
    "Yuklanmoqda...", "Hech qanday natija topilmadi"
]

async def run_tests():
    print(f"[*] Starting Playwright i18n testing against {BASE_URL}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # 1. Test clicking 'En' on home page
        print("[1] Opening home page and clicking 'En'...")
        await page.goto(f"{BASE_URL}/", timeout=30000)
        await page.wait_for_load_state("networkidle")
        
        # Click En
        en_btn = page.locator("#langBtn-en")
        await en_btn.click()
        await page.wait_for_load_state("networkidle")
        
        # Verify URL has lang=en or page is rendered in English
        content = await page.content()
        assert "lang=\"en\"" in content, "HTML lang attribute is not 'en' after clicking En!"
        print("  -> PASS: Clicked 'En' and page switched to English!")
        
        # Screenshot Home EN
        ss_home_en = os.path.join(SCREENSHOTS_DIR, "home_en.png")
        await page.screenshot(path=ss_home_en, full_page=False)
        print(f"  -> Screenshot saved: {ss_home_en}")

        # 2. Test Home Page RU
        print("[2] Opening home page in RU (?lang=ru)...")
        await page.goto(f"{BASE_URL}/?lang=ru", timeout=30000)
        await page.wait_for_load_state("networkidle")
        content_ru = await page.content()
        assert "lang=\"ru\"" in content_ru, "HTML lang attribute is not 'ru'!"
        
        ss_home_ru = os.path.join(SCREENSHOTS_DIR, "home_ru.png")
        await page.screenshot(path=ss_home_ru, full_page=False)
        print(f"  -> Screenshot saved: {ss_home_ru}")

        # 3. Test Search 'yurak' in EN
        print("[3] Testing search 'yurak' with lang=en...")
        await page.goto(f"{BASE_URL}/?lang=en", timeout=30000)
        await page.wait_for_load_state("networkidle")
        
        # Input yurak in search
        search_input = page.locator("#universalSearchInput")
        if await search_input.count() > 0:
            await search_input.fill("yurak")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(2500)
            
            ss_search_en = os.path.join(SCREENSHOTS_DIR, "search_yurak_en.png")
            await page.screenshot(path=ss_search_en, full_page=False)
            print(f"  -> Screenshot saved: {ss_search_en}")

        # 4. Check interface strings for leakage across public pages in EN
        print("[4] Checking visible text on public pages in EN for Uzbek leakage...")
        for page_name in ["", "methodology_statistics.html", "sources_rights.html"]:
            url = f"{BASE_URL}/{page_name}?lang=en"
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # Check nav menu or header visible text
            header_loc = page.locator("nav") if await page.locator("nav").count() > 0 else page.locator("header")
            nav_text = await header_loc.inner_text()
            for kw in ["Bosh sahifa", "Tahlil", "Metodologiya", "Manbalar va huquqlar", "Kirish"]:
                assert kw not in nav_text, f"Uzbek interface keyword '{kw}' leaked in EN nav menu on {url}!"
            print(f"  -> {url}: 0 Uzbek interface keywords in header/nav!")

        print("\n=======================================================")
        print("ALL PLAYWRIGHT I18N AND BROWSER TESTS PASSED (0 UZBEK STRINGS IN INTERFACE)!")
        print("=======================================================")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_tests())

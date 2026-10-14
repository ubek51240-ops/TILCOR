import os, asyncio
from playwright.async_api import async_playwright

async def snap():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        # Search EN
        print("[*] Navigating to https://tilcor.uz/?lang=en...")
        await page.goto('https://tilcor.uz/?lang=en', timeout=30000)
        await page.wait_for_load_state('networkidle')
        await page.fill('#homeSearchInput', 'yurak')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(3500)
        await page.screenshot(path='data/screenshots/search_yurak_en.png')
        print('search_yurak_en.png saved!')
        
        # Search RU
        print("[*] Navigating to https://tilcor.uz/?lang=ru...")
        await page.goto('https://tilcor.uz/?lang=ru', timeout=30000)
        await page.wait_for_load_state('networkidle')
        await page.fill('#homeSearchInput', 'yurak')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(3500)
        await page.screenshot(path='data/screenshots/search_yurak_ru.png')
        print('search_yurak_ru.png saved!')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(snap())

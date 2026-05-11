import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://nebius.com/prices")
        await page.wait_for_timeout(3000)
        els = await page.query_selector_all("table tr, .pricing-table > div, div[role='row'], div.grid, table tbody tr, div")
        for el in els:
            try:
                txt = await el.inner_text()
                if "NVIDIA" in txt and "$" in txt:
                    # Let's see what the container is and how many lines it has
                    lines = txt.split('\n')
                    if len(lines) > 2 and len(lines) < 20:
                        print(f"FOUND BLOCK:\n{txt}\n------------------")
            except Exception:
                pass
        await browser.close()

asyncio.run(main())

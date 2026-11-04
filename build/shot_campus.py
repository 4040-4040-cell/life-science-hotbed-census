import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('file:///home/claude/build/site/index.html#basel-land'); await pg.wait_for_timeout(4500)
        el=await pg.query_selector('#v-basel-land section.campus'); await el.screenshot(path='shots/campus_bl.png')
        await pg.goto('file:///home/claude/build/site/index.html#basel-city'); await pg.wait_for_timeout(4500)
        m=await pg.query_selector('#map-basel-city'); await m.scroll_into_view_if_needed(); await pg.wait_for_timeout(800)
        for i in range(2): await pg.click('#v-basel-city .leaflet-control-zoom-in'); await pg.wait_for_timeout(800)
        await m.screenshot(path='shots/map_bs.png')
        print(errs); await b.close()
asyncio.run(main())

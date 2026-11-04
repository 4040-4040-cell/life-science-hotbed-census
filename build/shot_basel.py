import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1050})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('file:///home/claude/build/site/index.html#basel'); await pg.wait_for_timeout(4000)
        await pg.screenshot(path='shots/b_top.png')
        await pg.screenshot(path='shots/b_full.png',full_page=True)
        await pg.goto('file:///home/claude/build/site/index.html#compare'); await pg.wait_for_timeout(3000)
        await pg.screenshot(path='shots/b_compare.png')
        await pg.goto('file:///home/claude/build/site/index.html#basel'); await pg.wait_for_timeout(3000)
        await pg.fill('#q-basel','Idorsia'); await pg.wait_for_timeout(300)
        await pg.click('#t-basel tbody tr >> nth=0'); await pg.wait_for_timeout(1200)
        el=await pg.query_selector('#drawer'); await el.screenshot(path='shots/b_drawer.png')
        print('errors:',errs[:10]); await b.close()
asyncio.run(main())

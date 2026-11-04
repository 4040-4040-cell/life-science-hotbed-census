import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1050})
        errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
        for h in ['compare','biotech-beach','genetown','biotech-bay','uk','biomidwest','pharm-country','bio-nc','biocapital','seattle','colorado']:
            await pg.goto(f'file:///home/claude/build/site/index.html#{h}'); await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f'shots/f_{h}.png')
        await pg.goto('file:///home/claude/build/site/index.html#biotech-beach'); await pg.wait_for_timeout(3000)
        await pg.fill('#q-biotech-beach','Neurocrine'); await pg.wait_for_timeout(300)
        await pg.click('#t-biotech-beach tbody tr >> nth=0'); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='shots/f_drawer.png')
        el=await pg.query_selector('#drawer'); await el.screenshot(path='shots/f_drawer_full.png')
        print('errors:',errs[:10]); await b.close()
asyncio.run(main())

import asyncio,sys
from playwright.async_api import async_playwright
async def main(pages):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000})
        errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
        for h,out,full in pages:
            await pg.goto(f'file:///home/claude/build/site/index.html#{h}'); await pg.wait_for_timeout(3500)
            await pg.screenshot(path=out,full_page=full)
        if len(sys.argv)>1 and sys.argv[1]=='drawer':
            await pg.goto('file:///home/claude/build/site/index.html#biotech-beach'); await pg.wait_for_timeout(3000)
            await pg.click('.lcell >> nth=0'); await pg.wait_for_timeout(800); await pg.screenshot(path='shots/drawer.png')
        print('errors:',errs[:10]); await b.close()
import os; os.makedirs('shots',exist_ok=True)
asyncio.run(main([('compare','shots/compare.png',False),('biotech-beach','shots/beach.png',False)]))

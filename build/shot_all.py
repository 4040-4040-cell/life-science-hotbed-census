import asyncio,sys
from playwright.async_api import async_playwright
H=sys.argv[1].split(',')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1050})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        for h in H:
            await pg.goto(f'file:///home/claude/build/site/index.html#{h}'); await pg.wait_for_timeout(4500)
            await pg.screenshot(path=f'shots/a_{h}.png')
            if h!='compare':
                el=await pg.query_selector(f'#map-{h}') or await pg.query_selector('.leaflet-container >> nth=1')
                await pg.evaluate("window.scrollTo(0, document.body.scrollHeight*0.45)"); await pg.wait_for_timeout(1500)
                await pg.screenshot(path=f'shots/a_{h}_mid.png')
        print('errors:',errs[:10]); await b.close()
asyncio.run(main())

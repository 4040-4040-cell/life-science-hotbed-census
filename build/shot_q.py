import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1150})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('file:///home/claude/build/site/index.html#compare'); await pg.wait_for_timeout(2500)
        await pg.screenshot(path='shots/q_compare.png')
        for slug,q in [('biotech-beach','Artiva'),('biocapital','Samsung'),('basel','Boehringer'),('uk','Almac')]:
            await pg.goto(f'file:///home/claude/build/site/index.html#{slug}'); await pg.wait_for_timeout(3500)
            await pg.fill(f'#q-{slug}',q); await pg.wait_for_timeout(400)
            await pg.click(f'#t-{slug} tbody tr >> nth=0'); await pg.wait_for_timeout(1200)
            el=await pg.query_selector('#drawer'); await el.screenshot(path=f'shots/q_{slug}.png')
            await pg.click('#drawer button'); await pg.wait_for_timeout(300)
            await pg.fill(f'#q-{slug}',''); 
        # interactive map at high zoom
        await pg.goto('file:///home/claude/build/site/index.html#genetown'); await pg.wait_for_timeout(3500); await b.close(); print('errors',errs[:5]); return
        m=await pg.query_selector_all('.leaflet-container'); print(len(m))
        await m[-1].scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
        for i in range(3):
            await pg.click('.leaflet-control-zoom-in >> nth=-1'); await pg.wait_for_timeout(700)
        await m[-1].screenshot(path='shots/q_zoom.png')
        print('errors',errs[:5]); await b.close()
asyncio.run(main())

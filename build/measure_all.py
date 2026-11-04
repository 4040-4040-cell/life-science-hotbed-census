import asyncio
from playwright.async_api import async_playwright
SL='basel-city,basel-land'.split(',')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        for s in SL:
            await pg.goto(f'file:///home/claude/build/site/index.html#{s}'); await pg.wait_for_timeout(3500)
            await pg.evaluate(f"window.preparePrint('{s}')"); await pg.wait_for_timeout(1200); await pg.emulate_media(media='print')
            r=await pg.evaluate(f"()=>[document.documentElement.scrollWidth,Math.round(document.querySelector('#v-{s}').getBoundingClientRect().height),Math.round(document.querySelector('#v-{s} .psheet').getBoundingClientRect().height),Math.round(document.querySelector('#exw-{s}').getBoundingClientRect().height)]")
            print(s,r); await pg.emulate_media(media='screen'); await pg.evaluate("endPrint()")
        await b.close()
asyncio.run(main())

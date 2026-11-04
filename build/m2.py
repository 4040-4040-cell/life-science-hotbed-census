import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        for s in ['basel-city','basel-land']:
            await pg.goto(f'file:///home/claude/build/site/index.html#{s}'); await pg.wait_for_timeout(3500)
            await pg.evaluate(f"window.preparePrint('{s}')"); await pg.wait_for_timeout(1000); await pg.emulate_media(media='print')
            r=await pg.evaluate(f"()=>[...document.querySelectorAll('#v-{s} .psheet > *, #v-{s} .pgrid > *')].map(e=>e.className+':'+Math.round(e.getBoundingClientRect().height)+'x'+Math.round(e.getBoundingClientRect().width))")
            print(s,r); await pg.emulate_media(media='screen'); await pg.evaluate("endPrint()")
        await b.close()
asyncio.run(main())

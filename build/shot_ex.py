import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        await pg.goto('file:///home/claude/build/site/index.html#genetown'); await pg.wait_for_timeout(4500)
        el=await pg.query_selector('#exw-genetown'); await el.screenshot(path='shots/ex_screen.png')
        n=await pg.evaluate("document.querySelector('#exw-genetown svg.leaders').innerHTML.length")
        d=await pg.evaluate("getComputedStyle(document.querySelector('#exw-genetown svg.leaders')).display")
        print(n,d); await b.close()
asyncio.run(main())

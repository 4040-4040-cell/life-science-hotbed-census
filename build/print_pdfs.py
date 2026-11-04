import asyncio,sys
from playwright.async_api import async_playwright
SL=sys.argv[1].split(',')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        for s in SL:
            await pg.goto(f'file:///home/claude/build/site/index.html#{s}'); await pg.wait_for_timeout(4500)
            if s=='compare': await pg.evaluate("window.preparePrintCompare()")
            else: await pg.evaluate(f"window.preparePrint('{s}')")
            await pg.wait_for_timeout(2500)
            await pg.pdf(path=f'print/{s}.pdf',prefer_css_page_size=True,print_background=True)
            await pg.evaluate("endPrint()")
        print('errors',errs[:5]); await b.close()
asyncio.run(main())

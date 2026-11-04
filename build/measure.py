import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        await pg.goto('file:///home/claude/build/site/index.html#biotech-beach'); await pg.wait_for_timeout(4000)
        await pg.evaluate("window.preparePrint('biotech-beach')"); await pg.wait_for_timeout(1500)
        await pg.emulate_media(media='print')
        r=await pg.evaluate("""()=>{const o={sw:document.documentElement.scrollWidth,sh:document.documentElement.scrollHeight,bw:document.body.scrollWidth};
          const v=document.querySelector('#v-biotech-beach'); const b=v.getBoundingClientRect(); o.view=[b.width,b.height];
          o.ps=document.querySelector('#v-biotech-beach .psheet').getBoundingClientRect().height; o.ex=document.querySelector('#exw-biotech-beach').getBoundingClientRect().height; o.emap=document.querySelector('#ex-biotech-beach').getBoundingClientRect().height;
          let wide=[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>1600).slice(0,5).map(e=>e.tagName+'.'+e.className+':'+Math.round(e.getBoundingClientRect().right)); o.wide=wide; return o;}""")
        print(r); await b.close()
asyncio.run(main())

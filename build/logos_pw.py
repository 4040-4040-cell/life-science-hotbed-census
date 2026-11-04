import asyncio, json, os, re, sys, io
from PIL import Image
sys.path.insert(0,'/home/claude/build')
from logos import key_of, trim, lightness, LD
META=f'{LD}/meta_pw.json'
meta=json.load(open(META)) if os.path.exists(META) else {}
JS=r'''() => {
  const origin=location.origin.replace(/\/$/,'');
  const isHome=a=>{try{const u=new URL(a.href,location.href);return u.origin===location.origin&&(u.pathname==='/'||u.pathname===''||/^\/(en|us|en-us)\/?$/i.test(u.pathname));}catch(e){return false}};
  const vis=el=>{const r=el.getBoundingClientRect();const s=getComputedStyle(el);return r.width>20&&r.height>10&&r.top<260&&r.bottom>0&&s.visibility!=='hidden'&&s.display!=='none'&&parseFloat(s.opacity)>0.1};
  let cands=[];
  document.querySelectorAll('a').forEach(a=>{ if(!isHome(a))return; a.querySelectorAll('img,svg,picture').forEach(el=>{ if(el.closest('svg')&&el.tagName.toLowerCase()!=='svg'&&el.closest('svg')!==el)return; if(vis(el))cands.push({el,score:3}); }); if(!a.querySelector('img,svg')&&vis(a)&&getComputedStyle(a).backgroundImage!=='none')cands.push({el:a,score:2}); });
  document.querySelectorAll('header img, header svg, [class*=logo] img, [class*=logo] svg, img[alt*=logo i], img[src*=logo i], [class*=logo i]').forEach(el=>{ if(el.tagName.toLowerCase()!=='svg'&&el.closest('svg'))return; if(vis(el))cands.push({el,score:1}); });
  cands=cands.filter(c=>{const r=c.el.getBoundingClientRect();return r.width/r.height>=0.6&&r.width<700;});
  cands.sort((a,b)=>b.score-a.score||a.el.getBoundingClientRect().top-b.el.getBoundingClientRect().top||a.el.getBoundingClientRect().left-b.el.getBoundingClientRect().left);
  if(!cands.length)return null; const el=cands[0].el; el.setAttribute('data-wcls-logo','1');
  let p=el; while(p&&p!==document.documentElement){p.style.setProperty('background','transparent','important');p.style.setProperty('box-shadow','none','important');p.style.setProperty('backdrop-filter','none','important');p=p.parentElement;}
  document.documentElement.style.setProperty('background','transparent','important'); document.body.style.setProperty('background','transparent','important');
  document.body.style.setProperty('visibility','hidden','important'); el.style.setProperty('visibility','visible','important'); el.querySelectorAll('*').forEach(c=>c.style.setProperty('visibility','visible','important'));
  const r=el.getBoundingClientRect(); return {score:cands[0].score,tag:el.tagName,w:r.width,h:r.height,src:el.currentSrc||el.src||''};
}'''
async def one(ctx,company,website,sem):
    k=key_of(company)
    if k in meta and meta[k].get('status') in ('ok','fail_final'): return
    async with sem:
        m={'company':company,'website':website,'status':'fail'}
        pg=await ctx.new_page()
        try:
            await pg.goto(website,timeout=25000,wait_until='domcontentloaded')
            await pg.wait_for_timeout(2500)
            # dismiss cookie banners that may overlay header
            for sel in ['#onetrust-accept-btn-handler','button:has-text("Accept")','button:has-text("I agree")']:
                try:
                    b=pg.locator(sel).first
                    if await b.is_visible(timeout=500): await b.click(timeout=1000); break
                except Exception: pass
            info=await pg.evaluate(JS)
            if info:
                loc=pg.locator('[data-wcls-logo="1"]').first
                await pg.wait_for_timeout(300)
                png=await loc.screenshot(omit_background=True,timeout=8000,scale='device')
                im=trim(Image.open(io.BytesIO(png)).convert('RGBA'))
                op=sum(1 for p in im.resize((80,max(1,int(80*im.height/max(1,im.width))))).getdata() if p[3]>60)
                if im.width>=24 and im.height>=10 and op>=40:
                    h=96; w=int(im.width*h/im.height)
                    if w>420: w=420; h=int(im.height*w/im.width)
                    im=im.resize((w,h),Image.LANCZOS); im.save(f'{LD}/pw/{k}.png')
                    m.update(status='ok',score=info['score'],src=info['src'][:200],light=lightness(im)>215,w=w,h=h,final_url=pg.url)
        except Exception as e: m['err']=str(e)[:150]
        finally: await pg.close()
        meta[k]=m; json.dump(meta,open(META,'w'))
async def run(items,conc=6):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1440,'height':900},device_scale_factor=2,user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',ignore_https_errors=True)
        sem=asyncio.Semaphore(conc)
        await asyncio.gather(*[one(ctx,c,w,sem) for c,w in items if w])
        await b.close()
if __name__=='__main__':
    items=json.load(open(sys.argv[1])) if len(sys.argv)>1 else [('Neurocrine Biosciences','https://www.neurocrine.com'),('Gilead Sciences','https://www.gilead.com'),('Illumina','https://www.illumina.com'),('IDEAYA Biosciences','https://www.ideayabio.com'),('Arcturus Therapeutics','https://arcturusrx.com'),('Moderna','https://www.modernatx.com')]
    pass
    asyncio.run(run(items))
    for c,_ in items: print(meta.get(key_of(c)))

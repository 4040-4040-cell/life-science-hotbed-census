# Ten-point audit of every print page and site view. Run after render.py and print_pdfs.py.
import asyncio, json, re, sys, glob
from playwright.async_api import async_playwright
from pypdf import PdfReader
SL='compare,biotech-beach,biotech-bay,genetown,pharm-country,biocapital,bio-nc,biomidwest,seattle,colorado,uk,basel,basel-city,basel-land'.split(',')
BANNED=['leverage','robust','streamline','holistic','delve','landscape','unlock','navigate','game-changer','it is worth noting',"it's worth noting",'in today','CBRE','—','~']
def strip_b64(t): return re.sub(r'data:image/[a-z+]+;base64,[A-Za-z0-9+/=]+','',t)
async def main():
    report={}
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1100})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        for s in SL:
            R={}
            await pg.goto(f'file:///home/claude/build/site/index.html#{s}'); await pg.wait_for_timeout(4000)
            pages=len(PdfReader(f'print/{s}.pdf').pages)
            R['1 one page']=(pages==1,f'{pages} page(s)')
            if s=='compare':
                txt=await pg.evaluate("document.querySelector('#v-compare').innerText")
                hl=[l for l in txt.split('\n') if 'Tier A' in l][0] if 'Tier A' in txt else ''
                R['2 headline is a finding']=(bool(re.search(r'\d',hl)),hl[:90])
                R['3 plain language']=(all(w.lower() not in txt.lower() for w in BANNED),'banned words absent')
                R['4 scope and date']=('as of' in txt,'as-of present')
                R['5 leaders']=(True,'n/a on cover')
                R['6 no overflow']=(await pg.evaluate("document.documentElement.scrollWidth<=1600"),'width ok')
                rows=await pg.evaluate("[...document.querySelectorAll('table.compare tbody tr')].length")
                R['7 numbers reconcile']=(rows==11,f'{rows} hub rows')
                R['8 logos']=(True,'n/a')
                R['9 no internal text']=(not re.search(r'\.csv|V6|row cap|gco_',txt),'clean')
                R['10 legend and sources']=('inclusion rule' in txt.lower(),'definitions present')
                report[s]=R; continue
            await pg.evaluate(f"window.preparePrint('{s}')"); await pg.wait_for_timeout(2200)
            d=await pg.evaluate(f"""()=>{{const v=document.querySelector('#v-{s}'); const h=v.querySelector('.hrow h2').innerText;
              const calls=[...v.querySelectorAll('.call')].length; const leaders=v.querySelector('svg.leaders').querySelectorAll('polyline').length;
              const tiles=v.querySelectorAll('#ex-{s} img').length; const over=[...v.querySelectorAll('*')].filter(e=>e.getBoundingClientRect().right>1601&&!e.className.toString().includes('leaflet')).length;
              const kp=[...v.querySelectorAll('.pkpis b')].map(e=>e.innerText); const rows=[...v.querySelectorAll('.ptab tbody tr')].map(tr=>[...tr.children].map(td=>td.innerText));
              const logos=[...v.querySelectorAll('.call img')].filter(i=>i.getBoundingClientRect().width>0).map(i=>i.naturalWidth>0&&i.getBoundingClientRect().width>8); const names=[...v.querySelectorAll('.call em')].length;
              const txt=v.innerText; const legend=!!v.querySelector('.plegend'); const foot=v.querySelector('.pfoot')?v.querySelector('.pfoot').innerText:'';
              const small=[...v.querySelectorAll('.psheet *')].filter(e=>e.children.length===0&&e.innerText.trim()&&parseFloat(getComputedStyle(e).fontSize)<11.5).length;
              return {{h,calls,leaders,tiles,over,kp,rows,logos,names,txt,legend,foot,small}};}}""")
            await pg.evaluate("endPrint()")
            R['1 one page']=(pages==1,f'{pages} page(s)')
            R['2 headline is a finding']=(bool(re.search(r'\d+ expansion and \d+ contraction',d['h'])) and ('Largest' in d['h']),d['h'][:110])
            low=d['txt'].lower(); bad=[w for w in BANNED if w.lower() in low]
            R['3 plain language']=(not bad and 'tier a:' in low,f'banned={bad}; tier defined={"tier a:" in low}')
            R['4 scope and date']=('as of' in low and 'imagery' in d['foot'].lower(),'as-of and imagery credit present')
            R['5 leaders']=(d['leaders']==d['calls'] and d['calls']>0,f"{d['leaders']} lines for {d['calls']} callouts")
            R['6 no overflow']=(d['over']==0 and d['small']==0,f"{d['over']} elements past page edge; {d['small']} text nodes under 11.5px")
            hq=sum(int(r[1]) for r in d['rows'] if r and r[1].strip().isdigit()); scored=int(d['kp'][0].replace(',',''))
            R['7 numbers reconcile']=(hq==scored,f'table HQs {hq} vs KPI {scored}')
            R['8 logos']=(all(d['logos']),f"{sum(d['logos'])}/{len(d['logos'])} logos render; {d['names']} typeset names")
            R['9 no internal text']=(not re.search(r'\.csv|\bV6\b|row cap|gco_|check filing|TODO',d['txt']),'clean')
            R['10 legend and map']=(d['legend'] and d['tiles']>0,f"legend={d['legend']}, tiles={d['tiles']}")
            report[s]=R
        await b.close()
    fails=0
    for s,R in report.items():
        bad=[k for k,v in R.items() if not v[0]]; fails+=len(bad)
        print(f"{s}: {10-len(bad)}/10" + (f"  FAIL {bad}" if bad else ""))
        for k,v in R.items():
            if not v[0]: print('    ',k,'->',v[1])
    print('page errors',errs[:5]); print('TOTAL FAILS',fails)
    json.dump({s:{k:list(v) for k,v in R.items()} for s,R in report.items()},open('audit_report.json','w'),indent=1)
asyncio.run(main())

import re, json, os, sys, html as H, datetime as dt
sys.path.insert(0,'/home/claude/build')
from enrich import get, cik_for, UA
import urllib.request, hashlib, time
TD='/home/claude/build/tenk'; os.makedirs(TD,exist_ok=True)
LANDLORDS=['Alexandria Real Estate','Alexandria','BioMed Realty','Healthpeak','Kilroy','IQHQ','Breakthrough Properties','Longfellow','Phase 3','Bulfinch','DivcoWest','Boston Properties','BXP','Tishman Speyer','Hines','Brandywine','Lab Space','Harrison Street','Elevate','Ventas','Wexford','Kayne Anderson','Brookfield','Blackstone','Oxford Properties','King Street Properties','Beacon Capital','Spear Street','SKB','Bristol Group','Lincoln Property','Trammell Crow','Steelwave','Stanford University','Drawbridge','HCP','Prologis','Rubenstein','Patrizia','Bellco','Graphite Bio','MIT','Harvard']
LL_SKIP={'Phase 3','HCP','MIT','Harvard','Graphite Bio','Brookfield','Blackstone','Alexandria','Stanford University'}
def doc_text(url):
    fn=f'{TD}/{hashlib.md5(url.encode()).hexdigest()}.txt'
    if os.path.exists(fn): return open(fn).read()
    for i in range(3):
        try:
            raw=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read().decode('utf-8','ignore'); break
        except Exception: time.sleep(2); raw=''
    time.sleep(0.12)
    t=re.sub(r'(?is)<(script|style).*?</\1>',' ',raw); t=re.sub(r'(?s)<[^>]+>',' ',t); t=H.unescape(t); t=re.sub(r'[\xa0\s]+',' ',t)
    open(fn,'w').write(t); return t
def tenks(cik):
    s=get(f'https://data.sec.gov/submissions/CIK{cik}.json')
    r=s.get('filings',{}).get('recent',{})
    rows=list(zip(r.get('form',[]),r.get('filingDate',[]),r.get('accessionNumber',[]),r.get('primaryDocument',[]),r.get('reportDate',[])))
    k=[x for x in rows if x[0] in ('10-K','10-KT')]
    off=[x for x in rows if x[0] in ('424B4','424B5','424B1','424B3','S-1','F-1') ]
    return s,k,off
def url_of(cik,acc,doc): return f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-","")}/{doc}'
EMP=[r'(?:had|employed|employ|have)\s+(?:a\s+total\s+of\s+)?(?:approximately|about|over|more than)?\s*([\d,]{2,7})\s+(?:full[- ]time|total|regular|employees|people|full time)',
     r'([\d,]{2,7})\s+(?:full[- ]time\s+)?employees']
def employees(t):
    i=t.lower().find('human capital')
    segs=[t[i:i+2500]] if i>=0 else []
    j=t.lower().find(' employees'); 
    if j>=0: segs.append(t[max(0,j-1500):j+1500])
    for seg in segs:
        vals=[]
        for m in re.finditer(r'(?<![\$\d.,])(\d{1,3}(?:,\d{3})+|\d{2,6})(?![\d,]*\s*%)(?=[^.]{0,60}?(?:employee|full[- ]time|people|team members|staff))',seg,flags=re.I):
            v=int(m.group(1).replace(',',''))
            if 1990<=v<=2035 and ',' not in m.group(1): continue
            if 3<=v<=500000: vals.append(v)
        k=re.search(r'(?:full[- ]time\s+)?employees',seg,flags=re.I)
        if k:
            for m in re.finditer(r'(?<![\$\d.,])(\d{1,3}(?:,\d{3})+|\d{2,6})(?![\d,]*\s*%)',seg[k.end():k.end()+250]):
                v=int(m.group(1).replace(',',''))
                if 1990<=v<=2035 and ',' not in m.group(1): continue
                if 3<=v<=500000: vals.append(v)
        if vals: return max(vals)
    return None
def item2(t):
    m=None
    for mm in re.finditer(r'item\s*2\.?\s*[\.:\-–—]?\s*properties',t,flags=re.I): m=mm
    # choose the occurrence with the longest following text before item 3 (skip table of contents)
    best=''
    for mm in re.finditer(r'item\s*2\.?\s*[\.:\-–—]?\s*properties',t,flags=re.I):
        rest=t[mm.end():mm.end()+12000]
        e=re.search(r'item\s*3\.?\s*[\.:\-–—]?\s*legal',rest,flags=re.I)
        seg=rest[:e.start()] if e else rest[:4000]
        if len(seg)>len(best): best=seg
    return best.strip()
def parse_props(seg):
    sf=[int(x.replace(',','')) for x in re.findall(r'([\d,]{4,9})\s*(?:rentable\s+|gross\s+|net\s+rentable\s+)?(?:square\s+feet|sq\.?\s*ft|rsf)',seg,flags=re.I)]
    if re.search(r'square\s+feet|square\s+footage|sq\.?\s*ft',seg[:600],flags=re.I):
        sf=sf+[int(x.replace(',','')) for x in re.findall(r'(?<![\$\d])(\d{1,3}(?:,\d{3})+)(?![\d,]*\s*%)',seg)]
    sf=[x for x in sf if 500<=x<=5_000_000]
    yrs=sorted(set(int(y) for y in re.findall(r'expir\w*[^.]{0,80}?(20[2-4]\d)',seg,flags=re.I) if 2026<=int(y)<=2045))
    if re.search(r'expiration',seg,flags=re.I): yrs=sorted(set(yrs)|set(int(y) for y in re.findall(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(20[2-4]\d)',seg) if 2026<=int(y)<=2045))
    owned=bool(re.search(r'\bwe own\b|\bowned\b',seg,flags=re.I))
    sub=bool(re.search(r'sublease|sub-lease|sublet',seg,flags=re.I))
    return sf,yrs,owned,sub
def landlords(t):
    found=[]
    for L in LANDLORDS:
        if L in LL_SKIP: continue
        if re.search(r'\b'+re.escape(L)+r'\b',t): found.append(L)
    if re.search(r'Alexandria Real Estate|ARE-[A-Z]|ARE[- ]\w+, LLC',t): found.append('Alexandria Real Estate Equities')
    return sorted(set(x for x in found if x!='Alexandria Real Estate'))
def profile(ticker):
    cik=cik_for(ticker)
    if not cik: return {'tk_status':'no cik'}
    s,k,off=tenks(cik)
    out={'cik':cik,'sec_name':s.get('name'),'sec_state':(s.get('addresses',{}).get('business',{}) or {}).get('stateOrCountry'),'sic':s.get('sicDescription')}
    if k:
        f,d,acc,doc,rep=k[0]; u=url_of(cik,acc,doc); t=doc_text(u)
        seg=item2(t)
        if len(seg)<250:
            sents=re.findall(r'[^.]{0,300}(?:square feet|sq\. ft)[^.]{0,200}\.',t,flags=re.I)
            seg=' '.join(sents[:8]); out['props_method']='sentences'
        else: out['props_method']='item2'
        sf,yrs,owned,sub=parse_props(seg)
        out.update(tenk_url=u,tenk_filed=d,tenk_period=rep,emp_now=employees(t),props_sf_max=max(sf) if sf else None,props_sf_sum=sum(sorted(set(sf))) if sf else None,
                   props_n_sf=len(set(sf)),lease_exp_years=yrs,owns_property=owned,sublease_mention=sub,landlords=landlords(seg) if out.get('props_method')=='item2' else [],
                   props_excerpt=re.sub(r'\s+',' ',seg)[:700])
        if len(k)>1:
            f2,d2,acc2,doc2,rep2=k[1]; out['emp_prior']=employees(doc_text(url_of(cik,acc2,doc2))); out['emp_prior_period']=rep2
    cut=(dt.date(2026,10,28)-dt.timedelta(days=365)).isoformat()
    rec=[x for x in off if x[1]>=cut and x[0] in ('424B4','424B5','424B1')]
    out['offerings_12m']=len(rec); out['last_offering_date']=rec[0][1] if rec else None
    ipo=[x for x in off if x[0] in ('S-1','F-1')]
    out['ipo_filed']=ipo[-1][1] if ipo else None
    return out
if __name__=='__main__':
    for tk in sys.argv[1:] or ['NBIX','IDYA','GILD','ILMN','ARCT']:
        p=profile(tk); print(tk,{k:v for k,v in p.items() if k!='props_excerpt'}); print('   ',(p.get('props_excerpt') or '')[:300])

import csv, json, os, sys, re, glob, math, collections
sys.path.insert(0,'/home/claude/build')
from geocode import geocode
from enrich import sec_profile
from enrich import fda_profile, ct_profile
from tenk import profile as tenk_profile
from score import score, num, W
from tiles import fit_zoom, tile_set, fetch, stylize
REG=[('biotech_beach','biotech-beach','Biotech Beach','San Diego, Orange County, Los Angeles, Thousand Oaks'),
     ('biotech_bay','biotech-bay','Biotech Bay','San Francisco Bay Area'),
     ('genetown','genetown','Genetown','Greater Boston and Massachusetts'),
     ('pharm_country','pharm-country','Pharm Country','New Jersey, New York, Pennsylvania and neighbors'),
     ('biocapital','biocapital','BioCapital','Maryland, Washington DC, Virginia'),
     ('bio_nc','bio-nc','Bio NC','North Carolina'),
     ('biomidwest','biomidwest','BioMidwest','Midwest states'),
     ('seattle','seattle','Seattle','Puget Sound, Washington'),
     ('colorado','colorado','Colorado','Boulder, Denver and the Front Range'),
     ('uk','uk','United Kingdom','Cambridge, Oxford, London and major UK sites'),
     ('basel','basel','Basel','Basel trinational area: Switzerland, Alsace and South Baden'),
     ('basel_city','basel-city','Basel-Stadt','Canton Basel-Stadt, building level: city of Basel and Riehen'),
     ('basel_land','basel-land','Basel-Landschaft','Canton Basel-Landschaft, building level: Allschwil, Schweizerhalle, Birs valley, upper Baselbiet')]
DETAIL={'basel_city','basel_land'}
ENR='/home/claude/build/enriched'; os.makedirs(ENR,exist_ok=True)
def enrich_region(key):
    src=f'/home/claude/census/{key}.csv'
    rows=list(csv.DictReader(open(src,newline='',encoding='utf-8-sig')))
    for add in sorted(glob.glob(f'/home/claude/census/{key}_add*.csv'))+[f'/home/claude/census/{key}_formd.csv']+([f'/home/claude/census/{key}_overflow.csv'] if key=='biotech_bay' else []):
        if os.path.exists(add): rows+=list(csv.DictReader(open(add,newline='',encoding='utf-8-sig')))
    web={}
    wf='/home/claude/census/websites_existing.csv'
    if os.path.exists(wf):
        for w in csv.DictReader(open(wf,newline='',encoding='utf-8-sig')):
            if w.get('region_slug')==key and w.get('website'): web[w['company'].strip().lower()]=w['website'].strip()
    EXCLUDE={'raythera','arthrosi'}  # website redirects to Biogen; treated as acquired pending confirmation
    rows=[r for r in rows if (r.get('tests_met') or '').strip() and not any(x in r['company'].lower() for x in EXCLUDE)]
    best={}
    for r in rows:  # dedupe company+city, prefer a row with a street address
        k=(r['company'].strip().lower(),(r.get('city') or '').strip().lower(),(r.get('site_type') or '').strip())
        if k not in best or (not (best[k].get('street') or '').strip() and (r.get('street') or '').strip()): best[k]=r
    rows=list(best.values())
    fpc=collections.defaultdict(list)
    fcf='/home/claude/census/footprint_class.csv'
    if os.path.exists(fcf):
        for x in csv.DictReader(open(fcf,newline='',encoding='utf-8-sig')):
            if x['region_slug']==key: fpc[x['company'].strip().lower()].append(x)
    out=[]
    for i,r in enumerate(rows):
        r={k:(v or '').strip() for k,v in r.items() if k}
        if not r.get('website'): r['website']=web.get(r['company'].lower(),'')
        if (r.get('footprint_event_2025_26') or '').strip() and fpc.get(r['company'].lower()):
            x=fpc[r['company'].lower()].pop(0)
            r.update(fp_dir=int(x['dir']),fp_label=x['label'],fp_sf=x['sf_change'],fp_month=x['event_month'],fp_reason=x['reason'])
        g=dict(r)
        nl=(r.get('notes') or '').lower()
        if 'registered office' in nl and (r.get('country','').upper() not in ('CH','FR','DE') or 'shared registered office' in nl): g['street']=''; g['zip']=''
        lat,lon,prec,dn=geocode(g); r.update(lat=lat,lon=lon,geo_precision=prec,geo_match=dn)
        tk=r.get('ticker','')
        hq_like=r.get('site_type')=='HQ'
        pre=tk.split(':')[0].upper() if ':' in tk else ''
        us_listed= tk and (pre in ('','NASDAQ','NYSE','NYSEAMERICAN','NYSE AMERICAN','AMEX')) and not (r.get('country','').upper() in ('UK','GB','CH','FR','DE') and pre=='')
        if r.get('sec_ticker'): us_listed=True; tk=r['sec_ticker']
        if us_listed:
            sp=sec_profile(tk); r.update({k:v for k,v in sp.items()})
            if hq_like:
                try: r.update({'k_'+k:v for k,v in tenk_profile(tk).items()})
                except Exception as e: r['k_err']=str(e)[:100]
        T8_KEEP=('agilent','pall ','sumitomo','swedish orphan','cheplapharm','shimadzu','organogenesis','caris','monte rosa')
        t8_only=(r.get('tests_met','').strip()=='T8') and not any(r['company'].lower().startswith(k) for k in T8_KEEP)
        if r['category']!='Institution' and not t8_only:  # directory rows: one-word names give false FDA/CT matches, so only distinctive names are matched
            r.update(fda_profile(r['company'])); r.update(ct_profile(r['company']))
        r['ticker_is_local']= bool(tk) and hq_like
        out.append(r)
    json.dump(out,open(f'{ENR}/{key}.json','w'))
    return out
def short(n):
    n=re.sub(r',?\s+(Inc\.?|Incorporated|Corporation|Corp\.?|LLC|Ltd\.?|plc|Co\.)$','',n); return n
if __name__=='__main__':
    keys=sys.argv[1:] or [k for k,*_ in REG]
    for k in keys:
        if os.path.exists(f'/home/claude/census/{k}.csv'):
            o=enrich_region(k); print(k,len(o))

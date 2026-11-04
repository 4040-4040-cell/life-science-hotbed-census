import json, os, sys, re, math, collections, datetime as dt
SPACE=[('radio','Radiation-licensed lab, hot cells, shielded space'),('cell therap','Wet lab plus GMP cleanroom (ISO 7) for cell processing'),('car-t','Wet lab plus GMP cleanroom (ISO 7) for cell processing'),
 ('gene','Wet lab, BSL-2, GMP viral vector suites if manufacturing'),('aav','Wet lab, BSL-2, GMP viral vector suites if manufacturing'),('rna','Wet lab plus GMP formulation and fill'),
 ('antibod','Biology wet lab, vivarium access'),('protein','Biology wet lab, vivarium access'),('biologic','Biology wet lab, vivarium access'),('peptide','Chemistry and biology wet lab'),
 ('small molecule','Chemistry wet lab, high fume hood density'),('vaccine','Wet lab, BSL-2, GMP manufacturing'),('cdmo','GMP manufacturing, cleanroom, warehouse'),
 ('diagnost','Lab plus light manufacturing and assembly'),('tool','Lab plus light manufacturing and assembly'),('instrument','Lab plus light manufacturing and assembly'),
 ('sequenc','Lab plus light manufacturing and assembly'),('ai','Office-heavy, dry lab, small wet lab'),('computational','Office-heavy, dry lab, small wet lab'),('platform','Wet lab, mixed biology and chemistry')]
def implied_space(mod,cat):
    m=(mod or '').lower()
    if cat=='CDMO/CRO': return 'GMP manufacturing, cleanroom, warehouse'
    for k,v in SPACE:
        if re.search(r'\b'+k,m): return v
    return ''
def months_to(d):
    try: d=dt.date.fromisoformat(d if len(d)>=10 else d[:7]+'-15')
    except Exception: return None
    return (d-dt.date(2026,11,2)).days/30.44
INTERNAL=re.compile(r'\.csv|\bV6\b|\bagent\b|row cap|-row cap|-site cap|cap of 2|max-2|\bcap\b|CAP FLAG|SUPERSEDES|SUBSTITUTED|user named|check it|\brows?\b|dedupe|BRIEF|in scope per|per scope|parallel dataset',re.I)
def clean_notes(n):
    # keep source and verification notes for the client view; drop build-process remarks
    if not n: return n
    parts=re.split(r'(?<=[.;])\s+(?=[A-Z(])',n.strip())
    keep=[p for p in parts if not INTERNAL.search(p)]
    return ' '.join(keep).strip() or None
# building-level zones for the Basel canton views: anchor addresses geocoded with the federal register, nearest anchor within its radius
BS_ANCHORS=[('Novartis Campus','Fabrikstrasse 2 4056 Basel',0.45),('Klybeck','Klybeckstrasse 141 4057 Basel',0.45),('Stücki and Kleinhüningen','Hochbergerstrasse 60 4057 Basel',0.55),
  ('Rosental','Mattenstrasse 22 4058 Basel',0.32),('Roche Basel site','Grenzacherstrasse 124 4058 Basel',0.42),('Schällemätteli (university, hospital)','Spitalstrasse 41 4056 Basel',0.42),
  ('City centre','Barfüsserplatz 3 4051 Basel',0.45),('SBB and Peter Merian','Centralbahnstrasse 4 4051 Basel',0.5),('Aeschen and St. Alban','Aeschenplatz 6 4052 Basel',0.45),
  ('Gundeli and Dreispitz','Münchensteinerstrasse 38 4052 Basel',0.6)]
BL_RX=[('Allschwil: Main Campus and Bachgraben',1,r'allschwil|sch.nenbuch'),('Schweizerhalle and Muttenz',1,r'muttenz|schweizerhalle|birsfelden'),('Pratteln and Augst',1,r'pratteln|frenkendorf|f.llinsdorf|^augst| augst'),
  ('Birs valley',1,r'reinach|aesch|arlesheim|m.nchenstein|dornach|pfeffingen'),('Leimental',1,r'binningen|bottmingen|oberwil|therwil|ettingen|biel-benken'),
  ('Upper Baselbiet',1,r'liestal|bubendorf|sissach|lausen|itingen|ziefen|oberdorf|h.lstein|gelterkinden|waldenburg'),('Laufental',0,r'laufen|liesberg|zwingen|grellingen|dittingen')]
_ANC={}
def _anchor(addr):
    if addr not in _ANC:
        from geocode import swiss
        r=swiss(addr); _ANC[addr]=(r[0]['attrs']['lat'],r[0]['attrs']['lon']) if r else None
    return _ANC[addr]
def detail_zone(key,o,r):
    if key=='basel_city':
        if o['lat'] is None: return ('Basel (street not mapped)',False)
        best=None
        for nm,addr,rad in BS_ANCHORS:
            c=_anchor(addr)
            if not c: continue
            d=km((o['lat'],o['lon']),c)
            if d<=rad and (best is None or d<best[1]): best=(nm,d)
        if best: return (best[0],True)
        if re.search(r'riehen|bettingen',(r.get('city') or '').lower()): return ('Riehen',False)
        return ('Basel, other districts',False)
    s=(r.get('city') or '').lower()
    for nm,core,rx in BL_RX:
        if re.search(rx,s): return (nm,bool(core))
    return ((r.get('city') or 'Other'),False)
def read_rule(r,o):
    if o['tier']=='Anchor': return ('Anchor','Institution or incubator')
    if o['tier']=='Site':
        if o['footprint_dir']>0: return ('Expansion candidate','Expansion event 2025 to 2026 at this site')
        if o['footprint_dir']<0: return ('Contraction risk','Contraction event 2025 to 2026 at this site')
        return ('No trigger','No footprint event found at this site in 2025 to 2026; absence of a signal, not confirmed stability')
    rw=r.get('runway_months'); rwn=None if rw in (None,'','CF+') else float(rw)
    emp_chg=o.get('emp_chg')
    fin12=(o.get('last_fin_months') is not None and o['last_fin_months']<=12) or (r.get('k_offerings_12m') or 0)>0
    con=o['footprint_dir']<0 or bool(r.get('k_sublease_mention') and o['footprint_dir']<=0 and False)
    if (rwn is not None and rwn<12) or o['footprint_dir']<0 or (emp_chg is not None and emp_chg<=-10):
        why=[]
        if rwn is not None and rwn<12: why.append(f'{rwn:.0f} months of cash')
        if o['footprint_dir']<0: why.append('contraction event 2025 to 2026')
        if emp_chg is not None and emp_chg<=-10: why.append(f'headcount {emp_chg:+.0f}%')
        return ('Contraction risk','; '.join(why))
    if o['tier'] in ('A','B') and (fin12 or (emp_chg is not None and emp_chg>=10) or o['footprint_dir']>0) and (rw=='CF+' or (rwn is not None and rwn>=24) or (r.get('ticker')=='' and fin12)):
        why=[]
        if fin12: why.append('raised capital in last 12 months')
        if emp_chg is not None and emp_chg>=10: why.append(f'headcount {emp_chg:+.0f}%')
        if o['footprint_dir']>0: why.append('expansion event 2025 to 2026')
        return ('Expansion candidate','; '.join(why))
    nr=months_to(r.get('next_readout') or '')
    if nr is not None and 0<=nr<=12: return ('Watch',f"Phase 2/3 readout expected {r.get('next_readout')}")
    return ('No trigger','No footprint, capital, headcount or readout trigger found in the data; absence of a signal, not confirmed stability')
sys.path.insert(0,'/home/claude/build')
from build import REG, short, DETAIL
from score import score, num, W
from tiles import fit_zoom, tile_set, fetch, stylize
from logos import key_of
from zones_map import zone_of
ENR='/home/claude/build/enriched'
BBOX={ # sanity bounds per region (lat_min, lat_max, lon_min, lon_max)
 'biotech_beach':(32.5,34.9,-120.1,-116.0),'biotech_bay':(36.9,38.6,-123.2,-121.4),'genetown':(41.2,42.95,-73.6,-69.8),
 'pharm_country':(38.9,45.1,-80.6,-71.0),'biocapital':(36.5,40.0,-83.8,-74.9),'bio_nc':(33.8,36.7,-84.4,-75.4),'biomidwest':(36.0,49.5,-104.1,-80.4),
 'seattle':(45.5,49.0,-124.8,-116.9),'colorado':(37.0,41.0,-109.1,-102.0),'uk':(49.8,59.5,-8.2,1.9),'basel':(47.25,47.80,7.15,8.15),'basel_city':(47.50,47.62,7.53,7.72),'basel_land':(47.33,47.60,7.38,7.95)}
SUBSIDIARY={'calico life sciences':'Alphabet','cepheid (danaher)':'Danaher','molecular devices (danaher)':'Danaher','beckman coulter (danaher) brea':'Danaher',
            'kite pharma (gilead) headquarters':'Gilead Sciences','biolegend (revvity)':'Revvity'}  # verified against SEC registrant names, Oct 28 2026
def build(max_tiles_region=900):
    regions=[];tiles={};zmin={};zmax={};compare=[];allrows=[]
    for key,slug,name,geo in [x for x in REG if not os.environ.get('ONLY') or x[0] in os.environ['ONLY'].split(',')]:
        fn=f'{ENR}/{key}.json'
        if not os.path.exists(fn): continue
        rows=json.load(open(fn)); out=[]
        # Form D addresses that do not locate an operating site: mailbox or virtual addresses, and one office suite shared by 3+ Form D filers (a VC office)
        def nst(s): return re.sub(r'[^a-z0-9 ]','',(s or '').lower().replace('street','st'))
        share=collections.Counter(nst(r.get('street'))+'|'+(r.get('city') or '').lower() for r in rows if 'T7' in (r.get('tests_met') or '') and r.get('street'))
        for r in rows:
            if 'T7' not in (r.get('tests_met') or ''): continue
            s=(r.get('street') or '').lower()
            if re.search(r'\bpmb\b|\bapt\b|attn:|p\.?o\.? box|ste 14011|registered agent|c/o ',s) or share[nst(r.get('street'))+'|'+(r.get('city') or '').lower()]>=3 and re.search(r'floor|fl\b|suite|ste\b',s):
                r['address_unlocated']=True; r['submarket']=''; r['lat']=r['lon']=None; r['geo_precision']='none'
        # submarket for rows that have none (Form D additions): majority of the 3 nearest labeled sites within 4 km
        lab=[(r['lat'],r['lon'],r['submarket']) for r in rows if r.get('submarket') and r.get('lat') is not None and r.get('geo_precision')=='street']
        for r in rows:
            if (r.get('submarket') or '').strip() or r.get('lat') is None: continue
            if r.get('address_unlocated'): continue
            if r.get('geo_precision')!='street': r['submarket_unmapped']=True; continue
            d=sorted((math.hypot((r['lat']-la)*111,(r['lon']-lo)*111*math.cos(math.radians(la))),sm) for la,lo,sm in lab)[:3]
            near=[sm for dd,sm in d if dd<=1.5]
            if near: r['submarket']=collections.Counter(near).most_common(1)[0][0]; r['submarket_inferred']=True
        seen=set()
        for i,r in enumerate(rows):
            k=(r['company'].lower(),r.get('street','').lower()[:20],r.get('city','').lower())
            if k in seen: continue
            seen.add(k)
            par=SUBSIDIARY.get(r['company'].strip().lower())
            if par:
                r['subsidiary_of']=par; r['ticker_is_local']=False
                for k_ in [k_ for k_ in list(r) if k_.startswith('k_')]+['liquidity_usd_m','op_cash_flow_fy_usd_m','revenue_fy_usd_m','runway_months','public_float_usd_m']: r.pop(k_,None)
            s=score(r); r.update(s)
            la,lo=r.get('lat'),r.get('lon'); b=BBOX[key]
            if la is not None and not (b[0]<=la<=b[1] and b[2]<=lo<=b[3]) and r.get('zip'):
                from geocode import q as _gq
                cc={'UK':'gb','GB':'gb','CH':'ch','FR':'fr','DE':'de'}.get((r.get('country') or '').upper(),'us')
                g=_gq({'postalcode':r['zip'].split('-')[0]},cc)
                if g:
                    la2,lo2=float(g[0]['lat']),float(g[0]['lon'])
                    if b[0]<=la2<=b[1] and b[2]<=lo2<=b[3]: r['lat'],r['lon'],r['geo_precision']=la2,lo2,'zip'; la,lo=la2,lo2
            if la is not None and not (b[0]<=la<=b[1] and b[2]<=lo<=b[3]): r['geo_flag']='outside region bounds'; r['lat']=r['lon']=None
            emp=num(r.get('employees')) or num(r.get('sec_employees'))
            pf=num(r.get('public_float_usd_m')); pr=num(r.get('private_raised_total_usd_m'))
            if r.get('ticker') and pf is not None: cap,ck=pf,'float'
            elif pr is not None: cap,ck=pr,'raised'
            elif num(r.get('last_round_usd_m')) is not None: cap,ck=num(r.get('last_round_usd_m')),'last round'
            else: cap,ck=None,''
            if r['site_type']!='HQ' and r.get('category') in ('Big Pharma','Tools & Diagnostics','CDMO/CRO') and not r.get('ticker_is_local'): cap,ck=None,'parent'
            rw=r.get('runway_months')
            out.append({'id':f'{slug}-{i}','company':r['company'],'short':short(r['company']),'ticker':r.get('ticker',''),'category':r['category'],
              'site_type':r['site_type'],'street':r.get('street',''),'city':r.get('city',''),'state':r.get('state',''),'submarket':r.get('submarket','') or 'Unassigned',
              'modality':r.get('modality',''),'emp':emp,'cap':cap,'cap_kind':ck,'runway_disp':('Cash-flow positive' if rw=='CF+' else ('120+' if (num(rw) or 0)>120 else (f'{num(rw):.0f}' if num(rw) is not None else ''))),
              'runway_sort':999 if rw=='CF+' else num(rw),'stage_label':s.get('stage_label',''),'fda':int(num(r.get('fda_nda_bla')) or 0) or None,'fda_brands':r.get('fda_brands',''),
              'footprint':r.get('fp_label') or r.get('footprint_event_2025_26',''),'footprint_full':r.get('footprint_event_2025_26',''),'footprint_dir':s.get('footprint_dir',0),'tests_met':r.get('tests_met',''),
              'tier':s['tier'],'tier_rank':{'A':0,'B':1,'C':2,'Site':3,'Anchor':4}[s['tier']],'score':s.get('score'),'low_cov':(s.get('score_coverage') or 1)<0.6,
              'lat':r.get('lat'),'lon':r.get('lon'),'geo_precision':r.get('geo_precision'),'source_url':r.get('source_url',''),
              '_slug':slug,'web':'' if r['company'].lower().startswith('indupro') else r.get('website',''),'logo':key_of(r['company'])})
            o=out[-1]
            o['zone'],o['core']=zone_of(key,r.get('submarket',''),r.get('city',''),r.get('state',''))
            if key in DETAIL: o['zone'],o['core']=detail_zone(key,o,r); o['campus']=r.get('campus','')
            if r.get('address_unlocated'):
                o['zone']='Filing address is a mailbox or shared VC office'; o['core']=False; o['submarket']=o['zone']
            elif r.get('submarket_unmapped') or (not (r.get('submarket') or '').strip() and r.get('geo_precision')!='street'):
                o['zone']=f"{(r.get('city') or 'Unknown').title()} (street not mapped)"; o['core']=False; o['submarket']=o['zone']
            en=num(r.get('k_emp_now')); ep=num(r.get('k_emp_prior'))
            if en and ep and (en/ep>5 or en/ep<0.15): en=None  # parse sanity: implausible year-over-year jump
            if en and not o['emp']: o['emp']=en
            o['emp_chg']=round((en-ep)/ep*100,1) if en and ep else None
            from score import months_since
            m=months_since(r.get('last_round_date')); lo=r.get('k_last_offering_date')
            m2=months_since(lo) if lo else None
            o['last_fin_months']=min([x for x in (m,m2) if x is not None],default=None)
            o['p']={k:v for k,v in {
              'emp_now':en,'emp_prior':ep,'emp_period':r.get('k_tenk_period'),'emp_src':'10-K' if en else (r.get('employees_source') or ''),
              'sf_max':r.get('k_props_sf_max'),'sf_sum':r.get('k_props_sf_sum'),'lease_exp':r.get('k_lease_exp_years'),'owns':r.get('k_owns_property'),
              'sublease':r.get('k_sublease_mention'),'landlords':r.get('k_landlords'),'props':r.get('k_props_excerpt'),'tenk':r.get('k_tenk_url'),'tenk_filed':r.get('k_tenk_filed'),
              'liq':r.get('liquidity_usd_m'),'liq_asof':r.get('liquidity_asof'),'ocf':r.get('op_cash_flow_fy_usd_m'),'ocf_end':r.get('ocf_fy_end'),'rev':r.get('revenue_fy_usd_m'),'rev_end':r.get('revenue_fy_end'),
              'float':r.get('public_float_usd_m'),'float_asof':r.get('public_float_asof'),'raised':r.get('private_raised_total_usd_m'),'last_round':r.get('last_round_usd_m'),'last_round_date':r.get('last_round_date'),
              'last_round_type':r.get('last_round_type'),'fund_src':r.get('funding_source_url'),'off12':r.get('k_offerings_12m'),'last_off':lo,
              'brands':r.get('fda_brands'),'latest_appr':r.get('fda_latest_approval'),'phase':r.get('ct_max_phase'),'n_trials':r.get('ct_active'),
              'next':r.get('next_readout'),'next_ph':r.get('next_readout_phase'),'next_nct':r.get('next_readout_nct'),'next_cond':r.get('next_readout_condition'),
              'fp_src':r.get('footprint_source_url'),'verified':r.get('verified'),'notes':clean_notes(r.get('notes')),'space':implied_space(r.get('modality'),r.get('category')),
              'cov':s.get('score_coverage'),'parts':[s.get('s_scale'),s.get('s_capital'),s.get('s_durability'),s.get('s_stage'),s.get('s_momentum')]}.items() if v not in (None,'',[],False)}
            o['read'],o['read_why']=read_rule(r,o)
            allrows.append({**r,'region_name':name,'tier':s['tier'],'score':s.get('score')})
        pts=[(o['lat'],o['lon']) for o in out if o['lat'] is not None]
        zf=fit_zoom([p[0] for p in pts],[p[1] for p in pts],w=900,h=600)
        zx=min(zf+5,16 if key in DETAIL else 15); radius=(420 if key=='basel_city' else 300) if key in DETAIL else 220; cap=(1100 if key=='basel_city' else 720) if key in DETAIL else max_tiles_region
        while True:
            ts=tile_set(pts,zf,zmax=zx,radius_px=radius)
            if len(ts)<=cap or zx<=zf+2: break
            if radius>150: radius-=40
            else: zx-=1
        print(name,'rows',len(out),'zfit',zf,'zmax',zx,'tiles',len(ts),flush=True)
        T={}
        for (z,x,y) in sorted(ts):
            f=fetch(z,x,y)
            if f: T[f'{z}/{x}/{y}']=stylize(f)
        tiles[slug]=T; zmin[slug]=max(zf-1,3); zmax[slug]=zx
        sc=[o for o in out if o['tier'] not in ('Anchor','Site')]
        subs=collections.Counter(o['zone'] for o in sc)
        za=collections.Counter(o['zone'] for o in sc if o['tier']=='A')
        cnt=collections.Counter(o['tier'] for o in out)
        topA=sorted([o for o in sc if o['tier']=='A'],key=lambda o:-(o['score'] or 0))
        sub1,n1=subs.most_common(1)[0]
        headline=f"{name}: {len(sc)} headquartered companies scored, {cnt['A']} in Tier A, plus {cnt['Site']} major sites of outside companies; {sub1} has the most company headquarters, {n1}"
        regions.append({'slug':slug,'name':name,'geo':geo,'headline':headline,'rows':out})
        regions[-1]['campuses']=load_campuses(key) if key in DETAIL else []
        if key in DETAIL: continue
        compare.append({'slug':slug,'name':name,'geo':geo,'n':len(sc),'A':cnt['A'],'B':cnt['B'],'C':cnt['C'],
            'pub':sum(1 for o in sc if o['ticker'] and o['site_type']=='HQ'),
            'liq':None if key in ('uk','basel') else round(sum(num(r.get('liquidity_usd_m')) or 0 for r in rows if r.get('ticker') and r.get('site_type')=='HQ' and not r.get('subsidiary_of'))),
            'raised':round(sum(o['cap'] or 0 for o in sc if o['cap_kind'] in ('raised','last round'))),'sites':cnt['Site'],
            'comm':sum(1 for o in sc if o['stage_label'].startswith('Commercial')),
            'exp':sum(1 for o in out if o['footprint_dir']>0),'con':sum(1 for o in out if o['footprint_dir']<0),'top_sub':f'{sub1} ({n1})'})
    return regions,tiles,zmin,zmax,compare,allrows

def load_campuses(key):
    import csv as _csv
    fn={'basel_city':'/home/claude/census/basel_campus_bs.csv','basel_land':'/home/claude/census/basel_campus_bl.csv'}[key]
    if not os.path.exists(fn): return []
    from geocode import geocode
    out=[]
    for c in _csv.DictReader(open(fn,newline='',encoding='utf-8-sig')):
        g={'street':c.get('street',''),'city':c.get('city',''),'state':'','zip':c.get('zip',''),'country':'CH'}
        la,lo,prec,_=geocode(g) if (g['street'] or g['city']) else (None,None,'none','')
        st=(c.get('status') or '').lower()
        ns=('vacating' if 'vacating' in st else 'for lease' if re.search(r'for lease|vacant|marketed',st) else 'under construction' if re.search(r'construction|expanding|partly',st)
            else 'planned' if re.search(r'planned|development|funded',st) else 'operating')
        c=dict(c); c['status_raw']=c.get('status',''); c['status']=ns
        out.append({k:(c.get(k) or '').strip() for k in ('status_raw',)}|{k:(c.get(k) or '').strip() for k in ('campus','building','street','zip','city','owner_developer','use_type','status','year_delivered_or_due','size_m2','size_basis','lab_share_or_note','anchor_tenants','other_tenants','available_m2','availability_note','footprint_event_2025_26','source_url','notes')}|{'lat':la,'lon':lo,'prec':prec})
    return out
ZONE_COLORS=['#8E6C8A','#C9636F','#5E9BB0','#E8B07A','#7FB59B','#9A8F84','#6E7FA8','#B58B5A']
def hull(pts):
    pts=sorted(set(pts))
    if len(pts)<3: return pts
    def cr(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
def elsewhere(rows):
    c=collections.Counter(o['zone'] for o in rows if not o['core'] and o['tier']!='Anchor')
    for nm,n in getattr(zones,'dropped',[]): c[nm]=c.get(nm,0)+n
    return [{'name':k,'n':v} for k,v in c.most_common() if v>0]
FOCUS_KM={'biotech_beach':14,'biotech_bay':55,'genetown':22,'pharm_country':160,'biocapital':70,'bio_nc':40,'biomidwest':1500,'seattle':30,'colorado':45,'uk':110,'basel':30,'basel_city':6,'basel_land':28}
def km(a,b): return math.hypot((a[0]-b[0])*111,(a[1]-b[1])*111*math.cos(math.radians(a[0])))
def zones(rows,maxz=8,maxco=8,region=None):
    by=collections.defaultdict(list)
    for o in rows:
        if o['core']: by[o['zone']].append(o)
    ranked=sorted(by.items(),key=lambda kv:(-len([o for o in kv[1] if o['tier']!='Anchor']),-sum(o['score'] or 0 for o in kv[1])))
    def cen(os_):
        P=[(o['lat'],o['lon']) for o in os_ if o['lat'] is not None]
        return (sorted(p[0] for p in P)[len(P)//2],sorted(p[1] for p in P)[len(P)//2]) if P else None
    c0=cen(ranked[0][1]) if ranked else None
    R_=FOCUS_KM.get(region,1e9); dropped=[]
    keep=[]
    ranked=[(nm,os_) for nm,os_ in ranked if any(o['tier']!='Anchor' for o in os_)]
    c0=cen(ranked[0][1]) if ranked else None
    for nm,os_ in ranked:
        c=cen(os_)
        if c and c0 and km(c,c0)<=R_: keep.append((nm,os_))
        else: dropped.append((nm,len([o for o in os_ if o['tier']!='Anchor'])))
    ranked=keep[:maxz]; dropped+= [(nm,len([o for o in os_ if o['tier']!='Anchor'])) for nm,os_ in keep[maxz:]]
    zones.dropped=dropped
    out=[]
    for i,(name,os_) in enumerate(ranked):
        P=[(o['lat'],o['lon']) for o in os_ if o['lat'] is not None and o.get('geo_precision')=='street'] or [(o['lat'],o['lon']) for o in os_ if o['lat'] is not None]
        if not P: continue
        # drop far outliers (> 3x median distance from median point)
        mla=sorted(p[0] for p in P)[len(P)//2]; mlo=sorted(p[1] for p in P)[len(P)//2]
        d=[math.hypot(p[0]-mla,(p[1]-mlo)*math.cos(math.radians(mla))) for p in P]; md=sorted(d)[len(d)//2] or 0.01
        P=[p for p,dd in zip(P,d) if dd<=max(2.2*md,0.02)]
        h=hull(P)
        cla=sum(p[0] for p in P)/len(P); clo=sum(p[1] for p in P)/len(P)
        cos_=sorted([o for o in os_ if o['tier']!='Anchor'],key=lambda o:({'A':0,'Site':1,'B':2,'C':3}[o['tier']],-(o['score'] or 0)))
        anchors=[o for o in os_ if o['tier']=='Anchor']
        out.append({'name':name,'n':len([o for o in os_ if o['tier']!='Anchor']),'color':ZONE_COLORS[i%8],'hull':h,'c':[cla,clo],
                    'cos':[{'id':o['id'],'n':o['short'],'t':o['tier']} for o in cos_[:maxco]],'more':max(0,len(cos_)-maxco),
                    'anchors':[o['short'] for o in anchors][:3]})
    return out

def snapshots(rows):
    by=collections.defaultdict(list)
    for o in rows: by[o['zone']].append(o)
    out=[]
    for z,os_ in by.items():
        sc=[o for o in os_ if o['tier'] in ('A','B','C')]
        if not sc and not any(o['tier']=='Site' for o in os_): continue
        t=collections.Counter(o['tier'] for o in os_)
        pubs=[o for o in sc if o['ticker'] and o['site_type']=='HQ']
        cash=sum((o['p'].get('liq') or 0) for o in pubs)
        priv=sum((o['cap'] or 0) for o in sc if o['cap_kind'] in ('raised','last round'))
        exp=[(o['short'],o['footprint']) for o in os_ if o['footprint_dir']>0]
        con=[(o['short'],o['footprint']) for o in os_ if o['footprint_dir']<0]
        lease=sorted([(min(o['p']['lease_exp']),o['short']) for o in sc if o['p'].get('lease_exp') and min(o['p']['lease_exp'])<=2028])
        ll=collections.Counter(l for o in os_ for l in (o['p'].get('landlords') or []))
        rd=sorted([(o['p']['next'],o['short'],o['p'].get('next_ph','')) for o in sc if o['p'].get('next') and '2026-10'<=o['p']['next'][:7]<='2027-10'])
        mod=collections.Counter((o['modality'] or '').split('(')[0].split(';')[0].split(',')[0].strip().lower() for o in sc if o['modality'])
        fin12=sum(1 for o in sc if o.get('last_fin_months') is not None and o['last_fin_months']<=12)
        sf=sum(int(o['p']['sf_max']) for o in sc if o['p'].get('sf_max'))
        reads=collections.Counter(o['read'] for o in os_)
        top=[o['short'] for o in sorted(sc,key=lambda o:-(o['score'] or 0))[:6]]
        OFF=r'financial district|back bay|downtown|manhattan|midtown|center city|washington dc|cbd|west end|holborn|city/farringdon|paddington|westminster|canary'
        office=sum(1 for o in sc if re.search(OFF,(o.get('submarket') or '').lower()))
        n=len(sc)
        sent=(f"{n} headquartered {'company' if n==1 else 'companies'} ({t['A']} Tier A)"+(f" and {t['Site']} major outside {'site' if t['Site']==1 else 'sites'}" if t['Site'] else '')
              +f"; {len(exp)} expansion and {len(con)} contraction events in 2025 to 2026"
              +(f"; {len(lease)} name lease expiries in 2026 to 2028" if lease else '')
              +(f"; {len(rd)} Phase 2/3 readouts due by October 2027" if rd else '')+'.'
              +(f" {office} of the {n} list an office-district address, so their lab space may sit in another submarket." if office>=3 else ''))
        out.append({'zone':z,'core':os_[0]['core'],'n':n,'A':t['A'],'B':t['B'],'C':t['C'],'sites':t['Site'],'anchors':t['Anchor'],'pub':len(pubs),'priv':n-len(pubs),
            'cash':round(cash),'raised':round(priv),'comm':sum(1 for o in sc if o['stage_label'].startswith('Commercial')),'ph3':sum(1 for o in sc if o['stage_label']=='Phase 3'),
            'fin12':fin12,'sf10k':sf,'exp':exp[:8],'con':con[:8],'lease':lease[:10],'landlords':ll.most_common(5),'readouts':rd[:10],'modality':mod.most_common(4),
            'reads':{'exp':reads['Expansion candidate'],'con':reads['Contraction risk'],'watch':reads['Watch']},'top':top,'sentence':sent,'office':office})
    out.sort(key=lambda s:(not s['core'],-s['n']))
    return out

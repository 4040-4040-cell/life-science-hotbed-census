# Deterministic scoring. Weights and bands are analyst assumptions (labeled as such in the page).
import datetime as dt
ASOF=dt.date(2026,10,28)
W={'scale':0.25,'capital':0.20,'durability':0.20,'stage':0.20,'momentum':0.15}
def num(v):
    try: return float(str(v).replace(',','').replace('$',''))
    except: return None
def band(v,cuts):  # cuts ascending -> score 1..len(cuts)+1
    if v is None: return None
    return 1+sum(v>=c for c in cuts)
def months_since(d):
    try: d=dt.date.fromisoformat(str(d)[:10] if len(str(d))>=10 else str(d)[:7]+'-01')
    except: return None
    return (ASOF-d).days/30.44
EXP=('lease','expan','new plant','new site','new facility','opened','open ','groundbreak','construct','acquired building','purchase','headquarters move','relocat')
CON=('layoff','closure','closing','close ','sublease','consolidat','shutter','downsiz','wind','reduction','vacat','exit')
def footprint_dir(t):
    t=(t or '').lower()
    if not t.strip(): return 0
    c=any(k in t for k in CON); e=any(k in t for k in EXP)
    return -1 if c and not ('expan' in t or 'new plant' in t) else (1 if e else 0)
def score(r):
    cat=r['category']; out={}
    fd0=r['fp_dir'] if r.get('fp_dir') is not None else footprint_dir(r.get('footprint_event_2025_26'))
    if cat=='Institution': return {'tier':'Anchor','score':None,'s_scale':None,'s_capital':None,'s_durability':None,'s_stage':None,'s_momentum':None,'stage_label':'','footprint_dir':fd0}
    parent_site=(r['site_type'] in ('R&D','Manufacturing','Campus') and cat in ('Big Pharma','Tools & Diagnostics','CDMO/CRO') and not r.get('ticker_is_local')) or bool(r.get('subsidiary_of'))
    if parent_site: return {'tier':'Site','score':None,'s_scale':None,'s_capital':None,'s_durability':None,'s_stage':None,'s_momentum':None,'stage_label':'Site of a larger company','footprint_dir':fd0}
    emp=num(r.get('employees')) or num(r.get('sec_employees'))
    rev=num(r.get('revenue_fy_usd_m'))
    s_scale=band(emp,[50,200,500,2000])
    if s_scale is None and rev is not None: s_scale=band(rev,[10,100,500,2000])
    if s_scale is None and parent_site: s_scale=3
    liq=num(r.get('liquidity_usd_m')); raised=num(r.get('private_raised_total_usd_m'))
    pf=num(r.get('public_float_usd_m'))
    if r.get('ticker'): s_cap=band(pf,[250,1000,3000,10000]) if pf is not None else band(liq,[50,150,400,1000])
    else: s_cap=band(raised if raised is not None else num(r.get('last_round_usd_m')),[100,200,400,800])
    if parent_site: s_cap=5
    rw=r.get('runway_months')
    if rw=='CF+' or parent_site: s_dur=5
    elif num(rw) is not None: s_dur=band(num(rw),[12,24,36,60])
    else:
        m=months_since(r.get('last_round_date'))
        s_dur=None if m is None else (4 if m<=12 else 3 if m<=24 else 2)
    dev=cat=='Tools & Diagnostics' and ((num(r.get('fda_pma')) or 0)>0 or (num(r.get('fda_510k')) or 0)>0)
    approved=(num(r.get('fda_nda_bla')) or 0)>0 or dev
    ph=num(r.get('ct_max_phase')) or 0
    commercial= approved or 'T4' in (r.get('tests_met') or '') or (cat!='Biopharma' and (rev or 0)>=50)
    if commercial: s_stage,lab=5,'Commercial'
    elif cat in ('CDMO/CRO','Tools & Diagnostics') : s_stage,lab=(4,'Revenue') if (rev or 0)>0 else (2,'Development')
    elif ph>=3: s_stage,lab=4,'Phase 3'
    elif ph>=2: s_stage,lab=3,'Phase 2'
    elif ph>=0.5: s_stage,lab=2,'Phase 1'
    else: s_stage,lab=1,'Preclinical / undisclosed'
    if parent_site and s_stage<5: s_stage,lab=5,'Commercial (parent)'
    mom=2.5
    fd=r['fp_dir'] if r.get('fp_dir') is not None else footprint_dir(r.get('footprint_event_2025_26'))
    mom+= 1.5*fd
    m=months_since(r.get('last_round_date'))
    if m is not None and m<=12: mom+=1
    la=months_since(r.get('fda_latest_approval'))
    if la is not None and la<=24: mom+=1
    s_mom=max(0,min(5,mom))
    parts={'scale':s_scale,'capital':s_cap,'durability':s_dur,'stage':s_stage,'momentum':s_mom}
    have={k:v for k,v in parts.items() if v is not None}
    wsum=sum(W[k] for k in have)
    sc=round(sum(W[k]*v for k,v in have.items())/wsum,2) if wsum else None
    coverage=round(wsum,2)
    tier='A' if sc is not None and sc>=3.8 else 'B' if sc is not None and sc>=2.6 else 'C'
    return {'tier':tier,'score':sc,'score_coverage':coverage,'footprint_dir':fd,'stage_label':lab,
            **{'s_'+k:v for k,v in parts.items()}}

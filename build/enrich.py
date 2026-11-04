import json, os, re, time, urllib.parse, urllib.request, datetime as dt
UA={'User-Agent':os.environ.get('WCLS_UA','WCLS research chad.urie@urieinvestments.com')}
CD='/home/claude/build/apicache'; os.makedirs(CD,exist_ok=True)
def get(url, pause=0.15):
    import hashlib; fn=os.path.join(CD,('sec_' if 'sec.gov' in url else 'x_')+hashlib.md5(url.encode()).hexdigest()+'.json')
    if os.path.exists(fn): return json.load(open(fn))
    data=None
    for i in range(3):
        try:
            data=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30)); break
        except urllib.error.HTTPError as e:
            if e.code==404: data={}; break
            time.sleep(2)
        except Exception: time.sleep(2)
    time.sleep(pause)
    if data is not None: json.dump(data,open(fn,'w'))
    return data or {}
_t=None
def cik_for(ticker):
    global _t
    if _t is None:
        d=get('https://www.sec.gov/files/company_tickers.json')
        _t={v['ticker'].upper():str(v['cik_str']).zfill(10) for v in d.values()}
    return _t.get((ticker or '').upper().split(':')[-1].strip())
def _facts(cik): return get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json')
def _series(f,tags,units='USD'):
    for tag in tags:
        for ns in ('us-gaap','dei','ifrs-full'):
            u=f.get('facts',{}).get(ns,{}).get(tag,{}).get('units',{}).get(units)
            if u: return tag,u
    return None,[]
def latest_instant(f,tags):
    u=_all(f,tags)
    u=[x for x in u if x.get('form') in ('10-K','10-Q','20-F','10-K/A','10-Q/A')]
    if not u: return None,None
    x=max(u,key=lambda x:(x['end'],x.get('filed','')));return x['val'],x['end']
def _all(f,tags,units='USD'):
    out=[]
    for tag in tags:
        for ns in ('us-gaap','dei','ifrs-full'):
            out+=f.get('facts',{}).get(ns,{}).get(tag,{}).get('units',{}).get(units,[])
    return out
def latest_annual(f,tags):
    u=_all(f,tags)
    best=None
    for x in u:
        if 'start' not in x: continue
        d=(dt.date.fromisoformat(x['end'])-dt.date.fromisoformat(x['start'])).days
        if 350<=d<=380 and x.get('form','').startswith(('10-K','20-F')):
            if best is None or (x['end'],x.get('filed',''))>(best['end'],best.get('filed','')): best=x
    return (best['val'],best['end']) if best else (None,None)
def sec_profile(ticker):
    cik=cik_for(ticker)
    if not cik: return {'sec_status':'ticker not found'}
    f=_facts(cik)
    if not f: return {'cik':cik,'sec_status':'no xbrl'}
    def inst(tags):
        out={}
        for t in tags:
            for ns in ('us-gaap','ifrs-full'):
                for x in f.get('facts',{}).get(ns,{}).get(t,{}).get('units',{}).get('USD',[]):
                    if 'start' in x or x.get('form') not in ('10-K','10-Q','20-F','10-K/A','10-Q/A','6-K'): continue
                    out.setdefault(t,{})[x['end']]=x['val']
        return out
    CASH=['CashAndCashEquivalentsAtCarryingValue','CashAndCashEquivalents','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents','Cash']
    COMB=['CashCashEquivalentsAndShortTermInvestments']
    CUR=['ShortTermInvestments','MarketableSecuritiesCurrent','AvailableForSaleSecuritiesDebtSecuritiesCurrent','DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent','HeldToMaturitySecuritiesCurrent','DebtSecuritiesHeldToMaturityExcludingAccruedInterestAfterAllowanceForCreditLossCurrent']
    NON=['MarketableSecuritiesNoncurrent','AvailableForSaleSecuritiesDebtSecuritiesNoncurrent','DebtSecuritiesAvailableForSaleExcludingAccruedInterestNoncurrent','LongTermInvestments','HeldToMaturitySecuritiesNoncurrent']
    ic=inst(CASH+COMB+CUR+NON)
    dates=sorted({d for t in CASH+COMB for d in ic.get(t,{})})
    liq=None; ce=None
    if dates:
        ce=dates[-1]
        first=lambda tags:next((ic[t][ce] for t in tags if ce in ic.get(t,{})),None)
        comb=first(COMB)
        if comb is not None: liq=comb
        else: liq=(first(CASH) or 0)+(first(CUR) or 0)
        liq+= (first(NON) or 0)
    ocf,oe=latest_annual(f,['NetCashProvidedByUsedInOperatingActivities','CashFlowsFromUsedInOperatingActivities'])
    rev,re_=latest_annual(f,['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','RevenueFromContractWithCustomerIncludingAssessedTax','Revenue'])
    tag,u=_series(f,['EntityPublicFloat'])
    pf=max(u,key=lambda x:x['end']) if u else None
    emp=None
    tag,ue=_series(f,['EntityNumberOfEmployees'],'pure')
    if ue: x=max(ue,key=lambda x:x['end']); emp=(x['val'],x['end'])
    runway=None
    if liq is not None and ocf is not None:
        runway='CF+' if ocf>=0 else round(liq/(-ocf/12),1)
    return {'cik':cik,'sec_status':'ok','liquidity_usd_m':round(liq/1e6,1) if liq is not None else None,'liquidity_asof':ce,
            'op_cash_flow_fy_usd_m':round(ocf/1e6,1) if ocf is not None else None,'ocf_fy_end':oe,
            'revenue_fy_usd_m':round(rev/1e6,1) if rev is not None else None,'revenue_fy_end':re_,
            'runway_months':runway,'public_float_usd_m':round(pf['val']/1e6,1) if pf else None,'public_float_asof':pf['end'] if pf else None,
            'sec_employees':emp[0] if emp else None}
LEGAL=r'\b(inc|incorporated|corp|corporation|co|company|llc|ltd|plc|n\.?v|s\.?a|ag|gmbh|holdings?|group|the)\b\.?'
def norm(n):
    n=re.sub(r'\(.*?\)','',n); n=re.sub(LEGAL,'',n,flags=re.I); n=re.sub(r'[^A-Za-z0-9& -]',' ',n)
    return re.sub(r'\s+',' ',n).strip()
def key_token(name):
    w=norm(name).upper().split()
    if not w: return ''
    return w[0] if len(w[0])>=5 or len(w)==1 else ' '.join(w[:2])
_FDA=None
def _fda():
    global _FDA
    if _FDA is None:
        d=json.load(open('/home/claude/build/bulk/drug-drugsfda-0001-of-0001.json'))
        _FDA=[r for r in d['results'] if r.get('application_number','').startswith(('NDA','BLA'))]
    return _FDA
FDA_EXCLUDE={'bridgebio oncology','spectrum antimicrobials','bright peak','alloy therapeutics','granite bio'}  # distinct company that shares a sponsor-name prefix with BridgeBio Pharma
def fda_profile(name):
    nm=key_token(name)
    out={'fda_query':nm}
    if any(x in name.lower() for x in FDA_EXCLUDE):
        out.update(fda_nda_bla=0,fda_latest_approval=None,fda_brands='',fda_510k=0,fda_pma=0); return out
    apps=set(); latest=None; brands=set()
    ctoks=norm(name).upper().split()
    SUFX={'INC','LLC','CORP','LTD','CO','LP','PLC','AG','SA','NV','GMBH','HLDGS','HOLDINGS','USA','US','AMERICA','AMERICAS','NORTH','GLOBAL','INTL','INTERNATIONAL','PHARMS','PHARMA','PHARMACEUTICALS','THERAPS','THERAPEUTICS','THERAP','BIOSCIENCES','BIOSCIENCE','BIO','LABS','LABORATORIES','SCIENCES','SCIENCES,'}
    for r in _fda():
        sp=r.get('sponsor_name','').upper()
        if not (sp==nm or sp.startswith(nm+' ')): continue
        st=re.sub(r'[^A-Z0-9 ]',' ',sp).split()
        nt=len(nm.split())
        if len(st)>nt:
            nxt=st[nt]
            ok= nxt in SUFX or (len(ctoks)>nt and nxt[:3]==ctoks[nt][:3])
            if not ok: continue
        for s in r.get('submissions',[]):
            if s.get('submission_type')=='ORIG' and s.get('submission_status')=='AP':
                apps.add(r['application_number']); dte=s.get('submission_status_date')
                if dte and (latest is None or dte>latest): latest=dte
                for p in r.get('products',[]): brands.add(p.get('brand_name',''))
    out.update(fda_nda_bla=len(apps),fda_latest_approval=f'{latest[:4]}-{latest[4:6]}-{latest[6:]}' if latest else None,
               fda_brands='; '.join(sorted(b for b in brands if b))[:120])
    q=urllib.parse.quote(f'applicant:"{nm}"')
    d=get(f'https://api.fda.gov/device/510k.json?search={q}&limit=1')
    out['fda_510k']=d.get('meta',{}).get('results',{}).get('total',0) if d else 0
    d=get(f'https://api.fda.gov/device/pma.json?search={q}&limit=1')
    out['fda_pma']=d.get('meta',{}).get('results',{}).get('total',0) if d else 0
    return out
PH={'EARLY_PHASE1':0.5,'PHASE1':1,'PHASE2':2,'PHASE3':3,'PHASE4':4}
def ct_profile(name):
    nm=norm(name)
    url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.lead':nm,'pageSize':200,
        'fields':'NCTId,Phase,OverallStatus,LeadSponsorName,StartDate,PrimaryCompletionDate,BriefTitle,Condition','filter.overallStatus':'RECRUITING,ACTIVE_NOT_RECRUITING,NOT_YET_RECRUITING,ENROLLING_BY_INVITATION,COMPLETED'})
    d=get(url)
    mx=0; n_active=0; n=0; nxt=None
    for s in d.get('studies',[]):
        ps=s.get('protocolSection',{})
        lead=ps.get('sponsorCollaboratorsModule',{}).get('leadSponsor',{}).get('name','')
        if not lead.upper().startswith(key_token(name)): continue
        st=ps.get('statusModule',{}); start=st.get('startDateStruct',{}).get('date','')
        if st.get('overallStatus')=='COMPLETED' and start<'2021': continue
        n+=1
        if st.get('overallStatus')!='COMPLETED': n_active+=1
        phs=ps.get('designModule',{}).get('phases',[]) or []
        for p in phs: mx=max(mx,PH.get(p,0))
        pcd=st.get('primaryCompletionDateStruct',{}).get('date','')
        if st.get('overallStatus')!='COMPLETED' and any(p in ('PHASE2','PHASE3') for p in phs) and pcd>='2026-10':
            cand=(pcd,'/'.join(p.replace('PHASE','Ph') for p in phs),ps.get('identificationModule',{}).get('nctId',''),(ps.get('conditionsModule',{}).get('conditions') or [''])[0][:60])
            if nxt is None or cand[0]<nxt[0]: nxt=cand
    return {'ct_trials_since2021':n,'ct_active':n_active,'ct_max_phase':mx,
            'next_readout':nxt[0] if nxt else None,'next_readout_phase':nxt[1] if nxt else None,'next_readout_nct':nxt[2] if nxt else None,'next_readout_condition':nxt[3] if nxt else None}
if __name__=='__main__':
    for nm,tk in [('Gilead Sciences, Inc.','GILD'),('IDEAYA Biosciences','IDYA'),('Neurocrine Biosciences','NBIX'),('Illumina, Inc.','ILMN')]:
        print(nm, sec_profile(tk), fda_profile(nm), ct_profile(nm))

import json,csv,glob,collections,sys
H='region,company,category,site_type,street,city,state,zip,submarket,ticker,biospace_listed,tests_met,employees,employees_source,private_raised_total_usd_m,last_round_usd_m,last_round_date,last_round_type,funding_source_url,modality,footprint_event_2025_26,footprint_source_url,verified,source_url,notes,website,country'.split(',')
NAME={'biotech_beach':'Biotech Beach','biotech_bay':'Biotech Bay','genetown':'Genetown','pharm_country':'Pharm Country','biocapital':'BioCapital','bio_nc':'Bio NC','biomidwest':'BioMidwest','seattle':'Seattle','colorado':'Colorado'}
geo={c['cik']:c for c in json.load(open('/home/claude/build/formd/new_candidates_geo.json'))}
scr={}
for f in glob.glob('/home/claude/census/formd_screen_*.csv'):
    for r in csv.DictReader(open(f,encoding='utf-8-sig')): scr[r['cik'].zfill(10)]=r
out=collections.defaultdict(list); n=collections.Counter()
for cik,c in geo.items():
    s=scr.get(cik)
    if not s: n['unscreened']+=1; continue
    if s.get('keep','').upper()!='Y': n['dropped:'+s.get('status','')+'/'+s.get('category','')]+=1; continue
    url=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{c['adsh_last'].replace('-','')}/primary_doc.xml"
    nm=c['name'].strip()
    REN={'0001995302':'Lykos Therapeutics','0001513330':'Macro Biologics','0001679037':'Nortiva Bio','0002001012':'FathomTx'}
    if cik=='0002028122': n['dup:Formation Bio']+=1; continue
    if cik in REN: nm=REN[cik]
    nm=nm.title() if nm.isupper() else nm
    row={'region':NAME[c['region']],'company':nm,'category':s.get('category') or 'Biopharma','site_type':'HQ','street':(c['street']+' '+c['street2']).strip(),'city':c['city'].title() if c['city'].isupper() else c['city'],
         'state':c['state'],'zip':c['zip'],'submarket':'','ticker':'','biospace_listed':'N','tests_met':'T7','private_raised_total_usd_m':c['raised_since_2023_usd_m'],
         'last_round_date':c['last_first_sale'],'last_round_type':'Form D offering','funding_source_url':url,'modality':s.get('modality',''),'verified':'Y','source_url':url,
         'notes':f"SEC Form D: ${c['raised_since_2023_usd_m']}M sold since Jan 2023 across {c['n_offerings']} offering(s). {s.get('status_note','')}".strip(),'website':s.get('website',''),'country':'US'}
    out[c['region']].append(row); n['kept']+=1
for k,rows in out.items():
    with open(f'/home/claude/census/{k}_formd.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=H); w.writeheader(); [w.writerow(r) for r in rows]
print(dict(n)); print({k:len(v) for k,v in out.items()})

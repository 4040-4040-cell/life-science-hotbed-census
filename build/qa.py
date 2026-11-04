import json,glob,collections,sys,re
sys.path.insert(0,'/home/claude/build')
from score import score, num, footprint_dir
from assemble import BBOX
issues=collections.defaultdict(list)
allc=collections.defaultdict(list)
for f in sorted(glob.glob('enriched/*.json')):
    k=f.split('/')[-1][:-5]; rows=json.load(open(f))
    geo=collections.Counter(r['geo_precision'] for r in rows)
    subs=collections.Counter(r.get('submarket','') for r in rows)
    print(f'\n== {k}: {len(rows)} rows; geo {dict(geo)}')
    print('   submarkets:',dict(subs.most_common()))
    for r in rows:
        s=score(r); c=r['company']
        if r.get('site_type')=='HQ': allc[c.lower()].append(k)
        la=r.get('lat')
        if la is not None and k in BBOX:
            b=BBOX[k]
            if not (b[0]<=la<=b[1] and b[2]<=r['lon']<=b[3]): issues['out_of_bbox'].append((k,c,r.get('city'),la,r['lon'],r.get('geo_match','')[:60]))
        if r.get('category')=='Biopharma' and (num(r.get('fda_nda_bla')) or 0)>0 and 'T4' not in (r.get('tests_met') or ''):
            issues['fda_check'].append((k,c,r.get('fda_query'),r.get('fda_brands','')[:70]))
        if r.get('category')!='Institution' and (num(r.get('ct_max_phase')) or 0)>=3 and not r.get('ticker') and not num(r.get('private_raised_total_usd_m')) and r.get('category')=='Biopharma':
            issues['ct_check_private_ph3'].append((k,c,r.get('ct_max_phase'),r.get('ct_trials_since2021')))
        rw=num(r.get('runway_months'))
        if rw is not None and (rw<3 or rw>240): issues['runway_outlier'].append((k,c,rw,r.get('liquidity_usd_m'),r.get('op_cash_flow_fy_usd_m')))
        fp=r.get('footprint_event_2025_26','')
        if fp: issues['footprint_dir'].append((footprint_dir(fp),k,c,fp[:110]))
        if r.get('ticker') and r.get('site_type')=='HQ' and r.get('sec_status')!='ok' and (r.get('country','US') or 'US').upper() not in ('UK','CH','FR','DE'): issues['sec_missing'].append((k,c,r.get('ticker'),r.get('sec_status')))
        en=num(r.get('k_emp_now')); ep=num(r.get('k_emp_prior'))
        if en and ep and (en/ep>3 or en/ep<0.33): issues['emp_jump'].append((k,c,ep,en))
        if num(r.get('k_props_sf_max')) and num(r.get('k_props_sf_max'))>2_000_000: issues['sf_big'].append((k,c,r.get('k_props_sf_max')))
dups={c:v for c,v in allc.items() if len(set(v))>1}
for k,v in issues.items():
    print(f'\n## {k}: {len(v)}')
    for x in v[:400]: print('  ',x)
print('\n## HQ in >1 region:',dups)

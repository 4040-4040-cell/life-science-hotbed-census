import json,glob,csv
out='/home/claude/build/hotbed_census_2026-10-28.csv'
cols=['region','company','ticker','tier','score','read','read_why','category','site_type','street','city','state','submarket','zone','modality','tests_met',
 'employees','employees_prior','emp_change_pct','emp_asof','cash_and_investments_usd_m','cash_asof','op_cash_flow_fy_usd_m','runway_months','revenue_fy_usd_m','public_float_usd_m','float_asof',
 'private_raised_usd_m','last_round_usd_m','last_round_date','last_round_type','offerings_12m','stage','fda_products','latest_fda_approval','next_ph2_3_completion','next_trial',
 'largest_site_sf_10k','lease_expiration_years','landlords_named','footprint_2025_26','footprint_direction','website','address_source','address_verified','lat','lon','geo_precision']
n=0
with open(out,'w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for fn in sorted(glob.glob('/home/claude/build/site/data/*.js')):
        s=open(fn).read(); R=json.loads(s[s.index('=')+1:-1])
        for o in R['rows']:
            p=o.get('p',{})
            w.writerow([R['name'],o['company'],o['ticker'],o['tier'],o['score'],o['read'],o['read_why'],o['category'],o['site_type'],o['street'],o['city'],o['state'],o['submarket'],o.get('zone'),o['modality'],o['tests_met'],
              p.get('emp_now') or o.get('emp'),p.get('emp_prior'),o.get('emp_chg'),p.get('emp_period'),p.get('liq'),p.get('liq_asof'),p.get('ocf'),o.get('runway_disp'),p.get('rev'),p.get('float'),p.get('float_asof'),
              p.get('raised'),p.get('last_round'),p.get('last_round_date'),p.get('last_round_type'),p.get('off12'),o['stage_label'],p.get('brands'),p.get('latest_appr'),p.get('next'),p.get('next_nct'),
              p.get('sf_max'),';'.join(str(x) for x in p.get('lease_exp',[]) or []),';'.join(p.get('landlords',[]) or []),o.get('footprint'),o.get('footprint_dir'),o.get('web'),o.get('source_url'),p.get('verified'),o.get('lat'),o.get('lon'),o.get('geo_precision')])
            n+=1
print(n,out)

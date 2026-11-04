import csv,glob,sys,json
sys.path.insert(0,'/home/claude/build')
from tenk import profile
from enrich import ct_profile
tks=set(); names=set()
for f in glob.glob('/home/claude/census/*.csv'):
    if 'websites' in f: continue
    for r in csv.DictReader(open(f,newline='',encoding='utf-8-sig')):
        tk=(r.get('ticker') or '').strip(); pre=tk.split(':')[0].upper() if ':' in tk else ''
        if tk and pre in ('','NASDAQ','NYSE','AMEX','NYSEAMERICAN') and (r.get('country','US') or 'US').upper()!='UK' and r.get('site_type')=='HQ': tks.add(tk)
        if r.get('category')!='Institution': names.add(r['company'])
print(len(tks),'tickers',len(names),'names',flush=True)
for i,tk in enumerate(sorted(tks)):
    try: p=profile(tk)
    except Exception as e: print('ERR',tk,e,flush=True)
    if i%25==0: print(i,tk,flush=True)
for n in sorted(names):
    try: ct_profile(n)
    except Exception as e: pass
print('done',flush=True)

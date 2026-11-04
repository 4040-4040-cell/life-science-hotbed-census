import csv,glob,json,sys
sys.path.insert(0,'/home/claude/build')
web={}
for w in csv.DictReader(open('/home/claude/census/websites_existing.csv',newline='',encoding='utf-8-sig')):
    if w.get('website'): web[w['company'].strip()]=w['website'].strip()
items={}
for f in glob.glob('/home/claude/census/*.csv'):
    if 'websites' in f or 'overflow' in f: continue
    for r in csv.DictReader(open(f,newline='',encoding='utf-8-sig')):
        if 'company' not in r: break
        c=r['company'].strip(); u=(r.get('website') or '').strip() or web.get(c,'')
        if u and r.get('category')!='Institution' or u: items[c]=u
json.dump(sorted(items.items()),open('/home/claude/build/logo_items.json','w'))
print(len(items))

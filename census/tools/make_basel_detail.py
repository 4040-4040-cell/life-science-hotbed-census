# Build the two canton-level census files from the Basel hub rows plus the detail directory; sites keep their own canton
import csv,os
H=None; rows=[]
for f in ['basel.csv','basel_add.csv','basel_directory.csv']:
    if not os.path.exists(f): continue
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        rows.append(r)
cols=[]
for r in rows:
    for k in r:
        if k and k not in cols: cols.append(k)
for k in ('campus','building','subsidiary_of','sec_ticker'):
    if k not in cols: cols.append(k)
seen=set(); n={}
for key,st in (('basel_city','BS'),('basel_land','BL')):
    out=[r for r in rows if (r.get('state') or '').strip()==st and (r.get('country') or '').strip()=='CH']
    dd=[]
    for r in out:
        k=(r['company'].strip().lower(),(r.get('street') or '').strip().lower())
        if k in seen: continue
        seen.add(k); dd.append(r)
    w=csv.DictWriter(open(f'{key}.csv','w',newline='',encoding='utf-8'),fieldnames=cols,extrasaction='ignore'); w.writeheader(); w.writerows(dd); n[key]=len(dd)
# footprint classifications follow the site into its canton view
fc=list(csv.DictReader(open('footprint_class.csv',encoding='utf-8-sig'))); h=list(fc[0].keys())
base=[x for x in fc if x['region_slug']=='basel']; keep=[x for x in fc if x['region_slug'] not in ('basel_city','basel_land')]
names={key:{r['company'].strip().lower() for r in csv.DictReader(open(f'{key}.csv',encoding='utf-8'))} for key in ('basel_city','basel_land')}
for key in ('basel_city','basel_land'):
    for x in base:
        if x['company'].strip().lower() in names[key]: keep.append({**x,'region_slug':key})
w=csv.DictWriter(open('footprint_class.csv','w',newline='',encoding='utf-8'),fieldnames=h); w.writeheader(); w.writerows(keep)
print(n)

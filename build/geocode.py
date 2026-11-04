import csv, json, os, re, sys, time, urllib.parse, urllib.request
CACHE='/home/claude/build/geocache.json'
cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
UA={'User-Agent':os.environ.get('WCLS_UA','WCLS hotbed census research build')}
def q(params,cc='us'):
    key=json.dumps(params,sort_keys=True)+('' if cc=='us' else cc)
    if key in cache: return cache[key]
    url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({**params,'format':'json','limit':1,'countrycodes':cc})
    for i in range(3):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=20)); break
        except Exception as e:
            time.sleep(3); r=None
    time.sleep(1.1)
    cache[key]=r; json.dump(cache,open(CACHE,'w'))
    return r
WORDNUM={'one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','ten':'10','eleven':'11','twelve':'12','fifteen':'15','twenty':'20','fifty':'50','hundred':'100'}
def clean_street(s):
    s=re.sub(r',?\s*\b\d+(st|nd|rd|th)\s+(floor|fl)\b.*$','',s,flags=re.I)
    s=re.sub(r',?\s*\b(suite|ste\.?|unit|floor|fl\.?|bldg\.?|building|room|rm\.?|#|mailbox|pmb|c/o)\b\s*[\w-]*.*$','',s,flags=re.I)
    s=re.sub(r'\s*#\s*[\w-]+.*$','',s)
    s=re.sub(r'^\s*(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|fifty|hundred)\b',lambda m:WORDNUM[m.group(1).lower()],s,flags=re.I)
    return s.strip(' ,')
def swiss(text):
    key='geoadmin|'+text
    if key in cache: return cache[key]
    url='https://api3.geo.admin.ch/rest/services/api/SearchServer?'+urllib.parse.urlencode({'searchText':text,'type':'locations','origins':'address','limit':1})
    r=None
    for i in range(3):
        try: r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=20)).get('results') or None; break
        except Exception: time.sleep(2)
    cache[key]=r; json.dump(cache,open(CACHE,'w')); return r
def geocode(row):
    st,city,state,z=row['street'].strip(),row['city'].strip(),row['state'].strip(),row['zip'].strip()
    ctry=(row.get('country') or '').strip().upper()
    cc={'UK':'gb','GB':'gb','CH':'ch','FR':'fr','DE':'de'}.get(ctry,'us')
    tries=[]
    if cc=='ch' and st:
        cs=re.sub(r'\(.*?\)','',clean_street(st)).strip(' ,')
        r=swiss(f'{cs} {z} {city}'.strip())
        if r and re.search(r'\d',cs):
            a=r[0]['attrs']; lab=re.sub('<[^>]+>','',a['label'])
            num=re.search(r'\d+\w?',cs).group(0).lower()
            if num in lab.lower().split() or (' '+num+' ') in (' '+lab.lower()+' '): return a['lat'],a['lon'],'street',lab+' (geo.admin.ch)'
    if st:
        cs=clean_street(st)
        tries+=[('street',{'street':cs,'city':city,'state':state,'postalcode':z}),
                ('street',{'street':cs,'city':city,'state':state}),
                ('street',{'q':f'{cs}, {city}, {state} {z}'})]
        if z: tries.append(('zip',{'postalcode':z,'state':state}))
    if cc!='us' and z: tries.append(('zip',{'postalcode':z}))
    tries.append(('city',{'city':city,'state':state}))
    for prec,p in tries:
        if cc!='us' and 'state' in p: p={k:v for k,v in p.items() if k!='state'}
        if cc!='us' and 'q' not in p: p.setdefault('country',{'gb':'United Kingdom','ch':'Switzerland','fr':'France','de':'Germany'}[cc])
        r=q({k:v for k,v in p.items() if v},cc)
        if r: return float(r[0]['lat']),float(r[0]['lon']),prec,r[0].get('display_name','')
    return None,None,'none',''
if __name__=='__main__':
    src,dst=sys.argv[1],sys.argv[2]
    rows=list(csv.DictReader(open(src,newline='',encoding='utf-8')))
    out=[]
    for row in rows:
        lat,lon,prec,dn=geocode(row)
        row.update(lat=lat,lon=lon,geo_precision=prec,geo_match=dn); out.append(row)
    with open(dst,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    from collections import Counter
    print(src, len(out), Counter(r['geo_precision'] for r in out))

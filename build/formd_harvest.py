import json,os,time,urllib.parse,urllib.request,sys
UA={'User-Agent':'WCLS research chad.urie@urieinvestments.com'}
OUT='/home/claude/build/formd/hits.json'
hits=json.load(open(OUT)) if os.path.exists(OUT) else {}
STATES=['CA','MA','NJ','NY','PA','CT','RI','MD','DC','VA','DE','NC','IL','IN','MI','MN','MO','OH','WI','IA','WA','CO']
def q(term,st,frm):
    u='https://efts.sec.gov/LATEST/search-index?'+urllib.parse.urlencode({'q':f'"{term}"','forms':'D','dateRange':'custom','startdt':'2023-01-01','enddt':'2026-10-28','locationCodes':st,'from':frm})
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
        except Exception as e: time.sleep(2+i*2)
    return {}
for term in ['Biotechnology','Pharmaceuticals']:
    for st in STATES:
        frm=0
        while True:
            d=q(term,st,frm); H=d.get('hits',{}).get('hits',[])
            tot=d.get('hits',{}).get('total',{}).get('value',0)
            for h in H:
                s=h['_source']; hits[h['_id']]={'adsh':s['adsh'],'cik':s['ciks'][0],'name':s['display_names'][0],'date':s['file_date'],'loc':s.get('biz_locations',[''])[0],'state':st,'term':term}
            frm+=len(H)
            if not H or frm>=tot or frm>=9900: break
            time.sleep(0.15)
        print(term,st,tot,flush=True)
        json.dump(hits,open(OUT,'w'))
print('total filings',len(hits))

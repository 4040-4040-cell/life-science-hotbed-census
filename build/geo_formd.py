import json,sys
sys.path.insert(0,'/home/claude/build')
from geocode import geocode
new=json.load(open('formd/new_candidates.json'))
for i,c in enumerate(new):
    r={'street':(c['street'] or '').strip(),'city':c['city'],'state':c['state'],'zip':c['zip'],'country':'US'}
    lat,lon,prec,dn=geocode(r); c.update(lat=lat,lon=lon,geo_precision=prec)
    if i%50==0: print(i,flush=True)
json.dump(new,open('formd/new_candidates_geo.json','w')); print('done')

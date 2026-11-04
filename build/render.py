import json, re, sys, os, io, base64, collections
sys.path.insert(0,'/home/claude/build')
from assemble import build, zones, elsewhere, snapshots
from score import W
from build import REG
from tiles import fit_zoom, deg2num, fetch, stylize
from PIL import Image
LD='/home/claude/build/logos'; OUT=os.environ.get('SITE_OUT','/home/claude/build/site')
os.makedirs(f'{OUT}/data',exist_ok=True)
CHOICE=json.load(open(f'{LD}/choice.json')) if os.path.exists(f'{LD}/choice.json') else {}
def logo_uri(k):
    src=CHOICE.get(k)
    if src in (None,'reject'): return None,False
    p=f'{LD}/{src}/{k}.png'
    if not os.path.exists(p): return None,False
    im=Image.open(p).convert('RGBA'); im.thumbnail((300,72))
    px=[q for q in im.resize((60,max(1,int(60*im.height/im.width)))).getdata() if q[3]>60]
    lum=[0.3*q[0]+0.59*q[1]+0.11*q[2] for q in px]
    light=(sum(1 for v in lum if v>222)/len(lum)>0.45) if lum else False
    b=io.BytesIO(); im.save(b,'WEBP',quality=82,method=6)
    return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode(), light
regions,tiles,zmin,zmax,compare,allrows=build(max_tiles_region=int(sys.argv[1]) if len(sys.argv)>1 else 520)
total=0
for R in regions:
    key=[k for k,s_,*_ in REG if s_==R['slug']][0]
    R['zones']=zones(R['rows'],region=key); R['elsewhere']=elsewhere(R['rows']); R['snaps']=snapshots(R['rows']); logos={}
    # exhibit bounds and full tile coverage for that view
    P=[p for z in R['zones'] for p in z['hull']]
    if P:
        la=[p[0] for p in P]; lo=[p[1] for p in P]; dla=(max(la)-min(la))*0.14+0.004; dlo=(max(lo)-min(lo))*0.14+0.004
        bb=(min(la)-dla,max(la)+dla,min(lo)-dlo,max(lo)+dlo); R['ex_bounds']=[[bb[0],bb[2]],[bb[1],bb[3]]]
        zx=fit_zoom([bb[0],bb[1]],[bb[2],bb[3]],w=880,h=660,pad=0.0)
        # dense-core inset: zones whose centroids sit within 70 px of each other at the exhibit zoom
        import math as _m
        Zs=R['zones']; ppk=256*2**zx/(40075*_m.cos(_m.radians((bb[0]+bb[1])/2)))
        def kmd(a,b): return _m.hypot((a[0]-b[0])*111,(a[1]-b[1])*111*_m.cos(_m.radians(a[0])))
        best=[]
        for i,zi in enumerate(Zs):
            g=[j for j,zj in enumerate(Zs) if kmd(zi['c'],zj['c'])*ppk<(130 if R['slug']=='basel-land' else 70)]
            if len(g)>len(best): best=g
        if len(best)>=3:
            P2=[p for j in best for p in Zs[j]['hull']]
            la2=[p[0] for p in P2]; lo2=[p[1] for p in P2]; d2=max(max(la2)-min(la2),0.01)*0.18; e2=max(max(lo2)-min(lo2),0.01)*0.18
            ib=(min(la2)-d2,max(la2)+d2,min(lo2)-e2,max(lo2)+e2); R['inset']={'zones':best,'bounds':[[ib[0],ib[2]],[ib[1],ib[3]]]}
            zi_=min(fit_zoom([ib[0],ib[1]],[ib[2],ib[3]],w=330,h=270,pad=0.0),zmax[R['slug']])
            R['inset']['zoom']=zi_
            for z in (zi_-1,zi_):
                x0,y1=deg2num(ib[0]-d2*2,ib[2]-e2*3,z); x1,y0=deg2num(ib[1]+d2*2,ib[3]+e2*3,z)
                for x in range(int(x0)-1,int(x1)+2):
                    for y in range(int(y0)-1,int(y1)+2):
                        k_=f'{z}/{x}/{y}'
                        if k_ not in tiles[R['slug']]:
                            f=fetch(z,x,y)
                            if f: tiles[R['slug']][k_]=stylize(f)
        wla=(bb[1]-bb[0])*0.35; wlo=(bb[3]-bb[2])*0.65
        cb=(bb[0]-wla,bb[1]+wla,bb[2]-wlo,bb[3]+wlo)
        for z in (zx-1,zx,zx+1):
            if z>zmax[R['slug']]: continue
            x0,y1=deg2num(cb[0],cb[2],z); x1,y0=deg2num(cb[1],cb[3],z)
            for x in range(int(x0)-1,int(x1)+2):
                for y in range(int(y0)-1,int(y1)+2):
                    k_=f'{z}/{x}/{y}'
                    if k_ not in tiles[R['slug']]:
                        f=fetch(z,x,y)
                        if f: tiles[R['slug']][k_]=stylize(f)
    for o in R['rows']:
        u,lt=logo_uri(o['logo'])
        if u: logos[o['logo']]=u; o['logo_light']=lt
        else: o['logo']=None
    payload={**R,'tiles':tiles[R['slug']],'logos':logos}
    js='window.REGION['+json.dumps(R['slug'])+']='+json.dumps(payload,separators=(',',':'))+';'
    open(f"{OUT}/data/{R['slug']}.js",'w').write(js); total+=len(js)
    print(R['slug'],'rows',len(R['rows']),'logos',len(logos),'MB',round(len(js)/1e6,2))
n_sc=sum(c['n'] for c in compare); nA=sum(c['A'] for c in compare)
lead=max(compare,key=lambda c:c['A']); nS=sum(c['sites'] for c in compare)
DATA={'title':'Life science hotbeds: who is in each cluster and where they sit',
 'subtitle':f'{n_sc:,} headquartered companies and {nS:,} major sites of outside companies across {len(compare)} hubs, plus building-level views of Basel-Stadt and Basel-Landschaft, each tested against a fixed inclusion rule and scored on scale, capital, cash durability, development stage and 2025 to 2026 momentum. US and UK hubs as of October 28, 2026; Basel as of November 2, 2026.',
 'compare_headline':f"{lead['name']} has the most Tier A companies at {lead['A']} of {lead['n']}; {nA:,} of {n_sc:,} headquartered companies make Tier A across all hubs",
 'compare_note':'<p>Counts reflect the inclusion rule below, not every company in each market. Public liquidity is cash plus marketable securities from the latest 10-Q in SEC XBRL, summed across public companies headquartered in the region (US filers only; UK and Basel show n/a because most of their listed companies do not file with the SEC). Private capital raised sums totals found in company releases and SEC Form D filings and is a floor. Expansion and contraction counts are 2025 to 2026 footprint events found in filings and releases.</p>',
 'regions':[{'slug':R['slug'],'name':R['name'],'geo':R['geo']} for R in regions],'compare':compare,'zmin':zmin,'zmax':zmax,
 'method':open('/home/claude/build/method.html').read().replace('{WS}',str(int(W['scale']*100))).replace('{WC}',str(int(W['capital']*100))).replace('{WD}',str(int(W['durability']*100))).replace('{WT}',str(int(W['stage']*100))).replace('{WM}',str(int(W['momentum']*100)))}
css=re.sub(r'url\([^)]*\)','none',open('/home/claude/build/vendor/package/dist/leaflet.css').read())
html=open('/home/claude/build/template.html').read().replace('LEAFLETCSS',css).replace('__DATA__',json.dumps(DATA,separators=(',',':'))).replace('__APP__',open('/home/claude/build/app.js').read())
open(f'{OUT}/index.html','w').write(html); total+=len(html)
json.dump(allrows,open('/home/claude/build/allrows.json','w'))
print('total MB',round(total/1e6,2))

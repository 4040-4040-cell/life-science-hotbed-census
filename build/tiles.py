import math, os, io, time, base64, urllib.request
from PIL import Image, ImageEnhance, ImageOps
TD='/home/claude/build/tilecache'; os.makedirs(TD,exist_ok=True)
UA={'User-Agent':os.environ.get('WCLS_UA','WCLS hotbed census research build')}
def deg2num(lat,lon,z):
    n=2**z; x=(lon+180)/360*n; y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n
    return x,y
AD='/home/claude/build/tilecache_aerial'; os.makedirs(AD,exist_ok=True)
USGS='https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}'
ESRI='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
REF='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'
def _get(url,fn):
    if os.path.exists(fn): return fn
    for i in range(3):
        try:
            b=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read()
            if len(b)>200: open(fn,'wb').write(b); return fn
        except Exception: time.sleep(2)
    return None
def _blank(fn):
    g=Image.open(fn).convert('L'); h=g.histogram(); n=g.size[0]*g.size[1]
    return (h[255]+h[254]+h[0]+h[1])/n>0.12
def fetch(z,x,y):
    # aerial: USGS public-domain imagery west of 50W (US hubs), Esri World Imagery elsewhere (UK, Basel); Esri place labels on top
    lon=x/2**z*360-180
    src,url=('esri',ESRI)  # one imagery source for every hub so tones match across tiles
    out=f'{AD}/{src}_{z}_{x}_{y}.jpg'
    if os.path.exists(out): return out
    a=_get(url.format(z=z,x=x,y=y),f'{AD}/raw_{src}_{z}_{x}_{y}.jpg')
    if src=='usgs' and (not a or _blank(a)): a=_get(ESRI.format(z=z,x=x,y=y),f'{AD}/raw_esri_{z}_{x}_{y}.jpg')  # USGS returns blank tiles over open water and at coverage edges
    if not a: return None
    r=_get(REF.format(z=z,x=x,y=y),f'{AD}/ref_{z}_{x}_{y}.png')
    im=Image.open(a).convert('RGB')
    im=ImageEnhance.Color(im).enhance(0.62); im=ImageEnhance.Contrast(im).enhance(0.92); im=ImageEnhance.Brightness(im).enhance(1.06)
    im=im.convert('RGBA')
    if r:
        try: im.alpha_composite(Image.open(r).convert('RGBA'))
        except Exception: pass
    im.convert('RGB').save(out,'JPEG',quality=92)
    return out
def fetch_osm(z,x,y):
    fn=f'{TD}/{z}_{x}_{y}.png'
    if not os.path.exists(fn):
        for i in range(3):
            try:
                b=urllib.request.urlopen(urllib.request.Request(f'https://tile.openstreetmap.org/{z}/{x}/{y}.png',headers=UA),timeout=30).read()
                open(fn,'wb').write(b); break
            except Exception: time.sleep(2)
        time.sleep(0.25)
    return fn if os.path.exists(fn) else None
def stylize(fn):
    if fn.endswith('.jpg'):
        im=Image.open(fn).convert('RGB'); buf=io.BytesIO(); im.save(buf,'WEBP',quality=52,method=6)
        return 'data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
    im=Image.open(fn).convert('RGB')
    im=ImageEnhance.Color(im).enhance(0.16)
    im=ImageEnhance.Contrast(im).enhance(0.8)
    im=ImageEnhance.Brightness(im).enhance(1.08)
    buf=io.BytesIO(); im.save(buf,'WEBP',quality=40,method=6)
    return 'data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
def fit_zoom(lats,lons,w=1000,h=640,pad=0.12):
    for z in range(15,3,-1):
        x0,y1=deg2num(min(lats),min(lons),z); x1,y0=deg2num(max(lats),max(lons),z)
        if (x1-x0)*256*(1+pad)<=w and (y1-y0)*256*(1+pad)<=h: return z
    return 4
def tile_set(points,zfit,zmax=None,full_levels=2,radius_px=260):
    zmax=zmax or min(zfit+5,16)
    lats=[p[0] for p in points]; lons=[p[1] for p in points]
    want=set()
    for z in range(max(zfit-1,3),zmax+1):
        if z<zfit+full_levels:
            x0,y1=deg2num(min(lats)-0.15*(max(lats)-min(lats)+.05),min(lons)-0.2*(max(lons)-min(lons)+.05),z)
            x1,y0=deg2num(max(lats)+0.15*(max(lats)-min(lats)+.05),max(lons)+0.2*(max(lons)-min(lons)+.05),z)
            for x in range(int(x0)-1,int(x1)+2):
                for y in range(int(y0)-1,int(y1)+2): want.add((z,x,y))
        else:
            r=radius_px/256
            for la,lo in points:
                x,y=deg2num(la,lo,z)
                for xx in range(int(x-r),int(x+r)+1):
                    for yy in range(int(y-r*0.7),int(y+r*0.7)+1): want.add((z,xx,yy))
    return want

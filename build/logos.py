import io, os, re, json, sys, hashlib, urllib.request, urllib.parse
from bs4 import BeautifulSoup
from PIL import Image, ImageChops
import cairosvg
LD='/home/claude/build/logos'; META=f'{LD}/meta.json'
meta=json.load(open(META)) if os.path.exists(META) else {}
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36','Accept-Language':'en-US,en'}
def fetch(url,timeout=15):
    r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=timeout)
    return r.read(), r.geturl(), r.headers.get('Content-Type','')
def key_of(company): return re.sub(r'[^a-z0-9]+','-',company.lower()).strip('-')[:60]
def to_png(data, ctype, url):
    s=data[:400].lstrip().lower()
    if b'<svg' in data[:2000].lower() or 'svg' in ctype or url.lower().split('?')[0].endswith('.svg'):
        try: data=cairosvg.svg2png(bytestring=data, output_height=240)
        except Exception:
            t=data.decode('utf-8','ignore'); m=re.search(r'viewBox=["\']\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)',t)
            if not m: raise
            t=re.sub(r'<svg',f'<svg width="{m.group(1)}" height="{m.group(2)}"',t,count=1); data=cairosvg.svg2png(bytestring=t.encode(), output_height=240)
    im=Image.open(io.BytesIO(data)); im.load()
    if getattr(im,'n_frames',1)>1: im.seek(0)
    return im.convert('RGBA')
def trim(im):
    bg=Image.new('RGBA',im.size,(255,255,255,0))
    a=im.split()[-1]
    if a.getextrema()[0]<250: box=a.point(lambda v:255 if v>20 else 0).getbbox()
    else:
        rgb=im.convert('RGB'); diff=ImageChops.difference(rgb,Image.new('RGB',im.size,rgb.getpixel((0,0)))).convert('L').point(lambda v:255 if v>18 else 0); box=diff.getbbox()
    return im.crop(box) if box else im
def lightness(im):
    px=[p for p in im.resize((60,max(1,int(60*im.height/im.width)))).getdata() if p[3]>60]
    if not px: return 255
    return sum(0.3*p[0]+0.59*p[1]+0.11*p[2] for p in px)/len(px)
def candidates(html, base):
    soup=BeautifulSoup(html,'lxml'); out=[]
    def absu(u): return urllib.parse.urljoin(base,u)
    def logoish(el):
        s=' '.join([str(el.get('class','')),el.get('id','') or '',el.get('alt','') or '',el.get('src','') or '',el.get('aria-label','') or '']).lower()
        return 'logo' in s or 'brand' in s
    scopes=soup.select('header, nav, [class*=header], [id*=header]') or [soup]
    for sc in scopes+[soup]:
        for el in sc.find_all(['img','svg','a','div','span']):
            if el.name=='img' and (logoish(el) or (el.parent and logoish(el.parent))):
                src=el.get('src') or el.get('data-src') or (el.get('srcset','').split(' ')[0] if el.get('srcset') else '')
                if src and not src.startswith('data:image/gif'): out.append(('img',absu(src)))
            elif el.name=='svg' and (logoish(el) or (el.parent and logoish(el.parent)) or (el.parent and el.parent.parent and logoish(el.parent.parent))):
                svg=str(el)
                if 'xmlns' not in svg[:200]: svg=svg.replace('<svg','<svg xmlns="http://www.w3.org/2000/svg"',1)
                if len(svg)>300: out.append(('inline',svg))
        if out: break
    for l in soup.find_all('link',rel=lambda v: v and any('apple-touch-icon' in x or 'icon'==x for x in (v if isinstance(v,list) else [v]))):
        if l.get('href'): out.append(('icon',absu(l['href'])))
    seen=set(); res=[]
    for c in out:
        if c[1] in seen: continue
        seen.add(c[1]); res.append(c)
    return res
def get_logo(company, website, force=False):
    k=key_of(company)
    if k in meta and not force: return meta[k]
    m={'company':company,'website':website,'status':'fail'}
    try:
        html,final,_=fetch(website)
        for kind,c in candidates(html,final)[:6]:
            try:
                if kind=='inline': im=to_png(c.encode(),'svg','x.svg'); src='inline svg'
                else:
                    d,u,ct=fetch(c); im=to_png(d,ct,u); src=c
                im=trim(im)
                if im.width<24 or im.height<12: continue
                if kind!='icon' and im.width/im.height<1.1 and im.width<120: continue
                h=96; w=int(im.width*h/im.height)
                if w>420: w=420; h=int(im.height*w/im.width)
                im=im.resize((max(1,w),max(1,h)),Image.LANCZOS)
                im.save(f'{LD}/static/{k}.png')
                m.update(status='ok' if kind!='icon' else 'icon',source=src,light=lightness(im)>215,w=im.width,h=im.height); break
            except Exception as e: m['err']=str(e)[:120]; continue
    except Exception as e: m['err']=str(e)[:120]
    meta[k]=m
    return m
if __name__=='__main__':
    for co,w in [('Neurocrine Biosciences','https://www.neurocrine.com'),('Gilead Sciences','https://www.gilead.com'),('Illumina','https://www.illumina.com'),('IDEAYA Biosciences','https://www.ideayabio.com'),('Arcturus Therapeutics','https://arcturusrx.com'),('Moderna','https://www.modernatx.com')]:
        print(get_logo(co,w,force=True))

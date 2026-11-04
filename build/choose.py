import json,os,sys,re,difflib,collections
from PIL import Image
import pytesseract
sys.path.insert(0,'/home/claude/build')
from logos import key_of
LD='/home/claude/build/logos'
pw=json.load(open(f'{LD}/meta_pw.json')); st=json.load(open(f'{LD}/meta.json'))
over=json.load(open(f'{LD}/override.json')) if os.path.exists(f'{LD}/override.json') else {}
OC=f'{LD}/ocr_cache.json'; ocache=json.load(open(OC)) if os.path.exists(OC) else {}
GEN={'inc','corp','corporation','co','llc','ltd','plc','the','holdings','holding','group','therapeutics','pharmaceuticals','pharmaceutical','pharma','biosciences','bioscience','biotherapeutics','biologics','biopharma','biotech','sciences','science','laboratories','labs','medicine','medicines','technologies','bio','and','of','company'}
def core(name):
    n=re.sub(r'\(.*?\)','',name.lower()); t=re.findall(r'[a-z0-9]+',n)
    k=[x for x in t if x not in GEN] or t
    return k
def lum(im):
    px=[p for p in im.resize((60,max(1,int(60*im.height/max(1,im.width))))).getdata() if p[3]>60]
    return sum(0.3*p[0]+0.59*p[1]+0.11*p[2] for p in px)/len(px) if px else 255
def ocr(p):
    if p in ocache: return ocache[p]
    im=Image.open(p).convert('RGBA'); L=lum(im)
    bg=Image.new('RGBA',im.size,(0,0,0,255) if L>200 else (255,255,255,255)); bg.alpha_composite(im)
    g=bg.convert('L').resize((im.width*3,im.height*3))
    try: t=pytesseract.image_to_string(g,config='--psm 6')
    except Exception: t=''
    ocache[p]=t; return t
def match(name,txt):
    t=re.sub(r'[^a-z0-9]','',txt.lower()); best=0
    for w in core(name)[:2]:
        if len(w)<3: continue
        if w in t: return 1.0
        sm=difflib.SequenceMatcher(None,w,t); m=sm.find_longest_match(0,len(w),0,len(t))
        best=max(best,m.size/len(w))
    return round(best,2)
items=json.load(open('/home/claude/build/logo_items.json'))
choice={}; review=[]
for c,_ in items:
    k=key_of(c)
    if k in over: choice[k]=over[k]; continue
    cands=[]
    for src,meta in (('pw',pw.get(k,{})),('static',st.get(k,{}))):
        p=f'{LD}/{src}/{k}.png'
        if meta.get('status')=='ok' and os.path.exists(p):
            im=Image.open(p); asp=im.width/im.height
            cands.append((match(c,ocr(p)),asp,src))
    if not cands: choice[k]='reject'; continue
    cands.sort(key=lambda x:(x[0]>=0.75, x[0], x[1]>=1.8, x[1]), reverse=True)
    m,asp,src=cands[0]
    choice[k]=src
    if m<0.75: review.append((c,k,src,m,round(asp,2)))
json.dump(choice,open(f'{LD}/choice.json','w'),indent=0); json.dump(ocache,open(OC,'w'))
json.dump(review,open(f'{LD}/needs_review.json','w'),indent=0)
print(collections.Counter(choice.values()),'needs review',len(review))

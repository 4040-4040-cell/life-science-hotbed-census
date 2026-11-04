# Render chosen logos on white (as on the site) with alternates, 36 per sheet
import json,os,sys
from PIL import Image,ImageDraw,ImageFont
LD='/home/claude/build/logos'
ch=json.load(open(f'{LD}/choice.json')); items=json.load(open('/home/claude/build/logo_items.json'))
sys.path.insert(0,'/home/claude/build'); from logos import key_of
keys=[(key_of(c),c) for c,_ in items]
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
def cell(p,bg):
    im=Image.new('RGB',(200,46),bg)
    if p and os.path.exists(p):
        lg=Image.open(p).convert('RGBA'); lg.thumbnail((190,38)); im.paste(lg,(5,4),lg)
    return im
per=36; os.makedirs('/home/claude/build/review',exist_ok=True)
for s in range(0,len(keys),per):
    chunk=keys[s:s+per]; W=4*(270+430); 
    sheet=Image.new('RGB',(2*(250+420),((len(chunk)+1)//2)*50+4),'white'); d=ImageDraw.Draw(sheet)
    for i,(k,c) in enumerate(chunk):
        col=i%2; row=i//2; x=col*670; y=row*50+2
        d.text((x+4,y+16),f'{s+i:>3} {c[:30]}',fill='black',font=f)
        c1=ch.get(k,'reject'); other='static' if c1=='pw' else 'pw'
        sheet.paste(cell(f'{LD}/{c1}/{k}.png' if c1!='reject' else None,(255,255,255) if c1!='reject' else (255,220,220)),(x+250,y))
        sheet.paste(cell(f'{LD}/{other}/{k}.png',(200,200,200)),(x+455,y))
    sheet.save(f'/home/claude/build/review/r{s:04d}.png')
print(len(keys))

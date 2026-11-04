import json,os
from PIL import Image,ImageDraw,ImageFont
LD='/home/claude/build/logos'
rv=json.load(open(f'{LD}/needs_review.json'))
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
def cell(p,bg):
    im=Image.new('RGB',(210,46),bg)
    if p and os.path.exists(p):
        lg=Image.open(p).convert('RGBA'); lg.thumbnail((200,38)); im.paste(lg,(5,4),lg)
    return im
per=40; os.makedirs('review2',exist_ok=True)
for s in range(0,len(rv),per):
    ch=rv[s:s+per]; sh=Image.new('RGB',(2*700,((len(ch)+1)//2)*50+4),'white'); d=ImageDraw.Draw(sh)
    for i,(c,k,src,m,a) in enumerate(ch):
        x=(i%2)*700; y=(i//2)*50+2
        d.text((x+4,y+16),f'{s+i:>3} {c[:32]}',fill='black',font=f)
        sh.paste(cell(f'{LD}/pw/{k}.png',(170,170,170)),(x+260,y)); sh.paste(cell(f'{LD}/static/{k}.png',(230,230,230)),(x+478,y))
    sh.save(f'review2/v{s:04d}.png')
print(len(rv))

import sys, os, json
from PIL import Image, ImageDraw, ImageFont
LD='/home/claude/build/logos'
def sheet(keys, out, cols=('static','pw')):
    rh=70; W=260*len(cols)+330
    im=Image.new('RGB',(W,rh*len(keys)+10),'white'); d=ImageDraw.Draw(im)
    try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    except: f=None
    for i,(k,label) in enumerate(keys):
        y=i*rh+5; d.text((6,y+25),f'{i:>3} {label[:38]}',fill='black',font=f)
        for j,c in enumerate(cols):
            x=330+j*260; d.rectangle([x,y,x+250,y+rh-6],fill=(150,150,150) if j%2==0 else (150,150,150))
            p=f'{LD}/{c}/{k}.png'
            if os.path.exists(p):
                lg=Image.open(p).convert('RGBA'); lg.thumbnail((240,rh-14)); im.paste(lg,(x+5,y+4),lg)
            else: d.text((x+8,y+25),'none',fill='white',font=f)
    im.save(out)
if __name__=='__main__':
    from logos import key_of
    names=['Neurocrine Biosciences','Gilead Sciences','Illumina','IDEAYA Biosciences','Arcturus Therapeutics','Moderna']
    sheet([(key_of(n),n) for n in names],'/home/claude/build/sheet_test.png')

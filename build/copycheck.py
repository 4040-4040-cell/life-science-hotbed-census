import re,glob,json,sys
BAN=['leverage','robust','streamline','holistic','delve','landscape','unlock','foster','navigate','game-changer','game changer',"it's worth noting",'it is worth noting','important to note',"in today's"]
def scan(name,text):
    hits=[]
    for w in BAN:
        for m in re.finditer(r'\b'+re.escape(w)+r'\b',text,flags=re.I): hits.append((w,text[max(0,m.start()-50):m.end()+40]))
    for m in re.finditer('—',text): hits.append(('EM DASH',text[max(0,m.start()-50):m.end()+40]))
    for m in re.finditer(r'~\s?\d',text): hits.append(('TILDE',text[max(0,m.start()-30):m.end()+30]))
    for m in re.finditer(r'lorem|TODO|TBD|xxx',text,flags=re.I): hits.append(('PLACEHOLDER',text[max(0,m.start()-30):m.end()+30]))
    return hits
for f in ['template.html','app.js','method.html','render.py','assemble.py','spec/company_profile_spec.md']:
    h=scan(f,open(f).read())
    for x in h: print(f,x)
# authored strings in data (labels from classifier, reads)
import csv
for r in csv.DictReader(open('/home/claude/census/footprint_class.csv',encoding='utf-8-sig')):
    for x in scan('fp_label',r['label']): print('fp_label',r['company'],x)
print('done')

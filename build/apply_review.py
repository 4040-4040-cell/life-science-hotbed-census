import json,sys
LD='/home/claude/build/logos'
rv=json.load(open(f'{LD}/needs_review.json'))
ov=json.load(open(f'{LD}/override.json')) if __import__('os').path.exists(f'{LD}/override.json') else {}
code={'p':'pw','s':'static','r':'reject'}
start=int(sys.argv[1]); dec=sys.argv[2]
for i,ch in enumerate(dec):
    ov[rv[start+i][1]]=code[ch]
json.dump(ov,open(f'{LD}/override.json','w'),indent=0); print(len(ov))

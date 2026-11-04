import json,glob,sys
sys.path.insert(0,'/home/claude/build')
from tiles import fetch
from concurrent.futures import ThreadPoolExecutor
keys=[]
for f in glob.glob('/home/claude/build/site/data/*.js'):
    s=open(f).read(); R=json.loads(s[s.index('=')+1:-1]); keys+=list(R['tiles'].keys())
print(len(keys),flush=True)
def go(k):
    z,x,y=map(int,k.split('/'))
    return fetch(z,x,y) is not None
with ThreadPoolExecutor(16) as ex: ok=sum(ex.map(go,keys))
print('ok',ok,'of',len(keys))

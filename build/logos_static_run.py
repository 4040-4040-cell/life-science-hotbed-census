import json,sys
sys.path.insert(0,'/home/claude/build')
import logos
from concurrent.futures import ThreadPoolExecutor
items=json.load(open(sys.argv[1]))
def f(it):
    try: logos.get_logo(it[0],it[1])
    except Exception as e: pass
with ThreadPoolExecutor(8) as ex: list(ex.map(f,items))
print('done')
json.dump(logos.meta,open(logos.META,'w'))

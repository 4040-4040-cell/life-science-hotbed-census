#!/bin/bash
# usage: g.sh URL [regex]
u="$1"; re="${2:-(NC|North Carolina)[ ,]*2[78][0-9]{3}}"
curl -sSL -m 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36" "$u" -o /tmp/w/p.html
python3 -I -c "
import re,html,sys
t=open('/tmp/w/p.html',errors='ignore').read()
t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t)
print('LEN',len(t))
for m in re.finditer(sys.argv[1],t):
    print('...',t[max(0,m.start()-160):m.end()+20])
" "$re" | head -30

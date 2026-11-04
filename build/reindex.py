# rebuild site/index.html from template + app.js, reusing the DATA already embedded (no data change)
import re,json
cur=open('site/index.html').read()
i=cur.index('const DATA=')+len('const DATA='); j=cur.index(';\n',i)
data=cur[i:j]; json.loads(data)
css=re.sub(r'url\([^)]*\)','none',open('vendor/package/dist/leaflet.css').read())
html=open('template.html').read().replace('LEAFLETCSS',css).replace('__DATA__',data).replace('__APP__',open('app.js').read())
open('site/index.html','w').write(html); print('ok',len(html))

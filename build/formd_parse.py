import json,os,time,urllib.request,xml.etree.ElementTree as ET,hashlib
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'WCLS research chad.urie@urieinvestments.com'}
hits=json.load(open('formd/hits.json')); CD='formd/xml'; os.makedirs(CD,exist_ok=True)
def get(h):
    adsh=h['adsh']; fn=f"{CD}/{adsh}.xml"
    if not os.path.exists(fn):
        u=f"https://www.sec.gov/Archives/edgar/data/{int(h['cik'])}/{adsh.replace('-','')}/primary_doc.xml"
        for i in range(3):
            try: open(fn,'wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read()); break
            except Exception: time.sleep(1.5)
        time.sleep(0.12)
    try: return h,ET.parse(fn).getroot()
    except Exception: return h,None
def t(el,path):
    x=el.find(path); return (x.text or '').strip() if x is not None and x.text else ''
rows=[]
with ThreadPoolExecutor(6) as ex:
    for h,root in ex.map(get,hits.values()):
        if root is None: continue
        iss=root.find('.//primaryIssuer'); od=root.find('.//offeringData')
        if iss is None or od is None: continue
        ind=t(od,'industryGroup/industryGroupType')
        rows.append({'adsh':h['adsh'],'cik':h['cik'],'filed':h['date'],'name':t(iss,'entityName'),'street':t(iss,'issuerAddress/street1'),'street2':t(iss,'issuerAddress/street2'),
          'city':t(iss,'issuerAddress/city'),'state':t(iss,'issuerAddress/stateOrCountry'),'zip':t(iss,'issuerAddress/zipCode'),'entity_type':t(iss,'entityType'),
          'year_inc':t(iss,'yearOfInc/value'),'industry':ind,'is_amend':t(root,'.//offeringData/typeOfFiling/newOrAmendment/isAmendment'),
          'first_sale':t(od,'typeOfFiling/dateOfFirstSale/value'),'total_offering':t(od,'offeringSalesAmounts/totalOfferingAmount'),'sold':t(od,'offeringSalesAmounts/totalAmountSold'),
          'securities':','.join(sorted({x.tag for x in (od.find('typesOfSecuritiesOffered') or [])})),'revenue_range':t(iss,'issuerSize/revenueRange') or t(od,'issuerSize/revenueRange')})
json.dump(rows,open('formd/parsed.json','w'))
import collections
print(len(rows),collections.Counter(r['industry'] for r in rows).most_common(8))

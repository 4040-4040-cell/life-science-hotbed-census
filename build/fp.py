import csv,glob,os
D=r'''0|1|70000|2025|Leased 70,000 SF in Morrisville for new manufacturing|New lease adds manufacturing and lab space.
1|-1||2025-10|Job cuts at Clayton plant; $4.1B expansion announced 2024|Only 2025-26 event is job cuts; expansion predates window.
2|1||2025-04|Won $3B Regeneron deal; Holly Springs campus doubling|Campus doubling adds manufacturing capacity.
3|1||2025|$1B Holly Springs expansion adding 370 jobs|Expansion broke ground in 2025.
4|1|700000|2026-01|New 700,000 SF fill-finish plant, investment raised to $2B|New plant under construction.
5|0|||Cumulative $1.7B RTP investment since 2020|Cumulative investment figure, no dated space change.
6|1||2025|Concord site ramping up with 900+ jobs in 2025|New site ramping capacity and headcount.
7|1||2025-07|$2B manufacturing expansion at RTP campuses|New factory and capacity expansion.
8|1|225000|2025-03|Opened 225,000 SF, $1B vaccine plant in Durham|New plant opened.
9|1|440000|2026-04|New $1.4B Durham campus, 440,000 SF phase one|New campus commitment.
10|1|56200|2026-05|New 56,200 SF API facility plus 202,000 SF upfit|New facility adds capacity.
11|1|174000|2025-11|$400M biologics plant in acquired 174,000 SF Durham building|Acquired building to operate.
12|1||2026-01|Second $2B biologics plant announced in Wilson|New plant commitment.
13|0||2024-06|Up to $530M Sanford biologics plant under construction|Approved 2024; no new 2025-26 milestone stated.
14|1||2025-03|Consolidated all gene therapy production into Sanford|Sanford gains production moved from California.
15|1||2025|Acquired Durham gene therapy plant from Resilience for $4.5M|Buyer acquiring a plant to operate.
16|1||2025|$195.4M first North American plant, 62 jobs|New plant.
17|-1|||Closing Durham pathology facility|Site closure.
18|0||2023|Opened 50,000 SF RTP site in late 2023|Event predates 2025.
19|-1|-517000|2025-12|Wilmington office buildings, 517,000 SF, put up for sale|Owned space classified held for sale.
20|-1||2026-01|Moved HQ and assigned old Gaithersburg lease to another party|Old lease handed off; consolidated footprint.
21|-1||2025-03|Sold Baltimore-Bayview plant to Syngene for $36.5M|Seller of an operating site.
22|0|||Occupies 136,016 SF in Rockville through 2034|Statement of occupancy.
23|-1||2026-07|Sold Rockville manufacturing operations to Bora for $122.5M|Seller of an operating site.
24|0|||35,000 SF Frederick HQ; small Gaithersburg lease ends 2027|Statement of occupancy.
25|-1|-39432|2026-07|Terminated 39,432 SF, cutting Beltsville space to 29,864 SF|Lease terminated, premises shrunk.
26|0|||43,462 SF Washington HQ, leases expire 2026 to 2028|Statement of occupancy.
27|0|||Owns 415,000 SF Silver Spring campus|Statement of occupancy.
28|0|||61,048 SF Germantown lab and manufacturing|Statement of occupancy.
29|0||2025-10|Extended Vienna office lease to 2031|Extension of same space.
30|1||2025-11|$2B Maryland plan adds Gaithersburg clinical supply facility|New facility and 300 jobs.
31|1||2025-11|Expanding Frederick biologics plant under $2B Maryland plan|Plant expansion.
32|1||2026-10|Broke ground on $5B Goochland plant, 650 jobs|Groundbreaking on new plant.
33|1||2026-07|Acquired MacroGenics Rockville plant for $122.5M|Buyer acquiring a plant to operate.
34|1||2025-03|Acquired Emergent Baltimore plant for $36.5M|Buyer acquiring a plant to operate.
35|0||2026|Raised about $92.7M Series B|Financing news, no space content.
36|1||2025-09|Moving HQ to 82,451 SF at Cortex, tripling footprint|Relocating into more space.
37|1||2026-07|HQ moved to Blue Ash; $750M Ohio expansion, 400 jobs|HQ relocation in and capacity expansion.
38|1||2026|New fill-finish line at 580,000 SF West Chester plant|New production line adds capacity.
39|1||2025-05|Up to $550M Indianapolis expansion with new CGM plant|New manufacturing facility.
40|-1||2026-03|400 layoffs at Bloomington plant|Site layoffs.
41|1|300000|2025-07|$250M expansion plus new 300,000 SF Indiana site|Expansion and site purchase.
42|0||2026-07|$100M over five years to modernize Tippecanoe Labs|Modernization, no space change.
43|1||2026-03|$1.5B Kankakee expansion, 300+ jobs, after 2025 job cuts|Expansion outweighs earlier job cuts.
44|1||2025-07|$45M Madison expansion, about 200 jobs|Expansion.
45|0||2024-05|$3M Germantown ADC investment in 2024|Event predates 2025.
46|1|418000|2025-04|$900M expansion with new 418,000 SF facility|New facility.
47|1|||$76M St. Louis expansion, 170 jobs|Expansion adds capacity and jobs.
48|1|||$64.5M Kalamazoo and Portage investment, 45 jobs|Capacity investment adding jobs.
49|1||2026-05|Opened Lebanon advanced therapies site; $4.5B more announced|New site opened and further expansion.
50|-1||2025-08|Exact Sciences cut about 200 Wisconsin jobs; Abbott acquired company|Site-linked job cuts; ownership change neutral.
51|0||2022|No 2025-26 event; expansion announced 2022|Event predates 2025.
52|0|||Portal holds 58,000 SF at Fulton Labs campus|Portal's own space unchanged; activity is other tenants.
53|1||2026-04|Up to $263M DOE loan to finish Janesville plant|Financing tied to completing a new plant.
54|1||2025-08|$195M API expansion at North Chicago, 50+ jobs|Expansion.
55|0||2026-05|Planned Indiana capital above $21B since 2020|Cumulative investment figure, no specific space change.
56|1||2025|New HPAPI suite in Riverview, $90M US investment|New production capacity.
57|1|175000|2026-05|Opened 175,000 SF Madison HQ and manufacturing site|New facility opened.
58|0|||Added 22,000 SF office; subleased out inherited 22,365 SF|Added and subleased space roughly offset.
59|0|||Occupies 65,818 SF in Brisbane|Statement of occupancy.
60|0|||Subleased out 50,000 SF Brisbane in 2023 and 2024|Sublease predates 2025.
61|-1|-26000||Subleasing out 26,000 SF of Redwood City space|Space subleased out to others.
62|1|40884|2025-12|Added 40,884 SF in Redwood City via expansion option|Expansion option exercised.
63|0|||234,892 SF at 350 Oyster Point through 2033|Statement of occupancy.
64|-1|-40000|2025-11|Moving HQ from 76,000 SF to 36,000 SF in Emeryville|Relocating into less space.
65|1||2026-03|Expanding 5000 Shoreline Ct to 80,196 SF|Lease expansion.
66|0|||108,000 SF SSF HQ through 2031|Statement of occupancy.
67|1|19430|2026|Added 19,430 SF to Foster City HQ|Lease expansion.
68|0|||195,888 SF Brisbane lease through 2031|Statement of occupancy.
69|1|38176|2026|New 38,176 SF HQ lease in South San Francisco|New HQ lease; prior space size not stated.
70|-1||2025|Evaluating sublease of part of 100,904 SF HQ|Signalling sublease after restructuring.
71|0|||60,600 SF Newark lease through 2029|Statement of occupancy.
72|0|||57,000 SF across Fremont and San Jose|Statement of occupancy.
73|0|||44,819 SF at 250 East Grand Ave|Statement of occupancy.
74|0|||91,000 SF Emeryville, leases expire 2026 to 2030|Statement of occupancy.
75|0|||105,000 SF SSF office and lab|Statement of occupancy.
76|0|||130,000 SF SSF HQ through 2032|Statement of occupancy.
77|0|||71,735 SF Berkeley lab and office|Statement of occupancy.
78|0|||148,020 SF SSF HQ through 2029|Statement of occupancy.
79|0||2025|Holds 610,000 SF in Alameda; exited Philadelphia-area space|Reduction was outside this region.
80|0||2024-12|Took 16,731 SF San Carlos sublease in Dec 2024|Event predates 2025.
81|0|||25,900 SF Redwood City HQ, renewal option pending|Statement of occupancy.
82|0|||Subleases 75,662 SF in Emeryville|Statement of occupancy, no date.
83|0|||293,906 SF leased in Redwood City|Statement of occupancy.
84|-1|-18400||Subleasing out 18,400 SF of SSF HQ; merger pending|Space subleased out to others.
85|0|||115,466 SF SSF HQ|Statement of occupancy.
86|0|||32,370 SF SSF HQ plus Union City plant|Statement of occupancy.
87|1|46217|2026|Additional 46,217 SF commencing at San Carlos HQ|New space commencing.
88|0|||133,896 SF Mission Bay HQ through 2033|Statement of occupancy.
89|0|||Owns 148,000 SF and leases 300,000 SF in Pleasanton|Statement of occupancy.
90|0|||99,000 SF Fremont HQ through 2029|Statement of occupancy.
91|0|||180,200 SF Menlo Park HQ through 2034|Statement of occupancy.
92|0|||New 220,000 SF lab lease in Austin, not Bay Area|Expansion is outside this region.
93|0|||88,000 SF across Brisbane HQ and lab|Statement of occupancy.
94|0||2026-09|Relocating HQ from Menlo Park to Sunnyvale|Relocation within region; new size not stated.
95|0|||249,500 SF Palo Alto HQ plus other sites|Statement of occupancy.
96|0||2026-10|100,000 SF Fremont HQ; going-private deal pending|Corporate transaction, no space change.
97|0|||65,700 SF SSF office and lab|Statement of occupancy.
98|0|||77,300 SF Redwood City office and lab|Statement of occupancy.
99|1||2025-07|$3B to $5B SSF campus overhaul, 1M SF new labs|Major lab build outweighs 143 layoffs.
100|-1||2025-11|Ended Calico collaboration, about 100 chemists affected|Program end cuts research staff.
101|-1|||Emeryville research moving to new San Diego center|Consolidating out of the Bay Area.
102|0||2026-02|Waters completed combination with BD Biosciences|Ownership change, no space change.
103|1|40700|2025-01|Leased 40,700 SF more in San Carlos|New lease for added space.
104|-1||2025-11|AbbVie ended collaboration, about 100 chemists affected|Loss of partner funding cuts staff.
105|1|7400||Subleases 7,400 SF of Senti's SSF space|Taking sublease space as subtenant.
106|0||2026-06|Series D reached $327M; plants in New Jersey and Netherlands|Financing; expansion outside region.
107|0||2024-12|HQ moved to Gateway of Pacific III in Dec 2024|Event predates 2025.
108|-1||2025-05|Cut about 65 roles, 22% of staff|Workforce cut above 20%.
109|0||2026-01|Adding East Coast manufacturing capacity|Expansion is outside this region.
110|0|||67,000 SF San Diego office through 2031|Statement of occupancy.
111|0|||43,234 SF leased through 2032|Statement of occupancy.
112|0|||9,254 SF HQ office|Statement of occupancy.
113|1|22000|2025|Added 22,000 SF to San Diego HQ|Lease expansion.
114|0|||78,000 SF HQ through 2032|Statement of occupancy.
115|0|||18,421 SF HQ through 2029|Statement of occupancy.
116|0|||32,512 SF San Diego HQ through 2033|Statement of occupancy.
117|-1|-26455|2025-01|Subleased out 26,455 SF of San Diego HQ|Space subleased out to others.
118|0|||7,940 SF HQ plus 6,307 SF subleased|Statement of occupancy, no date.
119|-1||2025|Completed strategic restructuring in 2025|Restructuring signals reduction; scale not stated.
120|0|||316,531 SF HQ plus Carlsbad and Waples sites|Statement of occupancy.
121|0|||200,000 SF HQ through 2036|Statement of occupancy.
122|0|||196,000 SF leased across all sites|Statement of occupancy.
123|1|||535,000 SF HQ; marketing former HQ space for sublease|New HQ far exceeds space offered for sublease.
124|-1||2025-07|Cut about 34 jobs|Workforce reduction.
125|0|||Owns 26,800 SF Carlsbad plant plus 25,800 SF leased|Statement of occupancy.
126|0|||27,000 SF Vista HQ plus 28,000 SF Carlsbad sublease|Statement of occupancy.
127|1|59626|2024-12|Signed 59,626 SF lease to relocate Irvine HQ|New larger HQ; move falls in window.
128|1||2025-10|Added HQ expansion space; HQ now 30,716 SF|Expansion space commenced.
129|0|||49,000 SF Pasadena HQ|Statement of occupancy.
130|-1||2025-10|Cut about 30% of staff|Workforce cut above 20%.
131|0|||22,643 SF HQ office|Statement of occupancy.
132|0|||144,000 SF San Diego lease through 2038|Statement of occupancy.
133|1|82514|2025-09|Opened 82,514 SF Gateway Labs in Torrey Pines|New lab space opened.
134|1|427000|2026|Consolidating San Diego R&D into 427,000 SF Campus Point lease|New large lease commitment.
135|-1||2026|Sold 500,000+ SF campus, moving to 230,000 SF lease|Relocating into less space plus layoffs.
136|1|466000|2026-02|Building 466,000 SF San Diego research hub|New research hub under construction.
137|1|10000||Opened 10,000 SF Carlsbad radioligand plant|New plant opened.
138|1||2025|New Oceanside biologics facility operational early 2025|New production facility.
139|0||2026-07|Vertex acquired Crinetics; 94,000 SF HQ|Ownership change, no space change.
140|0||2025|Merck acquired Cidara|Ownership change, no space change.
141|1|5999|2026-08|Adding 5,999 SF to San Diego HQ|Lease expansion.
142|1||2026-01|Named tenant at Torrey Heights campus|New lease implied.
143|-1|||85 layoffs at Carlsbad operations|Site layoffs.
144|-1|||85 layoffs in Allergan Aesthetics workforce|Site layoffs.
145|-1||2026|Sold program and transferred staff; headcount 146 to 127|Program sale cuts staff.
146|0||2026-06|Extended 14,790 SF Boulder HQ lease|Extension of same space.
147|0||2024-07|Nearly $500M Boulder expansion announced 2024|Announcement predates 2025.
148|1|64000|2026-03|15-year lease of 64,000 SF building in Boulder|New full-building lease.
149|1|275000|2026|$725M expansion adding 275,000 SF in Frederick|Expansion adds space.
150|0||2026-01|Illumina acquired SomaLogic|Ownership change, no space change.
151|1|100000|2026-09|Leased 100,000 SF in Boulder for manufacturing|New lease.
152|1|31465|2026-03|Leased 31,465 SF in Boulder|New lease.
153|-1||2026-06|HQ moved to California; Boulder lease renewal undecided|HQ moved out of region.
154|1|7407|2025-07|Subleased 7,407 SF in Cambridge|Taking sublease space as subtenant.
155|1|43474|2026-01|Signed 43,474 SF Waltham lease to move HQ|New HQ lease; prior space size not stated.
156|-1||2025-03|New 580,000 SF Cambridge HQ; MA footprint cut 40%|Net plan cuts footprint about 40%.
157|1|51726|2025|Leased 51,726 SF of lab in Cambridge|New lease.
158|0|||50,678 SF Stoughton HQ|Statement of occupancy.
159|0||2026-05|Renewed 36,000 SF Norwood lease|Renewal of same space.
160|0|||68,000 SF Waltham office and lab|Statement of occupancy.
161|0|||59,783 SF Cambridge through 2028|Statement of occupancy.
162|0|||81,229 SF Boston HQ|Statement of occupancy.
163|-1||2026-10|Plans to cut workforce in half|Workforce cut above 20%.
164|-1||2026-10|Cut about 40% of staff after 2025 Watertown lease|Latest event is large workforce cut.
165|1|74537|2025|Leased 74,537 SF of lab in Andover|New lease.
166|-1|-259000|2026-02|196,000 SF offered for sublease; 63,000 SF Cambridge leases ended|Sublease listing and lease exits.
167|1|147000|2025|Leased 147,000 SF in Cambridge; old HQ lease expiring|New lease far exceeds space given up.
168|-1||2026|Massachusetts headcount fell from 4,434 to 3,042|Headcount down about 31%.
169|1|24000|2026-01|Subleased 24,000 SF in Bedford as future HQ|Taking sublease space as subtenant.
170|0||2026-02|Sublease expired; same space under license to 2027|Same space held on new terms.
171|0|||149,000 SF Cambridge plus 48,500 SF Watertown|Statement of occupancy.
172|-1|||Subleasing out unused Bedford and Marlborough space|Space vacated and subleased out.
173|0|||33,339 SF Lexington sublease plus 67,663 SF Lowell|Statement of occupancy.
174|0|||18,712 SF Woburn HQ plus 63,000 SF Framingham|Statement of occupancy.
175|0||2025-08|HQ lease extended about two years|Extension of same space.
176|0|||164,587 SF across two Waltham buildings|Statement of occupancy.
177|0|||Boston HQ leases extended to 2044; Leiden II under construction|Extension predates 2025; build has no dated milestone.
178|1||2025-09|Added expansion space in Waltham building|Lease expansion.
179|0|||44,000 SF Cambridge plus 90,000 SF Lexington|Statement of occupancy.
180|0|||30,305 SF Waltham HQ|Statement of occupancy.
181|-1|-630153|2026-02|Put 630,153 SF on sublease market in Cambridge|Net Cambridge footprint shrinking despite new building.
182|-1||2026|Repurposing Lexington cell therapy plant after exit|Exited program at site with layoffs.
183|0||2026-07|Extended 900,000 SF Cambridge Crossing lease early|Extension of same space.
184|1|171224|2025|Leased 171,224 SF of lab across two Waltham leases|New leases; headcount rising.
185|1|570000|2026-10|Opened 570,000 SF R&D centre in Cambridge|New building opened.
186|1|75000|2025-10|Added 75,000 SF at 645 Summer St, Boston|Expansion into more space.
187|0|||722,000 SF Norwood campus|Statement of occupancy.
188|1|23000|2026-05|Building 110,000 SF Waltham facility, up from 87,000 SF|Moving into more space.
189|1|103800|2025|Leased 103,800 SF of manufacturing in Lexington|New lease.
190|1|235000|2025-10|Leased 235,000 SF at Alewife Park, Cambridge|New lease.
191|1|11200|2025-01|Added 11,200 SF in New Haven|Expansion; termination was 2024.
192|-1|-2858|2026|Cut 2,858 SF in lease amendment|Lease shrunk.
193|0||2025-10|Owns 328,000 SF Danbury campus; acquired scPharmaceuticals|Acquisition, no space change in region.
194|1|33000|2026-01|Leased 33,000 SF in New Haven for HQ move|HQ relocating into region.
195|-1|-67000|2025|Ended 67,000 SF New Haven lease; new lease in San Diego|Exited regional lease; growth is elsewhere.
196|-1||2026|718 job cuts in Lawrence Twp and Princeton|Site layoffs.
197|1|||Expanded Bridgewater lab lease to 46,671 SF|Lease expansion.
198|-1||2026-12|88 layoffs in New Brunswick|Site layoffs.
199|0||2024-09|Subleases 17,406 SF in Princeton and Hopewell|Statement of occupancy; started 2024.
200|0|||103,000 SF Bridgewater lab and office|Statement of occupancy.
201|1|73000|2026-06|Doubled Hampton space; new 40,400 SF New Haven lease|Expansion and new lease in region.
202|0||2026-07|New 11,232 SF lease in Waltham, Massachusetts|Expansion is outside this region.
203|1|4600|2025-11|Added 4,600 SF to NYC office|Lease expansion.
204|-1|-33300|2025|Seeking subtenant for 33,300 SF lab and office|Space put on sublease market.
205|1|10663|2026|Moving NYC HQ to 18,563 SF from 7,900 SF|Relocating into more space.
206|0|||Developing 1M SF Saratoga site; Tarrytown expansion ongoing|Projects predate 2025; no new milestone.
207|0|||136,047 SF NYC office through 2037|Statement of occupancy.
208|-1|-4000|2025-08|Gave up 4,000 SF NYC office at expiry|Space exited.
209|1|11588|2026-03|Added 11,588 SF in NYC, now 27,400 SF|Lease expansion.
210|0|||10,000 SF NYC HQ through 2028|Statement of occupancy.
211|0|||18,000 SF Queensbury site; new Ireland space|Regional lease from 2024; new space abroad.
212|-1|-25000|2026|Subleased out 25,000 SF of Plymouth Meeting HQ|Space subleased out to others.
213|0||2026-10|Moving to acquire Pacira BioSciences|Corporate transaction, no space change.
214|0|||Philadelphia leases expire 2026; decision pending|Statement of occupancy.
215|-1|-31734|2026-06|Surrendered 31,734 SF floor in Philadelphia|Lease shrunk.
216|0|||67,000 SF Pittsburgh lab and office|Statement of occupancy.
217|0|||19,370 SF Radnor lease through 2034|Statement of occupancy.
218|1||2026-10|$2.9B Montgomery County expansion incl. new R&D facility|New facility and expansion.
219|-1||2026|806 NJ layoffs in 2025, 718 more in 2026|Large site layoffs.
220|1|260000|2026|260,000 SF Pearl River R&D facility due early 2026|New facility completing in window.
221|0|||Developing 1M SF Saratoga Springs site acquired 2024|Acquisition predates 2025; no new milestone.
222|-1||2026-07|Multiple 2026 layoff rounds at East Hanover HQ|Site layoffs.
223|1||2025-09|New biologics factory at Upper Merion|New plant.
224|0||2025|Opened 260,000 SF Morristown office; exited Bridgewater campus|Relocation within NJ; net size change not stated.
225|-1||2025-12|263 layoffs at Plainsboro HQ|Site layoffs.
226|-1||2025|Laid off 337 of 647 Spark staff|Workforce cut above 20%.
227|1|||Opened $100M New Jersey manufacturing expansion|Expansion opened.
228|-1||2025-08|$44.6M impairment on 79,565 SF Bothell plant|Shifting to outsourcing, idling plant.
229|0|||106,949 SF Seattle lease through 2027|Statement of occupancy.
230|0|||53,000 SF Bothell lease through 2033|Statement of occupancy.
231|0||2026-09|Raised $116M Series A; no lease yet|Financing news, no space content.
232|-1||2025-08|About 100 layoffs at Bothell campus|Site layoffs.
233|1|37575|2026-03|Added 37,575 SF in Bothell|Expansion.
234|0||2026-10|Repligen acquired BioLife; 75,241 SF Bothell site|Ownership change, no space change.
235|0||2025-11|QIAGEN acquiring Parse Biosciences|Ownership change, no space change.
236|1|160000|2026-01|160,000 SF fill-finish line due 2026; new allergens building|Capacity expansion.
237|1|124000|2025|Preleased 124,000 SF at 1916 Boren|New lease.'''
cls={}
for line in D.split('\n'):
    p=line.split('|'); cls[int(p[0])]=p[1:]
rows=[];i=0
for f in sorted(glob.glob('/home/claude/census/*.csv')):
    b=os.path.basename(f)
    if b in('websites_existing.csv','footprint_class.csv') or b.endswith('_overflow.csv'): continue
    slug=b[:-4]
    if slug.endswith('_add'): slug=slug[:-4]
    for x in csv.DictReader(open(f,encoding='utf-8')):
        if (x.get('footprint_event_2025_26') or '').strip():
            d,sf,m,lab,rs=cls[i]
            assert len(lab.split())<=12,(i,lab); assert len(rs.split())<=15,(i,rs)
            assert '—' not in lab+rs
            rows.append([slug,x['company'],d,sf,m,lab,rs]); i+=1
assert i==len(cls)==238
with open('/home/claude/census/footprint_class.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(['region_slug','company','dir','sf_change','event_month','label','reason']); w.writerows(rows)
from collections import Counter
c=Counter((r[0],r[2]) for r in rows)
for s in sorted({r[0] for r in rows}): print(s, {k:c[(s,k)] for k in('1','0','-1')})
print(Counter(r[2] for r in rows))

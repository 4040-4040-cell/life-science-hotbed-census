const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=(v,d=0)=>v==null||v===''||isNaN(v)?'':Number(v).toLocaleString('en-US',{maximumFractionDigits:d,minimumFractionDigits:d});
const logoImg=(r,cls)=>{const L=(window.REGION[r._slug]||{}).logos||{}; const u=L[r.logo]; if(!u) return ''; return `<img class="${cls}${r.logo_light?' lt':''}" src="${u}" alt="${esc(r.company)} logo">`;};
const link=(r,inner)=>r.web?`<a href="${esc(r.web)}" target="_blank" rel="noopener">${inner}</a>`:inner;
const TC={A:'var(--accent)',B:'var(--tierB)',C:'var(--tierC)',Site:'#7C93A6',Anchor:'var(--anchor)'};
const TCH={A:'#C4122F',B:'#2B2F35',C:'#A9A49B',Site:'#7C93A6',Anchor:'#2F6B8A'};
$('#h1').textContent=DATA.title; $('#sub').textContent=DATA.subtitle; $('#method').innerHTML=DATA.method;
const views={};
function navBuild(){
  const items=[{slug:'compare',name:'Compare regions'},...DATA.regions];
  $('#nav').innerHTML=items.map(r=>`<a href="#${r.slug}" data-v="${r.slug}">${esc(r.name)}</a>`).join('');
}
function compareView(){
  const v=document.createElement('section'); v.className='view'; v.id='v-compare';
  const rows=DATA.compare;
  v.innerHTML=`<div class="pmast"><span class="kick">Life science hotbed census</span><b>All markets</b><span class="pno">${DATA.compare.length} hubs plus 2 Basel canton views · US and UK company data as of October 28, 2026; Basel as of November 2, 2026</span></div><h2>${esc(DATA.compare_headline)}</h2>
  <p class="hsub">${esc(DATA.subtitle)}</p>
  <div class="tablewrap" style="max-height:none"><table class="compare"><thead><tr>
  <th>Region</th><th class="num">Companies headquartered</th><th class="num">Tier A</th><th class="num">Tier B</th><th class="num">Tier C</th>
  <th class="num">Publicly listed</th><th class="num">Public cash, $M</th><th class="num">Private capital raised, $M</th><th class="num">Commercial-stage</th>
  <th class="num">Sites of outside companies</th><th class="num">Expansion events</th><th class="num">Contraction events</th><th>Most company HQs</th></tr></thead><tbody>
  ${rows.map(r=>`<tr data-go="${r.slug}"><td class="co">${esc(r.name)}<small>${esc(r.geo)}</small></td>
  <td class="num">${r.n}</td><td class="num"><b>${r.A}</b></td><td class="num">${r.B}</td><td class="num">${r.C}</td>
  <td class="num">${r.pub}</td><td class="num">${r.liq==null?'n/a':fmt(r.liq)}</td><td class="num">${fmt(r.raised)}</td><td class="num">${r.comm}</td>
  <td class="num">${r.sites}</td><td class="num">${r.exp}</td><td class="num">${r.con}</td><td>${esc(r.top_sub)}</td></tr>`).join('')}
  </tbody></table></div>
  <div class="note">${DATA.compare_note}</div>
  <section class="pindex"><h3>Markets in this set</h3><ol>${DATA.regions.map((r,i)=>`<li><b>${esc(r.name)}</b>${/^basel-/.test(r.slug)?' <em>(canton detail, not in hub totals)</em>':''}<span>page ${i+2}</span></li>`).join('')}</ol>
  <p class="pfoot">Counts follow a fixed inclusion rule (exchange-listed, funded private, 100+ regional staff, approved product, major site of a pharma, tools or CDMO company, anchor institution, $10M+ raised since 2023) and are floors, not a full census. Public liquidity: cash plus marketable securities from the latest SEC filing, companies headquartered in the hub; n/a where most listed companies do not file with the SEC. Private capital: company releases and SEC Form D, a floor. Events: 2025 to 2026 footprint events in filings and releases. Tier scores are an analyst weighting (scale 25%, capital 20%, cash durability 20%, stage 20%, momentum 15%).</p></section>`;
  v.querySelectorAll('tr[data-go]').forEach(tr=>tr.onclick=()=>location.hash=tr.dataset.go);
  $('#main').appendChild(v); views.compare={el:v};
}
window.REGION={};
function loadRegion(slug,cb){
  if(window.REGION[slug]) return cb();
  const s=document.createElement('script'); s.src=`data/${slug}.js`; s.onload=cb;
  s.onerror=()=>{views[slug].el.innerHTML='<p class="note">This region failed to load. Reload the page to try again.</p>';};
  document.head.appendChild(s);
}
function tileLayer(slug){
  const T=(window.REGION[slug]||{}).tiles||{};
  const L2=L.GridLayer.extend({createTile(c){const k=`${c.z}/${c.x}/${c.y}`;
    const el=document.createElement(T[k]?'img':'div'); if(T[k]){el.src=T[k];el.alt='';} return el;}});
  return new L2({attribution:'Imagery and labels: Esri, Maxar, Earthstar Geographics, USDA, USGS',minZoom:DATA.zmin[slug],maxZoom:DATA.zmax[slug]});
}
function regionShell(meta){
  const v=document.createElement('section'); v.className='view'; v.id='v-'+meta.slug;
  v.innerHTML=`<h2>${esc(meta.name)}</h2><p class="note">Loading ${esc(meta.name)}…</p>`;
  $('#main').appendChild(v); views[meta.slug]={el:v,init:false,shell:true};
}
function trimEv(t){t=String(t||''); if(t.length<=115) return t; const i=t.lastIndexOf('; ',115); return i>40?t.slice(0,i):t.slice(0,t.lastIndexOf(' ',112))+' …';}
function finding(R){
  const ne=R.rows.filter(r=>r.footprint_dir>0).length, nc=R.rows.filter(r=>r.footprint_dir<0).length;
  const ab=r=>Math.abs(+r.fp_sf||0);
  const big=d=>R.rows.filter(r=>r.footprint_dir===d&&r.footprint).sort((a,b)=>ab(b)-ab(a))[0];
  const e=big(1), c=big(-1); const parts=[`${R.name}: ${ne} expansion and ${nc} contraction events in 2025 to 2026`];
  const cut=t=>{t=String(t||'').replace(/\s*\(.*?\)\s*/g,' ').trim(); if(t.length<=64) return t; const m=Math.max(t.lastIndexOf(': ',62),t.lastIndexOf('; ',62),t.lastIndexOf(', ',62)); return m>24?t.slice(0,m):t.slice(0,t.lastIndexOf(' ',60));};
  const nm=r=>String(r.short||r.company).replace(/\s*\(.*?\)\s*$/,'');
  if(e) parts.push(`Largest expansion: ${nm(e)}, ${cut(e.footprint)}`);
  if(c) parts.push(`Largest give-back: ${nm(c)}, ${cut(c.footprint)}`);
  return parts.join('. ')+'.';
}
const TESTS={T1:'exchange-listed and headquartered here',T2:'private with $100M+ raised, or $50M+ since October 2023',T3:'100+ staff in the region',T4:'has an approved product',T5:'major site of a pharma, tools or CDMO company',T6:'anchor institution',T7:'$10M+ raised in SEC Form D offerings since 2023',T8:'verified life-science operating address in the canton'};
function whyListed(t){const k=String(t||'').split(/[;,\s]+/).filter(Boolean); const out=k.map(x=>TESTS[x.trim()]).filter(Boolean); return out.length?out.join('; '):'see method';}
function campusPop(c){return `<b>${esc(c.campus)}${c.building?' · '+esc(c.building):''}</b><br>${esc(c.street||'')} ${esc(c.city||'')}<br>${esc(c.status||'')}${c.year_delivered_or_due?' · '+esc(c.year_delivered_or_due):''}${c.size_m2?' · '+fmt(+c.size_m2)+' m2 '+esc(c.size_basis||''):''}${c.available_m2?'<br>Available: '+fmt(+c.available_m2)+' m2':''}${c.anchor_tenants?'<br>Anchors: '+esc(c.anchor_tenants):''}${c.source_url?`<br><a href="${esc(c.source_url)}" target="_blank" rel="noopener">source</a>`:''}`;}
function campusHTML(R){
  const C=(R.campuses||[]); if(!C.length) return '';
  const st=c=>/for lease|vacat/i.test(c.status)?0:/construction/i.test(c.status)?1:/planned/i.test(c.status)?2:3;
  const rows=C.slice().sort((a,b)=>st(a)-st(b)||(+b.available_m2||0)-(+a.available_m2||0)||(+b.size_m2||0)-(+a.size_m2||0)||a.campus.localeCompare(b.campus));
  const fl=c=>c.size_m2&&!/site area|floor plate/i.test(c.size_basis||'');
  const pipeC=C.filter(c=>/construction|planned/.test(c.status)), pipe=pipeC.filter(fl).reduce((t,c)=>t+(+c.size_m2),0);
  const avC=C.filter(c=>+c.available_m2>0), avail=avC.reduce((t,c)=>t+(+c.available_m2||0),0);
  return `<section class="campus"><h3>Campuses, buildings and space pipeline</h3>
  <p class="flag">${C.length} campuses and buildings. ${pipeC.length} are under construction or planned; those with a published floor area sum to ${fmt(pipe)} m2 (mixed bases: gross, usable or building area, so indicative only; site areas excluded). ${avC.length} state available space, ${fmt(avail)} m2 in total. Each size is shown on the basis its source uses. On the map, grey squares are operating buildings and outlined squares are pipeline.</p>
  <p class="mkt"><b>Supply against demand.</b> JLL Research models life sciences lab take-up for the whole Basel market at 10,000 to 15,000 m2 a year (EMEA 2026 Life Sciences Industry &amp; Cluster Report). The ${fmt(avail)} m2 stated as available in ${esc(R.name)} alone equals ${(avail/15000).toFixed(1)} to ${(avail/10000).toFixed(1)} years of that take-up${pipe?`, before the ${fmt(pipe)} m2 of published pipeline floor area`:''}. Bases differ by source (usable, listed, lab or office), so treat this as an order of magnitude.</p>
  <div class="tablewrap" style="max-height:520px"><table class="ctab"><thead><tr><th>Campus</th><th>Building</th><th>Owner or developer</th><th>Use</th><th>Status</th><th>Year</th><th class="num">Size, m2</th><th>Basis</th><th class="num">Available, m2</th><th>Anchor tenants</th><th>Source</th></tr></thead><tbody>
  ${rows.map(c=>`<tr><td class="co">${esc(c.campus)}</td><td>${esc(c.building)}</td><td>${esc(c.owner_developer)}</td><td>${esc(c.use_type)}</td><td>${esc(c.status)}</td><td>${esc(c.year_delivered_or_due)}</td><td class="num">${c.size_m2?fmt(+c.size_m2):''}</td><td class="flag">${esc(c.size_basis)}</td><td class="num">${c.available_m2?fmt(+c.available_m2):''}</td><td>${esc(c.anchor_tenants)}</td><td>${c.source_url?`<a href="${esc(c.source_url)}" target="_blank" rel="noopener">link</a>`:''}</td></tr>`).join('')}
  </tbody></table></div></section>`;
}
function asOf(slug){return /^basel/.test(slug)?'Data as of November 2, 2026':'Company data as of October 28, 2026; SEC figures from the latest filing, through November 4, 2026';}
function printSheet(R,scored,cnt){
  const S=(R.snaps||[]).slice().sort((a,b)=>(b.core-a.core)||(b.n-a.n));
  const core=S.filter(s=>s.core).slice(0,(R.campuses||[]).length?6:8), rest=S.filter(s=>!core.includes(s));
  const sum=(a,k)=>a.reduce((t,s)=>t+(+s[k]||0),0);
  const money=v=>v?fmt(v):'n/a';
  const row=s=>`<tr><td class="co">${esc(s.zone)}</td><td class="num">${s.A+s.B+s.C}</td><td class="num">${s.A} / ${s.B} / ${s.C}</td><td class="num">${s.sites||0}</td><td class="num">${money(s.cash)}</td><td class="num">${money(s.raised)}</td><td class="num">${(s.exp||[]).length} / ${(s.con||[]).length}</td><td class="num">${s.reads.exp} / ${s.reads.con}</td><td>${esc((s.top||[]).slice(0,4).join(', '))}</td></tr>`;
  const restRow=rest.length?`<tr class="rest"><td class="co">Elsewhere (${rest.length} areas)</td><td class="num">${sum(rest,'A')+sum(rest,'B')+sum(rest,'C')}</td><td class="num">${sum(rest,'A')} / ${sum(rest,'B')} / ${sum(rest,'C')}</td><td class="num">${sum(rest,'sites')}</td><td class="num">${money(sum(rest,'cash'))}</td><td class="num">${money(sum(rest,'raised'))}</td><td class="num">${rest.reduce((t,s)=>t+(s.exp||[]).length,0)} / ${rest.reduce((t,s)=>t+(s.con||[]).length,0)}</td><td class="num">${rest.reduce((t,s)=>t+s.reads.exp,0)} / ${rest.reduce((t,s)=>t+s.reads.con,0)}</td><td>${esc(rest.slice(0,4).map(s=>s.zone).join(', '))}</td></tr>`:'';
  const big=r=>/SF|m2|\$|CHF|£|€|jobs|roles/.test(r.footprint)?0:1; const tr={A:0,Site:1,B:2,C:3,Anchor:4};
  const srt=(a,b)=>big(a)-big(b)||(tr[a.tier]??5)-(tr[b.tier]??5)||(b.score||0)-(a.score||0);
  const up=R.rows.filter(r=>r.footprint_dir>0&&r.footprint).sort(srt), dn=R.rows.filter(r=>r.footprint_dir<0&&r.footprint).sort(srt);
  const ev=[...up.slice(0,Math.max(3,6-Math.min(3,dn.length))),...dn.slice(0,Math.max(3,6-Math.min(3,up.length)))].slice(0,6);
  const rd=k=>R.rows.filter(r=>r.tier!=='Anchor'&&(r.read||'')===k).length;
  return `<section class="psheet" aria-hidden="true">
  <div class="pkpis"><div><b>${scored.length}</b><span>companies headquartered here</span></div><div class="hot"><b>${cnt('A')}</b><span>Tier A, the strongest</span></div><div><b>${cnt('B')} / ${cnt('C')}</b><span>Tier B / Tier C</span></div><div><b>${cnt('Site')}</b><span>sites of outside companies</span></div><div><b>${scored.filter(r=>r.ticker).length}</b><span>publicly listed</span></div><div><b>${R.rows.filter(r=>r.footprint_dir>0).length} / ${R.rows.filter(r=>r.footprint_dir<0).length}</b><span>expansions / contractions, 2025 to 2026</span></div></div>
  <div class="preads"><div><b>${rd('Expansion candidate')}</b><span>likely to need more space</span></div><div class="hot"><b>${rd('Contraction risk')}</b><span>at risk of giving space back</span></div>${(()=>{const up=R.rows.filter(r=>r.footprint_dir>0).reduce((t,r)=>t+Math.abs(+r.fp_sf||0),0), dn=R.rows.filter(r=>r.footprint_dir<0).reduce((t,r)=>t+Math.abs(+r.fp_sf||0),0); const m=/^basel/.test(R.slug); const f=v=>m?fmt(Math.round(v/10.764))+' m2':fmt(v)+' SF'; return `<div><b>${f(up)}</b><span>space added where a size is stated</span></div><div class="hot"><b>${f(dn)}</b><span>space given back where a size is stated</span></div>`;})()}</div>
  <div class="pgrid"><table class="ptab"><thead><tr><th>Submarket</th><th class="num">HQs</th><th class="num">Tier A / B / C</th><th class="num">Outside sites</th><th class="num">Public cash, $M</th><th class="num">Private raised, $M</th><th class="num">Expansions / contractions</th><th class="num">Exp cand. / con risk</th><th>Highest-scored companies</th></tr></thead><tbody>${core.map(row).join('')}${restRow}</tbody></table>
  ${(R.campuses||[]).length?`<div class="pev ppipe"><h4>Space pipeline and availability <span class="lg">size basis as published</span></h4><p class="pmk">${(()=>{const av=(R.campuses||[]).reduce((t,c)=>t+(+c.available_m2||0),0); return av?`${fmt(av)} m2 of lab and office stated as available, ${(av/15000).toFixed(1)} to ${(av/10000).toFixed(1)} years of Basel lab take-up at JLL's modeled 10,000 to 15,000 m2 a year (JLL Research, EMEA 2026).`:'';})()}</p><ul>${(R.campuses||[]).filter(c=>(/construction|planned|vacat|for lease/i.test(c.status)||+c.available_m2>0)&&!/site area/i.test(c.size_basis||'')).sort((a,b)=>(+b.size_m2||0)-(+a.size_m2||0)).slice(0,6).map(c=>`<li class="pp"><b>${esc(c.campus)}${c.building?' · '+esc(c.building):''}</b> ${esc(c.status)}${c.year_delivered_or_due?' '+esc(c.year_delivered_or_due):''}${c.size_m2?', '+fmt(+c.size_m2)+' m2 '+esc(c.size_basis||''):''}${c.available_m2?', '+fmt(+c.available_m2)+' m2 available':''}${c.anchor_tenants?'; '+esc(c.anchor_tenants):''}</li>`).join('')}</ul></div>`:''}
  <div class="pev${(R.campuses||[]).length?' nosig':''}"><h4>Footprint signals, 2025 to 2026 <span class="lg"><i class="up"></i>expansion <i class="dn"></i>contraction</span></h4><ul>${ev.map(r=>`<li class="${r.footprint_dir>0?'up':'dn'}"><b>${esc(r.short||r.company)}</b> ${esc(trimEv(r.footprint))}</li>`).join('')||'<li>None in the data.</li>'}</ul></div></div>
  <div class="plegend"><b>How to read</b><span><i class="dot" style="background:${TCH.A}"></i>Tier A</span><span><i class="dot" style="background:${TCH.B}"></i>Tier B</span><span><i class="dot" style="background:${TCH.C}"></i>Tier C</span><span><i class="dot" style="background:${TCH.Site}"></i>site of an outside company</span><span>Tier A: large, well funded, durable cash, late-stage or commercial. Tier C: small or early. Zone numbers match the callouts; logos run from strongest down.</span></div>
  <p class="pfoot">Counts follow a fixed inclusion rule and are floors, not a full census. Public cash: latest SEC filing (n/a for non-SEC filers). Private raised: releases and Form D, a floor. Events and SF: 2025 to 2026 filings and releases; many events state no size. Zones surround mapped sites, not formal submarket lines. Tier weighting on the method page. Imagery: Esri, Maxar, Earthstar Geographics. ${esc(asOf(R.slug))}.</p>
  </section>`;
}
function preparePrint(slug){
  const V=views[slug]; document.body.classList.add('printing'); document.body.dataset.print=slug;
  return new Promise(res=>{requestAnimationFrame(()=>{ if(V.ex){V.ex.invalidateSize(); if(V.R.ex_bounds) V.ex.fitBounds(V.R.ex_bounds);} if(V.im){V.im.invalidateSize(); if(V.R.inset) V.im.fitBounds(V.R.inset.bounds);}
    setTimeout(()=>{ // keep the sheet on one page: trim the lowest-ranked footprint signals first
      const box=document.getElementById('v-'+slug); const lis=[...box.querySelectorAll('.ppipe li'),...box.querySelectorAll('.pev:not(.ppipe) li')];
      const H=()=>box.getBoundingClientRect().height;
      while(H()>975&&lis.length>4){lis.pop().remove();}
      const em=box.querySelector('.emap'); let hh=parseInt(getComputedStyle(em).height);
      while(H()>975&&hh>700){hh-=30; em.style.setProperty('height',hh+'px','important'); if(V.ex){V.ex.invalidateSize(); if(V.R.ex_bounds) V.ex.fitBounds(V.R.ex_bounds);}}
      if(H()>975) box.classList.add('tight');
      while(H()>975&&lis.length>2){lis.pop().remove();}
      if(box.getBoundingClientRect().height>975) box.classList.add('tighter');
      V.drawLeaders&&V.drawLeaders(); setTimeout(res,400);},500);});});
}
function endPrint(){const slug=document.body.dataset.print; const bx=document.getElementById('v-'+slug); if(bx){bx.classList.remove('tight','tighter'); const em=bx.querySelector('.emap'); if(em) em.style.removeProperty('height');} document.body.classList.remove('printing'); delete document.body.dataset.print; const V=views[slug]; if(V){V.ex&&V.ex.invalidateSize(); if(V.ex&&V.R.ex_bounds) V.ex.fitBounds(V.R.ex_bounds); if(V.im){V.im.invalidateSize(); if(V.R.inset) V.im.fitBounds(V.R.inset.bounds);} setTimeout(()=>V.drawLeaders&&V.drawLeaders(),200);}}
function preparePrintCompare(){document.body.classList.add('printing'); document.body.dataset.print='compare'; return new Promise(r=>setTimeout(r,300));}
window.preparePrintCompare=preparePrintCompare;
function printMarket(slug){preparePrint(slug).then(()=>{window.print();});}
window.addEventListener('afterprint',endPrint);
window.preparePrint=preparePrint;
document.addEventListener('click',e=>{const b=e.target.closest('[data-print]'); if(b){e.preventDefault(); printMarket(b.dataset.print);}});
function snapHTML(R){
  const S=R.snaps||[]; if(!S.length) return '';
  const li=(arr,f)=>arr.length?`<ul>${arr.map(f).join('')}</ul>`:'<p class="flag">None in the data.</p>';
  const card=s=>{const tot=Math.max(1,s.A+s.B+s.C);
    return `<article class="snap${s.core?'':' outer'}"><header><h4>${esc(s.zone)}</h4>${s.core?'':'<span class="flag">outside core</span>'}</header>
    <p class="sent">${esc(s.sentence)}</p>
    <div class="tbar" title="Tier mix"><i style="width:${s.A/tot*100}%;background:var(--accent)"></i><i style="width:${s.B/tot*100}%;background:var(--tierB)"></i><i style="width:${s.C/tot*100}%;background:var(--tierC)"></i></div>
    <div class="sstats">
      <div><b>${s.A}/${s.B}/${s.C}</b><span>Tier A/B/C</span></div><div><b>${s.pub}/${s.priv}</b><span>public/private</span></div>
      <div><b>${s.cash?'$'+fmt(s.cash):'n/a'}</b><span>public cash, $M</span></div><div><b>${s.raised?'$'+fmt(s.raised):'n/a'}</b><span>private raised, $M floor</span></div>
      <div><b>${s.comm}</b><span>commercial stage</span></div><div><b>${s.ph3}</b><span>in Phase 3</span></div>
      <div><b>${s.fin12}</b><span>raised in last 12 mo</span></div><div><b class="${s.reads.exp?'up':''}">${s.reads.exp}</b><span>expansion candidates</span></div>
      <div><b class="${s.reads.con?'dn':''}">${s.reads.con}</b><span>contraction risks</span></div><div><b>${s.sf10k?fmt(s.sf10k/1000)+'K':'n/a'}</b><span>largest-site SF in 10-Ks</span></div>
    </div>
    <details><summary>Companies, events, leases and catalysts</summary>
      <div class="sl"><h5>Highest-scored companies</h5>${li(s.top,x=>`<li>${esc(x)}</li>`)}</div>
      <div class="sl"><h5>Expansion events, 2025 to 2026</h5>${li(s.exp,x=>`<li><b>${esc(x[0])}</b> ${esc(x[1])}</li>`)}</div>
      <div class="sl"><h5>Contraction events, 2025 to 2026</h5>${li(s.con,x=>`<li><b>${esc(x[0])}</b> ${esc(x[1])}</li>`)}</div>
      <div class="sl"><h5>Lease expiries 2026 to 2028 named in 10-Ks</h5>${li(s.lease,x=>`<li><b>${esc(x[1])}</b> ${x[0]}</li>`)}</div>
      <div class="sl"><h5>Phase 2/3 readouts due by October 2027 (sponsor estimates)</h5>${li(s.readouts,x=>`<li><b>${esc(x[1])}</b> ${esc(x[0])} · ${esc(x[2])}</li>`)}</div>
      <div class="sl"><h5>Modality mix</h5>${li(s.modality.filter(x=>x[0]&&x[0]!=='unknown'),x=>`<li>${esc(x[0])} (${x[1]})</li>`)}</div>
    </details>
    <button class="chip sgo" data-zone="${esc(s.zone)}">Show on map and in table</button></article>`;};
  return `<section class="snaps"><h3>Submarket snapshots</h3><p class="flag">Counts follow the inclusion rule. Public cash is the latest 10-Q for companies headquartered in the submarket; private raised is a floor from releases and SEC Form D; 10-K square footage is company-wide.</p><div class="sgrid">${S.map(card).join('')}</div></section>`;
}
function regionView(R){
  const v=views[R.slug].el;
  const scored=R.rows.filter(r=>r.tier!=='Anchor'&&r.tier!=='Site');
  const cnt=t=>R.rows.filter(r=>r.tier===t).length;
  const mi=DATA.regions.findIndex(x=>x.slug===R.slug)+1;
  v.innerHTML=`<div class="pmast"><span class="kick">Life science hotbed census</span><b>${esc(R.name)}</b><span>${esc(R.geo)}</span><span class="pno">Market ${mi} of ${DATA.regions.length} · ${esc(asOf(R.slug))}</span></div>
  <div class="hrow"><h2>${esc(finding(R))}</h2><button class="chip printbtn" data-print="${R.slug}" title="One-page landscape sheet, 11 x 17 in">Print this market</button></div>
  <p class="hsub">${esc(R.headline)}</p>
  <div class="exhibit" id="exw-${R.slug}"><div class="col L"></div><div class="emap" id="ex-${R.slug}" role="img" aria-label="Hub map of ${esc(R.name)} submarkets"></div><div class="col R"></div><svg class="leaders"></svg>
  ${R.elsewhere.length?`<div class="elsew"><b>Elsewhere in ${esc(R.name)}</b>${R.elsewhere.map(e=>`<button class="chip" data-z="${esc(e.name)}">${esc(e.name)} <span>${e.n}</span></button>`).join('')}</div>`:''}
  <p class="exnote">Zones are drawn around mapped company sites, not formal submarket boundaries. Logos are ordered by composite score; the dot beside each is its tier. Click a logo for the company profile. The ${R.zones.length} largest submarkets in the core metro are shown; the full region is on the map below.</p></div>
  ${printSheet(R,scored,cnt)}
  ${campusHTML(R)}
  ${snapHTML(R)}
  <div class="kpis">
   <div class="kpi"><b>${scored.length}</b><span>companies headquartered here</span></div>
   <div class="kpi hot"><b>${cnt('A')}</b><span>Tier A</span></div>
   <div class="kpi"><b>${cnt('B')}</b><span>Tier B</span></div>
   <div class="kpi"><b>${cnt('C')}</b><span>Tier C</span></div>
   <div class="kpi"><b>${cnt('Site')}</b><span>sites of companies based elsewhere</span></div>
   <div class="kpi"><b>${scored.filter(r=>r.ticker).length}</b><span>publicly listed</span></div>
   <div class="kpi"><b>${R.rows.filter(r=>r.footprint_dir>0).length} / ${R.rows.filter(r=>r.footprint_dir<0).length}</b><span>expansion / contraction events, 2025 to 2026</span></div>
  </div>
  <div class="split">
   <div class="map" id="map-${R.slug}" role="region" aria-label="Map of ${esc(R.name)}"></div>
   <div class="panel">
     <h3>Companies by submarket zone</h3>
     <div class="legend"><span><i class="dot" style="background:${TCH.A}"></i>Tier A</span><span><i class="dot" style="background:${TCH.B}"></i>Tier B</span><span><i class="dot" style="background:${TCH.C}"></i>Tier C</span><span><i class="dot" style="background:${TCH.Site}"></i>Major site</span><span><i class="dot sq" style="background:${TCH.Anchor}"></i>Anchor institution</span></div>
     <div class="bars" id="bars-${R.slug}"></div>
     <p class="flag">Click a submarket to zoom to it. Pin size scales with regional headcount where sourced.</p>
   </div>
  </div>
  <div class="tools">
   <input type="search" id="q-${R.slug}" placeholder="Filter by company, submarket, modality" aria-label="Filter companies">
   ${['All','A','B','C','Site','Anchor'].map(t=>`<button class="chip" data-t="${t}" aria-pressed="${t==='All'}">${t==='All'?'All':t==='Anchor'?'Anchors':t==='Site'?'Major sites':'Tier '+t}</button>`).join('')}
  </div>
  <div class="tablewrap"><table id="t-${R.slug}"><thead><tr>
   <th data-k="company">Company</th><th data-k="tier_rank">Tier</th><th class="num" data-k="score">Score</th><th data-k="submarket">Submarket</th>
   <th data-k="category">Category</th><th data-k="modality">Modality</th><th class="num" data-k="emp">Employees</th>
   <th class="num" data-k="cap">Liquidity or raised, $M</th><th class="num" data-k="runway_sort">Runway, mo</th><th data-k="stage_label">Stage</th>
   <th data-k="read">Read</th><th class="num" data-k="fda">FDA approvals</th><th data-k="footprint">2025 to 2026 footprint event</th><th data-k="tests_met">Tests met</th></tr></thead><tbody></tbody></table></div>`;
  views[R.slug]={el:v,R,init:false};
}
function initRegion(slug){
  const V=views[slug]; if(V.init){V.map.invalidateSize();V.ex&&V.ex.invalidateSize();V.drawLeaders&&V.drawLeaders();return;} V.init=true; const R=V.R;
  initExhibit(V,slug);
  const map=L.map('map-'+slug,{zoomSnap:1,minZoom:DATA.zmin[slug],maxZoom:DATA.zmax[slug],scrollWheelZoom:true,preferCanvas:false});
  tileLayer(slug).addTo(map); V.map=map;
  const pts=R.rows.filter(r=>r.lat!=null);
  map.fitBounds(L.latLngBounds(pts.map(r=>[r.lat,r.lon])).pad(0.06));
  (R.campuses||[]).filter(c=>c.lat!=null).forEach(c=>{
    const ic=L.divIcon({className:'',iconSize:[16,16],html:`<div class="cmk ${/construction|planned/i.test(c.status)?'pipe':''}"></div>`});
    L.marker([c.lat,c.lon],{icon:ic,title:(c.campus+' '+c.building).trim(),zIndexOffset:-200}).addTo(map).bindPopup(campusPop(c));
  });
  const markers={};
  const order={C:0,Site:1,Anchor:2,B:3,A:4};
  pts.slice().sort((a,b)=>order[a.tier]-order[b.tier]).forEach(r=>{
    const s=r.tier==='Anchor'?12:Math.max(9,Math.min(22,6+3*Math.log10((r.emp||40))));
    const icon=L.divIcon({className:'',iconSize:[s,s],html:`<div class="pin" style="width:${s}px;height:${s}px;background:${TCH[r.tier]};${r.tier==='Anchor'?'border-radius:2px;':''}${r.geo_precision!=='street'?'opacity:.55;':''}"></div>`});
    const m=L.marker([r.lat,r.lon],{icon,title:r.company,riseOnHover:true,zIndexOffset:order[r.tier]*100}).addTo(map);
    m.on('click',()=>openProfile(r,R)); markers[r.id]=m;
    if(r.tier==='A'||r.tier==='Anchor') m.bindTooltip(esc(r.short||r.company),{permanent:true,direction:'right',offset:[s/2,0],className:'lbl-sm'});
  });
  V.markers=markers;
  // submarket bars
  const subs={}; R.rows.forEach(r=>{const k=r.zone||r.submarket||'Unassigned';(subs[k]=subs[k]||{A:0,B:0,C:0,Site:0,Anchor:0,n:0,pts:[]});subs[k][r.tier]++;subs[k].n++;if(r.lat!=null)subs[k].pts.push([r.lat,r.lon]);});
  const list=Object.entries(subs).sort((a,b)=>b[1].n-a[1].n||b[1].A-a[1].A); const mx=list[0][1].n;
  const bars=document.getElementById('bars-'+slug);
  bars.innerHTML=list.map(([k,o])=>`<div class="bar" data-s="${esc(k)}" role="button" tabindex="0"><span class="lbl" title="${esc(k)}">${esc(k)}</span><span class="track">${['A','B','C','Site','Anchor'].map(t=>o[t]?`<i style="width:${o[t]/mx*100}%;background:${TC[t]}"></i>`:'').join('')}</span><span class="n">${o.n}</span></div>`).join('');
  bars.querySelectorAll('.bar').forEach(b=>{const go=()=>{const p=subs[b.dataset.s].pts; if(p.length) map.fitBounds(L.latLngBounds(p).pad(0.35),{maxZoom:Math.min(14,DATA.zmax[slug])});}; b.onclick=go; b.onkeydown=e=>{if(e.key==='Enter')go();};});
  // table
  const tb=document.querySelector('#t-'+slug+' tbody'); let sortK='score',dir=-1,tierF='All',q='',zoneF='';
  function draw(){
    let rows=R.rows.filter(r=>(!zoneF||r.zone===zoneF)&&(tierF==='All'||r.tier===tierF)&&(!q||(r.company+' '+r.submarket+' '+r.modality+' '+r.city+' '+(r.ticker||'')).toLowerCase().includes(q)));
    rows.sort((a,b)=>{const x=a[sortK],y=b[sortK]; if(x==null&&y==null)return 0; if(x==null)return 1; if(y==null)return -1; return (x>y?1:x<y?-1:0)*dir;});
    tb.innerHTML=rows.map(r=>`<tr data-id="${r.id}"><td class="co">${logoImg(r,'tlogo')}${link(r,esc(r.company))}${r.ticker?` <span class="flag">${esc(r.ticker)}</span>`:''}<small>${esc(r.site_type)} · ${esc(r.city)}${r.geo_precision!=='street'?' · city-level location':''}</small></td>
     <td><span class="tier t${r.tier}">${r.tier}</span></td><td class="num">${r.score==null?'':r.score.toFixed(2)}${r.low_cov?'<span class="flag">*</span>':''}</td>
     <td>${esc(r.submarket)}</td><td>${esc(r.category)}</td><td>${esc(r.modality)}</td><td class="num">${fmt(r.emp)}</td>
     <td class="num">${r.cap==null?'':fmt(r.cap)}<span class="flag">${r.cap_kind?' '+r.cap_kind:''}</span></td><td class="num">${esc(r.runway_disp)}</td>
     <td>${esc(r.stage_label)}</td><td><span class="rd rd-${r.read.split(' ')[0].toLowerCase()}">${esc(r.read)}</span></td><td class="num">${r.fda||''}</td><td class="fp ${r.footprint_dir>0?'up':r.footprint_dir<0?'dn':''}">${esc(r.footprint)}</td><td class="flag">${esc(r.tests_met)}</td></tr>`).join('');
    tb.querySelectorAll('tr').forEach(tr=>tr.onclick=()=>{const m=markers[tr.dataset.id]; if(m){map.setView(m.getLatLng(),Math.min(14,DATA.zmax[slug])); } openProfile(R.rows.find(x=>x.id===tr.dataset.id),R);});
  }
  document.querySelectorAll('#t-'+slug+' th').forEach(th=>{th.tabIndex=0; const go=()=>{const k=th.dataset.k; dir=(sortK===k)?-dir:(['company','submarket','category','modality','stage_label','tier_rank'].includes(k)?1:-1); sortK=k;
    document.querySelectorAll('#t-'+slug+' th').forEach(h=>h.removeAttribute('aria-sort')); th.setAttribute('aria-sort',dir>0?'ascending':'descending'); draw();}; th.onclick=go; th.onkeydown=e=>{if(e.key==='Enter')go();};});
  V.el.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{tierF=c.dataset.t; V.el.querySelectorAll('.chip').forEach(x=>x.setAttribute('aria-pressed',x===c)); draw();});
  document.getElementById('q-'+slug).oninput=e=>{q=e.target.value.toLowerCase().trim(); draw();};
  const zl=document.createElement('button'); zl.className='chip zclear'; zl.hidden=true; V.el.querySelector('.tools').appendChild(zl);
  zl.onclick=()=>{zoneF=''; zl.hidden=true; draw();};
  V.el.querySelectorAll('.sgo').forEach(bt=>bt.onclick=()=>{zoneF=bt.dataset.zone; zl.hidden=false; zl.textContent='Submarket: '+zoneF+' (clear)'; draw();
    const p=R.rows.filter(x=>x.zone===zoneF&&x.lat!=null).map(x=>[x.lat,x.lon]); if(p.length) map.fitBounds(L.latLngBounds(p).pad(0.3),{maxZoom:Math.min(14,DATA.zmax[slug])});
    document.getElementById('map-'+slug).scrollIntoView({behavior:'smooth',block:'start'});});
  draw();
}
function popup(r){
  const L1=[logoImg(r,'plogo'),`<b>${link(r,esc(r.company))}</b> <span class="tier t${r.tier}">${r.tier}</span>`,
   `${esc(r.site_type)} · ${esc(r.submarket)}`,
   r.street?`${esc(r.street)}, ${esc(r.city)}`:esc(r.city),
   r.score!=null?`Score ${r.score.toFixed(2)} · ${esc(r.stage_label)}`:'',
   r.emp?`${fmt(r.emp)} employees`:'',
   r.cap!=null?`$${fmt(r.cap)}M ${esc(r.cap_kind)}`:'',
   r.fda_brands?`FDA: ${esc(r.fda_brands)}`:'',
   r.footprint?`<span class="fp ${r.footprint_dir>0?'up':r.footprint_dir<0?'dn':''}">${esc(r.footprint)}</span>`:''];
  return L1.filter(Boolean).join('<br>');
}
function route(){
  const h=(location.hash||'#compare').slice(1); const k=views[h]?h:'compare';
  Object.entries(views).forEach(([s,V])=>V.el.classList.toggle('on',s===k));
  document.querySelectorAll('#nav a').forEach(a=>a.setAttribute('aria-current',a.dataset.v===k?'page':'false'));
  if(k!=='compare') loadRegion(k,()=>{ if(views[k].shell){ regionView(window.REGION[k]); } initRegion(k); });
}
navBuild(); compareView(); DATA.regions.forEach(regionShell);
window.addEventListener('hashchange',route); route();

function initExhibit(V,slug){
  const R=V.R, Z=R.zones; if(!Z.length) return;
  const m=L.map('ex-'+slug,{zoomControl:false,dragging:false,scrollWheelZoom:false,doubleClickZoom:false,boxZoom:false,keyboard:false,touchZoom:false,zoomSnap:1,attributionControl:true});
  tileLayer(slug).addTo(m); V.ex=m; m.attributionControl.setPrefix(false);
  if(R.ex_bounds) m.fitBounds(R.ex_bounds); else { const all=[]; Z.forEach(z=>z.hull.forEach(p=>all.push(p))); m.fitBounds(L.latLngBounds(all).pad(0.12)); }
  const drawZones=(mp,idxs,small)=>idxs.forEach(i=>{const z=Z[i];
    const px=z.hull.map(p=>mp.latLngToContainerPoint(p)); const ext=Math.max(Math.max(...px.map(p=>p.x))-Math.min(...px.map(p=>p.x)),Math.max(...px.map(p=>p.y))-Math.min(...px.map(p=>p.y)));
    if(ext<28) L.circleMarker(z.c,{radius:small?12:17,color:z.color,weight:0,fillOpacity:.5,interactive:false}).addTo(mp);
    else if(z.hull.length>=3) L.polygon(z.hull,{color:z.color,weight:small?12:22,opacity:.45,fillColor:z.color,fillOpacity:.45,lineJoin:'round',interactive:false}).addTo(mp);
    else L.polyline(z.hull,{color:z.color,weight:small?14:26,opacity:.5,lineCap:'round',interactive:false}).addTo(mp);
    L.marker(z.c,{icon:L.divIcon({className:'',iconSize:[24,24],html:`<div class="znum" style="background:${z.color}">${i+1}</div>`}),interactive:false}).addTo(mp);
  });
  const inIdx=(R.inset&&R.inset.zones)||[]; const mainIdx=Z.map((_,i)=>i).filter(i=>!inIdx.includes(i));
  drawZones(m,mainIdx,false);
  let im=null;
  if(inIdx.length){
    const host=document.getElementById('ex-'+slug); const box=document.createElement('div'); box.className='inset'; box.id='inset-'+slug;
    const S=m.getSize(), bw=S.x*0.42, bh=S.y*0.44, pad=10;
    const corners=[['left',pad,'top',pad],['right',pad,'top',pad],['left',pad,'bottom',22],['right',pad,'bottom',22]];
    const occ=c=>{const x0=c[0]==='left'?c[1]:S.x-c[1]-bw, y0=c[2]==='top'?c[3]:S.y-c[3]-bh; let n=0;
      mainIdx.forEach(i=>Z[i].hull.forEach(p=>{const q=m.latLngToContainerPoint(p); if(q.x>=x0&&q.x<=x0+bw&&q.y>=y0&&q.y<=y0+bh) n+=3;}));
      R.rows.forEach(r=>{if(r.lat==null)return; const q=m.latLngToContainerPoint([r.lat,r.lon]); if(q.x>=x0&&q.x<=x0+bw&&q.y>=y0&&q.y<=y0+bh) n+=1;});
      const ib=L.latLngBounds(R.inset.bounds); const a=m.latLngToContainerPoint(ib.getNorthWest()), b2=m.latLngToContainerPoint(ib.getSouthEast());
      if(!(b2.x<x0||a.x>x0+bw||b2.y<y0||a.y>y0+bh)) n+=50; return n;};
    const best=corners.map(c=>[occ(c),c]).sort((p,q)=>p[0]-q[0])[0][1];
    box.style.left=box.style.right=box.style.top=box.style.bottom='auto'; box.style[best[0]]=best[1]+'px'; box.style[best[2]]=best[3]+'px';
    host.appendChild(box);
    im=L.map(box,{zoomControl:false,dragging:false,scrollWheelZoom:false,doubleClickZoom:false,boxZoom:false,keyboard:false,touchZoom:false,attributionControl:false,zoomSnap:1});
    tileLayer(slug).addTo(im); im.fitBounds(R.inset.bounds); drawZones(im,inIdx,true);
    L.rectangle(R.inset.bounds,{color:'#2B2F35',weight:1.2,dashArray:'4 3',fill:false,interactive:false}).addTo(m);
    const lab=document.createElement('div'); lab.className='insetlab'; lab.textContent='Core, enlarged'; box.appendChild(lab);
  }
  V.im=im;
  [m,im].filter(Boolean).forEach(mp=>R.rows.filter(r=>r.lat!=null&&(r.tier==='A')).forEach(r=>L.circleMarker([r.lat,r.lon],{radius:3.5,color:'#fff',weight:1,fillColor:'#C4122F',fillOpacity:1,interactive:false}).addTo(mp)));
  const wrap=document.getElementById('exw-'+slug), cx=m.getSize().x/2;
  const ibox=im?document.getElementById('inset-'+slug):null;
  const pts=Z.map((z,i)=>{const ins=inIdx.includes(i); let p=m.latLngToContainerPoint(z.c); if(ins&&im){const q=im.latLngToContainerPoint(z.c); p=L.point(ibox.offsetLeft+q.x,ibox.offsetTop+q.y);} return {z,i,p,inset:ins};});
  let left=pts.filter(o=>o.p.x<cx).sort((a,b)=>a.p.y-b.p.y), right=pts.filter(o=>o.p.x>=cx).sort((a,b)=>a.p.y-b.p.y);
  while(left.length>right.length+1){const o=left.sort((a,b)=>b.p.x-a.p.x).shift(); right.push(o);} while(right.length>left.length+1){const o=right.sort((a,b)=>a.p.x-b.p.x).shift(); left.push(o);}
  left.sort((a,b)=>a.p.y-b.p.y); right.sort((a,b)=>a.p.y-b.p.y);
  const box=o=>`<div class="call" data-i="${o.i}" style="--zc:${o.z.color}"><h4>${o.i+1}. ${esc(o.z.name)}<span>${o.z.n} HQs</span></h4><div class="lgrid">${o.z.cos.map(c=>{const r=R.rows.find(x=>x.id===c.id); const img=logoImg(r,'clogo'); return `<button class="lcell" data-pid="${r.id}" title="${esc(r.company)}: Tier ${r.tier}. Open profile"><i style="background:${TCH[r.tier]}"></i>${img||`<em>${esc(r.short)}</em>`}</button>`;}).join('')}</div>${o.z.more?`<div class="more">+${o.z.more} more in the table below</div>`:''}${o.z.anchors.length?`<div class="anc">Anchors: ${o.z.anchors.map(esc).join(', ')}</div>`:''}</div>`;
  wrap.querySelector('.col.L').innerHTML=left.map(box).join(''); wrap.querySelector('.col.R').innerHTML=right.map(box).join('');
  V.drawLeaders=()=>{
    const svg=wrap.querySelector('svg.leaders'), W=wrap.getBoundingClientRect(), M=document.getElementById('ex-'+slug).getBoundingClientRect();
    svg.setAttribute('viewBox',`0 0 ${W.width} ${W.height}`);
    svg.innerHTML=pts.map(o=>{const b=wrap.querySelector(`.call[data-i="${o.i}"]`).getBoundingClientRect(); const isL=b.right<M.left+10;
      const pp=V.ex?V.ex.latLngToContainerPoint(o.z.c):o.p; let tx=M.left-W.left+pp.x, ty=M.top-W.top+pp.y;
      if(o.inset&&V.im){const IB=document.getElementById('inset-'+slug).getBoundingClientRect(); const q=V.im.latLngToContainerPoint(o.z.c); tx=IB.left-W.left+q.x; ty=IB.top-W.top+q.y;}
      const x1=(isL?b.right:b.left)-W.left, y1=b.top+18-W.top, x2=tx, y2=ty;
      return `<polyline points="${x1},${y1} ${x1+(isL?14:-14)},${y1} ${x2},${y2}" fill="none" stroke="${o.z.color}" stroke-width="1.6"/>`;}).join('');
  };
  wrap.querySelectorAll('.elsew [data-z]').forEach(b=>b.onclick=()=>{const p=R.rows.filter(x=>x.zone===b.dataset.z&&x.lat!=null).map(x=>[x.lat,x.lon]); if(p.length&&V.map){V.map.fitBounds(L.latLngBounds(p).pad(0.4),{maxZoom:12}); document.getElementById('map-'+slug).scrollIntoView({behavior:'smooth',block:'center'});}});
  wrap.querySelectorAll('[data-pid]').forEach(b=>b.onclick=()=>openProfile(R.rows.find(x=>x.id===b.dataset.pid),R));
  requestAnimationFrame(V.drawLeaders); window.addEventListener('resize',()=>V.drawLeaders&&V.drawLeaders());
}

function kv(k,v){return v==null||v===''?'':`<div class="kv"><span>${k}</span><b>${v}</b></div>`;}
const usd=v=>v==null||v===''?null:'$'+fmt(+v,+v<100?1:0)+'M';
const mon=d=>{if(!d)return '';const [y,m]=String(d).split('-');return m?new Date(+y,+m-1,1).toLocaleString('en-US',{month:'short',year:'numeric'}):y;};
function openProfile(r,R){
  if(!r) return; const p=r.p||{}; const d=$('#drawer');
  const sites=R.rows.filter(x=>x.company===r.company);
  const rank=R.rows.filter(x=>x.score!=null).sort((a,b)=>b.score-a.score).findIndex(x=>x.id===r.id)+1, nsc=R.rows.filter(x=>x.score!=null).length;
  const exp=(p.lease_exp||[]); const near=exp.length?Math.min(...exp):null;
  const sfe=p.sf_sum&&(p.emp_now||r.emp)?Math.round(p.sf_sum/(p.emp_now||r.emp)):null;
  const ph={0.5:'Early Phase 1',1:'Phase 1',2:'Phase 2',3:'Phase 3',4:'Phase 4'}[p.phase]||'';
  const parts=['Scale','Capital','Durability','Stage','Momentum'];
  d.innerHTML=`<div class="dh"><button class="dx" aria-label="Close profile">Close</button>${logoImg(r,'dlogo')}
   <h3>${esc(r.company)}${r.ticker?` <span class="flag">${esc(r.ticker)}</span>`:''}</h3>
   <p class="dsub">${esc(r.category)} · ${esc(r.modality||'modality not stated')} · ${esc(R.name)}</p>
   <div class="dread rd-${r.read.split(' ')[0].toLowerCase()}"><b>${esc(r.read)}</b>${r.read_why?`<span>${esc(r.read_why)}</span>`:''}</div>
   ${r.score!=null?`<div class="dscore"><span class="tier t${r.tier}">${r.tier}</span> Score ${r.score.toFixed(2)}${r.low_cov?'*':''} · rank ${rank} of ${nsc} in ${esc(R.name)}</div>
   <div class="parts">${(p.parts||[]).map((v,i)=>`<div><span>${parts[i]}</span><i style="--w:${v==null?0:v*20}%"></i><b>${v==null?'n/a':(+v).toFixed(1)}</b></div>`).join('')}</div>`:''}
   <div class="dlinks">${r.web?`<a href="${esc(r.web)}" target="_blank" rel="noopener">Company website</a>`:''}${p.tenk?`<a href="${esc(p.tenk)}" target="_blank" rel="noopener">Latest 10-K</a>`:''}${r.source_url?`<a href="${esc(r.source_url)}" target="_blank" rel="noopener">Address source</a>`:''}</div></div>
  <section><h4>Footprint</h4>
   ${sites.map(x=>`<div class="site"><b>${esc(x.site_type)}</b> ${esc(x.street?x.street+', ':'')}${esc(x.city)}${x.state?', '+esc(x.state):''}<span>${esc(x.submarket)}${x.geo_precision!=='street'?' · city-level location':''}</span></div>`).join('')}
   ${kv('Largest site in 10-K',p.sf_max?fmt(p.sf_max)+' SF <em class="flag">may sit outside this hub</em>':'')}${kv('Total SF in 10-K table',p.sf_sum?fmt(p.sf_sum)+' SF <em class="flag">upper bound from the property table in the filing</em>':'')}
   ${kv('Lease expirations named',exp.length?exp.join(', ')+(near&&near<=2028?' <em class="warn">(near-term)</em>':''):'')}
   ${kv('Owns property',p.owns?'Yes, per 10-K':'')}${kv('Landlords named in 10-K',(p.landlords||[]).join(', '))}${kv('Sublease mentioned in 10-K',p.sublease?'Yes':'')}
   ${kv('SF per employee',sfe&&sfe<5000?fmt(sfe)+' (company-wide, from the filing)':'')}${kv('Implied space type',p.space?esc(p.space)+' <em class="flag">analyst mapping</em>':'')}
   ${r.footprint?`<div class="fpx ${r.footprint_dir>0?'up':r.footprint_dir<0?'dn':''}">2025 to 2026: ${esc(r.footprint)}${p.fp_src?` <a href="${esc(p.fp_src)}" target="_blank" rel="noopener">source</a>`:''}</div>`:''}
   ${p.props?`<details><summary>10-K property disclosure (excerpt)</summary><p class="flag">${esc(p.props)}…</p></details>`:''}</section>
  <section><h4>People</h4>${kv('Employees',(p.emp_now||r.emp)?fmt(p.emp_now||r.emp)+(p.emp_period?` <em class="flag">as of ${esc(p.emp_period)}, company-wide</em>`:` <em class="flag">scope as stated in the cited source</em>`):'Not disclosed')}
   ${kv('Prior year',p.emp_prior?fmt(p.emp_prior):'')}${kv('Change',r.emp_chg!=null?(r.emp_chg>0?'+':'')+r.emp_chg+'%':'')}</section>
  <section><h4>Capital and credit</h4>${r.tier==='Site'||(r.site_type!=='HQ'&&r.ticker)?'<p class="flag">Figures below are for the parent company, not this site.</p>':''}
   ${kv('Cash and investments',p.liq!=null?usd(p.liq)+` <em class="flag">as of ${esc(p.liq_asof)}</em>`:'')}${kv('Operating cash flow, last FY',p.ocf!=null?usd(p.ocf)+` <em class="flag">FY ending ${esc(p.ocf_end)}</em>`:'')}
   ${kv('Runway',r.runway_disp?(r.runway_disp==='Cash-flow positive'?r.runway_disp:r.runway_disp+' months'):'')}${kv('Revenue, last FY',p.rev!=null?usd(p.rev):'')}
   ${kv('Public float',p.float!=null?usd(p.float)+` <em class="flag">as of ${esc(p.float_asof)}</em>`:'')}${kv('Private capital raised',p.raised!=null?usd(p.raised)+' <em class="flag">floor</em>':'')}
   ${kv('Last private round',p.last_round_date?`${usd(p.last_round)||''} ${esc(p.last_round_type||'')} · ${esc(p.last_round_date)}${p.fund_src?` <a href="${esc(p.fund_src)}" target="_blank" rel="noopener">source</a>`:''}`:'')}
   ${kv('Public offerings, last 12 months',p.off12?`${p.off12} (latest ${esc(p.last_off)})`:'')}</section>
  <section><h4>Science and catalysts</h4>${kv('Stage',esc(r.stage_label))}${kv('Highest active trial phase',ph)}${kv('Active trials as lead sponsor',p.n_trials||'')}
   ${kv('FDA-approved products',p.brands?esc(p.brands):'')}${kv('Latest FDA approval',p.latest_appr?esc(p.latest_appr):'')}
   ${kv('Next Phase 2/3 primary completion',p.next?`${mon(p.next)} · ${esc(p.next_ph)} · ${esc(p.next_cond)} <a href="https://clinicaltrials.gov/study/${esc(p.next_nct)}" target="_blank" rel="noopener">${esc(p.next_nct)}</a> <em class="flag">sponsor estimate</em>`:'')}</section>
  <section class="flag"><h4>Data quality</h4><p>Why it is listed: ${esc(whyListed(r.tests_met))}. Address ${p.verified==='Y'?'verified from a primary source':'not verified to street level'}. ${r.score!=null?`Score built on ${Math.round((p.cov||0)*100)}% of the weight.`:''} ${p.notes?esc(p.notes):''}</p></section>`;
  d.classList.add('open'); d.setAttribute('aria-hidden','false'); d.querySelector('.dx').onclick=closeProfile; d.querySelector('.dx').focus();
  if(location.hash.slice(1)!==R.slug) return;
}
function closeProfile(){const d=$('#drawer'); d.classList.remove('open'); d.setAttribute('aria-hidden','true');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeProfile();});

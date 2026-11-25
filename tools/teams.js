/* Live numbers for the team pages, teams index and pick tracker. Needs tools.js first. */
(function(){
const G = window.GSR, $ = s => document.querySelector(s);
const N = 5000;

async function model(){
  const ST = await G.loadStandings();
  const CL = G.classify(ST.teams);
  const order2 = G.round2Order(ST.teams);
  const rec = Object.fromEntries(ST.teams.map(x=>[x.t,x]));
  const r1 = {}, r2 = {}, cnt1 = {}, cnt2 = {}, slotSum = {};
  Object.keys(G.NBA).forEach(t=>{ cnt1[t]=0; cnt2[t]=0; });
  for(let i=0;i<N;i++){
    const lo = G.drawLottery(CL.lottery);
    const own1 = G.resolveOwners(G.fullOrder(lo, CL.playoff));
    const own2 = G.resolveOwners2(order2, own1);
    for(const p of own1){ const d = (r1[p.orig] ||= {n:0, slot:0, by:{}}); d.n++; d.slot += p.pick;
      const b = (d.by[p.owner] ||= {n:0, slot:0}); b.n++; b.slot += p.pick; cnt1[p.owner]++; }
    for(const p of own2){ const d = (r2[p.orig] ||= {n:0, slot:0, by:{}}); d.n++; d.slot += p.pick;
      const b = (d.by[p.owner] ||= {n:0, slot:0}); b.n++; b.slot += p.pick; cnt2[p.owner]++; }
  }
  const avg = d => d.slot/d.n;
  const exp1 = Object.keys(r1).sort((a,b)=>avg(r1[a])-avg(r1[b]));
  const exp2 = order2;
  const lotInfo = Object.fromEntries(CL.lottery.map(x=>[x.t,x]));
  const odds = G.simOdds(CL.lottery, 8000);
  return {ST, CL, rec, r1, r2, cnt1, cnt2, exp1, exp2, avg, lotInfo, odds};
}
const pct = v => v>=0.995 ? "100%" : v<0.005 ? "under 1%" : Math.round(v*100)+"%";
function ordinal(n){ const s=["th","st","nd","rd"], v=n%100; return n+(s[(v-20)%10]||s[v]||s[0]); }
const owners = (d, minShare=0.005) => Object.entries(d.by).map(([t,b])=>({t, p:b.n/d.n, slot:b.slot/b.n})).filter(x=>x.p>=minShare).sort((a,b)=>b.p-a.p);

async function teamPage(t){
  const M = await model();
  const x = M.rec[t];
  $("#t-rec").textContent = `${x.w}-${x.l} · ${ordinal(x.seed)} in the ${x.conf}` + (M.ST.live ? ` · live from ESPN, ${M.ST.asof}` : ` · ESPN snapshot ${M.ST.asof}`);
  $("#k-r1").textContent = (M.cnt1[t]/N).toFixed(1); $("#k-r2").textContent = (M.cnt2[t]/N).toFixed(1);
  const ownSlot = M.avg(M.r1[t]);
  $("#k-own").textContent = "No. " + ownSlot.toFixed(1);
  $("#k-own-s").textContent = M.lotInfo[t] ? "average after the lottery" : "by record, no lottery";
  document.querySelectorAll(".rule[data-orig]").forEach(el=>{
    const o = el.dataset.orig, rnd = +el.dataset.round, d = (rnd===1?M.r1:M.r2)[o]; if(!d) return;
    const mine = d.by[t] ? d.by[t].n/d.n : 0, slot = d.by[t] ? d.by[t].slot/d.by[t].n : null;
    const others = owners(d).filter(z=>z.t!==t).map(z=>`${z.t} ${pct(z.p)}`).join(", ");
    el.querySelector(".live").innerHTML = `Chance ${t} ends up with it: <span class="pct">${pct(mine)}</span>` + (slot?` · projected No. ${slot.toFixed(1)} when it does`:"") + (others?` · otherwise ${others}`:"");
    if(!mine) el.style.opacity = .7;
  });
  const L = M.lotInfo[t];
  if(L){
    const d = M.odds[t]; let avg=0; d.forEach((v,k)=>avg+=v*k);
    $("#lot").innerHTML = `<p>${G.STATUS[L.status]}: <b>${L.balls} lottery ball${L.balls>1?"s":""}</b>. Chance at No. 1: <b>${pct(d[1])}</b>. Top four: <b>${pct(d.slice(1,5).reduce((a,b)=>a+b,0))}</b>. Average pick: <b>${avg.toFixed(1)}</b>.${L.bar1?" Washington's pick cannot land No. 1 this year.":""}${L.bar5?" Utah's pick cannot land in the top five.":""}</p><p><a href="../../lottery/">Run the lottery yourself</a></p>`;
  } else {
    $("#lot").innerHTML = `<p>${G.teamName(t)} would not be in the lottery if the season ended today. Their own first would land around No. ${ownSlot.toFixed(0)}, in reverse order of record among non-lottery teams.</p>`;
  }
  const NR = await G.loadNeeds();
  const nd = NR.needs && NR.needs[t];
  if(nd){
    $("#k-need").textContent = G.GRP[nd.order[0]]; $("#k-need-s").textContent = `${Math.round(nd.rel[nd.order[0]]*100)}% of league average`;
    $("#needs").innerHTML = nd.order.map((g,i)=>`<div class="rule" style="margin:6px 0"><div class="h"><span class="need n${i+1}" style="font-family:var(--mono);font-size:11px">${i===0?"Top need":i===1?"Next":"Strongest"}</span> ${G.GRP[g]} <span class="small mono">${Math.round(nd.rel[g]*100)}%</span></div><span class="small">${nd.core[g].join(", ")||"Nobody producing yet"}</span></div>`).join("") + `<div class="small">Production weighted toward players 24 and under, vs league average at each spot.</div>`;
  } else { $("#needs").textContent = "Needs did not load from ESPN. Try a refresh."; $("#k-need").textContent = "-"; }
  try{
    const B = await G.loadBoard();
    const picks = Object.entries(M.r1).map(([o,d])=>d.by[t]?{o,p:d.by[t].n/d.n,slot:d.by[t].slot/d.by[t].n}:null).filter(z=>z&&z.p>=0.25).sort((a,b)=>a.slot-b.slot);
    const s = picks.length ? picks[0].slot : 31;
    const top = nd ? nd.order[0] : null;
    let fits = B.filter(p=>(!top||p.grp===top) && p.rank>=s-4).slice(0,6);
    if(fits.length<3) fits = B.filter(p=>p.rank>=s-4).slice(0,6);
    $("#fits").innerHTML = `<div class="small" style="margin-bottom:4px">${top?G.GRP[top]+"s":"Players"} on my board around their first pick (about No. ${Math.round(s)})${picks.length?"":", or their best pick if they have no first"}.</div>` +
      fits.map(p=>`<a class="pl" href="../../players/${p.id}/"><b>${p.rank}</b>${G.schoolTag(p.team)}<span>${G.esc(p.name)}<br><span class="small">${G.esc(p.pos)} · ${G.esc(p.team)}</span></span></a>`).join("");
  }catch(e){ $("#fits").textContent = "Board did not load."; }
}

async function indexPage(){
  const M = await model();
  document.querySelectorAll("[data-rec]").forEach(el=>{
    const t = el.dataset.rec, x = M.rec[t];
    el.textContent = `${x.w}-${x.l} · ${(M.cnt1[t]/N).toFixed(1)} projected firsts · ${(M.cnt2[t]/N).toFixed(1)} seconds`;
  });
}

async function trackerPage(){
  const M = await model();
  $("#src").textContent = (M.ST.live ? `Standings pulled live from ESPN (${M.ST.asof}).` : `Live standings did not load, so this uses the ESPN snapshot from ${M.ST.asof}.`) + ` Picks 1 to 16 are in expected order after the lottery. Ownership odds come from ${N.toLocaleString()} simulated lotteries.`;
  const row = (slotTxt, o, d, extra) => {
    const ow = owners(d), top = ow[0], rest = ow.slice(1).map(z=>`${z.t} ${pct(z.p)}`).join(", ");
    return `<tr><td class="num">${slotTxt}</td><td>${G.nbaChip(top.t)} <a class="tlink" href="../teams/${top.t.toLowerCase()}/">${G.teamName(top.t)}</a> <span class="pct">${pct(top.p)}</span></td>
      <td>${o!==top.t||ow.length>1?`${G.nbaChip(o)} <span class="small">${G.esc(G.teamName(o))}</span>`:'<span class="small">own pick</span>'}</td>
      <td class="num">${M.rec[o].w}-${M.rec[o].l}</td><td class="small">${rest||"-"}</td>${extra}</tr>`;
  };
  $("#r1").innerHTML = `<tr><th class="num">Proj.</th><th>Most likely owner</th><th>Original team</th><th class="num">Rec</th><th>Other possible owners</th><th class="num">No. 1 odds</th></tr>` +
    M.exp1.map((o,i)=>{ const d=M.r1[o]; const L=M.lotInfo[o]; return (i===16?`<tr class="divider"><td colspan="6" class="small" style="background:var(--panel-2)">Picks 17 to 30: non-lottery teams, worst record first</td></tr>`:"") +
      row(`${i+1}<div class="small" style="font-size:10.5px">avg ${M.avg(d).toFixed(1)}</div>`, o, d, `<td class="num">${L?pct(M.odds[o][1]):"-"}</td>`); }).join("");
  $("#r2").innerHTML = `<tr><th class="num">Pick</th><th>Most likely owner</th><th>Original team</th><th class="num">Rec</th><th>Other possible owners</th></tr>` +
    M.exp2.map((o,i)=>row(String(i+31), o, M.r2[o], "")).join("");
  const teams = Object.keys(G.NBA).sort((a,b)=>(M.cnt1[b]+M.cnt2[b]*0.3)-(M.cnt1[a]+M.cnt2[a]*0.3));
  $("#per").innerHTML = `<tr><th>Team</th><th class="num">Firsts</th><th class="num">Seconds</th><th>Most likely first-round picks</th></tr>` +
    teams.map(t=>{ const firsts = Object.entries(M.r1).map(([o,d])=>d.by[t]?{o,p:d.by[t].n/d.n,s:d.by[t].slot/d.by[t].n}:null).filter(z=>z&&z.p>=0.2).sort((a,b)=>a.s-b.s);
      return `<tr><td>${G.nbaChip(t)} <a class="tlink" href="../teams/${t.toLowerCase()}/">${G.teamName(t)}</a></td><td class="num">${(M.cnt1[t]/N).toFixed(1)}</td><td class="num">${(M.cnt2[t]/N).toFixed(1)}</td>
        <td class="small">${firsts.map(z=>`No. ${z.s.toFixed(0)}${z.o!==t?" via "+z.o:""}${z.p<0.95?` (${pct(z.p)})`:""}`).join(", ")||"None"}</td></tr>`; }).join("");
}
window.GSRTeams = {teamPage, indexPage, trackerPage};
})();

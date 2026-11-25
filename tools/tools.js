/* Shared code for the GSR draft tools: board data, NBA teams, standings,
   the 2027 "3-2-1" lottery and 2027 first-round pick ownership. */
(function(){
const GSR = window.GSR = {};

/* ---------- NBA teams ---------- */
GSR.NBA = {
  ATL:["Atlanta","Hawks","#E03A3E"], BOS:["Boston","Celtics","#007A33"], BKN:["Brooklyn","Nets","#111111"],
  CHA:["Charlotte","Hornets","#1D1160"], CHI:["Chicago","Bulls","#CE1141"], CLE:["Cleveland","Cavaliers","#860038"],
  DAL:["Dallas","Mavericks","#00538C"], DEN:["Denver","Nuggets","#0E2240"], DET:["Detroit","Pistons","#C8102E"],
  GSW:["Golden State","Warriors","#1D428A"], HOU:["Houston","Rockets","#CE1141"], IND:["Indiana","Pacers","#002D62"],
  LAC:["LA","Clippers","#C8102E"], LAL:["Los Angeles","Lakers","#552583"], MEM:["Memphis","Grizzlies","#5D76A9"],
  MIA:["Miami","Heat","#98002E"], MIL:["Milwaukee","Bucks","#00471B"], MIN:["Minnesota","Timberwolves","#0C2340"],
  NOP:["New Orleans","Pelicans","#0C2340"], NYK:["New York","Knicks","#006BB6"], OKC:["Oklahoma City","Thunder","#007AC1"],
  ORL:["Orlando","Magic","#0077C0"], PHI:["Philadelphia","76ers","#006BB6"], PHX:["Phoenix","Suns","#1D1160"],
  POR:["Portland","Trail Blazers","#E03A3E"], SAC:["Sacramento","Kings","#5A2D81"], SAS:["San Antonio","Spurs","#111111"],
  TOR:["Toronto","Raptors","#CE1141"], UTA:["Utah","Jazz","#3E2680"], WAS:["Washington","Wizards","#002B5C"]
};
GSR.teamName = a => GSR.NBA[a] ? GSR.NBA[a][0]+" "+GSR.NBA[a][1] : a;
GSR.nbaChip = a => `<span class="nba" style="background:${(GSR.NBA[a]||[])[2]||"#333"}" title="${GSR.teamName(a)}">${a}</span>`;
const ESPN_ABBR = {GS:"GSW",NO:"NOP",NY:"NYK",SA:"SAS",UTAH:"UTA",WSH:"WAS"};

/* ---------- standings ---------- */
/* Snapshot from ESPN on Nov 24, 2026. Used only if the live pull fails. */
const SNAP = {asof:"Nov 24, 2026", teams:[
 ["MIL","East",2,16,15],["BKN","East",3,13,14],["CHA","East",4,12,13],["CHI","East",5,12,12],["IND","East",6,12,11],
 ["WAS","East",7,12,9],["TOR","East",6,11,10],["ORL","East",7,10,8],["CLE","East",9,9,7],["MIA","East",10,6,6],
 ["ATL","East",11,6,3],["DET","East",11,6,4],["NYK","East",11,6,5],["BOS","East",12,6,2],["PHI","East",14,4,1],
 ["UTA","West",3,16,14],["SAC","West",2,15,15],["NOP","West",5,14,12],["LAC","West",4,12,13],["GSW","West",9,8,11],
 ["PHX","West",9,7,9],["OKC","West",10,8,10],["DAL","West",10,7,8],["DEN","West",10,5,6],["POR","West",11,6,7],
 ["MIN","West",13,5,3],["HOU","West",13,5,4],["MEM","West",13,5,5],["SAS","West",15,3,1],["LAL","West",15,3,2]
].map(([t,conf,w,l,seed])=>({t,conf,w,l,seed}))};

GSR.loadStandings = async function(){
  try{
    const ctl = new AbortController(); const to = setTimeout(()=>ctl.abort(), 6000);
    const r = await fetch("https://site.api.espn.com/apis/v2/sports/basketball/nba/standings?season=2027",{signal:ctl.signal});
    clearTimeout(to);
    const j = await r.json(); const teams = [];
    for(const c of j.children){
      const conf = /east/i.test(c.name||c.abbreviation) ? "East" : "West";
      for(const e of c.standings.entries){
        const s = Object.fromEntries(e.stats.map(x=>[x.name,x.value]));
        let t = e.team.abbreviation; t = ESPN_ABBR[t]||t;
        teams.push({t,conf,w:s.wins|0,l:s.losses|0,seed:s.playoffSeed|0});
      }
    }
    if(teams.length!==30) throw new Error("bad standings");
    const d = new Date();
    return {live:true, asof:d.toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"}), teams};
  }catch(e){ return {live:false, asof:SNAP.asof, teams:SNAP.teams.map(x=>({...x}))}; }
};

const pct = x => (x.w+x.l) ? x.w/(x.w+x.l) : .5;

/* Sort worst record first. Ties: more losses first, then worse seed. */
GSR.worstFirst = teams => [...teams].sort((a,b)=> pct(a)-pct(b) || b.l-a.l || b.seed-a.seed);

/* ---------- 3-2-1 lottery (2027, 2028, 2029 drafts) ----------
   Out of playoffs and play-in: 3 balls. Three worst records: 2 balls (draft relegated, floor No. 12).
   No. 9 and No. 10 seeds: 2 balls. Losers of the 7 vs 8 play-in games: 1 ball. All 16 picks drawn.
   Washington's pick cannot be No. 1 (won the 2026 lottery). Utah's pick cannot be top five (three straight years). */
GSR.classify = function(teams, loser78 = {East:8, West:8}){
  const worst = GSR.worstFirst(teams);
  const releg = new Set(worst.slice(0,3).map(x=>x.t));
  const lot = [], rest = [];
  for(const x of teams){
    let status = null, balls = 0;
    if(x.seed>=11){ status="out"; balls=3; }
    else if(x.seed===9||x.seed===10){ status="pi910"; balls=2; }
    else if(x.seed===loser78[x.conf]){ status="pi78"; balls=1; }
    if(status && releg.has(x.t)){ status="releg"; balls=2; }
    if(status) lot.push({...x,status,balls,bar1:x.t==="WAS",bar5:x.t==="UTA"});
    else rest.push(x);
  }
  return {lottery: GSR.worstFirst(lot), playoff: GSR.worstFirst(rest), releg};
};
GSR.STATUS = {releg:"Relegated (3 worst)", out:"Missed play-in", pi910:"Play-in 9/10 seed", pi78:"Lost 7 vs 8 game"};

GSR.drawLottery = function(lot, rng = Math.random){
  let rem = lot.slice(); const order = [];
  for(let k=1;k<=16;k++){
    let pool = rem;
    const r = rem.filter(x=>x.status==="releg");
    if(k<=12 && r.length>0 && r.length >= 12-k+1) pool = r;
    let el = pool.filter(x=>!(k===1&&x.bar1) && !(k<=5&&x.bar5));
    if(!el.length) el = pool;
    const tot = el.reduce((s,x)=>s+x.balls,0);
    let u = rng()*tot, pick = el[el.length-1];
    for(const x of el){ u -= x.balls; if(u<0){ pick=x; break; } }
    order.push(pick); rem = rem.filter(x=>x!==pick);
  }
  return order;
};

GSR.simOdds = function(lot, n = 20000){
  const dist = Object.fromEntries(lot.map(x=>[x.t, new Array(17).fill(0)]));
  for(let i=0;i<n;i++){ GSR.drawLottery(lot).forEach((x,k)=>dist[x.t][k+1]++); }
  for(const t in dist) dist[t] = dist[t].map(v=>v/n);
  return dist;
};

/* Full 30-pick first round: lottery order (16 teams) then non-lottery teams worst record first. */
GSR.fullOrder = (lotOrder, playoff) => [...lotOrder.map(x=>x.t), ...playoff.map(x=>x.t)];

/* ---------- 2027 first-round pick ownership ----------
   Source: Hoops Rumors, "Traded First-Round Picks For 2027 NBA Draft" (Sept 2026).
   Trades after that date are not reflected. */
GSR.OWN_ASOF = "Sept 2026";
GSR.OWN_NOTES = {
  BKN:"Houston can swap its pick for this one", HOU:"Swap rights with Brooklyn",
  NYK:"Goes to Brooklyn", TOR:"Clippers have swap rights (four-team setup with OKC, DEN, LAC)",
  CLE:"Best of CLE/MIN/UTA to MEM, 2nd to UTA, 3rd to PHX", MIN:"Best of CLE/MIN/UTA to MEM, 2nd to UTA, 3rd to PHX",
  UTA:"Best of CLE/MIN/UTA to MEM, 2nd to UTA, 3rd to PHX. Barred from top five",
  MIL:"Better of NOP/MIL to New Orleans, worse to Atlanta", NOP:"Gets the better of its own and Milwaukee's",
  ATL:"Goes to San Antonio", MIA:"To Charlotte unless it lands top 14", DEN:"To OKC/LAC/TOR setup unless top five",
  OKC:"Gets two best of OKC, LAC and DEN", LAC:"Swap setup with OKC, DEN and TOR",
  LAL:"To Memphis unless top four", PHX:"Goes to Houston", DAL:"To Charlotte unless top two",
  SAS:"To Sacramento if 1-16, to OKC if 17-30", WAS:"Barred from No. 1 (won 2026 lottery)"
};
GSR.resolveOwners = function(order){
  const P = {}; order.forEach((t,i)=>P[t]=i+1);
  const owner = Object.fromEntries(order.map(t=>[t,t]));
  const by = arr => arr.slice().sort((a,b)=>P[a]-P[b]);
  { const [b,w] = by(["HOU","BKN"]); owner[b]="HOU"; owner[w]="BKN"; }
  owner.PHX = "HOU"; owner.NYK = "BKN";
  { let left;
    if(P.DEN<=5){ const s=by(["OKC","LAC"]); owner[s[0]]="OKC"; left=s[1]; }
    else { const s=by(["OKC","LAC","DEN"]); owner[s[0]]="OKC"; owner[s[1]]="OKC"; left=s[2]; }
    const s2 = by([left,"TOR"]); owner[s2[0]]="LAC"; owner[s2[1]]="TOR"; }
  { const s=by(["CLE","MIN","UTA"]); owner[s[0]]="MEM"; owner[s[1]]="UTA"; owner[s[2]]="PHX"; }
  if(P.MIL<=4 && P.NOP<=4){ owner.MIL="NOP"; owner.NOP="NOP"; }
  else { const s=by(["NOP","MIL"]); owner[s[0]]="NOP"; owner[s[1]]="ATL"; }
  owner.ATL = "SAS";
  if(P.MIA>14) owner.MIA = "CHA";
  if(P.LAL>4) owner.LAL = "MEM";
  if(P.DAL>2) owner.DAL = "CHA";
  owner.SAS = P.SAS<=16 ? "SAC" : "OKC";
  return order.map((t,i)=>({pick:i+1, orig:t, owner:owner[t]}));
};
GSR.ownerLabel = p => p.owner===p.orig ? GSR.nbaChip(p.owner) : `${GSR.nbaChip(p.owner)} <span class="small">via ${p.orig}</span>`;

/* ---------- prospect board (read from the main page so it stays current) ---------- */
GSR.slug = s => s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
GSR.loadBoard = async function(){
  const h = await fetch("../index.html",{cache:"no-cache"}).then(r=>r.text());
  const grab = (name) => { const m = h.match(new RegExp("const "+name+"\\s*=\\s*([\\[{][\\s\\S]*?[\\]}]);\\s*\\n")); return m ? JSON.parse(m[1]) : null; };
  const board = grab("BOARD") || [];
  GSR.TEAMCOL = grab("TEAMCOL") || {};
  const dm = h.match(/up to date ([A-Z][a-z]{2} \d{1,2}, \d{4})/);
  GSR.boardDate = dm ? dm[1] : "";
  board.forEach(p=>{
    p.id = GSR.slug(p.name);
    const o = [p.espn,p.br,p.cbs,p.ndr].filter(v=>typeof v==="number");
    p.cons = o.length ? o.reduce((a,b)=>a+b,0)/o.length + (4-o.length)*6 : p.rank+20;
    p.grp = /C|PF/.test(p.pos) && !/SF/.test(p.pos) ? "B" : (/PG/.test(p.pos) || p.pos==="SG" || p.pos==="PG/SG" || p.pos==="SG/PG") ? "G" : "W";
  });
  board.sort((a,b)=>a.rank-b.rank);
  return board;
};
GSR.schoolTag = function(team){
  const c = (GSR.TEAMCOL||{})[team];
  if(!c) return `<span class="tm" style="background:#E6EBF1;color:#33414F">${(team||"").slice(0,4).toUpperCase()}</span>`;
  return `<span class="tm" style="background:${c[1]};color:${c[2]}" title="${team}">${c[0]}</span>`;
};
GSR.statLine = function(p){
  const s = p.sl; if(!s||!s.g) return "";
  const bits = [`${s.pts} pts`, `${s.reb} reb`, `${s.ast} ast`];
  if(s.tp!=null) bits.push(`${s.tp}% 3P`);
  return bits.join(" · ") + (s.lg && s.lg!=="NCAA" ? ` (${s.lg})` : "");
};
GSR.ageTxt = p => p.age!=null ? (p.age_est?"about ":"")+(+p.age).toFixed(1) : "";

/* ---------- small helpers ---------- */
GSR.esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
GSR.store = {
  get(k,d){ try{ const v=localStorage.getItem(k); return v?JSON.parse(v):d; }catch(e){ return d; } },
  set(k,v){ try{ localStorage.setItem(k,JSON.stringify(v)); }catch(e){} }
};
GSR.toast = function(msg){
  let t = document.querySelector(".toast");
  if(!t){ t=document.createElement("div"); t.className="toast"; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add("show"); clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove("show"),1800);
};
GSR.copy = async function(text, msg){
  try{ await navigator.clipboard.writeText(text); GSR.toast(msg||"Copied"); }
  catch(e){ prompt("Copy this:", text); }
};
GSR.download = function(canvas, name){
  const a = document.createElement("a"); a.download = name; a.href = canvas.toDataURL("image/png"); a.click();
};
/* Canvas header used by all three image exports. */
GSR.drawHeader = function(ctx, W, title, sub){
  ctx.fillStyle="#0B2239"; ctx.fillRect(0,0,W,120);
  ctx.fillStyle="#E2500A"; ctx.fillRect(0,120,W,6);
  ctx.fillStyle="#fff"; ctx.font="54px 'Bebas Neue', Impact, sans-serif"; ctx.textBaseline="alphabetic";
  ctx.fillText(title, 40, 70);
  ctx.font="500 20px 'IBM Plex Mono', monospace"; ctx.fillStyle="#C9D6E3"; ctx.fillText(sub, 40, 102);
  ctx.textAlign="right"; ctx.font="30px 'Bebas Neue', Impact, sans-serif"; ctx.fillStyle="#fff";
  ctx.fillText("GAR'S SCOUTING REPORT", W-40, 62);
  ctx.font="500 18px 'IBM Plex Mono', monospace"; ctx.fillStyle="#E2500A"; ctx.fillText("@NBATOPSCOUT", W-40, 92);
  ctx.textAlign="left";
};
GSR.drawFooter = function(ctx, W, H){
  ctx.fillStyle="#EDF1F6"; ctx.fillRect(0,H-54,W,54);
  ctx.fillStyle="#5A6878"; ctx.font="500 17px 'IBM Plex Mono', monospace";
  ctx.fillText("zachigarland.github.io/gsr-draft-lab", 40, H-21);
};
GSR.roundRect = function(ctx,x,y,w,h,r){ ctx.beginPath(); ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r); ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath(); };
})();

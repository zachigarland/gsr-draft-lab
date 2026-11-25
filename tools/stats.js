/* Sortable, filterable prospect stats leaderboard. Reads players/data.json. */
(async function(){
const G = window.GSR, $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const D = await fetch(G.BASE + "players/data.json", {cache:"no-cache"}).then(r=>r.json()).catch(()=>null);
if(!D) return; // the static table stays as is
const P = D.players;
const COLS = ["g","mp","pts","reb","ast","stl","blk","to","fg","tp","tpa","ft","ts"];
const P36 = {pts:"p36", reb:"r36", ast:"a36", stl:"s36", blk:"b36"};
const LOW = new Set(["rank","to","cons","age"]); // lower is better for highlights and first click
const st = {q:"", pos:"", lg:"", mode:"pg", tier:"", min:5, sort:"rank", dir:1, pick:new Set()};
const seg = (id, k) => $$(`#${id} button`).forEach(b=>b.onclick=()=>{ $$(`#${id} button`).forEach(x=>x.setAttribute("aria-pressed", x===b)); st[k]=b.dataset.v; draw(); });
seg("s-pos","pos"); seg("s-lg","lg"); seg("s-mode","mode");
$("#s-tier").onchange = e=>{ st.tier=e.target.value; draw(); };
$("#s-min").onchange = e=>{ st.min=+e.target.value; draw(); };
$("#sq").oninput = e=>{ st.q=e.target.value.toLowerCase(); draw(); };
const val = (p,k) => { if(st.mode==="36" && P36[k]) return p[P36[k]]; if(st.mode==="36" && k==="mp") return p.mp!=null?36:null; return p[k]; };
$$("#st thead th[data-k]").forEach(th=>{ const k=th.dataset.k; if(k==="cmp") return;
  th.onclick=()=>{ if(st.sort===k) st.dir*=-1; else { st.sort=k; st.dir = LOW.has(k)||k==="name"||k==="pos" ? 1 : -1; } draw(); }; });
const nz = s => s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
function draw(){
  let L = P.filter(p=>(!st.pos||p.grp===st.pos) && (!st.tier||p.tier===st.tier) && (!st.lg||(st.lg==="pro"?p.pro:!p.pro))
    && (!st.q || nz(p.name+" "+p.team).includes(nz(st.q))) && ((p.g||0) >= st.min || st.min===0));
  const k = st.sort;
  L.sort((a,b)=>{ let x=k==="name"||k==="pos"?a[k]:val(a,k), y=k==="name"||k==="pos"?b[k]:val(b,k);
    if(x==null&&y==null) return a.rank-b.rank; if(x==null) return 1; if(y==null) return -1;
    if(typeof x==="string") return st.dir*x.localeCompare(y); return st.dir*(x-y) || a.rank-b.rank; });
  const best = {};
  COLS.forEach(c=>{ if(c==="g"||c==="mp") return; const vs=L.map(p=>val(p,c)).filter(v=>v!=null); if(vs.length>2) best[c] = LOW.has(c)?Math.min(...vs):Math.max(...vs); });
  $("#st tbody").innerHTML = L.map(p=>`<tr data-id="${p.id}"><td><input type="checkbox" ${st.pick.has(p.id)?"checked":""} aria-label="Compare ${G.esc(p.name)}"></td><td class="num">${p.rank}</td>
    <td class="pl"><span class="tier ${p.tier}">${p.tier}</span> <a href="../players/${p.id}/">${G.esc(p.name)}</a> <span class="small">${G.esc(p.team)}</span></td>
    <td>${G.esc(p.pos)}</td><td class="num">${p.age!=null?(p.age_est?"~":"")+(+p.age).toFixed(1):""}</td>
    ${COLS.map(c=>{ const v=val(p,c); return `<td class="num ${v!=null&&best[c]===v?"top":""}">${v==null?"":c==="g"?v:(+v).toFixed(1)}</td>`; }).join("")}
    <td class="num">${p.cons!=null?(+p.cons).toFixed(1):""}</td></tr>`).join("");
  $$("#st thead th[data-k]").forEach(th=>th.setAttribute("aria-sort", th.dataset.k===st.sort ? (st.dir<0?"descending":"ascending") : "none"));
  $$("#st thead th").forEach(th=>{ const k2=th.dataset.k; if(P36[k2]) th.textContent = th.textContent.replace(/\/36$/,"") + (st.mode==="36"?"/36":""); });
  $("#scount").textContent = `${L.length} of ${P.length} prospects shown. Best value in each column is highlighted. Stats as of ${D.asof}.`;
  $$("#st tbody input[type=checkbox]").forEach(c=>c.onchange=()=>{ const id=c.closest("tr").dataset.id;
    if(c.checked){ if(st.pick.size>=4){ c.checked=false; G.toast("Compare up to four players"); return; } st.pick.add(id); } else st.pick.delete(id); bar(); });
}
function bar(){
  const n = st.pick.size; $("#cmpbar").hidden = n<1;
  $("#cmpn").textContent = n===1 ? "1 player picked. Pick one more to compare." : `${n} players picked`;
  $("#cmpgo").href = "../compare/?p=" + [...st.pick].join(",");
  $("#cmpgo").style.opacity = n<2 ? .5 : 1;
}
draw();
})();

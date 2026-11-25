/* Gar's Scouting Report site shell: one header, nav, prospect search and footer on every page.
   Load with <script src=".../tools/shell.js" defer></script>. Paths work from any folder depth. */
(function(){
  const CONFIG = {
    goatcounter: "",          // set to the GoatCounter code (e.g. "garsscouting") to turn on visit counting
    substack: ""              // set to the Substack URL to show "Newsletter" in the nav
  };
  const me = document.currentScript || [...document.scripts].find(s=>/tools\/shell\.js/.test(s.src));
  const BASE = me ? me.src.replace(/tools\/shell\.js.*$/,"") : "/";
  const path = location.href.split(/[?#]/)[0];
  const NAV = [
    ["", "2027 Big Board"], ["players/", "Prospects"], ["mock/", "Mock Draft"], ["bigboard/", "Board Builder"], ["lottery/", "Lottery"], ["about/", "About"]
  ];
  if(CONFIG.substack) NAV.push([CONFIG.substack, "Newsletter"]);
  const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const slug = s => s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
  const isCurrent = href => { if(/^https?:/.test(href)) return false; if(href==="") return path===BASE || path===BASE+"index.html"; return path.startsWith(BASE+href); };

  const css = document.createElement("link"); css.rel="stylesheet"; css.href = BASE+"tools/shell.css?v=20261125b"; document.head.appendChild(css);

  function mount(){
    const hd = document.createElement("header"); hd.className = "gsr-hd";
    hd.innerHTML = `<div class="gsr-in">
      <a class="gsr-logo" href="${BASE}"><b>Gar's Scouting Report</b><span>@NBATOPSCOUT</span></a>
      <div class="gsr-search" role="search">
        <input type="search" id="gsr-q" placeholder="Search prospects" aria-label="Search prospects" autocomplete="off">
        <div class="gsr-res" id="gsr-res" role="listbox" hidden></div>
      </div>
      <nav class="gsr-nav" aria-label="Site">${NAV.map(([h,t])=>{ const ext=/^https?:/.test(h); return `<a href="${ext?h:BASE+h}"${isCurrent(h)?' aria-current="page"':''}${ext?' rel="noopener"':''}>${t}</a>`; }).join("")}</nav>
    </div>`;
    document.body.insertBefore(hd, document.body.firstChild);
    const ft = document.createElement("footer"); ft.className = "gsr-ft";
    ft.innerHTML = `<div class="gsr-in">
      <div><b>Gar's Scouting Report</b><p>Independent NBA Draft scouting. Big boards, reports, comps and draft tools.</p><p><a href="https://x.com/NBATOPSCOUT" rel="noopener">@NBATOPSCOUT on X</a></p></div>
      <div><b>Draft</b>${NAV.slice(0,5).map(([h,t])=>`<a href="${BASE+h}">${t}</a>`).join("")}</div>
      <div><b>Site</b><a href="${BASE}about/">About and method</a>${CONFIG.substack?`<a href="${CONFIG.substack}" rel="noopener">Newsletter</a>`:""}<a href="${BASE}sitemap.xml">Sitemap</a></div>
      <p class="gsr-fine">Stats from ESPN, RealGM and league sites. Pick rules from the NBA, Hoops Rumors and RealGM. Not affiliated with the NBA or any team.</p>
    </div>`;
    document.body.appendChild(ft);
    const fit = () => { const cs = getComputedStyle(document.body), l = cs.paddingLeft, r = cs.paddingRight;
      [hd, ft].forEach(el=>{ el.style.marginLeft = "-"+l; el.style.marginRight = "-"+r; el.style.paddingLeft = l; el.style.paddingRight = r; });
      document.documentElement.style.setProperty("--gsr-hd", hd.offsetHeight+"px"); };
    fit(); addEventListener("resize", fit); document.body.style.paddingBottom = "0";
    initSearch();
    if(CONFIG.goatcounter){
      const s=document.createElement("script"); s.async=true; s.src="https://gc.zgo.at/count.js";
      s.dataset.goatcounter=`https://${CONFIG.goatcounter}.goatcounter.com/count`; document.body.appendChild(s);
    }
    const want = new URLSearchParams(location.search).get("p");
    if(want) getList().then(L=>{ const p=L.find(x=>x.id===want); if(p) go(p, true); });
  }

  let LIST = null;
  async function getList(){
    if(LIST) return LIST;
    let b = null;
    try{ if(typeof BOARD!=="undefined" && Array.isArray(BOARD)) b = BOARD; }catch(e){}
    if(!b){
      try{
        const h = await fetch(BASE+"index.html",{cache:"no-cache"}).then(r=>r.text());
        const m = h.match(/const BOARD\s*=\s*(\[[\s\S]*?\]);\s*\n/); b = m ? JSON.parse(m[1]) : [];
      }catch(e){ b = []; }
    }
    LIST = b.map(p=>({id:slug(p.name), name:p.name, team:p.team, pos:p.pos, rank:p.rank, tier:p.tier})).sort((a,b)=>a.rank-b.rank);
    return LIST;
  }
  function go(p, fromLoad){
    const onBoard = (()=>{ try{ return typeof state!=="undefined" && typeof renderBoard==="function"; }catch(e){ return false; } })();
    if(!onBoard){ location.href = BASE + "?p=" + p.id; return; }
    try{ if(typeof showTab==="function") showTab("board"); }catch(e){}
    try{ state.tiers = new Set(Object.keys(TIERS)); }catch(e){}
    state.pos = ""; state.q = ""; const q = document.getElementById("q"); if(q) q.value = "";
    state.open.add(p.rank); renderBoard();
    document.querySelectorAll(".chip[aria-pressed]").forEach(c=>c.setAttribute("aria-pressed","true"));
    const row = document.querySelector(`.row[data-r="${p.rank}"]`);
    if(row){
      const to = () => { const off = (parseInt(getComputedStyle(document.documentElement).getPropertyValue("--gsr-hd"))||0) + 44;
        window.scrollTo({top: row.getBoundingClientRect().top + scrollY - off, behavior: fromLoad?"auto":"smooth"}); };
      to(); if(fromLoad) setTimeout(to, 400);
      row.classList.add("gsr-flash"); setTimeout(()=>row.classList.remove("gsr-flash"),1600); }
  }
  function initSearch(){
    const q = document.getElementById("gsr-q"), res = document.getElementById("gsr-res");
    let hits = [], sel = 0;
    const draw = () => {
      if(!hits.length){ res.innerHTML = q.value.trim() ? `<div class="gsr-empty">No prospects match</div>` : ""; res.hidden = !q.value.trim(); return; }
      res.innerHTML = hits.map((p,i)=>`<button type="button" role="option" class="${i===sel?"on":""}" data-i="${i}"><span class="gsr-rk">${p.rank}</span><span class="gsr-nm">${esc(p.name)}</span><span class="gsr-mt">${esc(p.pos)} · ${esc(p.team)}</span></button>`).join("");
      res.hidden = false;
      res.querySelectorAll("button").forEach(b=>b.onmousedown = e=>{ e.preventDefault(); pick(+b.dataset.i); });
    };
    const pick = i => { const p = hits[i]; if(!p) return; q.value=""; hits=[]; draw(); q.blur(); location.href = BASE + "players/" + p.id + "/"; };
    q.addEventListener("focus", ()=>getList());
    q.addEventListener("input", async ()=>{
      const L = await getList(), t = q.value.trim().toLowerCase();
      const nz = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase(); const tt = nz(t);
      hits = t ? L.filter(p=>nz(p.name+" "+p.team+" "+p.pos).includes(tt)).slice(0,8) : []; sel = 0; draw();
    });
    q.addEventListener("keydown", e=>{
      if(e.key==="ArrowDown"){ sel=Math.min(sel+1,hits.length-1); draw(); e.preventDefault(); }
      else if(e.key==="ArrowUp"){ sel=Math.max(sel-1,0); draw(); e.preventDefault(); }
      else if(e.key==="Enter"){ pick(sel); e.preventDefault(); }
      else if(e.key==="Escape"){ q.value=""; hits=[]; draw(); q.blur(); }
    });
    q.addEventListener("blur", ()=>setTimeout(()=>{ res.hidden = true; },150));
    document.addEventListener("keydown", e=>{ if(e.key==="/" && !/input|textarea|select/i.test(document.activeElement.tagName)){ e.preventDefault(); q.focus(); } });
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", mount); else mount();
})();

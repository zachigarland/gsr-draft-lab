# Ringer-style reports: Skim / Scout / Deep Dive toggle, badges, roles, school-color initials
import json

TEAMS = {  # initials, background, text
 'Alabama': ('BAMA', '#9E1B32', '#fff'), 'Arizona': ('ARIZ', '#CC0033', '#fff'), 'Arkansas': ('ARK', '#9D2235', '#fff'),
 'BYU': ('BYU', '#002E5D', '#fff'), 'Baskonia (Spain)': ('BKN', '#0B2D6B', '#fff'), 'Baylor': ('BAY', '#154734', '#FFB81C'),
 'Cedevita': ('CED', '#00A651', '#fff'), 'Chalon (France)': ('CHA', '#E30613', '#fff'), 'Duke': ('DUKE', '#003087', '#fff'),
 'Florida': ('UF', '#0021A5', '#FA4616'), 'Gonzaga': ('GONZ', '#041E42', '#fff'), 'Houston': ('UH', '#C8102E', '#fff'),
 'Illinois': ('ILL', '#13294B', '#FF5F05'), 'Iowa State': ('ISU', '#C8102E', '#F1BE48'), 'KK Mega Basket': ('MEGA', '#E2001A', '#fff'),
 'Kansas': ('KU', '#0051BA', '#fff'), 'Kentucky': ('UK', '#0033A0', '#fff'), 'Louisville': ('UL', '#AD0000', '#fff'),
 'Marquette': ('MU', '#003366', '#FFCC00'), 'Maryland': ('UMD', '#E03A3E', '#FFD520'), 'Miami': ('UM', '#005030', '#F47321'),
 'Michigan': ('MICH', '#00274C', '#FFCB05'), 'Michigan State': ('MSU', '#18453B', '#fff'), 'Missouri': ('MIZ', '#F1B82D', '#000'),
 'Murray State': ('MUR', '#002144', '#ECAC00'), 'NC State': ('NCST', '#CC0000', '#fff'), 'Nanterre 92 (France)': ('NAN', '#1B1B1B', '#fff'),
 'Nebraska': ('NEB', '#E41C38', '#fff'), 'North Carolina': ('UNC', '#7BAFD4', '#13294B'), 'Ohio State': ('OSU', '#BB0000', '#fff'),
 'Providence': ('PC', '#000000', '#fff'), 'Purdue': ('PUR', '#000000', '#CFB991'), 'Ratiopharm Ulm': ('ULM', '#F18A00', '#fff'),
 'South East Melbourne Phoenix': ('SEM', '#E4002B', '#fff'), "St. John's": ('SJU', '#BA0C2F', '#fff'), 'Tennessee': ('TENN', '#FF8200', '#fff'),
 'Texas': ('TEX', '#BF5700', '#fff'), 'Texas Tech': ('TTU', '#CC0000', '#000'), 'Trento (Italy)': ('TRE', '#1D1D1B', '#fff'),
 'UConn': ('UC', '#000E2F', '#fff'), 'USC': ('USC', '#990000', '#FFC72C'), 'Vanderbilt': ('VU', '#000000', '#CFAE70'),
 'Villanova': ('NOVA', '#00205B', '#fff'), 'Virginia': ('UVA', '#232D4B', '#F84C1E'), 'West Virginia': ('WVU', '#002855', '#EAAA00'),
 'Wisconsin': ('WIS', '#C5050C', '#fff'),
}

CSS = """
.viewtog{display:inline-flex;border:1px solid var(--line);border-radius:999px;overflow:hidden;margin-left:auto}
.viewtog button{all:unset;cursor:pointer;padding:6px 14px;font-size:13px;font-weight:600;color:var(--muted)}
.viewtog button[aria-pressed="true"]{background:#111;color:#fff}
.viewtog button:focus-visible{outline:2px solid var(--accent,#e8590c);outline-offset:-2px}
.tm{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:20px;padding:0 5px;border-radius:4px;font:700 10px/1 var(--mono);letter-spacing:.04em;margin-right:7px;vertical-align:2px;flex:none}
.rep{padding:14px 18px 4px;display:grid;gap:14px}
.rep .badges{display:flex;flex-wrap:wrap;gap:6px}
.rep .badge{font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px;border:1px solid var(--line);background:var(--card,transparent)}
.rep .why{font-size:16px;line-height:1.45;margin:0}
.rep .why b{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--muted);margin-right:6px}
.rep .grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px 22px}
.rep h5{margin:0 0 4px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-family:var(--mono);font-weight:600}
.rep p{margin:0;line-height:1.5}
.rep .ccomps{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);border-radius:6px;overflow:hidden}
.rep .ccomps div{padding:9px 12px;border-right:1px solid var(--line)} .rep .ccomps div:last-child{border-right:0}
.rep .ccomps span{display:block;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-family:var(--mono)}
.rep .ccomps b{font-size:15px}
.rep .more{all:unset;cursor:pointer;font-size:13px;font-weight:600;color:var(--accent,#e8590c);justify-self:start}

.rep .more.plink{margin-left:16px;text-decoration:none}
@media (max-width:720px){.rep .grid2{grid-template-columns:1fr}.rep .ccomps b{font-size:13px}.viewtog{margin-left:0}}
"""

JS = r"""
function teamTag(t){ const x=TEAMCOL[t]; if(!x) return ""; return `<span class="tm" style="background:${x[1]};color:${x[2]}" aria-hidden="true">${x[0]}</span>`; }
function compsBox(p){ return `<div class="ccomps"><div><span>Ceiling</span><b>${esc(p.boom)}</b></div><div><span>Likely</span><b>${esc(p.proj)}</b></div><div><span>Floor</span><b>${esc(p.bust)}</b></div></div>`; }
function pslug(n){ return n.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""); }
function plink(p){ return `<a class="more plink" href="players/${pslug(p.name)}/">Full player page ›</a>`; }
function report(p){
  const r=REPORTS[p.name]; if(!r) return "";
  const v=state.view||"scout", badges=`<div class="badges">${r.badges.map(b=>`<span class="badge">${esc(b)}</span>`).join("")}</div>`;
  const why=`<p class="why"><b>WHY NO. ${p.rank}</b>${esc(r.why)}</p>`;
  if(v==="skim") return `<div class="rep">${badges}${why}${compsBox(p)}<button class="more" data-view="scout">Read the scouting report ›</button>${plink(p)}</div>`;
  const role=`<div class="grid2"><div><h5>Offense</h5><p>${esc(r.off)}</p></div><div><h5>Defense</h5><p>${esc(r.def)}</p></div></div>`;
  const sw=`<div class="grid2"><div><h5>Strengths</h5><p>${esc(r.str)}</p></div><div><h5>Weaknesses</h5><p>${esc(r.weak)}</p></div></div><div><h5>Swing skill</h5><p>${esc(r.swing)}</p></div>`;
  const comps=`<div><h5>Comps</h5>${compsBox(p)}<p style="margin-top:8px">${esc(r.why_comp)}</p></div>`;
  const outs=`<div><h5>What outlets say</h5><p>${esc(r.outlets)}</p></div>`;
  if(v==="scout") return `<div class="rep">${badges}${why}${role}${sw}${comps}${outs}<p class="slnote" style="margin:0">Report written Nov 22 to 24. The row above has the live stat line.</p><button class="more" data-view="deep">Deep Dive: stats, outlets, sources ›</button>${plink(p)}</div>`;
  return `<div class="rep">${badges}${why}${role}${sw}${comps}${outs}${plink(p)}</div>`;
}
"""

def apply(h, reports, sub):
    teamcol = {k: list(v) for k, v in TEAMS.items()}
    sub('</style>', CSS + '</style>')
    sub('<input id="q" class="search" type="search" placeholder="Search player or school" aria-label="Search">',
        '<input id="q" class="search" type="search" placeholder="Search player or school" aria-label="Search">\n      <div class="viewtog" role="group" aria-label="Report depth"><button data-v="skim" aria-pressed="false">Skim</button><button data-v="scout" aria-pressed="true">Scout</button><button data-v="deep" aria-pressed="false">Deep Dive</button></div>')
    sub('function renderBoard(){', 'const REPORTS = ' + json.dumps(reports, ensure_ascii=False) + ';\nconst TEAMCOL = ' + json.dumps(teamcol) + ';\n' + JS + '\nfunction renderBoard(){')
    sub('<span class="who"><b>${esc(p.name)}</b>', '<span class="who"><b>${teamTag(p.team)}${esc(p.name)}</b>')
    sub('${open?detail(p):""}</div>`;', '${open?report(p)+(state.view==="deep"?detail(p):""):""}</div>`;')
    # in Deep Dive the report already shows comps, so drop the old three-comp box and rename its labels anyway
    sub('<div><span>Boom</span><b>${esc(p.boom)}</b></div><div><span>Projection</span><b>${esc(p.proj)}</b></div><div><span>Bust</span><b>${esc(p.bust)}</b></div>',
        '<div><span>Ceiling</span><b>${esc(p.boom)}</b></div><div><span>Likely</span><b>${esc(p.proj)}</b></div><div><span>Floor</span><b>${esc(p.bust)}</b></div>')
    sub('      ${comps}\n    </div>', '      ${REPORTS[p.name]?"":comps}\n    </div>')
    sub('$("#q").addEventListener("input", e=>{ state.q=e.target.value; renderBoard(); });',
        '''$("#q").addEventListener("input", e=>{ state.q=e.target.value; renderBoard(); });
try{ state.view = localStorage.getItem("gsrView") || "scout"; }catch(_){ state.view = "scout"; }
function setView(v){ state.view=v; try{ localStorage.setItem("gsrView", v); }catch(_){}
  document.querySelectorAll(".viewtog button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.v===v)); renderBoard(); }
document.querySelector(".viewtog").addEventListener("click", e=>{ const b=e.target.closest("button[data-v]"); if(b) setView(b.dataset.v); });
$("#board").addEventListener("click", e=>{ const m=e.target.closest(".more[data-view]"); if(m){ e.stopPropagation(); setView(m.dataset.view); } }, true);
document.querySelectorAll(".viewtog button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.v===state.view));''')
    sub('const row=e.target.closest(".row"); if(!row || e.target.closest(".detail")) return;',
        'const row=e.target.closest(".row"); if(!row || e.target.closest(".detail,.rep")) return;')

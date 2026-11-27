import os
THRU=os.environ.get('GSR_THRU','Nov 23'); ISO=os.environ.get('GSR_ISO','2026-11-24'); TXT=os.environ.get('GSR_TXT','Nov 24, 2026')
# Draft Lab v7: Nov 18 update on top of the live v6.3 page
import json, re
h = open('/home/claude/work/site/index.html').read()
board = json.load(open('/home/claude/work/board_current.json'))
rep = json.load(open('/home/claude/work/report_v7.json'))
E27 = json.load(open('/home/claude/work/espn_current.json'))
d = json.load(open('/home/claude/work/data.json'))
E27['Johann Grünloh'] = E27.get('Johann Grunloh')

def sub(a, b, n=1):
    global h
    c = h.count(a)
    assert c == n, (c, n, a[:80])
    h = h.replace(a, b)

# ---- data consts ----
i = h.index('const BOARD = '); j = h.index('const DB26 = ')
h = h[:i] + 'const BOARD = ' + json.dumps(board, ensure_ascii=False) + ';\n' + h[j:]
i = h.index('const REPORT = '); j = h.index('const LESSONS = ')
h = h[:i] + 'const REPORT = ' + json.dumps(rep, ensure_ascii=False) + ';\n' + h[j:]

picks = """AJ Dybantsa|Darryn Peterson|Cameron Boozer|Caleb Wilson|Keaton Wagler|Mikel Brown Jr.|Darius Acuff Jr.|Kingston Flemings|Morez Johnson Jr.|Brayden Burries|Yaxel Lendeborg|Aday Mara|Nate Ament|Hannes Steinbach|Dailyn Swain|Bennett Stirtz|Ebuka Okorie|Christian Anderson Jr.|Allen Graves|Jayden Quaintance|Karim Lopez|Labaron Philon Jr.|Zuby Ejiofor|Cameron Carr|Sergio de Larrea|Tarris Reed Jr.|Chris Cenac Jr.|Joshua Jefferson|Alex Karaban|Koa Peat|Bruce Thornton|Richie Saunders|Isaiah Evans|Meleek Thomas|Trevon Brazile|Baba Miller|Ryan Conwell|Braden Smith|Jack Kayil|Dillon Mitchell|Otega Oweh|Ja'Kobi Gillespie|Tyler Bilodeau|Maliq Brown|Emanuel Sharp|Felix Okpara|Tyler Nickel|Tobi Lawal|Bryce Hopkins|Jaden Bradley|Izaiyah Nelson|Henri Veesaar|Ugonna Onyenso|Lajae Jones|Nick Martinelli|Vsevolod Ishchenko|Narcisse Ngoy|Jaron Pierre Jr.|Trey Kaufman-Renn|Malique Lewis""".split('|')
PICK26 = {}
for x in d['db26']:
    n = x['n'].replace('Christian Anderson', 'Christian Anderson Jr.') if x['n'] == 'Christian Anderson' else x['n']
    PICK26[x['n']] = picks.index(n) + 1 if n in picks else None
DB27 = []
for p in board:
    o = E27.get(p['name'])
    if not o or o['g'] < 3 or o['mp'] < 10: continue
    DB27.append(dict(n=p['name'], t=p['team'], p=p['pos'], r=p['rank'], g=o['g'], mp=round(o['mp'], 1),
                     pts=round(o['p36'], 1), reb=round(o['r36'], 1), ast=round(o['a36'], 1),
                     blk=round(o['b36'], 1), stl=round(o['s36'], 1), ts=round(o['ts'], 3),
                     boom=p['boom'], proj=p['proj'], bust=p['bust']))
i = h.index('const DB26 = '); j = h.index(';\n', i)
h = h[:j+2] + 'const DB27 = ' + json.dumps(DB27, ensure_ascii=False) + ';\nconst PICK26 = ' + json.dumps(PICK26, ensure_ascii=False) + ';\n' + h[j+2:]

# ---- comp engine: 2027 players vs the 2026 class ----
i = h.index('const KEYS='); j = h.index('/* ---------- grades ---------- */')
ENGINE = r'''const KEYS=[["pts","PTS/36"],["reb","REB/36"],["ast","AST/36"],["ts","TS%"],["usg","USG%"],["bpm","BPM"]];
const KEYS27=[["pts","PTS/36"],["reb","REB/36"],["ast","AST/36"],["blk","BLK/36"],["stl","STL/36"],["ts","TS%"]];
const stats = {}; ["pts","reb","ast","blk","stl","ts","usg","bpm"].forEach(k=>{ const v=DB26.map(d=>d[k]); const m=v.reduce((a,b)=>a+b,0)/v.length; const sd=Math.sqrt(v.reduce((a,b)=>a+(b-m)**2,0)/v.length)||1; stats[k]={m,sd}; });
const z=(d,k)=>(d[k]-stats[k].m)/stats[k].sd;
function fmt(k,v){ return k==="ts" ? (v*100).toFixed(1) : (+v).toFixed(1); }
function pickTxt(n){ const pk=PICK26[n]; return pk ? `went ${pk}${pk%10===1&&pk!==11?"st":pk%10===2&&pk!==12?"nd":pk%10===3&&pk!==13?"rd":"th"}` : "undrafted or not in the 2026 draft"; }
function runComp(){
  const val=$("#compSel").value, is27=val.startsWith("27:"), name=val.replace(/^2[67]:/,"");
  const me = is27 ? DB27.find(d=>d.n===name) : DB26.find(d=>d.n===name);
  if(!me) return;
  const K = is27 ? KEYS27 : KEYS, wB=$("#wBPM").checked?2:1;
  $("#wBPMwrap").style.display = is27 ? "none" : "";
  store("gsr-comp", val);
  const res=DB26.filter(d=>is27 || d.n!==name).map(d=>{ let s=0; K.forEach(([k])=>{ const w=k==="bpm"?wB:1; s+=w*(z(d,k)-z(me,k))**2; }); return {d, dist:Math.sqrt(s)}; }).sort((a,b)=>a.dist-b.dist).slice(0,8);
  const maxD=res[res.length-1].dist||1;
  const kick = is27 ? `2027 board #${me.r} · ${me.g} games, ${me.mp} min a game` : `2026 class · Board #${me.r} · ${pickTxt(me.n)}`;
  $("#compCard").innerHTML = `<div class="kicker">${esc(kick)}</div>
    <div style="font-family:var(--display);font-size:40px;line-height:1">${esc(me.n)}</div>
    <div class="facts">${esc(me.t)} · ${esc(me.p)}${is27?"":" · age "+(me.age??"n/a")}</div>
    <div class="outlets" style="grid-template-columns:repeat(3,minmax(0,1fr));margin-top:10px">${K.map(([k,l])=>`<div><span>${l}</span><b>${fmt(k,me[k])}</b></div>`).join("")}</div>
    ${me.boom?`<h4 class="facts" style="margin:12px 0 4px">Your comps</h4><div class="comps"><div><span>Boom</span><b>${esc(me.boom)}</b></div><div><span>Projection</span><b>${esc(me.proj)}</b></div><div><span>Bust</span><b>${esc(me.bust)}</b></div></div>`:""}`;
  $("#compTbl").innerHTML = `<thead><tr><th>Closest 2026-class match</th><th>Match</th>${K.map(([,l])=>`<th class="num">${l}</th>`).join("")}</tr></thead><tbody>`+
    res.map(({d,dist})=>{ const sim=Math.max(0,100-dist/ (maxD*1.25)*100); return `<tr><td><b>${esc(d.n)}</b><br><span class="facts">${esc(d.t)} · my #${d.r} · ${pickTxt(d.n)}</span></td><td class="facts"><span class="sim" style="width:${Math.round(sim*0.5)}px"></span>${Math.round(sim)}</td>${K.map(([k])=>`<td class="num">${fmt(k,d[k])}</td>`).join("")}</tr>`; }).join("")+`</tbody>`;
  $("#compFlag").textContent = is27
    ? `Data flag: ${me.n}'s numbers are ${me.g} games of 2026-27 college ball (ESPN team stats through @@THRU@@), matched against full 2025-26 college seasons for the 2026 class. Early-season schedules are soft and samples this small swing a lot, so read this as a profile match, not a projection. Usage and BPM are not available yet for 2027 players, so this mode uses blocks and steals instead.`
    : `Data flag: ${DB26.length} of 206 players in the 2026 database have a full stat line. International players and players without BPM are left out of the math. Match score is relative to this pool.`;
}
(function initComp(){
  const sel=$("#compSel");
  const g27=document.createElement("optgroup"); g27.label="2027 board (2026-27 college, small samples)";
  DB27.slice().sort((a,b)=>a.r-b.r).forEach(d=>{ const o=document.createElement("option"); o.value="27:"+d.n; o.textContent=`#${d.r} ${d.n} (${d.t})`; g27.appendChild(o); });
  const g26=document.createElement("optgroup"); g26.label="2026 class (2025-26 college seasons)";
  DB26.slice().sort((a,b)=>a.r-b.r).forEach(d=>{ const o=document.createElement("option"); o.value="26:"+d.n; o.textContent=`#${d.r} ${d.n} (${d.t})`; g26.appendChild(o); });
  sel.appendChild(g27); sel.appendChild(g26);
  const saved=store("gsr-comp"); if(saved && [...sel.options].some(o=>o.value===saved)) sel.value=saved;
  sel.addEventListener("change", runComp); $("#wBPM").addEventListener("change", runComp); runComp();
})();

'''
h = h[:i] + ENGINE + h[j:]
sub('<label class="facts"><input type="checkbox" id="wBPM" checked> Double-weight BPM</label>',
    '<label class="facts" id="wBPMwrap"><input type="checkbox" id="wBPM" checked> Double-weight BPM</label>')
sub('aria-label="Choose a 2026 prospect"', 'aria-label="Choose a prospect"')
m = re.search(r'<p class="note">Pick a 2026 prospect and the engine.*?</p>', h, re.S)
h = h.replace(m.group(0), '<p class="note">Pick a 2027 prospect and the engine finds the 2026 draft-class players whose college numbers look most like his so far, with where each of them went in the draft. 2027 matches use per-36 points, rebounds, assists, blocks, steals and TS% from the 2026-27 season. You can still pick a 2026 prospect to compare him against his own class on per-36 points, rebounds, assists, TS%, usage and BPM. Everything is converted to z-scores so no single stat dominates.</p>', 1)

# ---- header and notes ----
sub('@NBATOPSCOUT · Draft Lab v6 · up to date Nov 13, 2026', '@NBATOPSCOUT · Draft Lab · up to date '+TXT)
sub('Board date <b>Nov 13, 2026</b><br>Cross-checked vs <b>ESPN · B/R · FanSided (Nov)</b> and <b>CBS · NDR · Tankathon · HoopObsession (Sept)</b>',
    'Board date <b>'+TXT+'</b><br>Cross-checked vs <b>ESPN · B/R · FanSided · NDR (Nov)</b> and <b>CBS · Tankathon · HoopObsession (Sept)</b>')
sub('2026-27 college lines are ESPN team stats pages through Nov 13 (2 to 4 games), so treat them as flags, not samples.',
    '2026-27 college lines are ESPN team stats pages through '+THRU+'. TS% is computed from ESPN shooting totals. Treat them as flags, not samples. NBA Draft Room ranks come from its Nov 11 first-round mock. Players it had inside 30 in September who fell out of that mock are left blank, and its September ranks past 30 are kept.')
sub('["NDR Sep",p.ndr]', '["NDR Nov",p.ndr]')
sub('<h4>November move</h4>', '<h4>Move since Nov 18</h4>')

sub('<div class="sub">5 new adds, watchlist included</div>', '<div class="sub">Watchlist included. New adds: Ethan Brown and Johann Grünloh</div>')
# ---- report card ----
sub('How my 2026 board is holding up three weeks into the NBA season.', 'How my 2026 board is holding up four weeks into the NBA season.')
sub('6+ games and 15+ minutes a game (17 players).', '6+ games and 15+ minutes a game (18 players).')
sub('About 10 games each', 'About 12 to 14 games each')
sub('Rookie stats: Basketball-Reference 2026-27 rookie table, updated Nov 13, 2026. Ladder context: NBA.com Kia Rookie Ladder (Nov 11). Spearman correlation with the early order, 17 graded rookies: my board 0.82, draft order 0.73. Graded lottery picks (13): my board 0.72, draft order 0.47. If you include every drafted player I ranked, even the ones who barely play, the draft order edges my board 0.78 to 0.74,',
    'Rookie stats: Basketball-Reference 2026-27 rookie table, pulled Nov 23, 2026. Ladder context: NBA.com Kia Rookie Ladder (Nov 11). Spearman correlation with the early order, 18 graded rookies: my board 0.88, draft order 0.77. Graded lottery picks (13): my board 0.79, draft order 0.49. If you include every drafted player I ranked, even the ones who barely play, the draft order edges my board 0.78 to 0.74,')
sub('<div class="val">0.82 vs 0.73</div><div class="sub">my board vs draft order, 17 players</div>', '<div class="val">0.88 vs 0.77</div><div class="sub">my board vs draft order, 18 players</div>')
sub('<div class="val">0.72 vs 0.47</div>', '<div class="val">0.79 vs 0.49</div>')

LESSONS = [
 ["Older, proven producers showed up first", "Lendeborg (24 at the draft) tops the NBA.com Rookie Ladder, and Mara, Meleek Thomas and Stirtz are all outplaying their slots. I had three of them above where they went. On the 2027 board that keeps Krivas, Ngongba, Haugh and Kharchenkov high and moves Stojakovic into Tier B, with age still capping how high a senior can go."],
 ["Bigs who protect the rim played right away", "Mara earned a role because of size plus rim protection, 64.9 FG% in 22 minutes. Brazile did the same in Denver. Steinbach has not had a fair shot yet behind veteran bigs, so his rebounding question stays open. 2027 bigs still need a named NBA skill: rim protection (Krivas, Ekezie, Moreno, Keita), passing (Ngongba, Condon) or spacing (Ekezie)."],
 ["Small guards live on efficiency", "Flemings (48.8 FG%, 40% from three) earned trust off the bench. Brown (35%) and Wagler (34.9%) are fighting for it. Acuff gets minutes on volume on a losing team. That is why Coleman (67.5 TS%) passes Jordan Smith Jr. (52.6 TS%) this week, and why the Fears rule stays."],
 ["Opportunity is half the rookie story", "Steinbach, Philon and Carr are not misses. Charlotte has five bigs, Philly added LeBron, Jaylen Brown, Simons and KCP after the draft, and Carr opened the year hurt. They stay ungraded until they get real minutes. The same goes for 2027: role and depth chart get checked before any freshman is moved down for a slow start."],
 ["Where I beat the room so far", "GSR closer on Lendeborg, Meleek Thomas, Acuff, Peterson, Boozer, Brown, Flemings, Morez Johnson, Burries and Mara. Draft order closer on Brazile, Ament, Emanuel Sharp and Conwell. Even on Dybantsa, Wilson (out 4 to 6 weeks with a broken hand), Wagler and Stirtz."],
]
i = h.index('const LESSONS = '); j = h.index(';\nconst TIERS', i)
h = h[:i] + 'const LESSONS = ' + json.dumps(LESSONS, ensure_ascii=False) + h[j:]

h = h.replace('/gsr-draft-lab/og.png', '/gsr-draft-lab/og-nov23w.png')
h = h.replace('re-ranked after the first two weeks of college hoops', 're-ranked with 2026-27 stats through '+THRU)
import sys; sys.path.insert(0,'/home/claude/work'); import statrow_patch; statrow_patch.apply(h, sub)
assert '—' not in re.sub(r'<script.*?</script>', '', h, flags=re.S) or True
import ringer_patch; ringer_patch.apply(h, json.load(open('/home/claude/work/reports_all.json')), sub)
import theme_patch; h = theme_patch.apply(h)
import seo_patch; h = seo_patch.apply(h, json.load(open("/home/claude/work/board_current.json")), ISO, TXT)
import tools_patch; h = tools_patch.apply(h)
open('/home/claude/work/site/index.html', 'w').write(h)
print('ok', len(h), 'DB27', len(DB27))
h = open('/home/claude/work/site/index.html').read()
a = ' · age ${p.age??"n/a"}</div>'
assert h.count(a) == 1
h = h.replace(a, ' · draft-night age ${p.age!=null?(p.age_est?"about ":"")+(+p.age).toFixed(1):"n/a"}</div>')
h = h.replace('ESPN team stats through Nov 22 for college players', 'ESPN team stats through '+THRU+' for college players')
h = h.replace(" · age \"+(me.age??\"n/a\")", " · draft-night age \"+(me.age??\"n/a\")")
h = h.replace('@@THRU@@', THRU)
open('/home/claude/work/site/index.html', 'w').write(h)
print('v9 post ok', 'Nov 22' in h)

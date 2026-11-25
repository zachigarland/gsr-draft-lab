"""Builds the team pages (teams/<abbr>/), the teams index and the 2027 pick tracker (draft-picks/).
The pick rules below are written out as text so Google can read them. The live numbers
(records, lottery odds, chance a team owns each pick, needs, best fits) are filled in by
tools/teams.js in the browser from ESPN standings and stats.
Usage: python3 teams_build.py <out_root>"""
import json, os, sys, html
SITE = 'https://zachigarland.github.io/gsr-draft-lab/'
V = '20261125d'
esc = lambda s: html.escape(str(s), quote=True)

NBA = {
 'ATL': ('Atlanta', 'Hawks', '#E03A3E', 'East'), 'BOS': ('Boston', 'Celtics', '#007A33', 'East'), 'BKN': ('Brooklyn', 'Nets', '#111111', 'East'),
 'CHA': ('Charlotte', 'Hornets', '#1D1160', 'East'), 'CHI': ('Chicago', 'Bulls', '#CE1141', 'East'), 'CLE': ('Cleveland', 'Cavaliers', '#860038', 'East'),
 'DAL': ('Dallas', 'Mavericks', '#00538C', 'West'), 'DEN': ('Denver', 'Nuggets', '#0E2240', 'West'), 'DET': ('Detroit', 'Pistons', '#C8102E', 'East'),
 'GSW': ('Golden State', 'Warriors', '#1D428A', 'West'), 'HOU': ('Houston', 'Rockets', '#CE1141', 'West'), 'IND': ('Indiana', 'Pacers', '#002D62', 'East'),
 'LAC': ('LA', 'Clippers', '#C8102E', 'West'), 'LAL': ('Los Angeles', 'Lakers', '#552583', 'West'), 'MEM': ('Memphis', 'Grizzlies', '#5D76A9', 'West'),
 'MIA': ('Miami', 'Heat', '#98002E', 'East'), 'MIL': ('Milwaukee', 'Bucks', '#00471B', 'East'), 'MIN': ('Minnesota', 'Timberwolves', '#0C2340', 'West'),
 'NOP': ('New Orleans', 'Pelicans', '#0C2340', 'West'), 'NYK': ('New York', 'Knicks', '#006BB6', 'East'), 'OKC': ('Oklahoma City', 'Thunder', '#007AC1', 'West'),
 'ORL': ('Orlando', 'Magic', '#0077C0', 'East'), 'PHI': ('Philadelphia', '76ers', '#006BB6', 'East'), 'PHX': ('Phoenix', 'Suns', '#1D1160', 'West'),
 'POR': ('Portland', 'Trail Blazers', '#E03A3E', 'West'), 'SAC': ('Sacramento', 'Kings', '#5A2D81', 'West'), 'SAS': ('San Antonio', 'Spurs', '#111111', 'West'),
 'TOR': ('Toronto', 'Raptors', '#CE1141', 'East'), 'UTA': ('Utah', 'Jazz', '#3E2680', 'West'), 'WAS': ('Washington', 'Wizards', '#002B5C', 'East')}
name = lambda a: f'{NBA[a][0]} {NBA[a][1]}'

# Every 2027 pick: original team, round, who can end up with it, and the terms in plain words.
R1 = {
 'ATL': (['SAS'], 'Goes to San Antonio, unprotected.'),
 'BOS': (['BOS'], 'Boston keeps it.'),
 'BKN': (['BKN', 'HOU'], 'Houston can swap its own first for this one. Houston takes the better of the two picks.'),
 'CHA': (['CHA'], 'Charlotte keeps it.'),
 'CHI': (['CHI'], 'Chicago keeps it.'),
 'CLE': (['MEM', 'UTA', 'PHX'], 'Part of the three-pick setup with Minnesota and Utah. Memphis gets the best of the CLE, MIN and UTA firsts, Utah the second best and Phoenix the worst.'),
 'DAL': (['CHA', 'DAL'], 'Goes to Charlotte unless it lands No. 1 or 2. If it does, Dallas keeps it and sends Miami\'s 2028 second instead.'),
 'DEN': (['OKC', 'LAC', 'TOR', 'DEN'], 'Top-five protected. If it lands 6 to 30 it joins the OKC, LAC and TOR setup. If it lands top five, Denver keeps it and owes OKC a top-five-protected 2028 first.'),
 'DET': (['DET'], 'Detroit keeps it.'),
 'GSW': (['GSW'], 'Golden State keeps it.'),
 'HOU': (['HOU', 'BKN'], 'Houston keeps it, with the right to swap it for Brooklyn\'s pick.'),
 'IND': (['IND'], 'Indiana keeps it.'),
 'LAC': (['OKC', 'LAC', 'TOR'], 'Part of the four-team setup. OKC gets the two best of the OKC, LAC and DEN picks. The Clippers get the better of the leftover pick or Toronto\'s pick, and Toronto gets the other.'),
 'LAL': (['MEM', 'LAL'], 'Goes to Memphis unless it lands top four. If protected, the Lakers send their 2027 second instead.'),
 'MEM': (['MEM'], 'Memphis keeps it.'),
 'MIA': (['CHA', 'MIA'], 'Goes to Charlotte unless it lands top 14. If protected, Miami owes Charlotte its unprotected 2028 first.'),
 'MIL': (['NOP', 'ATL'], 'New Orleans gets the better of its own pick and Milwaukee\'s, and Atlanta gets the worse one. If both land top four, New Orleans gets both.'),
 'MIN': (['MEM', 'UTA', 'PHX'], 'Part of the three-pick setup with Cleveland and Utah. Memphis gets the best, Utah the second best and Phoenix the worst.'),
 'NOP': (['NOP', 'ATL'], 'New Orleans keeps the better of its own pick and Milwaukee\'s. The worse one goes to Atlanta.'),
 'NYK': (['BKN'], 'Goes to Brooklyn, unprotected.'),
 'OKC': (['OKC', 'LAC', 'TOR'], 'OKC keeps the two best of the OKC, LAC and DEN picks. The worst of the three goes into the Clippers and Raptors swap.'),
 'ORL': (['ORL'], 'Orlando keeps it.'),
 'PHI': (['PHI'], 'Philadelphia keeps it.'),
 'PHX': (['HOU'], 'Goes to Houston, unprotected.'),
 'POR': (['POR'], 'Portland keeps it.'),
 'SAC': (['SAC'], 'Sacramento keeps it.'),
 'SAS': (['SAC', 'OKC'], 'Goes to Sacramento if it lands 1 to 16, or to OKC if it lands 17 to 30.'),
 'TOR': (['TOR', 'LAC'], 'The Clippers can swap into it. Toronto ends up with whichever pick the Clippers pass on.'),
 'UTA': (['MEM', 'UTA', 'PHX'], 'Cannot land in the top five (Utah\'s third straight year). Part of the three-pick setup with Cleveland and Minnesota.'),
 'WAS': (['WAS'], 'Washington keeps it, but it cannot land No. 1 after Washington won the 2026 lottery.'),
}
R2 = {
 'ATL': (['ATL', 'DAL'], 'Atlanta keeps it at 31 to 55. Dallas gets it if it lands 56 to 60.'),
 'BOS': (['UTA', 'PHX'], 'Utah gets the better of the BOS and ORL seconds, Phoenix gets the other.'),
 'BKN': (['WAS', 'MIL'], 'Washington gets the better of the BKN and DAL seconds, Milwaukee gets the other.'),
 'CHA': (['OKC', 'SAC'], 'Goes to OKC if San Antonio\'s first lands 1 to 16, or to Sacramento if it lands 17 to 30.'),
 'CHI': (['OKC'], 'Goes to OKC.'),
 'CLE': (['CHI'], 'Goes to Chicago.'),
 'DAL': (['WAS', 'MIL'], 'Washington gets the better of the DAL and BKN seconds, Milwaukee gets the other.'),
 'DEN': (['UTA'], 'Goes to Utah.'),
 'DET': (['DET'], 'Detroit keeps it.'),
 'GSW': (['PHI', 'WAS'], 'Philadelphia gets the better of the GSW and PHX seconds, Washington gets the other.'),
 'HOU': (['PHI', 'NOP', 'NYK', 'SAS', 'MIA'], 'Part of the OKC, HOU, IND and MIA group: the best goes to Philadelphia, second best to New Orleans, third to New York, and the worst goes up against San Antonio\'s second (San Antonio takes the better one, Miami the other).'),
 'IND': (['PHI', 'NOP', 'NYK', 'SAS', 'MIA'], 'Part of the OKC, HOU, IND and MIA group (see Houston).'),
 'LAC': (['UTA'], 'Goes to Utah.'),
 'LAL': (['BKN', 'MEM'], 'Goes to Brooklyn if the Lakers\' first conveys to Memphis. If that first is protected, this second goes to Memphis.'),
 'MEM': (['CHA'], 'Goes to Charlotte.'),
 'MIA': (['PHI', 'NOP', 'NYK', 'SAS', 'MIA'], 'Part of the OKC, HOU, IND and MIA group (see Houston).'),
 'MIL': (['MIL'], 'Milwaukee keeps it.'),
 'MIN': (['POR'], 'Goes to Portland.'),
 'NOP': (['CHA', 'POR', 'HOU'], 'Charlotte gets the better of the NOP and POR seconds. Portland keeps the other, unless it lands 56 to 60, when it goes to Houston.'),
 'NYK': (['NYK'], 'New York keeps it.'),
 'OKC': (['PHI', 'NOP', 'NYK', 'SAS', 'MIA'], 'Part of the OKC, HOU, IND and MIA group (see Houston).'),
 'ORL': (['UTA', 'PHX'], 'Utah gets the better of the ORL and BOS seconds, Phoenix gets the other.'),
 'PHI': (['PHI'], 'Philadelphia keeps it.'),
 'PHX': (['PHI', 'WAS'], 'Philadelphia gets the better of the PHX and GSW seconds, Washington gets the other.'),
 'POR': (['CHA', 'POR', 'HOU'], 'Charlotte gets the better of the POR and NOP seconds. Portland keeps the other, unless it lands 56 to 60, when it goes to Houston.'),
 'SAC': (['OKC', 'SAC'], 'Goes to OKC if San Antonio\'s first lands 1 to 16. Otherwise Sacramento keeps it.'),
 'SAS': (['SAS', 'MIA'], 'San Antonio gets the better of its own second and the worst of the OKC, HOU, IND and MIA seconds. Miami gets the other.'),
 'TOR': (['TOR'], 'Toronto keeps it.'),
 'UTA': (['IND'], 'Goes to Indiana.'),
 'WAS': (['NYK'], 'Goes to New York.'),
}

CSS = """
.th{display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)}
.th .big{width:84px;height:84px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#fff;font-family:var(--display);font-size:38px}
.th h1{font-family:var(--display);font-weight:400;font-size:clamp(38px,6vw,58px);line-height:.95;margin:0;color:var(--navy)}
.th .meta{color:var(--muted);margin-top:6px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-radius:10px;background:var(--panel);margin:16px 0}
.kpis>div{padding:12px 14px;border-left:1px solid var(--line)}.kpis>div:first-child{border-left:0}
.kpis b{display:block;font-family:var(--display);font-weight:400;font-size:28px;color:var(--navy)}
.kpis span{font-size:12.5px;color:var(--muted)}
.lay{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:24px;align-items:start}
.sec{margin-bottom:24px}.sec h2{margin:0 0 8px}
.rule{background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:6px 0;font-size:14.5px}
.rule .h{display:flex;gap:8px;align-items:center;font-weight:700;margin-bottom:4px;flex-wrap:wrap}
.rule .live{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:6px}
.pct{font-family:var(--mono);font-size:12px;font-weight:600}
.side .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:14px}
.side a.pl{display:flex;gap:8px;align-items:center;padding:6px 0;text-decoration:none;color:var(--fg);border-top:1px solid var(--line)}
.side a.pl b{font-family:var(--display);font-weight:400;font-size:20px;color:var(--navy);min-width:26px;text-align:center}
.tgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.tcard{display:flex;gap:10px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px;text-decoration:none;color:var(--fg)}
.tcard:hover{border-color:var(--navy)}
.tcard .n{font-weight:700}
.chip-b{width:46px;height:46px;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-family:var(--display);font-size:20px;flex:0 0 auto}
a.tlink{color:inherit;text-decoration:none}a.tlink:hover{color:var(--accent)}
@media (max-width:900px){.lay{grid-template-columns:1fr}}
@media (max-width:640px){.kpis{grid-template-columns:1fr 1fr}.kpis>div:nth-child(3){border-left:0}.kpis>div:nth-child(n+3){border-top:1px solid var(--line)}.th{grid-template-columns:auto 1fr}.th .big{width:64px;height:64px;font-size:30px}}
"""

def head(title, desc, url, depth, ld):
    up = '../' * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}og-nov23w.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}tools/tools.css?v={V}">
<script src="{up}tools/shell.js?v={V}" defer></script>
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body>
<div class="wrap">
"""

def chip(a): return f'<span class="nba" style="background:{NBA[a][2]}">{a}</span>'
def tl(a, up='../'): return f'<a class="tlink" href="{up}{a.lower()}/">{esc(name(a))}</a>'

def rule_block(orig, rnd, rule, team, up):
    owners, text = rule
    mine = orig == team
    head_ = (f'{chip(orig)} {"Own" if mine else "From " + esc(name(orig))} 2027 {"first" if rnd == 1 else "second"}-round pick')
    who = ', '.join(name(o) for o in owners)
    return (f'<div class="rule" data-orig="{orig}" data-round="{rnd}"><div class="h">{head_}</div>{esc(text)}'
            f'<div class="small">Can end up with: {esc(who)}</div><div class="live"></div></div>')

def team_page(t):
    url = f'{SITE}teams/{t.lower()}/'
    nm = name(t)
    title = f"{nm} 2027 NBA Draft Picks, Lottery Odds and Needs | Gar's Scouting Report"
    desc = f"Every 2027 first and second-round pick the {nm} own or owe, with protections and swaps, live lottery odds, team needs and the best fits on Gar's big board."
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url,
          "about": {"@type": "SportsTeam", "name": nm, "sport": "Basketball", "memberOf": {"@type": "SportsOrganization", "name": "NBA"}}}
    own1 = [(o, 1, R1[o]) for o in R1 if o == t]
    in1 = [(o, 1, R1[o]) for o in R1 if o != t and t in R1[o][0]]
    own2 = [(o, 2, R2[o]) for o in R2 if o == t]
    in2 = [(o, 2, R2[o]) for o in R2 if o != t and t in R2[o][0]]
    out = [head(title, desc, url, 2, ld)]
    out.append(f'<div class="crumb small" style="margin-top:14px"><a href="../">Teams</a> › {esc(nm)}</div>')
    out.append(f'''<div class="th"><div class="big" style="background:{NBA[t][2]}">{t}</div>
      <div><h1>{esc(nm)}</h1><div class="meta">{NBA[t][3]}ern Conference · <span id="t-rec">record loading</span></div></div><div></div></div>
      <div class="kpis"><div><span>Projected first-rounders</span><b id="k-r1">-</b><span>average, from 5,000 lottery sims</span></div>
      <div><span>Projected second-rounders</span><b id="k-r2">-</b><span>average</span></div>
      <div><span>Own pick</span><b id="k-own">-</b><span id="k-own-s">if the season ended today</span></div>
      <div><span>Top need</span><b id="k-need">-</b><span id="k-need-s">from ESPN player stats</span></div></div>''')
    out.append('<div class="lay"><main>')
    out.append('<section class="sec"><h2>2027 first-round picks</h2>' + ''.join(rule_block(*x, t, '../') for x in own1 + in1) + '</section>')
    out.append('<section class="sec"><h2>2027 second-round picks</h2>' + ''.join(rule_block(*x, t, '../') for x in own2 + in2) + '</section>')
    out.append(f'''<section class="sec"><h2>Lottery outlook</h2><div id="lot" class="small">Loading live standings…</div></section>
      <div class="pagenote">Pick terms from Hoops Rumors (first round, Sept 2026) and RealGM (second round, Nov 24, 2026). Trades after those dates are not reflected. Live numbers use ESPN standings and the 3-2-1 lottery rules. See every pick on the <a href="../../draft-picks/">2027 pick tracker</a>.</div>''')
    out.append('</main><aside class="side">')
    out.append('<div class="card"><h3>Team needs</h3><div id="needs" class="small">Loading…</div></div>')
    out.append('<div class="card"><h3>Best fits on my board</h3><div id="fits" class="small">Loading…</div></div>')
    out.append(f'<div class="card"><h3>Mock for {esc(NBA[t][1])}</h3><p class="small">Pick for this team and let the CPU draft the rest.</p><a class="btn primary" href="../../mock/">Open the mock draft</a></div>')
    out.append('</aside></div>')
    out.append(f'</div>\n<script src="../../tools/tools.js?v={V}"></script>\n<script src="../../tools/teams.js?v={V}"></script>\n<script>GSRTeams.teamPage("{t}")</script>\n</body>\n</html>\n')
    return ''.join(out)

def teams_index():
    url = SITE + 'teams/'
    title = "NBA Teams: 2027 Draft Picks, Lottery Odds and Needs | Gar's Scouting Report"
    desc = "All 30 NBA teams with every 2027 draft pick they own or owe, live lottery odds and team needs."
    out = [head(title, desc, url, 1, {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": url})]
    out.append('<div class="hero"><div class="kicker">2027 NBA Draft</div><h1>Teams</h1><p>Every team\'s 2027 picks, with protections and swaps spelled out, plus live lottery odds and team needs. Want every pick in one place? Use the <a href="../draft-picks/">pick tracker</a>.</p></div>')
    for conf in ('East', 'West'):
        out.append(f'<h2>{conf}ern Conference</h2><div class="tgrid">')
        for t in sorted([a for a in NBA if NBA[a][3] == conf], key=name):
            out.append(f'<a class="tcard" href="{t.lower()}/"><span class="chip-b" style="background:{NBA[t][2]}">{t}</span><span><span class="n">{esc(name(t))}</span><br><span class="small" data-rec="{t}"></span></span></a>')
        out.append('</div>')
    out.append(f'</div>\n<script src="../tools/tools.js?v={V}"></script>\n<script src="../tools/teams.js?v={V}"></script>\n<script>GSRTeams.indexPage()</script>\n</body>\n</html>\n')
    return ''.join(out)

def tracker():
    url = SITE + 'draft-picks/'
    title = "2027 NBA Draft Pick Tracker: Every Pick, Owner and Protection | Gar's Scouting Report"
    desc = "Who owns every 2027 NBA Draft pick. Projected order under the 3-2-1 lottery, the chance each team ends up with each conditional pick, and every protection and swap."
    out = [head(title, desc, url, 1, {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url})]
    out.append('''<div class="hero"><div class="kicker">2027 NBA Draft</div><h1>Pick Tracker</h1>
      <p>Every 2027 pick, who owns it and what it depends on. The projected order uses the standings right now and the expected result of the 3-2-1 lottery. The owner column comes from 5,000 simulated lotteries, so conditional picks show how often they actually convey.</p></div>
      <div class="note" id="src">Loading live standings…</div>
      <h2>First round</h2><div class="scrollx"><table class="tbl" id="r1"></table></div>
      <h2>Second round</h2><div class="scrollx"><table class="tbl" id="r2"></table></div>
      <h2>Picks per team</h2><div class="scrollx"><table class="tbl" id="per"></table></div>
      <h2>Every pick, in plain words</h2>''')
    for rnd, R in ((1, R1), (2, R2)):
        out.append(f'<h3 style="margin-top:14px">{"First" if rnd == 1 else "Second"} round</h3>')
        for o in sorted(R, key=name):
            out.append(f'<div class="rule"><div class="h">{chip(o)} <a class="tlink" href="../teams/{o.lower()}/">{esc(name(o))}</a></div>{esc(R[o][1])}</div>')
    out.append('<div class="pagenote">First-round terms from Hoops Rumors (Sept 2026). Second-round terms from RealGM (Nov 24, 2026). Trades after those dates are not reflected.</div>')
    out.append(f'</div>\n<script src="../tools/tools.js?v={V}"></script>\n<script src="../tools/teams.js?v={V}"></script>\n<script>GSRTeams.trackerPage()</script>\n</body>\n</html>\n')
    return ''.join(out)

def build(root):
    for t in NBA:
        d = os.path.join(root, 'teams', t.lower()); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w').write(team_page(t))
    open(os.path.join(root, 'teams', 'index.html'), 'w').write(teams_index())
    os.makedirs(os.path.join(root, 'draft-picks'), exist_ok=True)
    open(os.path.join(root, 'draft-picks', 'index.html'), 'w').write(tracker())
    json.dump({'r1': {k: v[0] for k, v in R1.items()}, 'r2': {k: v[0] for k, v in R2.items()}}, open(os.path.join(root, 'tools', 'pickrules.json'), 'w'))

if __name__ == '__main__':
    build(sys.argv[1]); print('team pages built')

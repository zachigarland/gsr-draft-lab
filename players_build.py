"""Builds one static page per prospect (players/<slug>/index.html), a players index page and the sitemap.
Static HTML on purpose: Google reads it without running any JavaScript.
Usage: python3 players_build.py <out_root> "<Nov 25, 2026>" <2026-11-25>
<out_root> is the site folder (the one that holds index.html)."""
import json, os, re, sys, html, unicodedata
W = os.path.dirname(os.path.abspath(__file__)) + '/'
SITE = 'https://zachigarland.github.io/gsr-draft-lab/'
V = '20261125d'
TIERNAME = {'A': 'Tier A', 'B': 'Tier B', 'C': 'Tier C', 'D': 'Tier D', 'W': 'Watchlist'}
OUTLETS = [('espn', 'ESPN'), ('br', 'Bleacher Report'), ('cbs', 'CBS Sports'), ('ndr', 'NBA Draft Room'),
           ('tk', 'Tankathon'), ('fs', 'FanSided'), ('ho', 'HoopObsession')]

def esc(s): return html.escape(str(s if s is not None else ''), quote=True)
def slug(s):
    s = unicodedata.normalize('NFD', s); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def grp(pos):
    p = pos.upper()
    if ('C' in p or 'PF' in p) and 'SF' not in p: return 'B'
    if 'PG' in p or p in ('SG', 'SG/PG'): return 'G'
    return 'W'
def load(path, default):
    try: return json.load(open(path))
    except Exception: return default

def team_tag(team, TEAMS):
    t = TEAMS.get(team)
    if not t: return f'<span class="tm" style="background:#E6EBF1;color:#33414F">{esc(team[:4].upper())}</span>'
    return f'<span class="tm" style="background:{t[1]};color:{t[2]}">{esc(t[0])}</span>'

def age_txt(p):
    if p.get('age') is None: return ''
    return ('about ' if p.get('age_est') else '') + f"{float(p['age']):.1f}"

PAGE_CSS = """
.crumb{font-size:13px;color:var(--muted);margin:14px 0 0}
.crumb a{color:var(--muted)}
.ph{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;padding:16px 0 18px;border-bottom:1px solid var(--line)}
.ph .rk{font-family:var(--display);font-size:78px;line-height:.9;color:var(--navy);text-align:center;min-width:86px}
.ph .rk small{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.8px;color:var(--muted)}
.ph h1{font-family:var(--display);font-weight:400;font-size:clamp(40px,6vw,60px);line-height:.95;margin:0;color:var(--navy)}
.ph .meta{margin-top:6px;font-size:15px;color:var(--muted);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.ph .tiers{display:flex;flex-direction:column;gap:6px;align-items:flex-end}
.tierpill{font-family:var(--display);font-size:18px;letter-spacing:.4px;color:#fff;padding:4px 12px;border-radius:6px}
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid var(--line);border-radius:10px;margin:16px 0;background:var(--panel)}
.strip>div{padding:12px 14px;border-left:1px solid var(--line)}.strip>div:first-child{border-left:0}
.strip .lab{display:block;margin-bottom:4px}
.strip b{font-family:var(--display);font-weight:400;font-size:28px;color:var(--navy)}
.strip span.s{display:block;font-size:12.5px;color:var(--muted)}
.lay{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:24px;align-items:start}
.sec{margin-bottom:22px}
.sec h2{margin:0 0 8px}
.sec p{margin:6px 0;font-size:15.5px;line-height:1.55}
.sec h4{font-family:var(--mono);font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:var(--muted);margin:14px 0 4px;font-weight:500}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.badges{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 8px}
.badge{border:1px solid var(--line);background:#fff;border-radius:999px;padding:4px 10px;font-size:13px;font-weight:600}
.comps{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:6px 0}
.comps>div{padding:10px 12px;border-left:1px solid var(--line);background:#fff}.comps>div:first-child{border-left:0}
.comps span{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.6px;text-transform:uppercase;color:var(--muted)}
.comps b{font-size:16px}
.side .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:14px}
.side .card h3{margin-bottom:6px}
.side a.pl{display:flex;gap:8px;align-items:center;padding:6px 0;text-decoration:none;color:var(--fg);border-top:1px solid var(--line)}
.side a.pl:first-of-type{border-top:0}
.side a.pl b{font-family:var(--display);font-weight:400;font-size:20px;color:var(--navy);min-width:26px;text-align:center}
.side a.pl:hover span.n{color:var(--accent)}
.cta{display:flex;gap:8px;flex-wrap:wrap}
.cta a{text-decoration:none}
.lastg{background:#FFF7F2;border:1px solid #F3D3BF;border-radius:8px;padding:8px 12px;font-size:14.5px;margin:8px 0}
.srcs{font-size:13px;word-break:break-word}
.srcs li{margin:4px 0}
.pn{display:flex;justify-content:space-between;gap:10px;margin-top:20px;flex-wrap:wrap}
.pn a{text-decoration:none;font-weight:600}
@media (max-width:900px){.lay{grid-template-columns:1fr}}
@media (max-width:640px){.ph{grid-template-columns:auto 1fr}.ph .tiers{grid-column:1/-1;flex-direction:row;align-items:center}.ph .rk{font-size:60px;min-width:64px}
  .strip{grid-template-columns:1fr 1fr}.strip>div:nth-child(3){border-left:0}.strip>div:nth-child(n+3){border-top:1px solid var(--line)}
  .grid2,.comps{grid-template-columns:1fr}.comps>div{border-left:0;border-top:1px solid var(--line)}.comps>div:first-child{border-top:0}}
"""
TIERCOL = {'A': '#E2500A', 'B': '#1F5FA8', 'C': '#2E8B57', 'D': '#6B7A8C', 'W': '#7B61C9'}

def head(title, desc, url, depth, extra_ld):
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
<style>{PAGE_CSS}</style>
<script type="application/ld+json">{json.dumps(extra_ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
"""

def stat_table(p, e):
    sl = p.get('sl') or {}
    if not sl.get('g'): return ''
    lg = sl.get('lg') or 'NCAA'
    def f(v, pct=False):
        if v is None: return '-'
        return f"{v:.1f}" if isinstance(v, (int, float)) else esc(v)
    cols = [('G', sl.get('g')), ('MIN', e.get('mp') if e else None), ('PTS', sl.get('pts')), ('REB', sl.get('reb')), ('AST', sl.get('ast')),
            ('STL', sl.get('stl')), ('BLK', sl.get('blk')), ('FG%', sl.get('fg')), ('3P%', sl.get('tp')), ('FT%', sl.get('ft')),
            ('TS%', (e.get('ts') or 0) * 100 if e and e.get('ts') else None)]
    th = ''.join(f'<th class="num">{c}</th>' for c, _ in cols)
    td = ''.join(f'<td class="num">{(str(v) if c=="G" else f(v))}</td>' for c, v in cols)
    per36 = ''
    if e and e.get('p36'):
        per36 = (f'<tr><td class="small">Per 36 min</td><td class="num">-</td><td class="num">36.0</td><td class="num">{e["p36"]:.1f}</td>'
                 f'<td class="num">{e["r36"]:.1f}</td><td class="num">{e["a36"]:.1f}</td><td class="num">{e["s36"]:.1f}</td>'
                 f'<td class="num">{e["b36"]:.1f}</td><td class="num" colspan="4"></td></tr>')
    return (f'<div class="scrollx"><table class="tbl"><tr><th>2026-27</th>{th}</tr>'
            f'<tr><td>{esc(lg)}</td>{td}</tr>{per36}</table></div>')

def player_page(p, ctx):
    R, TEAMS, E, LG, txt = ctx['R'], ctx['TEAMS'], ctx['E'], ctx['LG'], ctx['txt']
    r = R.get(p['name'], {})
    s = slug(p['name']); url = f'{SITE}players/{s}/'
    e = E.get(p['name'])
    tier = p.get('tier', 'W')
    title = f"{p['name']} Scouting Report, 2027 NBA Draft | Gar's Scouting Report"
    why = r.get('why') or p.get('note', '')
    desc = f"No. {p['rank']} on Gar's 2027 NBA Draft big board. {p['name']} ({p['pos']}, {p['team']}): {why}"[:300]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "name": title, "url": url, "dateModified": ctx['iso'],
         "mainEntity": {"@type": "Person", "name": p['name'], "affiliation": {"@type": "SportsTeam", "name": p['team']},
                        "jobTitle": "Basketball player", "description": why}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "2027 Big Board", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Players", "item": SITE + 'players/'},
            {"@type": "ListItem", "position": 3, "name": p['name'], "item": url}]}]}
    out = [head(title, desc, url, 2, ld)]
    out.append(f'<div class="crumb"><a href="../../">2027 Big Board</a> › <a href="../">Players</a> › {esc(p["name"])}</div>')
    meta = ' · '.join(x for x in [esc(p['pos']), esc(p.get('ht', '')), (esc(p['wt']) + ' lbs') if p.get('wt') else '', esc(p.get('cls', '')),
                                  ('draft-night age ' + age_txt(p)) if age_txt(p) else ''] if x)
    out.append(f'''<div class="ph"><div class="rk"><small>GSR RANK</small>{p["rank"]}</div>
      <div><h1>{esc(p["name"])}</h1><div class="meta">{team_tag(p["team"], TEAMS)} <b style="color:var(--fg)">{esc(p["team"])}</b> · {meta}</div></div>
      <div class="tiers"><span class="tierpill" style="background:{TIERCOL.get(tier, "#999")}">{TIERNAME.get(tier, tier)}</span></div></div>''')
    cons = p.get('consensus'); delta = p.get('delta')
    mv = p.get('move') or ''
    mvhead = re.match(r'^(Up \d+ since Nov 18|Down \d+ since Nov 18|Holds|New)', mv)
    out.append(f'''<div class="strip">
      <div><span class="lab">Gar rank</span><b>No. {p["rank"]}</b><span class="s">{TIERNAME.get(tier, tier)}</span></div>
      <div><span class="lab">Outlet consensus</span><b>{f"{cons:.1f}" if isinstance(cons, (int, float)) else "-"}</b><span class="s">{p.get("outlets") or 0} outlets ranked him</span></div>
      <div><span class="lab">Gar vs outlets</span><b class="{"up" if (delta or 0) > 0 else "down" if (delta or 0) < 0 else ""}">{f"{delta:+.1f}" if isinstance(delta, (int, float)) else "-"}</b><span class="s">+ means I have him higher</span></div>
      <div><span class="lab">Movement</span><b style="font-size:22px">{esc(mvhead.group(1) if mvhead else "-")}</b><span class="s">board update {esc(txt)}</span></div></div>''')
    out.append('<div class="lay"><main>')
    # stats
    out.append('<section class="sec"><h2>2026-27 stats</h2>' + (stat_table(p, e) or '<p class="small">No 2026-27 games yet.</p>'))
    if p.get('early'): out.append(f'<p class="small">{esc(p["early"])}</p>')
    lg = LG.get(p['name'])
    if lg:
        tp = f", {lg['tpm']}-{lg['tpa']} from three" if lg.get('tpa') else ''
        out.append(f'<div class="lastg"><b>Last game:</b> {lg["pts"]} points, {lg["reb"]} rebounds, {lg["ast"]} assists, {lg["stl"]} steals, {lg["blk"]} blocks in {lg["min"]} minutes{tp}.</div>')
    out.append('</section>')
    # report
    if r:
        out.append('<section class="sec"><h2>Scouting report</h2>')
        out.append('<div class="badges">' + ''.join(f'<span class="badge">{esc(b)}</span>' for b in r.get('badges', [])) + '</div>')
        out.append(f'<p><b>Why No. {p["rank"]}:</b> {esc(r.get("why", ""))}</p>')
        out.append(f'<div class="grid2"><div><h4>Offense</h4><p>{esc(r.get("off", ""))}</p></div><div><h4>Defense</h4><p>{esc(r.get("def", ""))}</p></div></div>')
        out.append(f'<div class="grid2"><div><h4>Strengths</h4><p>{esc(r.get("str", ""))}</p></div><div><h4>Weaknesses</h4><p>{esc(r.get("weak", ""))}</p></div></div>')
        out.append(f'<h4>Swing skill</h4><p>{esc(r.get("swing", ""))}</p>')
        out.append('</section>')
    out.append(f'''<section class="sec"><h2>NBA comps</h2><div class="comps"><div><span>Ceiling</span><b>{esc(p.get("boom", ""))}</b></div>
      <div><span>Likely</span><b>{esc(p.get("proj", ""))}</b></div><div><span>Floor</span><b>{esc(p.get("bust", ""))}</b></div></div>
      {f"<p>{esc(r.get('why_comp'))}</p>" if r.get('why_comp') else ""}</section>''')
    if mv: out.append(f'<section class="sec"><h2>Board movement</h2><p>{esc(mv)}</p><p class="small">Written for the Nov 18 to 24 board update, so numbers in this note can trail the stat table above.</p></section>')
    # outlets
    rows = ''.join(f'<tr><td>{n}</td><td class="num">{esc(p[k])}</td></tr>' for k, n in OUTLETS if isinstance(p.get(k), (int, float)))
    out.append('<section class="sec"><h2>Where the outlets have him</h2>' + (
        f'<div class="scrollx" style="max-width:420px"><table class="tbl"><tr><th>Outlet</th><th class="num">Rank</th></tr>{rows}'
        f'<tr><td><b>Gar\'s Scouting Report</b></td><td class="num"><b>{p["rank"]}</b></td></tr></table></div>' if rows else '<p class="small">No outlet rankings yet.</p>'))
    if r.get('outlets'): out.append(f'<p>{esc(r["outlets"])}</p>')
    out.append('</section>')
    # role and background
    if p.get('depth') or p.get('outlook'):
        out.append('<section class="sec"><h2>Role and situation</h2>')
        if p.get('depth'): out.append(f'<p>{esc(p["depth"])}</p>')
        if p.get('outlook'): out.append(f'<p>{esc(p["outlook"])}</p>')
        out.append('</section>')
    if p.get('stats') or p.get('note'):
        out.append('<section class="sec"><h2>Background</h2>')
        if p.get('note'): out.append(f'<p>{esc(p["note"])}</p>')
        if p.get('stats'): out.append(f'<p class="small">{esc(p["stats"])}</p>')
        out.append('</section>')
    src = [u for u in (p.get('src') or []) if isinstance(u, str) and u.startswith('http')]
    if src:
        short = lambda u: re.sub(r'^https?://(www[.])?', '', u)[:90]
        out.append('<section class="sec"><h2>Sources</h2><ul class="srcs">' + ''.join(
            '<li><a href="' + esc(u) + '" rel="noopener nofollow">' + esc(short(u)) + '</a></li>' for u in src) + '</ul></section>')
    prv, nxt = ctx['by_rank'].get(p['rank'] - 1), ctx['by_rank'].get(p['rank'] + 1)
    out.append('<div class="pn">' + (f'<a href="../{slug(prv["name"])}/">‹ No. {prv["rank"]} {esc(prv["name"])}</a>' if prv else '<span></span>') +
               (f'<a href="../{slug(nxt["name"])}/">No. {nxt["rank"]} {esc(nxt["name"])} ›</a>' if nxt else '') + '</div>')
    out.append('</main><aside class="side">')
    out.append(f'''<div class="card"><h3>Use him in the tools</h3><div class="cta">
      <a class="btn primary" href="../../mock/">Mock draft</a><a class="btn" href="../../bigboard/">Board builder</a><a class="btn" href="../../?p={s}">See him on the board</a><a class="btn" href="../../compare/?p={s}">Compare him</a></div></div>''')
    def plist(title, ps):
        if not ps: return ''
        return f'<div class="card"><h3>{title}</h3>' + ''.join(
            f'<a class="pl" href="../{slug(q["name"])}/"><b>{q["rank"]}</b>{team_tag(q["team"], TEAMS)}<span><span class="n">{esc(q["name"])}</span><br><span class="small">{esc(q["pos"])} · {esc(q["team"])}</span></span></a>' for q in ps) + '</div>'
    g = grp(p['pos'])
    near = sorted([q for q in ctx['board'] if q['name'] != p['name'] and grp(q['pos']) == g], key=lambda q: abs(q['rank'] - p['rank']))[:5]
    out.append(plist({'G': 'Guards near him on the board', 'W': 'Wings near him on the board', 'B': 'Bigs near him on the board'}[g], sorted(near, key=lambda q: q['rank'])))
    mates = [q for q in ctx['board'] if q['team'] == p['team'] and q['name'] != p['name']]
    out.append(plist(f'Also on the board from {esc(p["team"])}', mates))
    out.append('</aside></div>')
    out.append(f'<div class="pagenote">Report and rank by Gar\'s Scouting Report. Board updated {esc(txt)}. Stats from ESPN and RealGM.</div>')
    out.append('</div>\n</body>\n</html>\n')
    return s, ''.join(out)

def players_index(board, TEAMS, txt, iso):
    url = SITE + 'players/'
    title = f"2027 NBA Draft Prospects: All {len(board)} Scouting Reports | Gar's Scouting Report"
    desc = "Every prospect on Gar's 2027 NBA Draft big board, with full scouting reports, stats, NBA comps and outlet rankings."
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": url, "dateModified": iso}
    out = [head(title, desc, url, 1, ld).replace('../tools/', '../tools/')]
    out.append(f'''<div class="hero"><div class="kicker">2027 NBA Draft</div><h1>Prospects</h1>
      <p>Every player on my board with a full page: scouting report, stats, comps, outlet ranks and sources. Updated {esc(txt)}.</p></div>
      <div class="filters" style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0"><input type="search" id="pq" placeholder="Filter by name, school or position" style="flex:1 1 240px" aria-label="Filter prospects"></div>''')
    rows = ''.join(f'<tr data-q="{esc((p["name"]+" "+p["team"]+" "+p["pos"]).lower())}"><td class="num">{p["rank"]}</td><td><span class="tier {p["tier"]}">{p["tier"]}</span></td>'
                   f'<td><a href="{slug(p["name"])}/"><b>{esc(p["name"])}</b></a></td><td>{team_tag(p["team"], TEAMS)} {esc(p["team"])}</td><td>{esc(p["pos"])}</td>'
                   f'<td class="hide-m">{esc(p.get("ht",""))}</td><td class="num hide-m">{age_txt(p)}</td></tr>' for p in board)
    out.append(f'<div class="scrollx"><table class="tbl" id="pt"><tr><th class="num">Rank</th><th>Tier</th><th>Player</th><th>School / club</th><th>Pos</th><th class="hide-m">Ht</th><th class="num hide-m">Age</th></tr>{rows}</table></div>')
    out.append("""<script>document.getElementById('pq').addEventListener('input',e=>{const t=e.target.value.toLowerCase();document.querySelectorAll('#pt tr[data-q]').forEach(r=>r.hidden=t&&!r.dataset.q.includes(t));});</script>""")
    out.append('</div>\n</body>\n</html>\n')
    return ''.join(out)

def sitemap(board, iso):
    urls = [('', 'daily'), ('players/', 'daily'), ('stats/', 'daily'), ('compare/', 'weekly'), ('teams/', 'daily'), ('draft-picks/', 'daily'), ('mock/', 'weekly'), ('bigboard/', 'weekly'), ('lottery/', 'weekly'), ('about/', 'monthly')]
    urls += [(f'teams/{t}/', 'daily') for t in ['atl','bos','bkn','cha','chi','cle','dal','den','det','gsw','hou','ind','lac','lal','mem','mia','mil','min','nop','nyk','okc','orl','phi','phx','por','sac','sas','tor','uta','was']]
    urls += [(f'players/{slug(p["name"])}/', 'daily') for p in board]
    body = ''.join(f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{iso}</lastmod>\n    <changefreq>{c}</changefreq>\n  </url>\n' for u, c in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'

# ---------- data file, stats leaderboard ----------
def player_data(board, R, E):
    rows = []
    for p in board:
        sl, e, r = p.get('sl') or {}, E.get(p['name']) or {}, R.get(p['name'], {})
        def rnd(v, n=1): return round(v, n) if isinstance(v, (int, float)) else None
        rows.append({
            'id': slug(p['name']), 'name': p['name'], 'rank': p['rank'], 'tier': p['tier'], 'team': p['team'], 'pos': p['pos'], 'grp': grp(p['pos']),
            'ht': p.get('ht'), 'wt': p.get('wt'), 'cls': p.get('cls'), 'age': p.get('age'), 'age_est': bool(p.get('age_est')),
            'lg': sl.get('lg') or ('NCAA' if e else None), 'pro': bool(sl.get('lg') and sl.get('lg') != 'NCAA'),
            'g': sl.get('g'), 'mp': rnd(e.get('mp')), 'pts': sl.get('pts'), 'reb': sl.get('reb'), 'ast': sl.get('ast'), 'stl': sl.get('stl'), 'blk': sl.get('blk'),
            'to': rnd(e.get('to')), 'fg': sl.get('fg'), 'tp': sl.get('tp'), 'tpa': rnd(e['tpa'] / e['g']) if e.get('g') and e.get('tpa') is not None else None,
            'ft': sl.get('ft'), 'ts': rnd(e['ts'] * 100) if e.get('ts') else None,
            'p36': rnd(e.get('p36')), 'r36': rnd(e.get('r36')), 'a36': rnd(e.get('a36')), 's36': rnd(e.get('s36')), 'b36': rnd(e.get('b36')),
            'cons': p.get('consensus'), 'delta': p.get('delta'), 'outlets': p.get('outlets'),
            'boom': p.get('boom'), 'proj': p.get('proj'), 'bust': p.get('bust'), 'badges': r.get('badges', []), 'why': r.get('why', ''),
            'off': r.get('off', ''), 'def': r.get('def', ''), 'swing': r.get('swing', ''),
            'ranks': {k: p.get(k) for k, _ in OUTLETS if isinstance(p.get(k), (int, float))}})
    return rows

STAT_COLS = [('g', 'G', 0), ('mp', 'MIN', 1), ('pts', 'PTS', 1), ('reb', 'REB', 1), ('ast', 'AST', 1), ('stl', 'STL', 1), ('blk', 'BLK', 1), ('to', 'TOV', 1),
             ('fg', 'FG%', 1), ('tp', '3P%', 1), ('tpa', '3PA', 1), ('ft', 'FT%', 1), ('ts', 'TS%', 1)]

def stats_page(rows, TEAMS, txt, iso):
    url = SITE + 'stats/'
    title = "2027 NBA Draft Prospect Stats: Sortable Leaderboard | Gar's Scouting Report"
    desc = "Sortable 2026-27 stats for every prospect on Gar's 2027 NBA Draft big board. Filter by position, tier and league, and switch between per game and per 36 minutes."
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "2027 NBA Draft prospect stats", "url": url, "dateModified": iso,
          "description": desc, "creator": {"@type": "Organization", "name": "Gar's Scouting Report"}}
    out = [head(title, desc, url, 1, ld)]
    out.append(f"""<style>
.sb{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:10px 0}}
.sb input[type=search]{{flex:1 1 220px}}
#st th{{cursor:pointer;user-select:none}}
#st th[aria-sort=descending]::after{{content:" ▼";font-size:9px}}#st th[aria-sort=ascending]::after{{content:" ▲";font-size:9px}}
#st td.top{{background:#FFF1E8;font-weight:700}}
#st td.pl a{{font-weight:700;color:var(--fg);text-decoration:none}}#st td.pl a:hover{{color:var(--accent)}}
#st td.pl{{white-space:nowrap}}
.cmpbar{{position:sticky;bottom:0;background:var(--navy);color:#fff;border-radius:10px 10px 0 0;padding:10px 14px;display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-top:10px}}
.cmpbar .btn{{background:var(--accent);border-color:var(--accent);color:#fff}}
</style>
<div class="hero"><div class="kicker">2027 NBA Draft</div><h1>Prospect Stats</h1>
<p>2026-27 numbers for every player on my board. Click any column to sort, filter by position, tier or league, and check up to four players to compare them. Updated {esc(txt)}.</p></div>
<div class="sb">
  <input type="search" id="sq" placeholder="Filter by name or school" aria-label="Filter players">
  <div class="seg" id="s-pos"><button data-v="" aria-pressed="true">All</button><button data-v="G">Guards</button><button data-v="W">Wings</button><button data-v="B">Bigs</button></div>
  <div class="seg" id="s-lg"><button data-v="" aria-pressed="true">All leagues</button><button data-v="ncaa">College</button><button data-v="pro">Pro / intl</button></div>
  <div class="seg" id="s-mode"><button data-v="pg" aria-pressed="true">Per game</button><button data-v="36">Per 36</button></div>
  <div class="ctl"><label for="s-tier">Tier</label><select id="s-tier"><option value="">All tiers</option><option>A</option><option>B</option><option>C</option><option>D</option><option value="W">Watchlist</option></select></div>
  <div class="ctl"><label for="s-min">Min games</label><select id="s-min"><option value="0">Any</option><option value="3">3+</option><option value="5" selected>5+</option><option value="8">8+</option></select></div>
</div>""")
    head_ = '<tr><th data-k="cmp" style="cursor:default"><span class="lab">Cmp</span></th><th data-k="rank" class="num">Rank</th><th data-k="name">Player</th><th data-k="pos">Pos</th><th data-k="age" class="num">Age</th>' + \
        ''.join(f'<th data-k="{k}" class="num">{lab}</th>' for k, lab, _ in STAT_COLS) + '<th data-k="cons" class="num">Cons</th></tr>'
    body = []
    for r in rows:
        cells = ''.join(f'<td class="num">{"" if r[k] is None else (r[k] if n == 0 else f"{r[k]:.1f}")}</td>' for k, _, n in STAT_COLS)
        body.append(f'<tr data-id="{r["id"]}"><td><input type="checkbox" aria-label="Compare {esc(r["name"])}"></td><td class="num">{r["rank"]}</td>'
                    f'<td class="pl"><span class="tier {r["tier"]}">{r["tier"]}</span> <a href="../players/{r["id"]}/">{esc(r["name"])}</a> <span class="small">{esc(r["team"])}</span></td>'
                    f'<td>{esc(r["pos"])}</td><td class="num">{age_txt({"age": r["age"], "age_est": r["age_est"]})}</td>{cells}'
                    '<td class="num">' + ('' if r['cons'] is None else '%.1f' % r['cons']) + '</td></tr>')
    out.append(f'<div class="scrollx"><table class="tbl" id="st"><thead>{head_}</thead><tbody>{"".join(body)}</tbody></table></div>')
    out.append('<div class="small" id="scount" style="margin-top:6px"></div>')
    out.append('<div class="cmpbar" id="cmpbar" hidden><span id="cmpn"></span><a class="btn" id="cmpgo" href="../compare/">Compare</a></div>')
    out.append('<div class="pagenote">College stats from ESPN through the latest refresh. Pro and international stats from RealGM and league sites, which do not always list minutes, turnovers or TS%. Per-36 numbers are for college players only. "Cons" is the average rank across ESPN, B/R, CBS and NBA Draft Room.</div>')
    out.append(f'</div>\n<script src="../tools/tools.js?v={V}"></script>\n<script src="../tools/stats.js?v={V}"></script>\n</body>\n</html>\n')
    return ''.join(out)

def build(out_root, txt, iso):
    sys.path.insert(0, W)
    import ringer_patch
    TEAMS = ringer_patch.TEAMS
    board = sorted(load(W + 'board_current.json', []), key=lambda p: p['rank'])
    ctx = dict(R=load(W + 'reports_all.json', {}), TEAMS=TEAMS, E=load(W + 'espn_current.json', {}),
               LG={g['name']: g for g in load(W + 'last_games.json', [])}, txt=txt, iso=iso, board=board,
               by_rank={p['rank']: p for p in board})
    pdir = os.path.join(out_root, 'players'); os.makedirs(pdir, exist_ok=True)
    keep = set()
    for p in board:
        s, page = player_page(p, ctx); keep.add(s)
        os.makedirs(os.path.join(pdir, s), exist_ok=True)
        open(os.path.join(pdir, s, 'index.html'), 'w').write(page)
    open(os.path.join(pdir, 'index.html'), 'w').write(players_index(board, TEAMS, txt, iso))
    rows = player_data(board, ctx['R'], ctx['E'])
    json.dump({'asof': txt, 'players': rows}, open(os.path.join(pdir, 'data.json'), 'w'), ensure_ascii=False)
    sdir = os.path.join(out_root, 'stats'); os.makedirs(sdir, exist_ok=True)
    open(os.path.join(sdir, 'index.html'), 'w').write(stats_page(rows, TEAMS, txt, iso))
    open(os.path.join(out_root, 'sitemap.xml'), 'w').write(sitemap(board, iso))
    # players who left the board keep their old page (so links do not break) but drop out of the sitemap
    return len(keep)

if __name__ == '__main__':
    n = build(sys.argv[1], sys.argv[2], sys.argv[3])
    print('player pages:', n)

# GSR daily refresh. Usage: python3 daily.py espn_raw.txt "Nov 24" 2026-11-25 "Nov 25, 2026"
# espn_raw.txt lines: "<Board Name> : GP MIN FGM FGA FTM FTA 3PM 3PA PTS OR DR REB AST TO STL BLK" (ESPN team-stats totals)
import json, re, sys, subprocess, shutil, os
W = '/home/claude/work/'
raw, thru, today_iso, today_txt = sys.argv[1:5]
board = json.load(open(W + 'board_current.json'))
names = {p['name'].replace('ü', 'u'): p['name'] for p in board}
E = {}
for l in open(raw):
    if ' : ' not in l: continue
    k, v = l.rsplit(' : ', 1); k = k.strip().replace('ü', 'u')
    if k not in names: print('unknown name', k); continue
    g, mn, fgm, fga, ftm, fta, tpm, tpa, pts, orb, drb, reb, ast, to, stl, blk = map(int, v.split())
    if not g or not mn: continue
    E[names[k]] = dict(g=g, mp=mn/g, pts=pts/g, reb=reb/g, ast=ast/g, stl=stl/g, blk=blk/g, to=to/g,
        fg=100*fgm/fga if fga else 0, tp=100*tpm/tpa if tpa else 0, tpm=tpm, tpa=tpa, ft=100*ftm/fta if fta else None,
        ftm=ftm, fta=fta, ts=pts/(2*(fga+0.44*fta)) if fga+fta else 0, min=mn,
        p36=36*pts/mn, r36=36*reb/mn, a36=36*ast/mn, b36=36*blk/mn, s36=36*stl/mn)
old = json.load(open(W + 'espn_current.json'))
changed = []
for p in board:
    o = E.get(p['name'])
    if not o: continue
    if old.get(p['name'], {}).get('g') != o['g']: changed.append(p['name'])
    tp = f"{o['tp']:.1f}% from three ({o['tpm']}-{o['tpa']})" if o['tpa'] else "no threes attempted"
    line = (f"ESPN through {thru}: {o['pts']:.1f} pts, {o['reb']:.1f} reb, {o['ast']:.1f} ast, {o['blk']:.1f} blk, "
            f"{o['fg']:.1f} FG%, {tp}, {o['ts']*100:.1f} TS% ({o['g']} GP, {o['mp']:.1f} min).")
    e = p.get('early') or ''
    p['early'] = re.sub(r'^ESPN through [^:]+: .*?\(\d+ GP, [\d.]+ min\)\.', line, e) if e.startswith('ESPN through') else line
    p['sl'] = dict(g=o['g'], pts=round(o['pts'], 1), reb=round(o['reb'], 1), ast=round(o['ast'], 1), blk=round(o['blk'], 1),
                   stl=round(o['stl'], 1), fg=round(o['fg'], 1) if (o['fg'] or o['tpa']) else None,
                   ft=round(o['ft'], 1) if o['ft'] is not None else None, tp=round(o['tp'], 1) if o['tpa'] else None, lg='NCAA')
    p['move'] = re.sub(r'[\d.]+ points, [\d.]+ rebounds and [\d.]+ assists on [\d.]+ TS% through \d+ games\.',
        f"{o['pts']:.1f} points, {o['reb']:.1f} rebounds and {o['ast']:.1f} assists on {o['ts']*100:.1f} TS% through {o['g']} games.", p.get('move') or '')
merged = dict(old); merged.update(E)
json.dump(merged, open(W + 'espn_current.json', 'w'))
json.dump(board, open(W + 'board_current.json', 'w'), indent=0)
env = dict(os.environ, GSR_THRU=thru, GSR_ISO=today_iso, GSR_TXT=today_txt)
shutil.copy(W + 'site_v63_backup.html', W + 'site/index.html')
subprocess.run(['python3', W + 'build_site_daily.py'], check=True, env=env)
print('updated', len(E), 'players; new games for', len(changed), ':', ', '.join(changed))
games = []
for n in changed:
    a, o = old.get(n), E[n]
    if not a or o['g'] - a['g'] != 1: continue
    t = lambda d, k: d[k] * d['g']
    games.append(dict(name=n, rank=next(p['rank'] for p in board if p['name'] == n),
        pts=round(t(o,'pts')-t(a,'pts')), reb=round(t(o,'reb')-t(a,'reb')), ast=round(t(o,'ast')-t(a,'ast')),
        stl=round(t(o,'stl')-t(a,'stl')), blk=round(t(o,'blk')-t(a,'blk')), tpm=o['tpm']-a['tpm'], tpa=o['tpa']-a['tpa'],
        min=round(o['min']-a['min'])))
games.sort(key=lambda x: -x['pts'])
json.dump(games, open(W + 'last_games.json', 'w'), indent=1)
print('last-game lines (from total deltas):'); [print(' ', g) for g in games[:12]]

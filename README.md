# GSR Draft Lab pipeline (not served)
Clone this branch to /home/claude/work. Daily run:
1. Run fetch_espn.js in a Chrome tab on espn.com, wait ~90s, read window.__t in 900-char slices, save as espn_raw.txt.
2. python3 daily.py espn_raw.txt "<stats-through date, e.g. Nov 24>" <today ISO> "<today, e.g. Nov 25, 2026>"
3. Copy site/index.html to the main branch, bump sitemap.xml lastmod, push main. Commit board_current.json and espn_current.json back to this branch.


## Tools pages
The mock draft, board builder and lottery pages live on main under mock/, bigboard/, lottery/ and tools/. They read the player data from the main index.html at load time, so the daily refresh updates them automatically. tools_patch.py adds the site nav to the main page during each build.


## Player pages
players_build.py writes players/<slug>/index.html for every prospect, players/index.html and sitemap.xml. daily.py runs it after each rebuild, copies the output into /home/claude/gsr-draft-lab and stages it with git add. history.json gets one rank and stat snapshot per day for future movers charts.

## Privacy
No birthdates anywhere in public text. Some prospects are minors. Ages show as draft-night age only.


## Team pages and pick tracker
teams_build.py writes teams/<abbr>/, teams/index.html and draft-picks/index.html with every 2027 pick rule as plain text. It does not need to run daily: the live numbers (records, lottery odds, ownership chances, needs, best fits) come from tools/teams.js in the browser. Rerun it only when a pick trade changes the rules, and update GSR.resolveOwners / resolveOwners2 in tools/tools.js to match.

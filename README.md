# GSR Draft Lab pipeline (not served)
Clone this branch to /home/claude/work. Daily run:
1. Run fetch_espn.js in a Chrome tab on espn.com, wait ~90s, read window.__t in 900-char slices, save as espn_raw.txt.
2. python3 daily.py espn_raw.txt "<stats-through date, e.g. Nov 24>" <today ISO> "<today, e.g. Nov 25, 2026>"
3. Copy site/index.html to the main branch, bump sitemap.xml lastmod, push main. Commit board_current.json and espn_current.json back to this branch.

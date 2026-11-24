import json, re, html as H
def apply(h, board, date_iso="2026-11-23", date_txt="Nov 23, 2026"):
    n = len(board)
    def sub(a, b):
        assert h.count(a) == 1, a
        return h.replace(a, b)
    h = sub("<title>Gar's Scouting Report Draft Lab</title>",
            f"<title>2027 NBA Draft Big Board and Rankings ({date_txt}) | Gar's Scouting Report</title>")
    h = re.sub(r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="2027 NBA Draft big board: {n} prospects ranked with 2026-27 stats, heights, international players and NBA comps. Top 5: '
        + ", ".join(p["name"] for p in board[:5]) + f'. Updated {date_txt} by Gar\'s Scouting Report (@NBATOPSCOUT).">', h, count=1)
    h = h.replace('85 prospects re-ranked', f'{n} prospects re-ranked')
    h = sub('<div class="val" id="s-count">85</div>', f'<div class="val" id="s-count">{n}</div>')
    ld = {"@context": "https://schema.org", "@type": "Article",
          "headline": f"2027 NBA Draft Big Board ({date_txt})",
          "description": f"{n} prospects for the 2027 NBA Draft ranked with stats, heights and comps.",
          "author": {"@type": "Person", "name": "Zach Garland", "url": "https://x.com/NBATOPSCOUT"},
          "publisher": {"@type": "Organization", "name": "Gar's Scouting Report"},
          "datePublished": "2026-09-10", "dateModified": date_iso,
          "image": "https://zachigarland.github.io/gsr-draft-lab/og-nov23w.png",
          "mainEntityOfPage": "https://zachigarland.github.io/gsr-draft-lab/"}
    head_add = ('<link rel="canonical" href="https://zachigarland.github.io/gsr-draft-lab/">\n'
                '<meta name="robots" content="index, follow">\n'
                '<script type="application/ld+json">' + json.dumps(ld) + '</script>\n')
    h = sub('<link rel="preconnect" href="https://fonts.googleapis.com">', head_add + '<link rel="preconnect" href="https://fonts.googleapis.com">')
    rows = "".join(f"<li>{p['rank']}. {H.escape(p['name'])}, {H.escape(p['team'])}, {H.escape(p.get('pos') or '')}, {H.escape(p.get('ht') or '')}</li>" for p in board)
    seo = (f'<section id="seo-list" style="max-width:1100px;margin:40px auto 24px;padding:0 24px;color:#5A6878;font-size:14px;line-height:1.6">'
           f'<h2 style="font-size:18px;color:#0E1A26">2027 NBA Draft Big Board: full rankings ({date_txt})</h2>'
           f'<p>Gar\'s Scouting Report ranks the top {n} prospects for the 2027 NBA Draft, including college freshmen, returning players and international prospects. '
           f'Each player has 2026-27 stats, height, tier, NBA comps and how the ranking compares to ESPN, Bleacher Report, CBS, Tankathon and other mock drafts.</p>'
           f'<details><summary style="cursor:pointer;color:#0E1A26">Text list of all {n} rankings</summary><ol style="list-style:none;padding:0;columns:2">{rows}</ol></details></section>')
    h = sub('</body>', seo + '\n</body>')
    return h

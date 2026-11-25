"""Adds the site nav (Big Board, Mock Draft, Board Builder, Lottery) to the main page.
Safe to run more than once."""

CSS = """<style id="gsr-sitenav">
.gsr-top{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:10px 0;border-bottom:1px solid var(--line)}
.gsr-top .gsr-logo{font-family:var(--display);font-size:22px;letter-spacing:.4px;color:var(--navy);text-decoration:none}
.gsr-nav{display:flex;gap:4px;flex-wrap:wrap}
.gsr-nav a{font-family:var(--display);font-size:18px;letter-spacing:.4px;text-decoration:none;color:var(--navy);padding:5px 10px;border-radius:6px}
.gsr-nav a:hover{background:var(--panel-2)}
.gsr-nav a[aria-current="page"]{background:var(--navy);color:#fff}
.gsr-nav a.new::after{content:"NEW";font-family:var(--mono);font-size:9px;letter-spacing:.5px;background:var(--accent);color:#fff;border-radius:3px;padding:1px 4px;margin-left:5px;vertical-align:3px}
</style>"""

NAV = """<div class="gsr-top"><a class="gsr-logo" href="./">Gar's Scouting Report</a><nav class="gsr-nav" aria-label="Site"><a href="./" aria-current="page">2027 Big Board</a><a class="new" href="mock/">Mock Draft</a><a class="new" href="bigboard/">Board Builder</a><a class="new" href="lottery/">Lottery</a></nav></div>
"""

def apply(h):
    if 'id="gsr-sitenav"' in h:
        return h
    h = h.replace("</head>", CSS + "\n</head>", 1)
    i = h.find('<header class="mast">')
    if i < 0:
        raise RuntimeError("tools_patch: masthead not found")
    return h[:i] + NAV + "  " + h[i:]

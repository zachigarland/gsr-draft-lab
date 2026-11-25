"""Adds the shared site shell (header, nav, prospect search, footer) to the main page.
The shell itself lives in tools/shell.js and tools/shell.css on the main branch.
Safe to run more than once."""

TAG = '<script src="tools/shell.js?v=20261125a" defer></script>'
CSS = '<style id="gsr-shell-fix">.slhead{top:var(--gsr-hd,0px)!important}</style>'

def apply(h):
    if 'tools/shell.js' in h:
        return h
    return h.replace("</head>", CSS + "\n" + TAG + "\n</head>", 1)

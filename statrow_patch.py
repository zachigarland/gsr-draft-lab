# appended step for build_site_v7: per-game stat line in each board row
def apply(h, sub):
    sub('.row>button{all:unset;box-sizing:border-box;display:grid;grid-template-columns:44px minmax(0,1.6fr) 70px minmax(0,1.4fr) 64px 20px;',
        '.row>button{all:unset;box-sizing:border-box;display:grid;grid-template-columns:44px minmax(0,1.25fr) 50px minmax(340px,2.5fr) minmax(0,1fr) 64px 20px;')
    sub('.pos{font-family:var(--mono);font-size:12px;color:var(--muted)}',
        '.pos{font-family:var(--mono);font-size:12px;color:var(--muted)} .sl{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:4px;font-family:var(--mono);font-size:12px;font-variant-numeric:tabular-nums;text-align:right;padding-right:14px} .sl i{font-style:normal;color:var(--muted)} .slhead{display:grid;grid-template-columns:44px minmax(0,1.25fr) 50px minmax(340px,2.5fr) minmax(0,1fr) 64px 20px;gap:12px;padding:4px 6px;position:sticky;top:0;background:var(--bg);z-index:2;border-bottom:1px solid var(--line)} .slhead .sl{font-size:10px;letter-spacing:.08em;color:var(--muted)} .slhead .lab2{grid-column:5/7;font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--muted);text-align:right} .slnote{font-family:var(--mono);font-size:11px;color:var(--muted);margin:4px 0 0}')
    sub('  .row>button .pos,.row>button .rail{display:none}',
        '  .row>button .pos,.row>button .rail{display:none}\n  .row>button .sl{grid-column:2/-1;grid-row:2;font-size:11px}\n  .slhead{grid-template-columns:36px minmax(0,1fr) 56px 16px;gap:8px} .slhead .sl{grid-column:2/-1;font-size:9px} .slhead .lab2,.slhead .sp{display:none}')
    sub('<span class="pos">${esc(p.pos)}</span>${rail(p)}${deltaCell(p)}<span class="caret">›</span></button>',
        '<span class="pos">${esc(p.pos)}</span>${statCell(p)}${rail(p)}${deltaCell(p)}<span class="caret">›</span></button>')
    sub('<small>${esc(p.team)} · ${esc(p.cls)}${mvBadge(p)}</small>', '<small>${esc(p.team)} · ${esc(p.cls)}${p.ht?" · "+esc(p.ht):""}${mvBadge(p)}</small>')
    JS = open('/home/claude/work/statrow.js').read()
    sub('function renderBoard(){', JS + '\nfunction renderBoard(){')
    sub("""  $("#board").innerHTML = h || '<p class="note">No prospects match. Clear the search or turn a tier back on.</p>';""",
        """  $("#board").innerHTML = h ? SLHEAD + h + '<p class="slnote">Per-game stats: ESPN team stats through Nov 22 for college players. Pro players show their main league (hover a row for league and games). A dash means no 2026-27 number yet or no attempts.</p>' : '<p class="note">No prospects match. Clear the search or turn a tier back on.</p>';""")

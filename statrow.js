function statCell(p){
  const s=p.sl, f=v=> v==null ? '<i>-</i>' : (+v).toFixed(1);
  if(!s) return `<span class="sl" title="No 2026-27 stats yet">${'<span><i>-</i></span>'.repeat(8)}</span>`;
  return `<span class="sl" title="${esc(s.lg)} 2026-27, ${s.g} games">${[s.pts,s.reb,s.ast,s.blk,s.stl,s.fg,s.ft,s.tp].map(v=>`<span>${f(v)}</span>`).join("")}</span>`;
}
const SLHEAD = `<div class="slhead" aria-hidden="true"><span class="sp"></span><span class="sp"></span><span class="sp"></span><span class="sl"><span>PPG</span><span>RPG</span><span>APG</span><span>BPG</span><span>SPG</span><span>FG%</span><span>FT%</span><span>3P%</span></span><span class="lab2">vs outlets</span><span class="sp"></span></div>`;

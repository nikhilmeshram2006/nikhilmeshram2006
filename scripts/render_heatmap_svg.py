from pathlib import Path
from datetime import date, timedelta
import json, html
ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data/contributions.json", ROOT / "contrib-heatmap.svg"
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def main():
    if not DATA.exists():
        raise SystemExit("Missing data/contributions.json. Run fetch_contributions.py first.")
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    records = {r["date"]:r for r in payload.get("contributions", [])}
    today = date.today()
    start = today - timedelta(days=370)
    start -= timedelta(days=(start.weekday()+1)%7)
    days, cur = [], start
    while cur <= today:
        r = records.get(cur.isoformat(), {})
        days.append((cur, int(r.get("count",0)), max(0,min(4,int(r.get("level",0))))))
        cur += timedelta(days=1)
    cell,gap,left,top = 11,4,52,44
    weeks = (len(days)+6)//7
    width,height = left+weeks*(cell+gap)+12, top+7*(cell+gap)+40
    rects=[]
    for i,(day,count,level) in enumerate(days):
        x=left+(i//7)*(cell+gap); y=top+(((day.weekday()+1)%7)*(cell+gap))
        title=html.escape(f"{count} contributions on {day.isoformat()}")
        rects.append(f'<rect class="cell" style="--i:{i}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{COLORS[level]}"><title>{title}</title></rect>')
    total=int(payload.get("total",sum(x[1] for x in days)))
    legend=''.join(f'<rect x="{width-118+j*15}" y="{height-22}" width="11" height="11" rx="2" fill="{c}"/>' for j,c in enumerate(COLORS))
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>{html.escape(payload.get("username","GitHub"))} contribution calendar</title><rect width="100%" height="100%" rx="8" fill="#0d1117" stroke="#30363d"/>
<text x="18" y="24" font-family="monospace" font-size="13" fill="#e6edf3">{total:,} contributions · last year</text>
<g font-family="monospace" font-size="10" fill="#8b949e"><text x="{left}" y="38">Sun</text><text x="{left}" y="{top+2*(cell+gap)+1}">Tue</text><text x="{left}" y="{top+4*(cell+gap)+1}">Thu</text></g>
<style>.cell{{opacity:0;animation:appear .35s ease-out forwards;animation-delay:calc(var(--i)*2ms)}} @keyframes appear{{to{{opacity:1}}}} @media(prefers-reduced-motion:reduce){{.cell{{opacity:1;animation:none}}}}</style>
{''.join(rects)}
<g font-family="monospace" font-size="10" fill="#8b949e"><text x="{width-150}" y="{height-12}">Less</text>{legend}<text x="{width-35}" y="{height-12}">More</text></g></svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()

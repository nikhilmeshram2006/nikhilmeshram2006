from pathlib import Path
from PIL import Image
import html

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "source-prepped.png", ROOT / "avi-ascii.svg"
RAMP = "  .,:;irsXA253hMHGS#9B&@"

def main():
    if not SRC.exists():
        raise SystemExit("Run python scripts/prep_photo.py first.")
    im = Image.open(SRC).convert("L").resize((68,40))
    pixels = list(im.getdata())
    rows = []
    for y in range(40):
        line = "".join(RAMP[min(len(RAMP)-1, int((255-pixels[y*68+x])/256*len(RAMP)))] for x in range(68))
        rows.append(f'<text x="8" y="{16+y*10}" class="row" style="--i:{y}">{html.escape(line)}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="430" viewBox="0 0 700 430" role="img">
<title>Animated ASCII portrait</title><rect width="100%" height="100%" rx="8" fill="#0b0d10"/>
<style>.row {{font:10px monospace;fill:#d6d9dc;opacity:0;animation:reveal .22s steps(1,end) forwards;animation-delay:calc(var(--i)*55ms)}} @keyframes reveal {{to {{opacity:1}}}} @media(prefers-reduced-motion:reduce){{.row{{opacity:1;animation:none}}}}</style>
{''.join(rows)}</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()

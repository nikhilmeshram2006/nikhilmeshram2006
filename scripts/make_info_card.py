from pathlib import Path
import os, html
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "info-card.svg"

def main():
    user = html.escape(os.getenv("PROFILE_NAME", "nikhilmeshram2006"))
    entries = [("USER", user), ("ROLE", "CSE Student"), ("FOCUS", "Web Development"),
               ("STATUS", "Learning by building"), ("SKILLS", "Python · JavaScript"),
               ("STACK", "HTML · CSS · Git")]
    lines, y = [], 90
    for key, value in entries:
        lines.append(f'<text x="25" y="{y}" class="key">{key}</text><text x="145" y="{y}" class="val">{html.escape(value)}</text>')
        y += 34
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="470" height="310" viewBox="0 0 470 310" role="img">
<title>Developer information card</title><rect width="470" height="310" rx="10" fill="#0b0d10" stroke="#30363d"/>
<path d="M10 0H460a10 10 0 0 1 10 10V44H0V10A10 10 0 0 1 10 0Z" fill="#161b22"/>
<circle cx="20" cy="22" r="5" fill="#ff5f56"/><circle cx="38" cy="22" r="5" fill="#ffbd2e"/><circle cx="56" cy="22" r="5" fill="#27c93f"/>
<text x="78" y="27" fill="#c9d1d9" font-family="monospace" font-size="13">system-info — bash</text>
<style>.key{{font:bold 12px monospace;fill:#7ee787}} .val{{font:13px monospace;fill:#e6edf3}}</style>
<text x="25" y="65" fill="#7ee787" font-family="monospace" font-size="13">{user}@github ~ $ whoami</text>
{''.join(lines)}
<text x="25" y="292" fill="#8b949e" font-family="monospace" font-size="11">profile card • generated with Python</text></svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()

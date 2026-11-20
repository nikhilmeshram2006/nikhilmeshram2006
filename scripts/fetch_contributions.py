from pathlib import Path
from datetime import datetime, timezone
import json, os, re, urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = os.getenv("GITHUB_USERNAME", "nikhilmeshram2006")
URL = f"https://github.com/users/{USER}/contributions"
OUT = ROOT / "data" / "contributions.json"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "animated-profile-readme/1.1"})
    html_text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")

    tooltips = {}
    for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>', html_text, re.S):
        tooltips[m.group(1)] = re.sub(r"<[^>]+>", "", m.group(2)).strip()

    rows = []
    for m in re.finditer(r"<td\b([^>]*)>", html_text):
        attrs = m.group(1)
        dm = re.search(r'data-date="([^"]+)"', attrs)
        if not dm:
            continue
        day = dm.group(1)
        lm = re.search(r'data-level="(\d+)"', attrs)
        cm = re.search(r'data-count="(\d+)"', attrs)
        im = re.search(r'\bid="([^"]+)"', attrs)
        level = max(0, min(4, int(lm.group(1)))) if lm else 0
        count = int(cm.group(1)) if cm else 0
        if count == 0 and im:
            tip = tooltips.get(im.group(1), "")
            tm = re.match(r"^(\d+)\s+contribution", tip)
            if tm:
                count = int(tm.group(1))
        rows.append({"date": day, "count": count, "level": level})

    rows.sort(key=lambda r: r["date"])
    if not rows:
        raise SystemExit("Could not parse GitHub contribution cells.")

    OUT.parent.mkdir(exist_ok=True)
    payload = {
        "username": USER,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "contributions": rows,
        "total": sum(r["count"] for r in rows),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} days for {USER}; total={payload['total']}")


if __name__ == "__main__":
    main()

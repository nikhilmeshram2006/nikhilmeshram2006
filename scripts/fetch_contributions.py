from pathlib import Path
from datetime import datetime, date, timezone
import json, os, re, urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = os.getenv("GITHUB_USERNAME", "nikhilmeshram2006")
OUT = ROOT / "data" / "contributions.json"


def parse_contributions_html(html_text: str) -> dict[str, dict]:
    tooltips = {}
    for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>', html_text, re.S):
        tooltips[m.group(1)] = re.sub(r"<[^>]+>", "", m.group(2)).strip()

    days = {}
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
        days[day] = {"date": day, "count": count, "level": level}
    return days


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "animated-profile-readme/1.2"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")


def main():
    # Determine account start year so lifetime totals always start from account creation (Jan 9, 2026)
    start_year = 2026
    created_date = "2026-01-09"
    try:
        u_info = json.loads(fetch_url(f"https://api.github.com/users/{USER}"))
        if u_info.get("created_at"):
            created_date = u_info["created_at"][:10]
            start_year = int(created_date[:4])
    except Exception:
        pass

    cur_year = date.today().year
    all_days = {}

    # Fetch rolling default calendar first (ensures heatmap has latest 370 days)
    base_url = f"https://github.com/users/{USER}/contributions"
    all_days.update(parse_contributions_html(fetch_url(base_url)))

    # Fetch each calendar year since account creation so lifetime contributions never roll off
    for yr in range(start_year, cur_year + 1):
        yr_url = f"https://github.com/users/{USER}/contributions?from={yr}-01-01&to={yr}-12-31"
        try:
            all_days.update(parse_contributions_html(fetch_url(yr_url)))
        except Exception:
            pass

    today_iso = date.today().isoformat()
    rows = sorted((r for r in all_days.values() if r["date"] <= today_iso), key=lambda r: r["date"])
    if not rows:
        raise SystemExit("Could not parse GitHub contribution cells.")

    OUT.parent.mkdir(exist_ok=True)
    payload = {
        "username": USER,
        "created_date": created_date,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": base_url,
        "contributions": rows,
        "total": sum(r["count"] for r in rows),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} days for {USER} (since {created_date}); total={payload['total']}")


if __name__ == "__main__":
    main()

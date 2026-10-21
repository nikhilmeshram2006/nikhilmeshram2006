from pathlib import Path
from datetime import datetime, timezone
import json, os, requests
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
USER = os.getenv("GITHUB_USERNAME", "nikhilmeshram2006")
URL = f"https://github.com/users/{USER}/contributions"
OUT = ROOT / "data" / "contributions.json"

def main():
    response = requests.get(URL, headers={"User-Agent":"animated-profile-readme/1.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day, [data-date][data-level]")
    rows = []
    for cell in cells:
        day = cell.get("data-date")
        if not day:
            continue
        try:
            count = int(cell.get("data-count", "0"))
            level = max(0, min(4, int(cell.get("data-level", "0"))))
        except ValueError:
            count, level = 0, 0
        rows.append({"date":day, "count":count, "level":level})
    if not rows:
        raise SystemExit("Could not parse GitHub contribution cells. Public page markup may have changed; inspect the workflow log.")
    OUT.parent.mkdir(exist_ok=True)
    payload = {"username":USER, "fetched_at":datetime.now(timezone.utc).isoformat(),
               "source":URL, "contributions":rows, "total":sum(r["count"] for r in rows)}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} days for {USER}; total={payload['total']}")

if __name__ == "__main__":
    main()

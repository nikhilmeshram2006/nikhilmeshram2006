from pathlib import Path
from datetime import date, timedelta
import json, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "streak-card.svg"


def fmt_date(d: date) -> str:
    return d.strftime("%b %d").replace(" 0", " ")


def fmt_range(start: date | None, end: date | None) -> str:
    if not start or not end:
        return "No active streak"
    if start == end:
        return start.strftime("%b %d, %Y").replace(" 0", " ")
    if start.year == end.year:
        return f"{fmt_date(start)} - {fmt_date(end)}, {end.year}"
    return f"{fmt_date(start)}, {start.year} - {fmt_date(end)}, {end.year}"


def compute_streaks(records: dict[str, int]):
    if not records:
        return 0, None, None, 0, None, None, 0, None, None

    today = date.today()
    all_dates = sorted(d for d in (date.fromisoformat(k) for k in records.keys()) if d <= today)
    active_dates = [d for d in all_dates if records.get(d.isoformat(), 0) > 0]
    first_day = active_dates[0] if active_dates else all_dates[0]
    last_day = all_dates[-1]
    total = sum(records.get(d.isoformat(), 0) for d in all_dates)

    # Longest streak across the full period
    best_len, best_start, best_end = 0, None, None
    cur_len, cur_start = 0, None
    d = first_day
    while d <= last_day:
        if records.get(d.isoformat(), 0) > 0:
            if cur_len == 0:
                cur_start = d
            cur_len += 1
            if cur_len >= best_len:
                best_len, best_start, best_end = cur_len, cur_start, d
        else:
            cur_len = 0
            cur_start = None
        d += timedelta(days=1)

    # Current streak: anchor at the latest date with contributions if it is today or yesterday (last_day or last_day - 1)
    anchor = last_day
    if records.get(anchor.isoformat(), 0) == 0:
        prev = anchor - timedelta(days=1)
        if records.get(prev.isoformat(), 0) > 0:
            anchor = prev

    active_len, active_start, active_end = 0, None, None
    if records.get(anchor.isoformat(), 0) > 0:
        active_end = anchor
        d = anchor
        while d >= first_day and records.get(d.isoformat(), 0) > 0:
            active_len += 1
            active_start = d
            d -= timedelta(days=1)

    return total, first_day, last_day, active_len, active_start, active_end, best_len, best_start, best_end


def main():
    if not DATA.exists():
        raise SystemExit("Missing data/contributions.json. Run fetch_contributions.py first.")
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    user = html.escape(payload.get("username", "nikhilmeshram2006"))
    records = {r["date"]: int(r.get("count", 0)) for r in payload.get("contributions", [])}

    (
        total,
        first_day,
        last_day,
        cur_len,
        cur_start,
        cur_end,
        best_len,
        best_start,
        best_end,
    ) = compute_streaks(records)

    total_range = f"{first_day.strftime('%b %d, %Y').replace(' 0', ' ')} - Present" if first_day else "No contributions yet"
    cur_range = fmt_range(cur_start, cur_end)
    best_range = fmt_range(best_start, best_end)

    # Ring progress for Current Streak (circumference = 2 * pi * 36 ~= 226.2)
    ring_circ = 226.2
    ratio = min(1.0, cur_len / max(best_len, 1)) if cur_len > 0 else 0.0
    dash_offset = round(ring_circ * (1.0 - max(0.08, ratio)), 2) if cur_len > 0 else ring_circ

    cur_unit = "day" if cur_len == 1 else "days"
    best_unit = "day" if best_len == 1 else "days"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="224" viewBox="0 0 860 224" role="img">
  <title>{user} GitHub contribution streak</title>
  <defs>
    <linearGradient id="streakGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7ee787"/>
      <stop offset="100%" stop-color="#26a641"/>
    </linearGradient>
    <style>
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
      .fade {{ opacity: 0; animation: fadeIn 0.55s ease-out forwards; }}
      .d1 {{ animation-delay: 0.1s; }}
      .d2 {{ animation-delay: 0.25s; }}
      .d3 {{ animation-delay: 0.4s; }}
      .ring {{ stroke-dasharray: {ring_circ}; stroke-dashoffset: {ring_circ}; animation: drawRing 1.1s ease-out 0.2s forwards; }}
      .pulse {{ animation: pulseDot 2.2s ease-in-out infinite; transform-origin: 430px 92px; }}
      @keyframes fadeIn {{ to {{ opacity: 1; }} }}
      @keyframes drawRing {{ to {{ stroke-dashoffset: {dash_offset}; }} }}
      @keyframes pulseDot {{ 0%, 100% {{ opacity: 0.85; }} 50% {{ opacity: 1; }} }}
      @media (prefers-reduced-motion: reduce) {{
        .fade {{ opacity: 1; animation: none; }}
        .ring {{ stroke-dashoffset: {dash_offset}; animation: none; }}
        .pulse {{ animation: none; }}
      }}
    </style>
  </defs>

  <!-- Terminal Window Frame -->
  <rect x="0.5" y="0.5" width="859" height="223" rx="10" fill="#0b0d10" stroke="#30363d"/>
  <path d="M10 1H850a9 9 0 0 1 9 9V38H1V10A9 9 0 0 1 10 1Z" fill="#161b22"/>
  <line x1="1" y1="38" x2="859" y2="38" stroke="#30363d" stroke-width="1"/>
  <circle cx="20" cy="19.5" r="5" fill="#ff5f56"/>
  <circle cx="38" cy="19.5" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="19.5" r="5" fill="#27c93f"/>
  <text x="78" y="24" fill="#c9d1d9" class="mono" font-size="12.5">git-streak &#8212; bash</text>
  <text x="840" y="24" text-anchor="end" fill="#8b949e" class="mono" font-size="11">{user}@github</text>

  <!-- Command Prompt -->
  <text x="22" y="61" fill="#7ee787" class="mono" font-size="12.5">{user}@github ~ $ git streak --stats</text>

  <!-- Column Dividers -->
  <line x1="286" y1="78" x2="286" y2="194" stroke="#21262d" stroke-width="1"/>
  <line x1="574" y1="78" x2="574" y2="194" stroke="#21262d" stroke-width="1"/>

  <!-- Left Column: Total Contributions -->
  <g class="fade d1" text-anchor="middle">
    <text x="143" y="128" fill="#e6edf3" class="mono" font-size="34" font-weight="700">{total}</text>
    <text x="143" y="154" fill="#7ee787" class="mono" font-size="12" font-weight="700" letter-spacing="0.8">TOTAL CONTRIBUTIONS</text>
    <text x="143" y="176" fill="#8b949e" class="mono" font-size="11">{html.escape(total_range)}</text>
  </g>

  <!-- Center Column: Current Streak -->
  <g class="fade d2" text-anchor="middle">
    <circle cx="430" cy="118" r="36" fill="none" stroke="#161b22" stroke-width="5"/>
    <circle cx="430" cy="118" r="36" fill="none" stroke="url(#streakGlow)" stroke-width="5" stroke-linecap="round" transform="rotate(-90 430 118)" class="ring"/>
    <!-- Subtle flame icon at top of ring -->
    <circle cx="430" cy="82" r="9" fill="#0b0d10"/>
    <path class="pulse" d="M430 75.5c1.8 2.4 3.5 4.2 3.5 6.4a3.5 3.5 0 1 1-7 0c0-1.4.7-2.8 1.6-3.9.2 1.1.9 1.6 1.4 1.6.1-1.4-.1-2.8.5-4.1Z" fill="#7ee787"/>
    <text x="430" y="127" fill="#e6edf3" class="mono" font-size="28" font-weight="700">{cur_len}</text>
    <text x="430" y="172" fill="#7ee787" class="mono" font-size="12" font-weight="700" letter-spacing="0.8">CURRENT STREAK ({cur_unit.upper()})</text>
    <text x="430" y="191" fill="#8b949e" class="mono" font-size="11">{html.escape(cur_range)}</text>
  </g>

  <!-- Right Column: Longest Streak -->
  <g class="fade d3" text-anchor="middle">
    <text x="717" y="128" fill="#e6edf3" class="mono" font-size="34" font-weight="700">{best_len}</text>
    <text x="717" y="154" fill="#7ee787" class="mono" font-size="12" font-weight="700" letter-spacing="0.8">LONGEST STREAK ({best_unit.upper()})</text>
    <text x="717" y="176" fill="#8b949e" class="mono" font-size="11">{html.escape(best_range)}</text>
  </g>

  <!-- Footer -->
  <text x="22" y="211" fill="#6e7681" class="mono" font-size="10.5">streak tracker &#8226; synced daily from github contributions</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT} (total={total}, current={cur_len}, longest={best_len})")


if __name__ == "__main__":
    main()

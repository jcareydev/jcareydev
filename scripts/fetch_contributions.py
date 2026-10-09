"""
Scrape the public contribution calendar (no API token needed) and write
data/contributions.json with every day plus streak and total stats.

    python scripts/fetch_contributions.py [username]

Standard library only, so the daily GitHub Action needs no installs.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "jcareydev")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "data", "contributions.json")


class Calendar(HTMLParser):
    """Collect day cells (<td data-date data-level>) and their tooltips."""

    def __init__(self):
        super().__init__()
        self.days = {}        # cell id -> {"date", "level"}
        self.tips = {}        # cell id -> tooltip text
        self._tip_for = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and "data-date" in a and "data-level" in a:
            self.days[a.get("id")] = {"date": a["data-date"], "level": int(a["data-level"])}
        elif tag == "tool-tip" and a.get("for"):
            self._tip_for = a["for"]

    def handle_data(self, data):
        if self._tip_for:
            self.tips[self._tip_for] = self.tips.get(self._tip_for, "") + data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self._tip_for = None


def count_from(tip):
    m = re.match(r"\s*(\d[\d,]*) contribution", tip or "")
    return int(m.group(1).replace(",", "")) if m else 0


req = urllib.request.Request(
    f"https://github.com/users/{USER}/contributions",
    headers={"User-Agent": "profile-readme-heatmap"},
)
with urllib.request.urlopen(req, timeout=30) as r:
    page = r.read().decode("utf-8")

cal = Calendar()
cal.feed(page)
if not cal.days:
    sys.exit("no calendar cells found; has GitHub changed the page?")

days = sorted(
    ({"date": d["date"], "level": d["level"], "count": count_from(cal.tips.get(cid))}
     for cid, d in cal.days.items()),
    key=lambda d: d["date"],
)

# streaks: today with no activity yet doesn't break the current streak
active = {d["date"] for d in days if d["count"] > 0}
longest = run = 0
for d in days:
    run = run + 1 if d["date"] in active else 0
    longest = max(longest, run)
day = date.fromisoformat(days[-1]["date"])
if day.isoformat() not in active:
    day -= timedelta(days=1)
current = 0
while day.isoformat() in active:
    current += 1
    day -= timedelta(days=1)

best = max(days, key=lambda d: d["count"])
stats = {
    "user": USER,
    "total": sum(d["count"] for d in days),
    "active_days": len(active),
    "current_streak": current,
    "longest_streak": longest,
    "best_day": {"date": best["date"], "count": best["count"]} if best["count"] else None,
    "from": days[0]["date"],
    "to": days[-1]["date"],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump({"stats": stats, "days": days}, f, indent=1)
print("wrote", OUT, json.dumps(stats))

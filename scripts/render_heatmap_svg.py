"""
Draw data/contributions.json as a terminal-window contribution heatmap SVG:
53 weeks x 7 days of rounded cells, a key, and a stats footer. Days since
joining GitHub show the real activity in GitHub's greens and reveal once
along a diagonal; days before joining are gold with a shimmer, and the key
says so, so the gold is never mistaken for activity.

    python scripts/render_heatmap_svg.py [output.svg]

Standard library only. STATIC=1 skips the animation.
"""
import json
import os
import random
import sys
from datetime import date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "contrib-heatmap.svg")
STATIC = bool(os.environ.get("STATIC"))

USER = "joe"
W = 860
PAD = 20
TITLEBAR_H = 30
LABEL_W = 30          # weekday labels
MONTH_H = 18
GAP = 3
FOOTER_H = 44

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#f0883e"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
GOLDS = ["#3b2c0b", "#5c4512", "#8a6a1c", "#c9a227", "#f2d270"]
GOLD_TEXT = "#d4a72c"

JOINED = date.fromisoformat(os.environ.get("JOINED", "2026-09-27"))  # GitHub account created
SHIMMER = 3.6        # seconds for the gold shimmer to pass a cell

data = json.load(open(DATA))
days, stats = data["days"], data["stats"]

# lay days out in week columns starting on Sunday, like GitHub
first = date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7          # Sunday = 0
weeks = (offset + len(days) + 6) // 7
CELL = (W - PAD * 2 - LABEL_W - GAP * (weeks - 1)) / weeks
STEP = CELL + GAP

grid_top = TITLEBAR_H + PAD + MONTH_H
grid_left = PAD + LABEL_W
grid_h = 7 * STEP - GAP
H = grid_top + grid_h + 26 + FOOTER_H

p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.1f}" '
         f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
p.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>')
p.append(f'<rect width="100%" height="100%" rx="12" fill="url(#bg)"/>')
p.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1:.1f}" rx="12" fill="none" stroke="{FRAME}"/>')
p.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    p.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
p.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">'
         f'{USER}@github: ~/contributions --last-year</text>')

# weekday labels
for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    p.append(f'<text x="{PAD}" y="{grid_top + row * STEP + CELL * 0.8:.1f}" fill="{MUTED}" font-size="10">{name}</text>')

# month labels at the first week that starts in a new month
last_month = None
for i, d in enumerate(days):
    col, row = divmod(i + offset, 7)
    dt = date.fromisoformat(d["date"])
    if row == 0 and dt.month != last_month and col < weeks - 2:
        p.append(f'<text x="{grid_left + col * STEP:.1f}" y="{grid_top - 6}" fill="{MUTED}" font-size="10">'
                 f'{dt.strftime("%b")}</text>')
        last_month = dt.month

# cells
rng = random.Random(27)          # fixed seed: the gold pattern doesn't jump each day
for i, d in enumerate(days):
    col, row = divmod(i + offset, 7)
    x, y = grid_left + col * STEP, grid_top + row * STEP
    if date.fromisoformat(d["date"]) < JOINED:
        base = rng.randint(0, 2)
        rect = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2" '
                f'fill="{GOLDS[base]}"><title>{d["date"]}, before joining GitHub</title>')
        if STATIC:
            p.append(rect + "</rect>")
            continue
        # brighten to the top gold and settle back; negative begin = lit from the first frame
        seq = [GOLDS[base]] + GOLDS[base + 1:] + GOLDS[base + 1:-1][::-1] + [GOLDS[base]]
        delay = col * 0.07 + row * 0.035 + rng.uniform(0, 0.3)
        p.append(f'{rect}<animate attributeName="fill" values="{";".join(seq)}" dur="{SHIMMER}s" '
                 f'begin="-{delay:.2f}s" repeatCount="indefinite"/></rect>')
        continue
    title = f'<title>{d["count"]} on {d["date"]}</title>'
    if STATIC:
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2" '
                 f'fill="{LEVELS[d["level"]]}">{title}</rect>')
        continue
    begin = (col + row) * 0.03
    p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2" '
             f'fill="{LEVELS[d["level"]]}" opacity="0">{title}'
             f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.4s" fill="freeze"/></rect>')

# legend: gold key bottom left, green scale bottom right
ly = grid_top + grid_h + 14
p.append(f'<rect x="{grid_left:.1f}" y="{ly - CELL + 2:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2" fill="{GOLDS[3]}"/>')
p.append(f'<text x="{grid_left + CELL + 6:.1f}" y="{ly:.1f}" fill="{MUTED}" font-size="10">before I joined GitHub '
         f'<tspan fill="{GOLD_TEXT}">· joined {JOINED.strftime("%-d %b %Y")}</tspan></text>')
lx = W - PAD - 5 * (CELL + GAP) - 34
p.append(f'<text x="{lx - 34:.1f}" y="{ly:.1f}" fill="{MUTED}" font-size="10">Less</text>')
for i, c in enumerate(LEVELS):
    p.append(f'<rect x="{lx + i * (CELL + GAP):.1f}" y="{ly - CELL + 2:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2" fill="{c}"/>')
p.append(f'<text x="{lx + 5 * (CELL + GAP) + 4:.1f}" y="{ly:.1f}" fill="{MUTED}" font-size="10">More</text>')

# stats footer
fy = H - FOOTER_H
p.append(f'<line x1="0" y1="{fy:.1f}" x2="{W}" y2="{fy:.1f}" stroke="{FRAME}"/>')
best = stats["best_day"]
best_txt = f'{best["count"]} on {date.fromisoformat(best["date"]).strftime("%-d %b")}' if best else "-"
items = [
    ("contributions", f'{stats["total"]:,} since joining'),
    ("current streak", f'{stats["current_streak"]}d'),
    ("longest streak", f'{stats["longest_streak"]}d'),
    ("best day", best_txt),
]
# space items by their text length (13px monospace is ~7.8px a character)
char_w = 13 * 0.6
gap = (W - PAD * 2 - sum(len(f"{k} {v}") * char_w for k, v in items)) / (len(items) - 1)
x = PAD
for k, v in items:
    p.append(f'<text x="{x:.1f}" y="{fy + 27:.1f}" font-size="13" fill="{MUTED}">{k} '
             f'<tspan fill="{ACCENT}">{v}</tspan></text>')
    x += len(f"{k} {v}") * char_w + gap

p.append("</svg>")
with open(OUT, "w") as f:
    f.write("".join(p))
print(f"wrote {OUT}: {W}x{H:.0f}, {weeks} weeks")

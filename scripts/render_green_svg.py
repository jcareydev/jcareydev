"""
Decorative all-green grid: the same 53 x 7 layout as a contribution graph,
every cell green, with a shimmer rippling across it forever. It is framed as
a visual (make-it-green.sh), not as activity; the footer carries the real
numbers from data/contributions.json, and GitHub's own contribution graph
sits further down the profile.

    python scripts/render_green_svg.py [output.svg]

Standard library only. STATIC=1 draws one still frame.
"""
import json
import os
import random
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "green.svg")
STATIC = bool(os.environ.get("STATIC"))

USER = "joe"
W = 860
PAD = 20
TITLEBAR_H = 30
WEEKS, DAYS = 53, 7
GAP = 3
FOOTER_H = 44

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
ACCENT = "#f0883e"
GREENS = ["#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CYCLE = 3.2          # seconds for one shimmer to pass a cell
SPREAD = 0.06        # delay per column, so the ripple travels left to right

stats = json.load(open(DATA))["stats"]
rng = random.Random(27)          # fixed seed: the pattern doesn't jump each day

CELL = (W - PAD * 2 - GAP * (WEEKS - 1)) / WEEKS
STEP = CELL + GAP
grid_top = TITLEBAR_H + PAD
H = grid_top + DAYS * STEP - GAP + PAD + FOOTER_H

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
         f'{USER}@github: ~/make-it-green.sh</text>')

for col in range(WEEKS):
    for row in range(DAYS):
        x, y = PAD + col * STEP, grid_top + row * STEP
        base = rng.randint(0, 3)
        # each cell brightens to the top green and settles back to its own shade
        seq = [GREENS[base]] + GREENS[base + 1:] + GREENS[base + 1:-1][::-1] + [GREENS[base]]
        rect = f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2" fill="{GREENS[base]}"'
        if STATIC:
            p.append(rect + "/>")
            continue
        # negative begin starts every cell mid-cycle, so the grid is lit from the first frame
        offset = col * SPREAD + row * SPREAD * 0.5 + rng.uniform(0, 0.25)
        p.append(f'{rect}><animate attributeName="fill" values="{";".join(seq)}" dur="{CYCLE}s" '
                 f'begin="-{offset:.2f}s" repeatCount="indefinite"/></rect>')

# footer: real numbers, labelled as such
fy = H - FOOTER_H
p.append(f'<line x1="0" y1="{fy:.1f}" x2="{W}" y2="{fy:.1f}" stroke="{FRAME}"/>')
items = [
    ("status", "all green"),
    ("contributions", f'{stats["total"]:,} since joining'),
    ("streak", f'{stats["current_streak"]}d'),
    ("best day", f'{stats["best_day"]["count"]}' if stats["best_day"] else "-"),
]
# space items by their text length (13px monospace is ~7.8px a character)
char_w = 13 * 0.6
text_w = sum(len(f"{k} {v}") * char_w for k, v in items)
gap = (W - PAD * 2 - text_w) / (len(items) - 1)
x = PAD
for k, v in items:
    p.append(f'<text x="{x:.1f}" y="{fy + 27:.1f}" font-size="13" fill="{MUTED}">{k} '
             f'<tspan fill="{ACCENT}">{v}</tspan></text>')
    x += len(f"{k} {v}") * char_w + gap

p.append("</svg>")
with open(OUT, "w") as f:
    f.write("".join(p))
print(f"wrote {OUT}: {W}x{H:.0f}")

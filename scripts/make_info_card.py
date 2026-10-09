"""
Hand-authored neofetch-style info card. Edit CARD below, then:

    python scripts/make_info_card.py [output.svg]

Lines fade and slide in one after another. STATIC=1 skips the animation.
Sized to sit beside portrait.svg (same height) in the README table.
"""
import html
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

USER, HOST = "joe", "github"
NAME = "Joe Carey"

# (label, value); a blank label continues the line above
# Public-safe only: no client names, private projects, email or phone.
CARD = [
    ("Role", "Marketing, photography & video"),
    ("Now", "josephcarey.com · personal site"),
    ("Built", "Gren · writing app (gren.app)"),
    ("Stack", "HTML · CSS · JavaScript · Python"),
    ("", "Node.js · Git · Cloudflare"),
    ("Creative", "Final Cut Pro · Lightroom · Photoshop"),
    ("Ships on", "Cloudflare Workers & Pages"),
    ("Web", "josephcarey.com"),
    ("LinkedIn", "linkedin.com/in/joecareyuk"),
    ("Insta", "instagram.com/ajoe"),
]

W, H = 490, 413            # H matches portrait.svg
PAD = 20
TITLEBAR_H = 30
LINE_H = 21
KEY_W = 92

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#f0883e"
BLOCKS = ["#30363d", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]

START = 0.4                # seconds before the first line
STAGGER = 0.35


def appear(i):
    """Fade + slide in for the i-th line (nothing when STATIC)."""
    if STATIC:
        return "", ""
    t = START + i * STAGGER
    return (' opacity="0" transform="translate(-8 0)"',
            f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-8 0" to="0 0" '
            f'begin="{t:.2f}s" dur="0.4s" fill="freeze"/>')


p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="14">')
p.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>')
p.append(f'<rect width="100%" height="100%" rx="12" fill="url(#bg)"/>')
p.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}"/>')
p.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    p.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
p.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">'
         f'{USER}@{HOST}: ~/neofetch</text>')

y = TITLEBAR_H + PAD + 18
n = 0

# header: user@host, then an underline the same length
attrs, anim = appear(n); n += 1
p.append(f'<g{attrs}><text x="{PAD}" y="{y}" font-weight="bold">'
         f'<tspan fill="{ACCENT}">{USER}</tspan><tspan fill="{INK}">@</tspan>'
         f'<tspan fill="{ACCENT}">{HOST}</tspan></text>{anim}</g>')
y += LINE_H
attrs, anim = appear(n); n += 1
p.append(f'<g{attrs}><text x="{PAD}" y="{y}" fill="{MUTED}">{"-" * len(USER + "@" + HOST)}</text>{anim}</g>')
y += LINE_H

for label, value in [("Name", NAME)] + CARD:
    attrs, anim = appear(n); n += 1
    key = f'<tspan fill="{ACCENT}" font-weight="bold">{html.escape(label)}</tspan>' if label else ""
    p.append(f'<g{attrs}><text x="{PAD}" y="{y}">{key}</text>'
             f'<text x="{PAD + KEY_W}" y="{y}" fill="{INK}">{html.escape(value)}</text>{anim}</g>')
    y += LINE_H

# neofetch colour blocks
y += 8
attrs, anim = appear(n); n += 1
blocks = "".join(f'<rect x="{PAD + i * 26}" y="{y}" width="24" height="14" rx="2" fill="{c}"/>'
                 for i, c in enumerate(BLOCKS))
p.append(f'<g{attrs}>{blocks}{anim}</g>')

# prompt with blinking cursor at the bottom
py = H - PAD
prompt = f"{USER}@{HOST}:~$"
p.append(f'<text x="{PAD}" y="{py}" fill="{MUTED}" font-size="13">{prompt}</text>')
p.append(f'<rect x="{PAD + (len(prompt) + 1) * 13 * 0.6:.1f}" y="{py - 11}" width="8" height="14" fill="{ACCENT}">'
         f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')

if y + 14 > py - 20:
    sys.exit(f"card content too tall: {y + 14:.0f} > {py - 20}")

p.append("</svg>")
with open(OUT, "w") as f:
    f.write("".join(p))
print(f"wrote {OUT}: {W}x{H}, {n} animated lines")

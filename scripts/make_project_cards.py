"""
Featured project cards in the same terminal style as the rest of the README,
two to a row (416px each, so both fit GitHub's 846px column). Each is wrapped in a link in
README.md, so edit PROJECTS here and the links there together.

    python scripts/make_project_cards.py

Writes card-<slug>.svg for each project. STATIC=1 skips the fade-in.
"""
import html
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STATIC = bool(os.environ.get("STATIC"))

USER = "joe"

# Public-safe only: no client names or private projects (see the README).
PROJECTS = [
    {
        "slug": "josephcarey",
        "title": "josephcarey.com",
        "lines": ["My portfolio: marketing, photography,",
                  "video and web. Case studies, a journal",
                  "and the story so far."],
        "tags": ["HTML", "CSS", "JavaScript", "Workers"],
        "url": "josephcarey.com",
    },
    {
        "slug": "gren",
        "title": "Gren",
        "lines": ["Calm, plain-text notes in the browser.",
                  "Works offline, reads aloud, checks UK",
                  "spelling and cleans up AI-written text."],
        "tags": ["JavaScript", "PWA", "IndexedDB", "Pages"],
        "url": "gren.app",
    },
]

W, H = 416, 196
PAD = 20
TITLEBAR_H = 30

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#f0883e"
TAG_BG = "#1f2630"


def card(p, delay):
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
    o.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>')
    o.append(f'<rect width="100%" height="100%" rx="12" fill="url(#bg)"/>')
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}"/>')
    o.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
    o.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">'
             f'{USER}@github: ~/projects/{html.escape(p["slug"])}</text>')

    body = []
    y = TITLEBAR_H + 32
    body.append(f'<text x="{PAD}" y="{y}" font-size="17" font-weight="bold" fill="{ACCENT}">'
                f'{html.escape(p["title"])}</text>')
    body.append(f'<text x="{W - PAD}" y="{y}" font-size="12" fill="{MUTED}" text-anchor="end">'
                f'{html.escape(p["url"])} ↗</text>')
    y += 26
    for line in p["lines"]:
        body.append(f'<text x="{PAD}" y="{y}" font-size="13" fill="{INK}">{html.escape(line)}</text>')
        y += 19

    # tag pills
    x, ty = PAD, H - 28
    for t in p["tags"]:
        w = len(t) * 7.2 + 16
        body.append(f'<rect x="{x:.1f}" y="{ty - 14}" width="{w:.1f}" height="20" rx="10" fill="{TAG_BG}" stroke="{FRAME}"/>'
                    f'<text x="{x + w / 2:.1f}" y="{ty}" font-size="12" fill="{MUTED}" text-anchor="middle">{html.escape(t)}</text>')
        x += w + 6

    if STATIC:
        o.extend(body)
    else:
        o.append(f'<g opacity="0">{"".join(body)}'
                 f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.6s" fill="freeze"/></g>')
    o.append("</svg>")
    return "".join(o)


for i, p in enumerate(PROJECTS):
    out = os.path.join(ROOT, f'card-{p["slug"]}.svg')
    with open(out, "w") as f:
        f.write(card(p, 0.3 + i * 0.3))
    print("wrote", out)

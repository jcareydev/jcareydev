"""
Turn the prepped portrait into a monochrome ASCII-art SVG that types itself
in like a terminal, then holds.

GitHub shows SVGs embedded with <img> and runs their SMIL animations (no JS),
so each row is revealed by a left-to-right clip wipe with a block cursor
riding the edge, staggered top to bottom.

    python scripts/make_ascii_svg.py [prepped.png] [output.svg]

Env:
    COLS=160        characters across (more = more detail)
    MODE=positive   bright skin -> dense characters (reads like a photo on
                    the dark card); MODE=negative does the opposite
    ART_W=330       width of the art in px (wider for combined portraits)
    STATIC=1        no animation, for previews
    NAME="..."      name shown after whoami (default Joe Carey)
    PREVIEW=x.png   also draw a still PNG of the result
"""
import html
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "portrait.svg")

COLS = int(os.environ.get("COLS", 160))
MODE = os.environ.get("MODE", "positive")
STATIC = bool(os.environ.get("STATIC"))
PREVIEW = os.environ.get("PREVIEW")

NAME = os.environ.get("NAME", "Joe Carey")
USER = "joe"

RAMP = " .`:-=+*cs#%@"   # sparse -> dense
GAMMA = float(os.environ.get("GAMMA", 1.5))
CONTRAST = float(os.environ.get("CONTRAST", 1.1))

ART_W = float(os.environ.get("ART_W", 330))  # 330 fits the README table column
CELL_W = ART_W / COLS
CELL_H = CELL_W * 15 / 8       # monospace glyphs are ~1:1.875
src = Image.open(SRC).convert("LA")
ROWS = round(COLS * src.height / src.width * 8 / 15)  # keep the photo's shape
ART_H = ROWS * CELL_H

PAD = 20
TITLEBAR_H = 30
STATUS_H = 34
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + PAD * 0.5 + ART_H + PAD * 0.5 + STATUS_H

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#f0883e"             # ginger, naturally

TOTAL_REVEAL = 5.5             # seconds for the whole portrait to print
ROW_DUR = TOTAL_REVEAL / ROWS

# ---- sample the image into a COLS x ROWS grid ------------------------------
lum_img = ImageEnhance.Contrast(src.getchannel("L")).enhance(CONTRAST)
lum_img = lum_img.resize((COLS, ROWS), Image.LANCZOS).load()
mask = src.getchannel("A").resize((COLS, ROWS), Image.LANCZOS).load()

rows = []
for y in range(ROWS):
    line = []
    for x in range(COLS):
        if mask[x, y] < 100:
            line.append(" ")
            continue
        lum = (lum_img[x, y] / 255.0) ** GAMMA
        density = lum if MODE == "positive" else 1.0 - lum
        idx = round(density * (len(RAMP) - 1))
        # keep the silhouette: never fully blank inside the person
        line.append(RAMP[max(1, min(len(RAMP) - 1, idx))])
    rows.append("".join(line).rstrip())

# ---- SVG -------------------------------------------------------------------
art_top = TITLEBAR_H + PAD * 0.5
font_size = CELL_H * 0.9

p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W:.0f}" height="{CANVAS_H:.0f}" '
         f'viewBox="0 0 {CANVAS_W:.1f} {CANVAS_H:.1f}" '
         f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
p.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
         f'</linearGradient></defs>')
p.append(f'<rect width="100%" height="100%" rx="12" fill="url(#bg)"/>')
p.append(f'<rect x=".5" y=".5" width="{CANVAS_W - 1:.1f}" height="{CANVAS_H - 1:.1f}" rx="12" '
         f'fill="none" stroke="{FRAME}"/>')

# title bar
p.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W:.1f}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    p.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
p.append(f'<text x="{CANVAS_W / 2:.1f}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" '
         f'text-anchor="middle">{USER}@github: ~/portrait.sh</text>')

# art, one <text> per row
for ry, line in enumerate(rows):
    if not line:
        continue
    row_y = art_top + ry * CELL_H
    w = len(line) * CELL_W
    text = (f'<text xml:space="preserve" x="{PAD}" y="{row_y + CELL_H * 0.78:.2f}" fill="{INK}" '
            f'font-size="{font_size:.2f}" textLength="{w:.2f}" lengthAdjust="spacingAndGlyphs">'
            f'{html.escape(line)}</text>')
    if STATIC:
        p.append(text)
        continue
    begin = ry * ROW_DUR
    p.append(f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.2f}" height="{CELL_H:.2f}" width="0">'
             f'<animate attributeName="width" from="0" to="{ART_W}" begin="{begin:.3f}s" '
             f'dur="{ROW_DUR:.3f}s" fill="freeze"/></rect></clipPath>')
    p.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    p.append(f'<rect y="{row_y:.2f}" width="{CELL_W:.2f}" height="{CELL_H:.2f}" fill="{ACCENT}" opacity="0">'
             f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{begin:.3f}s" '
             f'dur="{ROW_DUR:.3f}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>'
             f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.3f}s"/></rect>')

# status bar with a blinking cursor; the name appears once the art is done
line_y = art_top + ART_H + PAD * 0.5
status_y = line_y + STATUS_H / 2 + 5
prompt = f"{USER}@github:~$ whoami "
p.append(f'<line x1="0" y1="{line_y:.1f}" x2="{CANVAS_W:.1f}" y2="{line_y:.1f}" stroke="{FRAME}"/>')
name_attr = "" if STATIC else ' opacity="0"'
name_anim = "" if STATIC else f'<set attributeName="opacity" to="1" begin="{TOTAL_REVEAL:.2f}s"/>'
p.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">{html.escape(prompt)}'
         f'<tspan fill="{INK}"{name_attr}>{html.escape(NAME)}{name_anim}</tspan></text>')
cursor_x = PAD + len(prompt + NAME + " ") * 13 * 0.6
p.append(f'<rect x="{cursor_x:.1f}" y="{status_y - 11:.1f}" width="8" height="14" fill="{ACCENT}">'
         f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
         f'dur="1s" repeatCount="indefinite"/></rect>')
p.append("</svg>")

svg = "".join(p)
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}: {len(svg) // 1024} KB, {CANVAS_W:.0f}x{CANVAS_H:.0f}, {COLS}x{ROWS} chars")

# ---- optional still preview -----------------------------------------------
if PREVIEW:
    scale = 3
    img = Image.new("RGB", (int(CANVAS_W * scale), int(CANVAS_H * scale)), BG)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", int(font_size * scale))
    for ry, line in enumerate(rows):
        for cx, ch in enumerate(line):
            if ch != " ":
                d.text(((PAD + cx * CELL_W) * scale, (art_top + ry * CELL_H) * scale), ch, fill=INK, font=font)
    img.save(PREVIEW)
    print("wrote", PREVIEW)

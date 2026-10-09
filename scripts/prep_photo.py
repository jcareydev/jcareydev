"""
Prepare the portrait photo for ASCII conversion.

  1. cut the person out using the mask from person_mask.swift
  2. crop square to head and shoulders
  3. boost local contrast (CLAHE) and darken thin dark features (eyes,
     brows, smile) so they survive being shrunk to ~100 characters across
  4. composite onto white and keep the mask as the alpha channel, so the
     ASCII step knows exactly which cells are background

    swift scripts/person_mask.swift source-photo.webp person-mask.png
    python scripts/prep_photo.py [photo] [mask] [output]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PHOTO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-photo.webp")
MASK = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "person-mask.png")
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "source-prepped.png")

# Crop box as fractions of the person's bounding box: from just above the
# head down to mid-chest, so the face gets most of the characters.
TOP_PAD = 0.04       # space above the head, as a fraction of crop size
CROP_SCALE = float(os.environ.get("CROP_SCALE", 0.62))  # crop size / person width
LINE_WEIGHT = float(os.environ.get("LINE_WEIGHT", 1.4))  # push eyes, brows, smile darker

gray = np.array(Image.open(PHOTO).convert("L"))
alpha = np.array(Image.open(MASK).convert("L").resize(gray.shape[::-1]))

# local contrast, then a gentle smooth so skin doesn't turn into noise
clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
tone = clahe.apply(gray)
tone = cv2.bilateralFilter(tone, 7, 30, 7)

# stretch tones over the person only
lo, hi = np.percentile(tone[alpha > 128], [2, 97])
tone = np.clip((tone.astype(np.float32) - lo) / (hi - lo), 0, 1)

# darken dark-on-light ridges (difference of gaussians), which plain
# averaging washes out at ascii resolution
fine = cv2.GaussianBlur(gray, (0, 0), 2.0).astype(np.float32)
coarse = cv2.GaussianBlur(gray, (0, 0), 8.0).astype(np.float32)
lines = np.clip((coarse - fine) / 30.0, 0, 1)
tone = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255

# paste onto white with a slightly feathered edge
m = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.2)
out = tone * m + 255.0 * (1.0 - m)

ys, xs = np.where(alpha > 128)
side = int((xs.max() - xs.min()) * CROP_SCALE)
cx = int(np.median(xs[ys < ys.min() + side * 0.35]))  # centre on the head
y0 = int(ys.min() - side * TOP_PAD)
x0 = cx - side // 2

canvas = np.full((side, side, 2), (255, 0), np.uint8)
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0, 0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0, 1] = alpha[sy0:sy1, sx0:sx1]

Image.fromarray(canvas, mode="LA").save(OUT)
print("wrote", OUT, canvas.shape)

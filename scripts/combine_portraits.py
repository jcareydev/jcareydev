"""
Merge two prepped portraits (grayscale + cut-out alpha) into one wide image,
left and right, with the shoulders overlapping, for a single ASCII block.

    python scripts/combine_portraits.py <left.png> <right.png> <output.png>

Env: SIZE=700 (each portrait's height), OVERLAP=120 (px the two share)
"""
import os
import sys

import numpy as np
from PIL import Image

left_path, right_path, out_path = sys.argv[1:4]
SIZE = int(os.environ.get("SIZE", 700))
OVERLAP = int(os.environ.get("OVERLAP", 120))


def load(path):
    im = Image.open(path).convert("LA").resize((SIZE, SIZE), Image.LANCZOS)
    a = np.array(im)
    return a[..., 0].astype(np.float32), a[..., 1].astype(np.float32) / 255.0


W = SIZE * 2 - OVERLAP
lum = np.full((SIZE, W), 255.0, np.float32)
alpha = np.zeros((SIZE, W), np.float32)

# left first, then right on top, each blended by its own cut-out mask
for (l, a), x0 in ((load(left_path), 0), (load(right_path), SIZE - OVERLAP)):
    region = slice(x0, x0 + SIZE)
    lum[:, region] = l * a + lum[:, region] * (1 - a)
    alpha[:, region] = np.maximum(alpha[:, region], a)

out = np.dstack([lum, alpha * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(out, mode="LA").save(out_path)
print("wrote", out_path, out.shape[1], "x", out.shape[0])

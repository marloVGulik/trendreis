#!/usr/bin/env python3
"""Crop a page-spread photo into readable tiles with lighting normalization.

Usage: python3 crop.py <image.jpg> <out_dir> [rows] [contrast]
Each spread is assumed to be two pages side by side.
Tiles are saved as <basename>_p<page>_r<row>.png  (page 0=left, 1=right)
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

def main():
    src = sys.argv[1]
    out = sys.argv[2]
    rows = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    contrast = float(sys.argv[4]) if len(sys.argv) > 4 else 1.6
    os.makedirs(out, exist_ok=True)
    im = Image.open(src).convert("L")
    w, h = im.size
    base = os.path.splitext(os.path.basename(src))[0]
    pw = w // 2
    ph = h // rows
    for page in range(2):
        for r in range(rows):
            box = (page * pw, r * ph, (page + 1) * pw, min(h, (r + 1) * ph))
            tile = im.crop(box)
            # flatten lighting: divide by a heavily blurred copy of itself
            arr = np.asarray(tile, dtype=np.float32) + 1e-6
            bg = np.asarray(tile.resize((arr.shape[1] // 4, arr.shape[0] // 4)).filter(ImageFilter.GaussianBlur(30)), dtype=np.float32)
            bg = np.asarray(Image.fromarray(bg.astype(np.uint8)).resize(tile.size, Image.BICUBIC), dtype=np.float32) + 1e-6
            norm = np.clip(arr * (bg.max() * 0.98) / bg, 0, 255)
            tile = Image.fromarray(norm.astype(np.uint8))
            tile = ImageOps.autocontrast(tile, cutoff=0.5)
            if contrast != 1.0:
                tile = ImageEnhance.Contrast(tile).enhance(contrast)
            path = os.path.join(out, f"{base}_p{page}_r{r}.png")
            tile.save(path)
    print(f"tiles written to {out} ({2*rows} files, tile ~{pw}x{ph})")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Slice images/logos.png sprite into 8 brand PNG variants and compress with pngquant."""

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

INPUT = Path(__file__).resolve().parent.parent / "images" / "logos.png"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "themes" / "minimal" / "static" / "images" / "brand"

EXPECTED_SIZE = (1536, 1024)
CELL_W = 384
CELL_H = 512

# (col, row, filename) — locked per CONTEXT.md D-04.
# row 0 = top of sprite (dark bg, light marks) → *-dark outputs.
# row 1 = bottom of sprite (light bg, dark marks) → *-light outputs.
CELLS = [
    (0, 0, "logo-dark.png"),
    (0, 1, "logo-light.png"),
    (1, 0, "icon-dark.png"),
    (1, 1, "icon-light.png"),
    (2, 0, "minimum-dark.png"),
    (2, 1, "minimum-light.png"),
    (3, 0, "favicon-dark.png"),
    (3, 1, "favicon-light.png"),
]

WORDMARK_MAX_BYTES = 30 * 1024  # BRAND-03 / D-08: ≤ 30 KB after pngquant
WORDMARK_FILES = ("logo-dark.png", "logo-light.png")

PNGQUANT_CMD = ["pngquant", "--quality=65-90", "--strip", "--force", "--output"]


def crop_cell(image, col, row):
    x0 = col * CELL_W
    y0 = row * CELL_H
    return image.crop((x0, y0, x0 + CELL_W, y0 + CELL_H))


def run_pngquant(path):
    # List form, check=True per D-06; --strip drops metadata per Claude's discretion in CONTEXT.md.
    subprocess.run(PNGQUANT_CMD + [str(path), str(path)], check=True)


def rgb_hex(pixel):
    # Image is 8-bit RGB per D-02 — pixel is a 3-tuple, no alpha.
    return "#{:02X}{:02X}{:02X}".format(pixel[0], pixel[1], pixel[2])


def fmt_kb(num_bytes):
    kb = num_bytes / 1024.0
    return "{:>5.1f} KB".format(kb)


def main():
    if not INPUT.exists():
        sys.exit("images/logos.png not found at {}".format(INPUT))

    if shutil.which("pngquant") is None:
        sys.exit("pngquant not found — install with 'brew install pngquant' (macOS) or your package manager")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    img = Image.open(INPUT)
    if img.size != EXPECTED_SIZE:
        sys.exit("images/logos.png expected size {} but got {}".format(EXPECTED_SIZE, img.size))
    if img.mode != "RGB":
        img = img.convert("RGB")

    # D-03: sample row corner pixels for the Phase 4 cross-phase contract.
    top_hex = rgb_hex(img.getpixel((0, 0)))
    bot_hex = rgb_hex(img.getpixel((0, CELL_H)))

    sizes = []
    for col, row, name in CELLS:
        out_path = OUTPUT_DIR / name
        cell = crop_cell(img, col, row)
        cell.save(out_path, format="PNG")
        run_pngquant(out_path)
        sizes.append((name, out_path.stat().st_size))

    # D-03 stdout contract — formatting is locked, do not change.
    print("Top-row (dark) bg fill:    {}".format(top_hex))
    print("Bottom-row (light) bg fill: {}".format(bot_hex))
    print()
    print("Outputs (path → size):")
    for name, num_bytes in sizes:
        print("  {:<20} → {}".format(name, fmt_kb(num_bytes)))

    # D-08 / BRAND-03 acceptance gate — fail loudly if wordmark variants exceed 30 KB.
    oversized = [(n, b) for (n, b) in sizes if n in WORDMARK_FILES and b > WORDMARK_MAX_BYTES]
    if oversized:
        msg_lines = ["Wordmark size gate failed (BRAND-03: ≤ 30 KB after pngquant):"]
        for n, b in oversized:
            msg_lines.append("  {} = {} bytes (limit {})".format(n, b, WORDMARK_MAX_BYTES))
        sys.exit("\n".join(msg_lines))


if __name__ == "__main__":
    main()

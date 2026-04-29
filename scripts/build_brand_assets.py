#!/usr/bin/env python3
"""Rasterize fav-icon.svg into favicon.ico (16/32/48) and apple-touch-icon.png (180x180)."""

import io
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from cairosvg import svg2png

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "images" / "brand-source"
THEME_STATIC_DIR = ROOT / "themes" / "minimal" / "static"
FAV_ICON_SVG = SOURCE_DIR / "fav-icon.svg"

APPLE_TOUCH_SIZE = 180
ICO_SIZES = [(16, 16), (32, 32), (48, 48)]

PNGQUANT_CMD = ["pngquant", "--quality=65-90", "--strip", "--force", "--output"]


def run_pngquant(path):
    subprocess.run(PNGQUANT_CMD + [str(path), str(path)], check=True)


def fmt_kb(num_bytes):
    kb = num_bytes / 1024.0
    return "{:>5.1f} KB".format(kb)


def build_favicon_ico(svg_path, out_path):
    """Multi-frame .ico (16/32/48) rasterized from fav-icon.svg (D-12)."""
    png_bytes = svg2png(url=str(svg_path), output_width=48, output_height=48)
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    img.save(out_path, format="ICO", sizes=ICO_SIZES)


def build_apple_touch(svg_path, out_path):
    """180x180 apple-touch-icon.png rasterized from fav-icon.svg (D-13)."""
    png_bytes = svg2png(url=str(svg_path), output_width=APPLE_TOUCH_SIZE, output_height=APPLE_TOUCH_SIZE)
    out_path.write_bytes(png_bytes)
    run_pngquant(out_path)


def main():
    if shutil.which("pngquant") is None:
        sys.exit("pngquant not found - install with 'brew install pngquant' (macOS) or your package manager")
    if not FAV_ICON_SVG.exists():
        sys.exit("Source SVG not found: {}".format(FAV_ICON_SVG))

    ico_path = THEME_STATIC_DIR / "favicon.ico"
    apple_path = THEME_STATIC_DIR / "apple-touch-icon.png"

    build_favicon_ico(FAV_ICON_SVG, ico_path)
    build_apple_touch(FAV_ICON_SVG, apple_path)

    sizes = [
        (ico_path.name, ico_path.stat().st_size),
        (apple_path.name, apple_path.stat().st_size),
    ]
    print("Outputs (path -> size):")
    for name, num_bytes in sizes:
        print("  {:<20} -> {}".format(name, fmt_kb(num_bytes)))


if __name__ == "__main__":
    main()

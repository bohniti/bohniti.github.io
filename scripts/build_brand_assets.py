#!/usr/bin/env python3
"""Process 8 brand source PNGs into themed light/dark output variants with matched aspects."""

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "images" / "brand-source"
OUTPUT_DIR = ROOT / "themes" / "minimal" / "static" / "images" / "brand"

# (asset, max_width, force_square)
# force_square=True forces a 1:1 canvas at max_width x max_width (favicon must be square for browser tabs).
ASSETS = [
    ("logo",     800, False),
    ("icon",     512, False),
    ("minimum",  500, False),
    ("favicon",  512, True),
]

VARIANTS = ("dark", "light")
DARK_BG = (0, 0, 0)
LIGHT_BG = (253, 253, 253)

WORDMARK_MAX_BYTES = 30 * 1024  # BRAND-03: logo wordmarks <= 30 KB after pngquant
WORDMARK_FILES = ("logo-dark.png", "logo-light.png")

PNGQUANT_CMD = ["pngquant", "--quality=65-90", "--strip", "--force", "--output"]


def variant_bg(variant):
    return DARK_BG if variant == "dark" else LIGHT_BG


def flatten_alpha(img, bg):
    if img.mode in ("RGBA", "LA"):
        rgba = img.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, bg)
        canvas.paste(rgba, mask=rgba.split()[3])
        return canvas
    return img.convert("RGB")


def trim_to_content(img, bg):
    bg_canvas = Image.new("RGB", img.size, bg)
    bbox = ImageChops.difference(img, bg_canvas).getbbox()
    if bbox is None:
        return img
    return img.crop(bbox)


def pad_to_aspect(img, target_aspect, bg):
    w, h = img.size
    cur = w / h
    if abs(cur - target_aspect) < 0.001:
        return img
    if cur < target_aspect:
        new_w = int(round(h * target_aspect))
        new_h = h
    else:
        new_w = w
        new_h = int(round(w / target_aspect))
    canvas = Image.new("RGB", (new_w, new_h), bg)
    canvas.paste(img, ((new_w - w) // 2, (new_h - h) // 2))
    return canvas


def resize_max(img, max_w):
    w, h = img.size
    if w <= max_w:
        return img
    ratio = max_w / w
    return img.resize((max_w, int(round(h * ratio))), Image.LANCZOS)


def run_pngquant(path):
    subprocess.run(PNGQUANT_CMD + [str(path), str(path)], check=True)


def rgb_hex(pixel):
    return "#{:02X}{:02X}{:02X}".format(pixel[0], pixel[1], pixel[2])


def fmt_kb(num_bytes):
    kb = num_bytes / 1024.0
    return "{:>5.1f} KB".format(kb)


def main():
    if shutil.which("pngquant") is None:
        sys.exit("pngquant not found - install with 'brew install pngquant' (macOS) or your package manager")

    if not SOURCE_DIR.exists():
        sys.exit("Source directory not found: {}".format(SOURCE_DIR))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sizes = []
    bg_samples = {}

    for asset, max_w, square in ASSETS:
        loaded = {}
        for variant in VARIANTS:
            src = SOURCE_DIR / "{}-{}.png".format(asset, variant)
            if not src.exists():
                sys.exit("Missing source: {}".format(src))
            bg = variant_bg(variant)
            img = flatten_alpha(Image.open(src), bg)
            img = trim_to_content(img, bg)
            loaded[variant] = (img, bg)

        if square:
            target_aspect = 1.0
        else:
            target_aspect = max(w / h for (img, _) in loaded.values() for (w, h) in [img.size])

        for variant in VARIANTS:
            img, bg = loaded[variant]
            img = pad_to_aspect(img, target_aspect, bg)
            if square:
                img = img.resize((max_w, max_w), Image.LANCZOS)
            else:
                img = resize_max(img, max_w)

            out_path = OUTPUT_DIR / "{}-{}.png".format(asset, variant)
            img.save(out_path, format="PNG")
            run_pngquant(out_path)
            sizes.append((out_path.name, out_path.stat().st_size))

            if variant not in bg_samples:
                bg_samples[variant] = rgb_hex(Image.open(out_path).convert("RGB").getpixel((0, 0)))

    print("Top-row (dark) bg fill:    {}".format(bg_samples.get("dark", "?")))
    print("Bottom-row (light) bg fill: {}".format(bg_samples.get("light", "?")))
    print()
    print("Outputs (path -> size):")
    for name, num_bytes in sizes:
        print("  {:<20} -> {}".format(name, fmt_kb(num_bytes)))

    oversized = [(n, b) for (n, b) in sizes if n in WORDMARK_FILES and b > WORDMARK_MAX_BYTES]
    if oversized:
        msg_lines = ["Wordmark size gate failed (BRAND-03: <= 30 KB after pngquant):"]
        for n, b in oversized:
            msg_lines.append("  {} = {} bytes (limit {})".format(n, b, WORDMARK_MAX_BYTES))
        sys.exit("\n".join(msg_lines))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Process brand source PNGs into themed light/dark variants and the 3-file favicon set."""

import base64
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

THEME_STATIC_DIR = ROOT / "themes" / "minimal" / "static"
APPLE_TOUCH_SIZE = 180
ICO_SIZES = [(16, 16), (32, 32), (48, 48)]

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


def build_favicon_ico(source_png_path, out_path):
    """Multi-size .ico (16/32/48) from favicon-light.png (D-10)."""
    img = Image.open(source_png_path).convert("RGB")
    img.save(out_path, format="ICO", sizes=ICO_SIZES)


def build_apple_touch(source_png_path, out_path):
    """180x180 apple-touch-icon.png from favicon-light.png (D-11)."""
    img = Image.open(source_png_path).convert("RGB")
    img = img.resize((APPLE_TOUCH_SIZE, APPLE_TOUCH_SIZE), Image.LANCZOS)
    img.save(out_path, format="PNG")
    run_pngquant(out_path)


def build_favicon_svg(light_png_path, dark_png_path, out_path):
    """PNG-wrapped SVG with embedded prefers-color-scheme dark @media (D-07, D-08)."""
    with open(light_png_path, "rb") as f:
        light_b64 = base64.b64encode(f.read()).decode("ascii")
    with open(dark_png_path, "rb") as f:
        dark_b64 = base64.b64encode(f.read()).decode("ascii")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" '
        'width="512" height="512">'
        '<style>@media (prefers-color-scheme: dark){{.l{{display:none}}.d{{display:inline}}}}'
        '.d{{display:none}}</style>'
        '<image class="l" href="data:image/png;base64,{light}" width="512" height="512"/>'
        '<image class="d" href="data:image/png;base64,{dark}" width="512" height="512"/>'
        '</svg>'
    ).format(light=light_b64, dark=dark_b64)
    out_path.write_text(svg, encoding="ascii")


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

    favicon_light = OUTPUT_DIR / "favicon-light.png"
    favicon_dark = OUTPUT_DIR / "favicon-dark.png"

    ico_path = THEME_STATIC_DIR / "favicon.ico"
    apple_path = THEME_STATIC_DIR / "apple-touch-icon.png"
    svg_path = THEME_STATIC_DIR / "favicon.svg"

    build_favicon_ico(favicon_light, ico_path)
    build_apple_touch(favicon_light, apple_path)
    build_favicon_svg(favicon_light, favicon_dark, svg_path)

    sizes.append((ico_path.name, ico_path.stat().st_size))
    sizes.append((apple_path.name, apple_path.stat().st_size))
    sizes.append((svg_path.name, svg_path.stat().st_size))

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

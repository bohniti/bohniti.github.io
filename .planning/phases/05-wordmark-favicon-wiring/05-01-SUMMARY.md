---
phase: 05-wordmark-favicon-wiring
plan: 01
subsystem: brand-asset-pipeline
tags:
  - python
  - pillow
  - favicon
  - asset-pipeline
  - build-script
requires:
  - "themes/minimal/static/images/brand/favicon-light.png (Phase 3 output, 26.5 KB)"
  - "themes/minimal/static/images/brand/favicon-dark.png (Phase 3 output, 30.2 KB)"
  - "Pillow >= 10.0 (throwaway venv only — installed 11.3.0)"
  - "pngquant 3.0.3 (already required by Phase 3 — reused)"
provides:
  - "scripts/build_brand_assets.py: build_favicon_ico, build_apple_touch, build_favicon_svg helpers + main() wire-in"
  - "themes/minimal/static/favicon.ico (5.3 KB, 3 frames: 16x16, 32x32, 48x48)"
  - "themes/minimal/static/apple-touch-icon.png (4.9 KB, 180x180)"
  - "themes/minimal/static/favicon.svg (75.2 KB, PNG-wrapped with embedded prefers-color-scheme dark @media)"
affects:
  - "Plan 05-03 (favicon partial + baseof.html <head> wiring) — these 3 files are the consumed assets"
tech-stack:
  added:
    - "base64 (stdlib import — no new third-party dep)"
  patterns:
    - "Pillow Image.save(format='ICO', sizes=[...]) for multi-size .ico"
    - "Pillow Image.resize((180,180), Image.LANCZOS) + run_pngquant for apple-touch"
    - "base64.b64encode of PNG bytes embedded as data URI in inline SVG <image href>"
    - "Throwaway venv invocation (D-09) — same pattern Phase 3 used; not in any runtime manifest"
key-files:
  created:
    - "themes/minimal/static/favicon.ico"
    - "themes/minimal/static/favicon.svg"
    - "themes/minimal/static/apple-touch-icon.png"
  modified:
    - "scripts/build_brand_assets.py"
decisions:
  - "Honored D-12: 3 favicon files placed at theme static root, not under images/brand/"
  - "Honored D-10/D-11: favicon-light.png is the source for both .ico and apple-touch (not theme-swapped — browsers don't swap .ico, and apple-touch is always shown on iOS home screen which has variable wallpaper)"
  - "Honored D-07/D-08: PNG-wrapped SVG with embedded @media swap; both PNGs base64-embedded as data URIs (self-contained, no external href refs)"
  - "Honored D-09: extended existing scripts/build_brand_assets.py rather than creating a new script — single asset pipeline owns all brand outputs"
  - "Did NOT mkdir THEME_STATIC_DIR per D-12 — it already exists in the repo (sibling of static/css/, static/images/)"
metrics:
  duration: "~190s"
  completed: "2026-04-29"
  tasks_completed: "2/2"
  files_changed: 4
  commits:
    - "04caf31: feat(05-01): extend build_brand_assets.py with 3 favicon output stages"
    - "68c1873: feat(05-01): add 3-file favicon set at theme static root"
---

# Phase 5 Plan 01: Brand Asset Pipeline — Favicon Outputs Summary

**One-liner:** Extended `scripts/build_brand_assets.py` with 3 additive favicon output stages (multi-size `.ico`, 180×180 apple-touch PNG, PNG-wrapped SVG with prefers-color-scheme dark @media) and ran the pipeline once in a throwaway Pillow venv to materialize all 3 files at `themes/minimal/static/`.

## What Was Built

### `scripts/build_brand_assets.py` (modified — additive only)

- **Module docstring** updated from "Process 8 brand source PNGs into themed light/dark output variants with matched aspects." to "Process brand source PNGs into themed light/dark variants and the 3-file favicon set."
- **Stdlib import** added: `import base64` (PEP 8 grouping, after `sys`, before `from pathlib import Path`)
- **3 module-level constants** added in the existing constants block:
  - `THEME_STATIC_DIR = ROOT / "themes" / "minimal" / "static"`
  - `APPLE_TOUCH_SIZE = 180`
  - `ICO_SIZES = [(16, 16), (32, 32), (48, 48)]`
- **3 helper functions** added between `run_pngquant` and `rgb_hex`, matching existing helper granularity (single-purpose, snake_case, no type hints, single-line docstrings):
  - `build_favicon_ico(source_png_path, out_path)` — Pillow ICO save with `sizes=ICO_SIZES`
  - `build_apple_touch(source_png_path, out_path)` — LANCZOS resize to 180×180 then `run_pngquant`
  - `build_favicon_svg(light_png_path, dark_png_path, out_path)` — base64 both PNGs, format inline SVG with embedded `<style>@media (prefers-color-scheme: dark)…</style>` and two `<image>` elements
- **`main()` wire-in** — 3-stage block inserted between the existing 8-PNG ASSETS loop and the verbose print block. The 3 new outputs are appended to the same `sizes` list so they appear in the existing `path -> size` report (no new print code).

### 3 new committed files at `themes/minimal/static/`

| File                  | Size    | Content shape                                                                       |
| --------------------- | ------- | ----------------------------------------------------------------------------------- |
| `favicon.ico`         | 5.3 KB  | MS Windows icon resource, 3 embedded frames at 16×16, 32×32, 48×48 (D-10 satisfied) |
| `apple-touch-icon.png`| 4.9 KB  | PNG, 180×180 RGB (D-11 satisfied)                                                   |
| `favicon.svg`         | 75.2 KB | XML with `viewBox="0 0 512 512"`, embedded `@media (prefers-color-scheme: dark)` rule, two `<image>` elements with `data:image/png;base64,…` URIs (D-07, D-08 satisfied) |

## Verification

### Automated checks (all pass)

- `python3 -c "import ast; ast.parse(open('scripts/build_brand_assets.py').read())"` — exit 0 (valid Python)
- `python3 -c "...; names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]; assert all 3 helpers present"` — pass (full list: `variant_bg, flatten_alpha, trim_to_content, pad_to_aspect, resize_max, run_pngquant, build_favicon_ico, build_apple_touch, build_favicon_svg, rgb_hex, fmt_kb, main`)
- `grep -c "^def build_favicon_ico\|^def build_apple_touch\|^def build_favicon_svg" scripts/build_brand_assets.py` → `3`
- `grep -n "^import base64$"` → 1 match (line 4)
- `grep -n "^THEME_STATIC_DIR = "` → 1 match (line 32)
- `grep -n "^APPLE_TOUCH_SIZE = 180$"` → 1 match (line 33)
- `grep -n "^ICO_SIZES = "` → 1 match (line 34)
- `grep -n 'sizes=ICO_SIZES'` → matches inside `build_favicon_ico` (line 91)
- `grep -c "Image.LANCZOS"` → 3 matches (existing `resize_max` at line 81, the existing `square` resize at line 161, plus new `build_apple_touch` at line 96)
- `grep -n 'data:image/png;base64'` → 2 matches inside `build_favicon_svg` (lines 113, 114)
- `grep -n 'prefers-color-scheme: dark'` → 1 match inside `build_favicon_svg` (line 111)
- `grep -n 'build_favicon_ico(favicon_light, ico_path)'` → 1 match inside `main()` (line 180)
- `grep -c "for asset, max_w, square in ASSETS"` → 1 match (existing 8-PNG loop unchanged)
- `grep -c "WORDMARK_MAX_BYTES"` → 3 matches (declaration line 29 + 2 usages — BRAND-03 gate intact)

### End-to-end pipeline run

Pillow 11.3.0 throwaway venv at `/tmp/gsd-phase5-venv`. Script exited 0. Verbose stdout (verbatim):

```
Top-row (dark) bg fill:    #000000
Bottom-row (light) bg fill: #FEFEFE

Outputs (path -> size):
  logo-dark.png        ->  26.1 KB
  logo-light.png       ->  19.9 KB
  icon-dark.png        ->  20.5 KB
  icon-light.png       ->  15.1 KB
  minimum-dark.png     ->   9.5 KB
  minimum-light.png    ->  10.1 KB
  favicon-dark.png     ->  30.2 KB
  favicon-light.png    ->  25.9 KB
  favicon.ico          ->   5.3 KB
  apple-touch-icon.png ->   4.9 KB
  favicon.svg          ->  75.2 KB
```

- Phase 4 D-02 corner-pixel contract preserved (`#FEFEFE` light / `#000000` dark)
- BRAND-03 30 KB wordmark gate held (logo-dark 26.1 KB, logo-light 19.9 KB)
- 3 new favicon files appear in the same `path -> size` report alongside the existing 8 PNGs

### File-shape gates

- `file themes/minimal/static/favicon.ico` reports "MS Windows icon resource - 3 icons, 16x16 …, 32x32 …" (macOS `file` truncates after the 2nd frame, but Pillow `Image.open(...).ico.sizes()` returns `[(16, 16), (32, 32), (48, 48)]` — all 3 frames physically present per the binary structure)
- `Image.open('themes/minimal/static/apple-touch-icon.png').size` → `(180, 180)` (D-11 verified)
- `grep -c '<image class="l" href="data:image/png;base64,'` → `1`
- `grep -c '<image class="d" href="data:image/png;base64,'` → `1`
- `grep -c 'prefers-color-scheme: dark'` → `1`
- `grep -c 'viewBox="0 0 512 512"'` → `1`

### Phase 3 contract intact

- `ls themes/minimal/static/images/brand/*.png | wc -l` → `8` (unchanged)
- `ls themes/minimal/static/images/brand/{favicon.ico,favicon.svg,apple-touch-icon.png} 2>/dev/null | wc -l` → `0` (favicon outputs NOT polluting the brand/ dir per D-12)
- The 8 brand PNGs were re-pngquanted by the second run but git diff shows zero byte changes — pipeline is deterministic and idempotent

## Deviations from Plan

None — plan executed exactly as written. No bugs found, no missing critical functionality, no blockers, no architectural decisions needed.

The macOS `file` command truncating its multi-frame .ico output after the second frame is a tooling cosmetic, not a defect: the binary itself contains all 3 frames per Pillow introspection (`im.ico.sizes() == [(16,16), (32,32), (48,48)]`), and the must_haves.truths "favicon.ico contains exactly 3 embedded frames" is satisfied verbatim.

## Authentication Gates

None — this plan is local file pipeline work; no auth required.

## Throwaway Venv (D-09 pattern)

```bash
python3 -m venv /tmp/gsd-phase5-venv
/tmp/gsd-phase5-venv/bin/pip install --quiet --upgrade pip
/tmp/gsd-phase5-venv/bin/pip install --quiet 'Pillow>=10.0'
/tmp/gsd-phase5-venv/bin/python scripts/build_brand_assets.py
rm -rf /tmp/gsd-phase5-venv  # ephemeral cleanup
```

Pillow 11.3.0 was installed; `Pillow >= 10.0` is the documented minimum (10.x supports the `Image.save(format="ICO", sizes=[...])` kwarg). Per D-11 the venv is intentionally NOT added to any runtime manifest — Hugo build, GitHub Actions deploy, and any other automated pipeline DO NOT depend on Pillow. The script is human-invoked once when brand source assets change.

## Self-Check: PASSED

- File `scripts/build_brand_assets.py` — FOUND (modified)
- File `themes/minimal/static/favicon.ico` — FOUND (5413 bytes)
- File `themes/minimal/static/favicon.svg` — FOUND (77001 bytes)
- File `themes/minimal/static/apple-touch-icon.png` — FOUND (5026 bytes)
- Commit `04caf31` (Task 1: build_brand_assets.py extension) — FOUND
- Commit `68c1873` (Task 2: 3 favicon outputs) — FOUND

## TDD Gate Compliance

Not applicable — `tdd="false"` on both tasks (asset pipeline extension + binary file generation, not behavioral code).

## Threat Surface Scan

No new threat surface introduced beyond the threat model in `05-01-PLAN.md`:

- T-05-01 (Tampering via subprocess) — accepted; only `run_pngquant` reused on the apple-touch output, fixed argv pattern, no `shell=True`, no user-supplied paths
- T-05-02 (Information-Disclosure via base64 embed) — accepted; inputs are project-controlled brand PNGs in the repo, no PII, output is a public web asset

The 3 new favicon files are public static assets shipped to all visitors. No new network endpoints, no new auth paths, no new file-access patterns at trust boundaries.

## Known Stubs

None — every output is fully wired. Plan 05-03 (favicon partial + `baseof.html` `<head>` include) consumes the 3 files via `<link>` tags; this plan completes the asset-existence half of HEAD-04 (browser favicon visible in tabs/bookmarks).

## Requirements Touched

- `HEAD-04` — partial coverage at the asset-existence level: 3-file favicon set materialized. Plan 05-03 wires them into the `<head>` for full HEAD-04 closure.

## Next Plan

Plan 05-03 (favicon partial + `<head>` wiring) consumes the 3 files this plan ships:
- `themes/minimal/layouts/partials/favicon.html` — 3 `<link>` tags (D-13)
- `themes/minimal/layouts/_default/baseof.html` — `{{ partial "favicon.html" . }}` between `<title>` and `<meta name="description">` (D-14)

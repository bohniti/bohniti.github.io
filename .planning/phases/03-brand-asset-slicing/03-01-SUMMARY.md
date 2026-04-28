---
phase: 03-brand-asset-slicing
plan: 01
status: complete
completed: 2026-04-28
requirements: [BRAND-01, BRAND-02, BRAND-03]
---

# Plan 03-01 Summary: Brand Asset Pipeline

## What was built

A Pillow + pngquant pipeline at `scripts/build_brand_assets.py` (renamed from the originally-planned `scripts/slice_logos.py` via `git mv`) that processes 8 brand source PNGs at `images/brand-source/` into themed light/dark output variants at `themes/minimal/static/images/brand/`. The pipeline:

1. Flattens RGBA inputs onto the variant's bg color (`(0,0,0)` dark, `(253,253,253)` light) — D-02 spirit upheld, output is pure RGB.
2. Auto-trims each input to its content bbox via `ImageChops.difference` against the bg.
3. Aspect-matches each `{asset}-dark` / `{asset}-light` pair by padding the narrower image with bg color to the wider aspect — so the theme toggle does not visually shift the wordmark.
4. Resizes per asset class: logo 800px max width, icon 512px max width, minimum 500px max width, favicon forced 512×512 square (browser-tab requirement).
5. pngquant-compresses each output with `--quality=65-90 --strip --force`.
6. Enforces the BRAND-03 30 KB ceiling on `logo-dark.png` / `logo-light.png` via `sys.exit` non-zero.
7. Prints the D-03 cross-phase contract (dark + light bg hex values) for Phase 4.

## Plan deviation

The locked sprite assumption (D-01: 1536×1024 with rows split exactly at y=512) did not hold against the real `images/logos.png` — the actual dark→light row transition is at y≈570. Equal-grid slicing produced bottom-row variants with a ~58 px dark band stripe and broke the D-03 corner-pixel hex contract (both samples read `#030202` / `#030303` instead of one dark + one light).

User decision: re-supply assets as 8 individual PNG screenshots and replace the slicer with an asset-processing pipeline.

Decisions superseded: D-01, D-04, D-05.
Decisions upheld: D-02, D-03, D-06, D-07, D-08, D-09, D-10, D-11.
Full deviation rationale recorded in `03-CONTEXT.md` § "Mid-Execution Deviation (2026-04-28)".

## D-03 cross-phase contract handoff to Phase 4

Phase 4 must paste these exact values into `themes/minimal/static/css/style.css`:

```
Top-row (dark) bg fill:    #000000
Bottom-row (light) bg fill: #FEFEFE
```

Mapping:
- `--bg-dark` (dark theme bg) = `#000000`
- `--bg` (light theme bg) = `#FEFEFE`

Deviating from these values will reintroduce a visible rectangular seam framing each wordmark `<img>` because the brand PNGs ship with opaque backgrounds, not alpha-keyed transparency.

## Outputs

| File | Dimensions | Size |
|---|---|---|
| favicon-dark.png | 512×512 | 30.2 KB |
| favicon-light.png | 512×512 | 25.9 KB |
| icon-dark.png | 469×470 | 20.5 KB |
| icon-light.png | 512×513 | 15.1 KB |
| logo-dark.png | 800×467 | 26.1 KB |
| logo-light.png | 800×467 | 19.9 KB |
| minimum-dark.png | 440×217 | 9.5 KB |
| minimum-light.png | 446×220 | 10.1 KB |

Total: 157.3 KB across 8 PNGs.

## Acceptance criteria — all PASS

| # | Criterion | Result |
|---|---|---|
| 1 | Exactly 8 PNGs at `themes/minimal/static/images/brand/` with locked names (`{logo,icon,minimum,favicon}-{dark,light}.png`) | PASS — 8 PNGs, names match |
| 2 | `scripts/build_brand_assets.py` committed; single-line docstring; mirrors `scripts/transform_climbing_csv.py` shape (shebang, stdlib-first imports, `UPPER_CASE` constants, `snake_case` helpers, no type hints, `__main__` guard) | PASS |
| 3 | `logo-dark.png` and `logo-light.png` each ≤ 30720 bytes after pngquant (BRAND-03) | PASS — 26757 and 20418 bytes |
| 4 | Aspect-pair consistency (deviation-reinterpreted from "consistent column dimensions"): each `{asset}-dark` and `{asset}-light` share the same aspect ratio (Δ < 0.005) so theme toggle produces no layout shift | PASS — all 4 pairs Δ ≤ 0.0004 |

## Patterns established

- **Throwaway venv tooling pattern (D-11 upheld):** Pillow installed at `/tmp/slice-logos-venv/`, never added to a project manifest. Reusable for any future image processing script.
- **pngquant subprocess invocation pattern:** `subprocess.run(["pngquant", "--quality=65-90", "--strip", "--force", "--output", out, in], check=True)`. First use of pngquant in this repo. Reusable for any future PNG asset that needs lossless palette compression.
- **Aspect-pair matching for theme-variant assets:** generalizable approach — if a future feature ships asset pairs that toggle (e.g. light/dark icons in blog posts), the same trim → match-pair-aspect → resize pipeline applies.
- **flatten_alpha + trim_to_content pattern:** for any RGBA source where the desired output is solid-bg RGB. Avoids fringe artifacts from threshold-based bg removal.

## Files

| Created/Modified | File |
|---|---|
| Created | `scripts/build_brand_assets.py` (renamed from `scripts/slice_logos.py`, fully rewritten) |
| Created | `images/brand-source/{logo,icon,minimum,favicon}-{dark,light}.png` (8 source screenshots) |
| Created | `themes/minimal/static/images/brand/{logo,icon,minimum,favicon}-{dark,light}.png` (8 outputs) |
| Modified | `.planning/phases/03-brand-asset-slicing/03-CONTEXT.md` (deviation note appended) |
| Deleted | `scripts/slice_logos.py` (replaced by `build_brand_assets.py`) |

## Commits

- `55c2b39` — initial `scripts/slice_logos.py` (Task 1, sprite-based; superseded by deviation)
- `088c238` — replace slicer with brand asset processor; produces 8 outputs; CONTEXT deviation recorded

## Self-Check: PASSED

- [x] All 8 PNGs exist at the expected path
- [x] All 4 acceptance criteria pass
- [x] Wordmarks well under the 30 KB BRAND-03 gate (26.1 / 19.9 KB vs 30 KB limit)
- [x] Aspect ratios match within each pair (Δ ≤ 0.0004 across all 4 pairs)
- [x] D-03 cross-phase contract values recorded for Phase 4
- [x] Deviation rationale documented in CONTEXT.md
- [x] Script commits, runs end-to-end with exit 0, mirrors `transform_climbing_csv.py` conventions

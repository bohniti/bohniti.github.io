# Phase 3: Brand Asset Slicing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `03-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-28
**Phase:** 03-brand-asset-slicing
**Areas discussed:** Crop strategy, Background / alpha handling, -light/-dark naming semantics, Favicon outputs & pngquant integration

---

## Crop Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Equal grid (384×512) | Slice exactly 1/4 width × 1/2 height per cell, hardcoded in script. Reproducible, simple, matches success criterion #4 ("logo cells equal logo cells"). Each output keeps any inherent whitespace from the source design. | ✓ |
| Per-column tuned crop boxes | Measure each column's content extent in Pillow and hardcode 4 column widths summing to 1536. Tighter outputs but brittle if logos.png is re-exported. | |
| Auto-trim transparent/uniform borders | Equal-grid first, then trim each output's matching-color border. Tightest crops automatically, but source is RGB so risks over-trim of intentional light/dark wordmark pixels. | |
| Equal grid + visual alignment check | Equal grid + script asserts cell content's alpha/color centroid is reasonably centered. Catches off-by-one drift without hand-tuning. | |

**User's choice:** Equal grid (384×512) — reproducible, satisfies acceptance criterion, no manual measurement.
**Notes:** None.

---

## Background / Alpha Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Keep RGB, opaque backgrounds | Output 8 PNGs as RGB with original cell backgrounds. Phase 5 places each variant on a theme background that matches its fill. Simplest, no fringe risk. | ✓ |
| Key-out to RGBA via color threshold | Convert each cell to RGBA, replace pixels close to the cell's corner color with alpha=0. Wordmark sits transparently on any theme. Anti-aliased edges produce fringe pixels (the "white halos" the acceptance criterion warns against). | |
| Convert to RGBA, leave fully opaque | Promote mode to RGBA, alpha=255 everywhere. Satisfies a literal "alpha-preserving" read of BRAND-01 without changing visible output. Slightly larger files. | |

**User's choice:** Keep RGB, opaque backgrounds.
**Notes:** Followed up on the cross-phase implication (cell fill must match theme bg).

### Follow-up: Background colour matching

| Option | Description | Selected |
|--------|-------------|----------|
| Sample & document fill colors | Slicer samples corner pixel of each cell and prints hex codes to stdout. Phase 4's dark palette uses those exact hex values as `--bg-dark` so the wordmark blends. | ✓ |
| Trust Flexoki defaults | Assume the sprite's dark fill matches Flexoki dark base color (#100F0F) and the light fill matches #FFFCF0. No sampling, no verification — just document the assumption. | |
| Defer to Phase 5 wiring | Slicer doesn't care about colors. Phase 5 verifies the wordmark blends with the active theme bg — fix any seam by re-keying that one PNG. | |

**User's choice:** Sample & document fill colors — zero-cost guarantee, gives Phase 4 exact values to use.
**Notes:** Locked as a hard cross-phase contract: Phase 4 must adopt these hex values in `--bg` / `--bg-dark`.

---

## -light / -dark Naming Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| -light = for light theme (dark wordmark) | `logo-light.png` = the variant designed to sit on a light background, i.e. dark wordmark from the bottom row. Reads naturally in `html[data-theme="light"]` selectors. | ✓ |
| -light = looks light (top row) | `logo-light.png` = the variant that LOOKS light (light-coloured wordmark from top dark-background row). Inverts Phase 5 selector logic. | |

**User's choice:** -light = for light theme.
**Notes:** Sprite-row → output mapping locked: top row → `*-dark.png`, bottom row → `*-light.png`.

---

## Favicon Outputs & pngquant Integration

### Favicon Output Dimensions

| Option | Description | Selected |
|--------|-------------|----------|
| Raw 384×512 cell only | Slicer outputs `favicon-light.png` and `favicon-dark.png` at the raw cell dimension. Phase 5 handles all final sizing. Keeps Phase 3 pure "slicing". | ✓ |
| Raw cell + 180×180 apple-touch | Slicer also emits a single resized 180×180 apple-touch from one favicon. | |
| Full favicon set (raw + 180 + 32 + 16) | Slicer emits raw cells AND apple-touch (180), 32, 16. | |
| Raw cell + tightly cropped favicon | Raw cell AND a square content-tight crop (256×256). | |

**User's choice:** Raw 384×512 cell only — keeps Phase 3 scoped to slicing.

### pngquant Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Inside slicer (subprocess call) | Slicer runs `pngquant --quality=65-90 --force --output <path> <path>` per output via subprocess. Single-command pipeline. Fails fast if pngquant not on PATH with install hint. | ✓ |
| Separate documented step | Slicer only writes raw PNGs; humans run `pngquant` separately as documented in docstring/commit. | |
| Inside slicer, optional fallback | Try pngquant; warn and skip if not installed (won't meet 30 KB ceiling). | |

**User's choice:** Inside slicer (subprocess call) — single command, fail-fast on missing pngquant.

---

## Claude's Discretion

- Run-pattern documentation location (docstring vs README) — pick whichever lands cleanly without bloat.
- Internal script structure (single function vs module-level vs class) — match `transform_climbing_csv.py`'s formality level.
- Exact pngquant flag values within `--quality=65-90` envelope.
- Whether to strip metadata via Pillow / pngquant (sensible default: strip).

## Deferred Ideas

- Per-column content-fit cropping (rejected — pixel measurement + brittle to sprite re-export).
- Auto-trim on uniform-color borders (rejected — RGB source, risks over-trim).
- Alpha keying / RGBA conversion (rejected — no source alpha, fringe artifacts).
- Pre-resized favicons / .ico / .svg / apple-touch (Phase 5 scope).
- Sprite re-export resilience checks beyond fixed-dimension assertion (overengineering for this phase).

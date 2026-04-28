# Phase 3: Brand Asset Slicing - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Slice `images/logos.png` (1536×1024 RGB sprite, 2 rows × 4 cols) into 8 named PNG variants under `themes/minimal/static/images/brand/`, produced by a reproducible Pillow script at `scripts/slice_logos.py`. Outputs are raw assets only — wiring them into HTML/CSS is Phase 5; theming tokens that match their backgrounds are Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Crop Strategy
- **D-01:** Slicer crops on equal-grid integer cell boundaries — exactly 384×512 per cell (1536/4 wide × 1024/2 tall). Coordinates hardcoded as constants in the script. No per-asset hand-tuning, no auto-trim, no content-fit logic. Reproducible if `images/logos.png` is re-exported with the same 1536×1024 dimensions; satisfies success criterion #4 ("logo cells equal logo cells, favicon cells equal favicon cells — no off-by-one crop drift").

### Background & Alpha Handling
- **D-02:** Source is 8-bit RGB, no alpha channel. Outputs are written as RGB PNGs with their **original opaque cell backgrounds preserved** — top-row dark fill stays in the `-dark.png` outputs, bottom-row light fill stays in the `-light.png` outputs. No alpha keying, no RGBA promotion. Avoids fringe / halo artifacts from threshold-based background removal on anti-aliased wordmark edges.
- **D-03:** Slicer **samples the corner pixel of each row** and prints both hex values to stdout (and writes them as a comment block at the top of the script's run output). Example output:
  ```
  Top-row (dark) bg fill:    #100F0F
  Bottom-row (light) bg fill: #FFFCF0
  ```
  Phase 4's dark/light palette tokens (`--bg`, `--bg-dark`) **must use these exact hex values** so the wordmark blends seamlessly into the theme background — otherwise a visible rectangular seam frames each PNG. This is a hard cross-phase contract: changing the theme bg later means re-sampling and re-wiring.

### Naming Semantics
- **D-04:** `-light` / `-dark` suffix denotes **the theme each variant is used in**, NOT what the variant looks like:
  - `*-light.png` = used in **light theme** = the dark wordmark from the **bottom row** of the sprite (bottom = light-background variants in sprite-design terms)
  - `*-dark.png` = used in **dark theme** = the light wordmark from the **top row** of the sprite
  - Sprite-row → output mapping (locked):
    - **Top row** (dark backgrounds, light marks) → `logo-dark.png`, `icon-dark.png`, `minimum-dark.png`, `favicon-dark.png`
    - **Bottom row** (light backgrounds, dark marks) → `logo-light.png`, `icon-light.png`, `minimum-light.png`, `favicon-light.png`
  - This convention reads naturally in Phase 5 CSS selectors: `html[data-theme="light"] .wordmark { content: url('.../logo-light.png'); }`

### Favicon Outputs (Phase 3 Scope)
- **D-05:** `favicon-light.png` and `favicon-dark.png` are the **raw 384×512 cell crops** only — no resizing, no apple-touch, no .ico generation in this phase. The TB-in-circle sits centered with cell whitespace around it; that's fine — Phase 5 owns final favicon sizing (32×32 .ico, 180×180 apple-touch, optional .svg). Keeps Phase 3 strictly a "sprite → 8 PNGs" operation.

### pngquant Integration
- **D-06:** `scripts/slice_logos.py` runs `pngquant` **as a subprocess on each output PNG** as the final pipeline step. Single invocation of the script produces final assets ready to commit. Use `pngquant --quality=65-90 --force --output <path> <path>`.
- **D-07:** If `pngquant` is not on `PATH`, the script **fails fast** (non-zero exit) with a clear hint: `pngquant not found — install with 'brew install pngquant' (macOS) or your package manager`. No silent fallback to uncompressed PNGs (which would breach the ≤30 KB acceptance criterion).
- **D-08:** Acceptance gate (BRAND-03): after pngquant, the script verifies that `logo-light.png` and `logo-dark.png` are each ≤ 30 KB and prints final file sizes for all 8 outputs to stdout. If a wordmark variant exceeds 30 KB, the script exits non-zero so the run is treated as failed; the human re-runs after tuning quality range or re-exporting the source.

### Script Conventions (Inherits from Project)
- **D-09:** Single-line module docstring at top (matches `scripts/transform_climbing_csv.py` convention from `.planning/codebase/CONVENTIONS.md`).
- **D-10:** Uses `pathlib.Path` for filesystem ops; no type hints; PEP 8; `if __name__ == "__main__":` guard.
- **D-11:** Pillow installed in a **throwaway venv** by the human invoking the script — not added to any runtime manifest (no `requirements.txt`, no `pyproject.toml`). Documented invocation pattern (Claude's discretion to land in docstring or a one-liner README, see below).

### Claude's Discretion
- Run-pattern documentation location: docstring vs separate README — pick whichever lands cleanly in the script header without bloat.
- Internal script structure (single function vs module-level vs class) — match `transform_climbing_csv.py`'s level of formality.
- Exact pngquant flag values within `--quality=65-90` envelope — adjust if 30 KB ceiling can't be met at 65-90.
- Output color profile / strip metadata — strip is sensible default; not a user-facing decision.

### Folded Todos
None — no pending todos in STATE.md matched this phase's scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & Requirements
- `.planning/ROADMAP.md` § "Phase 3: Brand Asset Slicing" — phase goal, dependencies (none), success criteria (4 items)
- `.planning/REQUIREMENTS.md` § "Brand Assets" — BRAND-01 (8 PNGs at integer boundaries with alpha preserved), BRAND-02 (committed Pillow script), BRAND-03 (≤ 30 KB wordmark after pngquant)
- `.planning/PROJECT.md` § "Context" — sprite layout description (2×4, top dark / bottom light, columns: Logo / Icon / Minimum / Favicon)
- `.planning/PROJECT.md` § "Key Decisions" — locks: Pillow one-off slicer (not Hugo Crop), throwaway venv, output to `themes/minimal/static/images/brand/`

### Codebase Conventions
- `.planning/codebase/CONVENTIONS.md` § "Python Script Conventions" — PEP 8, snake_case, single-line docstring, pathlib, no type hints, `if __name__ == "__main__"` guard
- `.planning/codebase/STRUCTURE.md` § "Where to Add New Code → New Utility Script" — `scripts/snake_case.py` pattern
- `scripts/transform_climbing_csv.py` — reference Python script in this repo for style/structure

### Source Asset
- `images/logos.png` — 1536×1024, 8-bit RGB (no alpha), 2 rows × 4 cols. Top row = dark-background variants, bottom = light-background. Columns L→R: Logo (script "time BOHNSTEDT" with climber), Icon (TB monogram), Minimum (script "time" only), Favicon (TB in circle).

### Cross-Phase Contracts
- **Phase 4 (Theming Foundation):** must use the dark/light bg hex values that this phase's slicer prints to stdout — `--bg` (light theme) = bottom-row corner hex; `--bg-dark` (dark theme) = top-row corner hex. Otherwise a visible seam frames each wordmark.
- **Phase 5 (Wordmark + Favicon Wiring):** consumes all 8 outputs from `themes/minimal/static/images/brand/`. Wordmark CSS selector keys off `html[data-theme]` matching the filename suffix (`-light` for light theme, `-dark` for dark theme). Favicon resizing (32, 180, .ico, .svg) is Phase 5's responsibility.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/transform_climbing_csv.py` — reference Python script pattern in this repo: single-line docstring, `pathlib.Path` constants for INPUT/OUTPUT, module-level main, `if __name__ == "__main__"` guard. `scripts/slice_logos.py` should mirror this exactly.

### Established Patterns
- **Python conventions** (CONVENTIONS.md): PEP 8, `snake_case` functions/vars, `UPPER_CASE` module constants, no type hints, `pathlib.Path` for paths. New script must match.
- **Single utility script per file** — no shared module library; each script self-contained. `slice_logos.py` will be self-contained, no shared imports beyond stdlib + Pillow.
- **Throwaway tooling pattern** — Hugo project has zero Python runtime deps; existing CSV transform script also assumes manual venv. Pillow follows the same pattern: human-invoked, ephemeral environment.

### Integration Points
- **Output dir:** `themes/minimal/static/images/brand/` — must be created by the slicer (mkdir -p semantics via `Path.mkdir(parents=True, exist_ok=True)`); Hugo serves this verbatim at `/images/brand/*.png` after build.
- **Source:** `images/logos.png` at repo root (NOT under `static/` or `themes/minimal/static/`) — already in the repo, untracked changes show none for it.
- **No Hugo template touched in this phase** — Phase 5 does the `<img>` and `<link rel="icon">` wiring.
- **No CSS touched in this phase** — Phase 4 owns the palette tokens that need to match the slicer's printed hex values.

</code_context>

<specifics>
## Specific Ideas

- Slicer prints both row-corner hex values to stdout in a Phase-4-friendly format (e.g., one line per row, labeled). This is the only "non-pure" output beyond the 8 PNGs — it's deliberate, so Phase 4 can copy/paste the values.
- Failure modes that should exit non-zero: `images/logos.png` not found, dimensions ≠ 1536×1024, `pngquant` not on PATH, any wordmark output > 30 KB after compression.
- The script is run **manually by a human** before Phase 5 work starts; not part of the Hugo build, not part of CI.

</specifics>

<deferred>
## Deferred Ideas

- Per-column content-fit cropping — rejected for this phase (would need pixel measurement and break under sprite re-export). Could revisit if equal-grid outputs ship visible whitespace that downstream wiring can't tolerate.
- Auto-trim on uniform-color borders — rejected: source is RGB, color-matching would risk over-trimming light/dark wordmark pixels.
- Alpha keying / RGBA conversion — rejected: source has no alpha, keying introduces fringe artifacts. Revisit only if Phase 4/5 surfaces a visible seam that can't be solved by matching theme tokens to D-03's printed hex.
- Pre-resized favicons (32×32, 180×180, .ico generation) — explicitly Phase 5's scope.
- Multi-size .ico bundling, .svg with embedded `prefers-color-scheme` — Phase 5.
- Inline SVG wordmark with `currentColor` — already in `REQUIREMENTS.md` § "Future Requirements (deferred to v2.x)".
- Sprite re-export resilience (visual alignment check, content centroid assertion) — rejected for this phase as overengineering. If the source sprite is ever re-exported, re-running the script with new equal-grid bounds is sufficient.

</deferred>

---

## Mid-Execution Deviation (2026-04-28)

The locked sprite assumption (D-01: 1536×1024 with rows split exactly at y=512) did not hold against the real `images/logos.png` — the actual dark→light row transition is at y≈570, so equal-grid slicing produced bottom-row variants with a ~58 px dark band stripe and broke the D-03 corner-pixel hex contract (both samples read near-black). Source was re-supplied as **8 individual PNG screenshots** dropped at `images/brand-source/{logo,icon,minimum,favicon}-{dark,light}.png` instead of a single sprite.

The slicer was replaced with an asset-processing pipeline at `scripts/build_brand_assets.py` (renamed via `git mv` from `scripts/slice_logos.py`).

**Decisions superseded:**
- **D-01** (equal-grid 384×512 slicer) → **superseded.** New pipeline auto-trims each input to its content bbox, then aspect-matches each dark/light pair so a theme toggle produces no layout shift. Output dimensions per asset class: logo 800px max width, icon 512px max width, minimum 500px max width, favicon forced 512×512 square (browser-tab requirement).
- **D-02** (RGB-only, opaque cell backgrounds) → **upheld.** Pipeline flattens RGBA inputs onto the variant's bg color (`(0,0,0)` dark, `(253,253,253)` light) before any further processing, output mode is RGB.
- **D-03** (stdout hex contract for Phase 4) → **upheld.** Pipeline samples `(0,0)` of one finished dark output and one finished light output and prints them in the same labeled format. Phase 4 still pastes these into `--bg` / `--bg-dark`.
- **D-04** (sprite-row → output mapping) → **superseded.** Mapping now comes from input filename (`{asset}-{variant}.png` in source → identical name in output).
- **D-05** (raw 384×512 favicon cells) → **superseded.** Favicon is forced 512×512 square; tighter trim removes the surrounding canvas whitespace that was present in the source screenshot.
- **D-06**, **D-07**, **D-08** (pngquant integration, PATH check, BRAND-03 30 KB gate) → **upheld** verbatim.
- **D-09**, **D-10**, **D-11** (Python conventions, throwaway venv) → **upheld**.

**ROADMAP success criterion #4** ("consistent column dimensions — logo cells equal logo cells, favicon cells equal favicon cells, no off-by-one drift") is reinterpreted as **"aspect-pair consistency within each pair"**: each `{asset}-dark.png` and `{asset}-light.png` share the same aspect ratio (within 0.001), so toggling the theme does not visibly shift the wordmark in CSS layouts. Verified by `Image.open(...).size`.

**Recorded hex values for Phase 4 cross-phase contract (D-03):**
```
Top-row (dark) bg fill:    #000000
Bottom-row (light) bg fill: #FEFEFE
```

---

*Phase: 03-brand-asset-slicing*
*Context gathered: 2026-04-28*
*Mid-execution deviation recorded: 2026-04-28*

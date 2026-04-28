# Phase 3: Brand Asset Slicing - Pattern Map

**Mapped:** 2026-04-28
**Files analyzed:** 1 new file (+ 8 PNG artifacts, no code)
**Analogs found:** 1 / 1 (exact match)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/slice_logos.py` | utility (offline data/asset transform) | file-I/O batch | `scripts/transform_climbing_csv.py` | exact (same role, same flow shape: read input → transform → write outputs → print summary) |

**Artifacts (no code, no analog needed):**
- `themes/minimal/static/images/brand/{logo,icon,minimum,favicon}-{light,dark}.png` — 8 PNG outputs produced by the script. Created via `Path.mkdir(parents=True, exist_ok=True)` then `Image.crop().save()` + `pngquant` subprocess.

## Pattern Assignments

### `scripts/slice_logos.py` (utility, file-I/O batch)

**Analog:** `scripts/transform_climbing_csv.py` — only existing Python script in `scripts/`. Same data-flow shape: input file → deterministic transform → output files → summary printed to stdout. CONTEXT.md D-09 and D-10 explicitly mandate matching this script's conventions.

**Shebang + single-line module docstring** (analog lines 1-2):
```python
#!/usr/bin/env python3
"""Transform Vertical Life dataset.csv into Climbers Journal import format."""
```
→ Apply to `slice_logos.py`:
```python
#!/usr/bin/env python3
"""Slice images/logos.png sprite into 8 brand PNG variants and compress with pngquant."""
```

**Imports pattern** (analog lines 3-6):
```python
import csv
from collections import Counter
from pathlib import Path
```
- Stdlib first, no third-party imports in the analog (Pillow + `subprocess` are new for `slice_logos.py`).
- No `import` of project-internal modules — scripts are self-contained (CONTEXT.md `code_context > Established Patterns`).
→ Apply to `slice_logos.py`: `subprocess`, `sys`, `pathlib.Path`, then `from PIL import Image` after the stdlib block.

**Module-level constants pattern** (analog lines 8-27):
```python
INPUT = Path(__file__).resolve().parent.parent / "static" / "files" / "dataset.csv"
OUTPUT = INPUT.parent / "climbing_journal_import.csv"

STYLE_MAP = {
    "rp": "redpoint",
    "os": "onsight",
    ...
}

OUTPUT_COLUMNS = [
    "date", "tick_type", "crag_name", ...
]
```
Patterns to copy:
- `Path(__file__).resolve().parent.parent` to anchor at repo root — `slice_logos.py` will need `Path(__file__).resolve().parent.parent / "images" / "logos.png"` for INPUT and `... / "themes" / "minimal" / "static" / "images" / "brand"` for OUTPUT_DIR.
- `UPPER_CASE` for module-level constants (CONVENTIONS.md line 164).
- Constants are static lookup tables / paths — no environment reads, no argparse.
- Per CONTEXT.md D-01: cell coordinates are hardcoded as constants (`CELL_W = 384`, `CELL_H = 512`, `EXPECTED_SIZE = (1536, 1024)`).
- Per CONTEXT.md D-04: sprite-row → output mapping is locked. Encode as a `CELLS` table — list of `(col_index, row_index, output_filename)` tuples — analogous to `STYLE_MAP`'s static-mapping pattern.

**Helper-function pattern** (analog lines 30-52):
```python
def transform_row(row):
    date_raw = row.get("date", "")
    date = date_raw[:10] if len(date_raw) >= 10 else date_raw
    ...
    return { ... }
```
- Single-purpose top-level function, called from `main()`.
- `snake_case`, no type hints (CONVENTIONS.md line 165).
- No docstring on helpers (analog has none).
- Returns plain data — caller does the I/O.
→ For `slice_logos.py`, equivalent helpers are `crop_cell(image, col, row)` returning a `PIL.Image`, and `run_pngquant(path)` wrapping the subprocess call. Keep them module-level, no class.

**`main()` orchestration pattern** (analog lines 55-89):
```python
def main():
    warnings = []

    with open(INPUT, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    transformed = []
    tick_counts = Counter()

    for i, row in enumerate(rows, start=2):
        out = transform_row(row)
        tick_counts[out["tick_type"]] += 1
        ...
        transformed.append(out)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(transformed)

    print(f"Rows: {len(transformed)}")
    print(f"Tick types: {dict(tick_counts)}")
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
    print(f"\nOutput: {OUTPUT}")
```
Structural pattern to copy:
1. Initialize a `warnings = []` list (or equivalent collector for non-fatal issues).
2. Read input.
3. Loop, transforming each unit, accumulating outputs + summary counters.
4. Write outputs.
5. Print a summary block to stdout — counts, warnings, output path.
→ Apply to `slice_logos.py`:
1. Open `images/logos.png` with `Image.open(INPUT)`; assert size == `(1536, 1024)` per CONTEXT.md D-01 (fail-fast `sys.exit(1)` with hint if mismatch).
2. Sample top-row corner pixel `img.getpixel((0, 0))` and bottom-row corner `img.getpixel((0, 512))`; format as `#RRGGBB` hex strings.
3. Loop over `CELLS` table → `crop_cell` → `save` to `OUTPUT_DIR / filename` → `run_pngquant` on the saved file → `os.path.getsize` for the size summary.
4. Print:
   ```
   Top-row (dark) bg fill:    #100F0F
   Bottom-row (light) bg fill: #FFFCF0

   Outputs (path → size):
     logo-light.png       → 22.4 KB
     logo-dark.png        → 24.1 KB
     ...
   ```
   This satisfies CONTEXT.md D-03 (Phase 4 contract) and D-08 (size acceptance gate).
5. After printing, evaluate the `BRAND-03` gate: if `logo-light.png` or `logo-dark.png` > 30 KB, `sys.exit(1)` with the offending filename + size.

**`if __name__ == "__main__":` guard** (analog lines 92-93):
```python
if __name__ == "__main__":
    main()
```
→ Copy verbatim. CONVENTIONS.md line 168 + CONTEXT.md D-10 require this.

**Error handling pattern** (analog approach, CONVENTIONS.md line 218):
> "Python scripts: No explicit error handling; scripts are run manually and fail loudly."

The analog has zero try/except blocks — file-not-found and CSV parse errors are allowed to propagate as Python tracebacks. Mirror this for unexpected errors. **Exception:** CONTEXT.md adds explicit fail-fast checks for known pre-conditions (input missing, dimensions wrong, `pngquant` not on PATH, output > 30 KB). Use `sys.exit(1)` with a printed hint for those — no try/except, no logging framework.

Concrete failure-mode template (CONTEXT.md `<specifics>` line 109):
```python
if not INPUT.exists():
    sys.exit(f"images/logos.png not found at {INPUT}")

if shutil.which("pngquant") is None:
    sys.exit("pngquant not found — install with 'brew install pngquant' (macOS) or your package manager")
```

**Validation pattern:** None in the analog (CSV inputs are trusted). For `slice_logos.py`, the only validation is the dimension check (CONTEXT.md D-01) — single `if img.size != (1536, 1024): sys.exit(...)` line.

**Testing pattern:** No tests exist in this repo for `transform_climbing_csv.py` or any other code (no `tests/` dir, no test framework configured). Do not introduce a test file. Manual verification per CONTEXT.md `<specifics>` line 110: human runs the script before Phase 5.

---

## Shared Patterns

This phase has only one new code file, so "shared" patterns reduce to the single-file conventions above. The cross-cutting concerns relevant to that file:

### Self-contained utility script
**Source:** `scripts/transform_climbing_csv.py` (entire file, 94 lines)
**Apply to:** `scripts/slice_logos.py`
- Stdlib + one third-party import (Pillow, installed in throwaway venv per D-11).
- No shared module library imported from elsewhere in the repo.
- All logic in module scope + `main()` + a few small top-level helpers.

### pathlib for all filesystem ops
**Source:** `scripts/transform_climbing_csv.py` lines 8-9, plus CONVENTIONS.md line 167
**Apply to:** `scripts/slice_logos.py`
- Use `Path(__file__).resolve().parent.parent / "..."` to anchor at repo root.
- Use `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)` to create the brand dir (CONTEXT.md `code_context > Integration Points`).
- Pass `Path` objects to `Image.open()` and `Image.save()` — Pillow accepts them.
- Pass `str(path)` only when calling `subprocess.run(["pngquant", ..., str(path)])` to avoid Pillow/subprocess-arg ambiguity.

### Subprocess invocation (no analog — pattern from CONTEXT.md D-06)
No existing script invokes `subprocess` in this repo. Use the canonical safe form per D-06:
```python
subprocess.run(
    ["pngquant", "--quality=65-90", "--strip", "--force", "--output", str(path), str(path)],
    check=True,
)
```
- List form (not shell string) — avoids quoting issues.
- `check=True` — non-zero pngquant exit propagates as `CalledProcessError` (loud failure, matches "fail loudly" convention).
- `--strip` per CONTEXT.md `<decisions> > Claude's Discretion` — strip metadata is sensible default.
- The PATH lookup is done once up front via `shutil.which("pngquant")` so the failure message can be friendly (D-07).

### Stdout summary printing
**Source:** `scripts/transform_climbing_csv.py` lines 83-89
**Apply to:** `scripts/slice_logos.py`
- Plain `print()` — no logging framework.
- Blank-line separators (`print(f"\nOutput: {OUTPUT}")`) for visual grouping.
- Final line is the most useful artifact (output path / size summary).
- For `slice_logos.py`, the hex values printed at the top of the summary are a Phase 4 contract — keep their format stable: `Top-row (dark) bg fill:    #RRGGBB` and `Bottom-row (light) bg fill: #RRGGBB` (CONTEXT.md D-03 line 22-25).

---

## No Analog Found

None. The single code file in this phase has an exact-match analog.

The Pillow-specific operations (`Image.open`, `Image.crop`, `Image.save`, `getpixel`) and the `subprocess` invocation have no precedent in this repo, but they're library-level concerns — the surrounding script *shape* (constants → main → guard) maps cleanly onto the analog. Planner should reference Pillow docs directly for the API specifics; the script *structure* and *I/O conventions* come from `transform_climbing_csv.py`.

## Metadata

**Analog search scope:** `scripts/` (only Python directory in repo per STRUCTURE.md line 24-25). Root-level `convert_to_french_fixed.py` and `fix_data_properly.py` are untracked and were intentionally excluded — only the committed, reference-quality `scripts/transform_climbing_csv.py` is canonical per CONTEXT.md line 75 and CONVENTIONS.md line 188.
**Files scanned:** 1 (the only existing committed Python script).
**Pattern extraction date:** 2026-04-28

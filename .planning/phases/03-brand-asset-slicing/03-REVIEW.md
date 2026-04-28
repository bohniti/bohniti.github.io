---
phase: 03-brand-asset-slicing
reviewed: 2026-04-28T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - scripts/build_brand_assets.py
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-04-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Reviewed `scripts/build_brand_assets.py`, the offline brand-asset processing
script that ingests 8 controlled PNGs and emits 8 themed outputs. The script
adheres to all project conventions documented in `.planning/codebase/CONVENTIONS.md`
and `CLAUDE.md`: stdlib-first imports, snake_case, no type hints, no helper
docstrings, single-line module docstring, `pathlib.Path` for filesystem ops,
`__main__` guard, and "fail loudly via `sys.exit`" with no try/except.

Correctness is sound. The aspect-padding math, trim-to-content logic, and
size-gate enforcement all behave as intended for the documented input set,
and re-running the script over already-produced outputs is idempotent (pngquant
runs with `--force` writing to the same path).

Security surface is effectively zero: `subprocess.run` is called with a list
(no shell), and every path argument is derived from committed constants — no
untrusted input crosses any boundary.

One forward-compatibility warning (`Image.LANCZOS` is a deprecated Pillow alias)
and two minor stylistic info items. Nothing blocking for a manual-run dev
script.

## Warnings

### WR-01: Deprecated `Image.LANCZOS` alias may break on future Pillow

**File:** `scripts/build_brand_assets.py:76,124`
**Issue:** Both call sites reference `Image.LANCZOS`. Since Pillow 9.1 the
canonical spelling is `Image.Resampling.LANCZOS`; the bare `Image.LANCZOS`
is a deprecated alias that emits a `DeprecationWarning` and is slated for
removal. Because this script is run in a throwaway `/tmp/` venv that
installs Pillow fresh each time, a future `pip install Pillow` could pull
a version where this attribute no longer exists, causing the script to
fail with `AttributeError` instead of producing assets.
**Fix:**
```python
# Replace both occurrences:
return img.resize((max_w, int(round(h * ratio))), Image.LANCZOS)
img = img.resize((max_w, max_w), Image.LANCZOS)

# With the non-deprecated spelling:
return img.resize((max_w, int(round(h * ratio))), Image.Resampling.LANCZOS)
img = img.resize((max_w, max_w), Image.Resampling.LANCZOS)
```
This works on every Pillow >= 9.1 (released April 2022) and is the
documented stable API going forward.

## Info

### IN-01: Magic number `0.001` in aspect-equality check

**File:** `scripts/build_brand_assets.py:58`
**Issue:** `pad_to_aspect` uses a hardcoded epsilon of `0.001` to decide
whether the current aspect ratio already matches the target. The value is
fine in practice but appears as an unnamed literal, unlike the other
tunables (`WORDMARK_MAX_BYTES`, `DARK_BG`, etc.) which are named module
constants.
**Fix:** Promote to a module-level constant for consistency with the
rest of the file's style:
```python
ASPECT_TOLERANCE = 0.001  # treat aspects within this delta as equal

def pad_to_aspect(img, target_aspect, bg):
    w, h = img.size
    cur = w / h
    if abs(cur - target_aspect) < ASPECT_TOLERANCE:
        return img
    ...
```

### IN-02: Awkward generator-expression idiom for max aspect

**File:** `scripts/build_brand_assets.py:118`
**Issue:**
```python
target_aspect = max(w / h for (img, _) in loaded.values() for (w, h) in [img.size])
```
The trailing `for (w, h) in [img.size]` is a single-iteration unpack
trick that obscures intent. It works, but a reader has to pause to parse
it. Behavior is correct.
**Fix:** Unpack inline for clarity:
```python
target_aspect = max(img.size[0] / img.size[1] for (img, _) in loaded.values())
```
or, if you prefer the named locals:
```python
aspects = []
for (img, _) in loaded.values():
    w, h = img.size
    aspects.append(w / h)
target_aspect = max(aspects)
```

---

_Reviewed: 2026-04-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

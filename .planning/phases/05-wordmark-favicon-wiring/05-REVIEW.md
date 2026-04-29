---
phase: 05-wordmark-favicon-wiring
reviewed: 2026-04-29T12:13:58Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - scripts/build_brand_assets.py
  - themes/minimal/layouts/_default/baseof.html
  - themes/minimal/layouts/partials/favicon.html
  - themes/minimal/layouts/partials/header.html
  - themes/minimal/static/css/style.css
findings:
  critical: 0
  warning: 2
  info: 4
  total: 6
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-04-29T12:13:58Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Phase 05 wires the wordmark into the header (two `<img>` tags swapped via `[data-theme]`), adds a `favicon.html` partial included from `baseof.html`, and extends `scripts/build_brand_assets.py` with three favicon-asset builders (.ico, apple-touch-icon, PNG-wrapped SVG). The wiring is small, idiomatic Hugo, and the Python additions follow the existing style of the script.

The review surfaced no critical issues. Two warnings concern behavior when JavaScript is disabled or fails to run before paint: (1) the wordmark theme-swap relies on the bootstrap IIFE setting `data-theme` on `<html>`, and the CSS rules use `html[data-theme="…"]` selectors, so with JS off **both** wordmarks render stacked rather than one being hidden; and (2) the header layout uses `align-items: baseline` for a row that now mixes replaced images (wordmark) with text nav links, which can produce a subtle baseline-vs-bottom-edge mismatch. Info items cover small Python hygiene (PIL file handles not closed, an empty catch without a clarifying comment) and a minor dead-CSS-rule observation.

## Warnings

### WR-01: No-JS fallback renders both wordmarks stacked

**File:** `themes/minimal/static/css/style.css:131-132` (in conjunction with `themes/minimal/layouts/partials/header.html:4-5` and `themes/minimal/layouts/_default/baseof.html:11-23`)
**Issue:** The wordmark hide rules are scoped to `html[data-theme="light"]` and `html[data-theme="dark"]`. The `data-theme` attribute is set by the inline IIFE in `baseof.html`. If JavaScript is disabled, blocked, or throws before the IIFE assigns `document.documentElement.dataset.theme`, **neither** selector matches, so both `.wordmark-light` and `.wordmark-dark` render and stack vertically inside `.site-title a`. Screen readers also see two identical `alt="Timo Bohnstedt"` images instead of one (the comment at line 124 says hidden variants are removed from the a11y tree, which is only true when one is actually `display: none`).

This is a regression vs. the prior text-only `.site-title a` rendering, which had no JS dependency.

**Fix:** Default to one variant being hidden in CSS without requiring `data-theme`, and let the dark theme override it. Two equivalent options:

```css
/* Option A: light is the no-JS default; dark overrides */
.wordmark-dark { display: none; }
html[data-theme="dark"] .wordmark-dark  { display: block; }
html[data-theme="dark"] .wordmark-light { display: none; }
```

```css
/* Option B: use prefers-color-scheme as the no-JS fallback */
.wordmark-dark { display: none; }
@media (prefers-color-scheme: dark) {
  .wordmark-light { display: none; }
  .wordmark-dark  { display: block; }
}
html[data-theme="light"] .wordmark-dark  { display: none; }
html[data-theme="light"] .wordmark-light { display: block; }
html[data-theme="dark"]  .wordmark-light { display: none; }
html[data-theme="dark"]  .wordmark-dark  { display: block; }
```

Option B aligns the no-JS behavior with the OS preference (consistent with the SVG favicon, which already uses `prefers-color-scheme`). Either option also fixes the duplicate-alt-text issue in the a11y tree.

### WR-02: `align-items: baseline` on a row mixing images and text

**File:** `themes/minimal/static/css/style.css:69` (interacts with `themes/minimal/layouts/partials/header.html:4-5`)
**Issue:** `.site-header` has `align-items: baseline`. Replaced elements like `<img>` have no inherent text baseline; per CSS the baseline of a replaced element is its bottom margin edge. With the previous text-only `.site-title a`, baseline alignment lined up nicely with nav links. Now the wordmark's bottom edge sits on the same line as the nav links' text baseline, which typically pushes the wordmark a few pixels too low and the nav text appears to float relative to the logo's optical center.

**Fix:** Switch to `center` alignment for the header row, which is the conventional choice when mixing logo images with nav text:

```css
.site-header {
  display: flex;
  justify-content: space-between;
  align-items: center;   /* was: baseline */
  margin-bottom: 3rem;
  padding-bottom: 1rem;
}
```

If you want to preserve baseline alignment of the nav items themselves (e.g., should you later add vertically-different nav typography), keep `align-items: center` on the header and add `align-items: baseline` to `.site-nav`.

## Info

### IN-01: PIL `Image.open()` calls not closed

**File:** `scripts/build_brand_assets.py:90, 96, 148, 171`
**Issue:** Several `Image.open(...)` calls are not wrapped in a context manager and don't call `.close()`. PIL holds the underlying file handle open until the image is loaded or closed; for a one-shot build script this is harmless, but it's worth normalizing for hygiene and to silence ResourceWarning under `python -W error`.
**Fix:** Use `with Image.open(...) as img:` or assign and call `.close()`:

```python
def build_favicon_ico(source_png_path, out_path):
    with Image.open(source_png_path) as img:
        img.convert("RGB").save(out_path, format="ICO", sizes=ICO_SIZES)
```

Apply the same pattern at lines 96, 148, and 171.

### IN-02: Empty `catch` block without explanatory comment

**File:** `themes/minimal/layouts/_default/baseof.html:15`
**Issue:** `try { theme = localStorage.getItem('theme'); } catch (_) {}` swallows errors silently. The matching empty catch on line 52 has the inline comment `/* Safari private mode */` explaining the rationale. The line-15 catch should match for consistency, since a future reader will otherwise wonder whether the silence is intentional.
**Fix:** Add the same explanatory comment:

```js
try { theme = localStorage.getItem('theme'); } catch (_) { /* Safari private mode */ }
```

### IN-03: `.site-title a` text-only typography rules now mostly inert

**File:** `themes/minimal/static/css/style.css:74-83`
**Issue:** `.site-title a { font-size: 1.1rem; font-weight: 600; … }` and `.site-title a:hover { color: var(--accent); }` were written for the text wordmark. With the link's content now being two `<img>` tags, the typography properties only affect alt-text fallback, and the `:hover` color change is invisible (images don't pick up `color`). Not a bug, but the rules are misleading to read.
**Fix:** Either remove the now-inert properties or replace with an image-appropriate hover affordance, e.g. an opacity dip:

```css
.site-title a { display: inline-block; line-height: 0; text-decoration: none; }
.site-title a:hover { opacity: 0.85; }
```

(`line-height: 0` removes the descender gap that block images inside an inline anchor sometimes produce.)

### IN-04: Hardcoded wordmark dimensions duplicated across HTML and CSS

**File:** `themes/minimal/layouts/partials/header.html:4-5` and `themes/minimal/static/css/style.css:127-128, 326`
**Issue:** Width/height `200`/`117` appears as `<img>` attributes (desktop) and as CSS `width`/`height` (desktop), and `160`/`93` appears in the `@media (max-width: 600px)` rule. The desktop CSS dimensions duplicate the HTML attributes, and the mobile override silently drifts the aspect ratio: 200/117 ≈ 1.7094 vs. 160/93 ≈ 1.7204 — close enough that CLS is negligible, but it's a small inconsistency. The HTML `width`/`height` attributes are what the browser uses to reserve aspect-ratio space before CSS loads, so they should match the natural aspect of the source PNG.
**Fix:** Either drop the desktop `width`/`height` from `.wordmark` (let the HTML attributes drive intrinsic sizing) and use only `max-width` / `height: auto` for the responsive cap, or recompute the mobile dimensions to preserve the exact 200:117 ratio (200/117 × 160 ≈ 93.6 → use `width: 160px; height: auto;`):

```css
.wordmark { display: block; width: 200px; height: auto; }

@media (max-width: 600px) {
  .wordmark { width: 160px; }   /* height: auto preserves aspect ratio */
}
```

This also lets the browser use the HTML `width`/`height` attributes purely for aspect-ratio reservation, which is their intended modern role.

---

_Reviewed: 2026-04-29T12:13:58Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

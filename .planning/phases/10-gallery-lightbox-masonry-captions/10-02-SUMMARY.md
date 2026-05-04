---
phase: 10-gallery-lightbox-masonry-captions
plan: 02
subsystem: gallery-template-css-ci
tags:
  - hugo
  - css
  - masonry
  - dialog
  - exif
  - ci
  - gallery
dependency_graph:
  requires:
    - "Plan 10-01 frontmatter — Params.weight / Params.alt on every [[resources]] entry"
    - content/gallery/photos/*.{jpg,JPG,jpeg,JPEG}
  provides:
    - "Weight-sorted gallery iteration (sort .Resources.Match \"photos/*\" \"Params.weight\" \"asc\")"
    - "data-caption + data-alt DOM contract on every <a class=\"gallery-item\"> for Plan 10-03 to read"
    - "Single <dialog id=\"gallery-lightbox\"> markup with three Lucide-style 24×24 buttons + img + figcaption"
    - "Page-scoped <script src=\"js/lightbox.js\" defer></script> hook (target file ships in Plan 10-03)"
    - "column-count masonry CSS (3 cols ≥900px / 2 at 600–900px / 1 <600px) replacing v2.0 uniform CSS-Grid"
    - "Backdrop fallback + @supports (backdrop-filter: blur(12px)) progressive enhancement"
    - "Lightbox button visual rules mirroring Phase 8 .theme-toggle precedent (44×44 hit, button reset, focus-visible, hover)"
    - "Caption typography rule (UI-SPEC Gate 5)"
    - "Lightbox image sizing rule (D-25: max-height calc(100vh - 8rem); object-fit: contain)"
    - "EXIF CI gate (deploy.yml step) failing build on GPSLatitude|GPSLongitude|Make|Model|SerialNumber"
  affects:
    - .planning/phases/10-gallery-lightbox-masonry-captions/10-03-PLAN.md (lightbox.js reads dialog id, data-caption, data-alt)
tech_stack:
  added: []
  patterns:
    - "Hugo sort COLLECTION KEY ORDER over .Resources.Match (D-04)"
    - "Hugo image.Process Resize <W>x webp q<N> width-only directive for masonry (D-05)"
    - "Native <dialog> + ::backdrop CSS skeleton with @supports progressive enhancement (D-08, D-12, D-13)"
    - "CSS column-count masonry with break-inside: avoid (D-07)"
    - "body.page-gallery scoping prefix on every new lightbox/masonry rule (D-21, Pitfall 17)"
    - "@media (prefers-reduced-motion: no-preference) wrap on every transition (D-22, Pitfall 9)"
    - "GitHub Actions step pattern: apt-get install + bash gate between Checkout and Setup Pages (D-23)"
    - "Hand-authored Lucide-style 24×24 inline SVG (X / chevron-left / chevron-right) — no package install"
key_files:
  created: []
  modified:
    - themes/minimal/layouts/gallery/single.html
    - themes/minimal/static/css/style.css
    - .github/workflows/deploy.yml
decisions:
  - "Used Hugo sort COLLECTION KEY ORDER over .Resources.Match (D-04) — sort signature works on the rebound `.` from `with .Resources.Match`, no intermediate variable needed"
  - "Bumped existing .gallery-item / .gallery-img border-radius from literal 4px to var(--radius-soft) — Phase 9 token (12px) carry-forward; matches sitewide soft-corner aesthetic without touching the CSS budget"
  - "Bumped lightbox button :focus-visible border-radius from theme-toggle's literal 2px to var(--radius-soft) — UI-SPEC Gate 4 #6 explicit allowance"
  - "Used [[:space:]]* in EXIF grep regex instead of \\s* — POSIX-portable, no YAML/bash escape ambiguity"
  - "shopt -s nullglob nocaseglob in deploy.yml step — handles mixed-case filenames (.jpg/.JPG/.jpeg/.JPEG, Pitfall 14) and avoids literal '*.jpg' string when no files match"
  - "EXIF step inserted between Checkout and Setup Pages (PATTERNS placement) — fails build BEFORE the slow Hugo build cost on regression"
  - "Hugo 0.161.1 (local) built clean despite plan target 0.157.0 (CI pin) — sort syntax + Resize directive + dialog markup all parse correctly on a newer Hugo, confirming forward compat"
metrics:
  duration_seconds: 263
  duration_human: "4m 23s"
  completed_date: 2026-05-04
  tasks_completed: 4
  tasks_total: 4
  files_changed: 3
  commits: 3
requirements_addressed:
  - GALLERY-02
  - GALLERY-04
  - GALLERY-05
  - GALLERY-08
  - GALLERY-09
---

# Phase 10 Plan 02: Template + CSS + EXIF CI Summary

**One-liner:** Atomic Wave 2 — `gallery/single.html` now sorts photos by `Params.weight`, ships width-only `Resize 600x` thumbnails with `data-caption`/`data-alt` attributes, and appends a single `<dialog id="gallery-lightbox">` plus deferred `js/lightbox.js` hook; `style.css` swaps the v2.0 CSS-Grid for column-count masonry (3/2/1 across breakpoints) and adds the full lightbox visual layer (backdrop with `@supports`, dialog shell, image sizing, caption typography, three Phase-8-precedent buttons, all transitions reduced-motion-gated); `deploy.yml` adds an exiftool CI step that fails the build on GPS/Make/Model/Serial fields.

## What Shipped

### `themes/minimal/layouts/gallery/single.html` (28 → 55 LOC)

Four surgical edits delivered in a single Write:

1. **Edit 1 (D-04 weight-sort):** `range $idx, $photo := .` → `range $idx, $photo := sort . "Params.weight" "asc"`.
2. **Edit 2 (D-05 Resize 600x):** thumb directive `"fill 600x400 Smart webp q75"` → `"Resize 600x webp q75"` (width-only); full directive `"fit 1200x1200 webp q78"` unchanged (D-06).
3. **Edit 3 (D-28 data-attrs):** `<a class="gallery-item">` gains `data-caption="{{ $photo.Params.caption }}"` and `data-alt="{{ $photo.Params.alt }}"` — all existing attrs (`href`, `aria-label`, inner `<img>` `loading`/`fetchpriority`/`decoding`/`alt=""`) preserved verbatim per D-19.
4. **Edit 4 (D-09, D-14, D-20 dialog + script):** appended single `<dialog id="gallery-lightbox" aria-label="Photo viewer">` with three buttons (close → top-right; prev/next → vertical center) wrapping hand-authored 24×24 Lucide-style inline SVGs (X, chevron-left, chevron-right), plus `<img class="gallery-lightbox-img">` and `<figcaption class="gallery-lightbox-caption">`; appended `<script src="{{ "js/lightbox.js" | absURL }}" defer></script>` page-scoped (NOT in `baseof.html`).

### `themes/minimal/static/css/style.css` (568 → 676 LOC, +108)

Three Edits:

1. **Edit 1 (gallery block rewrite, lines 311–339):** Deleted v2.0 `.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }` and the unscoped `.gallery-item` / `.gallery-img` rules. Replaced with:
   - `/* === Gallery — Masonry === */` section: `body.page-gallery .gallery-grid { column-count: 3; column-gap: 1rem; margin: 0; }` + `.gallery-item { break-inside: avoid; margin-bottom: 1rem; border-radius: var(--radius-soft); }` (D-07) + scoped `:focus-visible` and `.gallery-img` rules.
   - `/* === Gallery — Lightbox === */` section (~85 LOC): backdrop fallback `rgba(16, 15, 15, 0.85)` outside `@supports`; `@supports (backdrop-filter: blur(12px))` block adds `rgba(16, 15, 15, 0.6)` + `backdrop-filter: blur(12px)` + `-webkit-backdrop-filter: blur(12px)` (D-12, D-13); flat dialog shell using existing tokens (`var(--bg)`, `var(--text)`, `var(--border)`, `var(--radius-soft)`, no `box-shadow`); image sizing per D-25 (`max-width: 100%; max-height: calc(100vh - 8rem); object-fit: contain;` — NO `width: 100%`); caption rule per UI-SPEC Gate 5 (`0.95rem` / `1.5` line-height / `var(--text-secondary)` / `60ch` / `text-align: center`); three buttons sharing 44×44 hit target, button reset, `color: var(--text)`, hover → `var(--accent)`, `:focus-visible` → 2px accent outline + `var(--radius-soft)` (Phase 8 `.theme-toggle` precedent); `transition: color 150ms ease` wrapped in `@media (prefers-reduced-motion: no-preference)` (D-22).
2. **Edit 2 (mobile @media (max-width: 600px)):** appended `body.page-gallery .gallery-grid { column-count: 1; }` inside the existing block (alongside Phase 9's about-rules at lines 535–568).
3. **Edit 3 (NEW @media block at file end):** inserted `@media (min-width: 600px) and (max-width: 899px) { body.page-gallery .gallery-grid { column-count: 2; } }` for tablet sizes.

### `.github/workflows/deploy.yml` (55 → 74 LOC, +19)

One Edit: inserted a new `Verify EXIF scrub (gallery)` step between `Checkout` and `Setup Pages`. Step:
- `sudo apt-get install -y libimage-exiftool-perl`
- `shopt -s nullglob nocaseglob` then `photos=(content/gallery/photos/*.jpg content/gallery/photos/*.jpeg)` → handles mixed casing (.jpg/.JPG/.jpeg/.JPEG, Pitfall 14)
- Empty-array guard fails fast with `::error::` if photos directory is empty
- `exiftool "${photos[@]}" 2>/dev/null | grep -E "^(GPSLatitude|GPSLongitude|Make|Model|SerialNumber)[[:space:]]*:"` → exit 1 with `::error::` annotation if any match
- Success path echoes audit-trail line with photo count

D-23 layer 1 (Hugo `[imaging.exif] disableLatLong` in `hugo.toml`) is untouched — defense in depth.

## Decisions Implemented

| Decision | Description | Where |
|---|---|---|
| D-04 | Sort photos by `Params.weight` ascending | `gallery/single.html:9` |
| D-05 | Width-only `Resize 600x webp q75` thumb (no crop) | `gallery/single.html:10` |
| D-06 | `fit 1200x1200 webp q78` full (unchanged from v2.0) | `gallery/single.html:11` |
| D-07 | column-count masonry 3/2/1 across breakpoints | `style.css` (Masonry section + 2 @media blocks) |
| D-09 | Single `<dialog>` mutated in place per click | `gallery/single.html:32` |
| D-12 | Backdrop fallback ALWAYS shipped + `@supports` blur enhancement | `style.css` Lightbox section |
| D-13 | Theme-invariant rgba backdrop (no `:root[data-theme="dark"]` override) | `style.css` Lightbox section |
| D-14 | Page-scoped `<script src="js/lightbox.js" defer>` (NOT in `baseof.html`) | `gallery/single.html:53` |
| D-19 | Semantic `<a class="gallery-item" href="…">` wrapper preserved (Pitfall 7 progressive enhancement) | `gallery/single.html:12-17` |
| D-20 | Dialog DOM order: close button, prev button, img, figcaption, next button | `gallery/single.html:32-49` |
| D-21 | All new lightbox/masonry CSS prefixed `body.page-gallery` (27 occurrences) | `style.css` Masonry + Lightbox sections |
| D-22 | All transitions wrapped in `@media (prefers-reduced-motion: no-preference)` | `style.css` Lightbox section |
| D-23 | EXIF CI gate (defensive, layer 2; layer 1 stays in `hugo.toml`) | `deploy.yml:33-51` |
| D-24 | `<img width=… height=…>` from Hugo processed image (CLS foundation) | `gallery/single.html:19-20` |
| D-25 | `.gallery-lightbox-img { max-width: 100%; max-height: calc(100vh - 8rem); object-fit: contain; }` (no `width: 100%`) | `style.css` Lightbox section |
| D-28 | `data-caption` + `data-alt` added; all v2.0 attrs preserved verbatim | `gallery/single.html:14-22` |

## Requirements Addressed

| Requirement | Description | Status |
| --- | --- | --- |
| GALLERY-02 | Masonry layout (no uniform grid; preserved aspect ratios) | Complete — column-count 3/2/1 across breakpoints; width-only Resize 600x produces variable-height thumbs |
| GALLERY-04 | Caption optionality (graceful empty rendering at template layer) | Foundation — `data-caption=""` ships empty when `$photo.Params.caption` is unset; figcaption is mutated by Plan 03 lightbox.js with the empty-string contract enforced there |
| GALLERY-05 | Native `<dialog>` lightbox with blurred backdrop | Markup + CSS complete — JS arrives in Plan 03 |
| GALLERY-08 | CLS < 0.1 (intrinsic width/height attrs on every img) | Template foundation in place; Lighthouse measurement is HUMAN-UAT in Plan 03 |
| GALLERY-09 | EXIF CI gate enforced on every build | Complete — `Verify EXIF scrub (gallery)` step ships with this commit |

## Verification

### Task-level grep gates

| Task | Gates | Result |
|---|---|---|
| Task 1 (gallery/single.html) | 12 distinct grep gates (sort, Resize 600x, no fill 600x400, fit 1200x1200, data-caption, data-alt, dialog id, all 5 button/img/caption classes, 3 button aria-labels, 3× viewBox/aria-hidden/stroke=currentColor, no Unicode glyphs, defer script tag, all 4 preserved v2.0 attrs, alt="") | ALL PASS |
| Task 2 (style.css) | 18 distinct grep gates (no display:grid, column-count 3/2/1, column-gap, tablet @media, break-inside, fallback rgba, @supports + 3 inner properties, no `data-theme*::backdrop`, no box-shadow on dialog, calc(100vh-8rem) + object-fit:contain, no width:100% on lightbox-img, 4 caption properties, 3 button hit-target, 2 button-reset, button hover, prefers-reduced-motion + transition:color 150ms, 5 forbidden generic-class checks, 5 body.page-gallery scope checks, both section comments) | ALL PASS |
| Task 3 (deploy.yml) | 7 grep gates (file exists, step name, exiftool + libimage-exiftool-perl, forbidden fields list, line-order Checkout < EXIF < Setup, build-step preserved, nocaseglob) + Python yaml.safe_load parse | ALL PASS |
| Task 4 (Hugo build) | hugo --minify --gc --cleanDestinationDir + 4 rendered-HTML greps + width-only thumb height variation | ALL PASS — 6 distinct heights across 18 photos confirms masonry layout |

### Plan-level audits

- **CSS scope audit:** `grep -E '^\.(lightbox|modal|close|prev|next)\b'` returns 0 matches — no leakage into other pages.
- **Markup contract for Plan 03:** dialog id, data-caption, data-alt, lightbox.js script tag all confirmed in `gallery/single.html`.
- **Decision-coverage spot-check:** all 16 in-scope decisions (D-04, D-05, D-06, D-07, D-09, D-12, D-13, D-14, D-19, D-20, D-21, D-22, D-23, D-24, D-25, D-28) verifiably implemented.
- **Hugo 0.161.1 build (local):** 16 pages, 13 non-page files, 11 static files, 46 processed images, 14097 ms. Only pre-existing `languageCode` deprecation warnings — unrelated to this plan (carry-forward from Plan 10-01).
- **Rendered output:** `public/gallery/index.html` ships `<dialog id=gallery-lightbox …>` (Hugo minifier dropped quotes — HTML5-valid); 18 `<a class="gallery-item">` blocks with `data-alt="…"` populated and `data-caption` empty (per Plan 01 — captions deferred to author iteration); thumbnail dimensions vary by aspect ratio (e.g., `width=600 height=800`, `width=600 height=450`, `width=600 height=338`, `width=600 height=1067`) — masonry working.
- **First photo in DOM order:** `IMG_8113.jpg` (weight=10, lowest) — sort by weight ascending verified at the rendered-HTML layer.
- **Hugo 0.161.1 vs CI-pinned 0.157.0:** local build uses a newer Hugo than the deploy pin; sort syntax + Resize directive + dialog markup all parse on the newer version, confirming forward compat. The CI build on next push will run 0.157.0.

## Deviations from Plan

None — plan executed exactly as written. The four edits across three files matched their authored verbatim shapes; all 37+ grep gates passed on first run; Hugo build was clean. The `data-caption=""` minification quirk (Hugo dropping `=""` from empty boolean attributes) was a tooling observation during verification, not a deviation — the attribute IS present on all 18 anchors and Plan 03's `a.dataset.caption` API will read empty string correctly.

## Out-of-Scope / Deferred

- **`themes/minimal/static/js/lightbox.js`** — NEW file with ~80 LOC IIFE; ships in Plan 10-03. This plan emits the DOM contract (dialog id, data-attrs, script-tag hook) the JS will read.
- **HUMAN-UAT for Lighthouse CLS < 0.1, real-device backdrop blur perf, dual-theme dialog visual** — deferred to post-Plan-03 walkthrough per CONTEXT D-26 wave 5.
- **Caption text authoring** — still deferred from Plan 10-01; author iterates after viewing rendered photos in context. Plan 03 figcaption-empty handling closes the graceful-empty contract for REQ GALLERY-04 at the JS layer.
- **Pre-existing `languageCode` deprecation warnings** — surface during `hugo --minify`; originate in `hugo.toml`, not this plan's files. Carry-forward from Plan 10-01 deferred items.
- **Apt-package caching for the EXIF step** — D-23 acknowledges ~10s install cost; defer until measured pain (T-10-09 accepted threat).

## Threat Flags

None — no new security-relevant surface beyond the modeled threats T-10-06..T-10-13. The new EXIF CI step ITSELF is a mitigation (T-10-08 disposition: mitigate); the apt-install cost is an accepted DoS risk (T-10-09: accept). No new endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Self-Check: PASSED

**Files claimed to exist (3 modified):**
- `themes/minimal/layouts/gallery/single.html` — FOUND (29 insertions, 2 deletions; 4 surgical edits per plan)
- `themes/minimal/static/css/style.css` — FOUND (117 insertions, 9 deletions; 568 → 676 LOC; both new section comments present)
- `.github/workflows/deploy.yml` — FOUND (19 insertions; new `Verify EXIF scrub (gallery)` step between Checkout and Setup Pages)

**Commits claimed to exist:**
- `a45495f` `feat(10-02): rewrite gallery template — sort by weight, Resize 600x, data-attrs, dialog markup` — FOUND
- `f55dd36` `feat(10-02): rewrite gallery CSS — column-count masonry, lightbox dialog, backdrop @supports` — FOUND
- `f6515cc` `feat(10-02): add EXIF CI gate — Verify EXIF scrub step in deploy.yml` — FOUND

**Build sanity:**
- `hugo --minify --gc --cleanDestinationDir` exited 0; 16 pages built; rendered `public/gallery/index.html` contains the dialog id, both data-attrs, the lightbox.js script reference, and 18 weight-sorted gallery-item anchors with variable-height thumbnails.

## Next Plan

**Plan 10-03** (`10-03-PLAN.md`) — Lightbox JS + Verification + HUMAN-UAT. Authors `themes/minimal/static/js/lightbox.js` (~80 LOC IIFE per D-15) reading the dialog id, data-caption, and data-alt this plan emits. Implements showModal() bind, ←/→ keyboard nav, touch swipe (50px deltaX, D-18), focus trap (native via `<dialog>`), body scroll lock (D-11), aria-label per nav (D-17), backdrop click close (D-10). Then runs the post-deploy HUMAN-UAT script for Lighthouse CLS < 0.1, real-device backdrop blur perf, dual-theme dialog visual.

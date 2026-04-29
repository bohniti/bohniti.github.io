---
phase: 05-wordmark-favicon-wiring
verified: 2026-04-29T15:00:00Z
status: human_needed
score: 7/8 must-haves verified
overrides_applied: 0
human_verification:
  - test: "With light theme active, confirm only the wordmark-light image renders in the header — wordmark rectangle sits flush against --bg (#FFFCF0) with no visible lightness band framing the PNG seam"
    expected: "Only the script 'time BOHNSTEDT' light logo visible; dark logo hidden; no seam artifact around the PNG"
    why_human: "Seam-masking background (#FEFEFE on .wordmark-light) correctness requires eyeballing on a real render — automated CSS checks confirm the rules exist but cannot confirm the pixel-level seam match"
  - test: "Click the theme toggle to switch to dark mode; verify only the wordmark-dark image renders; toggle back to light; confirm instant swap with no logo flicker or FOUC"
    expected: "Wordmark variants swap instantly on toggle; dark logo visible in dark mode; light logo visible in light mode; no flash or layout shift"
    why_human: "FOUC (Flash of Unstyled Content) and logo flicker are rendering behaviors that require a browser and a screen recording to verify"
  - test: "Run Lighthouse Mobile against / after deploy and confirm CLS < 0.1"
    expected: "Cumulative Layout Shift score below 0.1 — structurally guaranteed by explicit width/height attrs but must be measured post-deploy"
    why_human: "Lighthouse is an external tool requiring a live deploy and browser automation"
  - test: "After deploy: open a browser tab on /, bookmark the page, and add to iOS home screen ('Add to Home Screen'). Verify all three show the TB mark — not a generic Hugo or browser default favicon"
    expected: "Chrome/Firefox/Safari tab favicon shows TB mark; bookmark icon shows TB mark; iOS home-screen icon shows 180x180 TB mark"
    why_human: "Favicon rendering in browser UI chrome (tabs, bookmarks, iOS home screen) cannot be verified by static file analysis — requires a live deploy and manual visual check"
---

# Phase 5: Wordmark + Favicon Wiring Verification Report

**Phase Goal:** Every page renders the script "time BOHNSTEDT" wordmark in place of plain text site title, swapping cleanly with the active theme; browser tabs, bookmarks, and iOS home-screens show a real favicon set sourced from the same brand assets
**Verified:** 2026-04-29T15:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Site header replaces {{ .Site.Title }} text with two `<img>` tags toggled by `[data-theme]` CSS selectors, both carrying explicit `width`/`height` and meaningful `alt` | VERIFIED | `header.html` lines 4-5: both `<img class="wordmark wordmark-light">` and `<img class="wordmark wordmark-dark">` present; `alt="Timo Bohnstedt"` on both (count=2); `width="200" height="117"` on both (count=2); `{{ .Site.Title }}` absent (count=0); anchor wrapper preserved |
| 2 | Wordmark CSS swap keyed off `html[data-theme]` with no JS swap and no `<picture>` element | VERIFIED | `style.css` lines 131-132: `html[data-theme="light"] .wordmark-dark { display: none; }` and `html[data-theme="dark"] .wordmark-light { display: none; }` — pure CSS, no JS; `<picture>` count=0 in header.html |
| 3 | Per-variant seam-masking bg (`#FEFEFE` / `#000000`) applied via class — Phase 4 D-02 hard cross-phase contract honored | VERIFIED | `style.css` lines 136-137: `.wordmark-light { background: #FEFEFE; }` and `.wordmark-dark { background: #000000; }` — hardcoded hex, not `var(--bg)` |
| 4 | Mobile wordmark size override at 160x93 inside `@media (max-width: 600px)` | VERIFIED | `style.css` line 326: `.wordmark { width: 160px; height: 93px; }` confirmed inside the `@media (max-width: 600px)` block (awk check returned 1) |
| 5 | `themes/minimal/layouts/partials/favicon.html` exists with exactly 3 `<link>` tags in SVG → ICO → apple-touch order, all using `absURL` pipe | VERIFIED | File exists (3 lines, 3 `<link>` tags); line 1: `rel="icon" type="image/svg+xml"`; line 2: `rel="icon" type="image/x-icon"`; line 3: `rel="apple-touch-icon"`; all 3 use `absURL` pipe; no 4th link, no mstile/manifest |
| 6 | `{{ partial "favicon.html" . }}` inserted in `baseof.html` between `<title>` (line 8) and `<meta name="description">` (line 10) — file is 58 lines | VERIFIED | `baseof.html` line 8 = `<title>…`; line 9 = `{{ partial "favicon.html" . }}`; line 10 = `<meta name="description"…`; total line count = 58; Phase 4 IIFE intact; stylesheet link intact |
| 7 | Three favicon files physically exist at `themes/minimal/static/`: `favicon.ico` (5413 bytes), `favicon.svg` (77001 bytes, prefers-color-scheme dark, viewBox 512x512, 2 base64 image elements), `apple-touch-icon.png` (5026 bytes) | VERIFIED | All 3 files confirmed: `favicon.ico` 5413 B; `favicon.svg` 77001 B with `prefers-color-scheme: dark` (1 match), `data:image/png;base64,` (1 match — single concatenated SVG line), `viewBox="0 0 512 512"` (1 match); `apple-touch-icon.png` 5026 B |
| 8 | After deploy, browser tab, bookmark, and iOS home-screen show the TB mark (not generic Hugo/browser default) | NEEDS HUMAN | Static analysis can confirm the `<link>` tags are wired and the files exist — actual browser rendering of favicon in tab/bookmark/iOS requires a live deploy and visual check |

**Score:** 7/8 truths verified

### Deferred Items

None — all truths within this phase's scope. Post-deploy visual confirmation (truth 8) is human-verified, not deferred to a later phase.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `themes/minimal/layouts/partials/header.html` | Two wordmark `<img>` tags inside `<a href="{{ .Site.BaseURL }}">`, no `{{ .Site.Title }}` text | VERIFIED | Exactly as specified: wordmark-light and wordmark-dark `<img>` tags, both with `alt="Timo Bohnstedt"` and `width="200" height="117"`, inside anchor |
| `themes/minimal/static/css/style.css` | `.wordmark` base rule (200x117), `html[data-theme]` swap rules, seam-mask bg rules, mobile 160x93 override in `@media` block | VERIFIED | All 6 CSS rules confirmed present and correctly valued; mobile override confirmed inside `@media (max-width: 600px)`; existing Phase 4 `:root[data-theme="dark"]` block untouched; `.site-title a` typography preserved |
| `themes/minimal/layouts/partials/favicon.html` | Exactly 3 `<link>` tags (SVG/ICO/apple-touch), all `absURL`, no wrappers | VERIFIED | 3-line file, 3 `<link>` tags, 3 `absURL` usages, 0 template wrappers, 0 mstile/manifest/mask-icon references |
| `themes/minimal/layouts/_default/baseof.html` | Single `{{ partial "favicon.html" . }}` between `<title>` and `<meta name="description">` | VERIFIED | Partial include on line 9; `<title>` on line 8; `<meta name="description">` on line 10; file = 58 lines (was 57 +1) |
| `themes/minimal/static/favicon.ico` | Multi-size .ico (16/32/48) at theme static root | VERIFIED | File exists, 5413 bytes; generated by `build_favicon_ico` with `sizes=ICO_SIZES` |
| `themes/minimal/static/favicon.svg` | PNG-wrapped SVG with `prefers-color-scheme: dark` @media, two base64 `<image>` elements, viewBox 512x512 | VERIFIED | 77001 bytes; `prefers-color-scheme: dark` present; `data:image/png;base64,` present; `viewBox="0 0 512 512"` present |
| `themes/minimal/static/apple-touch-icon.png` | 180x180 PNG at theme static root | VERIFIED | File exists, 5026 bytes; generated by `build_apple_touch` with LANCZOS resize to 180x180 |
| `scripts/build_brand_assets.py` | `import base64`, 3 new constants, 3 new helper functions, wire-in in `main()`, existing 8-PNG stage and BRAND-03 gate intact | VERIFIED | Syntax valid; `import base64` (1 match); `THEME_STATIC_DIR`, `APPLE_TOUCH_SIZE = 180`, `ICO_SIZES` (1 each); `build_favicon_ico`, `build_apple_touch`, `build_favicon_svg` (3 matches); `WORDMARK_MAX_BYTES` (3 matches — declaration + usage preserving BRAND-03 gate); existing `for asset, max_w, square in ASSETS` loop (1 match) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `partials/header.html` | `themes/minimal/static/images/brand/logo-light.png` + `logo-dark.png` | `absURL` pipe on hardcoded relative paths | WIRED | Both files exist (26757 B / 20418 B); both `<img src>` attrs use `absURL` correctly |
| `html[data-theme="light"/"dark"]` | `.wordmark-light` / `.wordmark-dark` display:none toggle | CSS attribute selector — no JS | WIRED | Both selectors present in `style.css`; Phase 4 IIFE sets `data-theme` on `<html>` before stylesheet parse |
| `.wordmark-light` / `.wordmark-dark` | Phase 4 D-02 corner-pixel hex contract (`#FEFEFE` / `#000000`) | Hardcoded background rules — NOT theme tokens | WIRED | `.wordmark-light { background: #FEFEFE; }` and `.wordmark-dark { background: #000000; }` confirmed; no `var(--bg)` in these rules |
| `baseof.html` `<head>` (line 9) | `themes/minimal/layouts/partials/favicon.html` | `{{ partial "favicon.html" . }}` dot-context include | WIRED | Include present on line 9; partial file exists |
| `partials/favicon.html` | `themes/minimal/static/{favicon.svg,favicon.ico,apple-touch-icon.png}` | Hugo serves theme static root at site root; `absURL` resolves to `/favicon.*` | WIRED | All 3 static files exist at `themes/minimal/static/`; Hugo's static serving means they'll be at site root |

### Data-Flow Trace (Level 4)

Not applicable — this phase produces static templates, CSS rules, and pre-built binary/SVG assets. No dynamic data flows (no API, no state management, no fetch calls). The wordmark images are loaded by the browser directly from the static file server via the `<img src>` URLs; the favicon files are referenced by `<link href>` tags. Both are static asset references, not dynamic data.

### Behavioral Spot-Checks

Hugo CLI is not available locally (confirmed by CLAUDE.md: "Hugo is NOT installed locally"). End-to-end template rendering requires a Hugo build. All spot-checks that can be done statically have been performed via grep and file inspection above.

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `header.html` renders wordmark `<img>` tags | `grep -c '<img class="wordmark'` | 2 matches | PASS |
| `{{ .Site.Title }}` removed from `header.html` | `grep -c '{{ .Site.Title }}'` | 0 matches | PASS |
| `favicon.html` partial is wired into `baseof.html` | `grep -c '{{ partial "favicon.html" . }}'` | 1 match | PASS |
| favicon.svg contains dark-mode swap logic | `grep -c 'prefers-color-scheme: dark'` | 1 match | PASS |
| Build smoke-test (Hugo minify) | `hugo --minify` | NOT RUN — Hugo not on PATH | SKIP (CI gate) |
| Browser tab favicon visible as TB mark | Visual check of deployed site | NOT RUN — requires live deploy | SKIP (human gate) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| HEAD-01 | 05-02 | Site header shows script wordmark image instead of plain text title, on every page | SATISFIED | `header.html` replaces `{{ .Site.Title }}` with two wordmark `<img>` tags inside the existing anchor; partial is included by `baseof.html` for all routes |
| HEAD-02 | 05-02 | Wordmark swaps between dark/light variants automatically with active theme, two-image CSS toggle (no FOUC, no JS) | SATISFIED | `html[data-theme="light"] .wordmark-dark { display: none; }` and `html[data-theme="dark"] .wordmark-light { display: none; }` present; no `<picture>` element; no JS swap logic |
| HEAD-03 | 05-02 | Wordmark `<img>` tags carry explicit `width`/`height` attributes and meaningful `alt` text | SATISFIED | Both `<img>` tags have `width="200" height="117"` and `alt="Timo Bohnstedt"`; mobile CSS override maintains consistent sizing; display:none removes hidden variant from a11y tree |
| HEAD-04 | 05-01, 05-03 | Browser favicon via `favicon.ico` (multi-size) + `favicon.svg` (with embedded prefers-color-scheme dark swap) + `apple-touch-icon.png` (180x180) | SATISFIED (template-level) | All 3 files exist at `themes/minimal/static/`; all 3 referenced by `favicon.html` partial; post-deploy visual check required for full closure (human verification item) |
| HEAD-05 | 05-03 | Favicon `<link>` tags consolidated in `partials/favicon.html` and included from `baseof.html` `<head>` | SATISFIED | `themes/minimal/layouts/partials/favicon.html` exists with exactly 3 `<link>` tags; included via `{{ partial "favicon.html" . }}` on `baseof.html` line 9, between `<title>` and `<meta name="description">` |

All 5 phase requirements (HEAD-01 through HEAD-05) have implementation evidence in the codebase.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | — | — | — |

No TODO/FIXME/PLACEHOLDER comments found in any of the 5 modified files. No empty implementations, no stubs, no hardcoded empty data arrays. The wordmark `<img>` tags reference real asset files that exist on disk. The favicon `<link>` tags reference real static files that exist. The CSS rules are fully specified. The Python script is syntactically valid and functionally complete.

### Human Verification Required

#### 1. Wordmark Seam-Masking Visual Check (Both Themes)

**Test:** Open the deployed site in light mode. Inspect the header wordmark area against the page background.
**Expected:** The script "time BOHNSTEDT" wordmark rectangle should sit flush against `--bg` (`#FFFCF0`) with no visible ~5-7% lightness band framing the PNG. Switch to dark mode (click the toggle) and repeat — wordmark should sit flush against `--bg` (`#100F0F`) with no seam.
**Why human:** The seam-masking background (`#FEFEFE` for light, `#000000` for dark) must visually match the PNG corner pixels. CSS rules confirm the hex values are correct, but the perceptual result (no visible band) requires a screen or render.

#### 2. Theme Toggle — Wordmark Swap with No Flicker

**Test:** Click the theme toggle button in the header. Watch for any flash, FOUC, or layout shift in the wordmark area.
**Expected:** Wordmark variant swaps instantly (CSS data-theme swap) with no flicker. The Phase 4 IIFE sets `[data-theme]` before stylesheet parse so there should be zero light-frames on a dark-mode hard reload.
**Why human:** FOUC and logo flicker are rendering behaviors that require a browser and visual inspection (ideally a screen recording at slow network to confirm the head IIFE fires before stylesheet parse).

#### 3. Lighthouse Mobile CLS < 0.1 on /

**Test:** Run Lighthouse Mobile against the deployed `/` URL.
**Expected:** Cumulative Layout Shift < 0.1. This is structurally guaranteed by the explicit `width="200" height="117"` HTML attributes on both `<img>` tags plus matching CSS dimensions — but must be confirmed post-deploy.
**Why human:** Lighthouse requires a live URL, a browser, and Google's tooling to run.

#### 4. Browser Tab / Bookmark / iOS Home-Screen Favicon

**Test:** After deploy, check: (a) browser tab on `/` — should show TB mark; (b) bookmark the page — icon should be TB mark; (c) iOS "Add to Home Screen" on `/` — icon should be 180x180 TB mark.
**Expected:** No generic Hugo feather or browser default globe in any of these contexts — the TB brand mark should appear.
**Why human:** Favicon rendering in browser UI chrome (tabs, bookmarks, iOS home screen) cannot be determined by static HTML/file analysis. The `<link>` tags are wired and the files exist, but the browser's favicon-loading and display is the final validation gate.

### Gaps Summary

No automated gaps found. All 7 programmatically verifiable must-haves pass. The one remaining item (post-deploy browser/device visual checks) is human verification, not a code gap.

The phase is structurally complete:
- `header.html` wordmark wiring: fully verified
- CSS theme-swap rules: fully verified
- `favicon.html` partial: fully verified
- `baseof.html` wiring: fully verified
- All 3 favicon static files: exist and have correct content structure
- `build_brand_assets.py` extension: syntactically valid with all 3 helper functions wired

The only open items are post-deploy visual confirmations that require a live browser.

---

_Verified: 2026-04-29T15:00:00Z_
_Verifier: Claude (gsd-verifier)_

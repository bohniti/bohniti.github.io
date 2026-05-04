---
phase: 08-icon-svg-theme-toggle
plan: 01
subsystem: ui
tags: [hugo, svg, css, theme-toggle, accessibility, lucide, flexoki]

# Dependency graph
requires:
  - phase: 04-theme-toggle
    provides: ".theme-toggle button + head IIFE that sets documentElement.dataset.theme before stylesheet load (no-FOUC bootstrap)"
  - phase: 05.1-wordmark-inline-svg
    provides: "currentColor + var(--text) inline-SVG recoloring pattern (.site-title svg)"
provides:
  - "Sun + moon inline SVG theme toggle button (Lucide v0.547.0 path data, hand-authored, zero deps)"
  - ".theme-toggle CSS rules: 44×44 hit target via inline-grid + min-width/min-height (WCAG 2.5.5)"
  - "[data-theme]-keyed CSS visibility swap (sun visible in light, moon visible in dark) — zero JS for icon visibility"
  - "prefers-reduced-motion-gated 150ms opacity cross-fade — instant swap for reduced-motion users"
affects: [08-02-toggle-handler-rewrite, 09-about-page, 10-gallery-lightbox]

# Tech tracking
tech-stack:
  added: []   # no new deps; Lucide path data hand-copied inline
  patterns:
    - "Sun + moon Lucide v0.547.0 inline SVG with currentColor stroke + fill=none (extends footer.html GitHub/Instagram convention)"
    - "Icon-as-current-state mapping (sun shown in light, moon shown in dark) with action-oriented aria-label on button"
    - "44×44 hit target on button shell, not via SVG padding (decouples icon size from hit area)"
    - "CSS-only icon visibility via :root[data-theme=...] selectors keyed off head IIFE — zero JS in the swap path"
    - "Defensive :root:not([data-theme=\"dark\"]) selector covers pre-IIFE first-paint edge"

key-files:
  created: []
  modified:
    - "themes/minimal/layouts/partials/header.html (line 11 → 17 lines: text 'Dark' button replaced with sun + moon SVG button)"
    - "themes/minimal/static/css/style.css (lines 101-122 → 56 lines: rewrote .theme-toggle block with 44×44 hit target, [data-theme] visibility swap, motion-gated cross-fade; preserved :hover and :focus-visible verbatim)"

key-decisions:
  - "Used inline-grid + grid-area: 1 / 1 stacking (D-05 default) — reads cleaner than position: absolute and produces equivalent visual result with no layout reflow on swap"
  - "Selected 150ms opacity transition (upper bound of ICON-05 ≤150ms cap) — matches existing body color/background-color transition timing at style.css:51-54 for visual consistency across the site"
  - "Kept type='button' attribute (D Claude's Discretion) — preserves form-edge-case safety from v2.0"
  - "Added defensive :root:not([data-theme=\"dark\"]) selector for the moon — covers the architecturally-impossible-but-cheap-to-cover case of CSS loading before head IIFE"

patterns-established:
  - "Icon-as-current-state with action-oriented aria-label — sun icon + 'Switch to dark mode' label is the GitHub-style pattern; reusable for any future toggle pair"
  - "44×44 hit target via min-width/min-height + place-items: center — decouples visual icon size from interactive hit area; reusable for any future icon-only button"
  - "CSS-only visibility swap keyed off [data-theme] — zero JS in the swap path; the head IIFE's single mutation (dataset.theme = next) cascades through palette + icon visibility + meta theme-color sync"

requirements-completed: [ICON-01, ICON-04, ICON-05]

# Metrics
duration: 5min
completed: 2026-05-02
---

# Phase 8 Plan 1: Icon SVG Theme Toggle Summary

**Replaced text 'Dark' button with sun/moon Lucide v0.547.0 inline-SVG button + 44×44 hit target + CSS-only [data-theme] visibility swap + reduced-motion-gated 150ms opacity cross-fade — zero new dependencies, zero JS in the swap path**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-02T08:23:48Z
- **Completed:** 2026-05-02T08:28:33Z
- **Tasks:** 2 (both `auto`, no TDD)
- **Files modified:** 2

## Accomplishments

- Sun + moon Lucide v0.547.0 inline SVGs land in `header.html` with verbatim path data (circle + 8 ray paths for sun; single crescent path for moon), `currentColor` stroke, `fill="none"`, `aria-hidden="true"` on both — button is the labeled control
- `.theme-toggle` button shell sized to 44×44 CSS-px via `inline-grid + place-items: center + min-width/min-height` — WCAG 2.5.5 / iOS HIG compliant without padding
- CSS-only icon visibility keyed off `:root[data-theme="dark"|"light"]` set by the existing head IIFE before the stylesheet loads — zero FOUC, zero JS in the swap path
- 150ms opacity cross-fade declared **only** inside `@media (prefers-reduced-motion: no-preference)` — reduced-motion users get an instant swap (no fallback transition)
- `:hover` and combined `:focus-visible` rules preserved verbatim from v2.0
- Hugo build smoke confirmed: `public/index.html` contains both SVGs inside `<button class=theme-toggle>` (Hugo's `--minify` strips quotes from whitespace-free attribute values; semantically identical)

## Task Commits

Each task was committed atomically on `main`:

1. **Task 1: Replace text button with sun + moon inline SVG button in header.html** — `8796589` (feat)
2. **Task 2: Rewrite .theme-toggle CSS block with icon stacking, [data-theme] visibility swap, 44×44 hit target, and reduced-motion-gated transition** — `220394b` (feat)

**Plan metadata commit:** to follow (docs: complete plan)

## Files Created/Modified

- `themes/minimal/layouts/partials/header.html` (16 insertions, 1 deletion) — line 11 text button replaced with 17-line button containing two inline SVGs
- `themes/minimal/static/css/style.css` (39 insertions, 5 deletions) — `.theme-toggle` block at lines 101-122 rewritten; `font: inherit` and `font-size: 0.95rem` removed (D-11); 44×44 hit target, icon-stacking, `[data-theme]` visibility swap, and motion-gated 150ms opacity transition added; `:hover` + combined `:focus-visible` rules preserved verbatim

## Lucide v0.547.0 Path Data — Canonical Reference

Path data is **canonical** and must not drift in future edits. Sources:

**Sun glyph** (visible in light mode):
- `<circle cx="12" cy="12" r="4"/>` (center disc)
- 8 `<path>` ray elements at 12/3/6/9/1:30/4:30/7:30/10:30 o'clock positions

**Moon glyph** (visible in dark mode):
- Single `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>` (crescent)

Both SVGs share identical wrapper attributes: `xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"`.

If updating Lucide in future, update both glyphs together; do not mix versions.

## Pitfall 3 Audit (Hard-coded Color Literals)

```bash
$ grep -E 'fill="#|stroke="#' themes/minimal/layouts/partials/header.html
# (zero matches — PASSED)
```

Stroke uses `currentColor`; CSS uses `var(--text-secondary)` (idle) and `var(--accent)` (hover). No hex literals introduced anywhere in the SVG markup or the rewritten `.theme-toggle` CSS block.

## Decisions Made

- **150ms transition timing** chosen at the upper bound of ICON-05's ≤150ms cap (vs. 100ms) to mirror the existing body `transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;` at `style.css:49-56` — visual consistency across the site (theme swaps and icon swaps both feel ~150ms).
- **`inline-grid` + `grid-area: 1 / 1` stacking** chosen over `position: absolute` (both produce identical visual result with no layout reflow). The `inline-grid` form reads cleaner in CSS and self-documents the centering via `place-items: center` (also doubles as the 44×44 hit-area centering mechanism).
- **Defensive `:root:not([data-theme="dark"])` moon selector added** — architecturally unnecessary (the head IIFE always writes `data-theme` before stylesheet load), but the selector costs nothing and covers the rare CSS-loads-before-IIFE edge case.

## Deviations from Plan

None — plan executed exactly as written. Both tasks completed cleanly on the first pass with all verification gates green:

- All 7 grep gates in Task 1 verify block: PASSED
- All 10 grep gates in Task 2 verify block: PASSED
- Pitfall 3 hex-literal audit: PASSED (zero matches)
- Hugo build smoke (`hugo --minify`): PASSED — both `class="icon-sun"` and `class="icon-moon"` present in `public/index.html` inside the theme-toggle button (minifier strips quotes from whitespace-free attribute values, which is semantically equivalent)
- Lines NOT modified are intact: `baseof.html` and `footer.html` show zero diff lines across the two task commits

## Issues Encountered

**Hugo CLI availability:** Plan noted CLAUDE.md said "Hugo is NOT installed locally," so build smoke was scoped as a soft check deferred to CI. In practice Hugo v0.161.1+extended is on PATH via Homebrew — the build smoke ran locally and passed. The CLAUDE.md stack section is stale on this point; non-blocking.

**Hugo `--minify` attribute-quote stripping:** The verification used `grep -q 'class="theme-toggle"' public/index.html` which initially returned 0 matches. Investigation showed Hugo's HTML minifier strips quotes from attribute values that contain no whitespace (`class=theme-toggle` instead of `class="theme-toggle"`). This is correct minifier behavior; the source file `header.html` correctly carries the quoted form, and the rendered HTML is semantically identical. No action needed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

**Plan 08-02 (toggle-handler-rewrite) is unblocked and ready.** Plan 02 disjoint files: it touches only `themes/minimal/layouts/_default/baseof.html` (end-of-body IIFE at lines 34-56). Plan 01 has finished its territory (header.html, style.css). The two plans were designed to run in the same wave; with Plan 01 shipped, Plan 02 can land next and complete ICON-02 (no FOUC + persistence) and ICON-03 (aria-label/aria-pressed reconciliation).

**Intermediate state until Plan 02 ships:** The existing v2.0 click handler still tries to mutate `toggle.textContent` on click. Since the button no longer contains text, this is a no-op — no functional break. The `aria-label` will be stale until reload (the new server-rendered `aria-label="Switch to dark mode"` does not get reconciled to the actual current theme). This is the documented intermediate state called out in the plan's `<done>` block; resolved by Plan 02.

**No blockers, no deferred items.**

## Self-Check: PASSED

Verified after writing this SUMMARY:

- `themes/minimal/layouts/partials/header.html` — FOUND (modified file present, contains both SVGs)
- `themes/minimal/static/css/style.css` — FOUND (modified file present, contains 44×44 + icon-stacking + visibility + motion-gated transition rules)
- Commit `8796589` (Task 1) — FOUND in `git log`
- Commit `220394b` (Task 2) — FOUND in `git log`
- `.planning/phases/08-icon-svg-theme-toggle/08-01-SUMMARY.md` — FOUND (this file)

---
*Phase: 08-icon-svg-theme-toggle*
*Completed: 2026-05-02*

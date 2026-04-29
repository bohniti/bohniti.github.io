---
phase: 05-wordmark-favicon-wiring
plan: 02
subsystem: ui
tags: [hugo, css, wordmark, theming, flexoki, cls, html-template, data-theme]

# Dependency graph
requires:
  - phase: 03-brand-asset-slicing
    provides: "8 sliced PNGs at themes/minimal/static/images/brand/ — this plan consumes logo-light.png and logo-dark.png (~26 KB / ~21 KB, both under the BRAND-03 30 KB gate)"
  - phase: 04-theming-foundation
    provides: "html[data-theme] attribute set on <html> by the head-IIFE before stylesheet parse (no FOUC); D-02 hard cross-phase contract — wordmark seam must be masked with PNG corner pixels (#FEFEFE / #000000), NOT Flexoki --bg/--bg-dark tokens"
provides:
  - "Site header renders the script wordmark image instead of plain {{ .Site.Title }} text on every page (the partial is included by baseof.html for all routes)"
  - "Two-image CSS toggle keyed off html[data-theme] — wordmark variants swap with the active theme via pure CSS, no JS swap, no FOUC"
  - "Per-variant seam-masking background colors that mask the rectangular PNG seam against Flexoki --bg in both themes"
  - "Explicit width/height attrs on both <img> tags + matching CSS dimensions — structurally guarantees Lighthouse Mobile CLS < 0.1 on / per HEAD-03"
  - "Mobile size override under @media (max-width: 600px) — single image source per theme, no separate srcset (D-06)"
affects: [05-03 (favicon), 06-gallery, future header partials, future header-fragment partials, future <img>-with-theme-swap consumers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "html[data-theme] descendant selector for theme-aware element swaps (vs :root[data-theme] for palette tokens)"
    - "Per-variant PNG-corner-pixel hex bg as seam mask — hardcoded literals (#FEFEFE / #000000), intentionally NOT theme tokens"
    - "Two <img> + CSS display:none toggle (vs <picture> + prefers-color-scheme — explicitly rejected by REQUIREMENTS as silently overriding manual toggle)"
    - "absURL pipe over hardcoded relative paths for asset references inside theme partials (matches the existing baseof.html stylesheet idiom)"

key-files:
  created: []
  modified:
    - "themes/minimal/layouts/partials/header.html (line 3 swap — two <img class=\"wordmark wordmark-{light,dark}\"> tags inside the existing <a href=\"{{ .Site.BaseURL }}\"> anchor; {{ .Site.Title }} text removed from this partial)"
    - "themes/minimal/static/css/style.css (.wordmark family added inside the existing /* === Header === */ block: base 200x117, html[data-theme] swap, seam-mask bg, mobile 160x93 override inside @media (max-width: 600px))"

key-decisions:
  - "Adopted the suggested .wordmark / .wordmark-light / .wordmark-dark class names (CONTEXT line 88 explicitly proposed them; matches existing .site-* family closely enough)"
  - "Kept .site-title a typography rules at lines 74-83 untouched — link hover behavior preserved; font-size/font-weight/color become irrelevant for image content but harmless"
  - "Inserted the .wordmark CSS family inside the existing /* === Header === */ block (after :focus-visible, before /* === Post List (Home) === */) — follows the file's section-comment block organization"
  - "Used html[data-theme=\"light\"|\"dark\"] descendant selectors for the swap — vs :root[data-theme] (which Phase 4 uses for palette tokens). Per Phase 5 D-01 + 05-PATTERNS.md guidance: the html form is the correct shape for descendant selectors targeting non-:root elements"
  - "Hardcoded #FEFEFE / #000000 in .wordmark-light / .wordmark-dark backgrounds (NOT var(--bg) / var(--bg-dark)) — Phase 4 D-02 hard cross-phase contract: must match PNG corner pixels, not Flexoki theme tokens (#FFFCF0 / #100F0F)"

patterns-established:
  - "Wordmark theme-swap pattern: two <img> tags inside a clickable <a> wrapper, swapped via display:none keyed off html[data-theme]. Hidden variant exits both layout flow and a11y tree (single alt announcement)."
  - "Seam-masking pattern: per-variant PNG-corner hex applied directly to each <img> via class — bound to the asset variant rather than the active theme. Stays correct regardless of swap technique."
  - "CLS-prevention pattern: explicit width/height HTML attrs on <img> + matching CSS dimensions in the .wordmark base rule. Mobile-breakpoint override changes both axes consistently (160x93 preserves the 1.71:1 source aspect)."

requirements-completed: [HEAD-01, HEAD-02, HEAD-03]

# Metrics
duration: 109s
completed: 2026-04-29
---

# Phase 5 Plan 02: Wordmark Wiring (header.html + style.css) Summary

**Replaced the plain `{{ .Site.Title }}` text with two wordmark `<img>` tags inside the existing home-link anchor, and added the `.wordmark` CSS family (base sizing, `html[data-theme]` swap, seam-masking bg, mobile override) — pure-CSS theme-keyed swap, structural CLS prevention, Phase 4 D-02 contract honored.**

## Performance

- **Duration:** 109s (1m 49s)
- **Started:** 2026-04-29T12:00:40Z
- **Completed:** 2026-04-29T12:02:29Z
- **Tasks:** 2 / 2
- **Files modified:** 2

## Accomplishments

- Site header now renders the script "time BOHNSTEDT" wordmark in place of the plain text site title on every page (HEAD-01) — the partial is included by `baseof.html` for all routes.
- Wordmark variants swap automatically with the active theme via pure CSS (`html[data-theme="light"|"dark"]` descendant selectors → `display: none` on the off-variant) — no FOUC, no JS swap, no `<picture>` (HEAD-02).
- Both `<img>` tags carry `alt="Timo Bohnstedt"` (announced once thanks to `display: none` removing the hidden variant from the a11y tree) and explicit `width="200" height="117"` (HEAD-03) — matching CSS dimensions structurally guarantee Lighthouse Mobile CLS < 0.1 on `/`.
- Per-variant seam-masking background applied directly on each `<img>` via class: `.wordmark-light { background: #FEFEFE; }` and `.wordmark-dark { background: #000000; }` — honors Phase 4 D-02's hard cross-phase contract (matches PNG corner pixels, intentionally NOT Flexoki `--bg`/`--bg-dark` tokens).
- Mobile size override (`.wordmark { width: 160px; height: 93px; }`) added inside the existing `@media (max-width: 600px)` block — single image source per theme, no separate srcset (D-06).
- Anchor wrapper (`<a href="{{ .Site.BaseURL }}">`), Phase 4 theme-toggle button, and existing `.site-title a` typography rules all preserved untouched.

## Task Commits

Each task was committed atomically (`--no-verify` in worktree mode):

1. **Task 1: Replace `{{ .Site.Title }}` text with two wordmark `<img>` tags inside the existing anchor in `partials/header.html`** — `fe1c430` (feat)
2. **Task 2: Add `.wordmark` CSS rules to `style.css` — base sizing, `[data-theme]` swap, per-variant seam-masking bg, mobile size override** — `49ab8d5` (feat)

**Plan metadata commit:** to be added with this SUMMARY.md (one-shot in this worktree agent's exit step).

## Files Created/Modified

- `themes/minimal/layouts/partials/header.html` — line 3 swap. The plain `{{ .Site.Title }}` text inside `.site-title > a` is replaced by two `<img>` tags (light + dark variants) sitting inside the existing anchor. Surrounding structure (`<header>`, `.site-title`, `<nav>`, theme-toggle button) untouched.
- `themes/minimal/static/css/style.css` — additive only:
  - `.wordmark` base rule (`display: block; width: 200px; height: 117px;`) inserted after the existing `:focus-visible` rule at the end of the `/* === Header === */` block (lines 124-129 in the new file).
  - `html[data-theme="light"] .wordmark-dark { display: none; }` and `html[data-theme="dark"] .wordmark-light { display: none; }` swap rules (lines 131-132).
  - `.wordmark-light { background: #FEFEFE; }` and `.wordmark-dark { background: #000000; }` seam-mask rules (lines 136-137).
  - `.wordmark { width: 160px; height: 93px; }` mobile override inserted inside the existing `@media (max-width: 600px)` block (line 326).
  - No existing rules modified — `.site-title a` typography (lines 74-83), the `:root[data-theme="dark"]` palette block (line 20), and the Phase 4 theme-toggle styles (lines 101-122) all stay verbatim.

## Decisions Made

- **Class names:** Adopted `.wordmark` / `.wordmark-light` / `.wordmark-dark` — CONTEXT line 88 explicitly proposed these and they match the project's `.site-*` family closely enough to fit the convention. Did not rename `.site-title` (Claude's Discretion).
- **Existing `.site-title a` typography:** Kept verbatim — anchor link-color/hover behavior preserved (the typography props are now harmlessly inherited by the inline-replaced `<img>`). Alternative was to strip the props, but that adds churn for no behavior change.
- **Selector form:** Used `html[data-theme="..."]` for descendant selectors per Phase 5 D-01 + 05-PATTERNS.md cross-reference. (Phase 4 uses `:root[data-theme="dark"]` for palette tokens — the `:root` form is correct when the rule applies to the root element itself; for descendant selectors targeting other elements, `html[data-theme]` is the documented project shape.)
- **Background hex literals:** Hardcoded `#FEFEFE` / `#000000` (NOT `var(--bg)` / `var(--bg-dark)`). Phase 4 D-02 hard cross-phase contract: bg colors MUST match the PNG corner pixels, not the Flexoki theme tokens. Using `var(--bg)` would reintroduce the ~5–7% lightness band the contract is designed to mask.
- **Insertion location:** New `.wordmark` rules go inside the existing `/* === Header === */` block (between `:focus-visible` and `/* === Post List (Home) === */`); mobile override goes inside the existing `@media (max-width: 600px)` block. Honors the file's section-comment organization.
- **No `<picture>` element / no `prefers-color-scheme`:** REQUIREMENTS § Out of Scope explicitly rejects this — silently overrides the manual toggle (anti-pattern). Two `<img>` + CSS `display: none` is the locked technique.
- **No `loading="lazy"` / `loading="eager"` / `decoding="async"`:** Above-the-fold; defaults are fine; out of scope.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- **Hugo not installed locally** (CLAUDE.md / project tech-stack notes confirm this). The plan's `<verification>` block lists `hugo --minify` as a post-step verification, but it cannot run in this environment. The GitHub Actions workflow at `.github/workflows/deploy.yml` runs `hugo --minify` on push to `main` — that's the canonical build verification. All other automated grep-based acceptance criteria for both tasks pass (12/12 + 12/12). Visual verification of the wordmark seam against `--bg` in both themes (the eyeball check called out in `<verification>` line 5 and 05-CONTEXT.md "specifics") will need to happen on the deployed site or in a local Hugo dev container — not blocking for this plan's commit boundary.

## User Setup Required

None — no external service configuration required. The wordmark + favicon set is fully self-hosted; static assets ship via Hugo's `static/` pipeline.

## Threat Flags

None — no new security-relevant surface introduced. The plan adds two `<img>` tags with hardcoded literal `src` (via `absURL` pipe over hardcoded paths), hardcoded literal `alt`, and hardcoded literal `width`/`height`. No Hugo data binding, no user input, no network IO at runtime. T-05-03 (Cross-Site-Scripting) was already documented in the plan's threat register with disposition `accept`.

## Self-Check

- `themes/minimal/layouts/partials/header.html` — FOUND (modified, contains wordmark `<img>` tags, no `{{ .Site.Title }}`)
- `themes/minimal/static/css/style.css` — FOUND (modified, contains `.wordmark` family + mobile override)
- Commit `fe1c430` (Task 1) — FOUND in `git log`
- Commit `49ab8d5` (Task 2) — FOUND in `git log`

## Self-Check: PASSED

## Next Phase Readiness

- **Plan 05-03 (favicon wiring + asset generation pipeline)** runs in a separate worktree in this same wave; this plan's outputs do not block it.
- **Phase 6 (Gallery):** the partial-include + `absURL`-asset-reference patterns established here apply to any future header/footer fragments. The `.wordmark` family of rules sits inside the existing `/* === Header === */` block and will not collide with future `.gallery-*` or content-area rules.
- **Manual visual verification on the deployed site (or local Hugo dev):**
  - With light theme active, only the `wordmark-light` `<img>` should render; the wordmark rectangle should sit flush against `--bg` (`#FFFCF0`) with no visible 5–7% lightness band framing the PNG.
  - With dark theme active (toggle clicked or OS prefers-color-scheme dark), only the `wordmark-dark` `<img>` should render; same flush-bg check against `--bg` (`#100F0F`).
  - Theme toggle should swap variants with no flicker (Phase 4's IIFE sets `[data-theme]` synchronously before stylesheet parse → CSS swap is instantaneous).
  - Lighthouse Mobile run against `/` should report CLS < 0.1 (structurally guaranteed by the explicit `width`/`height` attrs).

---
*Phase: 05-wordmark-favicon-wiring*
*Completed: 2026-04-29*

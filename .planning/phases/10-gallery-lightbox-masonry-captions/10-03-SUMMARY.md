---
phase: 10-gallery-lightbox-masonry-captions
plan: 03
subsystem: gallery
tags: [vanilla-js, dialog, lightbox, keyboard-nav, touch-swipe, iife, human-uat, gallery]

# Dependency graph
requires:
  - phase: 10-gallery-lightbox-masonry-captions
    provides: "Plan 02 — gallery template (gallery/single.html) with dialog#gallery-lightbox markup, .gallery-grid > a.gallery-item[href][data-caption][data-alt], <script src='js/lightbox.js' defer> tag; CSS .gallery-lightbox-* rules and backdrop-filter @supports block; EXIF CI gate"
  - phase: 10-gallery-lightbox-masonry-captions
    provides: "Plan 01 — content/gallery/index.md TOML resources block with 18 [[resources]] entries (params.alt required, params.caption optional, params.weight for ordering)"
provides:
  - "themes/minimal/static/js/lightbox.js — 118-line page-scoped IIFE implementing all 9 D-15 lightbox behaviors (click-to-open, arrow keys, backdrop close, touch swipe, body scroll lock) plus D-17 dynamic aria-label"
  - ".planning/phases/10-gallery-lightbox-masonry-captions/10-HUMAN-UAT.md — 6-scenario post-deploy walkthrough scaffold (CLS, focus trap, touch swipe, backdrop blur, deployed-webp EXIF, graceful empty caption)"
  - "Phase 10 implementation complete — gallery lightbox fully functional in development; deployed-site gates deferred to HUMAN-UAT walkthrough (matching Phase 5/05.1/6/7/9 exit pattern)"
affects: [post-deploy, gallery, lightbox-future-iterations, accessibility-uat]

# Tech tracking
tech-stack:
  added: []  # No new dependencies — vanilla JS only, no libraries (per CLAUDE.md and Pitfall anti-features)
  patterns:
    - "Page-scoped IIFE loaded from layout (NOT baseof.html) — keeps non-gallery pages JS-free"
    - "Native <dialog> element with showModal() — focus trap, Esc, top-layer, aria-modal all free"
    - "DOM-walk sibling navigation via Array.from(grid.children).indexOf(a) — no separate state array"
    - "Manual body-scroll-lock (save/set/restore) bound to dialog open/close events"
    - "Touch swipe with deltaX threshold + vertical no-op (D-18 50px / Math.abs(dy)>Math.abs(dx))"
    - "HUMAN-UAT scaffold pattern — gates that need real device / deployed URL deferred to post-deploy walkthrough"

key-files:
  created:
    - "themes/minimal/static/js/lightbox.js (118 LOC vanilla JS IIFE)"
    - ".planning/phases/10-gallery-lightbox-masonry-captions/10-HUMAN-UAT.md (6-scenario walkthrough scaffold)"
  modified: []

key-decisions:
  - "D-08 — dialog.showModal() (NOT show, NOT removeAttribute('hidden')); native focus trap, Esc, top-layer, aria-modal are all free affordances"
  - "D-10 — backdrop click closes via `e.target === dialog` predicate; prev/next button clicks call e.stopPropagation() to prevent bubble-to-backdrop misfire"
  - "D-11 — manual body scroll lock: `savedBodyOverflow = document.body.style.overflow` on open, `'hidden'` while open, restored verbatim on dialog `close` event"
  - "D-15 — 9 IIFE behaviors implemented: click bind preventDefault, sibling-walk index, ArrowLeft/Right keyboard, X-button click, backdrop click, touch swipe, body lock save/restore, no preload"
  - "D-16 — prev/next via DOM-walk siblings: `Array.from(grid.querySelectorAll('a.gallery-item'))` with modulo wrap (idx<0 → total-1; idx>=total → 0)"
  - "D-17 — `dialog.setAttribute('aria-label', 'Photo ' + (idx+1) + ' of ' + total)` updates on open AND each prev/next nav (NOT aria-labelledby pointing to figcaption, because figcaption may be empty per D-02)"
  - "D-18 — touch swipe: 50px deltaX threshold; `Math.abs(dy) > Math.abs(dx)` returns early (vertical swipe is no-op); positive dx → prev, negative → next"
  - "D-19 / Pitfall 7 — full image URL read via `a.getAttribute('href')`, NOT from inner `<img src>` (which is the q75 thumb, not the q78 full)"
  - "REQ GALLERY-04 / D-02 — `caption.textContent = a.dataset.caption || ''` provides graceful empty fallback for caption-less photos (no 'undefined' / null / placeholder leak)"
  - "HUMAN-UAT deferral — 6 scenarios scaffolded for post-deploy walkthrough; ships per project exit pattern (Phases 5, 05.1, 6, 7, 9 precedent)"

patterns-established:
  - "IIFE shape (verbatim analog of baseof.html theme-toggle): `(function () { 'use strict'; ... })();` with const queries, early-return guards, addEventListener (no inline onclick), no globals leaked"
  - "Single source of truth for content swaps: `showAt(idx)` sets img.src + img.alt + caption.textContent + dialog aria-label in one place; open/next/prev all route through it"
  - "Touch event passive flag: `{ passive: true }` on touchstart for scroll-perf; no preventDefault needed because body-scroll-lock already prevents page movement"
  - "HUMAN-UAT scaffold convention: each scenario has Goal / Steps / Pass criteria checklist / Failure path pointing back to specific verify gate to inspect"

requirements-completed: [GALLERY-04, GALLERY-05, GALLERY-06, GALLERY-07, GALLERY-08, GALLERY-09]

# Metrics
duration: ~25min
completed: 2026-05-04
---

# Phase 10 Plan 03: Lightbox JS + HUMAN-UAT Summary

**Atomic Wave 3 — vanilla-JS IIFE lightbox + 6-scenario post-deploy walkthrough scaffold; gallery is now fully functional in development.**

---

## What Shipped

### Files Created (2)

1. **`themes/minimal/static/js/lightbox.js`** (118 LOC, ~70 LOC of code + ~48 LOC of comments/decision-tags)
   - Page-scoped IIFE — loaded only from `layouts/gallery/single.html` via `<script src="js/lightbox.js" defer>` (D-14)
   - No globals leaked; `'use strict'`; no `var`; no `import`; no `require`; no external libraries
   - Implements all 9 D-15 behaviors plus D-17 dynamic aria-label

2. **`.planning/phases/10-gallery-lightbox-masonry-captions/10-HUMAN-UAT.md`** (171 lines)
   - 6 scenarios scaffolded for post-deploy walkthrough on `https://tbohnstedt.cloud/gallery/`
   - Each scenario has Goal, Steps, Pass criteria checklist (`- [ ]`), and Failure path pointing back to specific verify gate

### Files Modified (0)

No modifications. Both tasks created new files only. Plan 02 already shipped the dialog DOM, the script tag, and the data-attributes that this JS reads from.

---

## Decisions Implemented (Plan 03 contributions)

| Decision | Implementation in lightbox.js | Verified by gate |
|----------|-------------------------------|------------------|
| D-08 | `dialog.showModal()` — NOT show(), NOT removeAttribute('hidden') | Gate 4 |
| D-09 | Single `dialog#gallery-lightbox` mutated in place per click (loop binds 18 click handlers, all routed through `open(idx)`) | (Plan 02 markup) |
| D-10 | `if (e.target === dialog) dialog.close();` backdrop predicate | Gate 11 |
| D-11 | `savedBodyOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden';` + restore on dialog `close` event | Gate 6 |
| D-14 | IIFE `(function () { ... })();` with `'use strict'`, no globals | Gate 2 |
| D-15 | 9 behaviors — click bind preventDefault, sibling-walk index, arrow keys, X-button, backdrop click, touch swipe, body lock save+restore, no preloading | All gates |
| D-16 | `Array.from(grid.querySelectorAll('a.gallery-item'))` with modulo wrap (idx<0 → total-1; idx>=total → 0) | Gate 17 |
| D-17 | `dialog.setAttribute('aria-label', 'Photo ' + (idx + 1) + ' of ' + total);` called from `showAt()` (every open and every nav) | Gate 5 |
| D-18 | 50px deltaX threshold; `Math.abs(dy) > Math.abs(dx)` returns early on vertical | Gates 13, 14 |
| D-19 / Pitfall 7 | `img.src = a.getAttribute('href');` (NOT from inner `<img src>`) | Gate 7 |
| REQ GALLERY-04 / D-02 | `caption.textContent = a.dataset.caption || '';` graceful empty fallback | Gate 9 |

## Requirements Addressed

- **GALLERY-04** (graceful empty caption) — JS layer: `caption.textContent = a.dataset.caption \|\| ''`
- **GALLERY-05** (lightbox open/close) — `dialog.showModal()` on click, `dialog.close()` on X / Esc / backdrop
- **GALLERY-06** (keyboard nav) — ArrowLeft/Right + Esc (free via showModal); focus trap + restoration are native dialog affordances
- **GALLERY-07** (touch swipe) — touchstart + touchend with 50px deltaX threshold; vertical no-op
- **GALLERY-08** (CLS < 0.1) — Plan 02 ships explicit width/height (foundation); HUMAN-UAT Scenario 1 measures deployed CLS
- **GALLERY-09** (EXIF zero-fields) — Plan 02 ships CI gate (source files); HUMAN-UAT Scenario 5 verifies deployed `.webp` output

---

## Verification Results

### Task 1 — lightbox.js (19 grep gates)

All 19 gates pass on first run:

```
Gate 1  file & line count       — exists, lines=118 (≥70 budget)
Gate 2  IIFE shell + 'use strict' + })(); — all present
Gate 3  no var declarations     — confirmed
Gate 4  showModal not show()    — confirmed
Gate 5  setAttribute aria-label dynamic — confirmed (Photo N of M)
Gate 6  body scroll lock save+restore — confirmed
Gate 7  a.getAttribute('href') — confirmed (Pitfall 7)
Gate 8  a.dataset.alt + a.dataset.caption — confirmed
Gate 9  empty caption fallback (\|\| '') — confirmed (REQ GALLERY-04)
Gate 10 ArrowLeft + ArrowRight  — confirmed
Gate 11 backdrop e.target === dialog — confirmed
Gate 12 dialog.close()           — confirmed
Gate 13 touchstart + touchend + < 50 — confirmed
Gate 14 vertical no-op (Math.abs dy>dx) — confirmed
Gate 15 no rel="preload" / createElement('link') / .preload — confirmed
Gate 16 e.preventDefault on click — confirmed
Gate 17 Array.from               — confirmed
Gate 18 no external libs / no import / no require — confirmed
Gate 19 no aria-labelledby setAttribute — confirmed
```

### Task 2 — 10-HUMAN-UAT.md (5 grep gates)

All 5 gates pass:

```
Gate 1  file & line count       — exists, lines=171 (≥100)
Gate 2  exactly 6 ## Scenario   — confirmed (count=6)
Gate 3  GALLERY-04..09 IDs      — all 6 present
Gate 4  tbohnstedt.cloud/gallery/ deployed URL — confirmed
Gate 5  Logging Results + STATE.md ref — confirmed
```

### Hugo build

`hugo --minify --quiet` exits 0; `public/js/lightbox.js` shipped (5045 bytes after minify); `public/gallery/index.html` references the script tag correctly.

---

## Deviations from Plan

**None — plan executed exactly as written.** Both tasks delivered their verbatim file contents with no deviations, no auto-fixes (Rules 1–3 not triggered), and no architectural concerns (Rule 4 not triggered).

---

## Phase 10 Status After This Plan

**Implementation complete.** All three plans landed:

- Plan 01 (Wave 1) — frontmatter authoring (`content/gallery/index.md` TOML with 18 entries)
- Plan 02 (Wave 2) — template + CSS + EXIF CI gate (gallery/single.html, .gallery-grid masonry, dialog markup, EXIF scrub on push)
- Plan 03 (Wave 3) — **this plan** — lightbox.js IIFE + HUMAN-UAT scaffold

**Decision coverage** across all three plans: D-01 through D-28, all 28 decisions land in at least one plan.

**Requirement coverage:** all 9 GALLERY-XX requirements covered:
- GALLERY-01 → Plan 01
- GALLERY-02 → Plan 02
- GALLERY-03 → Plan 01 + Plan 02
- GALLERY-04 → Plans 01, 02, 03 (data + template + JS layers)
- GALLERY-05 → Plan 02 + Plan 03 (dialog markup + JS open/close)
- GALLERY-06 → Plan 03
- GALLERY-07 → Plan 03
- GALLERY-08 → Plan 02 (CLS foundation: explicit width/height) + HUMAN-UAT Scenario 1 (deployed measurement)
- GALLERY-09 → Plan 02 (CI gate, source files) + HUMAN-UAT Scenario 5 (deployed `.webp` output)

**HUMAN-UAT deferral pattern** matches Phases 5, 05.1, 6, 7, 9 (per STATE.md § Deferred Items). Phase ships; UAT closes asynchronously after deploy.

---

## Next Action for User

1. Push to `main` → GitHub Actions deploy → site goes live at `https://tbohnstedt.cloud/gallery/`
2. Walk through `10-HUMAN-UAT.md` checklist:
   - Run Lighthouse on deployed `/gallery/` (Scenario 1)
   - VoiceOver / NVDA test on real desktop (Scenario 2)
   - Test touch swipe on real iOS Safari + Android Chrome (Scenario 3)
   - Inspect backdrop blur in both themes (Scenario 4)
   - `curl -O` a deployed `.webp` and run `exiftool` (Scenario 5)
   - Visually confirm caption-less photos render no placeholder (Scenario 6)
3. Record results in `.planning/STATE.md` § "Deferred Items" with the documented row format

---

## Commits

- `5851925` — feat(10-03): add lightbox.js — page-scoped IIFE per D-14/D-15
- `291d0f8` — docs(10-03): scaffold 10-HUMAN-UAT.md — 6 post-deploy walkthrough scenarios

## Self-Check: PASSED

- FOUND: themes/minimal/static/js/lightbox.js
- FOUND: .planning/phases/10-gallery-lightbox-masonry-captions/10-HUMAN-UAT.md
- FOUND: .planning/phases/10-gallery-lightbox-masonry-captions/10-03-SUMMARY.md
- FOUND commit: 5851925 (feat lightbox.js)
- FOUND commit: 291d0f8 (docs HUMAN-UAT)

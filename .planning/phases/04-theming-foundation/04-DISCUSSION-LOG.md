# Phase 4: Theming Foundation - Discussion Log

**Date:** 2026-04-29
**Mode:** discuss (interactive, no `--auto`, no `--all`, no `--chain`)
**Areas selected:** Bg reconciliation, Dark palette tokens, Toggle UI, Transition behavior

This is a full audit trail of the discuss-phase Q&A. Not consumed by downstream agents — for human reference only.

---

## Phase routing

**Q:** Which phase do you want to discuss?
**Options presented:**
- Phase 4: Theming Foundation (Recommended)
- Phase 5: Wordmark + Favicon
- Phase 6: Gallery
- Phase 7: About Enrichment

**Selected:** Phase 4: Theming Foundation

---

## Gray area selection

**Q:** Which areas do you want to discuss for Phase 4: Theming Foundation? (multiSelect)
**Options presented:**
- Bg reconciliation — Phase 3 contract (#FEFEFE/#000000) vs Flexoki tones (#FFFCF0/#100F0F) for `--bg`/`--bg-dark`
- Dark palette tokens — Concrete values for all dark-mode tokens
- Toggle UI — Visual design and placement of the toggle button in the header
- Transition behavior — Instant snap, smooth color fade, or just bg fade

**Selected:** All four areas

---

## Area 1: Bg reconciliation

**Q:** How do we resolve the Phase-3-contract vs Flexoki-palette conflict for `--bg`/`--bg-dark`?
**Options presented:**
- Contained seam fix (Recommended) — Site `--bg`/`--bg-dark` stay Flexoki; Phase 5 wordmark wrapper gets a localized bg matching the PNG corner-pixel hex
- Honor Phase 3 contract — Use #FEFEFE/#000000 site-wide
- Re-export brand assets — Redo Phase 3 with Flexoki bg colors flattened in
- Defer to Phase 5 — Pick Flexoki for now, decide seam-vs-redo when Phase 5 wires the wordmark

**Selected:** Contained seam fix

**Decision recorded:** D-01, D-02 in CONTEXT.md. Site `--bg`/`--bg-dark` use Flexoki Paper/Black. Phase 3 hex contract supersedes for site-wide tokens; the seam mitigation moves to Phase 5 as a localized wordmark-wrapper bg concern. Cross-phase note recorded explicitly in `<canonical_refs>` outgoing contracts.

---

## Area 2: Dark palette tokens

**Q:** Which dark-palette mapping do you want under `:root[data-theme="dark"]`?
**Options presented:**
- Canonical Flexoki dark (Recommended) — `#100F0F` Black / `#1C1B1A` Base950 / `#CECDC3` Base200 / `#878580` Base500 / `#575653` Base700 / `#D14D41` Red400 (brighter accent on dark) / `#DA7E76` Red300 / `#282726` Base900
- Pure inversion — Flip Base values, keep `--accent: #AF3029` (Red600) in both modes
- Conservative dark — Slightly lifted bg (`#1C1B1A` instead of `#100F0F`) for less-stark feel

**Selected:** Canonical Flexoki dark (with side-by-side preview confirmed)

**Decision recorded:** D-03, D-04 in CONTEXT.md. All nine token values listed verbatim. `--max-width` stays theme-agnostic at the un-attributed `:root`.

---

## Area 3: Toggle UI

**Q1:** Visual treatment for the theme toggle button?
**Options presented:**
- Single icon swap (Recommended) — Inline SVG sun/moon, currentColor, ~16px, matching the Phase 2 footer icon style
- Both glyphs visible — Pill/segmented control with sun and moon, current side highlighted
- Text label — Plain text "Light"/"Dark" that toggles

**Selected:** Text label

**Q2:** Where in the header does the toggle sit?
**Options presented:**
- After last nav link (Recommended) — Append to `.site-nav` so it flows with the existing nav cluster
- Standalone right edge — New flex slot to the right of `.site-nav`
- Between title and nav — Floats in the middle

**Selected:** After last nav link

**Decision recorded:** D-05, D-06, D-07, D-08 in CONTEXT.md. Text label semantics = target state on click ("Dark" in light mode, "Light" in dark mode). Real `<button type="button">` with `aria-pressed`. Styling matches `.site-nav a` (font-size, color, hover) plus button reset. Stacks naturally under the existing 600px column-layout media query.

---

## Area 4: Transition behavior

**Q:** How should the theme switch animate?
**Options presented:**
- Targeted 150ms fade (Recommended) — `body` gets `transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease`, wrapped in `@media (prefers-reduced-motion: no-preference)` so reduced-motion users get an instant snap with no rule firing
- Instant snap — No transition at all
- Slower 300ms fade — Same targeted approach but slower

**Selected:** Targeted 150ms fade (with preview confirmed)

**Decision recorded:** D-09, D-10 in CONTEXT.md. The `@media (prefers-reduced-motion: no-preference)` wrapper is the structural guarantee for THEME-03's reduced-motion clause — cleaner than a `transition: none` override.

---

## Wrap-up

**Q:** We've discussed all four areas. Anything else gray, or ready for context?
**Options presented:**
- I'm ready for context (Recommended)
- Explore more gray areas

**Selected:** I'm ready for context

**Outcome:** CONTEXT.md written at `.planning/phases/04-theming-foundation/04-CONTEXT.md`. Remaining specifics (IIFE exact code shape, `localStorage` key name, `theme-color` meta hex, focus-visible cleanup) flagged as Claude's Discretion in CONTEXT.md.

---

## Decisions inventory

16 decisions captured (D-01 through D-16), spanning:
- Background palette reconciliation (D-01, D-02) — supersedes Phase 3 cross-phase contract for site-wide tokens; localizes seam fix to Phase 5
- Dark palette tokens (D-03, D-04) — canonical Flexoki dark, all 9 values listed
- Toggle button design and placement (D-05, D-06, D-07, D-08) — text label, appended to `.site-nav`, real `<button>` with `aria-pressed`
- Transition behavior (D-09, D-10) — targeted 150ms fade wrapped in `@media (prefers-reduced-motion: no-preference)`
- No-flash bootstrap (D-11) — inline IIFE in `<head>` before stylesheet
- Accessibility (D-12) — visible text content is the accessible name, no separate aria-label needed
- Storage & meta (D-13, D-14, D-15) — `localStorage` key TBD by planner, `<meta name="color-scheme">` static, `<meta name="theme-color">` dynamic
- Cross-library readability (D-16) — manual smoke test on `/blog/2026-03-05-climbing-routes/`, no inline-script changes

Cross-phase contracts:
- **Incoming (from Phase 3):** the `#FEFEFE`/`#000000` hex contract from Phase 3 deviation is **superseded** for `--bg`/`--bg-dark`
- **Outgoing (to Phase 5):** the wordmark `<img>` wrapper must set its own bg to match the PNG corner-pixel hex; the `[data-theme]` attribute lives on `<html>` for Phase 5's CSS selectors

Deferred (eight items): cross-tab `storage` sync, view-transition API cross-fade, per-library reactivity, PWA manifest, three-state toggle, cookie persistence, `<picture>` for wordmark, focus-visible nav rework.

---

*Discussion conducted: 2026-04-29*
*CONTEXT.md written: 2026-04-29*

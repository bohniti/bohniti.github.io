# Roadmap: Personal Website Refinements — v3.0 Design Update

## Milestones

- ✅ **v1.0 Targeted Refinement** — Phases 1-2 (shipped 2026-04-27)
- ✅ **v2.0 Brand & Gallery** — Phases 3-7 + 05.1 inserted (shipped 2026-05-01)
- 🚧 **v3.0 Design Update** — Phases 8-10 (in progress, started 2026-05-01)

## Overview

v3.0 is a focused refinement of three rough edges in the v2.0 design — theme toggle, gallery, and About page — without changing the underlying Flexoki / Kindle / Obsidian-minimal aesthetic. Zero new runtime dependencies. All work uses platform-native primitives already present in the codebase (inline SVG, native `<dialog>`, CSS `column-count`, Hugo `[[resources]]` frontmatter, render-image hooks).

Phase ordering reflects ascending blast radius: ICON (smallest, lowest risk, no JS) → ABOUT (CSS + template, no JS) → GALLERY (most moving parts, only JS-adding phase). A regression in the latter does not block the simpler features already shipped.

Historical milestones (v1.0, v2.0) are preserved in `.planning/milestones/v2.0-ROADMAP.md` and the section below.

## Phases

**Phase Numbering:**
- v3.0 continues from v2.0's last phase (7), so v3.0 begins at Phase 8.
- Integer phases (8, 9, 10): Planned milestone work
- Decimal phases (e.g., 8.1): Reserved for urgent insertions

### v3.0 Active

- [x] **Phase 8: ICON — SVG Theme Toggle** — Replace text-button toggle with sun/moon SVG icon (header position unchanged, no FOUC, accessible) (completed 2026-05-02)
- [ ] **Phase 9: ABOUT — Dynamic Rounded Redesign** — Asymmetric rounded About layout balancing climbing + professional background, served from dedicated `layouts/about/single.html`
- [ ] **Phase 10: GALLERY — Lightbox + Masonry + Captions** — Native `<dialog>` lightbox, CSS column-count masonry, frontmatter captions in author-controlled order

<details>
<summary>✅ v1.0 Targeted Refinement (Phases 1-2) — SHIPPED 2026-04-27</summary>

- [x] Phase 1: Article Refinement (2/2 plans) — completed 2026-04-27
- [x] Phase 2: Footer Instagram Link (1/1 plan) — completed 2026-04-27

Full archive: [milestones/v2.0-ROADMAP.md](milestones/v2.0-ROADMAP.md) *(v1.0 recorded retroactively at v2.0 close)*

</details>

<details>
<summary>✅ v2.0 Brand & Gallery (Phases 3-7 + 05.1) — SHIPPED 2026-05-01</summary>

- [x] Phase 3: Brand Asset Slicing (1/1 plan) — completed 2026-04-28 *(superseded by 05.1)*
- [x] Phase 4: Theming Foundation (3/3 plans) — completed 2026-04-28
- [x] Phase 5: Wordmark + Favicon Wiring (3/3 plans) — completed 2026-04-29
- [x] Phase 05.1: Swap wordmark + favicon to SVG sources *(INSERTED)* (4/4 plans) — completed 2026-04-29
- [x] Phase 6: Gallery (4/4 plans) — completed 2026-04-30 *(HUMAN-UAT deferred to post-deploy)*
- [x] Phase 7: About Enrichment (4/4 plans) — completed 2026-05-01 *(HUMAN-UAT deferred to post-deploy)*

Full archive: [milestones/v2.0-ROADMAP.md](milestones/v2.0-ROADMAP.md)

</details>

## Phase Details

### Phase 8: ICON — SVG Theme Toggle
**Goal**: Replace the v2.0 text-button theme toggle with a sun/moon SVG icon button — same header position, same persistence, no FOUC, accessible.
**Depends on**: v2.0 Phase 4 (theming foundation — already shipped)
**Requirements**: ICON-01, ICON-02, ICON-03, ICON-04, ICON-05
**Success Criteria** (what must be TRUE on the deployed site):
  1. Visit `https://tbohnstedt.cloud/` in light mode and see a sun SVG icon in the header where the "Toggle theme" text button used to be; switch to dark mode and the icon swaps to a moon — icon always reflects current theme.
  2. Hard-reload the site in dark mode on a throttled connection (CPU 6×) and never see the wrong icon flash for any frame — the inline `<head>` IIFE applies `data-theme` before first paint and CSS keys the icon swap off it.
  3. Activate the icon button with a screen reader (VoiceOver / NVDA) and hear the *target action* announced ("Switch to dark mode" in light, "Switch to light mode" in dark), with `aria-pressed` reporting current state.
  4. Tap the icon on a 320 px-wide mobile viewport and successfully hit it without missing — the button's clickable area is ≥ 44×44 CSS-px even though the SVG itself is 24×24.
  5. Enable "Reduce motion" in OS settings, click the toggle, and observe an instant icon swap with no rotation or fade; disable reduce-motion and the swap eases over ≤ 150 ms.
**Plans**: 2 plans
Plans:
- [x] 08-01-PLAN.md — Markup + CSS: replace text button with sun + moon SVG, add 44×44 hit target, [data-theme]-keyed visibility swap, reduced-motion-gated transition (ICON-01, ICON-04, ICON-05)
- [x] 08-02-PLAN.md — Rewrite end-of-body IIFE: remove textContent, add aria-label setter (action-oriented), preserve persistence + theme-color sync (ICON-02, ICON-03)
**UI hint**: yes

### Phase 9: ABOUT — Dynamic Rounded Redesign
**Goal**: Redesign the About page with an asymmetric rounded layout that balances climbing with professional background, served from a dedicated `layouts/about/single.html` with extended render-image hook arms.
**Depends on**: Phase 8 (proves v3.0 milestone is tracking before larger surgery; no functional dependency)
**Requirements**: ABOUT-01, ABOUT-02, ABOUT-03, ABOUT-04, ABOUT-05, ABOUT-06, ABOUT-07
**Success Criteria** (what must be TRUE on the deployed site):
  1. Visit `https://tbohnstedt.cloud/about/` and see an asymmetric layout — alternating text-image / image-text grid ratios per section — rather than the v2.0 hero + grid-of-four pattern; rendered by a new `layouts/about/single.html` template.
  2. Read the About page top-to-bottom and learn about Timo's professional background AND personal interests (climbing, cycling, cooking) in proportionate measure — not climbing-dominant as in v2.0 Phase 7.
  3. Inspect any photo or role/credential card on the page and see soft 12 px rounded corners (driven by a new `--radius-soft: 12px` token) — replacing the 4–6 px values used pre-v3.0; cards use `var(--bg-secondary)` tint + `var(--border)`, no shadows, no gradients.
  4. Switch to dark theme and read the pullquote — the bolded `strong` text inside `.about-pullquote` remains legible at WCAG AA-large contrast (font-size ≥ 1.4 rem, weight ≥ 500, current 3.97:1 ratio held).
  5. Resize the browser to a < 600 px viewport (or open on mobile) and watch every asymmetric section collapse to a single column — no horizontal overflow, no broken image crops, hero portrait still readable.
  6. View the page source and confirm all About-specific CSS rules are scoped under `body.page-about` — visiting `/blog/` or `/gallery/` shows no leaked About styling.
**Plans**: TBD (planning step decides)
**UI hint**: yes

### Phase 10: GALLERY — Lightbox + Masonry + Captions
**Goal**: Replace the v2.0 uniform-grid + standalone-page-navigation gallery with a native `<dialog>` lightbox, CSS column-count masonry, and per-photo frontmatter captions in author-controlled order.
**Depends on**: Phase 9 (no functional dependency; ordered last because it adds the milestone's only new JS file and has the most moving parts — a regression here cannot block ICON or ABOUT delivery)
**Requirements**: GALLERY-01, GALLERY-02, GALLERY-03, GALLERY-04, GALLERY-05, GALLERY-06, GALLERY-07, GALLERY-08, GALLERY-09
**Success Criteria** (what must be TRUE on the deployed site):
  1. Visit `https://tbohnstedt.cloud/gallery/` on a ≥ 900 px viewport and see photos arranged in a 3-column masonry layout (2 columns at 600–900 px, 1 column < 600 px) with each photo's original aspect ratio preserved — no uniform-grid crops, no `fill 600x400`.
  2. Reload the gallery on consecutive deploys and observe the photos in the same deterministic order driven by `params.weight` in `[[resources]]` frontmatter — no client-side reflow on load, no shuffle between visits, deep-links remain stable.
  3. Click any thumbnail and see it open in a centered native `<dialog>` modal with a blurred backdrop (`backdrop-filter: blur(12px)` with rgba fallback); the body behind the modal is scroll-locked while open; a 1–2 sentence caption renders below the image (gracefully empty if a photo has no caption).
  4. Inside the lightbox, press `←` and `→` to navigate prev/next photos, press `Esc` or click the backdrop / X button to close, and confirm focus returns to the originating thumbnail; `Tab` cycles only within the dialog (focus-trap inherited from native `<dialog>` `showModal()`).
  5. On a touch device, swipe left or right inside the lightbox (≥ 50 px deltaX) and navigate prev/next; tap outside the image or on the X button to close.
  6. Run a Lighthouse / WebPageTest pass against `/gallery/` on a deployed build and observe CLS < 0.1 — every `<img>` ships with explicit `width` + `height` attributes from Hugo's `Resize "600x webp q75"` pipeline; the masonry does not reflow as images load.
  7. Add a new gallery photo by dropping the file into `content/gallery/` and adding a single `[[resources]]` block (`params.caption`, `params.alt`, `params.weight`) to `content/gallery/index.md` — no sidecar files, no build-step regeneration, photo appears at the authored position on next build.
  8. Download any image served from `/gallery/` and inspect its EXIF — find zero GPS, Make, Model, or Serial fields (CI gate carried forward from v2.0 Phase 6 enforces this on every build).
**Plans**: TBD (planning step decides)
**UI hint**: yes

## Progress

**Execution Order:**
v3.0 phases execute in numeric order: 8 → 9 → 10 (decimal insertions appear between integers as needed).

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Article Refinement | v1.0 | 2/2 | Complete | 2026-04-27 |
| 2. Footer Instagram Link | v1.0 | 1/1 | Complete | 2026-04-27 |
| 3. Brand Asset Slicing | v2.0 | 1/1 | Complete (superseded by 05.1) | 2026-04-28 |
| 4. Theming Foundation | v2.0 | 3/3 | Complete | 2026-04-28 |
| 5. Wordmark + Favicon Wiring | v2.0 | 3/3 | Complete | 2026-04-29 |
| 05.1. Swap wordmark + favicon to SVG | v2.0 | 4/4 | Complete | 2026-04-29 |
| 6. Gallery | v2.0 | 4/4 | Complete (HUMAN-UAT post-deploy) | 2026-04-30 |
| 7. About Enrichment | v2.0 | 4/4 | Complete (HUMAN-UAT post-deploy) | 2026-05-01 |
| 8. ICON — SVG Theme Toggle | v3.0 | 2/2 | Complete   | 2026-05-02 |
| 9. ABOUT — Dynamic Rounded Redesign | v3.0 | 0/TBD | Not started | - |
| 10. GALLERY — Lightbox + Masonry + Captions | v3.0 | 0/TBD | Not started | - |

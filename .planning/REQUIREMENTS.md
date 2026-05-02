# Requirements — v3.0 Design Update

**Milestone:** v3.0 Design Update
**Started:** 2026-05-01
**Status:** Locked for roadmap

## Goal

Refine three rough edges in the v2.0 design — theme toggle, gallery, and about page — without changing the underlying Flexoki / Kindle / Obsidian-minimal aesthetic. Zero new runtime dependencies. All work uses platform-native primitives already present in the codebase.

## Locked Decisions (User-confirmed 2026-05-01)

- **Gallery ordering model:** Author-controlled deterministic order via `params.weight` in `[[resources]]` frontmatter. Not Hugo build-time shuffle, not client-side random. Resolves the conflict surfaced in `.planning/research/SUMMARY.md` § Conflict Resolution.
- **About scope:** Layout redesign AND content rewrite ship in the same milestone. v3.0 delivers a single coherent About page balancing climbing + professional background.
- **Lightbox keyboard nav:** Day-one. Esc, ←/→ for prev/next, Tab focus-trap (mostly free via native `<dialog>`), focus restoration on close.

## v3.0 Requirements

### ICON — SVG Theme Toggle

Replace the existing text `<button class="theme-toggle">` with two inline SVG icons (sun + moon), keeping the current header position, persistence, and no-FOUC behavior.

- [x] **ICON-01**: User sees an SVG sun icon in light mode and an SVG moon icon in dark mode in the header (icon shows current state).
- [x] **ICON-02**: User toggles theme by clicking the icon button — same persistence (`localStorage`) and OS-preference detection as the v2.0 text-button toggle, with no flash of wrong icon on first paint.
- [x] **ICON-03**: User using a screen reader hears a meaningful label that reflects the *target action* ("Switch to dark mode" / "Switch to light mode"), and `aria-pressed` reports the current toggle state.
- [x] **ICON-04**: User on mobile or with a trackball hits a tap target ≥ 44×44 CSS-px regardless of the icon's intrinsic 24×24 viewBox.
- [x] **ICON-05**: User with `prefers-reduced-motion` set sees no rotation/fade transition; user without reduced-motion sees a ≤ 150 ms transition wrapped in `@media (prefers-reduced-motion: no-preference)`.

### ABOUT — Dynamic Rounded Redesign

Replace the existing flat About leaf bundle with an asymmetric, rounded layout that balances climbing with professional background, all within Flexoki/Kindle/Obsidian aesthetic constraints. Reference: https://www.tylerkarow.com/about.

- [ ] **ABOUT-01**: User visits `/about/` and sees an asymmetric layout (alternating text/image grid ratios per section) instead of the v2.0 hero + grid-of-four pattern, served from a new `themes/minimal/layouts/about/single.html` template.
- [ ] **ABOUT-02**: User authoring About content can use new image-shape arms (`split`, `feature`, `card`) on the existing `_default/_markup/render-image.html` hook by setting the image title — no new per-image CSS classes required.
- [ ] **ABOUT-03**: User sees softer rounded corners on photos and cards via a new `--radius-soft: 12px` CSS variable applied site-wide (replacing per-element 4–6 px values where used).
- [ ] **ABOUT-04**: User reads role/credential cards rendered with `var(--bg-secondary)` tint + `var(--border)` + 12 px radius — no shadows, no gradients, Flexoki-flat. All About-specific CSS scoped under `body.page-about` (no global rule pollution).
- [ ] **ABOUT-05**: User reading the About page learns about both Timo's professional background AND personal interests (climbing, cycling, cooking) in proportionate measure — not climbing-dominant as in v2.0 Phase 7.
- [ ] **ABOUT-06**: User on dark theme reads the pullquote with WCAG AA-large contrast preserved (`.about-pullquote strong` font-size ≥ 1.4 rem and weight ≥ 500 maintained — current 3.97:1 ratio held).
- [ ] **ABOUT-07**: User on a mobile viewport (< 600 px) sees all asymmetric sections collapse to a single column gracefully — no horizontal overflow, no broken image crops.

### GALLERY — Lightbox + Masonry + Captions

Replace the v2.0 uniform CSS Grid + standalone-image-page navigation with a native `<dialog>` lightbox, CSS column-count masonry, and per-photo captions authored in frontmatter. Reference: http://tylerkarow.com/gallery.

- [ ] **GALLERY-01**: User authoring a new gallery photo adds a single `[[resources]]` entry to `content/gallery/index.md` with `params.caption`, `params.alt`, and `params.weight` — no separate sidecar files, no build-step regeneration.
- [ ] **GALLERY-02**: User browsing `/gallery/` sees photos arranged in a multi-column masonry layout (3 columns ≥ 900 px, 2 at 600–900 px, 1 < 600 px) with each photo's original aspect ratio preserved (Hugo `Resize "600x webp q75"`, not `fill 600x400`).
- [ ] **GALLERY-03**: User browsing the gallery sees photos in a deterministic author-controlled order driven by `params.weight` — same order across deploys, no client-side reflow on load.
- [ ] **GALLERY-04**: User sees a 1–2 sentence caption rendered below each photo's lightbox view (and gracefully empty if a photo has no caption).
- [ ] **GALLERY-05**: User clicking a photo opens it in a centered native `<dialog>` lightbox modal with a blurred backdrop (`backdrop-filter: blur(12px)`, with `rgba` fallback for unsupported browsers), with body scroll locked while open.
- [ ] **GALLERY-06**: User can navigate the lightbox with keyboard: Esc closes, ← / → move to prev/next photo, Tab traps focus inside the dialog (free via `<dialog>` `showModal()`), and focus returns to the originating thumbnail on close.
- [ ] **GALLERY-07**: User on mobile can swipe left/right (50 px deltaX threshold) to navigate prev/next, and tap outside the image (or the X button) to close.
- [ ] **GALLERY-08**: User loading the gallery page experiences CLS < 0.1 — every `<img>` ships with explicit `width` and `height` attributes from Hugo's processed image, and the masonry layout does not reflow as images load.
- [ ] **GALLERY-09**: User downloading any published gallery image finds zero GPS / Make / Model / Serial EXIF fields (CI gate enforced as in v2.0 Phase 6).

## Future Requirements (Deferred)

These were considered for v3.0 and deferred to v3.x or later:

- **ICON-FUT-01**: Single-SVG sun-with-moon-mask morph trick (marginal visual gain over two-SVG approach)
- **GALLERY-FUT-01**: Photo counter overlay ("3 / 18") in lightbox
- **GALLERY-FUT-02**: `<link rel="preload">` for next/prev lightbox image
- **ABOUT-FUT-01**: Hover micro-interactions on role cards (only justified if cards become external links)
- **ABOUT-FUT-02**: Audience-specific About variants (recruiter / collaborator / friend)

## Out of Scope

Explicit exclusions for v3.0 and beyond:

- **Full visual redesign** — Flexoki palette, Kindle/Obsidian-minimal feel, single-stylesheet structure stay locked. v3.0 is refinement, not reinvention.
- **JavaScript framework** — no React, Vue, Svelte, Alpine, htmx. Vanilla JS only. Consistent with v1.0/v2.0.
- **Lightbox/masonry NPM packages** — no PhotoSwipe, GLightbox, Tobii, focus-trap, Macy.js, Masonry.js. Native `<dialog>` + CSS columns are sufficient.
- **CSS Grid Level 3 `masonry`** — Safari-only in 2026, blocked from production. CSS column-count is the universal path.
- **Hugo `collections.Shuffle` for gallery order** — non-deterministic across builds (Hugo issue #5641); breaks reproducible deploys.
- **Client-side random gallery order** — causes layout reflow + CLS risk + breaks deep-links/screenshots.
- **EXIF extraction at build time** — v2.0 invariant: scrub at source. Adding lat/lng or device data to captions via build-step is rejected (privacy).
- **Animation libraries / motion frameworks** — keep transitions to ≤ 150 ms CSS, gated behind `prefers-reduced-motion: no-preference`.
- **New blog posts during this milestone** — content additions deferred to a separate milestone.
- **Multi-language support** — out of scope until a future milestone if at all.
- **Comments / e-commerce / CMS / backend services** — site stays static, deployed to GitHub Pages.

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| ICON-01 | Phase 8 | Complete |
| ICON-02 | Phase 8 | Complete |
| ICON-03 | Phase 8 | Complete |
| ICON-04 | Phase 8 | Complete |
| ICON-05 | Phase 8 | Complete |
| ABOUT-01 | Phase 9 | Pending |
| ABOUT-02 | Phase 9 | Pending |
| ABOUT-03 | Phase 9 | Pending |
| ABOUT-04 | Phase 9 | Pending |
| ABOUT-05 | Phase 9 | Pending |
| ABOUT-06 | Phase 9 | Pending |
| ABOUT-07 | Phase 9 | Pending |
| GALLERY-01 | Phase 10 | Pending |
| GALLERY-02 | Phase 10 | Pending |
| GALLERY-03 | Phase 10 | Pending |
| GALLERY-04 | Phase 10 | Pending |
| GALLERY-05 | Phase 10 | Pending |
| GALLERY-06 | Phase 10 | Pending |
| GALLERY-07 | Phase 10 | Pending |
| GALLERY-08 | Phase 10 | Pending |
| GALLERY-09 | Phase 10 | Pending |

**Coverage:** 21/21 v3.0 requirements mapped to exactly one phase. No orphans. No duplicates.

---
*Last updated: 2026-05-01 — v3.0 milestone start; 21 requirements scoped (5 ICON / 7 ABOUT / 9 GALLERY); traceability filled by `gsd-roadmapper` 2026-05-01.*

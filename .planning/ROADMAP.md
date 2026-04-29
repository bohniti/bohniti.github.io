# Roadmap: Personal Website Refinements

## Overview

The site evolves milestone-by-milestone. **v1.0 (complete)** delivered targeted refinements: a Mermaid-diagrammed video editing post and an Instagram footer link. **v2.0 (current)** establishes a coherent visual identity (sliced brand assets + light/dark theming + script wordmark + favicon set), adds a standalone photo `/gallery/` page using Hugo's image pipeline, and enriches the About page — so the site looks unmistakably like *Timo's site* in either theme.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Article Refinement** - Replace node tree screenshot with Mermaid diagram and sharpen node descriptions with values and tips *(v1.0)*
- [x] **Phase 2: Footer Instagram Link** - Add Instagram icon to site footer matching minimal aesthetic *(v1.0)*
- [ ] **Phase 3: Brand Asset Slicing** - Slice `images/logos.png` sprite into 8 individual PNGs via reproducible Pillow script *(v2.0)*
- [ ] **Phase 4: Theming Foundation** - CSS-variable refactor + dark palette + no-flash inline `<head>` toggle bootstrap with accessibility *(v2.0)*
- [ ] **Phase 5: Wordmark + Favicon Wiring** - Header wordmark images swap by `[data-theme]`; 3-file favicon set wired into `<head>` *(v2.0)*
- [ ] **Phase 6: Gallery** - `/gallery/` page bundle with Hugo-processed WebP, EXIF-stripped, CLS-clean grid *(v2.0)*
- [ ] **Phase 7: About Enrichment** - Convert About to leaf bundle with inline personal photos *(v2.0)*

## Phase Details

### Phase 1: Article Refinement
**Goal**: The video editing article becomes a precise technical reference with an inline diagram and actionable node descriptions
**Depends on**: Nothing (first phase)
**Requirements**: ART-01, ART-02, ART-03, ART-04, ART-05
**Success Criteria** (what must be TRUE):
  1. The video editing article displays a Mermaid diagram showing the 5-node color grading chain instead of the Node tree screenshot
  2. Each node description includes specific parameter value ranges (e.g., Lift, Gamma, Gain values)
  3. Each node includes at least one practical do/don't tip about what the image should look like
  4. Node descriptions are noticeably shorter and more technical than the current prose
**Plans:** 2 plans
Plans:
- [x] 01-01-PLAN.md — Create Hugo `mermaid` shortcode with Flexoki theme variables (Wave 1)
- [x] 01-02-PLAN.md — Rewrite article with Mermaid diagram, per-node Parameter/Range/Tip tables, tighten prose, delete Node tree.png (Wave 2, depends on 01-01)

### Phase 2: Footer Instagram Link
**Goal**: Every page on the site shows an Instagram link in the footer that fits the existing design
**Depends on**: Nothing (independent of Phase 1)
**Requirements**: SOC-01, SOC-02, SOC-03
**Success Criteria** (what must be TRUE):
  1. An Instagram icon is visible in the site footer on every page
  2. Clicking the icon navigates to https://instagram.com/bohniti
  3. The icon's style is consistent with the site's minimal Flexoki-inspired aesthetic
**Plans:** 1 plan
Plans:
- [x] 02-01-PLAN.md - Add Instagram icon + convert GitHub link to icon in footer.html, add .social-icons cluster CSS (Wave 1)
**UI hint**: yes

### Phase 3: Brand Asset Slicing
**Goal**: A reproducible, deterministic slice of `images/logos.png` produces 8 named, alpha-preserving PNG variants under known paths so downstream phases can wire them as-is
**Depends on**: Nothing (foundation phase for v2.0; independent of theming work)
**Requirements**: BRAND-01, BRAND-02, BRAND-03
**Success Criteria** (what must be TRUE):
  1. `themes/minimal/static/images/brand/` contains 8 PNGs named `{logo,icon,minimum,favicon}-{light,dark}.png`, each cropped on integer cell boundaries from the 2×4 sprite with alpha preserved (no white halos on dark variants)
  2. `scripts/slice_logos.py` is committed and re-runnable in a throwaway Pillow venv (not added to any runtime manifest), with a single-line module docstring matching project Python convention
  3. Each sliced wordmark variant (`logo-light.png`, `logo-dark.png`) is ≤ 30 KB after `pngquant`; if measured size exceeds that ceiling, the assets are re-optimized before Phase 5 begins
  4. `identify` (or equivalent) confirms all 8 outputs share consistent dimensions for their column (logo cells equal logo cells, favicon cells equal favicon cells) — no off-by-one crop drift
**Plans:** 1 plan
Plans:
- [x] 03-01-PLAN.md — Author scripts/slice_logos.py, run it in a throwaway Pillow venv to produce 8 sliced PNGs at themes/minimal/static/images/brand/, and verify the BRAND-03 ≤ 30 KB wordmark gate (Wave 1)

### Phase 4: Theming Foundation
**Goal**: A user can toggle between light and dark mode from the header, the choice survives reload, the first paint never flashes the wrong palette, and the toggle is keyboard- and screen-reader-accessible
**Depends on**: Nothing architecturally — runs in parallel with Phase 3 if desired, but blocks Phase 5
**Requirements**: THEME-01, THEME-02, THEME-03, THEME-04, THEME-05, THEME-06
**Success Criteria** (what must be TRUE):
  1. Hard-reloading any page in dark mode under DevTools Slow-3G shows zero light frames in a screen recording — the inline `<head>` IIFE applies `data-theme="dark"` before the stylesheet parses
  2. Toggling the theme button persists the choice across reload (verified by closing and reopening the tab); first-time visitors with OS dark-mode see dark on first paint with no localStorage entry yet written
  3. The toggle is a real `<button type="button">` with `aria-pressed` mutating on click, reachable via Tab key, and respects `prefers-reduced-motion: reduce` (no transition fires under reduced-motion)
  4. `:root[data-theme="dark"]` block in `style.css` defines the full Flexoki dark palette; light palette under `:root` is unchanged from current values; `<meta name="color-scheme" content="light dark">` and a JS-managed `<meta name="theme-color">` keep iOS Safari chrome in sync
  5. Loading `/blog/2026-03-05-climbing-routes/` in dark mode shows Mermaid / Plotly / Leaflet content readable against the dark background using theme-agnostic Flexoki accents (smoke-test eyeball check, no per-library reactivity)
**Plans:** 3 plans
Plans:
- [ ] 04-01-PLAN.md — Add :root[data-theme="dark"] palette block, prefers-reduced-motion body transition, and .theme-toggle styling to style.css (Wave 1)
- [ ] 04-02-PLAN.md — Add color-scheme + theme-color meta tags and the inline head IIFE bootstrap to baseof.html (Wave 1, parallel to 04-01)
- [ ] 04-03-PLAN.md — Append theme-toggle button to header.html, add end-of-body click handler IIFE to baseof.html, and run the THEME-06 dark-mode smoke-test on /blog/2026-03-05-climbing-routes/ (Wave 2, depends on 04-01 + 04-02)
**UI hint**: yes

### Phase 5: Wordmark + Favicon Wiring
**Goal**: Every page renders the script "time BOHNSTEDT" wordmark in place of plain text site title, swapping cleanly with the active theme; browser tabs, bookmarks, and iOS home-screens show a real favicon set sourced from the same brand assets
**Depends on**: Phase 3 (sliced PNGs) AND Phase 4 (`[data-theme]` attribute already set on `<html>`)
**Requirements**: HEAD-01, HEAD-02, HEAD-03, HEAD-04, HEAD-05
**Success Criteria** (what must be TRUE):
  1. Site header replaces the plain `{{ .Site.Title }}` text with two `<img>` tags toggled by `[data-theme]` CSS selectors (no FOUC, no JS swap), both carrying explicit `width`/`height` attributes and the visible variant carrying meaningful `alt="Timo Bohnstedt"`
  2. Switching theme via the toggle from Phase 4 swaps wordmark variants instantly with no logo flicker; Lighthouse Mobile CLS on `/` is < 0.1
  3. `themes/minimal/layouts/partials/favicon.html` defines exactly 3 `<link>` tags — `favicon.ico` (32-multi), `favicon.svg` (with embedded `@media (prefers-color-scheme: dark)`), `apple-touch-icon.png` (180×180) — and is included from `baseof.html` `<head>` immediately after the `<title>`
  4. After deploy, the browser tab favicon, bookmark icon, and iOS home-screen icon all render the TB mark sourced from the sliced brand assets (no generic Hugo / browser default visible)
**Plans:** TBD
**UI hint**: yes

### Phase 6: Gallery
**Goal**: A standalone `/gallery/` page reachable from main nav displays the 18 personal photos in a uniform, web-optimized grid that loads under 2 MB on first paint, ships zero GPS metadata, and stays CLS-clean
**Depends on**: Nothing architecturally (independent of Phases 3/4/5); recommended sequenced after Phase 5 to verify the build-and-deploy loop with the new theme/header wired
**Requirements**: GAL-01, GAL-02, GAL-03, GAL-04, GAL-05, GAL-06, GAL-07
**Success Criteria** (what must be TRUE):
  1. `/gallery/` is reachable from the header nav; the page displays all 18 photos in a CSS Grid (`repeat(auto-fill, minmax(220px, 1fr))`) with the section `max-width` overridden to allow a wider canvas
  2. Each thumbnail is a Hugo-processed WebP (`Process "fill 600x400 Smart webp q75"`) carrying explicit `width`/`height` from `.Width`/`.Height`, `loading="lazy"` below the first row and `loading="eager"` (with `fetchpriority="high"` on the very first) for the above-fold row; clicking a thumbnail navigates to the full-size WebP rendition (`Process "fit 1600x1600 webp q82"`)
  3. `exiftool public/gallery/**/*.{webp,jpg}` after `hugo --minify` shows zero `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, or `Serial*` fields on every output; `[imaging.exif] disableLatLong = true` is set in `hugo.toml` belt-and-suspenders
  4. `/gallery/` first-paint network transfer (DevTools Network tab) is ≤ 2 MB; total `du -sh public/gallery/` ≤ 3 MB; Lighthouse Mobile CLS < 0.1 on the page
  5. `images/galary/` no longer exists in the repo; the photos live as page-bundle resources at `content/gallery/photos/`; `grep -r galary` over the repo returns zero hits in `content/`, `themes/`, and `hugo.toml`
**Plans:** TBD
**UI hint**: yes
**Research flag**: Recommend `/gsd-research-phase` during planning — empirical thumbnail-dimension / WebP-quality / srcset-breakpoint tuning against the actual 18 photos benefits from pre-flight measurement (largest source is 7.5 MB, smallest 150 KB).

### Phase 7: About Enrichment
**Goal**: The About page becomes a richer leaf-bundle layout with a small set of inline personal photos, while keeping the `/about/` URL identical and inheriting the site's theming and image-handling conventions
**Depends on**: Phase 6 (leaf-bundle pattern proven on a similar shape; any Markdown render-image hook from Phase 6 covers About transitively)
**Requirements**: ABOUT-01, ABOUT-02, ABOUT-03
**Success Criteria** (what must be TRUE):
  1. `content/about.md` no longer exists; `content/about/index.md` (leaf bundle) is the new source; the rendered URL `/about/` is unchanged (verified by hitting the deployed URL)
  2. The About page renders multiple personal photos in a richer layout (second column / photo grid / pull-quote rules added to `style.css`) — not a single-column inline-only stream
  3. All About-page images live under `content/about/images/` as page-bundle resources, render with explicit `width`/`height` to prevent CLS, and read correctly in both light and dark themes
**Plans:** TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Article Refinement | 2/2 | Complete | 2026-04-27 |
| 2. Footer Instagram Link | 1/1 | Complete | 2026-04-27 |
| 3. Brand Asset Slicing | 0/1 | Not started | - |
| 4. Theming Foundation | 0/0 | Not started | - |
| 5. Wordmark + Favicon Wiring | 0/0 | Not started | - |
| 6. Gallery | 0/0 | Not started | - |
| 7. About Enrichment | 0/0 | Not started | - |

# Project Research Summary

**Project:** Personal Website Refinements — milestone v2.0 Brand & Gallery
**Domain:** Hugo static site (personal blog) — theme/branding integration + photo gallery
**Researched:** 2026-04-28
**Confidence:** HIGH

## Executive Summary

This is an **integration milestone**, not a greenfield build. The site already has a clean, small custom Hugo theme (`themes/minimal/`, ~265 lines of CSS, 19-line `baseof.html`) with a Flexoki-inspired light palette already declared as CSS custom properties on `:root`. Every v2.0 feature lands in known files; the architecture work is *not* "design a theme system," it is "swap palettes via `[data-theme="dark"]`, slice an existing sprite into 8 PNGs, run 18 photos through Hugo's built-in image pipeline, and convert one page to a leaf bundle." All four research files independently converge on the same solution shape.

The recommended approach is uniformly **vanilla web platform** — Hugo built-ins for image processing, CSS custom properties driven by a `data-theme` attribute on `<html>`, an inline `<head>` IIFE for no-flash theme bootstrap, native `<img loading="lazy">`, and a 3-file favicon set (`.ico` + `.svg` + `apple-touch-icon.png`). **Zero new runtime dependencies are needed.** Pillow is used once, locally, to slice the sprite; the 8 PNG outputs are committed and the venv is thrown away. There is no Node, no npm, no Tailwind, no theme-toggle library, no lightbox library, no external image CDN, no PWA tooling.

The two highest-value risks are (1) **Flash of Unstyled Theme** — if the theme bootstrap is anywhere except inline-and-synchronous in `<head>` before the stylesheet, every visitor sees a light-flash on dark-mode hard reloads, the milestone's explicit launch-blocker — and (2) **gallery weight + EXIF leak** — if the 18 photos (totaling ~50 MB raw, with smartphone GPS metadata) ship through `static/` instead of through Hugo's resource pipeline, the site loses its Lighthouse score AND publishes Timo's home/crag GPS coordinates. Both risks have clean preventions: inline IIFE for FOUC; page-bundle + `.Resources.Match` + `.Process "... webp qN"` for gallery (which strips EXIF on re-encode by default).

## Key Findings

### Recommended Stack

The four researchers agree to the byte on stack choices: nothing new is added at runtime. Hugo Extended 0.157.0 (already pinned) has every needed primitive — `image.Process` / `Resize` / `Fill` / `Fit` with anchors including `Smart`, WebP output, page-resource cascade, `srcset` generation, build caching in `resources/_gen/`. CSS custom properties + a `[data-theme]` attribute selector cover all theming. A ~30-line vanilla JS toggle (inline bootstrap + click handler) covers all interaction. Pillow is the recommended one-off slicer because Hugo's `Crop` uses anchor enums (`TopLeft`, `Smart`, etc.), not pixel offsets, so it is the *wrong* tool for grid extraction from a 2×4 sprite.

**Core technologies:**
- **Hugo Extended 0.157.0** (already pinned) — site generator + image pipeline. No upgrade needed.
- **CSS custom properties + `[data-theme="dark"]` selector** — single source of color truth; existing `:root` palette already speaks in tokens, so dark mode is a palette-swap block, not a rewrite.
- **Inline `<head>` IIFE for theme bootstrap** — ~15 lines vanilla JS, runs synchronously before stylesheet parses, sets `data-theme` on `<html>`. Required by no-flash constraint.
- **Hugo `image.Process "... webp qN"`** — generates responsive thumbnails for 18 gallery photos; cached in `resources/_gen/`. WebP is right format in 2026; AVIF is *not* yet supported by Hugo.
- **Pillow 12.2.0** — one-off local sprite slicer (not a runtime dep, not added to any manifest).
- **3-file favicon set** — `favicon.ico` (32-multi), `favicon.svg` (with embedded `@media (prefers-color-scheme: dark)`), `apple-touch-icon.png` (180). Skip the legacy multi-PNG / `browserconfig.xml` / `mstile-*` matrix.

### Expected Features

The milestone has 6 declared target features. Research confirms each maps to a well-established 2026 personal-blog pattern.

**Must have (table stakes — v2.0 launch):**
- CSS-variables refactor + dark palette — single foundation that unblocks every other theming feature.
- Theme toggle with no-flash inline bootstrap, OS-preference default, `localStorage` persistence, `aria-pressed` on real `<button>`, `prefers-reduced-motion` respected, keyboard reachable.
- Logo sprite sliced into 8 PNGs — deterministic Pillow crop on integer cell boundaries, alpha preserved.
- Header wordmark that swaps via `[data-theme]` CSS — replaces text site title, keeps accessible `alt`.
- Favicon set wired into `<head>` (3 files + 3 `<link>` tags).
- `/gallery/` page — page bundle at `content/gallery/`, photos as resources, Hugo-processed WebP, uniform CSS Grid, native lazy-load with eager-load on first row, `width`/`height` from `.Width`/`.Height` to prevent CLS, EXIF stripped on re-encode.
- About page → leaf bundle + 1–3 inline photos.

**Should have (defer to v2.x):**
- View-transition cross-fade on theme toggle (gated behind `prefers-reduced-motion`).
- Inline SVG wordmark with `currentColor` — *if* SVG source becomes available.
- Native `<dialog>`-based lightbox — only when a real user asks "can I see this bigger?"
- Gallery captions on hover/focus.
- PWA `site.webmanifest` — mostly free given favicon work; ship later.
- Cross-tab theme sync via `storage` event.

**Defer indefinitely (anti-features for this site):**
- Three-state theme toggle (light/dark/auto), `<picture>` + `prefers-color-scheme` for wordmark (breaks manual toggle), JS lightbox libraries (PhotoSwipe et al.), masonry/infinite-scroll/filters, custom `@font-face` for wordmark, AVIF.

### Architecture Approach

The integration component map is small and entirely local: **4 files modified** (`baseof.html`, `header.html`, `style.css`, `hugo.toml`), **4 new files added** (`partials/favicon.html`, `partials/theme-toggle.html` or inline, `layouts/gallery/list.html`, `content/gallery/_index.md`), **1 page conversion** (`content/about.md` → `content/about/index.md`), **1 folder rename + move** (`images/galary/` → `content/gallery/photos/`), and ~14 new asset files in `themes/minimal/static/images/brand/` + `themes/minimal/static/`. The footer needs zero changes — the existing `.social-icons` cluster already uses `currentColor`, so it dark-adapts for free.

**Major components:**
1. **Theme bootstrap** (inline `<head>` IIFE in `baseof.html`) — only thing that runs synchronously before paint.
2. **Palette CSS** (`:root` + `:root[data-theme="dark"]` blocks) — single source of truth; no `@media (prefers-color-scheme)` block.
3. **Theme toggle button** (in `header.html`, click handler small JS) — real `<button>` with `aria-pressed`, sun/moon icon swap inside fixed-dimension container.
4. **Wordmark `<img>` pair** — two `<img>` tags toggled by CSS `[data-theme]` selectors, explicit `width`/`height`.
5. **Favicon partial** — 3 `<link>` tags.
6. **Gallery section** — page-bundle pattern; `.Resources.Match "photos/*"`; `.Process "fill 600x400 Smart webp q75"` thumbs, `.Process "fit 1600x1600 webp q82"` full.
7. **About leaf bundle** — same page-bundle convention as blog posts.

### Critical Pitfalls

1. **FOUC on dark-mode hard reload (Pitfall 1).** Theme bootstrap MUST be inline and synchronous in `<head>` before the stylesheet `<link>`. Verify by screen-recording hard reload under DevTools Slow 3G in dark mode; expect zero light frames.
2. **Gallery weight + EXIF leak (Pitfalls 2 & 3, paired).** Photos must flow through Hugo's resource pipeline (page bundle), not `static/`. Re-encoding to WebP via Hugo strips most EXIF (incl. GPS) by default; add `[imaging.exif] disableLatLong = true` belt-and-suspenders. Verify with `exiftool public/gallery/**/*.{webp,jpg}` post-build expecting empty GPS fields. `/gallery/` first-paint transfer must stay under ~2 MB.
3. **Mixing `prefers-color-scheme` CSS with `[data-theme]` JS.** Pick one. Recommendation: `[data-theme="dark"]` only. A `@media` block in CSS as a "fallback" silently overrides user's manual choice during the brief pre-script paint and creates a perception that the toggle is broken.
4. **CLS from unsized images (Pitfall 5).** Every `<img>` (wordmark, gallery thumbnails, about photos) needs explicit `width`/`height` attributes.
5. **Existing inline scripts (Mermaid, Plotly, Leaflet) won't react to theme toggle (Pitfall 11).** Documented limitation for v2.0. Either ship Mermaid/Plotly with theme-neutral Flexoki accent colors that read on both backgrounds (recommended), or fire a `theme-change` custom event and re-init each library (defer). Smoke-test: load `/blog/2026-03-05-climbing-routes/` in dark mode and eyeball it.

(Full pitfall catalog in `.planning/research/PITFALLS.md` — 20 numbered pitfalls + integration gotchas + recovery strategies.)

## Implications for Roadmap

All four research docs converge on **the same dependency graph**, which dictates phase order. Deviating forces backtracking — e.g., wiring the wordmark before the theme toggle works leaves the swap untested; building the gallery layout before the image pipeline gives a fake "it works" signal that hides 50 MB transfers.

### Phase 1: Brand Asset Slicing (foundation)

**Rationale:** Both the wordmark (Phase 3) and the favicon (Phase 3) consume the 8 sliced PNGs. Slicing is a one-shot deterministic operation that should not block downstream work.
**Delivers:** 8 PNGs in `themes/minimal/static/images/brand/` (`wordmark-{light,dark}.png`, `icon-{light,dark}.png`, `mark-{light,dark}.png`, `favicon-{light,dark}.png`); committed `scripts/slice_logos.py` for reproducibility; `images/logos.png` source untouched.
**Addresses:** Feature #2 (sprite slicing).
**Avoids:** Pitfall 8 (inconsistent dimensions / lossy re-encoding).
**Uses:** Pillow 12.2.0 in throwaway venv.

### Phase 2: Theming Foundation (highest-risk phase, blocks everything visual)

**Rationale:** 10 of 20 documented pitfalls cluster here (FOUC, accessibility, mobile-header layout, theme-color meta sync, localStorage failures, prefers-color-scheme misreads). Architecture, Stack, and Pitfalls all independently mark this as the load-bearing first step.
**Delivers:** CSS-variable refactor of `style.css`; dark-palette block under `:root[data-theme="dark"]`; inline `<head>` IIFE in `baseof.html`; theme-toggle button in `header.html` with sun/moon SVGs, `aria-pressed`, keyboard reachability, `prefers-reduced-motion` respected; localStorage persistence with try/catch; `<meta name="color-scheme" content="light dark">`; manual + scripted update of `<meta name="theme-color">`.
**Addresses:** Feature #1 (theme toggle).
**Avoids:** Pitfalls 1, 6, 7, 11 (decision recorded), 12, 14, 19, 20.
**Implements:** Components 1, 2, 3 from Architecture.

### Phase 3: Wordmark + Favicon Wiring (single coupled phase)

**Rationale:** Both consume same brand-asset inputs from Phase 1, both edit the same `<head>` / `header.html` files. Pitfalls research explicitly recommends not splitting them. Depends on Phase 2 because the wordmark CSS swap reacts to the `[data-theme]` attribute set by toggle bootstrap.
**Delivers:** Header `<a class="site-title">` body replaced with two `<img>` tags toggled by CSS `[data-theme]` selectors; explicit `width`/`height`; meaningful `alt`; `partials/favicon.html` with 3 `<link>` tags; `favicon.ico` + `favicon.svg` (with embedded `@media (prefers-color-scheme: dark)`) + `apple-touch-icon.png`.
**Addresses:** Features #3 (wordmark), #4 (favicon).
**Avoids:** Pitfalls 9, 10 (accepted tradeoff), 15, 18.
**Implements:** Components 4, 5 from Architecture.

### Phase 4: Gallery (highest-bandwidth phase)

**Rationale:** Largest single-feature work (Pitfalls 2, 3, 4, 5, 16, 17 all live here). Independent of Phase 2/3 architecturally but recommended sequenced after Phase 2 to prove build-and-deploy loop with new templates. Folder rename is FIRST commit (in isolation, easy to revert), image-processing pipeline SECOND, layout last.
**Delivers:** `images/galary/` renamed and moved to `content/gallery/photos/`; `content/gallery/_index.md`; `[[menu.main]]` entry in `hugo.toml`; `themes/minimal/layouts/gallery/list.html` using `.Resources.Match "photos/*"` + `.Process` for thumbs and full-size; eager-load first 1–3 thumbnails; `[imaging.exif] disableLatLong = true`; CSS Grid `repeat(auto-fill, minmax(220px, 1fr))` with section `max-width` override.
**Addresses:** Features #5 (gallery), #6 (folder rename).
**Avoids:** Pitfalls 2, 3, 4, 5, 16, 17.
**Implements:** Component 6 from Architecture.

### Phase 5: About Enrichment (lowest risk)

**Rationale:** Strictly last. Depends on leaf-bundle conversion pattern that Phase 4 has now exercised on a similar shape, and any Markdown render-image hook from Phase 4 covers About transitively.
**Delivers:** `content/about.md` → `content/about/index.md` rename; 1–3 personal photos in `content/about/images/`; existing `.page-content img` CSS already handles rendering; URL `/about/` unchanged.
**Addresses:** Feature #7 (richer About page).
**Avoids:** Pitfalls 13, 5.
**Implements:** Component 7 from Architecture.

### Phase Ordering Rationale

- **Phase 1 first** because slicing is deterministic, blocks both wordmark and favicon, and doesn't depend on theming.
- **Phase 2 second** because it concentrates highest-risk work into a single phase that ships verified before Phase 3 builds on top of `[data-theme]`. No "we'll add ARIA / FOUC fix later" version is acceptable.
- **Phase 3 third (single phase, both wordmark and favicon)** because Phase 2's `[data-theme]` is the swap mechanism, and the favicon set shares the same `<head>` partial edits.
- **Phase 4 fourth** because gallery is independent of theming and can be deferred until brand identity ships.
- **Phase 5 last** because it's a 30-minute migration that depends on no other phase architecturally.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Gallery):** Recommended `/gsd:research-phase` — concrete decisions on thumbnail dimensions, WebP quality, eager-vs-lazy thresholds, srcset breakpoints, and CI cache strategy benefit from pre-flight measurement against the actual 18 photos.

Phases with standard patterns (skip research-phase):
- **Phases 1, 2, 3, 5:** Patterns are locked in across all four research docs.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All recommendations verified against official Hugo docs, Pillow notes, MDN, direct repo read. Zero new runtime deps means no version-compat guesswork. |
| Features | HIGH | All 6 target features map to well-established 2026 personal-blog patterns; each backed by 5+ practitioner sources. |
| Architecture | HIGH | Researcher read every theme file directly; existing CSS already speaks in custom-property tokens; integration component map is concrete. |
| Pitfalls | HIGH | 20 pitfalls grounded in this repo's actual structure (verified file sizes, exact CSS line numbers, real grep audit for `galary`). |

**Overall confidence:** HIGH. The four docs converge on same architecture, stack, and phase-ordering recommendations without contradiction.

### Convergent Recommendations (all 4 docs agree — encode as roadmap success criteria)

- `data-theme` attribute on `<html>`, no `@media (prefers-color-scheme)` in CSS.
- Inline `<head>` IIFE for theme bootstrap, before stylesheet link.
- Hugo page bundle for gallery (NOT `static/`, NOT project-root `images/`).
- WebP via `image.Process`, no AVIF, no external image CDN.
- 3-file favicon set (`.ico`, `.svg`, `apple-touch-icon.png`).
- Pillow one-off slicer; not Hugo `Crop`; not in `requirements.txt`.
- Two-image CSS toggle for wordmark, not `<picture>` + `prefers-color-scheme`.
- Real `<button type="button">` with `aria-pressed`, `prefers-reduced-motion` honored.
- Native `loading="lazy"` + `decoding="async"`, eager on first row, no JS lightbox library.
- About page → leaf bundle.
- Folder rename `images/galary/` → `content/gallery/photos/` (move into Hugo content tree, not just rename in place).
- Footer needs zero changes.

### Tensions / Adjudications

1. **Favicon matrix size.** Features lists 6-file matrix as table stakes; Stack and Pitfalls recommend 3-file minimum. **Adjudication: 3-file set in Phase 3, defer manifest + 192/512 PNGs to v2.x.**
2. **Wordmark double-fetch.** Architecture endorses two-image CSS toggle; Pitfalls #10 flags as bandwidth waste. **Adjudication: two-image CSS toggle in Phase 3, with acceptance criterion that each variant is <30 KB after `pngquant`.** If measured size exceeds 50 KB per variant, fall back to single-`<img>` JS pattern.
3. **Lightbox in v2.0 vs deferred.** Features lists in "Should Have"; Stack and Architecture defer. **Adjudication: defer to v2.x.** Open question for requirements: does Timo want lightbox in v2.0?
4. **Existing diagrams (Mermaid/Plotly/Leaflet) under theme toggle.** Only Pitfalls #11 surfaces this. **Adjudication: roadmap Phase 2 must include smoke-test acceptance criterion (load `/blog/2026-03-05-climbing-routes/` in dark mode); no code change to existing posts in v2.0.**
5. **Resources cache committed to git vs `actions/cache`.** **Adjudication: defer until measured. If CI gallery-build exceeds ~60s, add `actions/cache` step.**

### Gaps to Address (Open Questions for Requirements Step)

- **Is an SVG source available for the wordmark?** If yes, Phase 3 changes from two-image CSS toggle to single inline SVG.
- **Lightbox in v2.0?** See adjudication #3.
- **Per-photo captions in v2.0?**
- **EXIF strip strategy.** Recommend belt-and-suspenders (Hugo re-encode + explicit `[imaging.exif]` config + `exiftool` smoke test).
- **Theme-color meta strategy on iOS Safari.** Hybrid pattern (two media-queried meta tags + one JS-managed). **Resolve in Phase 2 planning.**
- **Mobile-header layout when toggle button added.** Verify in Phase 2 at 320 / 375 / 414 / 600px viewports.
- **Exact Flexoki dark palette values.** Source from https://stephango.com/flexoki. Resolve in Phase 2 planning.
- **Thumbnail aspect ratio.** Default to `Fill 600x400 Smart` (4:3 uniform crop). Defer to Phase 4 planning, possibly preceded by `/gsd:research-phase`.

### Watch Out For (Top 5 Highest-Priority Pitfalls — Roadmapper Must Encode as Phase Success Criteria)

1. **FOUC on dark-mode hard reload (Phase 2).** Inline IIFE in `<head>` *before* stylesheet link. Verify by screen-recording hard reload under DevTools Slow 3G in dark mode; expect zero light frames.
2. **EXIF/GPS leak from gallery photos (Phase 4).** `exiftool public/gallery/**/*.{webp,jpg}` shows no `GPSLatitude` / `GPSLongitude` / `Make` / `Model` / `Serial` fields. Privacy harm cannot be undone after deploy.
3. **Gallery page weight blowup (Phase 4).** `du -sh public/gallery/` < 3 MB; first-paint network transfer < 2 MB.
4. **CLS on header wordmark, gallery, about photos (Phases 3 + 4 + 5).** Every `<img>` needs explicit `width`/`height`. Lighthouse Mobile CLS < 0.1 across `/`, `/gallery/`, `/about/`.
5. **Theme toggle accessibility (Phase 2).** Real `<button>` with `aria-pressed` mutating on click; keyboard reachable; `prefers-reduced-motion` respected. Verify with VoiceOver / NVDA + `prefers-reduced-motion: reduce` test.

## Sources

### Primary (HIGH confidence)
- Hugo official docs — image-processing, methods/resource/process, page-bundles, configuration/imaging
- Hugo releases — 0.157.0 pinned has every needed feature
- MDN — `aria-pressed`, `meta theme-color`, `meta color-scheme`, `prefers-color-scheme`, `prefers-reduced-motion`, `loading="lazy"`
- W3C ARIA APG — Switch Pattern, Button Pattern
- web.dev (Google official) — color-scheme, optimize-cls, browser-level-image-lazy-loading
- Flexoki spec — https://stephango.com/flexoki
- Pillow 12.2.0 release notes
- Direct repo read — `themes/minimal/static/css/style.css`, `baseof.html`, `header.html`, `footer.html`, `hugo.toml`, `content/about.md`, `images/galary/` (verified file sizes 152 KB → 7.5 MB)

### Secondary (MEDIUM confidence — multiple independent sources agree)
- Evil Martians — How to Favicon in 2026
- No-flash dark mode pattern — whitep4nth3r, bram.us, vbesse.com
- Hugo dark-mode community — Yonkov, Phelipe Teles, Radu Matei, Ken Muse, tiredsg.dev, Ryan Feigenbaum, CSSence, CSS-Tricks
- Hugo image-processing practitioner guides — Bryce Wray, Henrik Sommerfeld, Sander ten Brinke, Jack Henschel
- Hugo discourse — EXIF stripping, page-bundle paths, `resources/_gen/` caching
- Lighthouse / GitHub community — Safari 15.4 manifest icons, GitHub Pages favicon caching

### Tertiary (LOW confidence / single-source — flag for validation)
- CI build-time projections for first gallery build (resolve via Phase 4 measurement)
- Exact Flexoki dark palette values (taste calls, resolve in Phase 2 planning)
- Whether two-image wordmark double-fetch is acceptable in practice (resolve in Phase 3 with measured asset sizes)

---
*Research completed: 2026-04-28*
*Ready for roadmap: yes*

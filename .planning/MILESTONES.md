# Milestones

## v3.0 Design Update (Shipped: 2026-05-04)

**Phases:** 3 (8, 9, 10) | **Plans:** 8 | **Tasks:** 13
**Timeline:** 2026-05-01 → 2026-05-04 (4 days)
**Live at:** https://tbohnstedt.cloud/

### Delivered

Three rough edges in the v2.0 design refined without changing the underlying Flexoki / Kindle / Obsidian-minimal aesthetic. Theme toggle becomes an SVG icon, the About page gets an asymmetric rounded layout balancing climbing + professional background, and the gallery gains a native `<dialog>` lightbox with masonry layout and author-controlled per-photo captions. Zero new runtime dependencies — every feature uses platform-native primitives (inline SVG, `<dialog>`, CSS `column-count`, Hugo `[[resources]]` frontmatter, render-image hooks).

### Key Accomplishments

- **ICON — SVG theme toggle (Phase 8)** — Replaced text "Dark" button with sun/moon Lucide v0.547.0 inline-SVG button. CSS-only `[data-theme]` visibility swap (zero JS in the swap path), 44×44 WCAG 2.5.5 hit target via `place-items: center` shell, reduced-motion-gated 150 ms opacity cross-fade. End-of-body IIFE rewritten to set `aria-label` action-oriented strings ("Switch to dark mode" / "Switch to light mode") while preserving v2.0 persistence, `aria-pressed`, `theme-color` meta sync verbatim. Head IIFE byte-identical to v2.0 (Pitfall 1 contract held).
- **ABOUT — Dynamic rounded redesign (Phase 9)** — New `themes/minimal/layouts/about/single.html` template, 3 new Hugo shortcodes (`pullquote`, `split`, `feature`), 2 new render-image hook arms (`split`, `feature`), `--radius-soft: 12px` token applied site-wide. Asymmetric alternating text/image layout balancing professional background with climbing/cycling/cooking. WCAG AA-large pullquote contrast preserved in dark theme; mobile reflow to single column verified.
- **GALLERY — Lightbox + masonry + captions (Phase 10)** — Native `<dialog>` lightbox (free focus-trap via `showModal()`) with 12 px `backdrop-filter: blur` and rgba fallback, CSS `column-count` masonry (3/2/1 columns at 900/600/<600 px), per-photo `params.weight`-driven deterministic order, optional frontmatter captions with graceful empty rendering, 50 px deltaX touch-swipe nav, scroll-locked body, page-scoped vanilla-JS IIFE in `lightbox.js` (D-14/D-15). EXIF scrub CI gate added to `deploy.yml` against `GPSLatitude|GPSLongitude|Make|Model|SerialNumber`.
- **EXIF AutoOrient fix (post-execution patch)** — Discovered post-deploy that 4 gallery + 2 about photos with non-normal EXIF Orientation rendered upside-down or sideways because Hugo's `image.Process` strips EXIF without auto-rotating pixels first. Chained `images.AutoOrient` filter before every `.Process` call across 8 sites in 3 templates (`gallery/single.html`, `about/single.html`, `_default/_markup/render-image.html`). Documented in `.planning/debug/gallery-exif-rotation.md`.
- **Gallery content authoring (post-execution)** — 5 author-written captions added (Hochfeiler approach, Hasenalarm 12-pitch top-out, ice climbing with Peter & Isabell, Leonidio New Year's sport climbing, Lofoten sunset with Janine); 1 new photo (`IMG_8985.jpg`) added with EXIF privacy fields stripped before commit per REQ GALLERY-09.

### Known Deferred Items at Close

2 items acknowledged and deferred at close (see STATE.md § Deferred Items):

- **UAT (2 phases):** Phase 09 (5 gates) — closure happened indirectly via Phase 10 live-site walkthrough; Phase 10 (6 scenarios) — closure happened in `10-UAT.md`, all 6 passed live (commit `5ddece6`). Both `*-HUMAN-UAT.md` scaffold files retain `status: scaffolded` as the project pattern (frontmatter never gets ticked).

These do not block close — implementation is shipped, all CI gates green, all 21 v3.0 requirements complete (5 ICON + 7 ABOUT + 9 GALLERY).

### Requirements

21/21 v3 requirements marked Complete (ICON-01..05, ABOUT-01..07, GALLERY-01..09).

---

## v2.0 Brand & Gallery (Shipped: 2026-05-01)

**Phases:** 6 (3, 4, 5, 05.1, 6, 7) | **Plans:** 19 | **Tasks:** 20
**Timeline:** 2026-04-28 → 2026-05-01 (3 days, 98 commits)
**Code delta:** +1,173 LOC (CSS 146, HTML 96, Python 69, SVG 814, MD 34) across 49 files

### Delivered

A coherent visual identity (logo + dark/light theming) and a photo gallery — the site looks unmistakably like *Timo's site* on every page in either theme.

### Key Accomplishments

- **Theming foundation** — Flexoki dark palette under `[data-theme="dark"]`, no-FOUC inline `<head>` IIFE, accessible `<button>` toggle (`aria-pressed`, `prefers-reduced-motion`, `theme-color` meta sync); Mermaid/Plotly/Leaflet readability validated on `/blog/2026-03-05-climbing-routes/` (Phase 4).
- **Wordmark** — script "time BOHNSTEDT" wordmark inlined as SVG via Hugo `readFile + safeHTML`, recoloring through `currentColor + var(--text)`; replaced earlier sliced-PNG path (Phases 5 + 05.1).
- **Favicon set** — 3-file set wired into `<head>` via `partials/favicon.html`: `favicon.ico` (multi-frame 16/32/48), native path-based `favicon.svg` (4.8 KB, down from 77 KB; embedded `prefers-color-scheme` rule), 180×180 `apple-touch-icon.png` — all generated by `scripts/build_brand_assets.py` (cairosvg pipeline, 69 LOC, down from 205) (Phase 05.1).
- **Gallery** — `/gallery/` page bundle with 18 photos, Hugo `image.Process` WebP pipeline (q75 thumbs / q82 fulls), zero GPS/Make/Model/Serial in published output, ≤ 2 MB first-paint, CLS < 0.1 (Phase 6).
- **About enrichment** — leaf bundle with hero/pullquote/grid render-image hook (480×600 q80 / 400×300 q75 / 800×600 q78), 5 EXIF-scrubbed personal photos, legacy `content/about.md` retired (Phase 7).
- **Codebase health** — sliced-PNG brand path retired in 05.1; `.claude/` added to `.gitignore`; stale About refs auto-fixed in CLAUDE.md.

### Known Deferred Items at Close

6 items acknowledged and deferred to post-deploy human verification (see STATE.md § Deferred Items):

- **UAT (4 phases):** Phase 05 (4 scenarios), Phase 05.1 (6 scenarios), Phase 06, Phase 07 — all gated on deploying to `https://tbohnstedt.cloud/` and walking through `*-HUMAN-UAT.md` checklists in the browser.
- **Verification (2 phases):** Phase 05 and Phase 05.1 marked `human_needed` — favicon rendering must be confirmed in real browser tabs, bookmarks, and iOS home-screen icons after deploy.

These do not block close because the implementation is shipped, automated gates are green, and deferral was the planned exit pattern (`HUMAN-UAT.md` files written for post-deploy walkthrough).

### Requirements

24/24 v2 requirements marked Complete. BRAND-01..03 (Phase 3 sliced-PNG path) recorded as superseded by Phase 05.1 SVG implementation — underlying brand-assets need is met by the SVG path.

---

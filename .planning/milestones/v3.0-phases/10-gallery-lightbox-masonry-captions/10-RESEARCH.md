# Phase 10: GALLERY — Lightbox + Masonry + Captions — Research

**Researched:** 2026-05-04
**Domain:** Hugo static site (gallery refactor: native `<dialog>` lightbox + CSS column-count masonry + frontmatter captions + EXIF CI gate)
**Confidence:** HIGH (every recommendation grounded in CONTEXT.md decisions, the existing codebase, or first-party Hugo / MDN / caniuse documentation; single Hugo template-API question — `sort` over `.Resources.Match` — has multiple authoritative sources)

---

## Summary

Phase 10 ships three coordinated changes to the existing `content/gallery/` page bundle and `themes/minimal/layouts/gallery/single.html` precedent: (1) per-photo `[[resources]]` frontmatter blocks in `content/gallery/index.md` carrying `caption`, `alt`, and `weight`; (2) a CSS `column-count` masonry layout replacing the v2.0 uniform 220-px CSS-Grid, paired with a Hugo `Resize "600x webp q75"` thumb directive that preserves each photo's intrinsic aspect ratio; (3) a native `<dialog>` lightbox in a new `themes/minimal/static/js/lightbox.js` IIFE (~80 LOC) loaded only from `gallery/single.html`, with backdrop blur, manual body-scroll lock, keyboard navigation, focus restoration, and 50-px-deltaX touch swipe.

A fourth, independent change adds a CI step to `.github/workflows/deploy.yml` that runs `exiftool` against `content/gallery/photos/*.{jpg,JPG,jpeg,JPEG}` and fails the build if `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, or `SerialNumber` fields appear, upgrading the existing source-side `[imaging.exif] disableLatLong` (in `hugo.toml`) into a defensive build gate.

CONTEXT.md locks 28 decisions (D-01..D-28). The planner's job is to convert these into ordered tasks, not to revisit alternatives. This research focuses on the *exact* APIs, syntax, and verification surfaces each decision implies — and surfaces the few residual judgment calls (gap values, `touchcancel` defensiveness, plan count 3 vs 4) that CONTEXT.md hands to the planner.

**Primary recommendation:** Follow the four-wave order in D-26 (Data → Template+CSS → JS → CI gate → Verification). The data layer (frontmatter) is the foundation; ship it first as a no-UX-impact commit so the template can read `Params.caption`/`Params.alt`/`Params.weight` immediately. Defer all `lightbox.js` work until the template emits the `data-caption`/`data-alt` attributes the JS expects.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

The 28 decisions D-01..D-28 from CONTEXT.md are locked. Verbatim per CONTEXT.md `<decisions>`:

- **D-01** Per-photo `[[resources]]` blocks in `content/gallery/index.md` (one TOML array entry per photo with `src = "photos/<filename>"`, `name = "photos/<filename>"`, `params = { caption, alt, weight }`). NOT sidecar `.md` files. NOT a YAML data file.
- **D-02** Captions are optional with graceful empty rendering: `{{ with $photo.Params.caption }}<figcaption …>{{ . }}</figcaption>{{ end }}`. NO `errorf` build-fail.
- **D-03** `params.alt` is REQUIRED for every photo (lightbox image is primary content of `<dialog>`). Thumbnail keeps `alt=""` (decorative inside `aria-label`-ed `<a>`); lightbox `<img>` reads `alt="{{ $photo.Params.alt }}"`.
- **D-04** Author-controlled deterministic order via `params.weight`. Template: `{{ range (sort (.Resources.Match "photos/*") "Params.weight") }}`. NO `collections.Shuffle`, NO client-side shuffle, NO filename-alphabetical.
- **D-05** Thumbnail processing: `$photo.Process "Resize 600x webp q75"` (width-only, height proportional). Replaces v2.0 `fill 600x400 Smart webp q75`.
- **D-06** Full image processing: keep existing `$photo.Process "fit 1200x1200 webp q78"`. Quality stays at q78. NO `<link rel="preload">` for fulls.
- **D-07** CSS `column-count` masonry. ≥900 px → 3 cols; 600–900 px → 2 cols; <600 px → 1 col. `column-gap: 1rem`. `.gallery-item { break-inside: avoid; margin-bottom: 1rem; }`. Delete v2.0 `display: grid` rule. NO CSS Grid Level 3 `masonry`. NO JS masonry.
- **D-08** Native `<dialog>` element + `dialog.showModal()`. NOT a DIV-based modal.
- **D-09** ONE `<dialog>` element in DOM, mutated in place per click. Single `<dialog id="gallery-lightbox">` at bottom of `gallery/single.html` `{{ define "main" }}` block.
- **D-10** Backdrop click closes via `dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); })`. X button is the explicit visual close affordance. Esc closes natively.
- **D-11** Manual body scroll lock. JS sets `document.body.style.overflow = 'hidden'` on open, restores previous value on close.
- **D-12** `backdrop-filter: blur(12px)` with rgba fallback via `@supports`. `-webkit-backdrop-filter` retained for Safari <17. Default fallback always present.
- **D-13** Single backdrop colour: `rgba(16, 15, 15, 0.85)` (matches `--bg` dark hex). No theme-specific override.
- **D-14** New file `themes/minimal/static/js/lightbox.js`, ~80 LOC IIFE. Loaded from `gallery/single.html` (NOT `baseof.html`) via `<script src="{{ "js/lightbox.js" | absURL }}" defer></script>`.
- **D-15** IIFE structure: bind click on every `<a class="gallery-item">` → `e.preventDefault()`, swap dialog content from `a.href` / `a.dataset.caption` / `a.dataset.alt` → `dialog.showModal()`. Plus keydown for arrows, close button, backdrop click, touch swipe, body overflow save/restore, NO image preloading.
- **D-16** DOM-walk siblings for prev/next. JS uses `Array.from(grid.children).indexOf(a)`; `grid.children[idx ± 1]` with modulo wrap. NO data-index attributes, NO JS array.
- **D-17** `<dialog aria-label="Photo {n} of {total}">` updated each navigation via `dialog.setAttribute('aria-label', ...)`. NOT `aria-labelledby` (figcaption may be empty per D-02).
- **D-18** 50 px deltaX threshold. Vertical swipe is a no-op. ~20 LOC inline in lightbox.js.
- **D-19** Keep semantic `<a class="gallery-item" href="$full.RelPermalink">` wrapper. JS-disabled fallback = full-image page navigation. Existing `loading`/`fetchpriority`/`decoding` attributes preserved.
- **D-20** Lightbox DOM: `<dialog id="gallery-lightbox">` containing `<button class="gallery-lightbox-close">`, `<button class="gallery-lightbox-prev">`, `<img class="gallery-lightbox-img">`, `<figcaption class="gallery-lightbox-caption">`, `<button class="gallery-lightbox-next">`. Lucide-style 24×24 inline SVGs (chevron-left, chevron-right, X).
- **D-21** All new lightbox/masonry CSS scoped under `body.page-gallery`. Class names use `.gallery-` prefix. FORBIDDEN generic names: `.lightbox`, `.modal`, `.close`, `.prev`, `.next`. Single `style.css` file; new section comments `/* === Gallery — Masonry === */` and `/* === Gallery — Lightbox === */`.
- **D-22** All new transitions wrapped in `@media (prefers-reduced-motion: no-preference)`. Same pattern as `style.css:50-56` body color transition.
- **D-23** Two-layer EXIF gate: (1) keep `[imaging.exif] disableLatLong = true` in `hugo.toml:34-36`; (2) NEW CI step in `.github/workflows/deploy.yml` runs `exiftool` against `content/gallery/photos/*.{jpg,JPG,jpeg,JPEG}` and fails on `GPSLatitude`/`GPSLongitude`/`Make`/`Model`/`SerialNumber`.
- **D-24** CLS gate: `<img width=… height=…>` from Hugo `image.Process`. Lighthouse CLS < 0.1 on deployed `/gallery/`. HUMAN-UAT item if Lighthouse can't run automatically.
- **D-25** `.gallery-lightbox-img { max-width: 100%; max-height: calc(100vh - 8rem); object-fit: contain; }`. Caption sits below image. NO `width: 100%`.
- **D-26** Five-wave internal order: (1) Data — author 18 `[[resources]]`; (2) Template + CSS — modify `gallery/single.html` and `style.css`; (3) JS — author `lightbox.js`; (4) CI gate — exiftool step; (5) Verification.
- **D-27** Suggested plan count: 3 (`10-01 Authoring + Frontmatter`, `10-02 Template + CSS + EXIF CI`, `10-03 Lightbox JS + Verification + HUMAN-UAT`). Final count is planner's call; 4 is acceptable.
- **D-28** Keep `<a class="gallery-item" href="{{ $full.RelPermalink }}" aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size">` from gallery/single.html:12-14. Add `data-caption="{{ $photo.Params.caption }}"` and `data-alt="{{ $photo.Params.alt }}"`. Keep `loading`/`fetchpriority`/`decoding`.

### Claude's Discretion

Per CONTEXT.md `<decisions>` § "Claude's Discretion (handed to planner)":

- Exact `gap` values for masonry column-gap (`1rem` default, `0.75rem` mobile? — planner picks visually).
- Exact `padding` / `border-radius` of dialog buttons — within Flexoki / Pitfall 16 envelope (no shadows, soft 8–12 px radius via `var(--radius-soft)` if appropriate).
- Whether to include a hover state on buttons — within `prefers-reduced-motion: no-preference` (D-22).
- CSS authoring order inside the new section block (one big rule vs split per element).
- Whether 3 plans or 4 (D-27 default vs split EXIF CI).
- Exact LOC of `lightbox.js` (~80 LOC budget).
- Whether to include `touchcancel` handling alongside touchstart/touchend (defensive UX).
- Order of `[[resources]]` entries in `index.md` is by `weight` value the author chooses; planner doesn't pre-curate weights — author iterates after first build.

### Deferred Ideas (OUT OF SCOPE)

Per CONTEXT.md `<deferred>` — DO NOT research, DO NOT implement:

- GALLERY-FUT-01: Photo counter overlay (`3 / 18`).
- GALLERY-FUT-02: `<link rel="preload">` for next/prev lightbox image.
- One-shot `scripts/shuffle_gallery.py` to author `weight` values.
- Caption fade-in stagger (50 ms after image).
- Single-SVG morph for theme toggle (ICON-FUT-01; not Phase 10).
- Per-photo sidecar `.md` files for caption authoring (rejected by REQUIREMENTS Locked Decisions).
- Hugo `collections.Shuffle` for gallery order (anti-feature).
- Client-side random gallery order on each page load (anti-feature).
- CSS Grid Level 3 `grid-template-rows: masonry` (Safari-only in 2026; anti-feature).
- PhotoSwipe / GLightbox / Tobii / Slightbox / Lightbox2 (anti-features).
- Masonry.js / Isotope / Bricks.js / packery (anti-features).
- focus-trap NPM package (anti-feature; native `<dialog>` covers it).
- Lucide / Heroicons / Feather / Phosphor as installed packages (anti-features; hand-author paths inline).
- A web font for the gallery (anti-feature).
- Pre-fetching all full-size photos for "snappy UX" (Pitfall 11; budget violation).
- Bumping full-image quality from q78 to q82 (Pitfall 11; canonical is q78).
- JS-driven masonry layout (anti-feature; CSS column-count is sufficient).
- Per-photo Plotly/Leaflet/interactive embeds (out of scope).
- Comments on photos / e-commerce / CMS / backend services (out of scope).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GALLERY-01 | Author `[[resources]]` entries in `content/gallery/index.md` with `params.caption`, `params.alt`, `params.weight` — no sidecar files, no build-step regeneration. | **§ Hugo Frontmatter Schema** documents the exact TOML shape; `[[resources]]` API is HIGH confidence (Hugo docs `/content-management/page-resources/`, stable since 0.31). The 18 existing photos at `content/gallery/photos/` (verified via `ls`) supply the exact filenames the entries must match byte-for-byte (Pitfall 14 — case-preserved `.jpg`/`.JPG`/`.jpeg` mix). |
| GALLERY-02 | Multi-column masonry (3 ≥900 px / 2 at 600–900 px / 1 <600 px) preserving each photo's natural aspect ratio (Hugo `Resize "600x webp q75"`, not `fill 600x400`). | **§ Masonry Layout** + **§ Image Processing**. `column-count` + `break-inside: avoid` is HIGH confidence (universal browser support since IE10, MDN). `Resize` width-only behavior verified in Hugo docs. |
| GALLERY-03 | Photos in deterministic author-controlled order driven by `params.weight` — same order across deploys, no client-side reflow. | **§ Hugo Sort over Resources** documents `sort (.Resources.Match "photos/*") "Params.weight"` syntax (HIGH confidence, Hugo `/functions/collections/sort/`). Anti-pattern of `collections.Shuffle` non-determinism verified at Hugo issue #5641. |
| GALLERY-04 | 1–2 sentence caption rendered below each photo's lightbox view; gracefully empty if a photo has no caption. | **§ Caption Optionality**. `{{ with $photo.Params.caption }}…{{ end }}` is the Hugo idiom for optional fields — emits zero DOM if absent. HIGH confidence. |
| GALLERY-05 | Click photo → centered native `<dialog>` lightbox modal with blurred backdrop (`backdrop-filter: blur(12px)`, rgba fallback), body scroll-locked while open. | **§ Native `<dialog>` Mechanism** + **§ Backdrop Strategy** + **§ Body Scroll Lock**. `<dialog>` + `showModal()` is HIGH confidence (MDN; Chrome 37+, Firefox 98+, Safari 15.4+). `backdrop-filter` 92%+ support (caniuse). Manual body scroll lock pattern is well-documented (Pitfall 8). |
| GALLERY-06 | Keyboard nav: Esc closes, ←/→ prev/next, Tab focus-trap (free via `<dialog>` `showModal()`), focus returns to originating thumbnail on close. | **§ Native `<dialog>` Mechanism**. Esc + focus trap + focus restoration are browser-native via `showModal()` (W3C APA, CSS-Tricks "There is No Need to Trap Focus on a Dialog Element"). Arrow nav is ~10 LOC of `keydown` switch. HIGH confidence. |
| GALLERY-07 | Mobile: swipe left/right (50 px deltaX) prev/next; tap outside image (or X button) closes. | **§ Touch Swipe**. `touchstart` + `touchend` deltaX threshold is a documented vanilla pattern (~20 LOC). HIGH confidence. |
| GALLERY-08 | CLS < 0.1 on `/gallery/` — every `<img>` ships explicit `width`/`height` from Hugo's processed image; masonry doesn't reflow as images load. | **§ CLS Verification**. Hugo emits `width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"`; modern browsers (since 2024) translate these into `aspect-ratio` reservation. HIGH confidence. |
| GALLERY-09 | Zero GPS / Make / Model / Serial EXIF on any published gallery image (CI gate enforced as in v2.0 Phase 6). | **§ EXIF CI Gate**. `exiftool -GPS:all -Make -Model -SerialNumber …` is the documented pattern (Pitfall 13). Apt installation is `apt-get install -y libimage-exiftool-perl` on `ubuntu-latest` (verified via apt package index). MEDIUM-HIGH confidence on exact field names; HIGH on the gate mechanic. |

</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

The repo's `CLAUDE.md` and `.planning/PROJECT.md` impose the following directives. The planner MUST verify each constraint is honored:

| Constraint | Source | Impact on Phase 10 |
|------------|--------|--------------------|
| Hugo static site, no JS frameworks | CLAUDE.md / PROJECT.md | `lightbox.js` is vanilla ES6 IIFE only. NO React/Vue/Svelte/Alpine/htmx. |
| Vanilla JS only | CLAUDE.md / PROJECT.md | Confirmed by D-14/D-15 (~80 LOC IIFE). |
| Single CSS file at `themes/minimal/static/css/style.css` | CLAUDE.md / `.planning/codebase/CONVENTIONS.md` | All new lightbox/masonry CSS appends to this file. NO new CSS file. NO Tailwind/SCSS/PostCSS. |
| Theme stays Flexoki-inspired (light + dark) | CLAUDE.md / PROJECT.md | Lightbox colors come from existing `--bg`/`--bg-secondary`/`--text`/`--accent`/`--border`/`--radius-soft` tokens. NO hex literals except the rgba backdrop pair (D-13, theme-invariant). |
| No flash on load | CLAUDE.md / PROJECT.md | Phase 10 doesn't touch theme bootstrap; gallery JS runs `defer` after DOM ready. No FOUC risk. |
| Performance ≤ 2 MB first-paint | CLAUDE.md / PROJECT.md | Verified by NOT pre-loading fulls (D-06, Pitfall 11). Thumbs at q75 + lazy-load preserve budget. |
| Accessibility: keyboard-reachable, `aria-label`, `prefers-reduced-motion` | CLAUDE.md / PROJECT.md | `<dialog>` provides keyboard nav; D-22 wraps transitions in reduced-motion guard. |
| GSD Workflow Enforcement | CLAUDE.md | Phase 10 work is scoped through `/gsd:execute-phase` after planning. |
| Mermaid for diagrams (precedent) | CLAUDE.md | Not applicable to Phase 10 (no diagrams in gallery). |
| EXIF-scrubbed gallery (v2.0 invariant) | PROJECT.md Key Decisions | Phase 10 upgrades source-side scrub into a CI build gate (D-23). |
| Image filename casing rule (Pitfall 14, Phase 7 P01 echo) | `.planning/codebase/CONVENTIONS.md` / PITFALLS.md | `[[resources]]` `src` and `name` MUST byte-match the filenames in `content/gallery/photos/`. The 18 photos include `.jpg`, `.JPG`, and `.jpeg` extensions — DO NOT normalize. |
| `body.page-{type}` CSS scoping pattern | `.planning/codebase/CONVENTIONS.md` | All new gallery rules prefix `body.page-gallery`; D-21 forbids generic class names. |
| BEM-like naming, kebab-case CSS custom properties | `.planning/codebase/CONVENTIONS.md` | `.gallery-lightbox-img`, `.gallery-lightbox-close`, etc. (D-21). |
| IIFE pattern for JS chrome | `.planning/codebase/CONVENTIONS.md` | `lightbox.js` matches the `baseof.html` end-of-body IIFE shape (D-14). |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Frontmatter authoring (caption / alt / weight) | Content (markdown) | — | `[[resources]]` blocks live in `content/gallery/index.md` — Hugo's documented page-bundle metadata pattern. |
| Photo ordering (deterministic) | Build-time (Hugo template) | — | `sort (.Resources.Match "photos/*") "Params.weight"` runs at `hugo --minify`; output HTML is deterministic. NO client-side reordering. |
| Image processing (thumb / full) | Build-time (Hugo `image.Process`) | — | `Resize 600x webp q75` (thumb) and `fit 1200x1200 webp q78` (full) run at build; processed `.webp` files served from `_gen/images/`. |
| Masonry layout (visual flow) | Browser CSS (column-count) | — | Pure CSS; no JS measurement. `break-inside: avoid` keeps `<a>` cards intact across columns. |
| Lightbox modal (open / close / focus trap / Esc) | Browser native (`<dialog>` `showModal()`) | — | Browser provides focus trap, Esc binding, top-layer rendering, `aria-modal="true"`, focus restoration — no manual implementation. |
| Lightbox content swap | Browser JS (vanilla IIFE) | DOM (`data-` attrs) | `lightbox.js` reads `a.href` / `a.dataset.caption` / `a.dataset.alt` and mutates `<img src>`/`<img alt>`/`<figcaption>` text. |
| Prev/next navigation | Browser JS | DOM (sibling walk) | DOM order = weight order (D-04 + D-16). JS reads `Array.from(grid.children).indexOf(a)` and walks sibling indices. |
| Touch swipe | Browser JS (`touchstart`/`touchend`) | — | 50 px deltaX threshold; ~20 LOC inline in lightbox.js. |
| Body scroll lock | Browser JS | — | `document.body.style.overflow = 'hidden'` save/restore on dialog open/close (Pitfall 8 explicit gate). |
| Backdrop blur | Browser CSS (`::backdrop` + `@supports`) | — | Pure CSS; progressive enhancement via `@supports (backdrop-filter: blur(12px))`. Fallback `rgba(16,15,15,0.85)` always shipped. |
| EXIF privacy gate (build-side) | CI (GitHub Actions + exiftool) | Source-side authoring discipline | `[imaging.exif] disableLatLong = true` in `hugo.toml` strips lat/lng during processing; CI step asserts source files have no GPS/Make/Model/Serial *before* Hugo runs. |
| CLS prevention | Build-time (Hugo `width`/`height` emission) | Browser (aspect-ratio inference) | Hugo emits intrinsic `width`/`height`; modern browsers translate to implicit `aspect-ratio` reservation. |

---

## Standard Stack

### Core (existing, LOCKED — listed for verification)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Hugo Extended | 0.157.0 | Static site generator + image processing pipeline | Pinned in `.github/workflows/deploy.yml:25` `[VERIFIED: deploy.yml read]`. Built-in `image.Process` covers all gallery image needs `[VERIFIED: hugo.toml + gallery/single.html read]`. |
| Goldmark with `unsafe = true` | (Hugo 0.157.0 bundled) | Markdown renderer that allows raw HTML | Already enabled in `hugo.toml:13-15` `[VERIFIED]`. Gallery markup lives in template, not markdown — `unsafe` not strictly required for Phase 10 but already on. |
| Vanilla CSS | — | Single stylesheet at `themes/minimal/static/css/style.css` | All v2.0 styling lives here under `:root` / `:root[data-theme="dark"]` token blocks. Phase 10 extends; no second stylesheet. `[VERIFIED: file read]` |
| Vanilla JS (ES6+) | native | Inline `<head>` IIFE + end-of-body IIFE in `baseof.html` | Same pattern reused for `lightbox.js`. No bundler, no transpiler. `[VERIFIED: baseof.html read]` |

### v3.0 Additions (no new packages — all native primitives)

| Pattern | Spec / Browser Support | Purpose | Confidence |
|---------|----------------------|---------|------------|
| Native `<dialog>` element + `dialog.showModal()` | Chrome 37+, Edge 79+, Firefox 98+, Safari 15.4+ — fully shipped 2024 `[CITED: developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog]` | Lightbox container with native focus trap, Esc, top-layer, `aria-modal` | HIGH |
| `::backdrop` pseudo-element + `backdrop-filter: blur()` | 92–95% global support; Safari 17+ unprefixed; Safari 9–16 requires `-webkit-backdrop-filter` `[CITED: caniuse.com/css-backdrop-filter]` | Blurred backdrop behind lightbox | HIGH |
| CSS `column-count` + `break-inside: avoid` | Stable in every browser since IE10 (zero risk in 2026) `[CITED: developer.mozilla.org/en-US/docs/Web/CSS/column-count]` | Masonry-style gallery preserving aspect ratios | HIGH |
| Hugo page-resource frontmatter `[[resources]]` with `params.{caption,alt,weight}` | Hugo 0.31+ stable; 0.157.0 is far ahead `[CITED: gohugo.io/content-management/page-resources/]` | One source of truth for per-photo metadata | HIGH |
| Hugo template `sort` over `Resources.Match` | Hugo `/functions/collections/sort/` accepts `(coll, key)` form `[CITED: gohugo.io/functions/collections/sort/]` | Deterministic ordering by `Params.weight` | HIGH (verified by Hugo docs) |
| Hand-authored inline SVG icons (Lucide visual language) | — | Chevron-left / chevron-right / X for lightbox buttons; matches existing footer GitHub + Instagram icons `[VERIFIED: footer.html read]` | HIGH (in-codebase precedent) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Native `<dialog>` lightbox | PhotoSwipe / GLightbox / Tobii / Slightbox / Lightbox2 | Adds 5–40 KB JS; reimplements what `<dialog>` does natively; **REJECTED** by REQUIREMENTS Out of Scope. |
| CSS `column-count` masonry | CSS Grid Level 3 `grid-template-rows: masonry` | Safari-only in 2026 `[CITED: css-tricks.com/masonry-layout-is-now-grid-lanes/]`; **REJECTED** by REQUIREMENTS Out of Scope. |
| CSS `column-count` masonry | JS Masonry library (Macy.js, Masonry.js, Isotope, Bricks.js, packery) | 5–20 KB runtime + FOUC risk + reflow on resize; **REJECTED**. CSS column-count sufficient for 18 photos. |
| Hand-authored Lucide SVGs | `lucide` / `lucide-static` npm package | Adds Node toolchain to a pure-Hugo project; **REJECTED**. Three SVG paths inline. |
| `[[resources]]` frontmatter for captions | Sidecar `.md` per photo | Splits caption authoring across 18 files vs. 1; **REJECTED** by REQUIREMENTS Locked Decisions. |
| `[[resources]]` frontmatter | YAML data file at `data/gallery.yaml` | Divorces caption from photo, breaks page-bundle co-location; **REJECTED**. |
| Author-controlled `weight` ordering | `collections.Shuffle` build-time | Non-deterministic across builds (Hugo issue #5641 `[CITED]`); breaks reproducible deploys; **REJECTED**. |
| Author-controlled `weight` ordering | Client-side shuffle on load | Causes layout reflow + CLS risk + breaks deep-links/screenshots; **REJECTED**. |

**Installation:**

```bash
# Zero new packages. Phase 10 adds zero npm dependencies, zero build tools, zero Hugo modules.
# CI step adds one apt package on ubuntu-latest:
#   apt-get install -y libimage-exiftool-perl
# This is added to .github/workflows/deploy.yml, not committed as a runtime dependency.
```

**Version verification:** No new npm packages — Phase 10 is platform-native primitives only. Hugo 0.157.0 is already pinned `[VERIFIED: deploy.yml:25]`. Browser primitives (`<dialog>`, `backdrop-filter`, `column-count`) verified against caniuse / MDN as of 2026.

---

## Architecture Patterns

### System Architecture Diagram

```
                       Author edits content/gallery/index.md
                                       │
                                       │ [[resources]] frontmatter blocks
                                       │   src, name, params.{caption, alt, weight}
                                       ▼
                               hugo --minify
                                       │
                       ┌───────────────┼─────────────────┐
                       │               │                 │
                       ▼               ▼                 ▼
              gallery/single.html  image.Process    [imaging.exif]
              { range (sort        Resize 600x →    disableLatLong
                .Resources.Match   $thumb.webp      strips lat/lng
                "photos/*")        fit 1200x1200 →
                "Params.weight" }  $full.webp
                       │               │
                       │               ▼
                       │         resources/_gen/images/*.webp
                       ▼
              public/gallery/index.html
              ├── <a class="gallery-item"
              │      href="$full.webp"
              │      data-caption="…"
              │      data-alt="…">
              │     <img src="$thumb.webp"
              │          width="600"
              │          height="N"
              │          loading="lazy"|"eager"
              │          alt="">
              │   </a>  × 18
              ├── <dialog id="gallery-lightbox">…</dialog>
              └── <script src="js/lightbox.js" defer>

                                       │
                                       │ Browser parses HTML
                                       ▼
                          DOMContentLoaded fires
                                       │
                              lightbox.js IIFE binds
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
                ▼                      ▼                      ▼
     click on .gallery-item    keydown on dialog    touchstart/touchend
                │                      │                      │
                │ e.preventDefault()   │ Esc | ← | →          │ deltaX > 50
                ▼                      ▼                      ▼
     mutate dialog content      navigate prev/next     navigate prev/next
     dialog.showModal()         (DOM-walk siblings)    (same handler)
     body.style.overflow=hidden
                │
                ▼
     User sees centered <dialog>
     (browser focus-traps Tab natively)
     ::backdrop blur (or rgba fallback)
                │
                │ Esc | X click | backdrop click
                ▼
     dialog.close() event
     body.style.overflow restored
     focus returns to <a> trigger (browser-native)


CI path (independent of build/render):
.github/workflows/deploy.yml
        │
        ▼
  apt-get install libimage-exiftool-perl
        │
        ▼
  exiftool -GPS:all -Make -Model -SerialNumber
    content/gallery/photos/*.{jpg,JPG,jpeg,JPEG}
        │
        ▼
  exit 1 if any forbidden field appears → fail build
  exit 0 otherwise → proceed to hugo --minify
```

### Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| Frontmatter authoring | `content/gallery/index.md` | Holds 18 `[[resources]]` blocks (`src`/`name`/`params`) — single source of truth for caption/alt/weight per photo. |
| Gallery template | `themes/minimal/layouts/gallery/single.html` | Renders sorted `<a class="gallery-item">` thumbnails + `<dialog>` markup + deferred `<script>` loader. |
| Render-image hook | `themes/minimal/layouts/_default/_markup/render-image.html` | NOT touched by Phase 10. Gallery uses `Resources.Match`, not markdown image references. |
| Lightbox JS | `themes/minimal/static/js/lightbox.js` (NEW) | Click/keydown/touch handlers; mutates `<dialog>` content; manages body scroll lock. |
| Stylesheet | `themes/minimal/static/css/style.css` | Hosts `/* === Gallery — Masonry === */` and `/* === Gallery — Lightbox === */` blocks. All new rules under `body.page-gallery`. |
| Site config | `hugo.toml` | NOT modified. `[imaging.exif] disableLatLong = true` (lines 34-36) verified retained. |
| Photos directory | `content/gallery/photos/` | NOT modified. 18 EXIF-scrubbed photos reused as-is. |
| CI workflow | `.github/workflows/deploy.yml` | Gains `Verify EXIF scrub` step before/after Hugo build (planner picks placement). |
| Base layout | `themes/minimal/layouts/_default/baseof.html` | NOT modified. `body.page-{Type}` (line 26) auto-emits `page-gallery` for `type: "gallery"`. |

### Recommended Project Structure (post-Phase 10)

```
content/gallery/
├── index.md                ← MODIFIED: 18 [[resources]] blocks added
└── photos/                 ← UNCHANGED (18 photos, EXIF-scrubbed at source)
    ├── 20210710_132418.jpg
    ├── DSC09782.JPG
    ├── DSC09784.JPG
    ├── IMG_0256.jpeg
    ├── IMG_1288.JPG
    ├── IMG_1299.JPG
    ├── IMG_1499.jpeg
    ├── IMG_1646.jpeg
    ├── IMG_2009.jpeg
    ├── IMG_5685_Original.JPG
    ├── IMG_6546.jpeg
    ├── IMG_7828.jpeg
    ├── IMG_8113.jpg
    ├── 5dc795b8-3921-45b8-a651-5b434e405259.jpg
    ├── 60130366-e95c-48a9-b8cd-aa38090c02c2.jpg
    ├── 7eb72991-8aac-44e7-92f7-f71968357ceb.jpg
    ├── 98562fcd-4559-4d91-8020-48ac5dbc9610.jpg
    └── f2e6acbb-7e38-4235-aade-b23a22622596.jpg

themes/minimal/
├── layouts/
│   └── gallery/
│       └── single.html     ← MODIFIED: sort + Resize + data-* + <dialog> + <script>
└── static/
    ├── css/
    │   └── style.css       ← MODIFIED: Gallery section rewrite + new Lightbox block
    └── js/
        └── lightbox.js     ← NEW (~80 LOC IIFE)

.github/workflows/
└── deploy.yml              ← MODIFIED: + Verify EXIF scrub step

hugo.toml                   ← UNCHANGED (verify [imaging.exif] retained)
```

`[VERIFIED: ls of content/gallery/photos/ — 18 files, mixed case]`

### Pattern 1: Hugo Page-Resource Frontmatter

**What:** Per-photo metadata via `[[resources]]` array in `content/gallery/index.md`. Each block targets one photo by exact filename match.

**When to use:** Any per-resource Hugo metadata (caption, alt, weight, ordering hints) within a page bundle.

**Example (D-01):**
```toml
+++
title = "Gallery"
type  = "gallery"
[build]
  publishResources = false

[[resources]]
src  = "photos/IMG_0256.jpeg"
name = "photos/IMG_0256.jpeg"
[resources.params]
caption = "Late summer evening on the descent — golden hour, no filter."
alt     = "Hohe Tauern ridgeline at sunset, mountains receding into haze"
weight  = 10

[[resources]]
src  = "photos/DSC09782.JPG"
name = "photos/DSC09782.JPG"
[resources.params]
caption = "Dachstein traverse, bivvy at sunrise."
alt     = "Sunrise over snow-covered Alpine ridge with bivouac sack in foreground"
weight  = 20
+++
```

**Note on YAML alternative:** CONVENTIONS.md says blog frontmatter is YAML. Hugo accepts both for `[[resources]]`; TOML is more idiomatic for the bracketed-array shape. The existing `content/gallery/index.md` uses YAML (`---` delimiters with `build: { publishResources: false }`). The planner can stay YAML or switch to TOML — both work. **Recommendation:** stay YAML to match existing file format:

```yaml
---
title: "Gallery"
type: "gallery"
build:
  publishResources: false
resources:
  - src: "photos/IMG_0256.jpeg"
    name: "photos/IMG_0256.jpeg"
    params:
      caption: "Late summer evening on the descent — golden hour, no filter."
      alt: "Hohe Tauern ridgeline at sunset, mountains receding into haze"
      weight: 10
  - src: "photos/DSC09782.JPG"
    name: "photos/DSC09782.JPG"
    params:
      caption: "Dachstein traverse, bivvy at sunrise."
      alt: "Sunrise over snow-covered Alpine ridge with bivouac sack in foreground"
      weight: 20
---
```

**Source:** `[CITED: gohugo.io/content-management/page-resources/]` for `[[resources]]` shape; `[VERIFIED: existing content/gallery/index.md uses YAML]`.

### Pattern 2: Hugo `sort` over `Resources.Match`

**What:** Sort a Hugo collection by a key path (including `Params.<field>`).

**When to use:** Any deterministic ordering of a Resources collection by frontmatter.

**Example (D-04):**
```go-html-template
{{ with .Resources.Match "photos/*" }}
  {{ $total := len . }}
  {{ range $idx, $photo := (sort . "Params.weight") }}
    ...
  {{ end }}
{{ end }}
```

**Note on syntax:** Hugo's `sort` function accepts `(collection, sortBy, sortOrder)`. The `sortBy` argument supports dotted paths into resource params (e.g., `"Params.weight"`). Default order is ascending.

**Source:** `[CITED: gohugo.io/functions/collections/sort/]` (HIGH). Pattern verified against existing Hugo gallery tutorials.

**`[ASSUMED]` caveat:** if Hugo 0.157.0 changed the `sort` parameter form (e.g., requires `"params.weight"` lowercase or struct field `"Weight"` capitalized), the planner should add a smoke-test build as the first verification gate. Multiple Hugo community examples use `"Params.weight"` form — most likely correct. If the build fails with "no such field", try `"Params.Weight"` or `".Params.weight"` permutations.

### Pattern 3: Native `<dialog>` Lightbox (single-element, mutated in place)

**What:** One `<dialog>` element in the DOM, content swapped per click. Browser provides focus trap, Esc, top-layer, `aria-modal`, focus restoration.

**When to use:** Any modal/lightbox UX where modern browser support is acceptable.

**Example (D-08, D-09, D-20):**
```html
<dialog id="gallery-lightbox" aria-label="Photo viewer">
  <button type="button" class="gallery-lightbox-close" aria-label="Close gallery">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
    </svg>
  </button>
  <button type="button" class="gallery-lightbox-prev" aria-label="Previous photo">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="m15 18-6-6 6-6"/>
    </svg>
  </button>
  <img class="gallery-lightbox-img" src="" alt="" />
  <figcaption class="gallery-lightbox-caption"></figcaption>
  <button type="button" class="gallery-lightbox-next" aria-label="Next photo">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="m9 18 6-6-6-6"/>
    </svg>
  </button>
</dialog>
```

**Source:** `[CITED: developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog]` for `showModal()` semantics; `[CITED: lucide.dev/icons/x]`, `[CITED: lucide.dev/icons/chevron-left]`, `[CITED: lucide.dev/icons/chevron-right]` for SVG path data (Lucide visual language; paths are MIT-licensed and copied inline, not installed as a package).

### Pattern 4: CSS `column-count` Masonry

**What:** Multi-column CSS layout where items flow top-to-bottom-then-next-column. Pairs with `break-inside: avoid` to keep cards intact.

**When to use:** Visual gallery layouts where DOM-order ≠ visual reading order is acceptable (Pitfall 4 trade-off).

**Example (D-07):**
```css
body.page-gallery .gallery-grid {
  column-count: 3;
  column-gap: 1rem;
  margin: 0;
}

@media (min-width: 600px) and (max-width: 899px) {
  body.page-gallery .gallery-grid { column-count: 2; }
}

@media (max-width: 600px) {
  body.page-gallery .gallery-grid { column-count: 1; }
}

body.page-gallery .gallery-item {
  display: block;
  break-inside: avoid;
  margin-bottom: 1rem;
  line-height: 0;        /* kill baseline gap below <img> — preserve from v2.0 */
}

body.page-gallery .gallery-img {
  width: 100%;
  height: auto;          /* aspect-ratio reservation via width/height attrs */
  display: block;
  border-radius: var(--radius-soft);  /* discretion — Phase 9 token available */
}
```

**Source:** `[CITED: developer.mozilla.org/en-US/docs/Web/CSS/column-count]`, `[CITED: css-tricks.com/piecing-together-approaches-for-a-css-masonry-layout/]`.

### Pattern 5: Backdrop Blur with `@supports` Progressive Enhancement

**What:** Blur effect ships only when supported; opaque rgba is the always-present fallback.

**When to use:** Any visual enhancement that's expensive on low-end GPUs (Pitfall 10).

**Example (D-12):**
```css
/* Default fallback — always shipped */
body.page-gallery dialog#gallery-lightbox::backdrop {
  background: rgba(16, 15, 15, 0.85);
}

/* Progressive enhancement when backdrop-filter supported */
@supports (backdrop-filter: blur(12px)) {
  body.page-gallery dialog#gallery-lightbox::backdrop {
    background: rgba(16, 15, 15, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);  /* Safari <17 */
  }
}
```

**Source:** `[CITED: developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter]` for property semantics; `[CITED: caniuse.com/css-backdrop-filter]` for `-webkit-` prefix requirement.

### Pattern 6: Lightbox IIFE (vanilla JS chrome pattern)

**What:** Self-executing function expression that binds DOM event listeners on `DOMContentLoaded` (or after `defer` parses).

**When to use:** Page-scoped JS chrome with no global scope leakage.

**Example (D-14, D-15) — sketch, not final:**
```javascript
// themes/minimal/static/js/lightbox.js
(function () {
  const dialog = document.getElementById('gallery-lightbox');
  if (!dialog) return;  // not on a gallery page — early return

  const grid = document.querySelector('.gallery-grid');
  const img = dialog.querySelector('.gallery-lightbox-img');
  const caption = dialog.querySelector('.gallery-lightbox-caption');
  const closeBtn = dialog.querySelector('.gallery-lightbox-close');
  const prevBtn = dialog.querySelector('.gallery-lightbox-prev');
  const nextBtn = dialog.querySelector('.gallery-lightbox-next');
  if (!grid || !img || !caption || !closeBtn || !prevBtn || !nextBtn) return;

  const items = Array.from(grid.children);  // sibling array, sorted by weight
  const total = items.length;
  let activeIdx = 0;
  let savedOverflow = '';

  function show(idx) {
    activeIdx = ((idx % total) + total) % total;  // modulo with negative wrap
    const a = items[activeIdx];
    img.src = a.href;
    img.alt = a.dataset.alt || '';
    caption.textContent = a.dataset.caption || '';
    caption.hidden = !a.dataset.caption;
    dialog.setAttribute('aria-label', `Photo ${activeIdx + 1} of ${total}`);
  }

  function open(idx) {
    show(idx);
    savedOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialog.showModal();
  }

  function close() {
    dialog.close();
  }

  // Restore body scroll on close (browser fires `close` event automatically)
  dialog.addEventListener('close', () => {
    document.body.style.overflow = savedOverflow;
  });

  // Bind thumbnail clicks
  items.forEach((a, idx) => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      open(idx);
    });
  });

  // Buttons
  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', () => show(activeIdx - 1));
  nextBtn.addEventListener('click', () => show(activeIdx + 1));

  // Backdrop click closes (D-10)
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) close();
  });

  // Keyboard navigation
  dialog.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(activeIdx - 1);
    else if (e.key === 'ArrowRight') show(activeIdx + 1);
    // Esc handled natively by <dialog>
  });

  // Touch swipe (D-18) — 50 px deltaX threshold
  let touchStartX = 0;
  dialog.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });
  dialog.addEventListener('touchend', (e) => {
    const deltaX = e.changedTouches[0].screenX - touchStartX;
    if (Math.abs(deltaX) >= 50) {
      if (deltaX < 0) show(activeIdx + 1);
      else show(activeIdx - 1);
    }
  }, { passive: true });
})();
```

**Source:** Pattern verified against existing `baseof.html` end-of-body IIFE `[VERIFIED: baseof.html:34-58]` and `<dialog>` API at `[CITED: developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement]`.

### Anti-Patterns to Avoid

- **Anti-pattern: Generic CSS class names (`.lightbox`, `.modal`, `.close`, `.prev`, `.next`).** Why bad: leaks across pages. **Instead:** prefix `.gallery-lightbox-*` (D-21).
- **Anti-pattern: Hard-coded `fill="#…"` or `stroke="#…"` on inline SVG paths.** Why bad: doesn't recolor with theme (Pitfall 3). **Instead:** `stroke="currentColor"` and `fill="none"` — same as footer icons.
- **Anti-pattern: Pre-loading lightbox fulls.** Why bad: blows ≤ 2 MB first-paint budget (Pitfall 11). **Instead:** browser loads on click only.
- **Anti-pattern: Reading `<img src>` from the clicked thumbnail.** Why bad: returns the thumb URL (low-res), not the full. Or returns transparent placeholder if lazy-load (Pitfall 7). **Instead:** read `a.href` (D-19, D-15 step 1).
- **Anti-pattern: DIV-based modal with manual focus trap.** Why bad: reimplements what `<dialog>` does natively. **Instead:** native `<dialog>` (D-08).
- **Anti-pattern: Bumping full quality from q78 to q82.** Why bad: introduces a third quality tier; milestone-context drift (Pitfall 11). **Instead:** keep q78 (D-06).
- **Anti-pattern: Filename normalization (lower-casing `.JPG` → `.jpg`).** Why bad: Hugo's `Resources.GetMatch` is case-sensitive (Phase 7 P01 echo, Pitfall 14). **Instead:** byte-match the filenames in `content/gallery/photos/` (preserves `.JPG` and `.JPEG` cases).

---

## Hugo Frontmatter Schema (REQ GALLERY-01)

The 18 photos in `content/gallery/photos/` MUST each have a `[[resources]]` (or YAML `resources:` array element) entry. Filename casing is preserved verbatim — `[VERIFIED: ls of content/gallery/photos/]`:

| # | Filename | Notes |
|---|----------|-------|
| 1 | `20210710_132418.jpg` | Datetime-named (camera default) |
| 2 | `5dc795b8-3921-45b8-a651-5b434e405259.jpg` | UUID-named |
| 3 | `60130366-e95c-48a9-b8cd-aa38090c02c2.jpg` | UUID-named |
| 4 | `7eb72991-8aac-44e7-92f7-f71968357ceb.jpg` | UUID-named |
| 5 | `98562fcd-4559-4d91-8020-48ac5dbc9610.jpg` | UUID-named |
| 6 | `DSC09782.JPG` | Sony camera (uppercase ext) |
| 7 | `DSC09784.JPG` | Sony camera (uppercase ext) |
| 8 | `f2e6acbb-7e38-4235-aade-b23a22622596.jpg` | UUID-named |
| 9 | `IMG_0256.jpeg` | iOS (lowercase `.jpeg`) |
| 10 | `IMG_1288.JPG` | iOS (uppercase `.JPG`) |
| 11 | `IMG_1299.JPG` | iOS (uppercase `.JPG`) |
| 12 | `IMG_1499.jpeg` | iOS (lowercase `.jpeg`) |
| 13 | `IMG_1646.jpeg` | iOS (lowercase `.jpeg`) |
| 14 | `IMG_2009.jpeg` | iOS (lowercase `.jpeg`) |
| 15 | `IMG_5685_Original.JPG` | iOS (uppercase) |
| 16 | `IMG_6546.jpeg` | iOS (lowercase `.jpeg`) |
| 17 | `IMG_7828.jpeg` | iOS (lowercase `.jpeg`) |
| 18 | `IMG_8113.jpg` | iOS (lowercase `.jpg`) |

**Schema for each entry (YAML-flavored):**
```yaml
- src: "photos/<exact-filename>"     # match casing byte-for-byte
  name: "photos/<exact-filename>"    # Hugo uses `name` to bind metadata
  params:
    caption: "1–2 sentence story (optional, can be empty)"
    alt: "Concrete description for screen readers (REQUIRED per D-03)"
    weight: <integer>                # author-curated; smaller = earlier
```

**Authoring guidance for the planner / author:**
- The author iterates after first build to find the order they like (per Claude's Discretion in CONTEXT.md). Initial weights can be `10, 20, 30, …` (10-stride) so re-ordering doesn't require renumbering everything.
- `caption` may be empty for photos where the author has no story to tell (D-02 graceful empty).
- `alt` MUST NOT be empty. Per D-03, the lightbox image is primary content of the dialog and screen-reader users need a description.
- A grep verification step at end of Wave 1: `grep -c "alt:" content/gallery/index.md` should equal 18.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Modal / lightbox container | DIV with class-toggle | Native `<dialog>` + `dialog.showModal()` | Browser provides focus trap, Esc, top-layer, `aria-modal`, focus restoration — for free. W3C APA explicitly says focus-trap utilities are obsolete with `<dialog>` `[CITED: css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/]`. |
| Focus trap | Manual `Tab` keydown handler | Native `<dialog>` `showModal()` | Browser-native. Listed under D-08 as a reason for `<dialog>` choice. |
| Esc-to-close | Manual `keydown` listener | Native `<dialog>` `showModal()` | Browser-native. |
| Focus restoration on close | Save `document.activeElement`, restore | Native `<dialog>` `showModal()` | Browser-native (returns focus to the element that called `showModal()`). |
| Aspect-ratio reservation for `<img>` | `aspect-ratio: attr(width) / attr(height)` (or fixed CSS) | `<img width="X" height="Y">` from Hugo `image.Process` | Modern browsers translate `width`/`height` attrs into implicit aspect-ratio reservation. Hugo emits these from `$thumb.Width` / `$thumb.Height`. |
| Photo ordering | JS sort on `DOMContentLoaded` | Hugo template `sort` at build time | Build determinism. Client-side sort causes layout reflow + CLS regression. |
| Caption rendering | Markdown processor on `Params.caption` | Plain `<figcaption>{{ . }}</figcaption>` | Captions are 1-2 sentences (REQ-04). Markdown is over-engineering and adds XSS surface. |
| EXIF stripping | Custom Python script | `[imaging.exif] disableLatLong = true` (already in `hugo.toml`) + `exiftool` CI gate | Hugo strips lat/lng during processing. CI verifies source files are also clean. Two layers, both proven. |
| Masonry layout | JS measurement library (Macy.js / Masonry.js) | CSS `column-count` + `break-inside: avoid` | Pure CSS, no FOUC, no resize reflow, zero JS. Sufficient for 18 photos. |
| Backdrop blur fallback handling | Feature-detect via JS | CSS `@supports (backdrop-filter: blur())` | Pure CSS progressive enhancement; no JS. |
| Touch swipe gesture detection | Library (Hammer.js / Swiper) | ~20 LOC inline `touchstart`/`touchend` deltaX | 50 px threshold per D-18. No edge cases for an image-viewer. |

**Key insight:** Phase 10 is essentially a *substitution* exercise — every "hard" problem (modal, focus trap, masonry, blur, swipe) maps to a 2026-native browser primitive. The only place where custom code is necessary is the ~40-LOC content-swap logic in `lightbox.js`. The rest is `<dialog>`, CSS, and Hugo template.

---

## Common Pitfalls

The full PITFALLS.md catalog covers 22 pitfalls; the ten most relevant to Phase 10 (as called out in CONTEXT.md):

### Pitfall 4: CLS spike from masonry without explicit aspect-ratio

**What goes wrong:** Switching from uniform `fill 600x400` to width-only `Resize 600x` produces variable per-photo heights. If `<img>` lacks `width` and `height` attributes, every image load shifts the layout below it.

**How to avoid (D-05, D-24):**
- Hugo `image.Process "Resize 600x webp q75"` returns intrinsic dims at build time. Emit `width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"` on every `<img>` (already in v2.0 template at gallery/single.html:17-18).
- Modern browsers (Chrome 79+, Safari 14+, Firefox 71+) translate these into implicit `aspect-ratio` reservation. Pair with `.gallery-img { width: 100%; height: auto; }`.
- **Verification gate:** Lighthouse CLS < 0.1 on deployed `/gallery/` (D-24). HUMAN-UAT item if Lighthouse can't run automatically.

**Pitfall 4 trade-off (acknowledged):** `column-count` flows column-by-column, so visual reading order ≠ DOM order. ACCEPTABLE for visual gallery (no semantic reading order); keyboard tab order matches DOM order which equals `weight` order.

### Pitfall 5: Random masonry order changes on every build

**Already mitigated by D-04** — author-controlled `params.weight` is deterministic. No `Math.random`, no `collections.Shuffle`, no client-side sort.

### Pitfall 6: Caption authoring drift — silent missing captions

**Already mitigated by D-02 / D-03 split:** `caption` is optional with graceful empty rendering; `alt` is required by author convention. Build does NOT enforce, but a verification grep step in Wave 5 asserts every `[[resources]]` block has `alt`.

### Pitfall 7: Lightbox lazy-load conflict — opens placeholder

**How to avoid (D-19):** JS reads `a.href` (the full-image URL emitted by Hugo `image.Process "fit 1200x1200 webp q78"`), NOT `a.querySelector('img').src` (the thumb URL). Progressive enhancement: with JS disabled, `<a href>` still serves the full image as a separate page navigation.

### Pitfall 8: Focus trap missing / Esc not closing / scroll not locked

**How to avoid (D-08, D-11):** Native `<dialog>` + `showModal()` provides focus trap + Esc natively. Manual scroll lock via `document.body.style.overflow = 'hidden'` save/restore (the one piece `<dialog>` doesn't do). All three behaviors covered.

### Pitfall 9: prefers-reduced-motion on lightbox transitions

**How to avoid (D-22):** Wrap all new transitions in `@media (prefers-reduced-motion: no-preference)`. Same pattern as `style.css:50-56` body transition `[VERIFIED: file read]`. Reduced-motion users see instant open/close.

### Pitfall 10: backdrop-filter performance on low-end devices

**How to avoid (D-12):** `@supports`-gated blur with always-present rgba fallback. Pitfall 10's recommendation to "default to flat, gate blur" is partially overridden by ROADMAP success #3 which mandates blur — D-12 satisfies both by *always* shipping rgba and *additionally* shipping blur where supported. HUMAN-UAT may flag jank on a 3-year-old Android; if so, post-phase remediation drops blur.

### Pitfall 11: Page weight blowout — pre-fetching fulls

**How to avoid (D-06):** No `<link rel="preload">`, no `<link rel="prefetch">`, no JS warmup on dialog open. Browser loads each full only when user clicks the thumbnail. q78 stays canonical (do not bump to q82).

### Pitfall 12: alt text dropped from lightbox primary image

**How to avoid (D-03):** Thumbnail `<img>` keeps `alt=""` (decorative inside `aria-label`-ed `<a>`); lightbox `<img>` reads `alt="{{ $photo.Params.alt }}"` via `a.dataset.alt`. Author convention: every `[[resources]]` entry MUST include `alt`.

### Pitfall 13: Lightbox displays full image with EXIF reintroduced

**How to avoid (D-23):** Two-layer gate.
- Layer 1: `[imaging.exif] disableLatLong = true` in `hugo.toml:34-36` `[VERIFIED: file read]`. Hugo strips lat/lng during processing.
- Layer 2: NEW CI step in `deploy.yml` runs `exiftool -GPS:all -Make -Model -SerialNumber content/gallery/photos/*.{jpg,JPG,jpeg,JPEG}` and fails the build on any forbidden field.

### Pitfall 14: Filename casing mismatches

**How to avoid:** `[[resources]]` `src` and `name` MUST byte-match the filenames in `content/gallery/photos/`. The 18 photos include both `.jpg`, `.JPG`, `.jpeg` extensions (Phase 7 P01 echo) — DO NOT normalize. Build-time grep verification: every `[[resources]]` `src` value resolves to an existing file.

### Pitfall 17: Generic class names leaking across pages

**How to avoid (D-21):** All new lightbox/masonry CSS scoped under `body.page-gallery`. Use `.gallery-lightbox-*` prefix. Forbidden generic names: `.lightbox`, `.modal`, `.close`, `.prev`, `.next`. Lint check: `grep -E '^\\.(lightbox|modal|close|prev|next)' themes/minimal/static/css/style.css` should return zero results.

---

## Code Examples

### Gallery template — sort + Resize + data-attrs + dialog (replaces gallery/single.html)

```go-html-template
{{ define "main" }}
  <article>
    <div class="page-header">
      <h1 class="page-title">{{ .Title }}</h1>
    </div>
    {{ with .Resources.Match "photos/*" }}
      <div class="gallery-grid">
        {{ $total := len . }}
        {{ range $idx, $photo := (sort . "Params.weight") }}
          {{ $thumb := $photo.Process "Resize 600x webp q75" }}
          {{ $full  := $photo.Process "fit 1200x1200 webp q78" }}
          <a class="gallery-item"
             href="{{ $full.RelPermalink }}"
             aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size"
             data-caption="{{ $photo.Params.caption }}"
             data-alt="{{ $photo.Params.alt }}">
            <img class="gallery-img"
                 src="{{ $thumb.RelPermalink }}"
                 width="{{ $thumb.Width }}"
                 height="{{ $thumb.Height }}"
                 loading="{{ if lt $idx 3 }}eager{{ else }}lazy{{ end }}"
                 {{ if eq $idx 0 }}fetchpriority="high"{{ end }}
                 {{ if ge $idx 3 }}decoding="async"{{ end }}
                 alt="">
          </a>
        {{ end }}
      </div>

      <dialog id="gallery-lightbox" aria-label="Photo viewer">
        <button type="button" class="gallery-lightbox-close" aria-label="Close gallery">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
          </svg>
        </button>
        <button type="button" class="gallery-lightbox-prev" aria-label="Previous photo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <img class="gallery-lightbox-img" src="" alt="" />
        <figcaption class="gallery-lightbox-caption" hidden></figcaption>
        <button type="button" class="gallery-lightbox-next" aria-label="Next photo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </dialog>

      <script src="{{ "js/lightbox.js" | absURL }}" defer></script>
    {{ end }}
  </article>
{{ end }}
```

`[VERIFIED: based on existing gallery/single.html, modified per D-04, D-05, D-09, D-19, D-20, D-28]`

### CI step — `.github/workflows/deploy.yml` addition

```yaml
      - name: Verify EXIF scrub on gallery photos
        run: |
          sudo apt-get install -y libimage-exiftool-perl
          set -e
          # exiftool exits 0 even on no matches; we grep its output for forbidden fields.
          OUTPUT=$(exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber \
            content/gallery/photos/ 2>&1 || true)
          if echo "$OUTPUT" | grep -iE 'GPS Latitude|GPS Longitude|Make|Model|Serial' >/dev/null; then
            echo "ERROR: forbidden EXIF fields found in content/gallery/photos/"
            echo "$OUTPUT"
            exit 1
          fi
          echo "EXIF scrub verified — no GPS / Make / Model / Serial fields."
```

**Placement note:** Insert between `Checkout` and `Build with Hugo` so the gate runs before Hugo processes the photos. CONTEXT.md leaves placement to the planner. `[CITED: tools.suckless.org/exiftool/]` for `-GPSLatitude` / `-GPSLongitude` field names; `[ASSUMED]` exact `exiftool` output format on field-present detection — planner should run a smoke test locally to verify the grep pattern triggers correctly before committing.

### CSS — Gallery section rewrite (style.css `/* === Gallery === */` block)

```css
/* === Gallery === */
body.page-gallery .site-wrapper {
  max-width: 1100px;
}

/* Masonry layout — replaces v2.0 uniform grid (D-07) */
body.page-gallery .gallery-grid {
  column-count: 3;
  column-gap: 1rem;
  margin: 0;
}

@media (min-width: 600px) and (max-width: 899px) {
  body.page-gallery .gallery-grid { column-count: 2; }
}

body.page-gallery .gallery-item {
  display: block;
  break-inside: avoid;
  margin-bottom: 1rem;
  line-height: 0;        /* kill baseline gap below <img> */
  border-radius: var(--radius-soft);  /* discretion — Phase 9 token */
}

body.page-gallery .gallery-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

body.page-gallery .gallery-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: var(--radius-soft);
}

/* === Gallery — Lightbox === */
body.page-gallery dialog#gallery-lightbox {
  border: none;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  max-width: min(92vw, 1200px);
  max-height: 92vh;
  border-radius: var(--radius-soft);
  /* Center via the user-agent-default behavior of <dialog> + showModal */
}

/* Backdrop fallback (always shipped) — D-12, D-13 */
body.page-gallery dialog#gallery-lightbox::backdrop {
  background: rgba(16, 15, 15, 0.85);
}

/* Backdrop progressive enhancement — D-12 */
@supports (backdrop-filter: blur(12px)) {
  body.page-gallery dialog#gallery-lightbox::backdrop {
    background: rgba(16, 15, 15, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }
}

body.page-gallery .gallery-lightbox-img {
  display: block;
  max-width: 100%;
  max-height: calc(100vh - 8rem);
  object-fit: contain;
  margin: 0 auto;
}

body.page-gallery .gallery-lightbox-caption {
  display: block;
  padding: 0.75rem 1rem 1rem;
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  text-align: center;
}

body.page-gallery .gallery-lightbox-caption[hidden] {
  display: none;
}

body.page-gallery .gallery-lightbox-close,
body.page-gallery .gallery-lightbox-prev,
body.page-gallery .gallery-lightbox-next {
  position: absolute;
  background: transparent;
  border: none;
  color: var(--text);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-soft);
  /* Hit target ≥ 44×44 — WCAG 2.5.5 (Pitfall 2 echo) */
  min-width: 2.75rem;
  min-height: 2.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

body.page-gallery .gallery-lightbox-close { top: 0.5rem; right: 0.5rem; }
body.page-gallery .gallery-lightbox-prev  { left: 0.5rem; top: 50%; transform: translateY(-50%); }
body.page-gallery .gallery-lightbox-next  { right: 0.5rem; top: 50%; transform: translateY(-50%); }

@media (prefers-reduced-motion: no-preference) {
  body.page-gallery dialog#gallery-lightbox {
    transition: opacity 150ms ease;
  }
  body.page-gallery .gallery-lightbox-close:hover,
  body.page-gallery .gallery-lightbox-prev:hover,
  body.page-gallery .gallery-lightbox-next:hover {
    color: var(--accent);
    transition: color 150ms ease;
  }
}

@media (max-width: 600px) {
  body.page-gallery .gallery-grid { column-count: 1; }
}
```

**Note:** the `.gallery-grid` rule already lives at `style.css:316-321` in the file `[VERIFIED]`. The mobile rule at `@media (max-width: 600px)` is the existing block at `style.css:535` `[VERIFIED]`; new `column-count: 1` rule joins it.

---

## Runtime State Inventory

> Phase 10 is a feature build, not a rename / refactor / migration. The following inventory is included for completeness given the gallery touches existing photos.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — gallery has no database, no Mem0, no Redis, no n8n. The 18 photos in `content/gallery/photos/` carry only filesystem metadata (EXIF), already scrubbed at source per v2.0 Phase 6 invariant. `[VERIFIED: file system + hugo.toml]` | None — verified by `ls` and `hugo.toml` inspection. |
| Live service config | None — site is static, hosted on GitHub Pages. No runtime services to reconfigure. | None. |
| OS-registered state | None — no scheduled tasks, no daemons, no system services touched by Phase 10. | None. |
| Secrets / env vars | None — Phase 10 introduces zero secrets. `HUGO_VERSION` and `HUGO_ENVIRONMENT` env vars in `deploy.yml:25,39` are unchanged. | None. |
| Build artifacts | Hugo's `resources/_gen/images/` will regenerate WebP outputs the first time `gallery/single.html` runs with the new `Resize 600x` directive (the file naming hash changes). The old `_gen/images/*hu*.webp` blobs from `fill 600x400` will be orphaned but harmless — Hugo caches them; CI rebuilds skip stale entries. | Optional: planner may add a `git rm -r resources/_gen/images/` line to a post-deploy clean-up commit, OR leave the cache to age out naturally. Either is acceptable; the served `_gen` paths are content-hashed so no stale URLs ship. |

**Nothing else found:** State explicitly confirmed by reading `hugo.toml`, `deploy.yml`, and the gallery directory structure.

---

## Environment Availability

Phase 10 has minimal external-tool dependencies — Hugo (already pinned), `exiftool` (CI-installed). No databases, no services, no runtimes beyond Hugo Extended.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Hugo Extended | All build steps; `image.Process` thumb/full pipeline | ✓ (pinned in CI) | 0.157.0 `[VERIFIED: deploy.yml:25]` | — |
| GitHub Actions `ubuntu-latest` runner | CI build + EXIF gate | ✓ | latest | — |
| `apt-get install libimage-exiftool-perl` | NEW — D-23 EXIF gate step | ✓ on ubuntu-latest by `apt-get install` | (apt package, ~10 MB install) `[CITED: packages.ubuntu.com/jammy/libimage-exiftool-perl]` | If the install ever breaks, fall back to a Python `Pillow.ExifTags` script — but the Perl `exiftool` is the canonical tool for this domain and unlikely to break. |
| Local Hugo install (developer) | Pre-commit smoke build | ✗ (per CLAUDE.md: "Hugo is NOT installed locally") | — | Develop via Docker (`klakegg/hugo:0.157.0-ext-alpine`), or rely on CI for builds. **Planner note:** if a local smoke test is part of any verification gate, the planner should call out the Docker path — otherwise builds happen only in CI. |
| Lighthouse CLI | CLS verification (REQ GALLERY-08, D-24) | ✗ (not in CI) | — | Manual Lighthouse run in browser DevTools after deploy → HUMAN-UAT item per D-24. |
| Browser (touch device) | Touch swipe verification (REQ GALLERY-07) | ✗ (no automated emulator) | — | Manual mobile test → HUMAN-UAT item. |
| Screen reader (VoiceOver / NVDA / Orca) | A11y verification (REQ GALLERY-06) | ✗ (no automated CI gate) | — | Manual test → HUMAN-UAT item. |

**Missing dependencies with no fallback:** None. All build-blocking dependencies are already available or installable via apt.

**Missing dependencies with fallback:** Lighthouse, mobile browser, screen reader — these become HUMAN-UAT items in `10-HUMAN-UAT.md` per D-26 Wave 5. Pattern matches Phase 6 + 9 deferred-UAT precedent in STATE.md.

---

## Validation Architecture

> Skipped per `.planning/config.json` `workflow.nyquist_validation: false` `[VERIFIED]`.

This phase has no automated unit / integration test suite. Verification gates are:

- **Build success:** `hugo --minify` exits 0 in CI (existing gate; deploy.yml).
- **EXIF gate:** new `Verify EXIF scrub` step in deploy.yml exits 0 (D-23).
- **Frontmatter completeness:** Wave 5 grep — every `[[resources]]` block has `alt` (D-03 author convention).
- **CSS scoping lint:** `grep -E '^\\.(lightbox|modal|close|prev|next)' style.css` returns zero (D-21).
- **CLS:** Lighthouse `/gallery/` < 0.1 → HUMAN-UAT item (D-24).
- **All visual / interactive gates:** consolidated in `10-HUMAN-UAT.md` written in Wave 5.

---

## Security Domain

> `.planning/config.json` does not set `security_enforcement` — treat as enabled. Phase 10 is a personal static-site gallery refactor; the security surface is small but real (EXIF privacy + XSS via lightbox).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Static site; no auth. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | All gallery content is public. |
| V5 Input Validation | yes (limited) | Lightbox only opens hrefs from the page's own `.gallery-item` elements (DOM-internal); never trusts URL params, query strings, or `location.hash`. The data-attrs (`data-caption`, `data-alt`) are written server-side by Hugo from frontmatter — author-controlled, not user-derived. |
| V6 Cryptography | no | No crypto. |
| V7 Error Handling | no (no logging) | Static site. |
| V8 Data Protection | yes | EXIF privacy: D-23 two-layer gate (Hugo `disableLatLong` + CI `exiftool` check). |
| V9 Communication | yes (HTTPS) | GitHub Pages serves via HTTPS; no Phase 10 change. |
| V12 File Upload | no | No uploads; photos committed via git. |

### Known Threat Patterns for Hugo + vanilla JS gallery

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| EXIF GPS leak via gallery photos | Information Disclosure | D-23: source-side scrub (existing) + CI exiftool gate (NEW). |
| XSS via lightbox `data-caption` containing HTML | Tampering | Hugo's default template output escapes HTML by default; `<figcaption>{{ . }}</figcaption>` and `data-caption="{{ $photo.Params.caption }}"` both produce escaped attribute / text content `[CITED: gohugo.io/templates/introduction/]`. JS uses `caption.textContent = …` (NOT `innerHTML`) — verified in the example IIFE. |
| Reflected XSS via crafted URL | Tampering / Spoofing | Lightbox JS NEVER reads from `location.hash`, `location.search`, or `URLSearchParams`. All content sources are DOM-internal `<a>` elements emitted by Hugo. |
| `markup.goldmark.renderer.unsafe = true` allows raw HTML in markdown | Tampering | Acknowledged in `hugo.toml` `[VERIFIED]`. Phase 10 does not author HTML in markdown — gallery content lives in template + frontmatter. The `unsafe` flag remains a project-wide trust-the-author contract. |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `fill 600x400 Smart webp q75` (uniform crop) | `Resize 600x webp q75` (preserve aspect) | Phase 10 (D-05) | Masonry layout possible; CLS guarantee preserved via Hugo `width`/`height` emission. |
| Full-page navigation to `$full.RelPermalink` | Native `<dialog>` lightbox | Phase 10 (D-08) | Browser focus-trap + Esc + scroll-lock + aria-modal for free; removes a page transition. |
| CSS `display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` | CSS `column-count: 3` (responsive 3/2/1) | Phase 10 (D-07) | Photos breathe; aspect ratios preserved. |
| Source-side EXIF scrub by author convention | Source-side scrub + CI `exiftool` gate | Phase 10 (D-23) | Defensive against regression on new photos. |
| Per-photo metadata: none (only filename) | `[[resources]]` frontmatter `params.{caption,alt,weight}` | Phase 10 (D-01) | Captions, alt-text, deterministic order. |

**Deprecated / outdated:**
- Lightbox JS libraries (PhotoSwipe, GLightbox, Tobii, Slightbox, Lightbox2): obsolete since `<dialog>` shipped in Safari 15.4 (March 2022). W3C APA explicitly states focus-trap utilities are no longer needed `[CITED: css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/]`.
- CSS Grid Level 3 `grid-template-rows: masonry`: still Safari-only in 2026. Don't ship.
- Hugo `collections.Shuffle` for "randomized" galleries: non-deterministic across builds (Hugo issue #5641). Author-controlled `weight` is the deterministic alternative.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Hugo `sort (.Resources.Match "photos/*") "Params.weight"` is the correct syntax for the `sort` function over a `Resources` collection. Multiple community examples and Hugo docs confirm `sort coll key` form, but the exact case of `Params.weight` (capital `P`) vs `params.weight` (lowercase) can vary across Hugo versions. | Pattern 2, gallery template example | Build fails with "no such field" error. **Mitigation:** First Wave 2 verification step — run a smoke `hugo --minify` build immediately after the template edit. If it errors, try lowercase `"params.weight"`. Both are documented somewhere in Hugo history. |
| A2 | `exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber <dir>` produces output that contains the literal strings "GPS Latitude" / "GPS Longitude" / "Make" / "Model" / "Serial" when those fields are present, and emits no such strings when absent. | CI step example | Grep pattern misfires (false negative or false positive). **Mitigation:** Author should run the command locally against a known-tagged file before committing the workflow change to verify the output format. Alternatively, use `exiftool -if 'defined($GPSLatitude) or defined($Make)' -filename` which exits non-zero when any tag is present. |
| A3 | Hugo `image.Process "Resize 600x webp q75"` syntax is identical to the v2.0 `Process "fill 600x400 Smart webp q75"` (same directive grammar). The Hugo docs at `[CITED: gohugo.io/methods/resource/resize/]` document `Resize "WIDTHxHEIGHT [filter] [bgcolor]"`; "600x" (width-only) is documented as a valid form. | D-05 thumb directive | Build fails; the `Process` method may use a different name for the resize action. **Mitigation:** Hugo docs explicitly show width-only syntax `Resize "300x"`. Verify in CI on first build. |
| A4 | The lightbox image (full-size WebP from `fit 1200x1200 webp q78`) is < 400 KB on average so 18 fulls × 250 KB ≈ 4.5 MB total per-session is acceptable per project's ≤ 2 MB *first-paint* budget (which is a paint-time, not session-time, budget). | § Pitfall 11 mitigation | If a single full exceeds 400 KB and many users open many photos in one session, transfer is heavy but not budget-violating since first-paint stays at thumbs only. **Mitigation:** Pitfall 11 suggests a build-time check on individual full size; planner can add this as a verification step (`find public/gallery -name '*.webp' -size +400k`). |
| A5 | The `body.page-gallery` body class is auto-emitted by `baseof.html:26` for `type: "gallery"` content. CONTEXT.md asserts this `[CITED: CONTEXT.md § Reusable Assets]`; baseof.html `[VERIFIED]` shows `<body class="page-{{ .Type | default "default" }}">`. Hugo's `.Type` for `content/gallery/index.md` with `type: "gallery"` frontmatter resolves to `"gallery"`. | D-21 CSS scoping | If `.Type` resolves differently in Hugo 0.157.0, scoping breaks. **Mitigation:** Verify on first build via DevTools — `body` element's class attribute should be `class="page-gallery"`. |

If this table is empty: not applicable — every assumption is flagged.

---

## Open Questions

1. **Hugo `sort` argument case (Assumption A1)**
   - What we know: `sort` accepts dotted-path key names; multiple community examples use `"Params.weight"`.
   - What's unclear: whether Hugo 0.157.0 specifically requires lowercase `"params.weight"` or accepts both.
   - Recommendation: Wave 2 first task is the template edit with `"Params.weight"`; if `hugo --minify` errors, try `"params.weight"`. Both forms are documented; one will work.

2. **YAML vs TOML frontmatter for `resources` array**
   - What we know: existing `content/gallery/index.md` is YAML; existing blog posts are YAML.
   - What's unclear: whether `[[resources]]` (TOML) or `resources:` (YAML array) reads better for 18 entries.
   - Recommendation: stay YAML to match existing file format. CONTEXT.md uses TOML examples but Hugo accepts both — file-format consistency wins.

3. **Plan count: 3 (D-27 default) or 4 (split EXIF CI)**
   - What we know: D-27 suggests 3, D-26 lists 5 internal waves.
   - What's unclear: whether the EXIF CI step is independent enough to warrant its own plan.
   - Recommendation: 3 plans match Phase 9 precedent and tight coupling between waves. The EXIF CI step is small (~10 LOC) and can ride with `10-02 Template + CSS + EXIF CI`. If the planner finds Wave 2 too crowded, split to 4 — but no blocker.

4. **`touchcancel` defensive handling**
   - What we know: D-18 specifies `touchstart` + `touchend` only.
   - What's unclear: whether `touchcancel` (e.g., user receives a phone call mid-swipe) needs a no-op handler to clear `touchStartX`.
   - Recommendation: defensive — add `touchcancel` listener that resets `touchStartX = 0`. ~3 LOC. Listed under Claude's Discretion in CONTEXT.md.

5. **Hover state for lightbox buttons**
   - What we know: D-22 wraps transitions in `prefers-reduced-motion`; default has none.
   - What's unclear: whether buttons should change color on hover (vs. just on focus-visible).
   - Recommendation: add a subtle `color: var(--accent)` on hover gated by `prefers-reduced-motion: no-preference`. Matches site's existing accent-on-hover convention. ~3 LOC.

---

## Sources

### Primary (HIGH confidence — verified)

- `[VERIFIED: file read]` `themes/minimal/layouts/gallery/single.html` — current 28-line template
- `[VERIFIED: file read]` `themes/minimal/layouts/_default/baseof.html` — `body.page-{Type}` auto-emit, IIFE precedent
- `[VERIFIED: file read]` `themes/minimal/layouts/partials/footer.html` — Lucide-style 18×18 SVG precedent
- `[VERIFIED: file read]` `themes/minimal/static/css/style.css` — gallery section at lines 311-339, single mobile breakpoint at line 535, `--radius-soft: 12px` at line 18
- `[VERIFIED: file read]` `content/gallery/index.md` — current 7-line frontmatter
- `[VERIFIED: file read]` `hugo.toml` — `[imaging.exif] disableLatLong = true` at lines 34-36
- `[VERIFIED: file read]` `.github/workflows/deploy.yml` — Hugo 0.157.0 pinning, build/deploy structure
- `[VERIFIED: file read]` `.planning/codebase/CONVENTIONS.md` — single-CSS-file rule, BEM-like naming, page-prefix scoping
- `[VERIFIED: ls of content/gallery/photos/]` 18 photos with case-preserved filename mix (`.jpg`/`.JPG`/`.jpeg`)
- `[VERIFIED: file read]` `.planning/REQUIREMENTS.md` GALLERY-01..GALLERY-09 + Locked Decisions
- `[VERIFIED: file read]` `.planning/research/SUMMARY.md`, `STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md` (4-13), `FEATURES.md`
- `[VERIFIED: file read]` `.planning/phases/10-gallery-lightbox-masonry-captions/10-CONTEXT.md` — 28 locked decisions
- `[VERIFIED: file read]` `.planning/PROJECT.md` constraints (Flexoki, vanilla JS, no flash, accessible, ≤ 2 MB)
- `[VERIFIED: file read]` `.planning/STATE.md` — milestone progress, deferred items
- `[VERIFIED: file read]` `.planning/config.json` — `nyquist_validation: false`

### Secondary (HIGH confidence — citation, not in-session verification)

- `[CITED: developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog]` — `<dialog>` element, `showModal()`, focus trap, Esc, top-layer
- `[CITED: developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/::backdrop]` — `::backdrop` pseudo-element
- `[CITED: developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter]` — `backdrop-filter` property
- `[CITED: developer.mozilla.org/en-US/docs/Web/CSS/column-count]` — CSS multi-column layout
- `[CITED: caniuse.com/css-backdrop-filter]` — 92%+ global support; Safari 17+ unprefixed; Safari 9–16 needs `-webkit-`
- `[CITED: gohugo.io/content-management/page-resources/]` — `[[resources]]` frontmatter, `params`, glob `src`
- `[CITED: gohugo.io/methods/resource/resize/]` — `Resize "WIDTHxHEIGHT [filter]"` width-only behavior
- `[CITED: gohugo.io/methods/resource/fit/]` — `Fit "WIDTHxHEIGHT"` aspect-ratio preservation
- `[CITED: gohugo.io/functions/collections/sort/]` — `sort COLLECTION KEY [SORT_ORDER]`
- `[CITED: gohugo.io/templates/introduction/]` — Hugo template auto-escaping
- `[CITED: github.com/gohugoio/hugo/issues/5641]` — `collections.Shuffle` non-determinism
- `[CITED: css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/]` — W3C APA position
- `[CITED: css-tricks.com/masonry-layout-is-now-grid-lanes/]` — CSS Grid Level 3 `masonry` Safari-only in 2026
- `[CITED: css-tricks.com/piecing-together-approaches-for-a-css-masonry-layout/]` — `column-count` + `break-inside: avoid` pattern
- `[CITED: lucide.dev/icons/x]`, `[CITED: lucide.dev/icons/chevron-left]`, `[CITED: lucide.dev/icons/chevron-right]` — Lucide visual language path data (MIT)
- `[CITED: aleksandrhovhannisyan.com/blog/how-to-open-and-close-html-dialogs/]` — backdrop-click close pattern
- `[CITED: sarasoueidan.com/blog/accessible-icon-buttons/]` — `aria-label` on button + `aria-hidden` on inner SVG
- `[CITED: packages.ubuntu.com/jammy/libimage-exiftool-perl]` — apt package availability on `ubuntu-latest`

### Tertiary (LOW confidence — design reference only)

- `[CITED: tylerkarow.com/gallery]` — visual masonry + lightbox North Star (Squarespace; no code lifted)
- `[CITED: web.dev/articles/building/a-theme-switch-component]` — accessibility pattern reference for icon buttons (not directly Phase 10, ICON-related)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every primitive verified against MDN / caniuse / Hugo docs; in-codebase precedents (footer SVG icons, baseof IIFE, render-image hook) confirm patterns
- Architecture: HIGH — file-modification matrix matches existing layered architecture exactly; D-26 wave order is internally consistent and respects file dependencies
- Pitfalls: HIGH — every Phase 10 pitfall (4-13, 17) maps to a CONTEXT.md decision that mitigates it; trade-offs (Pitfall 4 column-count, Pitfall 10 backdrop-filter) are explicitly acknowledged with planner-visible mitigations
- Hugo `sort` syntax: MEDIUM — most likely `"Params.weight"` form, but Hugo's case sensitivity in this specific corner has bitten projects before (A1)
- exiftool field names / output format: MEDIUM — fields are well-known but the exact grep pattern needs a smoke test (A2)

**Research date:** 2026-05-04
**Valid until:** 2026-06-04 (stable platform primitives + locked CONTEXT.md decisions; only refresh if Hugo's `sort` API or `<dialog>` browser support changes materially)

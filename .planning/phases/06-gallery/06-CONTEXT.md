# Phase 6: Gallery - Context

**Gathered:** 2026-04-30
**Status:** Ready for planning
**Mode:** `--auto` — recommended defaults auto-selected; each decision logged inline so the user can audit.

<domain>
## Phase Boundary

A standalone `/gallery/` page rendered as a Hugo **leaf bundle** at `content/gallery/index.md` with the 18 personal photos co-located as page-bundle resources at `content/gallery/photos/`. The page renders a CSS Grid (`repeat(auto-fill, minmax(220px, 1fr))`) of Hugo-processed WebP thumbnails (`fill 600x400 Smart webp q75`); each thumbnail is an `<a>`-wrapped `<img>` linking to a full-size processed WebP rendition (`fit 1600x1600 webp q82`). All processed output is EXIF-scrubbed (zero `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, `Serial*`); the source folder typo `images/galary/` is retired.

**In scope:**
- New leaf bundle at `content/gallery/index.md` with `title: "Gallery"`
- 18 source photos moved from `images/galary/` → `content/gallery/photos/` (page-bundle resources, EXIF-pre-stripped before commit)
- New layout `themes/minimal/layouts/gallery/single.html` — iterates `.Resources.Match "photos/*"`, processes each via Hugo's `image.Process`, emits the grid markup
- New CSS section in `themes/minimal/static/css/style.css` (`.gallery-grid`, `.gallery-item`, `.gallery-img`) with the locked `repeat(auto-fill, minmax(220px, 1fr))` grid + a wider `max-width: 1100px` page canvas scoped via a body-type class
- One-line edit to `themes/minimal/layouts/_default/baseof.html`: add `<body class="page-{{ .Type | default "default" }}">` so gallery CSS can scope via `body.page-gallery`
- New menu entry in `hugo.toml` `[[menu.main]]`: name "Gallery", url "/gallery/", weight 2 (About bumps to weight 3)
- New `[imaging.exif]` block in `hugo.toml`: `disableLatLong = true` (belt-and-suspenders alongside source-side stripping)
- Pre-commit EXIF scrub of all 18 sources via `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original` (one-shot bulk run before move)
- Deletion of `images/galary/` (and verification that `grep -r galary` over `content/`, `themes/`, `hugo.toml` returns zero hits)

**Out of scope:**
- JS lightbox library (PhotoSwipe, Lightbox2, GLightbox, etc.) — REQUIREMENTS § Out of Scope
- Native `<dialog>` lightbox — REQUIREMENTS § Future
- Per-photo captions / front-matter caption arrays — REQUIREMENTS § Future
- Masonry / waterfall layout / infinite scroll / filter UI — REQUIREMENTS § Out of Scope
- AVIF format — Hugo 0.157 image pipeline does not support it (REQUIREMENTS § Out of Scope)
- `<picture>` with multiple `srcset` breakpoints — single 600×400 thumbnail at all viewports (CSS Grid handles responsive sizing via `auto-fill`)
- New blog content / About edits / Phase 7 work
- Renaming the source files — original filenames (DSC09782.JPG, IMG_1646.jpeg, etc.) preserved; Hugo URL-encodes any incidental spaces

</domain>

<decisions>
## Implementation Decisions

### Page Template & Hugo Wiring

- **D-01:** `/gallery/` is a **leaf bundle** at `content/gallery/index.md`. Hugo derives `Type = "gallery"` from the folder name. Front matter is minimal: `title: "Gallery"` only — no `date`, no `draft`, no `summary`, no `description` (mirrors `content/about.md`'s minimal-frontmatter pattern). The 18 photos sit as page-bundle resources at `content/gallery/photos/`, accessible via `.Resources.Match "photos/*"`.
  - `[auto] Page Template — Q: "How does Hugo render /gallery/?" → Selected: "Leaf bundle (content/gallery/index.md) + photos/ subdir as resources" (recommended; idiomatic Hugo, single layout, page-bundle EXIF/processing stays scoped to the gallery page)`
- **D-02:** Layout file is **`themes/minimal/layouts/gallery/single.html`** (NOT a `_default/single.html` conditional). Hugo's lookup order for `Type=gallery` resolves `gallery/single.html` before falling back to `_default/single.html`. Keeps the gallery's bespoke markup (CSS Grid, processed-resource iteration, eager/lazy loading attrs) isolated from the existing single-page template that drives `/about/` and blog posts.
  - `[auto] Layout File — Q: "Where does the gallery template live?" → Selected: "Dedicated layouts/gallery/single.html" (recommended; clean separation, no conditional cruft in _default/)`
- **D-03:** Resource iteration uses **`.Resources.Match "photos/*"`** (glob, not `.ByType "image"`). Glob is more explicit about WHERE the photos live and avoids accidentally pulling in non-photo images that may land in the bundle later (e.g., a hero banner). Sort is the default (alphabetical by filename) — see D-04.
  - `[auto] Resource Selector — Q: ".ByType \"image\" or .Match \"photos/*\"?" → Selected: ".Resources.Match \"photos/*\"" (recommended; explicit, future-proof against non-photo images in the bundle)`

### Photo Ordering

- **D-04:** Photos render in **alphabetical order by filename** — Hugo's default sort for `.Resources.Match`. Deterministic, zero-config, matches the order returned by `ls images/galary/` today. With the existing 18-photo set, this puts numeric-prefixed files (`20210710_…`, `5dc795b8…`, `60130366…`) first, then `DSC*`, then `IMG_*`. No curated `photos:` array in front matter — adding curation is a future-phase concern (it pairs naturally with captions, also deferred).
  - `[auto] Ordering — Q: "Alphabetical, date-based, or curated front-matter array?" → Selected: "Alphabetical by filename (Hugo default)" (recommended; deterministic, no per-photo metadata required)`

### Eager / Lazy Loading & fetchpriority

- **D-05:** **First 3 photos** load `eager`; remaining 15 load `lazy`. The CSS Grid `minmax(220px, 1fr)` yields up to 4 columns at the gallery's 1100 px max canvas, so the above-fold first row spans 3–4 thumbnails on desktop, 2 on tablet, 1 on phone. Eager-loading the first 3 covers the desktop above-fold case without over-fetching on mobile (browsers fetch eager images regardless of viewport, but at 600×400 q75 each thumbnail is ~30–60 KB so 3 eager = ≤ 180 KB worst case — well inside the 2 MB first-paint budget).
  - `[auto] Eager Row — Q: "How many photos load eagerly above the fold?" → Selected: "First 3" (recommended; covers desktop above-fold without over-fetching)`
- **D-06:** **`fetchpriority="high"`** on the **first photo only**. Per-Web.dev guidance, only one above-fold image should be tagged `high` to avoid contention with the CSS download. Photos 2–3 are eager but priority-default; photos 4–18 are `loading="lazy"` (no `fetchpriority` attribute).
  - `[auto] Priority Hint — Q: "fetchpriority='high' on first photo only, first 3, or none?" → Selected: "First photo only" (recommended; matches Web.dev LCP guidance, prevents CSS-vs-image bandwidth contention)`

### Click-Through to Full-Size

- **D-07:** Each thumbnail is **wrapped in an `<a>`** linking to the full-size processed WebP rendition's `.RelPermalink`. No new HTML page, no JS lightbox, no `target="_blank"` (lets the browser back button return to the gallery — same UX as native image viewing). The `<a>` is the click target; the `<img>` inside has no separate event handlers.
  ```html
  {{ $thumb := .Process "fill 600x400 Smart webp q75" }}
  {{ $full  := .Process "fit 1600x1600 webp q82" }}
  <a class="gallery-item" href="{{ $full.RelPermalink }}">
    <img class="gallery-img"
         src="{{ $thumb.RelPermalink }}"
         width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"
         loading="{{ if lt $idx 3 }}eager{{ else }}lazy{{ end }}"
         {{ if eq $idx 0 }}fetchpriority="high"{{ end }}
         alt="">
  </a>
  ```
  - `[auto] Click-Through — Q: "Direct link to full-size WebP, JS modal, or new HTML page?" → Selected: "Direct <a href> to full-size WebP" (recommended; honors REQUIREMENTS § no JS lightbox, simplest, browser-native back button)`

### CSS Grid & Wider Canvas

- **D-08:** Grid markup uses a wrapper `<div class="gallery-grid">` containing 18 `<a class="gallery-item">` children. Grid CSS:
  ```css
  .gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
    margin: 0;
  }
  .gallery-item {
    display: block;
    line-height: 0;       /* kill baseline gap below <img> */
  }
  .gallery-img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 4px;
  }
  ```
  Locks the ROADMAP-specified `repeat(auto-fill, minmax(220px, 1fr))` template verbatim. `gap: 1rem` matches the 1.5 rem header bottom-margin scale already used elsewhere in `style.css`. `line-height: 0` on `.gallery-item` removes the inline-baseline whitespace that would otherwise create vertical gaps in the grid cells.
- **D-09:** **Wider canvas: `max-width: 1100px`** on the gallery page only. At 1100 px content width with `minmax(220px, 1fr)`, the grid renders **4 columns** on a 1100 px canvas and **3 columns** at the 640 px default canvas (preserving the responsive auto-fill behavior on mid-width viewports). 1100 px is conservative enough to stay readable without the page feeling sprawling.
  - `[auto] Canvas Width — Q: "How wide should /gallery/ go?" → Selected: "1100px (4-col desktop, 3-col tablet, 1-col mobile)" (recommended; comfortable photo grid without abandoning the minimal aesthetic)`
- **D-10:** Wider canvas is scoped via **a body-type class** added in `baseof.html`. One-line edit:
  ```html
  <body class="page-{{ .Type | default "default" }}">
  ```
  CSS scopes the override:
  ```css
  body.page-gallery .site-wrapper {
    max-width: 1100px;
  }
  ```
  All other pages keep the existing 640 px `--max-width`. The body-class pattern is also useful for any future page-type-specific styling (Phase 7's About-enrichment may benefit). Alternative approaches (CSS-variable override per page, full-bleed `100vw` hacks) were rejected: the body-class pattern is more discoverable and less prone to specificity bugs.
  - `[auto] Width Scoping — Q: "How to scope wider canvas to /gallery/ only?" → Selected: "body.page-{{ .Type }} class added to baseof.html" (recommended; reusable for Phase 7, no specificity hacks, minimal baseof.html edit)`
- **D-11:** Mobile breakpoint behavior is **unchanged from the existing `@media (max-width: 600px)`** — the grid's `auto-fill` naturally collapses to 1 column at narrow viewports because `minmax(220px, 1fr)` won't fit two 220 px columns in 600 px minus padding. No additional mobile-specific gallery rules required.

### Menu Integration

- **D-12:** Add `[[menu.main]]` entry in `hugo.toml`: `name = "Gallery"`, `url = "/gallery/"`, `weight = 2`. **About bumps to `weight = 3`**. Final order: Blog → Gallery → About. Rationale: the gallery is content-heavy first-class material that fits next to Blog; About is a single page that conventionally sits last.
  - `[auto] Menu Position — Q: "Gallery's place in the nav order?" → Selected: "Blog → Gallery → About (Gallery weight 2, About bumped to 3)" (recommended; content-first nav, About last is conventional)`

### EXIF Stripping (privacy-critical, hard launch gate)

- **D-13:** **Two-pronged EXIF defense:**
  1. **Source-side pre-strip** before committing to `content/gallery/photos/`: run `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original` over all 18 source files. This is a **one-shot manual step** during Phase 6 execution, not a recurring pipeline. Removes the named fields from the JPEG containers.
  2. **Hugo build-side**: `[imaging.exif]` block in `hugo.toml` with `disableLatLong = true` (per ROADMAP success criterion 3). Hugo's `image.Process` re-encodes JPEGs to WebP, which already drops most EXIF as a side effect of format conversion, but `disableLatLong` is the explicit ROADMAP-mandated guard.
  - The combination guarantees: (a) original sources committed to git are clean (auditable via `git show`), (b) Hugo-processed output is also clean (auditable via `exiftool public/gallery/**/*.{webp,jpg}`).
  - `[auto] EXIF Strategy — Q: "Strip at source, in Hugo, or both?" → Selected: "Both: source pre-strip via exiftool + hugo.toml [imaging.exif] disableLatLong" (recommended; belt-and-suspenders, audit-friendly, source files clean in git)`
- **D-14:** **Verification gate (executed during Phase 6 before commit):**
  ```bash
  hugo --minify
  exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber public/gallery/photos/*.{webp,jpg} 2>/dev/null
  # Expected: zero matching field reports across all 18 thumbnails + 18 full-size renditions
  ```
  Failure on any field blocks the phase. Same scrutiny pattern as Phase 5's HUMAN-UAT favicon verification.

### File Locations & Migration

- **D-15:** Source filenames are **preserved** during the move from `images/galary/` to `content/gallery/photos/`. No kebab-case normalization, no extension lowercasing (`.JPG` stays `.JPG`, `.jpeg` stays `.jpeg`). Rationale: minimum churn, preserves traceability to original camera/phone naming, and Hugo's `.Resources.Match` is case-sensitive but extension-agnostic for image-type detection.
  - `[auto] Filename Normalization — Q: "Normalize to lowercase/kebab-case or keep originals?" → Selected: "Keep originals" (recommended; minimum churn, preserves source traceability)`
- **D-16:** **Move strategy: `git mv images/galary content/gallery/photos`** (preserves git history of each photo file), then run the exiftool scrub on the moved files in-place, then `git add` the modified files. Order matters: move first (so git tracks the rename), then scrub (so the EXIF deltas attach to the moved files).
- **D-17:** **`images/galary/` is fully removed** after the move. Verified via:
  ```bash
  test ! -d images/galary
  grep -r galary content/ themes/ hugo.toml || echo "No hits — clean"
  ```
  ROADMAP success criterion 5 makes the absence of any `galary` reference (the typo'd folder name) a hard gate. The correct spelling `gallery` is the only acceptable surface.

### Image Alt Text (a11y)

- **D-18:** All 18 thumbnails carry **`alt=""`** (empty). Per WCAG and Web.dev guidance, decorative images in galleries without informational content should use empty alt to keep screen readers from announcing 18 generic "Personal photo" labels in sequence. Adding curated descriptions is a future-phase concern (it pairs naturally with captions, also deferred).
  - `[auto] Alt Text — Q: "Empty alt, generic 'Personal photo', or curated descriptions?" → Selected: "Empty alt='' (decorative)" (recommended; WCAG-aligned for caption-less galleries, less screen-reader noise)`

### Hugo Image Processing Config

- **D-19:** **No `[imaging]` quality default** in `hugo.toml`. Per-call quality strings (`q75` for thumbnails, `q82` for full-size) are explicit in the Process invocations and easier to audit than a global default. The only `[imaging]` config touched is the `[imaging.exif]` block from D-13.
- **D-20:** **No `srcset` / `<picture>` element** for thumbnails. The CSS Grid's `auto-fill` + `minmax(220px, 1fr)` handles responsive layout; the 600×400 thumbnail is sharp enough on 1× displays at 220–275 px rendered widths and on 2× displays at 110–137 px (where the eye doesn't resolve the difference at typical viewing distance). Per Web.dev: "When in doubt, omit `srcset`." Adding it later is purely additive if metrics show it's needed.

### Build Cache & CI

- **D-21:** Hugo's image processing cache (`resources/_gen/images/`) is already gitignored (verified: `.gitignore` excludes `resources/`). The CI workflow (`.github/workflows/deploy.yml`) sets `HUGO_CACHEDIR` to a runner temp dir — first build after deploy runs all 18 photos × 2 renditions = 36 image-process operations. Cold build expected to add ~10–20 seconds to CI; hot/local builds reuse the cache. No CI workflow edits required for Phase 6.

### Claude's Discretion

- Exact CSS-rule placement in `style.css` — between the existing `/* === Single Post / Page === */` and `/* === Footer === */` sections (a new `/* === Gallery === */` section comment), or appended after `/* === Responsive === */`. Recommend the former — section ordering by content type is the existing convention.
- Whether the `<a class="gallery-item">` wrapper also gets `aria-label="Open full-size photo {{ $idx }}"` for screen-reader clarity. Recommend yes for the case where alt is empty (the link still needs a name) — Claude can finalize the wording during planning.
- Whether to add a tiny `:focus-visible` outline on `.gallery-item` (keyboard navigation through photos). Recommend yes for accessibility parity with the existing `.site-nav a:focus-visible` pattern.
- Whether to add `decoding="async"` alongside `loading="lazy"` on the lazy thumbnails. Web.dev recommends it for off-screen images; cost is one attribute per element. Recommend yes; Claude finalizes during planning.
- Whether to wrap the gallery template's resource iteration in a `{{ with .Resources.Match "photos/*" }}` guard so an empty bundle doesn't break the build. Recommend yes (defensive).
- Whether the page-type body class uses `page-{{ .Type }}` (D-10 default), `t-{{ .Type }}`, or `{{ .Type }}-page` — all functionally equivalent. Recommend `page-{{ .Type }}` per D-10 for self-documenting clarity.
- Whether to verify the build cache cold-start regenerates all 36 renditions correctly by deleting `resources/` locally before the smoke test. Recommend yes — surfaces any platform-specific Hugo image-pipeline issues before they hit CI.
- Whether to commit a `.gitkeep` or `README.md` inside `content/gallery/photos/` if the photos are added in a separate plan-execution step. Probably unnecessary if the photo move + commit happens atomically.
- The exact `exiftool` invocation for the scrub — the recommended invocation in D-13 strips the named fields. Claude can decide whether to additionally pass `-CommonIFD0=` for thoroughness; the verification gate at D-14 catches any leftover.

### Folded Todos

None — no pending todos in STATE.md matched this phase's scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & Requirements
- `.planning/ROADMAP.md` § "Phase 6: Gallery" — phase goal, 5 success criteria (CSS Grid template, Process strings, exiftool privacy gate, weight ceilings, `galary/` retirement), research flag noting empirical thumbnail/quality tuning is recommended
- `.planning/REQUIREMENTS.md` § "Gallery" — GAL-01 (nav reachability), GAL-02 (CSS Grid layout + max-width override), GAL-03 (WebP `Process "fill 600x400 Smart webp q75"`, lazy/eager mix, explicit width/height), GAL-04 (full-size `Process "fit 1600x1600 webp q82"`, no JS lightbox), GAL-05 (≤ 2 MB first-paint, ≤ 3 MB total `public/gallery/`), GAL-06 (zero GPS/Make/Model/Serial via exiftool verification), GAL-07 (move from `images/galary/` to `content/gallery/photos/`, no `galary` references in repo)
- `.planning/REQUIREMENTS.md` § "Future Requirements" — native `<dialog>` lightbox (deferred), per-photo captions (deferred); Phase 6 ships neither
- `.planning/REQUIREMENTS.md` § "Out of Scope" — JS lightbox library (PhotoSwipe, Lightbox2 etc. — REJECTED, conflicts with no-framework constraint), AVIF (REJECTED — Hugo 0.157 doesn't support), masonry/infinite-scroll/filters (REJECTED — doesn't fit minimal aesthetic)
- `.planning/PROJECT.md` § "Constraints" — Hugo static, no JS frameworks, vanilla JS only, performance ceilings via Hugo's image pipeline, no flash on load (theming inheritance — gallery inherits Phase 4's `[data-theme]` automatically since photos are theme-agnostic)
- `.planning/PROJECT.md` § "Key Decisions" — locks: standalone `/gallery/` page in nav (not embedded in About), Hugo image processing for gallery (built-in, WebP only), rename `images/galary/` → `content/gallery/photos/` (move into Hugo content tree)

### Cross-Phase Contracts (incoming)
- `.planning/phases/04-theming-foundation/04-CONTEXT.md` § "D-01" — `[data-theme]` set on `<html>` by head IIFE before stylesheet parse. Gallery page CSS uses `var(--bg)`/`var(--text)`/`var(--border)` for any theme-dependent surfaces (e.g., the optional `.gallery-img { border-radius: 4px }` looks correct against both palettes). Photo content itself is opaque imagery — theme-agnostic.
- `.planning/phases/05-wordmark-favicon-wiring/05-CONTEXT.md` § "Cross-Phase Contracts (outgoing) → To Phase 6" — favicon partial pattern (`partials/favicon.html` included from `baseof.html`) is the precedent for any future `<head>` partials. Phase 6 doesn't add any new head partials.
- `.planning/phases/05.1-swap-wordmark-favicon-to-new-svg-sources/05.1-CONTEXT.md` § "Cross-Phase Contracts (outgoing) → To Phase 6" — inline-SVG-with-`currentColor` is now a validated codebase pattern; if Phase 6 needs a small decorative icon (e.g., an "open in new tab" hint on the click-through link), use the inline SVG + `currentColor` idiom rather than reviving sliced PNGs. Phase 6 ships no such icons in the locked scope, but the pattern is available if needed.

### Codebase Conventions & Files
- `themes/minimal/layouts/_default/baseof.html` (currently 58 lines) — **EDIT (D-10):** add `class="page-{{ .Type | default "default" }}"` to the `<body>` element. One-line edit. All other content unchanged. Note: the current line 26 is `<body>`; it becomes `<body class="page-{{ .Type | default "default" }}">`.
- `themes/minimal/layouts/gallery/single.html` — **NEW.** Page template for the gallery leaf bundle. Iterates `.Resources.Match "photos/*"`, processes each photo at thumbnail (600×400 fill q75) and full-size (1600×1600 fit q82) via Hugo `image.Process`, emits `<a class="gallery-item"><img class="gallery-img" ...></a>` markup with eager/lazy + fetchpriority attributes per D-05/D-06.
- `themes/minimal/static/css/style.css` (currently 320 lines) — **EDIT.** Add `/* === Gallery === */` section block with `.gallery-grid` (display: grid + locked template), `.gallery-item` (display: block, line-height: 0, focus-visible outline), `.gallery-img` (width: 100%, height: auto, display: block, border-radius: 4px), and `body.page-gallery .site-wrapper { max-width: 1100px; }` (D-09, D-10). Mobile rules under existing `@media (max-width: 600px)` need no edits — `auto-fill` collapses naturally.
- `content/gallery/index.md` — **NEW.** Leaf bundle index with `title: "Gallery"` only. No date, no draft, no summary.
- `content/gallery/photos/` — **NEW (moved from `images/galary/`).** 18 source JPEGs preserved with original filenames; EXIF pre-stripped via exiftool (GPS:All, Make, Model, SerialNumber, InternalSerialNumber).
- `images/galary/` — **DELETED** (after `git mv` to `content/gallery/photos/`).
- `hugo.toml` (currently 39 lines) — **EDIT.** Two changes: (1) add `[[menu.main]]` block for Gallery (name "Gallery", url "/gallery/", weight 2); (2) bump existing About entry's weight from 2 → 3; (3) add `[imaging.exif]` block with `disableLatLong = true`.
- `.planning/codebase/CONVENTIONS.md` § "HTML Template Conventions" — Hugo Go templates, 2-space indentation, `{{ partial }}` includes, partial conditionals via `{{ with }}` and `{{ if }}` patterns
- `.planning/codebase/CONVENTIONS.md` § "CSS Conventions" — Flexoki palette (gallery uses `var(--border)` for any subtle dividers if needed), `kebab-case` class names with `.site-` / `.page-` / `.post-` prefixes (gallery introduces `.gallery-*` family, fits the convention), section comments `/* === Section Name === */`, single stylesheet
- `.planning/codebase/STRUCTURE.md` § "Where to Add New Code → New Static Page" — current pattern (top-level `content/foo.md` + menu entry); Phase 6 follows this for the page bundle and menu but uses a leaf-bundle directory instead of a single .md file (per the page-bundle convention already used by all blog posts)

### Hugo Documentation (research-flagged for `/gsd-research-phase`)
- Hugo image processing reference — empirical tuning of `Process "fill 600x400 Smart webp q75"` against the actual 18 photos (sources span 150 KB → 7.5 MB, exposure latitude varies wildly) benefits from research: confirm `Smart` crop centroid handles portrait-orientation phone shots, validate q75 lands within the 2 MB first-paint budget, validate `fit 1600x1600` doesn't upscale the smaller landscape shots
- Hugo `[imaging.exif]` config — confirm `disableLatLong` semantics across the WebP encoder vs the JPEG fallback path; verify that re-encoding to WebP additionally drops `Make`/`Model`/`Serial*` fields (this is what makes the source-side exiftool scrub the load-bearing layer for those non-GPS fields)
- Hugo Resources.Match + Process caching — confirm that the per-call quality string (`q75`, `q82`) participates in the cache key so changes to the quality value invalidate just the affected renditions

### Cross-Phase Contracts (outgoing)
- **To Phase 7 (About Enrichment):** the body-type class pattern (`<body class="page-{{ .Type | default "default" }}">` in baseof.html) introduced by Phase 6 D-10 unlocks page-type-specific CSS scoping for free. Phase 7's "richer About layout (second column / photo grid / pull-quote rules)" can scope its CSS via `body.page-about`. The leaf-bundle pattern (`content/gallery/index.md` + `photos/` subdir) is the proven shape Phase 7 mirrors when it converts `content/about.md` → `content/about/index.md`.
- **To future phases:** Hugo image processing pipeline + `[imaging.exif]` privacy config is now a codebase-validated pattern. Future image-heavy pages reuse the `Process "fill WxH Smart webp qN"` thumbnail / `Process "fit MxM webp qN"` full-size idiom with confidence.
- **To future phases:** the page-bundle resource scheme (`content/{section}/{leaf}/photos/`) is the established "many images, one page" pattern. About enrichment (Phase 7) and any future photo-heavy content uses this shape.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`themes/minimal/layouts/_default/baseof.html`** (58 lines) — already structured for `{{ partial "..." . }}` includes (header, footer, favicon). Theme bootstrap IIFE already sets `data-theme` on `<html>` so the gallery inherits theming "for free" (photos themselves are theme-agnostic, but the `.gallery-img { border-radius: 4px }` and any subtle borders pick up the active palette).
- **`themes/minimal/layouts/_default/single.html`** (10 lines) — minimal `<article>` wrapper with `.page-header` + `.page-title` + `.page-content`. Phase 6's `gallery/single.html` can borrow the `<article>` + `.page-header` shell and replace `.page-content` with the `<div class="gallery-grid">` block. Or skip the page-title chrome entirely — the Gallery page may read cleaner without an `<h1>Gallery</h1>` heading above the grid (eliminates the title-vs-photos visual conflict). **Claude's Discretion** — both reasonable; recommend keeping a small `<h1>` for SEO + nav-target context, styled consistently with the existing `.page-title`.
- **`themes/minimal/static/css/style.css`** § Flexoki palette + responsive breakpoint (line 314 `@media (max-width: 600px)`) — gallery rules append into the existing CSS architecture without restructuring.
- **`hugo.toml`** `[menu.main]` entries — adding Gallery follows the existing weight-based pattern; no new top-level config keys required.
- **GitHub Actions deploy workflow** (`.github/workflows/deploy.yml`) — `HUGO_CACHEDIR` already set; image processing cache works in CI without edits.
- **Page-bundle convention** — every blog post under `content/blog/YYYY-MM-DD-slug/` already uses page-bundle resources (images co-located in `images/`). Phase 6 applies the same shape at the section level for the gallery (`content/gallery/index.md` + `photos/`).

### Established Patterns
- **`{{ partial "header.html" . }}` / `{{ partial "footer.html" . }}` for `<body>` chrome** — gallery template inherits these via `baseof.html`'s `{{ block "main" . }}` pattern; no per-page header/footer changes.
- **Hugo Go template conditionals** — `{{ if eq $idx 0 }}fetchpriority="high"{{ end }}` and `{{ if lt $idx 3 }}eager{{ else }}lazy{{ end }}` patterns are already used elsewhere (e.g., `_default/list.html` line 23 `{{ if eq .Section "blog" }}`).
- **Single CSS file** — gallery rules consolidate into `style.css`, no new file.
- **Type-derived layout lookup** — Hugo automatically resolves `layouts/{type}/single.html` when `Type` matches the folder name above `index.md`. `content/gallery/index.md` → `Type=gallery` → `layouts/gallery/single.html` is the layout target. No `layout:` front-matter override needed.
- **Body-class pattern (NEW for Phase 6, available to Phase 7+)** — the `<body class="page-{{ .Type | default "default" }}">` edit is a one-line baseof.html addition that unlocks page-type-specific CSS scoping across the entire codebase. The `default` fallback ensures pages without a Type (the homepage) still emit a valid class.

### Integration Points
- **`content/gallery/index.md`** — NEW leaf bundle. Front matter: `title: "Gallery"` only.
- **`content/gallery/photos/`** — NEW page-bundle resource directory. 18 photos moved from `images/galary/` via `git mv`, then EXIF-scrubbed in place.
- **`themes/minimal/layouts/gallery/single.html`** — NEW. Iterates `.Resources.Match "photos/*"`, calls `image.Process` twice per photo (thumbnail + full-size), emits the grid markup.
- **`themes/minimal/layouts/_default/baseof.html`** — one-line edit: `<body class="page-{{ .Type | default "default" }}">`.
- **`themes/minimal/static/css/style.css`** — append `/* === Gallery === */` section block + `body.page-gallery .site-wrapper { max-width: 1100px; }` override.
- **`hugo.toml`** — three edits: new `[[menu.main]]` for Gallery (weight 2), bump About to weight 3, add `[imaging.exif]` block with `disableLatLong = true`.
- **`images/galary/`** — DELETED after `git mv`.

### Hugo-Specific Notes
- **Image processing cache lives at `resources/_gen/images/`** — gitignored. CI uses a fresh cache (slow first build, fast subsequent). Local dev caches across runs.
- **`.Resources.Match "photos/*"` is glob-based**, returns resources sorted alphabetically by name. No `.Resources.Match "photos/*.jpg"` filter needed — the bundle directory contains only image files.
- **`image.Process "fill 600x400 Smart webp q75"`** — `fill` keeps the destination at exactly 600×400 px (cropping to fit), `Smart` chooses the crop centroid based on entropy/face detection, `webp` is the output format, `q75` is the quality. Hugo 0.157 supports all four (verified via Hugo image processing docs).
- **`image.Process "fit 1600x1600 webp q82"`** — `fit` scales the longest side to ≤ 1600 px (no upscaling, preserves aspect), `webp q82` is the output. The smallest source (`5dc795b8…`, 152 KB at unknown dimensions) is unlikely to upscale; verify during research-phase.
- **EXIF: Hugo's WebP encoder** drops most JPEG EXIF as a side effect of format conversion. The source-side exiftool scrub is the load-bearing guarantee for non-GPS fields (Make, Model, Serial) because Hugo's `[imaging.exif] disableLatLong = true` only handles lat/long.
- **`fetchpriority` attribute** is part of HTML5 (Resource Hints spec), supported in Chrome 102+, Edge 102+, Firefox 132+, Safari 17.2+. Older browsers ignore it gracefully (eager loading still works).
- **Hugo serves `static/`** at site root automatically; the gallery page's CSS is loaded via `baseof.html`'s existing `<link rel="stylesheet" href="{{ "css/style.css" | absURL }}">` — no per-page CSS injection needed.

</code_context>

<specifics>
## Specific Ideas

- **Weight gate (hard launch criterion):** First-paint network transfer for `/gallery/` ≤ 2 MB; total `du -sh public/gallery/` ≤ 3 MB. Verification via Chrome DevTools Network tab (set Disable cache + Slow 3G) on the deployed URL after CI ships. With 600×400 q75 WebPs ranging ~25–60 KB each: 18 thumbnails × ~45 KB avg ≈ 810 KB; lazy-loading reduces first-paint to ~3 thumbnails × ~45 KB ≈ 135 KB. Plenty of headroom.
- **CLS gate (hard launch criterion):** Lighthouse Mobile CLS < 0.1 on `/gallery/`. Structurally guaranteed by `<img width={{ $thumb.Width }} height={{ $thumb.Height }}>` (Hugo provides exact processed-resource dimensions) + the CSS `aspect-ratio` enforcement via the `width: 100%; height: auto` pattern.
- **EXIF gate (hard launch criterion):** `exiftool` over `public/gallery/**/*.{webp,jpg}` after `hugo --minify` reports zero matches for `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, `Serial*`. **Block ship if any field surfaces.**
- **`galary` retirement gate:** `grep -r galary content/ themes/ hugo.toml` returns zero hits. **Block ship on any hit** — the typo'd folder name must not survive.
- **Visual smoke test:** Load `/gallery/` in dark mode (toggle from Phase 4 active), verify the photos read against the dark Flexoki bg without color cast. Verify photos in light mode similarly. Confirm the click-through to full-size opens the rendition cleanly (browser back returns to gallery scrolled correctly).
- **Cold-build smoke:** Delete `resources/` locally, run `hugo --minify`, verify all 36 renditions (18 thumbnails + 18 full-size) generate without error and the build time is acceptable (~10–20 s on the existing repo).
- **Mobile keyboard navigation:** Tab through the grid — `:focus-visible` outlines on `.gallery-item` should make the focused thumbnail clearly visible.
- **Source size sanity:** Largest source `IMG_1646.jpeg` is 7.2 MB; smallest `5dc795b8…` is 152 KB. Hugo processes both into the same 600×400 q75 WebP target, so the thumbnail sizes equalize. Full-size 1600×1600 fit on the 7.2 MB source (likely 4032×3024 from a phone) yields ~600–800 KB; on the 152 KB source (likely 800×600 already) yields no upscale, ~100–150 KB. All within budget.
- **Research flag (from ROADMAP):** Recommend `/gsd-research-phase` during planning to empirically validate the locked Process strings against the actual 18 photos before committing to implementation. Especially: confirm `Smart` crop handles portrait-orientation phone shots without amputating subjects, and confirm q75 / q82 land within the weight ceilings.

</specifics>

<deferred>
## Deferred Ideas

- **Native `<dialog>`-based lightbox** — REQUIREMENTS § Future. Currently click-through navigates to the standalone full-size WebP URL (browser-native back button, no JS). A future v2.x phase could layer a lightweight `<dialog>` modal over the grid for inline full-size viewing without the URL navigation. Pure progressive enhancement — current implementation works without it.
- **Per-photo captions** — REQUIREMENTS § Future. Today: 18 photos with empty alt and no captions. A future phase could add a `photos:` array in `content/gallery/index.md` front matter mapping filename → caption, surface captions under each thumbnail and inside the lightbox (when added). Pairs naturally with curated photo ordering (D-04) — both are "photo metadata" concerns.
- **Per-photo curated ordering** — current alphabetical (D-04) is fine for a 1.0 ship. A `photos:` front-matter array could enable curation; same shape as captions deferral above.
- **`srcset` / `<picture>` for hi-DPI thumbnails** — D-20 omits these; gallery looks fine on 1× and 2× displays at the rendered size. If real-world Lighthouse Mobile reports flag image quality, add a 1200×800 q75 WebP variant via `srcset="thumb.webp 1x, thumb-2x.webp 2x"`. Purely additive — no template restructuring required.
- **AVIF format** — REQUIREMENTS § Out of Scope. Hugo 0.157 doesn't support AVIF in the image pipeline. Revisit when Hugo adds AVIF (likely 0.158+ tracking issue).
- **Hugo render-image hook** for blog post images — Phase 6 isolates the photo-heavy treatment to `/gallery/`, but an opportunistic future improvement is to convert blog post `![alt](images/foo.jpg)` markdown calls into Hugo render-image hooks that auto-process to WebP + lazy-load. Out of scope for Phase 6; would benefit `/about/` (Phase 7) and existing blog posts.
- **Cross-tab gallery scroll-position restore** — irrelevant (no shared state).
- **View-transition API on click-through** — REQUIREMENTS § Future (general theme-toggle deferred); applies here too. Cross-fading thumbnail → full-size would be polish.
- **PWA caching of the gallery** — REQUIREMENTS § Future (`site.webmanifest` deferred). Service workers + image caching would let `/gallery/` work offline; not warranted for v2.0.
- **Filter / search / tag UI** — REQUIREMENTS § Out of Scope. Doesn't fit the minimal aesthetic.
- **Photo metadata sidebar (capture date, location, equipment)** — would expose the very EXIF fields Phase 6 just stripped for privacy. Hard rejection: would need a separate authored-metadata system.

</deferred>

---

*Phase: 06-gallery*
*Context gathered: 2026-04-30*

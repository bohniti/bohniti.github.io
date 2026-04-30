# Phase 6: Gallery - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-30
**Phase:** 06-gallery
**Mode:** `--auto` — Claude auto-selected the recommended option for every gray area without prompting the user. This log preserves the alternatives considered for each so the user can audit and override during planning if any default reads wrong.
**Areas discussed:** Page Template & Hugo Wiring, Photo Ordering, Eager/Lazy Loading & fetchpriority, Click-Through to Full-Size, CSS Grid & Wider Canvas, Width Scoping Approach, Menu Integration, EXIF Stripping, File Locations & Migration, Image Alt Text, Hugo Image Processing Config

---

## Page Template & Hugo Wiring

| Option | Description | Selected |
|--------|-------------|----------|
| Leaf bundle: `content/gallery/index.md` + `photos/` subdir as resources, custom `layouts/gallery/single.html` | Idiomatic Hugo, Type=gallery derived from folder, photos via `.Resources.Match "photos/*"` | ✓ |
| Section/branch bundle: `content/gallery/_index.md` + photos as separate page bundle | More general but adds a layer of indirection — photos aren't naturally `.Resources` of an `_index.md` |  |
| Single `.md` at `content/gallery.md` + photos at `static/gallery/` | Simplest but loses page-bundle resource scheme; `image.Process` doesn't work on `static/` files |  |

**User's choice:** auto → "Leaf bundle + custom layouts/gallery/single.html"
**Notes:** Page-bundle resources are the only path that lets `.Process "fill 600x400 Smart webp q75"` run on the photos. The leaf-bundle layout file (`gallery/single.html`) is resolved by Hugo's Type-based lookup automatically — no `layout:` front-matter override needed.

---

## Photo Ordering

| Option | Description | Selected |
|--------|-------------|----------|
| Alphabetical by filename (Hugo default for `.Resources.Match`) | Deterministic, zero-config, no per-photo metadata | ✓ |
| Date-based (parsing EXIF DateTimeOriginal or filename date prefix) | Chronological feel, but coupling: requires EXIF reads or filename-prefix conventions |  |
| Curated `photos:` array in front matter | User-controlled order, but requires touching front matter for any reordering and pairs with future captions feature |  |

**User's choice:** auto → "Alphabetical by filename"
**Notes:** Adding curation is deferred — pairs naturally with captions, which are a Future Requirement. Today's filenames yield: numeric prefixes first (20210710_…, 5dc795b8…, 60130366…, 7eb72991…, 98562fcd…, DSC09782, DSC09784, f2e6acbb…, IMG_0256, IMG_1288, IMG_1299, IMG_1499, IMG_1646, IMG_2009, IMG_5685, IMG_6546, IMG_7828, IMG_8113).

---

## Eager / Lazy Loading & fetchpriority

| Option | Description | Selected |
|--------|-------------|----------|
| First 3 eager, fetchpriority="high" on first only, rest lazy | Covers desktop above-fold (3-col layout) with minimum bandwidth contention | ✓ |
| First 4 eager, fetchpriority="high" on first 1–2 | Covers 4-col 1100-px layout but over-fetches on mobile |  |
| First 6 eager (full above-fold viewport on tall desktop) | Wasteful on 4-col layout; over-fetches on mobile |  |
| All lazy (no eager) | Defers LCP image, hurts perceived performance |  |

**User's choice:** auto → "First 3 eager, fetchpriority='high' on first only"
**Notes:** Per Web.dev guidance, only one image should carry `fetchpriority="high"` to prevent CSS-vs-image bandwidth contention. Three eager covers the desktop above-fold case (3 columns at 640 px, 4 at 1100 px); the 4th eager would be over-fetching on mid-width viewports.

---

## Click-Through to Full-Size

| Option | Description | Selected |
|--------|-------------|----------|
| `<a href="{{ $full.RelPermalink }}">` direct to processed WebP URL | No JS, browser-native, back button returns to gallery | ✓ |
| Native `<dialog>` modal (vanilla JS) for inline full-size view | Better UX but requires JS — REQUIREMENTS § Future |  |
| Generate per-photo HTML page (`/gallery/photos/IMG_xxx/`) | Adds 18 generated pages; no benefit over direct WebP URL |  |
| `target="_blank"` on the link (open full-size in new tab) | Breaks browser back-button workflow; users dislike forced new tabs |  |

**User's choice:** auto → "Direct `<a href>` to processed WebP URL"
**Notes:** REQUIREMENTS § Out of Scope explicitly forbids JS lightbox libraries. Native `<dialog>` is REQUIREMENTS § Future. Direct URL navigation is the simplest implementation that satisfies the click-to-full-size requirement (GAL-04) without violating any constraint.

---

## CSS Grid & Wider Canvas

| Option | Description | Selected |
|--------|-------------|----------|
| `max-width: 1100px` (4 cols at minmax(220px, 1fr)) | Comfortable photo grid, stays minimalist | ✓ |
| `max-width: 1280px` (5 cols) | More photos per row but feels sprawling on a minimal site |  |
| `max-width: 100vw - 2rem` (true full-bleed) | Maximizes photo density but breaks the site's compact rhythm |  |
| Keep existing `max-width: 640px` (3 cols) | No max-width override — minimal but cramped for 18 photos |  |

**User's choice:** auto → "1100px (4-col desktop, 3-col tablet, 1-col mobile via auto-fill)"
**Notes:** The CSS Grid `auto-fill` behavior gives the responsive-collapse for free. 1100 px is a conservative widening — meaningfully more photo-per-row than the 640 px default without abandoning the site's minimalism.

---

## Width Scoping Approach

| Option | Description | Selected |
|--------|-------------|----------|
| `<body class="page-{{ .Type | default "default" }}">` in baseof.html, scope CSS via `body.page-gallery` | One-line baseof edit, reusable for Phase 7+, no specificity hacks | ✓ |
| CSS-variable override per page via inline `<style>` in template | Inline styles split between template and stylesheet — discoverability hurt |  |
| Full-bleed CSS (`width: 100vw; margin-left: calc(50% - 50vw)`) | Bypasses `.site-wrapper` constraint but creates visual misalignment with header/footer |  |
| Override `--max-width` CSS variable on `:has(.gallery-grid)` | Modern but `:has()` support is browser-version-dependent (Firefox 121+) |  |

**User's choice:** auto → "Body-class via `<body class=\"page-{{ .Type }}\">` in baseof.html"
**Notes:** The body-class pattern unlocks page-type-specific CSS scoping for the entire codebase. Phase 7 (About Enrichment) can scope its richer-layout CSS via `body.page-about` for free. The `default` fallback ensures the homepage (no Type) emits a valid class.

---

## Menu Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Blog → Gallery → About (Gallery weight 2, About bumped to weight 3) | Content-first nav order; About last is conventional | ✓ |
| Blog → About → Gallery (Gallery appended at weight 3) | Adds Gallery without touching About; less visually balanced |  |
| Gallery → Blog → About (Gallery first) | Foregrounds Gallery; doesn't match a content-first hierarchy |  |

**User's choice:** auto → "Blog → Gallery → About"
**Notes:** Standard convention: content collections (Blog, Gallery) before profile pages (About). The About entry's weight bump from 2 → 3 is a minor `hugo.toml` edit.

---

## EXIF Stripping

| Option | Description | Selected |
|--------|-------------|----------|
| Two-pronged: pre-commit `exiftool -GPS:All= -Make= -Model= -Serial*=` + `[imaging.exif] disableLatLong = true` in hugo.toml | Belt-and-suspenders, audit-friendly, sources in git are clean | ✓ |
| Hugo-only: `[imaging.exif] disableExif = true` (strip ALL EXIF) | Simpler config but committed sources still carry EXIF — privacy concern leaks into git history |  |
| Source-side only (no Hugo config) | Misses ROADMAP success criterion 3 which mandates the hugo.toml setting |  |

**User's choice:** auto → "Two-pronged: source-side exiftool scrub + hugo.toml [imaging.exif] disableLatLong"
**Notes:** ROADMAP success criterion 3 explicitly requires the hugo.toml setting. The source-side scrub is the load-bearing layer for `Make`/`Model`/`Serial` (Hugo's `disableLatLong` only handles GPS). Source-clean files in git make the privacy posture auditable via `git show`.

---

## File Locations & Migration

| Option | Description | Selected |
|--------|-------------|----------|
| `git mv images/galary content/gallery/photos`, preserve original filenames, EXIF-scrub in place | Preserves git history, minimum churn, traceable to source | ✓ |
| Move + normalize filenames to kebab-case | Cleaner URLs but loses traceability to source camera/phone naming |  |
| Copy (not move), retain `images/galary/` for archival | Violates ROADMAP success criterion 5 (no `galary` references) |  |

**User's choice:** auto → "git mv with original filenames preserved"
**Notes:** Hugo URL-encodes any incidental spaces in filenames; `.Resources.Match` is glob-based and case-sensitive but extension-agnostic for image type detection.

---

## Image Alt Text

| Option | Description | Selected |
|--------|-------------|----------|
| Empty `alt=""` (decorative) | WCAG-aligned for caption-less galleries; no screen-reader noise | ✓ |
| Generic "Personal photo" repeated 18 times | Adds 18 redundant labels to screen readers — anti-pattern |  |
| Curated descriptions in front-matter array | Best a11y but pairs with captions (deferred) — out of scope |  |

**User's choice:** auto → "Empty alt='' (decorative)"
**Notes:** Per WCAG and Web.dev, decorative gallery images without informational content should use empty alt to keep screen readers from announcing 18 generic labels in sequence. The wrapping `<a>` carries an `aria-label` (Claude's discretion in CONTEXT.md) so the link still has a screen-reader-readable name.

---

## Hugo Image Processing Config

| Option | Description | Selected |
|--------|-------------|----------|
| Per-call quality strings (`q75`, `q82`); only `[imaging.exif] disableLatLong` in hugo.toml | Explicit, auditable, no global default coupling | ✓ |
| Set `[imaging] quality = 75` global default + per-call overrides | Adds a config-vs-call double-source-of-truth — confusion risk |  |
| Add `srcset` / `<picture>` element for 1×/2× DPI thumbnails | Out of scope for v2.0 — the 600×400 q75 thumbnail looks fine on 1× and 2× displays at typical viewing distance |  |

**User's choice:** auto → "Per-call quality strings; only [imaging.exif] disableLatLong"
**Notes:** Web.dev: "When in doubt, omit `srcset`." Adding it later is purely additive if Lighthouse Mobile flags image quality.

---

## Claude's Discretion

The following micro-decisions are deferred to Claude's judgment during planning/execution:

- Whether to include a small `<h1>Gallery</h1>` heading at the top of the gallery page (recommend yes for SEO + nav-target context).
- Whether the `<a class="gallery-item">` wrapper carries `aria-label="Open full-size photo {{ $idx }}"` for screen-reader clarity (recommend yes — the link needs a name when alt is empty).
- Whether to add `:focus-visible` outline on `.gallery-item` for keyboard navigation (recommend yes for parity with `.site-nav a:focus-visible`).
- Whether to add `decoding="async"` on lazy thumbnails (recommend yes per Web.dev).
- Whether to wrap the resource iteration in `{{ with .Resources.Match "photos/*" }}` for empty-bundle defense (recommend yes — defensive).
- Body-class naming: `page-{{ .Type }}` vs `t-{{ .Type }}` vs `{{ .Type }}-page` (recommend `page-{{ .Type }}` for self-documenting clarity).
- Whether to verify the cold-cache rebuild before commit (recommend yes — surfaces platform-specific Hugo image-pipeline issues before CI).
- Whether to delete `resources/_gen/images/` locally after the source rename to ensure a clean rebuild (recommend yes).
- Exact `exiftool` invocation — strip the named fields per D-13; consider adding `-CommonIFD0=` for thoroughness; the verification gate at D-14 catches any leftover.

## Deferred Ideas

- Native `<dialog>`-based lightbox (REQUIREMENTS § Future)
- Per-photo captions (REQUIREMENTS § Future) + curated photo ordering (pairs with captions)
- `srcset` / `<picture>` for hi-DPI thumbnails (purely additive if Lighthouse flags)
- AVIF format (Hugo 0.157 doesn't support — REQUIREMENTS § Out of Scope; revisit when Hugo adds it)
- Hugo render-image hook for blog post images (opportunistic future improvement)
- View-transition API on click-through to full-size (REQUIREMENTS § Future)
- PWA caching of the gallery (REQUIREMENTS § Future)
- Filter / search / tag UI (REQUIREMENTS § Out of Scope — doesn't fit minimal aesthetic)
- Photo metadata sidebar (would expose the very EXIF fields just stripped — hard rejection)

---

*Phase 6 discussion complete in `--auto` mode. CONTEXT.md is the canonical record; this log is for human audit.*

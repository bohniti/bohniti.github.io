# Phase 10: GALLERY — Lightbox + Masonry + Captions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-04
**Phase:** 10-gallery-lightbox-masonry-captions
**Mode:** `--auto` (Claude picked recommended defaults across all gray areas; single-pass)
**Areas discussed:** Authoring schema, Caption optionality, Per-photo alt text, Gallery ordering, Thumb image processing, Full image processing, Masonry layout, Lightbox mechanism, Dialog instances, Backdrop click close, Body scroll lock, Backdrop strategy, Lightbox JS file location, Lightbox IIFE structure, Prev/next data source, Lightbox aria-label, Touch swipe, Progressive enhancement, Lightbox markup, CSS scoping, Reduced motion, EXIF gate, CLS verification, Dialog sizing, Phase sub-task order, Plan granularity hint, Existing markup preservation

---

## Authoring Schema (D-01)

| Option | Description | Selected |
|--------|-------------|----------|
| `[[resources]]` array in `content/gallery/index.md` | TOML array, one entry per photo, individual `params.caption/alt/weight` | ✓ |
| Per-photo `.md` sidecar (ARCHITECTURE alt) | Hugo binds .md to bundle resource of same basename | |
| YAML data file at `data/gallery.yaml` | Externalized config | |

**Auto-selected:** `[[resources]]` frontmatter — locked by REQUIREMENTS.md § Locked Decisions.
**Notes:** Sidecar files split caption authoring across 18 files; data file divorces caption from photo.

---

## Caption Optionality (D-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Required (build-fail on missing) | Pitfall 6's `errorf` Hugo build-fail | |
| Optional with graceful empty | Template `{{ with $photo.Params.caption }}…{{ end }}` | ✓ |

**Auto-selected:** Optional with graceful empty.
**Notes:** REQUIREMENTS-04 + ROADMAP success #3 explicitly require graceful empty.

---

## Per-Photo Alt Text (D-03)

| Option | Description | Selected |
|--------|-------------|----------|
| `params.alt` REQUIRED on every photo | Author convention; thumbnail `alt=""` (decorative), lightbox `<img>` reads `params.alt` | ✓ |
| Skip alt entirely | Use caption as alt fallback | |

**Auto-selected:** REQUIRED `params.alt`.
**Notes:** Lightbox image is primary content (Pitfall 12). Caption ≠ alt (caption is for sighted users, alt is for screen readers).

---

## Gallery Ordering (D-04)

| Option | Description | Selected |
|--------|-------------|----------|
| `params.weight` deterministic | Author-controlled, reproducible builds | ✓ |
| Hugo `collections.Shuffle` | Build-time shuffle | |
| Client-side shuffle on load | JS Fisher-Yates | |
| Filename-alphabetical | Deterministic but no author control | |

**Auto-selected:** `params.weight` — locked by REQUIREMENTS Locked Decisions.
**Notes:** `collections.Shuffle` is non-deterministic (Hugo issue #5641); client-side shuffle reflows post-paint.

---

## Thumb Image Processing (D-05)

| Option | Description | Selected |
|--------|-------------|----------|
| `Resize 600x webp q75` | Width-only, height proportional, preserves aspect ratio | ✓ |
| `fill 600x400 Smart webp q75` (current v2.0) | 3:2 crop, breaks masonry intent | |

**Auto-selected:** `Resize 600x webp q75`.
**Notes:** REQUIREMENTS-02 explicitly says "Hugo Resize 600x webp q75, not fill 600x400".

---

## Full Image Processing (D-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `fit 1200x1200 webp q78` | v2.0 canonical | ✓ |
| Bump to q82 | Milestone context drift | |

**Auto-selected:** Keep q78 — Pitfall 11.

---

## Masonry Layout (D-07)

| Option | Description | Selected |
|--------|-------------|----------|
| CSS `column-count` 3/2/1 breakpoints | Universal browser support | ✓ |
| CSS Grid `grid-template-rows: masonry` | Safari-only in 2026 | |
| JS Pinterest-style with measurement | Adds runtime layout JS, CLS risk | |

**Auto-selected:** column-count.
**Notes:** Locked by REQUIREMENTS-02 + Out of Scope explicit ban on CSS Grid masonry.

---

## Lightbox Mechanism (D-08)

| Option | Description | Selected |
|--------|-------------|----------|
| Native `<dialog>` + `showModal()` | Free focus trap, Esc, aria-modal, top-layer | ✓ |
| DIV-based modal with class toggle | Reimplement everything manually | |

**Auto-selected:** Native `<dialog>`.

---

## Dialog Instances (D-09)

| Option | Description | Selected |
|--------|-------------|----------|
| One `<dialog>` mutated in place | DOM weight constant; JS swaps `<img src>` per click | ✓ |
| One `<dialog>` per photo | 18 dialogs in DOM | |

**Auto-selected:** One mutated in place — STACK research recommendation.

---

## Backdrop Click Close (D-10)

| Option | Description | Selected |
|--------|-------------|----------|
| `dialog.click → if e.target === dialog then close()` | One-line handler | ✓ |
| `closedby="any"` attribute | Newer Chrome only | |
| No backdrop close | Force X button | |

**Auto-selected:** Click handler.

---

## Body Scroll Lock (D-11)

| Option | Description | Selected |
|--------|-------------|----------|
| Manual `body.overflow = 'hidden'` on open, restore on close | Required (`<dialog>` doesn't lock natively) | ✓ |
| Rely on `<dialog>` (incorrect assumption) | — | |

**Auto-selected:** Manual lock — Pitfall 8.

---

## Backdrop Strategy (D-12, D-13)

| Option | Description | Selected |
|--------|-------------|----------|
| `backdrop-filter: blur(12px)` + rgba fallback via `@supports` | Locked by ROADMAP success #3 | ✓ |
| Flat `rgba(16,15,15,0.85)` only | Pitfall 10 conservative default | |
| Different colours per theme | Theme-specific overrides | |

**Auto-selected:** blur(12px) with `@supports` rgba fallback; single backdrop colour `rgba(16,15,15,0.85)` (theme-invariant).
**Notes:** Pitfall 10 perf concern mitigated by `@supports`-gating the blur.

---

## Lightbox JS File (D-14, D-15)

| Option | Description | Selected |
|--------|-------------|----------|
| New `themes/minimal/static/js/lightbox.js` page-scoped | Loaded from `gallery/single.html` only | ✓ |
| Inline in `gallery/single.html` | Same effect, less reusable | |
| Loaded from `baseof.html` | Ships JS to every page | |

**Auto-selected:** New file, page-scoped load — ARCHITECTURE recommendation.
**Notes:** ~80 LOC IIFE per D-15. `defer` attribute on script tag.

---

## Prev/Next Data Source (D-16)

| Option | Description | Selected |
|--------|-------------|----------|
| DOM-walk siblings of active `<a>` | DOM order = `weight` order | ✓ |
| JS array seeded from server-rendered `data-index` | Duplicates DOM order | |

**Auto-selected:** DOM-walk.

---

## Lightbox Aria Label (D-17)

| Option | Description | Selected |
|--------|-------------|----------|
| `aria-label="Photo {n} of {total}"` updated on nav | Stable name even when caption empty | ✓ |
| `aria-labelledby` pointing to figcaption | Empty when caption omitted | |

**Auto-selected:** Dynamic aria-label.

---

## Touch Swipe (D-18)

| Option | Description | Selected |
|--------|-------------|----------|
| 50 px deltaX threshold | REQUIREMENTS-07 + ROADMAP success #5 | ✓ |
| 30 px / 80 px alternative thresholds | Tunable | |
| Skip swipe (defer) | — | |

**Auto-selected:** 50 px — locked.

---

## Progressive Enhancement (D-19)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `<a href="$full">` wrapping each thumb | JS-disabled users get full image as separate page | ✓ |
| Replace with `<button>` | Loses progressive enhancement | |

**Auto-selected:** Keep `<a href>` — Pitfall 7.

---

## Lightbox Markup (D-20)

| Option | Description | Selected |
|--------|-------------|----------|
| `<dialog>` with close + prev + next + img + figcaption | Standard structure, Lucide-style SVG icons | ✓ |
| Minimal: just img + close | Skip prev/next, force keyboard | |

**Auto-selected:** Standard structure.

---

## CSS Scoping (D-21)

| Option | Description | Selected |
|--------|-------------|----------|
| `body.page-gallery .gallery-lightbox-*` | Locked by Pitfall 17 + Phase 6 precedent | ✓ |
| Generic `.lightbox`, `.modal` | Forbidden | |

**Auto-selected:** body.page-gallery scope.

---

## Reduced Motion (D-22)

| Option | Description | Selected |
|--------|-------------|----------|
| All transitions wrapped in `@media (prefers-reduced-motion: no-preference)` | Universal pattern | ✓ |
| Unguarded transitions | Pitfall 9 violation | |

**Auto-selected:** Wrapped.

---

## EXIF Gate (D-23)

| Option | Description | Selected |
|--------|-------------|----------|
| Two-layer: `disableLatLong` (existing) + new CI step in deploy.yml | Closes REQ-09 "CI gate" gap | ✓ |
| Source-side scrub script only (v2.0 status quo) | No CI enforcement | |
| Only Hugo config | Insufficient per REQ-09 | |

**Auto-selected:** Two-layer with new CI step.
**Notes:** v2.0 Phase 6 gate was effectively author-discipline; REQ-09 envisions actual CI enforcement.

---

## Phase Sub-Task Order (D-26, D-27)

| Option | Description | Selected |
|--------|-------------|----------|
| 3 plans: Authoring → Template+CSS+CI → JS+Verification | Coarse-grain favored, matches Phase 9 precedent | ✓ |
| 4 plans: split EXIF CI from Wave 2 | Acceptable if planner prefers | |
| 5+ plans: per file change | Over-fragmented | |

**Auto-selected:** 3 plans suggested (planner has final say).
**Notes:** Lightbox JS depends on template depends on frontmatter — tight coupling favors fewer plans.

---

## Existing Markup Preservation (D-28)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `<a aria-label>` wrapper, add `data-caption`/`data-alt` | Progressive enhancement preserved | ✓ |
| Replace with `<button>` | Loses accessibility + progressive enhancement | |

**Auto-selected:** Preserve `<a>` + add data attrs.

---

## Claude's Discretion

(Handed to planner via D-decisions in CONTEXT.md `<decisions>` section.)

- Exact `column-gap` values for masonry (default `1rem` suggested)
- Exact `padding` and `border-radius` of lightbox buttons (within Flexoki / Pitfall 16 envelope)
- Whether buttons get hover states (within `prefers-reduced-motion: no-preference`)
- CSS rule organization within new section block (one block vs split per element)
- 3 vs 4 plan split (D-27 default vs separate EXIF CI plan)
- Exact LOC of `lightbox.js` (~80 LOC budget)
- `touchcancel` handling alongside touchstart/touchend (defensive UX)

---

## Deferred Ideas

(All explicitly listed in CONTEXT.md `<deferred>` section. Highlights:)

- GALLERY-FUT-01: Photo counter overlay `3 / 18`
- GALLERY-FUT-02: `<link rel="preload">` for next/prev images
- One-shot `scripts/shuffle_gallery.py` for author-time weight derivation
- Caption fade-in stagger (50 ms after image)
- Per-photo sidecar `.md` files (ARCHITECTURE alternative)
- Hugo `collections.Shuffle` (anti-feature)
- Client-side random gallery order (anti-feature)
- CSS Grid Level 3 `grid-template-rows: masonry` (anti-feature)
- PhotoSwipe / GLightbox / Tobii / Slightbox / Lightbox2 (anti-features)
- Masonry.js / Isotope / Bricks.js / packery (anti-features)
- focus-trap NPM package (anti-feature)
- Lucide / Heroicons / Feather / Phosphor as installed packages (anti-features)
- Pre-fetching all full-size photos for "snappy UX" (Pitfall 11)
- Bumping full-image quality from q78 to q82 (Pitfall 11)
- JS-driven masonry layout (anti-feature)

---

*Phase: 10-gallery-lightbox-masonry-captions*
*Discussion logged: 2026-05-04*
*Mode: --auto (single pass; no user prompts)*

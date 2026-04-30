# Phase 7: About Enrichment - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-30
**Phase:** 07-about-enrichment
**Mode:** `--auto` (recommended defaults selected for every gray area; no AskUserQuestion calls)
**Areas discussed:** Bundle Structure, Front Matter, Layout File Strategy, CSS Scoping, Image Pipeline, Title-Keyword Convention, Loading Priority, Hero Layout, Hero Canvas Width, Pull-Quote Source, Pull-Quote Style, Grid Layout, Photo Count, Photo Source, EXIF Strategy, Hook Whitespace, Cross-Page Risk, CSS Section Placement, Copy Edits, CV Link Placement

---

## Bundle Structure (D-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Leaf bundle `content/about/index.md`, delete `content/about.md` | Idiomatic Hugo, mirrors Phase 6 D-01 | ✓ |
| Keep `content/about.md`, treat images as Hugo `static/` assets | Avoids any URL routing risk but loses page-bundle benefits | |
| Hybrid: bundle for images only, content stays at `content/about.md` | Hugo doesn't support this — bundle requires `index.md` | |

**Auto-selected:** Leaf bundle, delete legacy file after verification.
**Notes:** ABOUT-01 explicitly mandates the conversion. Order of operations matters: create new bundle, verify build, then delete `content/about.md` to avoid duplicate-permalink warnings.

---

## Front Matter (D-02)

| Option | Description | Selected |
|--------|-------------|----------|
| `title: "About"` only | Mirrors current minimal-frontmatter pattern (matches gallery leaf bundle) | ✓ |
| Add `date`, `summary`, `description` | More metadata but no rendering benefit on the About page | |

**Auto-selected:** `title` only.

---

## Layout File Strategy (D-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse `_default/single.html`, layout via raw HTML in markdown | Minimal template surface, no content-front-matter restructuring | ✓ |
| New `themes/minimal/layouts/about/single.html` | Custom template like gallery — but requires splitting About copy into front-matter fields | |
| Custom shortcodes for hero/grid/pullquote | Adds shortcode infrastructure for one-page use | |

**Auto-selected:** Reuse default; add raw HTML wrappers in markdown.

---

## CSS Scoping (D-04)

| Option | Description | Selected |
|--------|-------------|----------|
| `body.page-about` (Phase 6 pattern, already shipped in baseof.html) | Reuses existing infrastructure, zero baseof.html churn | ✓ |
| Inline `<style>` in `content/about/index.md` | Anti-pattern — duplicate CSS, no theme-token integration | |
| New `<link>` tag for an about-specific stylesheet | Over-engineering for a few CSS rules | |

**Auto-selected:** `body.page-about`.

---

## Image Pipeline (D-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Hugo render-image hook (deferred from Phase 6) | One-time infrastructure win, generic across blog + about, plain markdown stays plain | ✓ |
| Per-image shortcode (`{{< img >}}`) | Adds shortcode boilerplate per call site | |
| Raw `<img src="processed-path.webp">` with manual paths | No automatic processing; loses Hugo image pipeline benefits | |

**Auto-selected:** Render-image hook.
**Notes:** Phase 6 § Deferred Ideas explicitly identified this hook as a Phase 7 follow-up. Lands here as locked scope.

---

## Title-Keyword Convention (D-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Title-attribute switch: `"hero"` / `"grid"` / default | Stays in plain markdown, three-arm switch covers all current needs, additive extension | ✓ |
| Per-image YAML keys in front matter | Couples content-file structure to layout intent | |
| Multiple shortcodes (`{{< hero >}}`, `{{< grid-img >}}`) | Adds shortcode infrastructure for what is fundamentally a sizing hint | |
| Class hint via alt text (e.g., `![hero:alt text](...)`) | Hijacks alt text, hurts a11y | |

**Auto-selected:** Title-attribute switch.

---

## Loading Priority (D-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Hero only: `fetchpriority="high"` + `loading="eager"` | One above-fold image, matches Web.dev LCP guidance | ✓ |
| All hero + first row of grid | Over-fetches on mobile (grid is below the fold) | |
| Lazy-load everything | Hurts hero LCP | |

**Auto-selected:** Hero-only priority hint.

---

## Hero Layout (D-09)

| Option | Description | Selected |
|--------|-------------|----------|
| 2:1 (text 2fr / photo 1fr) | Biographical content is text-heavy, photo anchors without dominating | ✓ |
| 1:1 | Visually balanced but cramps the text column |  |
| 3:1 | Text-dominant, photo feels small |  |
| Sidebar (text full-width, photo floats right) | Older blog aesthetic, complicates mobile collapse |  |

**Auto-selected:** 2:1.

---

## Hero Canvas Width (D-10)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep 640 px (read-flow content) | Biographical text reads better at narrow measure | ✓ |
| Widen to 1100 px (match gallery) | Hurts paragraph readability across multiple sections | |
| Widen to 800 px (compromise) | Adds a third canvas size to maintain | |

**Auto-selected:** Keep 640 px.

---

## Pull-Quote Source (D-11)

| Option | Description | Selected |
|--------|-------------|----------|
| "40% → 95% routing accuracy" (Erste Group) | Concrete metric, biggest delta, anchors Experience visual rhythm | ✓ |
| "7,000 daily users across five countries" (Erste Group) | Also strong, picks scale over delta — Claude's discretion | |
| "2nd place at international GenAI hackathon (300 participants)" | Achievement-flavored but less impactful | |

**Auto-selected:** 40% → 95% accuracy. Planner can swap during execution.

---

## Pull-Quote Style (D-12)

| Option | Description | Selected |
|--------|-------------|----------|
| Left accent bar + bg-secondary fill + accent strong | Visually distinct from blockquote, theme-aware via existing Flexoki tokens | ✓ |
| Italic centered display | Conventional but doesn't differentiate from blockquote | |
| Boxed callout with full background | Heavier visual weight, may feel heavy in minimal aesthetic | |

**Auto-selected:** Left bar + bg-secondary + accent strong.

---

## Grid Layout (D-14)

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed `repeat(2, 1fr)` desktop / 1-col mobile | Predictable for 4 images, fits 640 px canvas without extra logic | ✓ |
| `repeat(auto-fit, minmax(180px, 1fr))` | More flexible for dynamic counts, but renders 2 cols at 640 px anyway | |
| 4-column row (single row of small thumbnails) | Too small per-thumbnail at 640 px canvas | |

**Auto-selected:** Fixed 2-col / 1-col mobile.

---

## Photo Count (D-15)

| Option | Description | Selected |
|--------|-------------|----------|
| 4 (one per outdoor interest) | Matches Interests copy (bouldering, cycling, running, cooking), 2x2 balances visually | ✓ |
| 5 (add one for "reading") | Reading doesn't photograph well as a candid | |
| 6+ | Page becomes photo-heavy; About is read-flow content first | |
| 1 hero + 0 grid | Misses ABOUT-02's "photo grid" criterion | |

**Auto-selected:** 4 grid photos.

---

## Photo Source (D-16)

| Option | Description | Selected |
|--------|-------------|----------|
| User provides at plan-execute time; HUMAN-UAT blocker if not selected | User owns curation, executor can stub-and-pause | ✓ |
| Reuse 5 photos from gallery (`content/gallery/photos/`) | Some may not match interests; gallery photos are the curated set, not necessarily about-page-fit | |
| Use stock illustrations | Conflicts with "personal photos" requirement (ABOUT-02) | |

**Auto-selected:** User-provided.

---

## EXIF Strategy (D-17)

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse Phase 6 D-13 (source-side exiftool + hugo.toml `[imaging.exif]`) | Pipeline already proven, hugo.toml already configured | ✓ |
| Source-side only | Misses build-side belt-and-suspenders | |
| Hugo-side only | Source files in git would still carry GPS — auditable risk | |

**Auto-selected:** Two-pronged Phase 6 recipe.

---

## Hook Whitespace (D-19)

| Option | Description | Selected |
|--------|-------------|----------|
| Whitespace-trimming with `{{- }}` | CSS Grid layout fragility outweighs template readability | ✓ |
| Readable formatting (no trim) | Risks stray whitespace nodes inside grid layouts | |

**Auto-selected:** Whitespace-trimming.

---

## Cross-Page Risk (D-20)

| Option | Description | Selected |
|--------|-------------|----------|
| Apply hook globally with cold-build smoke test on existing blog posts | Lets Phase 6's deferred improvement land for free; smoke-test guards regression | ✓ |
| Scope hook to leaf bundles only via per-type override | Adds a layout file just to suppress the global hook on blog posts | |
| Scope hook to `/about/` only | Wastes the cross-cutting infrastructure win | |

**Auto-selected:** Apply globally + smoke test.

---

## CSS Section Placement (D-21)

| Option | Description | Selected |
|--------|-------------|----------|
| Append `/* === About === */` between `/* === Gallery === */` and `/* === Footer === */` | Mirrors Phase 6's section-by-content-type ordering | ✓ |
| Append at very end (after `/* === Responsive === */`) | Breaks ordering convention | |

**Auto-selected:** Between Gallery and Footer.

---

## Copy Edits (D-23)

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve verbatim, structural additions only | Copy is content-complete; scope creep prevention | ✓ |
| Light rewrite for tone consistency | Drift risk; user owns the prose | |
| Major rewrite (recasting career narrative) | Out of phase scope | |

**Auto-selected:** Preserve verbatim.

---

## CV Link Placement (D-24)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep inline at top of hero text | Current placement works; polish is YAGNI | ✓ |
| Promote to button-style with download icon | Visual polish; defer to future v2.x | |
| Move to a dedicated "Download" sidebar | Adds layout complexity | |

**Auto-selected:** Keep inline.

---

## Claude's Discretion

(See `<decisions> § Claude's Discretion` in 07-CONTEXT.md for the full list. Highlights:)
- Pull-quote target line: planner can swap "40% → 95%" for "7,000 daily users" if user prefers.
- Hero `border-radius`: 6 px (recommended) vs 4 px (matches gallery thumb).
- Default-arm class on render-image hook output: keep classless (preserves existing `.page-content img` cascade).
- Grid CSS pattern: fixed `repeat(2, 1fr)` (recommended) vs `auto-fit, minmax(180px, 1fr)`.
- Whether to commit `.gitkeep` in empty `content/about/images/` if photos arrive separately.
- Whether title hint switch handles unknown values defensively (recommended: `else` arm catches all).

## Deferred Ideas

(See `<deferred>` in 07-CONTEXT.md for the full list.)

- Per-photo captions on hero / grid
- Per-experience photo callouts (one image per company in Experience)
- Native `<dialog>` lightbox for hero / grid
- `srcset` / `<picture>` for hi-DPI portraits
- AVIF format (blocked by Hugo 0.157)
- Title-keyword extension beyond "hero" / "grid" (e.g., "banner")
- Generalized `.pullquote` rule family (lift body-class scope if other pages adopt)
- CV download as a button-styled link with icon
- Two-column layout inside the Experience section
- Photo-set rotation / cycling on reload
- Hugo render-link hook for outbound links (auto-target="_blank")
- Splitting About copy into structured front-matter sections (would enable a custom layout iteration)

# Phase 6: Gallery - Pattern Map

**Mapped:** 2026-04-30
**Files analyzed:** 7 (4 NEW, 3 MODIFY, 1 DELETE)
**Analogs found:** 6 / 7 (the 18 photo resources are content, not code — no analog needed)

> Downstream consumer: `gsd-planner`. Use the per-file Pattern Assignments below to write `read_first` and `acceptance_criteria` (grep-verifiable strings) for each task. The Shared Patterns section captures cross-cutting concerns. The "No Analog Found" section flags genuinely-novel work that must be planned from RESEARCH.md/UI-SPEC.md rather than from existing code.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `content/gallery/index.md` (NEW) | content (leaf-bundle index) | static-render | `content/about.md` | partial — about.md is single-file, gallery is a bundle |
| `content/gallery/photos/*.{jpg,JPG,jpeg}` (NEW; 18 files moved via `git mv`) | resource (page-bundle assets) | static-render (Hugo image pipeline input) | `content/blog/2026-03-27-video-editing-journey/images/*.{png,jpg}` | partial — same bundle-resources idea, different subdir name (`photos/` vs `images/`) |
| `themes/minimal/layouts/gallery/single.html` (NEW) | template (Type-derived layout) | request-response (build-time) | `themes/minimal/layouts/_default/single.html` | role-match — same `<article>` shell, different inner content |
| `themes/minimal/layouts/_default/baseof.html` (MODIFY: line 26) | template (base layout) | request-response (build-time) | itself (one-line edit in place) | exact — direct edit |
| `themes/minimal/static/css/style.css` (MODIFY: append section) | stylesheet (single source of truth) | static-render | itself + `/* === Single Post / Page === */` section conventions | exact — append-in-place |
| `hugo.toml` (MODIFY: 3 changes) | config (site-wide) | config | itself + existing `[[menu.main]]` blocks | exact — pattern is already in the file |
| `images/galary/` (DELETE entire directory) | n/a (cleanup) | n/a | `git mv` source-of-move | exact — Hugo move idiom |

---

## Pattern Assignments

### `content/gallery/index.md` (NEW — content / leaf-bundle index)

**Closest Analog:** `content/about.md` (lines 1-3)

**Rationale:** Both are minimal-frontmatter standalone pages with `title:` only — no `date`, no `draft`, no `summary`. Difference: gallery is a **leaf bundle** (`content/gallery/index.md` + `photos/` subdir) instead of a single `.md` file at the section root. Hugo derives `Type=gallery` from the parent folder name, which routes layout lookup to `layouts/gallery/single.html` (D-01, D-02).

**Frontmatter pattern** (mirror lines 1-3 of `content/about.md`):

```yaml
---
title: "Gallery"
---
```

**Structural difference vs analog:**
- `content/about.md` is a standalone file → produces `Type="page"` (the homepage `.Type` quirk also affects standalone pages — see UI-SPEC § Body-Class Pattern Documentation)
- `content/gallery/index.md` is a leaf-bundle index → produces `Type="gallery"`, which is what enables `body.page-gallery` CSS scoping

**Pattern source for the leaf-bundle directory shape:** every blog post under `content/blog/YYYY-MM-DD-slug/` already uses page-bundles with co-located images. The shape `content/{section-or-page}/index.md + sibling resource subdir` is established. Phase 6 applies it at the section level for the first time.

**No body content in the markdown** — the entire page render comes from the template iterating bundle resources. Do NOT add Markdown prose under the frontmatter.

---

### `content/gallery/photos/*.{jpg,JPG,jpeg}` (NEW — moved from `images/galary/`)

**Closest Analog:** `content/blog/2026-03-27-video-editing-journey/images/` (page-bundle resources for an existing post)

**Rationale:** Both are page-bundle image resources. Difference: blog post images live in `images/` subdir (read by direct Markdown image references like `![alt](images/foo.png)`); gallery photos live in `photos/` subdir and are picked up programmatically via `.Resources.Match "photos/*"` (D-03).

**Move pattern** (verbatim from RESEARCH.md § Code Excerpts):

```bash
# Move with git history preserved (D-16)
git mv images/galary content/gallery/photos

# Scrub EXIF on the moved files in place (D-13 prong 1)
cd content/gallery/photos
exiftool \
  -GPS:All= \
  -Make= -Model= \
  -Serial*= \
  -OwnerName= -Artist= -Copyright= \
  -overwrite_original \
  ./*

# Stage modified files
cd ../../..
git add content/gallery/photos/
```

**Filename preservation:** Keep originals (D-15). Do NOT lowercase `.JPG` → `.jpg`, do NOT kebab-case. The 18 source filenames are: `20210710_132418.jpg`, `5dc795b8-...jpg`, `60130366-...jpg`, `7eb72991-...jpg`, `98562fcd-...jpg`, `DSC09782.JPG`, `DSC09784.JPG`, `f2e6acbb-...jpg`, `IMG_0256.jpeg`, `IMG_1288.JPG`, `IMG_1299.JPG`, `IMG_1499.jpeg`, `IMG_1646.jpeg`, `IMG_2009.jpeg`, `IMG_5685_Original.JPG`, `IMG_6546.jpeg`, `IMG_7828.jpeg`, `IMG_8113.jpg` (verified by `ls images/galary/`).

**Acceptance criteria for planner:**
- `test ! -d images/galary` returns success (D-17)
- `ls content/gallery/photos/ | wc -l` returns 18
- `exiftool -GPSLatitude -GPSLongitude -Make -Model -Serial* content/gallery/photos/*` produces zero field matches (D-14)

---

### `themes/minimal/layouts/gallery/single.html` (NEW — Type-derived layout)

**Closest Analog:** `themes/minimal/layouts/_default/single.html` (10 lines, full file)

**Rationale:** Same `{{ define "main" }}` block, same `<article>` + `.page-header` + `.page-title` shell. Difference: replace the `.page-content / {{ .Content }}` block with a `<div class="gallery-grid">` that ranges over bundle resources and emits `<a class="gallery-item"><img class="gallery-img"></a>` markup with eager/lazy loading attributes.

**Existing analog excerpt** (`themes/minimal/layouts/_default/single.html` lines 1-13):

```go-html-template
{{ define "main" }}
  <article>
    <div class="page-header">
      <h1 class="page-title">{{ .Title }}</h1>
      {{ if .Date }}
        <div class="page-date">{{ .Date.Format "January 2, 2006" }}</div>
      {{ end }}
    </div>
    <div class="page-content">
      {{ .Content }}
    </div>
  </article>
{{ end }}
```

**Patterns to copy from analog:**
1. Outer `{{ define "main" }} ... {{ end }}` block name (line 1, 13) — required for `baseof.html`'s `{{ block "main" . }}` slot
2. `<article>` wrapper (line 2, 12) — semantic landmark, no class needed
3. `<div class="page-header">` + `<h1 class="page-title">{{ .Title }}</h1>` (lines 3-4) — keep the heading per UI-SPEC § Typography decision (SEO + a11y), drop the `.Date` block (gallery has no date)
4. **Drop** the `.page-content` div — replace with the gallery grid

**New gallery-grid pattern** (verbatim from RESEARCH.md § Code Excerpts lines 686-715, finalized via UI-SPEC):

```go-html-template
{{ define "main" }}
  <article>
    <div class="page-header">
      <h1 class="page-title">{{ .Title }}</h1>
    </div>
    {{ with .Resources.Match "photos/*" }}
      <div class="gallery-grid">
        {{ $total := len . }}
        {{ range $idx, $photo := . }}
          {{ $thumb := $photo.Process "fill 600x400 Smart webp q75" }}
          {{ $full  := $photo.Process "fit 1600x1600 webp q82" }}
          <a class="gallery-item"
             href="{{ $full.RelPermalink }}"
             aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size">
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
    {{ end }}
  </article>
{{ end }}
```

**Per-attribute provenance:**
- `Process "fill 600x400 Smart webp q75"` — D-08 / GAL-03 / ROADMAP locked
- `Process "fit 1600x1600 webp q82"` — D-07 / GAL-04 / ROADMAP locked
- `width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"` — explicit pixel dims for CLS = 0 (Hugo provides post-processing dimensions)
- `loading` ternary `lt $idx 3 ? eager : lazy` — D-05 (first 3 eager)
- `fetchpriority="high"` only on `$idx == 0` — D-06 (LCP Web.dev guidance)
- `decoding="async"` only on `$idx >= 3` — UI-SPEC § Loading below the fold (CONTEXT.md "Claude's Discretion" finalized)
- `alt=""` (empty) — D-18 (decorative; `aria-label` on `<a>` carries the accessible name)
- `aria-label="Open photo N of M at full size"` — UI-SPEC § Copywriting Contract (1-indexed via `add $idx 1`)
- `{{ with .Resources.Match "photos/*" }}` guard — defensive empty-bundle handling (D-03 + Claude's Discretion)

**Hugo conditional idiom precedent:** `_default/list.html` line 22 uses `{{ if eq .Section "blog" }}` — the same conditional grammar (`if`/`eq`/`lt`/`ge`) is already in the codebase. The new template doesn't introduce any new template-language constructs.

**Resource iteration idiom precedent:** `_default/list.html` lines 4 and 24 use `{{ range where .Site.RegularPages "Section" "blog" }}` and `{{ range .Pages }}` — the `range` over a collection idiom is already established. `.Resources.Match "photos/*"` is the bundle-resource analog of those calls (returns `[]resource.Resource` sorted alphabetically by name).

**Acceptance criteria for planner (grep-verifiable):**
- `grep -c '{{ define "main" }}' themes/minimal/layouts/gallery/single.html` returns `1`
- `grep -c 'gallery-grid' themes/minimal/layouts/gallery/single.html` returns `1`
- `grep -c 'Process "fill 600x400 Smart webp q75"' themes/minimal/layouts/gallery/single.html` returns `1`
- `grep -c 'Process "fit 1600x1600 webp q82"' themes/minimal/layouts/gallery/single.html` returns `1`
- `grep -c 'aria-label="Open photo' themes/minimal/layouts/gallery/single.html` returns `1`
- `grep -c 'fetchpriority="high"' themes/minimal/layouts/gallery/single.html` returns `1`
- After `hugo --minify`: `grep -c 'aria-label="Open photo' public/gallery/index.html` returns `18`

---

### `themes/minimal/layouts/_default/baseof.html` (MODIFY — line 26 only)

**Self-analog (one-line edit in place).** Read the file first to anchor the diff.

**Read-first scope:** lines 1-58 (entire file is small).

**Current state (line 26):**

```html
<body>
```

**Target state (line 26):**

```html
<body class="page-{{ .Type | default "default" }}">
```

**Rationale:** D-10 — adds page-type-specific CSS hook so `body.page-gallery .site-wrapper { max-width: 1100px; }` works. The `default "default"` fallback is harmless cruft (homepage emits `body.page-page` per the Hugo Type quirk documented in UI-SPEC § Body-Class Pattern); the explicit fallback signals defensive intent.

**Surrounding context (DO NOT modify lines 25 or 27):**

| Line | Content |
|------|---------|
| 25 | `</head>` |
| 26 | `<body>` ← target of edit |
| 27 | `  <div class="site-wrapper">` |

All other lines (1-25, 27-58) including the theme-bootstrap IIFE (lines 11-23), the `{{ partial "favicon.html" . }}` (line 9), the `{{ block "main" . }}` slot (line 30), and the theme-toggle script (lines 34-56) are **not modified**.

**Acceptance criteria for planner:**
- `grep -c 'class="page-{{ .Type' themes/minimal/layouts/_default/baseof.html` returns `1`
- `grep -c '^<body>$' themes/minimal/layouts/_default/baseof.html` returns `0` (the bare `<body>` is gone)
- `grep -c '{{ block "main" . }}' themes/minimal/layouts/_default/baseof.html` still returns `1` (untouched)
- `grep -c 'partial "favicon.html"' themes/minimal/layouts/_default/baseof.html` still returns `1` (untouched)
- After `hugo --minify`: `grep -c 'class="page-gallery"' public/gallery/index.html` returns `1`
- After `hugo --minify`: `grep -c 'class="page-blog"' public/blog/index.html` returns `1` (cross-page sanity)

---

### `themes/minimal/static/css/style.css` (MODIFY — append section)

**Self-analog (append between two existing section comments).** Read the file first.

**Read-first scope:** lines 169-280 (the surrounding sections — `/* === Single Post / Page === */` starts at line 169; `/* === Footer === */` starts at line 276).

**Insertion point:** Between line 274 (`}` closing `.page-content hr`) and line 276 (`/* === Footer === */`). Add a blank line before and after the new section comment.

**Pattern from existing CSS** — section-comment convention used throughout the file (verified at lines 1, 58, 65, 132, 169, 276, 313):

```css
/* === Section Name === */
```

**Pattern for the focus-visible outline** — copied verbatim from `style.css` lines 117-122 (the existing `.site-nav a:focus-visible` and `.theme-toggle:focus-visible` rule):

```css
.site-nav a:focus-visible,
.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```

The new `.gallery-item:focus-visible` rule mirrors this exactly: `2px solid var(--accent)`, `outline-offset: 2px`. (The new rule omits the `border-radius: 2px` from the focus rule itself because `.gallery-item` already has `border-radius: 4px` — the focus outline traces a 4px-rounded rectangle aligned with the photo edges.)

**Pattern for the border-radius value** — copied from `style.css` line 225 (`.page-content img { border-radius: 4px; }`):

```css
.page-content img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 1.5rem 0;
}
```

The new `.gallery-img` rule reuses the same `4px` radius for visual consistency across the site.

**New CSS to append** (verbatim from RESEARCH.md § Code Excerpts lines 717-749 + UI-SPEC § Element Specs):

```css
/* === Gallery === */
body.page-gallery .site-wrapper {
  max-width: 1100px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  margin: 0;
}

.gallery-item {
  display: block;
  line-height: 0;        /* kill baseline gap below <img> */
  border-radius: 4px;
}

.gallery-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.gallery-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
}
```

**Specificity check (UI-SPEC § Layout):** `body.page-gallery .site-wrapper` is `(0,2,0)` — beats default `.site-wrapper` (line 59-63) at `(0,1,0)`. No `!important` required.

**No mobile breakpoint changes:** The existing `@media (max-width: 600px)` block at line 314-320 stays untouched. Auto-fill collapse handles gallery responsive behavior naturally (UI-SPEC § Responsive Breakpoints — empirically the 1-column collapse happens around 488 px viewport, not 600 px as CONTEXT D-11 assumed; behavior is acceptable as-is).

**Acceptance criteria for planner:**
- `grep -c '/\* === Gallery === \*/' themes/minimal/static/css/style.css` returns `1`
- `grep -c 'body\.page-gallery \.site-wrapper' themes/minimal/static/css/style.css` returns `1`
- `grep -c '\.gallery-grid' themes/minimal/static/css/style.css` returns `1`
- `grep -c '\.gallery-item' themes/minimal/static/css/style.css` returns `2` (the rule + `:focus-visible` rule)
- `grep -c '\.gallery-img' themes/minimal/static/css/style.css` returns `1`
- `grep -c '\.gallery-item:hover' themes/minimal/static/css/style.css` returns `0` (locked: zero hover styling per UI-SPEC § Color)
- `grep -c '@media (max-width: 600px)' themes/minimal/static/css/style.css` returns `1` (existing breakpoint untouched)
- `grep -c 'repeat(auto-fill, minmax(220px, 1fr))' themes/minimal/static/css/style.css` returns `1` (verbatim ROADMAP-locked template)

---

### `hugo.toml` (MODIFY — three changes)

**Self-analog (existing `[[menu.main]]` blocks at lines 21-28).** Read the file first.

**Read-first scope:** lines 1-39 (entire file is small).

**Existing pattern to mirror** (`hugo.toml` lines 20-28):

```toml
[menu]
  [[menu.main]]
    name = "Blog"
    url = "/blog/"
    weight = 1
  [[menu.main]]
    name = "About"
    url = "/about/"
    weight = 2
```

The Gallery insertion uses the same shape: `name`, `url`, `weight` inside a `[[menu.main]]` block, two-space indented nested under `[menu]`.

**Edit 1 — Insert Gallery menu entry between Blog (line 24) and About (line 25):**

```toml
[menu]
  [[menu.main]]
    name = "Blog"
    url = "/blog/"
    weight = 1
  [[menu.main]]
    name = "Gallery"
    url = "/gallery/"
    weight = 2
  [[menu.main]]
    name = "About"
    url = "/about/"
    weight = 3
```

**Edit 2 — Bump About weight from `2` → `3` (line 28):**
- Before: `    weight = 2`
- After:  `    weight = 3`

**Edit 3 — Insert `[imaging]` block after `[markup.highlight]` (after line 18) or before `[privacy]` (before line 30):**

```toml
[imaging]
  [imaging.exif]
    disableLatLong = true
```

Recommended placement: between line 28 (`weight = 3` of About) and line 30 (`[privacy]`), separated by blank lines. This keeps the file ordered as: site config → markup → menu → imaging → privacy.

**Final menu rendering verification:** `partials/header.html` lines 7-12 already iterate `{{ range .Site.Menus.main }}` sorted by weight, emitting `<a href="{{ .URL }}">{{ .Name }}</a>`. With weights 1/2/3 the rendered nav order is **Blog → Gallery → About** (D-12).

**Acceptance criteria for planner:**
- `grep -c '\[\[menu.main\]\]' hugo.toml` returns `3`
- `grep -c 'name = "Gallery"' hugo.toml` returns `1`
- `grep -c 'url = "/gallery/"' hugo.toml` returns `1`
- `grep -c '\[imaging.exif\]' hugo.toml` returns `1`
- `grep -c 'disableLatLong = true' hugo.toml` returns `1`
- `awk '/name = "About"/{f=1} f && /weight =/{print; exit}' hugo.toml` outputs `    weight = 3`
- After `hugo --minify`: rendered `/index.html` shows nav links in the order Blog, Gallery, About (verify with grep over `public/index.html`)

---

### `images/galary/` (DELETE — full directory removal)

**Pattern:** The `git mv images/galary content/gallery/photos` command from D-16 atomically removes the source directory as part of the move. After `git mv` completes, `images/galary/` no longer exists in the working tree or in git history's HEAD (each individual photo file's history is preserved via the rename detection).

**No analog needed** — this is a one-shot cleanup gated by D-17.

**Acceptance criteria for planner (D-17 + ROADMAP success criterion 5):**
- `test ! -d images/galary` returns success
- `grep -r galary content/ themes/ hugo.toml` returns zero hits
- `git log --follow -- content/gallery/photos/IMG_1646.jpeg` shows pre-move history (rename preserved)

---

## Shared Patterns

### Hugo Type-Derived Layout Lookup (NEW for this codebase)

**Source:** Hugo conventional file structure (gohugo.io/templates/lookup-order/)
**Apply to:** `themes/minimal/layouts/gallery/single.html` (NEW)
**Pattern:**

> When `.Type == "gallery"` (derived from `content/gallery/index.md`'s parent folder name), Hugo's lookup chain resolves `layouts/gallery/single.html` BEFORE falling back to `layouts/_default/single.html`. No `layout:` front-matter override needed.

**Existing precedent in this codebase:** None — only `_default/` layouts exist today (`baseof.html`, `single.html`, `list.html`). Phase 6 introduces the first non-default layout directory.

**Cross-phase implication:** Phase 7 (About Enrichment) gets the same pattern for free if it converts `content/about.md` → `content/about/index.md` (creates `Type=about` and unlocks `layouts/about/single.html`).

---

### Page-Bundle Resource Iteration (NEW for this codebase)

**Source:** `gohugo.io/methods/resource/process/` + RESEARCH.md § `.Resources.Match`
**Apply to:** `themes/minimal/layouts/gallery/single.html` (NEW)
**Pattern:**

```go-html-template
{{ with .Resources.Match "photos/*" }}
  {{ $total := len . }}
  {{ range $idx, $photo := . }}
    {{ $thumb := $photo.Process "fill 600x400 Smart webp q75" }}
    {{ $full  := $photo.Process "fit 1600x1600 webp q82" }}
    ...
  {{ end }}
{{ end }}
```

**Existing precedent in this codebase:** None — the existing blog posts reference images via Markdown `![alt](images/foo.png)`, which routes through Goldmark, not through `image.Process`. The `.Resources.Match` + `.Process` idiom is brand-new with Phase 6.

**Cross-phase implication:** Future image-heavy pages (Phase 7 About, hypothetical photo blog posts) inherit this pattern as the validated "many images, one page" shape.

---

### Body-Class Page-Type Hook (NEW for this codebase)

**Source:** RESEARCH.md § Body-Class Pattern Documentation + UI-SPEC § Body-Class Pattern Documentation
**Apply to:** `themes/minimal/layouts/_default/baseof.html` (MODIFY)
**Pattern:**

```html
<body class="page-{{ .Type | default "default" }}">
```

**Page-types this produces** (from UI-SPEC § Body-Class Pattern Documentation):

| Route | `.Type` | Body class |
|-------|---------|------------|
| `/` (homepage) | `page` | `page-page` |
| `/blog/` | `blog` | `page-blog` |
| `/blog/YYYY-MM-DD-slug/` | `blog` | `page-blog` |
| `/gallery/` | `gallery` | **`page-gallery`** ← Phase 6's CSS hook |
| `/about/` | `page` | `page-page` (changes to `page-about` after Phase 7 leaf-bundle conversion) |

**Cross-phase implication:** Phase 7+ uses `body.page-{type} .site-wrapper { max-width: NNNNpx; }` for any per-content-type canvas widening with specificity `(0,2,0)`.

---

### Focus-Visible Accessibility Pattern

**Source:** `themes/minimal/static/css/style.css` lines 117-122
**Apply to:** All new interactive elements (Phase 6: `.gallery-item:focus-visible`)
**Pattern:**

```css
.gallery-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

**Excerpt from existing source** (lines 117-122 verbatim):

```css
.site-nav a:focus-visible,
.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```

**Reuse rule:** Match `2px solid var(--accent)` and `outline-offset: 2px` exactly. The `border-radius: 2px` from the source is omitted on `.gallery-item:focus-visible` because the wrapper already has `border-radius: 4px`. **No `transition`** on focus state (matches existing convention — none of the focus-visible rules use transitions).

---

### CSS Section-Comment Convention

**Source:** `themes/minimal/static/css/style.css` (multiple section markers at lines 1, 58, 65, 132, 169, 276, 313)
**Apply to:** New `/* === Gallery === */` section
**Pattern:** `/* === Section Name === */` with title-case section name.

**Insertion ordering rule (CONTEXT.md § Claude's Discretion, recommended):** Place new sections by content type in logical reading order. Phase 6 places Gallery between `/* === Single Post / Page === */` (line 169) and `/* === Footer === */` (line 276) — the natural "page content" → "page chrome" boundary.

---

### Hugo Menu Configuration Pattern

**Source:** `hugo.toml` lines 20-28
**Apply to:** Gallery menu entry insertion + About weight bump
**Pattern:**

```toml
  [[menu.main]]
    name = "<Display Name>"
    url = "/<route>/"
    weight = <integer, lower = first>
```

**Sorting:** `partials/header.html` line 8 `{{ range .Site.Menus.main }}` automatically sorts by `weight` ascending. Inserting Gallery at weight 2 and bumping About to weight 3 yields the rendered order Blog → Gallery → About without any template change.

---

### Hugo `image.Process` Quality + Format Strings (NEW for this codebase)

**Source:** RESEARCH.md § Hugo Image Processing Reference + ROADMAP-locked verbatim
**Apply to:** `themes/minimal/layouts/gallery/single.html`
**Patterns (do NOT alter without measure-then-adjust authority — UI-SPEC § Performance Contract):**

- Thumbnails: `Process "fill 600x400 Smart webp q75"` — `fill` crops to exact 600×400 px; `Smart` chooses entropy/face-aware crop centroid; `webp` output format; `q75` quality (~30-70 KB per thumbnail at this photo set's content variance per RESEARCH § Empirical Findings)
- Full-size: `Process "fit 1600x1600 webp q82"` — `fit` scales longest side to ≤1600 px (no upscaling, preserves aspect); `q82` quality

**Adjustment authority (UI-SPEC § Performance Contract):**
- If `du -sh public/gallery/ > 3 MB`: drop full-size to `q78` (≈25-30% size reduction, marginal visual cost)
- If still > 3 MB: cap full-size at `1200x1200` (≈40% additional reduction)
- Document any deviation in PROJECT.md Key Decisions during phase transition

---

### Hugo `[imaging.exif]` Privacy Configuration (NEW for this codebase)

**Source:** `gohugo.io/configuration/imaging/` + RESEARCH.md § Hugo `[imaging.exif]` and EXIF Strategy
**Apply to:** `hugo.toml` (MODIFY)
**Pattern:**

```toml
[imaging]
  [imaging.exif]
    disableLatLong = true
```

**Critical caveat (RESEARCH-verified):** `[imaging.exif] disableLatLong = true` only controls EXIF *extraction in templates* (e.g., `.Exif.Lat`), NOT EXIF preservation in processed output. The load-bearing privacy guarantee remains the **source-side `exiftool` scrub** (D-13 prong 1) on the JPEG sources before commit. The `[imaging.exif]` block is the documented belt-and-suspenders defense and is required by ROADMAP success criterion 3.

**Cross-phase implication:** Future image-bearing source files MUST still be exiftool-scrubbed at commit time. This config does not absolve that obligation.

---

## No Analog Found

| File / Concern | Reason |
|---|---|
| The `image.Process "fill WxH Smart webp qN"` template invocation | No Hugo image processing exists in the current site (blog images bypass the pipeline via raw Markdown image syntax). Planner references RESEARCH.md § Hugo Image Processing Reference + RESEARCH.md § Code Excerpts lines 686-715 verbatim. |
| The `<body class="page-{{ .Type \| default "default" }}">` line | First introduction of body-class page-type scoping. Pattern documented in UI-SPEC § Body-Class Pattern Documentation; no precedent file in the codebase. |
| The `[imaging.exif]` config block | First `[imaging]` block in `hugo.toml`. Pattern documented in RESEARCH.md § Hugo `[imaging.exif]` Strategy + verbatim diff at RESEARCH.md lines 776-779. |
| The `aria-label="Open photo N of M at full size"` copywriting | UI-SPEC § Copywriting Contract finalized the wording (resolves CONTEXT.md "Claude's Discretion"). No prior aria-label precedent in the codebase to mirror. |
| The `decoding="async"` attribute on lazy thumbnails | UI-SPEC § Loading below the fold finalized this (CONTEXT.md "Claude's Discretion" — Web.dev recommendation). No prior `<img decoding>` use in the codebase. |
| EXIF scrub one-shot bash sequence | Manual phase-execution step, not a recurring pipeline. Documented as a runbook in CONTEXT.md D-13/D-14 and RESEARCH.md § Code Excerpts → Source-side EXIF scrub. No analogous script in `scripts/`. |

---

## Metadata

**Analog search scope:**
- `themes/minimal/layouts/_default/` (3 files: `baseof.html`, `single.html`, `list.html`)
- `themes/minimal/layouts/partials/` (`header.html` for menu rendering pattern; `footer.html` not relevant to Phase 6)
- `themes/minimal/static/css/style.css` (single 320-line stylesheet — sections, focus rules, spacing scale, media query)
- `content/about.md` (minimal-frontmatter standalone page analog)
- `content/blog/2026-03-27-video-editing-journey/` (page-bundle structure analog)
- `hugo.toml` (existing menu + config block conventions)
- RESEARCH.md § Code Excerpts (lines 682-842 — pre-staged executor-ready snippets)
- UI-SPEC.md § Element Specs + § Verification Map (final visual contract)

**Files scanned:** 9 source files + 3 phase-planning artifacts (CONTEXT, RESEARCH, UI-SPEC)

**Pattern extraction date:** 2026-04-30

---

## PATTERN MAPPING COMPLETE

Phase 6 introduces three brand-new patterns to this codebase (Type-derived layout, body-class page-type hook, Hugo `image.Process` pipeline) atop a strong base of existing analogs (`_default/single.html` shell, focus-visible rule, section-comment CSS convention, menu config). Every NEW file has either an exact analog or a documented verbatim snippet in RESEARCH.md/UI-SPEC.md ready for executor copy-paste.

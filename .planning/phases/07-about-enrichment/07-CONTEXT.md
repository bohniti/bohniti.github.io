# Phase 7: About Enrichment - Context

**Gathered:** 2026-04-30
**Status:** Ready for planning
**Mode:** `--auto` — recommended defaults auto-selected; each decision logged inline so the user can audit.

<domain>
## Phase Boundary

Convert `content/about.md` → `content/about/index.md` (Hugo **leaf bundle**) and re-render `/about/` with a richer multi-image layout that inherits the site's theming and image-handling conventions. The URL `/about/` must remain identical (verified by hitting the deployed URL). The new layout adds three CSS-rule families to `style.css` per ROADMAP success criterion 2: **two-column hero**, **photo grid**, and **pull-quote** — and the page renders multiple personal photos sourced from `content/about/images/` as page-bundle resources, all with explicit `width`/`height` to keep CLS < 0.1.

**In scope:**
- New leaf bundle at `content/about/index.md` with minimal front matter (`title: "About"` only — mirrors current `content/about.md`)
- New page-bundle resource directory `content/about/images/` with N personal photos (recommend 1 portrait + 4–6 candid photos matching the existing Interests section: bouldering, cycling, running, cooking)
- New Hugo render-image hook at `themes/minimal/layouts/_default/_markup/render-image.html` that auto-processes any in-bundle markdown image reference (`![alt](images/foo.jpg)`) into a Hugo-processed WebP `<img>` with explicit `width`/`height`, `loading="lazy"` (default), and `decoding="async"` — enables CLS-clean images with zero per-call boilerplate (deferred from Phase 6 as a v2.0 follow-up)
- New CSS section in `themes/minimal/static/css/style.css` (`/* === About === */`) containing `.about-hero`, `.about-hero-img`, `.about-grid`, `.about-grid-item`, `.about-pullquote` rule families — scoped via `body.page-about` (Phase 6's body-class pattern)
- Authored markdown content reusing the existing About copy (Hi / Experience / Education / Certifications / Interests sections preserved verbatim where possible) wrapped with raw HTML class hooks (`<div class="about-hero">…</div>`, `<aside class="about-pullquote">…</aside>`, `<div class="about-grid">…</div>`) — leverages existing `[markup.goldmark.renderer.unsafe = true]`
- One pull-quote inserted in the Experience section showcasing a standout metric (recommend "40% → 95% routing accuracy" or "7,000 daily users across five countries")
- Source-side EXIF scrub on all About images via `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original` before commit (mirrors Phase 6 D-13 procedure)
- Deletion of `content/about.md` after the leaf bundle is in place (Hugo will route `/about/` to the leaf bundle's `index.md` automatically once the standalone file is removed)
- HUMAN-UAT verification: `/about/` URL unchanged, photos render in light + dark themes, CLS < 0.1 on Lighthouse Mobile, no GPS/Make/Model/Serial fields in `public/about/images/*.webp`

**Out of scope:**
- New layout file `themes/minimal/layouts/about/single.html` — `_default/single.html` already renders About correctly; structural richness comes from raw HTML class hooks in markdown + new CSS, not template-level changes (keeps the template surface minimal, consistent with Phase 6's "edit only what's needed" pattern)
- Restructuring About copy beyond inserting layout wrappers and one pull-quote — the existing sections (Experience / Education / Certifications / Interests) are content-complete and out of scope to rewrite
- Lightbox / modal / click-through to full-size for About photos — About is a read-once page, not a gallery (no `<a>` wrappers around `<img>` tags)
- Adding photos to other pages (blog posts, gallery is already covered by Phase 6)
- New `[[menu.main]]` entries — About already exists at `weight = 3` in `hugo.toml` (Phase 6 left it in the correct position)
- Re-running gallery EXIF scrubbing — Phase 6 already cleaned `content/gallery/photos/`
- Switching wordmark / favicon / theme behavior — those are Phases 5 and 05.1, complete
- New `/cv/` page or extracting CV PDF link to a richer download UI — keep the existing `[Download full CV (PDF)](/files/timo-bohnstedt-cv.pdf)` markdown link verbatim
- AVIF format — Hugo 0.157 doesn't support it (REQUIREMENTS § Out of Scope, locked at gallery)
- `srcset` / `<picture>` for responsive images — render-image hook emits a single Hugo-processed WebP per source (matches Phase 6 D-20 rationale: rendered widths stay below 480 px on the hero and 220 px on grid thumbnails, hi-DPI gain is marginal at typical viewing distance)
- Per-photo captions — same deferral as Phase 6 (REQUIREMENTS § Future)
- Photo curation UI / front-matter `photos:` array — alphabetical / authored markdown order is sufficient

</domain>

<decisions>
## Implementation Decisions

### Bundle Structure & URL Preservation

- **D-01:** `content/about.md` is **deleted** and replaced by `content/about/index.md` (leaf bundle). Hugo serves `/about/` from a `content/foo.md` standalone OR from a `content/foo/index.md` leaf bundle interchangeably — the URL is identical in both cases. **Order of operations matters:** create `content/about/index.md` first, verify it builds and serves `/about/` correctly, **then** delete `content/about.md` (avoids a transient state where both files claim the same URL — Hugo would warn about duplicate output).
  - `[auto] Bundle Structure — Q: "How does /about/ resolve after the conversion?" → Selected: "Leaf bundle at content/about/index.md, content/about.md deleted, URL unchanged" (recommended; idiomatic Hugo, mirrors Phase 6 D-01 for /gallery/)`
- **D-02:** Front matter on `content/about/index.md` is **`title: "About"` only** — no `date`, no `draft`, no `summary`, no `description`. This mirrors the current `content/about.md` front matter exactly (single-key) and the gallery leaf bundle pattern (Phase 6 D-01). `_default/single.html` handles missing date with a `{{ if .Date }}` guard, so omitting date is safe.
  - `[auto] Front Matter — Q: "What fields belong on the About leaf bundle?" → Selected: "title only" (recommended; matches existing pattern, no superfluous fields)`

### Layout Strategy (NO custom template file)

- **D-03:** **No new layout file** is created. `/about/` continues to render through `themes/minimal/layouts/_default/single.html` — its existing `<article>` + `.page-header` + `.page-content` shell wraps the About content unchanged. Structural richness (two-column hero, pull-quote, photo grid) is authored as **raw HTML class hooks inline in markdown**, leveraging the existing `[markup.goldmark.renderer.unsafe = true]` setting. Rationale: Phase 6's `gallery/single.html` was justified because the gallery iterates 18 page-bundle resources and needs explicit `image.Process` calls per resource — that template logic does not apply to About, where photos are referenced inline by markdown. Adding `layouts/about/single.html` would require splitting the About markdown into front-matter fields (intro / experience entries / interests array), which is an order of magnitude more refactoring for no rendering benefit.
  - `[auto] Layout File — Q: "Custom layouts/about/single.html or reuse _default/single.html?" → Selected: "Reuse _default/single.html, layout via raw HTML in markdown" (recommended; minimal template surface, no content-front-matter restructuring, fits the existing convention where About is markdown-only)`
- **D-04:** Page-type CSS scoping uses **`body.page-about`** — the body-class pattern from Phase 6 D-10 is already live in `baseof.html` line 26 (`<body class="page-{{ .Type | default "default" }}">`). Hugo derives `Type = "about"` automatically from the leaf-bundle directory name, so the body class becomes `page-about` once the bundle exists. **No `baseof.html` edit required for Phase 7** — Phase 6 already shipped the hook.
  - `[auto] CSS Scoping — Q: "How to scope About's new rules to /about/ only?" → Selected: "body.page-about (Phase 6's existing body-class pattern)" (recommended; reuses already-shipped infrastructure, zero baseof.html churn)`

### Image Pipeline (Hugo render-image hook)

- **D-05:** **NEW: Hugo render-image hook** at `themes/minimal/layouts/_default/_markup/render-image.html` resolves any in-bundle markdown image reference to a Hugo-processed WebP `<img>` with explicit `width`/`height`, `loading="lazy"`, and `decoding="async"`. This was explicitly flagged in Phase 6's `<deferred>` section as a Phase 7 follow-up:
  > "Hugo render-image hook for blog post images — opportunistic future improvement [...] would benefit /about/ (Phase 7) and existing blog posts."

  Hook responsibilities:
  1. Resolve the image path against `.Page.Resources.GetMatch` (page-bundle resource lookup)
  2. If found → process via `image.Process "fill {WIDTH}x{HEIGHT} Smart webp q{QUALITY}"`
  3. Emit `<img>` with `src={{ .RelPermalink }}`, `width={{ .Width }}`, `height={{ .Height }}`, `alt={{ .Text }}`, `loading="lazy"`, `decoding="async"`
  4. If not found (e.g., a remote URL or `/static/...` reference) → fall back to a plain `<img src="{{ .Destination }}" alt="{{ .Text }}">`

  **Default processing dimensions:** `fill 800x600 Smart webp q78` for general inline images. Authored content can override via a **special class hint convention** (see D-06) for the hero portrait and grid thumbnails.

  - `[auto] Image Pipeline — Q: "Per-image shortcode, render-image hook, or raw <img> with manual paths?" → Selected: "Hugo render-image hook (deferred from Phase 6)" (recommended; one-time infrastructure win, generic across blog + about, plain markdown stays plain)`
- **D-06:** **Title-attribute convention for class + dimensions hints.** Markdown image syntax has no class slot, so the render-image hook reads the optional **`title`** field (the third tuple position in `![alt](src "title")`) to determine sizing intent. Convention:
  - `![Portrait of Timo](images/portrait.jpg "hero")` → process at `fill 480x600 Smart webp q80`, emit `<img class="about-hero-img">`
  - `![Bouldering at the gym](images/climbing.jpg "grid")` → process at `fill 400x300 Smart webp q75`, emit `<img class="about-grid-item">`
  - `![Untitled](images/foo.jpg)` (no title) → process at `fill 800x600 Smart webp q78`, emit a plain `<img>` (no extra class)

  The hook reads `.Title` from the AST node and switches on the literal string ("hero" / "grid" / default). Three switch arms cover all current needs; extending later is purely additive.
  - `[auto] Class/Dimension Hints — Q: "How to vary image dimensions per use without a shortcode?" → Selected: "title-attribute convention (![alt](src \"hero\")) parsed in the render-image hook" (recommended; stays in plain markdown, three-arm switch covers hero/grid/default, additive extension)`

- **D-07:** **Loading priority.** The hero portrait is the only above-fold image on `/about/` (the page is text-heavy with one prominent photo at the top). Hook emits **`fetchpriority="high"`** when `title == "hero"` AND `loading="eager"` for the same arm. All grid + default images get `loading="lazy" decoding="async"`. Matches Phase 6 D-06 ("first photo only gets fetchpriority='high'") philosophy applied to About's single-hero shape.
  - `[auto] Loading Priority — Q: "Which About images load eagerly with fetchpriority='high'?" → Selected: "Only the hero portrait" (recommended; one above-fold image, matches Web.dev LCP guidance, ≤120 KB hero thumbnail well inside any reasonable budget)`

### Two-Column Hero (`.about-hero` rule family)

- **D-08:** Hero markup is authored as **raw HTML wrapping the intro paragraph + portrait image reference** at the top of `content/about/index.md`:
  ```html
  <div class="about-hero">
    <div class="about-hero-text">

  ## Hi, I'm Timo.

  I'm a Senior Data Science Consultant at [Erste Group](https://www.erstegroup.com/) in Vienna, where I design AI platforms and deliver GenAI solutions across Central Europe.

  Before that, I worked with Accenture on data engineering, and with Siemens on machine learning and data analytics. I hold a B.Sc. in Information Systems and have an (almost complete) M.Sc. in Computer Science from FAU Erlangen-Nuremberg.

  [Download full CV (PDF)](/files/timo-bohnstedt-cv.pdf)

    </div>
    <div class="about-hero-photo">

  ![Portrait of Timo](images/portrait.jpg "hero")

    </div>
  </div>
  ```
  Goldmark renders the inner markdown blocks because (a) `unsafe = true`, (b) blank lines around the markdown content separate it from the HTML wrappers correctly. The render-image hook (D-05/D-06) processes `images/portrait.jpg` to a WebP at `fill 480x600 Smart webp q80` and emits the `<img class="about-hero-img">` with explicit dimensions.

- **D-09:** **Hero CSS:** CSS Grid two-column on desktop (text 2fr / photo 1fr), single-column stacked on mobile.
  ```css
  body.page-about .about-hero {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    align-items: start;
    margin-bottom: 2.5rem;
  }
  body.page-about .about-hero-photo img {
    width: 100%;
    height: auto;
    border-radius: 6px;
    display: block;
  }
  /* in the existing @media (max-width: 600px) block: */
  body.page-about .about-hero {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  ```
  Locks: 2fr/1fr ratio (text dominant — the page is biographical, photo is anchoring not decorative), 2rem desktop gap, 6px border-radius (slightly stronger than the 4px gallery thumb for visual hierarchy).
  - `[auto] Hero Layout — Q: "Two-column ratio? 1:1, 2:1, 3:1, sidebar?" → Selected: "2:1 (text 2fr / photo 1fr)" (recommended; biographical content is text-heavy, photo anchors without dominating)`
- **D-10:** Hero **does NOT widen the page canvas** — `body.page-about .site-wrapper` keeps the existing `--max-width: 640px` from `:root`. About is read-flow content (paragraphs + lists), not a photo grid; a wider canvas would hurt readability. The wider 1100 px override remains gallery-only (Phase 6 D-09).
  - `[auto] Canvas Width — Q: "Widen About's canvas like /gallery/ did?" → Selected: "Keep 640px (read-flow content)" (recommended; biographical text reads better at narrow measure, hero still feels rich at 2:1)`

### Pull-Quote (`.about-pullquote` rule family)

- **D-11:** **One pull-quote** inserted inside the Erste Group block of the Experience section, callout-style. Authored as raw HTML to keep markdown's blockquote semantics free for any future use:
  ```html
  <aside class="about-pullquote">
    Improved message routing accuracy from <strong>40% → 95%</strong>
  </aside>
  ```
  This metric is the most concrete and impressive line in the existing copy. Other candidates (e.g., "7,000 daily users across five countries") are tracked in Claude's Discretion below — the executor can pick during planning if the user prefers a different highlight.
  - `[auto] Pull-Quote Source — Q: "Which line becomes the pull-quote callout?" → Selected: "40% → 95% routing accuracy (Erste Group block)" (recommended; concrete metric, biggest delta, anchors the Experience visual rhythm)`
- **D-12:** **Pull-quote CSS:** large display text, accent color emphasis, left-border (matches existing `.page-content blockquote` family), generous vertical breathing room. Distinct enough from blockquote to read as "callout" not "quotation".
  ```css
  body.page-about .about-pullquote {
    font-size: 1.4rem;
    font-weight: 500;
    line-height: 1.4;
    color: var(--text);
    border-left: 4px solid var(--accent);
    padding: 0.5rem 0 0.5rem 1.25rem;
    margin: 1.75rem 0;
    background: var(--bg-secondary);
    border-radius: 0 4px 4px 0;
  }
  body.page-about .about-pullquote strong {
    color: var(--accent);
    font-weight: 700;
  }
  ```
  Both light and dark Flexoki palettes already define `--bg-secondary` (light: `#F2F0E5`, dark: `#1C1B1A`) and `--accent` (light: `#AF3029`, dark: `#D14D41`) — the rule reads correctly in both themes via the inherited custom properties.
  - `[auto] Pull-Quote Style — Q: "Pull-quote treatment? Italic / centered / left-bar / boxed?" → Selected: "Left accent bar + bg-secondary fill + accent strong (uses existing Flexoki tokens)" (recommended; visually distinct from blockquote, theme-aware via custom properties)`

### Photo Grid (`.about-grid` rule family)

- **D-13:** **Photo grid** placed at the end of the **Interests** section, displaying 4 candid photos showing the activities mentioned in the copy (bouldering / cycling / running / cooking). Authored as raw HTML wrapping markdown image references:
  ```html
  <div class="about-grid">

  ![Bouldering at the climbing gym](images/climbing.jpg "grid")

  ![Cycling in the Alps](images/cycling.jpg "grid")

  ![Trail running](images/running.jpg "grid")

  ![Cooking](images/cooking.jpg "grid")

  </div>
  ```
  The render-image hook processes each at `fill 400x300 Smart webp q75` (D-06) and emits `<img class="about-grid-item">`.
- **D-14:** **Grid CSS:** 2-column on desktop, 1-column on mobile (compatible with the 640 px page canvas).
  ```css
  body.page-about .about-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin: 1.5rem 0 0;
  }
  body.page-about .about-grid img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 4px;
  }
  /* in the existing @media (max-width: 600px) block: */
  body.page-about .about-grid {
    grid-template-columns: 1fr;
  }
  ```
  Locks: 2-col fixed (not `auto-fill` like gallery — the canvas is narrower at 640 px, so `auto-fill, minmax(220px, 1fr)` would render 2 columns identically anyway, and explicit `repeat(2, 1fr)` is more predictable for a 4-image set), 0.75 rem gap (tighter than gallery's 1 rem because the grid is smaller and visually subordinate to text), 4 px border-radius (matches gallery thumb).
  - `[auto] Grid Layout — Q: "Auto-fill or fixed columns for the About grid?" → Selected: "Fixed 2-col desktop / 1-col mobile" (recommended; predictable for 4 images, fits the 640px canvas without extra logic)`
- **D-15:** **Grid count: 4 photos** at v2.0 ship. Rationale: matches the four interests listed in the existing copy (bouldering, cycling, running, cooking — "reading" doesn't photograph well as a candid). 2-by-2 grid balances visually and stays under 200 KB total at q75 (≈40 KB × 4).
  - `[auto] Photo Count — Q: "How many candid photos in the grid?" → Selected: "4 (one per outdoor interest)" (recommended; matches Interests copy, 2x2 balances visually, fits weight budget)`

### Photo Sourcing (HUMAN-UAT dependency)

- **D-16:** **The user must provide 5 source photos** before plan-execute can complete: 1 portrait + 4 candid activity photos (bouldering / cycling / running / cooking). Recommended naming inside `content/about/images/`:
  - `portrait.jpg` (or `.jpeg` / `.png` — any format Hugo's image pipeline handles)
  - `climbing.jpg`
  - `cycling.jpg`
  - `running.jpg`
  - `cooking.jpg`
  Source photos can come from any of the user's existing photo sets (including potentially overlapping with the 18 gallery photos at `content/gallery/photos/` — but copy them, don't symlink, since each leaf bundle owns its own resource directory). The plan-execute step that adds these photos must run the EXIF scrub (D-17) before commit. **If photos are not yet selected at plan-execute time, this becomes a HUMAN-UAT blocker** and the phase pauses until the user provides them — same pattern as Phase 5's wordmark asset dependency.
  - `[auto] Photo Source — Q: "Where do the 5 About photos come from?" → Selected: "User provides at plan-execute time; treat as HUMAN-UAT blocker if not selected" (recommended; user owns curation, executor can stub-and-pause if needed)`
- **D-17:** **EXIF scrub** uses the same recipe as Phase 6 D-13:
  ```bash
  exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original content/about/images/*.{jpg,jpeg,png}
  ```
  Run **after** the photos land in `content/about/images/` and **before** they are committed. Hugo's existing `[imaging.exif] disableLatLong = true` (in `hugo.toml` from Phase 6) provides the second-line defense on the build-side WebP output. Verification gate after `hugo --minify`:
  ```bash
  exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber public/about/images/*.webp 2>/dev/null
  # Expected: zero matching field reports
  ```
  Same hard launch gate as Phase 6.
  - `[auto] EXIF Strategy — Q: "EXIF strip recipe for About photos?" → Selected: "Reuse Phase 6 D-13 (source-side exiftool + hugo.toml [imaging.exif])" (recommended; pipeline already proven, hugo.toml already configured)`

### Render-Image Hook Detail

- **D-18:** **Hook file location:** `themes/minimal/layouts/_default/_markup/render-image.html`. Hugo automatically uses this for ALL markdown image references site-wide (blog posts and About). The hook is **defensive against legacy blog content** — if the resource lookup fails (image is in `static/`, an external URL, or otherwise out-of-bundle), it falls back to a plain `<img src="{{ .Destination }}" alt="{{ .Text }}">`. This guards existing blog posts (e.g., `content/blog/2026-03-27-video-editing-journey/index.md` and friends) against breakage.
- **D-19:** **Hook source (locked shape):**
  ```go-html-template
  {{- $resource := .Page.Resources.GetMatch (printf "%s" .Destination) -}}
  {{- if $resource -}}
    {{- $title := .Title | default "" -}}
    {{- $isHero := eq $title "hero" -}}
    {{- $isGrid := eq $title "grid" -}}
    {{- $processed := "" -}}
    {{- if $isHero -}}
      {{- $processed = $resource.Process "fill 480x600 Smart webp q80" -}}
    {{- else if $isGrid -}}
      {{- $processed = $resource.Process "fill 400x300 Smart webp q75" -}}
    {{- else -}}
      {{- $processed = $resource.Process "fill 800x600 Smart webp q78" -}}
    {{- end -}}
    <img src="{{ $processed.RelPermalink }}"
         width="{{ $processed.Width }}"
         height="{{ $processed.Height }}"
         alt="{{ .Text }}"
         {{- if $isHero }} class="about-hero-img" loading="eager" fetchpriority="high"{{ else if $isGrid }} class="about-grid-item" loading="lazy" decoding="async"{{ else }} loading="lazy" decoding="async"{{ end -}}>
  {{- else -}}
    <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}"{{ with .Title }} title="{{ . }}"{{ end }}>
  {{- end -}}
  ```
  Whitespace control (`{{-` `-}}`) prevents stray whitespace nodes inside the grid CSS layout. The Title-as-classifier consumes `"hero"` and `"grid"` as keywords and does NOT pass them through to the output (the `<img title="...">` attribute is suppressed for in-bundle resources to avoid leaking the layout intent into the rendered DOM).
  - `[auto] Hook Whitespace — Q: "Use whitespace-trimming or readable formatting in the hook?" → Selected: "Whitespace-trimming with {{- }}" (recommended; CSS Grid layout fragility outweighs template readability)`
- **D-20:** **Risk: render-image hook affects every markdown image site-wide.** Mitigation: the hook's resource lookup uses `.Page.Resources.GetMatch` which only succeeds for in-bundle resources. Existing blog posts use page-bundle relative paths (`![alt](images/foo.png)`), so the hook will start auto-WebP-converting + lazy-loading them too — this is the Phase 6 § Deferred Ideas "opportunistic improvement" landing. **Pre-commit smoke**: build the site cold (`rm -rf resources && hugo --minify`) and visually verify a handful of existing blog posts (recommend `/blog/2026-03-05-climbing-routes/`, `/blog/2026-03-05-activity-overview/`, `/blog/2026-03-27-video-editing-journey/`) render correctly with the new hook active. Any blog-post breakage is a hard blocker.
  - `[auto] Cross-Page Risk — Q: "Acceptable to apply hook globally vs scoping to /about/ only?" → Selected: "Apply globally with cold-build smoke test on existing blog posts" (recommended; lets Phase 6's deferred improvement land for free, smoke-test guards regression)`

### CSS Section Placement

- **D-21:** New `/* === About === */` section in `style.css` placed **immediately after `/* === Gallery === */`** (line 276 area) and before `/* === Footer === */`. Mirrors Phase 6's section-by-content-type ordering convention. All About-specific rules (hero / pullquote / grid) live in this single section. Mobile overrides for About append into the existing `@media (max-width: 600px)` block at the bottom of the file.
- **D-22:** **No new CSS variables** introduced. About's rules consume the existing Flexoki tokens (`var(--text)`, `var(--accent)`, `var(--bg-secondary)`, `var(--border)`) — both light and dark palettes already provide all required values, so theming inherits "for free" the same way Phase 6 D-22 inherits.

### Markdown Content Editing

- **D-23:** **Verbatim copy preservation** — the existing About copy (Hi / Experience / Education / Certifications / Interests sections) transfers from `content/about.md` to `content/about/index.md` **unchanged in wording**. Only structural additions:
  1. Wrap the opening (Hi paragraph + 2 narrative paragraphs + CV link) in `<div class="about-hero">…<div class="about-hero-text">…</div><div class="about-hero-photo">![…]("hero")</div></div>`
  2. Insert `<aside class="about-pullquote">Improved message routing accuracy from <strong>40% → 95%</strong></aside>` after the Erste Group bullet list
  3. Append `<div class="about-grid">…4 image refs…</div>` at the very end of the file (after the Interests paragraph)

  No section reorderings, no new prose, no rewording. The `---` horizontal rules between sections stay (they're CSS-styled via `.page-content hr` and visually separate the major blocks).
  - `[auto] Copy Edits — Q: "Rewrite About copy or preserve verbatim?" → Selected: "Preserve verbatim, structural additions only" (recommended; copy is content-complete, scope creep prevention)`
- **D-24:** **CV download link** stays inline at the top of the hero text block (current placement). No promotion to button-style or sidebar widget — that's polish that belongs in a future iteration if at all.
  - `[auto] CV Link Placement — Q: "Promote the CV download link to a button or move it?" → Selected: "Keep inline at top of hero text" (recommended; current placement works, polish is YAGNI)`

### Verification Gates (HUMAN-UAT-eligible)

- **D-25:** **URL-preservation gate:** after Phase 7 ships, the deployed `/about/` URL must respond 200 with the new content. Local verification:
  ```bash
  hugo --minify
  test -f public/about/index.html && head -20 public/about/index.html | grep -q 'about-hero'
  ```
- **D-26:** **CLS gate:** Lighthouse Mobile CLS < 0.1 on `/about/`. Structurally guaranteed by the render-image hook always emitting explicit `width`/`height` (Hugo provides exact processed-resource dimensions, same mechanism as Phase 6 D-25 GAL-03).
- **D-27:** **EXIF gate:** `exiftool` over `public/about/images/*.webp` after `hugo --minify` reports zero matches for `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, `Serial*`. Block ship if any field surfaces.
- **D-28:** **Theme parity gate:** load `/about/` in light mode, toggle to dark, verify the hero photo + pull-quote + grid all read correctly against the dark palette (no color casting on photos, pull-quote bg + accent contrast adequate, grid borders visible). Same eyeball check pattern as Phase 4 THEME-06 (`/blog/2026-03-05-climbing-routes/` smoke test) and Phase 6 visual smoke.
- **D-29:** **Blog-post regression gate:** because the render-image hook is global (D-20), open at least three existing blog posts after build and verify images still render correctly:
  - `/blog/2026-03-05-climbing-routes/`
  - `/blog/2026-03-05-activity-overview/`
  - `/blog/2026-03-27-video-editing-journey/`
  Look for: images load, no broken references, no CLS regression, lazy-loading works (scroll the page and watch network tab fetch images on-demand).
- **D-30:** **`content/about.md` deletion gate:** after `content/about/index.md` is in place AND verified to render at `/about/`, delete `content/about.md` and rebuild. Run `grep -r "content/about\.md" .` to confirm no references linger (none expected).

### Claude's Discretion

- Whether the pull-quote uses `<strong>40% → 95%</strong>` for emphasis (recommended in D-11) or alternatives like the "7,000 daily users" metric. Both are defensible; planner can pick during execution and surface as a tiny variation point in HUMAN-UAT.
- Whether the hero photo uses `border-radius: 6px` (D-09 recommendation) or `4px` (matches gallery thumb). 6px gives the hero a slightly distinct visual weight — worth a one-row eyeball test, can revert to 4px if it feels off.
- Whether to add `aria-label="Open full-size photo"` on grid photos. About grid photos do NOT click through to full-size (D-13 doesn't wrap in `<a>`), so no aria-label is needed there. The hero photo also does not click through.
- Whether the render-image hook should add `class="page-content-img"` (or similar) on the default arm to allow blog-specific styling distinct from About. Recommend: NO — adding a class to existing blog-post images is a behavior change that risks breaking the existing CSS rule `.page-content img { max-width: 100%; height: auto; border-radius: 4px; margin: 1.5rem 0; }`. Keeping default-arm output classless preserves the existing cascade.
- Whether to add `<picture>` with multiple breakpoints for the hero (180px / 480px / 960px srcset). Recommend NO at v2.0 ship — single 480x600 q80 WebP is ~50–80 KB, hi-DPI gain marginal. Same rationale as Phase 6 D-20.
- Whether to scope `body.page-about .about-hero-photo img` selector vs the `.about-hero-img` class. Both work — class-based is more explicit and survives template churn better. Recommend the class-based selector for D-09's photo CSS.
- Whether the grid CSS uses `repeat(2, 1fr)` (D-14 default) vs `repeat(auto-fit, minmax(180px, 1fr))`. The fixed pattern is simpler for 4 known images; the auto-fit pattern would handle dynamic counts better but is YAGNI now. Recommend D-14 default.
- Whether to add a `.gitkeep` to `content/about/images/` if photos arrive in a separate plan-execute step. Probably unnecessary if photo arrival is atomic with the conversion commit.
- Whether to commit a placeholder portrait (e.g., a silhouette SVG) for the conversion commit and have the user swap real photos in a follow-up. Recommend: no placeholder — block on real photos to keep the phase clean (one phase = one cohesive deploy).
- Whether the title-attribute switch (D-06) handles unknown values defensively (e.g., `"hero!"` typo): recommend the `else` arm catches all non-"hero"/non-"grid" titles and processes at the default `800x600 q78` — already locked in D-06 + D-19.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & Requirements
- `.planning/ROADMAP.md` § "Phase 7: About Enrichment" — phase goal (leaf-bundle conversion + richer multi-photo layout), 3 success criteria (URL preserved, multi-photo richer layout with second-column / photo-grid / pull-quote CSS rules, CLS-clean width/height + page-bundle resources), depends on Phase 6 (leaf-bundle pattern proven), UI hint flag
- `.planning/REQUIREMENTS.md` § "About Page" — ABOUT-01 (`content/about.md` → `content/about/index.md`, `/about/` URL unchanged), ABOUT-02 (richer layout, second-column / photo-grid / pull-quote CSS rules, NOT single-column inline-only), ABOUT-03 (page-bundle resources at `content/about/images/`, explicit width/height for CLS, light + dark theme parity)
- `.planning/REQUIREMENTS.md` § "Future Requirements" — native `<dialog>` lightbox, per-photo captions, view-transition cross-fades — all DEFERRED, do not implement at Phase 7
- `.planning/REQUIREMENTS.md` § "Out of Scope" — JS lightbox library, AVIF, masonry/infinite-scroll/filters — REJECTED, applies transitively to About
- `.planning/PROJECT.md` § "Constraints" — Hugo static, no JS frameworks, vanilla JS only, accessibility (the keyboard reachability of `[Download CV PDF]` link is unchanged from current; no new interactive elements added that need keyboard handling)
- `.planning/PROJECT.md` § "Key Decisions" — Phase 6's locks (Hugo image processing, leaf-bundle pattern, body-class scoping) all carry forward to Phase 7

### Cross-Phase Contracts (incoming)
- `.planning/phases/04-theming-foundation/04-CONTEXT.md` § "D-01" — `[data-theme]` attribute is set on `<html>` by the head IIFE before stylesheet parse. About inherits theming for free; pull-quote uses `var(--bg-secondary)` and `var(--accent)` so it adapts to the active theme automatically.
- `.planning/phases/05-wordmark-favicon-wiring/05-CONTEXT.md` § Cross-phase contracts — favicon partial pattern unchanged; About does not modify `<head>`.
- `.planning/phases/05.1-swap-wordmark-favicon-to-new-svg-sources/05.1-CONTEXT.md` § "Cross-Phase Contracts (outgoing)" — inline-SVG-with-`currentColor` pattern available if About ever needs a small decorative icon. Phase 7 ships no such icons in the locked scope.
- `.planning/phases/06-gallery/06-CONTEXT.md` § "D-10" — body-class pattern (`<body class="page-{{ .Type | default "default" }}">` already in `baseof.html` line 26). Phase 7 reuses for `body.page-about` scoping. **No baseof.html edit required.**
- `.planning/phases/06-gallery/06-CONTEXT.md` § "D-13, D-14" — EXIF scrub recipe. `[imaging.exif] disableLatLong = true` already in `hugo.toml` (verified). Source-side exiftool scrub mirrored in Phase 7 D-17.
- `.planning/phases/06-gallery/06-CONTEXT.md` § "Deferred Ideas" — explicitly identifies "Hugo render-image hook for blog post images" as an opportunistic Phase 7 follow-up. Phase 7 D-05 lands this.
- `.planning/phases/06-gallery/06-CONTEXT.md` § "Cross-Phase Contracts (outgoing) → To Phase 7" — confirms body-type class + leaf-bundle + page-bundle-resource patterns are ready to consume.

### Codebase Conventions & Files
- `themes/minimal/layouts/_default/baseof.html` (currently 58 lines) — **READ-ONLY for Phase 7.** Body-class hook already shipped (line 26: `<body class="page-{{ .Type | default "default" }}">`); Hugo will derive `Type = "about"` from the leaf bundle directory automatically. No edits required.
- `themes/minimal/layouts/_default/single.html` (currently 13 lines) — **READ-ONLY for Phase 7.** Renders About via `<article>` + `.page-header` + `.page-content` shell. The page-title text becomes "About" (from front matter) and renders as `<h1 class="page-title">About</h1>` above the hero block — that's intended (provides nav/SEO heading anchor).
- `themes/minimal/layouts/_default/_markup/render-image.html` — **NEW (D-05, D-19).** Hugo render-image hook. Resolves bundle-relative image paths to processed WebP `<img>` tags with explicit dimensions, lazy/eager loading, fetchpriority on hero, decoding="async". Title-attribute switch for hero/grid/default sizing. Defensive fallback for non-bundle images.
- `themes/minimal/static/css/style.css` (currently 350 lines, last edited Phase 6) — **EDIT.** Append a new `/* === About === */` section between the existing `/* === Gallery === */` (line ~276) and `/* === Footer === */` (line ~306) sections containing `.about-hero` CSS Grid, `.about-hero-photo img` sizing, `.about-pullquote` callout, `.about-grid` 2-col grid, `.about-grid img` sizing — all scoped via `body.page-about`. Append mobile overrides for `.about-hero` (1-col stack) and `.about-grid` (1-col) into the existing `@media (max-width: 600px)` block at the bottom (line ~344).
- `content/about.md` (currently 51 lines) — **DELETE after conversion.** Source content (sections + copy) preserved verbatim into `content/about/index.md`. Deletion order: create new bundle first, verify, then delete legacy file (D-01).
- `content/about/index.md` — **NEW.** Leaf-bundle index. Front matter: `title: "About"` only (D-02). Body: existing About copy preserved verbatim with three structural raw-HTML wrappers added — `<div class="about-hero">` around the intro block (D-08), `<aside class="about-pullquote">` after the Erste Group experience block (D-11), `<div class="about-grid">` at the end (D-13).
- `content/about/images/` — **NEW.** Page-bundle resource directory. Contains 5 user-provided photos (1 portrait + 4 candid activity photos), EXIF-scrubbed via D-17 recipe before commit.
- `hugo.toml` (currently 39 lines, last edited Phase 6) — **READ-ONLY for Phase 7.** Menu entry for About already at correct `weight = 3`. `[imaging.exif] disableLatLong = true` already present. `[markup.goldmark.renderer.unsafe = true]` already present (required for raw HTML wrappers in D-08, D-11, D-13). No edits required.
- `static/files/timo-bohnstedt-cv.pdf` — **READ-ONLY.** Existing CV file referenced by the inline `[Download full CV (PDF)](/files/timo-bohnstedt-cv.pdf)` link in About copy. Path stays valid after the conversion (it's a `static/` reference, not a page-bundle resource).
- `.planning/codebase/CONVENTIONS.md` § "HTML Template Conventions" — Hugo Go templates, 2-space indentation, partials, `{{ with }}` / `{{ if }}` patterns. Render-image hook (D-19) follows these.
- `.planning/codebase/CONVENTIONS.md` § "CSS Conventions" — Flexoki palette tokens, `kebab-case` class names, section comments `/* === Section Name === */`. About CSS rules introduce the `.about-*` family — fits the convention.
- `.planning/codebase/STRUCTURE.md` § "Where to Add New Code → New Static Page" — current pattern (top-level `content/foo.md` + menu entry); Phase 7 mirrors Phase 6 in upgrading the pattern to a leaf bundle for image-heavy pages, and ALSO drops the legacy `content/foo.md` form for About.

### Hugo Documentation (research-flagged)
- Hugo render-image hook reference (Markdown render hooks for images) — confirm `.Page.Resources.GetMatch` semantics for bundle-relative `.Destination`, confirm `.Title` accessor returns the third-tuple title field of `![alt](src "title")` syntax, confirm rendering scope (which markdown calls trigger the hook — answer: every `![alt](url)` site-wide unless overridden per-format/per-content-type)
- Hugo image processing reference — empirical tuning of `Process "fill 480x600 Smart webp q80"` on a real portrait orientation phone shot (often 4032×3024 or similar) — confirm `Smart` crop centroid behaves on portrait subjects (face-priority), validate q80 is the right quality for a single hero image (subjective; user can tune in HUMAN-UAT)
- Hugo `.Resources.GetMatch` vs `.Resources.Match` — `GetMatch` returns first match (single resource); the render hook needs `GetMatch` for the by-name lookup since each markdown image references a single resource
- Hugo render-hook fallback patterns — best-practice for emitting a passthrough `<img>` when the resource isn't in the bundle (matches D-19 fallback arm)

### Cross-Phase Contracts (outgoing)
- **To future blog posts and image-heavy pages:** the render-image hook (D-05, D-19) is now a codebase-validated piece of infrastructure. Authors can add images to any leaf bundle by writing plain markdown `![alt](images/foo.jpg)` and the hook auto-processes to WebP with explicit width/height + lazy-loading. The `"hero"` and `"grid"` title keywords are reserved sizing hints; new keywords can be added later (additive switch arm in `render-image.html`).
- **To future phases:** the title-attribute-as-classifier convention is a lightweight pattern for varying image processing without introducing shortcodes. If a future phase needs a third or fourth image variant (e.g., "banner" for full-bleed hero images on long-form posts), add a new switch arm in the hook.
- **To future phases:** the leaf-bundle pattern is now applied to two top-level pages (`/gallery/` from Phase 6, `/about/` from Phase 7). Future image-heavy standalone pages (e.g., a hypothetical `/projects/`) follow the same shape: `content/{slug}/index.md` + `content/{slug}/images/` + `body.page-{slug}` CSS scoping.
- **To future phases:** the pull-quote pattern (`<aside class="about-pullquote">`) is About-specific today, but the CSS could be generalized to a `.pullquote` family if more pages adopt the callout. Out of scope for Phase 7.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`themes/minimal/layouts/_default/baseof.html`** (58 lines, Phase 6 already shipped body-class hook on line 26) — Phase 7 needs zero edits. The body class `page-about` materializes automatically when `Type = "about"` is derived from the leaf-bundle directory.
- **`themes/minimal/layouts/_default/single.html`** (13 lines) — `<article>` + `.page-header` + `.page-content` shell. About content (after conversion) renders inside `.page-content`, where the existing `.page-content img { max-width: 100%; height: auto; border-radius: 4px; margin: 1.5rem 0; }` rule provides a sane default for any image not specifically classed by the render-image hook. Critical: the new `.about-hero-img` and `.about-grid-item` classes override `max-width: 100%` with their own width-100 / display-block / border-radius rules — verify rule specificity at execute time.
- **`themes/minimal/static/css/style.css`** (350 lines, last edited Phase 6) — section-comment convention (`/* === Section Name === */`), single stylesheet, Flexoki custom-property palette in `:root` and `:root[data-theme="dark"]`. About rules slot in cleanly after Gallery rules.
- **`hugo.toml`** — `[markup.goldmark.renderer.unsafe = true]` (line 12 area) already enables raw HTML in markdown, which is load-bearing for D-08 / D-11 / D-13 wrappers. `[imaging.exif] disableLatLong = true` already in place from Phase 6. About menu entry at `weight = 3` already correct.
- **GitHub Actions deploy workflow** (`.github/workflows/hugo.yml` per STRUCTURE.md, actually `.github/workflows/deploy.yml` per CLAUDE.md — one of those is the canonical name; verify at execute) — `HUGO_CACHEDIR` already set; the cold first-build with the new render-image hook active will re-process all blog post images too (one-time cost, ~10–20 s in CI per Phase 6 D-21 estimate, scaled by image count across all bundles).
- **`content/about.md`** (51 lines) — source copy for the conversion. All sections and prose preserved verbatim per D-23 (Hi / Experience / Education / Certifications / Interests / horizontal rules between sections).
- **`static/files/timo-bohnstedt-cv.pdf`** — existing CV download referenced by the hero text block. Path stays valid after the conversion.

### Established Patterns
- **Page-bundle resources** — every blog post under `content/blog/YYYY-MM-DD-slug/` already uses `images/` subdirectory for co-located images. About adopts the same shape at `content/about/images/`.
- **Leaf-bundle for image-heavy standalone pages** — Phase 6 established `content/gallery/index.md` + `content/gallery/photos/`. Phase 7 mirrors with `content/about/index.md` + `content/about/images/`. Note the resource subdirectory naming difference: `photos/` (gallery, suggests a gallery's intent) vs `images/` (about, matches blog-post convention since About isn't a "photo" page per se). Both work; the about/images naming aligns with blog-post precedent and the render-image hook treats them identically.
- **Body-class CSS scoping** (`body.page-{{ .Type }}`) — introduced Phase 6 D-10, now the established pattern. About uses `body.page-about` for hero/pullquote/grid scoping so other pages aren't affected.
- **Hugo image processing via `image.Process "fill WxH Smart webp qN"`** — Phase 6 GAL-03 / GAL-04 locked the verb (`fill` for thumbnails, `fit` for unconstrained-aspect full-size). Phase 7 uses `fill` exclusively (hero is portrait-oriented, grid is landscape — both crop deliberately).
- **EXIF scrub via exiftool** — Phase 6 D-13 / D-17 procedure. Phase 7 D-17 reuses verbatim.
- **Raw HTML in markdown** — `[markup.goldmark.renderer.unsafe = true]` enables wrappers like `<div class="about-hero">…</div>` to interleave with markdown content. Existing pattern: blog post `content/blog/2026-03-05-climbing-routes/index.md` uses raw `<script>` and `<div>` blocks for inline visualizations — proven at-scale.
- **Section comments in style.css** — `/* === Section Name === */` precedes each rule family. About follows.
- **Hugo `Type` derivation from directory name** — Phase 6 confirmed `content/gallery/index.md` → `Type = "gallery"` → body class `page-gallery` and layout lookup `gallery/single.html`. Phase 7 piggybacks: `content/about/index.md` → `Type = "about"` → body class `page-about`. (No `layouts/about/single.html` is created — `_default/single.html` resolves at fallback per D-03.)

### Integration Points
- **`content/about/index.md`** — NEW leaf bundle. Front matter `title: "About"` only. Body: existing copy + three raw HTML wrappers (hero, pullquote, grid).
- **`content/about/images/`** — NEW page-bundle resource directory. 5 user-provided photos (1 portrait + 4 candids), EXIF-scrubbed before commit.
- **`themes/minimal/layouts/_default/_markup/render-image.html`** — NEW. Hugo render-image hook with title-keyword switch (hero/grid/default), in-bundle resource lookup with passthrough fallback for legacy/external image refs.
- **`themes/minimal/static/css/style.css`** — EDIT. Append `/* === About === */` section block (hero / pullquote / grid rules, `body.page-about` scoped), append mobile overrides into existing `@media (max-width: 600px)` block.
- **`content/about.md`** — DELETE after the leaf bundle is verified to render `/about/` correctly (D-30).
- **`baseof.html`** — NO EDIT. Body-class hook from Phase 6 covers Phase 7's needs.
- **`hugo.toml`** — NO EDIT. All required config (menu, EXIF, unsafe markdown) already present.

### Hugo-Specific Notes
- **Hugo URL routing for `/about/`** — both `content/about.md` and `content/about/index.md` produce the URL `/about/` identically. Hugo prints a warning ("REF_NOT_FOUND" or similar duplicate-permalink warning) if both exist simultaneously. **Order: create the bundle, verify, then delete the standalone file.** A transient state where both exist for the same commit is acceptable for the verification step but must not survive into the deployed build.
- **Render-image hook scope** — Hugo applies `_default/_markup/render-image.html` to ALL markdown image references site-wide unless a more-specific override exists at `{layout}/_markup/render-image.html`. The hook's resource-lookup-with-fallback (D-19) handles both leaf-bundle images (page-bundle resources) and out-of-bundle images (legacy `static/...` paths or remote URLs) gracefully.
- **`.Page.Resources.GetMatch` path resolution** — markdown `![alt](images/portrait.jpg)` produces `.Destination = "images/portrait.jpg"`. `GetMatch "images/portrait.jpg"` matches a resource at `content/about/images/portrait.jpg` when the render hook runs in the `content/about/index.md` page context. The relative-path semantics are the load-bearing detail of the hook's correctness.
- **Title attribute parsing** — `![alt](src "hero")` puts `"hero"` at `.Title` in the AST. Markdown parser strips the surrounding quotes; the hook reads the bare string. `![alt](src)` (no title) sets `.Title = ""`; the default switch arm catches that.
- **Mobile breakpoint** — existing `@media (max-width: 600px)` at line ~344 of style.css. Append two rules: `body.page-about .about-hero { grid-template-columns: 1fr; gap: 1.5rem; }` and `body.page-about .about-grid { grid-template-columns: 1fr; }`.
- **Image processing cache** — `resources/_gen/images/` is gitignored (verified per Phase 6 D-21). Render-image-hook-driven processing populates the cache the same way explicit `image.Process` calls in `gallery/single.html` do.
- **Front matter `Type` override** — not needed. Hugo correctly derives `Type = "about"` from the directory name; no `type: about` line is required in front matter.

</code_context>

<specifics>
## Specific Ideas

- **Pull-quote target metric:** D-11 selects "Improved message routing accuracy from 40% → 95%" as the standout line. Alternative candidates from existing copy: "AI platform on Azure & Databricks serving 7,000 daily users across five countries" or "2nd place at an international GenAI hackathon (300 participants)". Planner can swap if user prefers a different highlight; visual treatment from D-12 fits any of them.
- **Hero photo subject:** a portrait of Timo (face-front or 3/4-front, vertically oriented to suit the 480×600 aspect). Will be cropped via Hugo's `Smart` to face-priority entropy; if the source is panoramic/landscape, the crop will land on the centroid which may not capture the face — recommend the user provide a portrait-orientation source. Alternative: a portrait shot in an environment that fits Timo's interests (climbing crag, alpine cycling, kitchen) — works equally well as long as the face is recognizable in the 480×600 crop.
- **Photo grid subjects:** one image per outdoor interest mentioned in the existing Interests section — bouldering, cycling, running, cooking. "Reading" is also listed but doesn't photograph well as a candid; deliberately omitted from the 4-image grid (D-15).
- **Visual smoke test (HUMAN-UAT):** load `/about/` in dark mode (toggle from Phase 4 active), verify (a) hero photo reads against dark Flexoki bg without color cast, (b) pull-quote reads against dark `--bg-secondary` (#1C1B1A) with `--accent` (#D14D41) emphasis, (c) grid photos read against dark bg, (d) page-title `About` heading is visible. Then toggle to light, repeat.
- **Cold-build smoke (regression guard for D-20):** `rm -rf resources && hugo --minify`, then verify three blog posts render correctly: `/blog/2026-03-05-climbing-routes/`, `/blog/2026-03-05-activity-overview/`, `/blog/2026-03-27-video-editing-journey/`. If any blog post images break, the render-image hook needs a defensiveness fix before ship.
- **Photo weight sanity:** hero at 480×600 q80 ≈ 60–90 KB, 4 grid thumbs at 400×300 q75 ≈ 30–50 KB each = 120–200 KB. Page total well under 500 KB for first-paint. No first-paint weight gate ceiling required for `/about/` at this scope (gallery's 2 MB ceiling does not apply here, but eyeball watch network tab during smoke).
- **CLS gate:** Lighthouse Mobile CLS < 0.1. Structurally guaranteed by render-image hook always emitting `width` and `height` from `.Process` output dimensions.
- **EXIF gate (privacy hard launch criterion):** zero `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, `Serial*` fields in `public/about/images/*.webp` after `hugo --minify`. Block ship on any hit. Same scrutiny as Phase 6 GAL-06.
- **URL preservation gate (ABOUT-01):** after deploy, `https://tbohnstedt.cloud/about/` returns 200 with the new content. Local check: `test -f public/about/index.html`.
- **`content/about.md` deletion gate (cleanup):** `grep -r "content/about.md" .` returns zero hits after deletion (no stale references in `.planning/`, themes, or other content). The existing `.planning/REQUIREMENTS.md` ABOUT-01 line says "converted to" (process-language) so it's not a back-reference — verify.
- **No new menu changes:** verified. About already at `[[menu.main]] weight = 3` in `hugo.toml`. Page-bundle conversion does not alter URL or menu order.
- **CV PDF link survives the conversion:** `[Download full CV (PDF)](/files/timo-bohnstedt-cv.pdf)` is a `/static/files/...` reference — out-of-bundle by design. The render-image hook's fallback arm doesn't apply (it's an `<a>`, not an `<img>`); the link renders unchanged through Goldmark's standard link rendering.
- **HUMAN-UAT photo-curation pause:** if the user hasn't selected the 5 photos at plan-execute time, the executor must explicitly pause and surface the request before continuing. Same pattern as Phase 5's wordmark asset pause (an asset-dependency block, not a code-fix block).

</specifics>

<deferred>
## Deferred Ideas

- **Per-photo captions on the hero portrait or grid photos** — REQUIREMENTS § Future. Empty alt for grid (decorative; the photos illustrate the Interests section, the section header carries the meaning) and a meaningful alt for the hero portrait ("Portrait of Timo") is sufficient at v2.0 ship. Curated caption strings under each grid photo would add about 1.5–2 lines vertical per row; pairs naturally with a future "About expanded" milestone.
- **Per-experience photo callouts** (e.g., a photo per company in the Experience section) — would clutter the read-flow at the current 640 px canvas. Defer to a future redesign that widens About's canvas if image density grows.
- **Native `<dialog>` lightbox for hero / grid photos** — REQUIREMENTS § Future, applies transitively to About. Today: no click-through (D-13). Future progressive enhancement.
- **`srcset` / `<picture>` for hi-DPI portraits** — D-19 emits a single Hugo-processed WebP; hi-DPI gain is marginal at 480×600 rendered at most 320 px wide on desktop and 100% screen width on mobile. Add later if Lighthouse Mobile flags image quality.
- **AVIF format** — REQUIREMENTS § Out of Scope, blocked by Hugo 0.157. Revisit when Hugo upgrades.
- **Title-keyword extension** — current hook switch handles `"hero"` / `"grid"` / default. Future use cases (e.g., a "banner" full-bleed image on a hypothetical `/projects/` page or in a long-form blog post) extend the switch additively. Adding a fourth keyword requires editing only `render-image.html` + adding a CSS class rule — no content-file changes.
- **Generalized `.pullquote` rule family** — Phase 7 ships `.about-pullquote` scoped to `body.page-about`. If blog posts or other pages adopt the callout, generalize to `.pullquote` and lift the body-class scope. Out of scope for Phase 7.
- **CV download as a button-styled link** — D-24 keeps the inline markdown link. A dedicated button with an icon (e.g., download arrow SVG, `var(--accent)` background) would be visual polish; defer to a future v2.x.
- **Two-column layout for the Experience section** (left: company name + dates, right: bullet list of achievements) — would visually strengthen the experience section but requires either splitting bullet content into front matter or much more involved raw HTML in markdown. Hero two-column at the top is sufficient for ABOUT-02 satisfaction.
- **Personalized 404 / error page or sitemap surface for `/about/`** — out of milestone scope.
- **Tracking the conversion's impact on Lighthouse PageSpeed scores** — the render-image hook lazy-loads + WebP-converts existing blog post images as a side effect of D-20. This should be a positive Lighthouse delta but is observational, not a hard gate. Recommend a quick before/after note in the HUMAN-UAT after deploy.
- **Hugo render-link hook** for blog-post links (analogous to render-image) — would let us inject `target="_blank" rel="noopener"` on outbound links automatically. Out of scope; current `[Download CV PDF]` and Erste Group links work fine without it.
- **Splitting About content into structured front-matter sections** — would enable a custom `layouts/about/single.html` template iterating through experiences/education/certifications arrays. Larger refactor, no rendering benefit at 5 sections; defer indefinitely (current copy is content-complete).
- **Photo-set rotation** — having multiple hero portraits cycle on reload, or an interest grid that randomizes each visit. Out of milestone scope (no JS framework; cycling via vanilla JS would be possible but adds complexity for marginal personalization).

</deferred>

---

*Phase: 07-about-enrichment*
*Context gathered: 2026-04-30*

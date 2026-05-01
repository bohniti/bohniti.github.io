# Architecture Patterns — v3.0 Design Update

**Domain:** Hugo personal site (existing custom theme `minimal/`)
**Researched:** 2026-05-01
**Scope:** Integration of three v3.0 features into the existing architecture — SVG icon theme toggle, lightbox + randomized masonry gallery, dynamic About redesign. Existing architecture is NOT re-researched; only deltas are described.
**Confidence:** HIGH (all touchpoints verified by reading current files; one external claim — `collections.Shuffle` non-determinism — verified against gohugo.io)

---

## Existing architecture (touchpoints only)

| Component | Path | Role for v3.0 |
|-----------|------|---------------|
| Base layout | `themes/minimal/layouts/_default/baseof.html` | Hosts no-FOUC `<head>` IIFE, end-of-body theme-toggle handler, `<body class="page-{{ .Type | default "default" }}">` — feature (a) modifies handler; feature (b) needs lightbox JS; feature (c) flips body class |
| Header partial | `themes/minimal/layouts/partials/header.html` | Holds `<button class="theme-toggle">Dark</button>` — feature (a) replaces text with inline SVG |
| Render-image hook | `themes/minimal/layouts/_default/_markup/render-image.html` | Title-keyed (`hero` / `grid` / default) sizing for About images — feature (c) reuses, optionally extends with new keys |
| Gallery layout | `themes/minimal/layouts/gallery/single.html` | Currently emits `<a href="full">` link wrapping thumb — feature (b) repurposes anchors as lightbox triggers, adds caption resource lookup, adds shuffle |
| Gallery bundle | `content/gallery/index.md` (+ `photos/` resources) | Page bundle with `build.publishResources: false`. Resources accessed via `.Resources.Match "photos/*"` — feature (b) extends with caption metadata |
| About bundle | `content/about/index.md` (+ `images/`) | Leaf bundle, `type: "about"` → `body.page-about` — feature (c) drives layout switch by `type` |
| Stylesheet | `themes/minimal/static/css/style.css` | Single file, scoped via `body.page-*` — all three features add rules here (no new CSS file) |
| Theme bootstrap | inline `<head>` IIFE in `baseof.html` | Sets `documentElement.dataset.theme` before paint — feature (a) does NOT touch this |
| Footer SVG icons | `themes/minimal/layouts/partials/footer.html` | Existing pattern: 18×18 inline SVG, `stroke="currentColor"`, `aria-hidden="true"`, `aria-label` on parent — feature (a) follows this exact pattern |

**Hugo version:** 0.157.0 (extended) pinned in `.github/workflows/deploy.yml`.

---

## Recommended architecture per feature

### (a) SVG icon-button theme toggle

```
header.html
  ├── <button class="theme-toggle" aria-label="Toggle dark mode" aria-pressed="false">
  │     ├── <svg class="icon-sun"   …>  (visible when [data-theme="light"])
  │     └── <svg class="icon-moon"  …>  (visible when [data-theme="dark"])
  └── (NO partial extraction — same pattern as footer.html GitHub/Instagram icons)

baseof.html (end-of-body handler)
  └── click → toggle data-theme + aria-pressed + localStorage + meta theme-color
              (textContent line REMOVED; CSS drives icon swap)

style.css
  └── .theme-toggle .icon-moon { display: none; }
      :root[data-theme="dark"] .theme-toggle .icon-sun  { display: none; }
      :root[data-theme="dark"] .theme-toggle .icon-moon { display: block; }
```

**One concrete recommendation per question:**

| Question | Decision | Rationale |
|----------|----------|-----------|
| Where does the SVG live? | **Inline in `header.html`** (both icons) | Matches the established footer.html pattern (GitHub + Instagram inline 18×18 SVGs, `currentColor`). No new file, no Hugo asset pipeline, no extra HTTP request. Two ~200-byte `<path>` snippets weigh less than one `readFile`. |
| How does icon swap work? | **Two SVGs toggled via `display: none` driven by `[data-theme]` ancestor selector** | Zero JS coupling — the click handler only flips `data-theme`; CSS handles visibility. CSS-driven path-morph (single SVG, animate `d`) is over-engineered for a static minimal aesthetic. Two SVGs is the same approach as the existing wordmark recolor pattern, just with display instead of `currentColor`. |
| What changes in `header.html` and the click handler vs current text-button? | **`header.html`:** replace `>Dark</button>` with two `<svg>` children + add `aria-label="Toggle dark mode"`. **Handler:** delete the `toggle.textContent = …` line in both the first-paint sync block and the click callback (lines 45 and 51 of `baseof.html`). Keep `aria-pressed` updates. | The text was the visible state; CSS now is. `aria-pressed` remains the authoritative a11y state. No state sync issue because CSS reads `data-theme` directly. |
| Risk of FOUC during icon swap — does the inline `<head>` IIFE need updating? | **No** — IIFE already sets `documentElement.dataset.theme` before first paint (line 19 of `baseof.html`). | CSS `:root[data-theme="dark"]` selectors apply on the first paint after the IIFE runs. Since both SVGs are inline in the HTML, the correct one is shown immediately. **Caveat:** the wrong icon would briefly flash only if CSS loaded before the inline IIFE ran — but the IIFE runs before the `<link rel="stylesheet">` tag (lines 11–23 vs line 24), so this is impossible. |

**Files modified:** `themes/minimal/layouts/partials/header.html`, `themes/minimal/layouts/_default/baseof.html`, `themes/minimal/static/css/style.css`.
**Files created:** none.

**Risk callout:** the existing handler also overwrites `textContent` on first-paint sync. Forgetting to delete that line would inject the string "Dark" or "Light" between the two SVGs as a text node. Verify by checking `toggle.children` instead of `toggle.textContent` in the post-build DOM.

---

### (b) Lightbox + randomized masonry gallery

```
content/gallery/
  ├── index.md                 (front matter only — no per-photo data)
  └── photos/
      ├── DSC09782.JPG
      ├── DSC09782.md          ← NEW: caption sidecar  (resource metadata)
      ├── IMG_2009.jpeg
      ├── IMG_2009.md          ← NEW
      └── … (one .md per image)

themes/minimal/layouts/
  └── gallery/single.html      ← MODIFIED: shuffle + caption + lightbox triggers
                                 (no new layout file — gallery is a leaf bundle, single.html applies)

themes/minimal/static/
  ├── css/style.css            ← MODIFIED: column-count masonry + .lightbox rules
  └── js/lightbox.js           ← NEW: ~80 LOC vanilla, IIFE pattern (matches existing inline JS style)

baseof.html
  └── <script src="js/lightbox.js" defer></script>  ← NEW: gated by body.page-gallery
        OR: emit only on gallery page from gallery/single.html (preferred — see below)
```

**One concrete recommendation per question:**

| Question | Decision | Rationale |
|----------|----------|-----------|
| Where do captions live? | **Per-photo `.md` sidecar inside the page bundle** (e.g. `content/gallery/photos/DSC09782.md` next to `DSC09782.JPG`). Each sidecar carries `title:` (caption) and optional `description:` front matter. Read in template via `$photo.Title` and `$photo.Params.description`. | Hugo natively binds a `.md` sidecar to a page-bundle Resource of the same basename — this is the documented pattern for resource metadata. **Authoring path:** drop a JPG, drop a 3-line `.md` next to it. Single file edit per photo. **Rejected alternatives:** (1) Front-matter `resources:` list in `gallery/index.md` — loses ordering robustness (must reference each by `src:` glob), bloats the index, and forces re-ordering on each photo add. (2) YAML data file at `data/gallery.yaml` — divorces caption from photo, breaks page-bundle co-location principle established in v2.0. |
| Does existing `image.Process` pipeline still drive thumbnails, with lightbox showing `q82` full? | **Yes — exact same pipeline, no changes to processing parameters.** Existing `single.html` already produces both `$thumb` (`fill 600x400 webp q75`) and `$full` (`fit 1200x1200 webp q78`). Lightbox swaps in the `$full.RelPermalink` already wired to `<a href>`. | Reusing the existing pipeline preserves the v2.0-validated ≤ 2 MB first-paint and CLS < 0.1 invariants. The lightbox merely intercepts the click; the resource graph is unchanged. **Note:** quality is q78 on the full (per current code), not q82 as the question phrases it — keep at q78. |
| New layout file at `gallery/list.html` or `_default/section.html`? | **Neither — keep `gallery/single.html` as-is and modify it.** | The gallery is configured as a leaf bundle (`content/gallery/index.md`, no children pages). Hugo's lookup chain resolves leaf bundles to `single.html`, not `list.html` or `section.html`. Adding either would be a no-op file. Verify via `hugo --templateMetrics` if uncertain. |
| Where does the lightbox JS live? | **New file `themes/minimal/static/js/lightbox.js` loaded from `gallery/single.html` (NOT `baseof.html`).** Use `<script src="{{ "js/lightbox.js" | absURL }}" defer></script>` at the bottom of `gallery/single.html`'s `{{ define "main" }}` block. | Loading from `baseof.html` ships ~80 LOC of unused JS to every page. Loading from the gallery template ships it only where used. The existing `static/` directory already serves a precedent (favicon, css). `defer` lets the parser continue; the IIFE binds on `DOMContentLoaded`. |
| How is randomized layout achieved without breaking Hugo's deterministic builds? | **Client-side shuffle** in `lightbox.js` on `DOMContentLoaded`: read all `.gallery-item` elements, shuffle in place using `Array.prototype.sort` with a `Math.random` comparator (or a Fisher-Yates pass), re-append to `.gallery-grid`. | Hugo's `collections.Shuffle` is documented as **non-deterministic across builds** (gohugo.io/functions/collections/shuffle) — this would force every CI build to redeploy the gallery, defeating GitHub Actions caching and producing meaningless diffs. Server-rendered fixed order + client shuffle: build is deterministic, user gets a fresh layout per visit. **Trade-off:** SEO and JS-disabled users see the source order — acceptable for a personal photo gallery (no SEO target on individual photos; no a11y regression because all photos are reachable). **Rejected alt:** seeding `collections.Shuffle` with a build-time hash — Hugo provides no stable seed primitive, and `now.Unix` makes builds non-reproducible (verified at github.com/gohugoio/hugo/issues/5641). |
| Masonry approach (preserve original aspect ratios)? | **CSS `column-count` (multi-column) layout with `break-inside: avoid` on `.gallery-item`** — the simplest masonry that auto-arranges variable-aspect images. No JS layout calculation. Replace the existing `display: grid` block in `style.css` line 281–286. | CSS Grid with `grid-template-rows: masonry` is still behind a flag in 2026 (only Firefox with experimental flag — verify before adopting). CSS `column-count` is universal since 2015. The visual result is "Pinterest-style" masonry where each image keeps its natural aspect ratio. Pair with `img { width: 100%; height: auto; display: block; }` (already in place). **Trade-off:** column-count fills column-by-column, not row-by-row — visitors reading top-to-bottom may not see all photos in chronological order. With client-side shuffle this is moot. |
| New CSS rules — keep one file or split? | **Keep one file** (`style.css`). Add a `/* === Lightbox === */` section after the existing `/* === Gallery === */` section. | Existing convention: every component (header, post-list, page, gallery, about, footer) is a section comment in `style.css`. Splitting now contradicts the v2.0-validated structure and adds a request. The full file is ~410 lines today; lightbox + masonry adds ~60 lines — still well within "one file" sanity. |
| Lightbox JS surface (for sizing) | **`lightbox.js` ≈ 80 LOC** — IIFE that: (1) shuffles `.gallery-item` children of `.gallery-grid`, (2) binds click on each `.gallery-item`, (3) on click prevents-default, builds `<div class="lightbox">` with backdrop + `<img>` + caption + `Esc`/click-outside dismiss + arrow-key prev/next + focus trap. No external dependencies. | Matches the "vanilla JS only, no framework" v2.0 invariant. Backdrop blur via CSS `backdrop-filter: blur(8px)`. |

**Files modified:** `themes/minimal/layouts/gallery/single.html`, `themes/minimal/static/css/style.css`.
**Files created:** `themes/minimal/static/js/lightbox.js`, one `.md` sidecar per photo in `content/gallery/photos/`.

**Risk callouts:**
- **Build determinism vs random gallery:** explicitly chosen to randomize **client-side** to preserve Hugo build determinism (CI cache, meaningful diffs). Server shuffle would invalidate every deploy.
- **Caption data must precede lightbox JS work:** the lightbox reads `data-caption="…"` attributes off `.gallery-item`. The template must emit those attributes (`{{ $photo.Title }}` from sidecar) before the JS can be tested. Build order: caption sidecars → template emits data attrs → lightbox JS reads them.
- **CSS Grid masonry is NOT yet stable in 2026** — confirmed `column-count` is the only cross-browser option. If using Firefox-only `grid-template-rows: masonry`, it falls back to `auto`, breaking layout in Chrome/Safari. **Use column-count.**
- **`build.publishResources: false`** in `gallery/index.md` means originals are NOT copied to `public/`. The processed `$thumb` and `$full` are. This is correct and must be preserved — a regression would publish 60+ MB of originals.

---

### (c) About page redesign

```
content/about/
  ├── index.md                 ← MODIFIED: extend front matter, restructure markdown
  └── images/                  ← UNCHANGED (5 photos already EXIF-scrubbed)

themes/minimal/layouts/
  ├── about/                   ← NEW directory
  │   └── single.html          ← NEW: dedicated about layout (asymmetric sections)
  └── _default/_markup/
      └── render-image.html    ← MODIFIED: add new title keys (e.g. "split", "feature")

themes/minimal/static/css/style.css
  └── /* === About === */ section ← MODIFIED: add asymmetric grid rules
```

**One concrete recommendation per question:**

| Question | Decision | Rationale |
|----------|----------|-----------|
| Can the existing render-image hook stay (title-keyed sizing) or does the dynamic layout need new section/component templates? | **Keep the hook AND extend it** with two new title keys: `split` (for text+image rows, e.g. `400x500 webp q78`) and `feature` (for full-width focal images, e.g. `1024x576 webp q80`). The existing `hero` / `grid` / default keys keep working. | The hook has proven robust (validated in Phase 7, v2.0). Adding keys is additive — it does not invalidate the existing About content. The alternative (component templates / shortcodes for every layout variant) would multiply files and break the single-source-of-truth principle for image sizing. |
| Does About become a custom layout (`themes/minimal/layouts/about/single.html`) or stay on `_default/single.html` with markdown-driven structure? | **Custom layout at `themes/minimal/layouts/about/single.html`.** Hugo's `type: "about"` (already set in `index.md` line 3) routes to it. | The current About leans on raw HTML `<div class="about-hero">` blocks inside markdown (line 6 of `index.md`) because `_default/single.html` does nothing structural. A dedicated layout lets the template own the structural shell (hero + sections + grid + closing CTA), and markdown owns prose. Reduces HTML-in-markdown smell. **Wiring:** `front matter type: "about"` → Hugo lookup → `layouts/about/single.html` (already validated path: `gallery/single.html` works the same way for `type: "gallery"`). |
| New shortcodes needed for asymmetric sections / pull-quotes / split text+image rows? | **Three minimal shortcodes:** `{{< split >}}…{{< /split >}}` (two-column text+image row), `{{< pullquote >}}…{{< /pullquote >}}` (replaces the existing `<aside class="about-pullquote">` raw HTML), `{{< feature >}}…{{< /feature >}}` (full-bleed focal image w/ caption). Each is a 5–10 LOC template under `themes/minimal/layouts/shortcodes/`. | Shortcodes encapsulate the HTML wrapper so markdown stays prose-y and editable. The existing `mermaid` shortcode is precedent. Three is the minimum to express tylerkarow.com/about's asymmetric flow without over-engineering. **Rejected alt:** new front-matter fields (e.g. `sections: [{type: split, …}, …]`) — turns content into config; loses markdown-as-source-of-truth. |
| How is professional content blended in — markdown sections, new front-matter fields, or shortcodes? | **Markdown sections + the three shortcodes above.** No new front-matter fields. Mix climbing/professional via section ordering inside `index.md`: e.g. opener split (portrait + intro) → professional H2 with experience list → pullquote (career achievement OR climbing milestone — content choice) → split (climbing image + bouldering paragraph) → grid (existing 4-image cluster) → closing. | Markdown is the right tool for prose-with-structure. Front-matter fields force schema migrations every time the layout shifts. The current Phase 7 climbing-heavy bias is a content problem, not an architecture one — the architecture (layout + shortcodes) just has to support both flavors equally; ordering is the user's editorial choice. |

**Files modified:** `content/about/index.md`, `themes/minimal/layouts/_default/_markup/render-image.html`, `themes/minimal/static/css/style.css`.
**Files created:** `themes/minimal/layouts/about/single.html`, `themes/minimal/layouts/shortcodes/split.html`, `themes/minimal/layouts/shortcodes/pullquote.html`, `themes/minimal/layouts/shortcodes/feature.html`.

**Risk callouts:**
- **Render-image hook compatibility:** the new keys (`split`, `feature`) must NOT collide with existing keys. Verified: current keys are `hero`, `grid`, default — no collision.
- **`type: "about"` already maps to `body.page-about`** (verified: `baseof.html` line 26). New About-specific CSS rules continue to scope under `body.page-about` — no global pollution.
- **Hidden coupling to existing `.about-hero` raw HTML:** the current `index.md` uses `<div class="about-hero">` inline. If the new layout's shell already provides this wrapper, the markdown must drop the inline `<div>` to avoid double-wrapping. Verify on first build that `inspect element` shows one `.about-hero` div, not two.

---

## Component boundaries (post-v3.0)

| Component | Responsibility | Owns | Communicates with |
|-----------|---------------|------|-------------------|
| Theme bootstrap (`<head>` IIFE) | Set `data-theme` before first paint | `localStorage`, `prefers-color-scheme`, `meta[theme-color]` | CSS (via `data-theme` attribute) |
| Theme toggle (button + handler) | User toggles theme; visible state via icons | DOM event listener, `aria-pressed`, two SVG children | CSS (icon visibility), `localStorage` |
| Render-image hook | Title-keyed image sizing for content/* markdown images | All `image.Process` calls inside content rendering | None directly — fed by markdown image titles |
| Gallery template | Render gallery list with thumb + lightbox triggers | Resource shuffling (server-side, fixed order at build), thumb + full URLs, caption attributes | Lightbox JS (via DOM data-attrs), `image.Process` (via Hugo) |
| Lightbox JS | Modal viewer + masonry shuffle on load | Click handlers, modal DOM, focus trap, keyboard nav, in-page shuffle | DOM (`.gallery-item` nodes), CSS (`.lightbox` styles) |
| About layout | Compose hero + asymmetric sections + grid + close | Structural HTML shell | Shortcodes, render-image hook |
| Shortcodes (split / pullquote / feature) | HTML wrapper for asymmetric content blocks | Per-block HTML | About layout (via inclusion) |

---

## Suggested build order

Phase decomposition for the roadmapper, with dependencies and integration risk per feature.

| # | Phase | Touches | Depends on | Risk | Rationale |
|---|-------|---------|------------|------|-----------|
| 1 | **Theme-toggle icon button** | `header.html`, `baseof.html`, `style.css` | none | LOW — pattern proven by footer SVGs; FOUC impossible due to IIFE order | Smallest blast radius, most isolated. Builds confidence in the v3.0 milestone before larger surgery. No content changes. |
| 2 | **About page redesign** | new `layouts/about/single.html`, 3 new shortcodes, render-image hook extension, `index.md` rewrite, `style.css` | none (independent of #1, but #1 first reduces concurrent diff) | MEDIUM — content rewrite + structural template change; visual regression possible | Architecture work (new layout + shortcodes) is content-independent and can be scaffolded with placeholder copy. Content rewrite is editorial — separable from template work if needed. |
| 3 | **Gallery lightbox + masonry** | gallery `single.html`, new `lightbox.js`, sidecar `.md` files, `style.css`, page-bundle additions | **(b1) caption sidecar data must land BEFORE (b2) template emits data attrs BEFORE (b3) lightbox JS reads them** | MEDIUM-HIGH — three internal dependencies + first JS file added to theme + masonry layout regression risk | Most moving parts. Best done last so attention is undivided. The internal sub-ordering matters: caption sidecars are pure data (no UX impact) — land them first as a no-op commit, then template, then JS. |

**Why this order:**
- (a) is a 1-file-3-touch change — cheapest validation that the milestone is on track.
- (c) introduces new layout + shortcodes which can be scaffolded and visually validated with the existing 5 photos before any content rewrite — no JS, no new content infrastructure.
- (b) is the largest change and only feature that introduces a JS file + CSS layout primitive (column-count masonry) + new authoring workflow (sidecar `.md`). Save for last so a regression doesn't block the simpler features.

**Cross-feature concerns (none):** no shared files mutated by more than one feature except `style.css`. CSS section comments make merging diffs easy. No shared JS state (theme toggle handler in `baseof.html` is independent of `lightbox.js`).

---

## Patterns to follow

### Pattern 1: Inline SVG with `currentColor` for theme-aware icons
**What:** Inline 2-color SVG, `stroke="currentColor"` (or `fill`), recolors via CSS `color: var(--text)`.
**When:** Any single-color icon that must adapt to dark/light. Already proven by footer (GitHub, Instagram) and wordmark.
**Example:**
```html
<button class="theme-toggle" aria-label="Toggle dark mode" aria-pressed="false">
  <svg class="icon-sun" width="18" height="18" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
    <circle cx="12" cy="12" r="4"/><path d="M12 2v2…"/>
  </svg>
  <svg class="icon-moon" width="18" height="18" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
</button>
```

### Pattern 2: Page-bundle resource sidecar for metadata
**What:** Co-located `.md` next to a binary resource carries its metadata (title, params).
**When:** Any per-resource metadata (gallery captions, alt text, tags). Hugo natively binds them by basename.
**Example:** `content/gallery/photos/DSC09782.md`:
```yaml
---
title: "Sunrise on the Hochschwab ridge"
description: "March 2026, the morning the wind dropped just long enough."
---
```
Read in template: `$photo.Title`, `$photo.Params.description`.

### Pattern 3: `body.page-{type}` scoping for layout-specific CSS
**What:** Hugo emits `<body class="page-{{ .Type | default "default" }}">`; CSS scopes via `body.page-X .component { … }`.
**When:** Any rule that should only apply to one section/page type. Already used for `body.page-gallery` (max-width override) and `body.page-about` (hero, grid, pullquote).
**Why it matters for v3.0:** new About rules and lightbox rules continue this convention — no global rules added.

### Pattern 4: Shortcode for HTML wrapper, markdown for prose
**What:** Encapsulate decorative HTML in a shortcode; let markdown stay prose.
**When:** Any repeated HTML pattern (pullquote, split row, feature image). Precedent: `mermaid` shortcode.
**Why:** markdown stays editable in any editor; HTML wrappers stay maintainable in one template file.

---

## Anti-patterns to avoid

### Anti-pattern 1: Server-side shuffle for client-served randomness
**What:** Using `collections.Shuffle` on the gallery to randomize order.
**Why bad:** Non-deterministic between builds → every CI build produces a different `public/`, defeating GitHub Pages incremental deploy and producing meaningless diffs in `git log` if `public/` is ever committed. (Verified: gohugo.io/functions/collections/shuffle and github.com/gohugoio/hugo/issues/5641.)
**Instead:** Server emits fixed order; `lightbox.js` shuffles on `DOMContentLoaded`. User experience is identical; build reproducibility preserved.

### Anti-pattern 2: Two-image swap for theme-aware icon (display:none on `<img>` tags)
**What:** Two `<img>` tags, one shown per theme.
**Why bad:** Two HTTP requests, FOUC during image fetch, can't recolor with `currentColor`, can't accept a focus ring on the icon shape.
**Instead:** Two inline SVGs with `currentColor`, CSS toggles `display`. (Pattern 1 above.)

### Anti-pattern 3: Front-matter array of section objects in About
**What:** `index.md` front matter declares `sections: [{type: split, image: …, text: …}, …]`.
**Why bad:** Turns content into config; loses markdown-as-prose; every layout change forces front-matter migration; editor preview breaks.
**Instead:** Markdown body uses shortcodes inline. Section ordering is markdown ordering.

### Anti-pattern 4: Splitting `style.css` prematurely
**What:** Adding `gallery.css` or `about.css` as new files.
**Why bad:** Breaks the v2.0-validated single-stylesheet convention, adds requests, fragments cascade reasoning.
**Instead:** New `/* === Section === */` comment blocks within `style.css`. Re-evaluate splitting only if file exceeds ~1000 lines (currently ~410).

### Anti-pattern 5: Loading `lightbox.js` from `baseof.html`
**What:** `<script src="js/lightbox.js" defer>` in the global base.
**Why bad:** Ships unused JS to every page (home, blog, about, ~9 blog posts). Wastes bytes for a feature used on one URL.
**Instead:** Load it only from `gallery/single.html`. Page-scoped JS for page-scoped features.

---

## Scalability considerations

| Concern | Today (18 photos) | At 100 photos | At 1000 photos |
|---------|-------------------|---------------|----------------|
| Gallery page weight | ~2 MB first-paint (lazy beyond first 3) | Keep lazy; verify CLS still <0.1 | Paginate or virtual-scroll; build will slow `image.Process` significantly |
| Caption sidecar file count | 18 `.md` | 100 `.md` — still trivial in `git status` | 1000 — consider bulk-edit script or YAML data file (architectural fork point) |
| Lightbox keyboard nav (prev/next) | Linear array, no perf concern | Same | Same — DOM-bound, no list overhead |
| `image.Process` build time | <5s | ~30s on first build, cached after | minutes on first build — `HUGO_CACHEDIR` (already set in CI) is critical |
| Client-side shuffle perf | trivial | trivial | trivial (1000-element Fisher-Yates is microseconds) |

**1000-photo fork point:** at that scale, sidecar `.md` files become tedious to author. The architecture migration would be: introduce `data/gallery.yaml` keyed by filename basename, fall back to that if no sidecar exists. Defer until needed — the v3.0 + foreseeable scale is well under 100.

---

## Confidence assessment

| Decision | Confidence | Why |
|----------|------------|-----|
| Inline SVG icons in `header.html` | HIGH | Direct precedent in `footer.html` (GitHub + Instagram); pattern matches v2.0 wordmark approach |
| CSS `display: none` toggle by `[data-theme]` | HIGH | Standard CSS, no browser caveats |
| FOUC unaffected by icon work | HIGH | Verified by reading `baseof.html` IIFE order (lines 11–24) |
| Sidecar `.md` for captions | HIGH | Documented Hugo page-bundle resource metadata pattern |
| Reuse existing `image.Process` pipeline | HIGH | No change required; existing template already produces both URLs |
| Modify `gallery/single.html` (no new layout file) | HIGH | Verified by reading the file and Hugo lookup chain |
| Lightbox JS in new file at `static/js/lightbox.js`, loaded from `gallery/single.html` | HIGH | Convention match; minimizes JS surface |
| Client-side shuffle (NOT `collections.Shuffle`) | HIGH | Verified non-determinism at gohugo.io and Hugo issue #5641 |
| CSS `column-count` for masonry | HIGH | CSS Grid `masonry` still experimental in 2026; column-count universal since 2015 |
| One `style.css` (no split) | HIGH | Existing convention; volume well under threshold |
| Custom `layouts/about/single.html` | HIGH | `type: "about"` in front matter already routes; precedent in `gallery/single.html` |
| Three shortcodes (split/pullquote/feature) | MEDIUM | Three is a judgment call — could be two or four. Recommendation is the minimum to express tylerkarow.com-style asymmetric flow without proliferation |
| Build order: (a) → (c) → (b) | HIGH | Driven by complexity ordering and zero shared-file conflicts |

---

## Sources

- Existing repo files (read directly):
  - `themes/minimal/layouts/_default/baseof.html`
  - `themes/minimal/layouts/_default/single.html`
  - `themes/minimal/layouts/_default/list.html`
  - `themes/minimal/layouts/_default/_markup/render-image.html`
  - `themes/minimal/layouts/partials/header.html`
  - `themes/minimal/layouts/partials/footer.html`
  - `themes/minimal/layouts/partials/favicon.html`
  - `themes/minimal/layouts/gallery/single.html`
  - `themes/minimal/layouts/shortcodes/mermaid.html`
  - `themes/minimal/static/css/style.css`
  - `content/about/index.md`
  - `content/gallery/index.md`
  - `hugo.toml`
  - `.planning/PROJECT.md`
- External (HIGH confidence — verified):
  - [Hugo `collections.Shuffle` documentation](https://gohugo.io/functions/collections/shuffle/) — confirms non-determinism across builds
  - [Hugo issue #5641 — random number has fixed seeding](https://github.com/gohugoio/hugo/issues/5641) — confirms no stable seeding primitive
- External (MEDIUM confidence — pattern reference only):
  - [CSS Masonry & CSS Grid (CSS-Tricks)](https://css-tricks.com/css-masonry-css-grid/) — confirms `grid-template-rows: masonry` still behind flag
  - [Building a stylish Masonry layout (Andri.co)](https://blog.andri.co/021-building-a-stylish-masonry-layout-using-just-css-and-javascript/) — pattern reference for column-count + aspect ratios

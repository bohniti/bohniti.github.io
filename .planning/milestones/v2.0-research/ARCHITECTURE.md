# Architecture Research: v2.0 Brand & Gallery Integration

**Domain:** Hugo static site — theme/branding/gallery integration into existing custom theme
**Researched:** 2026-04-28
**Confidence:** HIGH — derived from direct read of every theme file plus Hugo 0.157 official image-processing & template lookup docs

This is **integration architecture**, not greenfield design. The existing theme (`themes/minimal/`) is small and clean — every change is local to a known file. The interesting questions are the FOUC story for the theme toggle, where Hugo image processing roots itself, and the sequencing dependencies between components.

## Existing System Overview (read, not invented)

```
┌─────────────────────────────────────────────────────────────┐
│                  Content Layer (content/)                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────────────┐    │
│  │ about.md │  │ blog/    │  │ blog/YYYY-MM-DD-slug/   │    │
│  │ (single) │  │ _index.md│  │   index.md + images/    │    │
│  └──────────┘  └──────────┘  └─────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│              Theme Layer (themes/minimal/)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  layouts/_default/baseof.html  (HTML shell, head)   │    │
│  │      ├── partials/header.html  (title + nav)        │    │
│  │      ├── {{ block "main" }}                         │    │
│  │      │     ├── list.html   (home, /blog/)           │    │
│  │      │     └── single.html (about, posts)           │    │
│  │      └── partials/footer.html (links + social SVG)  │    │
│  │  layouts/shortcodes/mermaid.html                    │    │
│  │  static/css/style.css   (Flexoki light, 265 lines)  │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│            Static Assets (project-root, served as-is)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐       │
│  │ static/  │  │ images/  │  │ images/galary/ (typo)│       │
│  │ files/*  │  │ logos.png│  │ 18 .jpg/.JPG/.jpeg   │       │
│  └──────────┘  └──────────┘  └──────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Key observations from the read:**

1. `baseof.html` is dead simple — 19 lines, single CSS link, no inline scripts, no favicon, no theme attribute on `<html>`. This is a clean integration target.
2. `header.html` hardcodes the site title via `{{ .Site.Title }}` from `hugo.toml`. The wordmark swap replaces the inner `<a>` content but keeps the `<a>` (so the home link still works).
3. `style.css` already uses CSS custom properties under `:root` for the entire palette. **All 13 colour tokens** (`--bg`, `--bg-secondary`, `--text`, `--text-secondary`, `--text-muted`, `--accent`, `--accent-hover`, `--link`, `--link-hover`, `--border`, `--code-bg`, plus `--max-width`) flow from one place. Adding a dark mode is a **palette swap**, not a CSS rewrite.
4. `images/` lives at project root, **not** under `static/` and **not** as a page bundle. Hugo will not auto-process it as page resources from there. Two integration options exist (covered below).
5. There is no `gallery/` content yet. There is no `partials/favicon.html`. There is no `assets/` directory (Hugo Pipes / global resources). All three are **NEW**.

## Integration Component Map

| Component | Type | File | Reason |
|-----------|------|------|--------|
| Dark palette CSS tokens | MODIFY | `themes/minimal/static/css/style.css` | Add `:root[data-theme="dark"]` block alongside existing `:root` |
| Theme-toggle inline init script | MODIFY | `themes/minimal/layouts/_default/baseof.html` | Inline `<script>` in `<head>` before stylesheet link |
| Theme-toggle button (UI) | MODIFY | `themes/minimal/layouts/partials/header.html` | New `<button class="theme-toggle">` after `<nav>` |
| Theme-toggle button JS handler | NEW or inline | `themes/minimal/layouts/partials/theme-toggle.html` (new partial holding markup + click handler), OR inline at bottom of header.html | Encapsulation; partial is cleaner |
| Header wordmark images | MODIFY | `themes/minimal/layouts/partials/header.html` | Replace text `{{ .Site.Title }}` with two `<img>` tags toggled by CSS |
| Sliced logo assets (8 files) | NEW | `themes/minimal/static/images/brand/*.png` (or `static/images/brand/`) | Copy out of `images/logos.png` sprite to individual files |
| Favicon partial | NEW | `themes/minimal/layouts/partials/favicon.html` | `<link rel="icon">` + apple-touch-icon set |
| Favicon `<head>` include | MODIFY | `themes/minimal/layouts/_default/baseof.html` | One-line `{{ partial "favicon.html" . }}` |
| Favicon assets | NEW | `themes/minimal/static/favicon.ico`, `favicon-16.png`, `favicon-32.png`, `apple-touch-icon.png` | Sourced from `images/logos.png` favicon column |
| Gallery content section | NEW | `content/gallery/_index.md` | Section index — drives `/gallery/` URL & menu |
| Gallery images (page-bundle resources) | NEW (move) | `content/gallery/photos/*.jpg` | Renamed/moved from `images/galary/`, becomes page resources for Hugo image processing |
| Gallery list layout | NEW | `themes/minimal/layouts/gallery/list.html` | Section-specific template; renders the grid |
| Gallery CSS | MODIFY | `themes/minimal/static/css/style.css` | `.gallery-grid`, `.gallery-item`, `.gallery-img` classes |
| Gallery menu entry | MODIFY | `hugo.toml` | New `[[menu.main]]` for `/gallery/` |
| About-page inline photos | MODIFY | `content/about.md` | Convert to page bundle (`content/about/index.md` + `images/`) OR keep flat and use `static/images/about/` paths |
| About page styling (optional) | MODIFY | `themes/minimal/static/css/style.css` | If portrait/landscape variants need framing |

**Footer:** No change — the `.social-icons` cluster already uses `currentColor` on its SVG strokes (verified in `footer.html` lines 7, 13), so it inherits whatever `--text-secondary` resolves to and dark-mode-adapts for free.

## Architectural Patterns to Apply

### Pattern 1: Inline blocking init script for theme — the FOUC contract

**What:** A tiny synchronous `<script>` placed inside `<head>` **before** `<link rel="stylesheet">` that reads the persisted preference (or OS preference) and writes `data-theme="dark"` onto `<html>`. CSS selectors keyed off `[data-theme="dark"]` then resolve correctly on first paint.

**When to use:** Any theme that supports both OS-driven and user-overridden preferences with persistence. Required by the milestone's "no flash on load" constraint.

**Trade-offs:** Adds ~200 bytes of inlined JS to every page. Cannot be deferred (would defeat the purpose). Must be hand-minified; Hugo's `--minify` does not minify inline `<script>` content reliably across versions, so keep it small.

**Example (drop into `baseof.html` between `<title>` and the CSS link):**

```html
<script>
  (function () {
    try {
      var stored = localStorage.getItem('theme');
      var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var theme = stored || (prefersDark ? 'dark' : 'light');
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      }
    } catch (e) { /* localStorage blocked — fall back to light */ }
  })();
</script>
```

Note: only the dark branch sets the attribute. Light mode is the default `:root` palette and needs no attribute. This avoids a redundant DOM write for the common case and keeps light-mode rendering to a single repaint event.

### Pattern 2: CSS custom property palette swap — the single source of truth

**What:** Two declarations of the same 11 palette tokens — one under `:root` (existing, light), one under `:root[data-theme="dark"]`. No component-level dark overrides.

**When to use:** Any time the existing CSS already speaks in custom-property tokens. This codebase does — verified by grep of `style.css`. There is essentially no work to do beyond defining the dark values.

**Trade-offs:** vs. `@media (prefers-color-scheme: dark)`-only approach: a media query alone cannot represent a user-overridden choice (e.g. user explicitly wants dark even though OS is light). `[data-theme="dark"]` driven by JS is required because the milestone wants persistence. **Recommendation: do not use `@media (prefers-color-scheme)` as a fallback inside CSS** — the inline init script already handles OS preference detection and translates it to `data-theme`. Mixing both approaches creates a "two sources of truth" bug where the user's explicit choice can be visually overridden by their OS during a brief flash.

**Example:**

```css
:root {
  --bg: #FFFCF0;          /* existing Flexoki light */
  --text: #100F0F;
  /* …existing 11 tokens unchanged… */
}

:root[data-theme="dark"] {
  --bg: #100F0F;          /* Flexoki black */
  --bg-secondary: #1C1B1A;
  --text: #CECDC3;        /* Flexoki paper */
  --text-secondary: #878580;
  --text-muted: #575653;
  --accent: #D14D41;      /* Flexoki red 400 — pops on dark */
  --accent-hover: #AF3029;
  --link: #D14D41;
  --link-hover: #AF3029;
  --border: #282726;
  --code-bg: #1C1B1A;
}
```

Source palette: Flexoki spec at https://stephango.com/flexoki — pair the existing light tokens with their `tx`/`tx-2`/`tx-3`/`bg`/`bg-2`/`ui`/`ui-2`/`re-400` dark counterparts.

### Pattern 3: CSS-toggled `<img>` pair for the wordmark — no FOUC, no JS swap

**What:** Two `<img>` tags inside the title `<a>`, one with class `logo-light`, one `logo-dark`. CSS hides the wrong one based on `[data-theme]`. Both sources are static files in `themes/minimal/static/images/brand/`, served at predictable URLs.

**When to use:** When the asset is a raster (logo wordmark sliced from `logos.png`) and you want zero flash and zero JS coupling. Because the `data-theme` attribute is set by the inline init script before paint, the correct logo is visible from frame 1.

**Trade-offs vs. single `<img>` with src swapped via JS:**

| Aspect | Two-image CSS toggle | Single `<img>` JS swap |
|--------|----------------------|------------------------|
| FOUC risk | None — `data-theme` is set before first paint | Brief flash of wrong logo (or alt text) before JS runs |
| Network | Both images downloaded | Only one downloaded |
| Cache | Both cached (good for fast theme toggle) | One cached; switching theme triggers a fetch |
| Complexity | One CSS rule | JS event listener + DOM mutation |
| Accessibility | `alt` on the visible one; `aria-hidden` on hidden | Single `alt`, simpler |

**Recommendation:** two-image CSS toggle. Wordmark assets are tiny (sliced from a 400KB sprite — each variant well under 50KB once optimized). The fast theme-toggle UX (no logo flicker on switch) outweighs the duplicate-download cost.

**Trade-offs vs. `<picture>` with `prefers-color-scheme`:** A `<picture>` element with `<source media="(prefers-color-scheme: dark)">` is elegant **but** binds the logo to the OS, not to the user's persisted choice. Same "two sources of truth" hazard as the CSS media-query approach in Pattern 2. Reject for this milestone.

**Example (replace the `<a>` body in `header.html`):**

```html
<a href="{{ .Site.BaseURL }}" aria-label="{{ .Site.Title }}">
  <img class="logo logo-light" src="{{ "images/brand/wordmark-light.png" | absURL }}"
       alt="{{ .Site.Title }}" width="180" height="40">
  <img class="logo logo-dark" src="{{ "images/brand/wordmark-dark.png" | absURL }}"
       alt="" aria-hidden="true" width="180" height="40">
</a>
```

```css
.logo-dark { display: none; }
[data-theme="dark"] .logo-light { display: none; }
[data-theme="dark"] .logo-dark { display: inline; }
```

Set explicit `width`/`height` on both `<img>` tags — Hugo image processing is **not** in play for these (they're static assets, not page resources), so the browser cannot infer dimensions from a Hugo-generated HTML attribute. Reserving the box prevents header layout shift.

### Pattern 4: Hugo image processing for the gallery — page resources only

**What:** Move the 18 photos under a Hugo page bundle so they become **page resources** (`.Resources`) of the gallery section. The `gallery/list.html` template iterates `.Resources.ByType "image"` and calls `.Resize "800x"` (or `.Fill "600x600 center"` for thumbs) which triggers Hugo's `image.Resize`/`image.Fill` to generate optimized renditions in `/resources/_gen/images/` and emit `<img srcset>` + responsive sizes.

**When to use:** This is the canonical Hugo gallery pattern (verified against current Hugo docs at https://gohugo.io/content-management/image-processing/). Hugo 0.157 supports `Resize`, `Fill`, `Fit`, `Crop` plus `webp`/`avif` output via `Process` — all available without any plugin.

**Critical decision: where the source photos live.**

| Option | Path | Becomes page resource? | Verdict |
|--------|------|------------------------|---------|
| A. Page bundle | `content/gallery/photos/*.jpg` next to `_index.md` | YES — `.Resources` works | **Recommended** |
| B. Project images/ | `images/gallery/*.jpg` (current `images/galary/` renamed) | NO — Hugo doesn't process project-root files automatically; would need `resources.Get` calls per file | Rejected — boilerplate and brittle |
| C. Static/ | `static/gallery/*.jpg` | NO — `static/` is served verbatim, never processed | Rejected — defeats the purpose |
| D. Assets/ | `assets/gallery/*.jpg` | YES via `resources.GetMatch` (Hugo Pipes) | Acceptable but more code than Option A |

**Recommendation: Option A.** The existing blog already uses page bundles (verified — `content/blog/2026-03-05-climbing-routes/` etc.). The gallery should follow the same convention. Rename `images/galary/` → `content/gallery/photos/` (or place photos directly under `content/gallery/` as branch-bundle resources). Files under a branch bundle's nested directories are still discoverable via `.Resources.Match "photos/*.jpg"`.

**Trade-offs:**
- Pro: idiomatic Hugo, automatic responsive renditions, `srcset` works, `--minify` does the rest.
- Pro: Hugo caches generated renditions in `resources/_gen/images/` — committing this directory to git speeds up CI builds dramatically (per Hugo docs, 90%+ build-time reduction). Already excluded by `.gitignore` — recommend whitelisting `resources/_gen/` for the gallery to keep CI fast.
- Con: 18 source photos at 150KB–7.5MB each = up to 130MB in source. Pre-shrinking to ~3000px max-edge before commit is sensible — Hugo's processing time scales with input pixel count (per Hugo docs).
- Con: First build is slow (Hugo regenerates everything); subsequent builds use the resource cache.

**Example (`themes/minimal/layouts/gallery/list.html`):**

```go-html-template
{{ define "main" }}
<article class="gallery-page">
  <div class="page-header">
    <h1 class="page-title">{{ .Title }}</h1>
  </div>
  {{ with .Content }}<div class="page-content">{{ . }}</div>{{ end }}
  <div class="gallery-grid">
    {{ range .Resources.Match "photos/*" }}
      {{ $thumb := .Fill "600x600 center webp q82" }}
      {{ $full  := .Resize "1600x webp q85" }}
      <a class="gallery-item" href="{{ $full.RelPermalink }}">
        <img class="gallery-img"
             src="{{ $thumb.RelPermalink }}"
             width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"
             loading="lazy" decoding="async"
             alt="">
      </a>
    {{ end }}
  </div>
</article>
{{ end }}
```

Hugo template lookup will pick this up automatically because the section is `gallery` (per `content/gallery/_index.md`). No layout config needed in `hugo.toml`.

### Pattern 5: About-page inline photos — page bundle conversion

**What:** Convert `content/about.md` (single-file page) into a page bundle `content/about/index.md` with co-located `images/`. Reference photos with relative Markdown image syntax (`![Portrait](images/portrait.jpg)`); Goldmark resolves them as page resources.

**When to use:** When you need Hugo-processed inline images on a static page. The conversion is mechanical: `content/about.md` → `content/about/index.md`, place images alongside. Hugo's URL routing is unchanged (`/about/` either way).

**Trade-offs vs. just dropping files in `static/images/about/`:**
- Bundle (recommended): images stay logically grouped with content; image-processing shortcodes work; Markdown `![](images/foo.jpg)` resolves cleanly.
- Static: simpler but no processing, manual URL paths, and breaks the "page bundle" convention the rest of the site already uses.

For very small inline portraits (<200KB), a render hook isn't necessary — the existing `.page-content img` rule in `style.css` lines 167–172 already constrains `max-width: 100%` and adds `border-radius: 4px`. A custom `_markup/render-image.html` hook becomes worthwhile only if the about page wants automatic responsive `srcset` for inline shots. Defer unless it's needed.

## Data Flow

### Theme-application flow (per page load)

```
HTML parser hits <head>
    ↓
Inline init script runs synchronously
    ├── reads localStorage['theme']
    ├── reads matchMedia('prefers-color-scheme: dark')
    └── if dark: document.documentElement.setAttribute('data-theme','dark')
    ↓
<link rel="stylesheet"> downloads style.css
    ↓
CSS resolves :root vs :root[data-theme="dark"] selector
    ↓
First paint — correct palette, correct wordmark (via .logo-light/.logo-dark CSS rules)
    ↓
Theme-toggle button hydrates (click handler attached)
    ↓
[User clicks toggle] → JS flips data-theme + writes localStorage → CSS re-resolves
```

### Build-time gallery flow

```
hugo --minify
    ↓
Reads content/gallery/_index.md → identifies section "gallery"
    ↓
Looks up layout: layouts/gallery/list.html (template lookup hierarchy)
    ↓
Iterates .Resources.Match "photos/*" — 18 image resources
    ↓
For each: .Fill "600x600" generates thumb in /resources/_gen/images/
          .Resize "1600x"  generates full in /resources/_gen/images/
    ↓
Renders <img src="..." srcset="..." width="..." height="..." loading="lazy">
    ↓
public/gallery/index.html written; processed images copied into public/
    ↓
GitHub Actions deploys public/ to Pages
```

## Suggested Build Order — Dependency-Driven

Phases below are independent (none has hidden state), but dependencies between **components** dictate order. Each phase is shippable on its own.

### Phase A — Theming Foundation (must come first; everything visual depends on it)

1. **A1. Add dark palette CSS tokens** (modify `style.css`).
   No JS yet — verify by manually adding `data-theme="dark"` to `<html>` in DevTools and confirming the whole site re-renders correctly.
2. **A2. Inline init script in `<head>`** (modify `baseof.html`).
   Defaults to OS preference; persistence comes in A3.
3. **A3. Theme-toggle button + click handler** (modify `header.html`, optionally extract to a `partials/theme-toggle.html`).
   Verifies `localStorage.setItem('theme', ...)` round-trip. Add CSS for `.theme-toggle` button (small icon button, sun/moon SVG).

**Blocks:** A1 must precede A2 (script needs CSS to react to). A2 must precede A3 (button writes preference; needs a system that reads it).

### Phase B — Brand Assets (depends on A — wordmark CSS toggle uses `[data-theme]`)

1. **B1. Slice `images/logos.png`** into 8 individual PNGs in `themes/minimal/static/images/brand/`. Naming convention: `wordmark-light.png`, `wordmark-dark.png`, `icon-light.png`, `icon-dark.png`, `mark-light.png`, `mark-dark.png`, `favicon-light.png`, `favicon-dark.png`. Optimize with `pngquant` or similar; target <30KB each for the wordmark.
2. **B2. Header wordmark swap** (modify `header.html` + add CSS rules for `.logo-light` / `.logo-dark`).
   Depends on B1 (assets) and A3 (`data-theme` is being set).

### Phase C — Favicon (parallel-safe with B; depends on A only because favicon variants use light/dark sources)

1. **C1. Generate favicon set** from `images/logos.png` favicon column. Standard outputs: `favicon.ico` (multi-size 16/32/48), `favicon-32.png`, `favicon-16.png`, `apple-touch-icon.png` (180×180). Optionally `favicon.svg` if a vector is available.
2. **C2. Create `partials/favicon.html`** with the `<link rel="icon">` block. Follow the modern minimal set: `icon` (svg/ico), `icon` (32 png), `icon` (16 png), `apple-touch-icon`. No need for the legacy 50+ PNG sizes — they're cargo-cult.
3. **C3. Wire into `baseof.html`** with one line: `{{ partial "favicon.html" . }}` directly after the existing `<title>` tag.

Note on dark-mode favicons: browser support for `<link rel="icon" media="(prefers-color-scheme: dark)">` is uneven (Safari/Firefox yes, Chromium partial). Recommendation: **ship a single neutral favicon** that reads on both backgrounds. Don't over-engineer. The TB-in-circle favicon in the sprite is already neutral.

### Phase D — Gallery (depends on B/C only by convention; technically independent)

1. **D1. Folder rename** `images/galary/` → `content/gallery/photos/` (move into Hugo's content tree to enable page resources). Preserve original filenames; add a `.gitattributes` entry for `*.jpg binary` if not already present.
2. **D2. Create `content/gallery/_index.md`** with `title: "Gallery"` and an optional intro paragraph as `.Content`.
3. **D3. Add menu entry** in `hugo.toml` under `[menu]`:
   ```toml
   [[menu.main]]
     name = "Gallery"
     url = "/gallery/"
     weight = 3
   ```
   (weight 3 places it after Blog/About; reorder if desired.)
4. **D4. Create `themes/minimal/layouts/gallery/list.html`** (the section template — see Pattern 4 example).
5. **D5. Add `.gallery-grid` / `.gallery-item` CSS** to `style.css`. CSS Grid with `grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` and `gap: 0.75rem` is the minimum-viable grid. Keep `--max-width: 640px` for the gallery section header but let `.gallery-grid` break out via `max-width: min(1200px, 95vw)` — current 640px is too narrow for a photo grid.
6. **D6. (Optional, if CI is slow) commit `resources/_gen/images/`** for the gallery to skip regeneration on every CI run. Add a narrow `.gitignore` exception. Defer until measured build time exceeds ~60s.

**Blocks:** D1 before D2 (content path must exist). D2 before D3 (menu URL must resolve). D4 before any visual verification. D5 can be developed in parallel with D4 once the HTML class names are decided.

### Phase E — About-page photos (depends on nothing in v2.0; safe last)

1. **E1. Convert** `content/about.md` → `content/about/index.md`. Hugo URL routing is unchanged.
2. **E2. Place inline photos** in `content/about/images/`. Recommend ≤4 photos to keep page weight in check; ≤1500px max edge.
3. **E3. Reference in markdown** with `![alt](images/portrait.jpg)`. Existing `.page-content img` CSS handles the rendering (border-radius, max-width 100%).
4. **E4. (Optional)** add `layouts/_default/_markup/render-image.html` if responsive `srcset` is wanted on the about page. Skip unless necessary — this is a single page with a handful of images.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Loading the theme via a deferred / external script

**What people do:** Put the theme-init JS in a separate `theme.js` file referenced with `<script src="/js/theme.js">` (or worse, with `defer`).
**Why it's wrong:** The browser begins painting before JS runs. Result: light mode flashes before the dark palette applies — exactly what the milestone forbids. This is the single most common Hugo dark-mode bug; verified across multiple community Hugo dark-mode posts.
**Do this instead:** Inline the init script inside `<head>` and ensure it runs **before** the stylesheet link or inside `<head>` ahead of `<body>`. Order of `<link>` and `<script>` does not matter for FOUC as long as both are in `<head>`.

### Anti-Pattern 2: Mixing `prefers-color-scheme` CSS with `[data-theme]` JS

**What people do:** Define dark variables inside `@media (prefers-color-scheme: dark)` AND define them again under `[data-theme="dark"]`.
**Why it's wrong:** Two sources of truth. When user explicitly chooses light on a system that prefers dark, the OS preference rule still matches and bleeds through (specificity wars; whichever rule is later wins). Toggle button "appears broken" intermittently.
**Do this instead:** Pick one. Recommend `[data-theme="dark"]` only (because it's both OS-aware via the init script AND user-overridable). Drop `@media (prefers-color-scheme)` from CSS entirely.

### Anti-Pattern 3: Putting gallery photos in `static/`

**What people do:** Drop the 18 photos in `static/gallery/` and reference them with raw `<img src="/gallery/foo.jpg">`.
**Why it's wrong:** Hugo cannot resize, generate `srcset`, or convert to WebP for files in `static/`. Page weight balloons; failing the milestone's "must not balloon page weight" constraint.
**Do this instead:** Page bundle under `content/gallery/`. The gain in build complexity is zero; the gain in delivered bytes is large.

### Anti-Pattern 4: One favicon `<link>` per device size

**What people do:** Copy a 50-line favicon-generator block from realfavicongenerator.net into `<head>`.
**Why it's wrong:** 90% of those links are obsolete (Windows tile, old iOS variants pre-iOS 7, etc). Adds head bloat and a dozen network requests.
**Do this instead:** Modern minimum: `favicon.ico` (multi-size), `favicon.svg` (if you have a vector), `apple-touch-icon.png` (180×180). Three `<link>` tags total.

### Anti-Pattern 5: Setting `data-theme="light"` explicitly on `<html>` for light mode

**What people do:** The init script sets `data-theme="light"` for light and `data-theme="dark"` for dark.
**Why it's wrong:** Adds a DOM write to every page load (vast majority of users in light mode). Mostly harmless, but it also forces `:root[data-theme="light"]` rules in CSS, doubling the cognitive surface.
**Do this instead:** Light mode is the default `:root`. Only set `data-theme="dark"` when needed. The CSS becomes "default + override," which mirrors the JS logic 1:1.

## Integration Points

### External (build / runtime)

| Service | Integration | Notes |
|---------|-------------|-------|
| GitHub Actions (`.github/workflows/hugo.yml`) | No change required | Hugo 0.157 already has all image-processing primitives; no new CLI flags needed |
| GitHub Pages | No change required | Static output |
| `localStorage` (browser) | Read+write of `theme` key | Wrap in try/catch — Safari Private Mode throws on `setItem` |
| `matchMedia('(prefers-color-scheme: dark)')` | Read once on init | Listen for `change` event optionally to react to live OS-theme changes when user hasn't set an explicit preference |

### Internal (component-to-component)

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `baseof.html` ↔ `style.css` | `data-theme` attribute on `<html>` | Single coordination primitive; no other state |
| `header.html` toggle button ↔ `<html>` | Direct DOM mutation + localStorage write | Single function; no event bus needed |
| `gallery/list.html` ↔ Hugo image processor | `.Resources` API + `.Fill`/`.Resize` chain | Hugo handles caching in `resources/_gen/`; nothing for the template to do |
| `favicon.html` partial ↔ `baseof.html` | Single `{{ partial }}` call | Stateless |
| Wordmark `<img>` pair ↔ theme toggle | CSS `display: none` keyed off `[data-theme]` | No JS coupling |

## Scaling Considerations

This is a personal site with single-digit blog posts and 18 gallery photos — scaling is bounded. Realistic ceilings:

| Scale | Adjustment |
|-------|------------|
| Current (18 photos, 5 posts) | All defaults work. Build < 30s on CI |
| 100+ gallery photos | Pre-shrink source photos to 3000px max edge before commit. Commit `resources/_gen/images/` for gallery to keep CI fast |
| 1000+ photos | Move gallery to a dedicated subdomain or CDN-fronted path; consider Hugo's `Process` method with `webp`/`avif` and multi-rendition `srcset`. Out of scope for v2.0 |

The bottleneck is build time (Hugo image processing), not runtime. There is no runtime — it's static HTML.

## Confidence Notes & Open Questions

**HIGH confidence (verified):**
- Existing theme structure and CSS architecture — I read every file.
- Hugo 0.157 image-processing API surface (`Resize`, `Fill`, page resources, render hooks) — confirmed against current Hugo docs.
- FOUC prevention via inline `<head>` script — universal pattern across multiple Hugo dark-mode references; confirmed against Hugo community write-ups.
- Page-bundle conventions — already used by every blog post in this repo.

**MEDIUM confidence:**
- Exact Flexoki dark palette values — recommended sourcing from https://stephango.com/flexoki rather than inventing. Final tokens to be set during Phase A1; this affects taste, not architecture.
- Whether CI build time benefits enough from committing `resources/_gen/images/` to justify the repo bloat. Defer the call until measured.

**LOW confidence / open questions for the roadmap:**
- Whether the home page `list.html` should also get a small wordmark/branding element — milestone doesn't say, leaving as out-of-scope.
- Whether the gallery should support per-photo captions / lightbox — milestone says "grid layout," nothing more. Recommend ship-without-lightbox for v2.0; lightbox is an easy follow-up.
- Whether the responsive breakpoint at `@media (max-width: 600px)` needs adjustment for the gallery grid — likely yes, but it's CSS-tweaking, not architecture.

## Sources

- [Hugo Image Processing — official docs](https://gohugo.io/content-management/image-processing/) — verified 2026-04-28; documents `Resize`, `Fill`, page resources, caching in `resources/_gen/`, build-time considerations
- [Hugo Resize method](https://gohugo.io/methods/resource/resize/) — argument syntax, format conversion, quality flags
- [Hugo Fill method](https://gohugo.io/methods/resource/fill/) — anchor/center options for thumbnail crops
- [Switching off the Lights — Adding Dark Mode to Hugo (Yonkov)](https://yonkov.github.io/post/add-dark-mode-toggle-to-hugo/) — inline-script FOUC pattern
- [Adopting a Dark Theme in Hugo (Ken Muse)](https://www.kenmuse.com/blog/adopting-a-dark-theme-in-hugo/) — `data-theme` attribute approach
- [Adding support for dark and light images to Hugo's figure shortcode (Sander ten Brinke)](https://stenbrinke.nl/blog/adding-support-for-dark-and-light-images-to-hugo-figure-shortcode/) — image-pair pattern reference
- [Adding a picture gallery to your Hugo blog (Jack Henschel)](https://blog.cubieserver.de/2020/adding-a-picture-gallery-to-your-hugo-blog/) — page-bundle gallery pattern
- [Responsive and optimized images with Hugo (BryceWray)](https://www.brycewray.com/posts/2022/06/responsive-optimized-images-hugo/) — `srcset` patterns
- [Flexoki color palette spec (Steph Ango)](https://stephango.com/flexoki) — palette source for dark tokens
- Direct read of `themes/minimal/layouts/_default/baseof.html`, `partials/header.html`, `partials/footer.html`, `static/css/style.css`, `hugo.toml`, `content/about.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

---
*Architecture research for: Hugo v2.0 Brand & Gallery integration*
*Researched: 2026-04-28*

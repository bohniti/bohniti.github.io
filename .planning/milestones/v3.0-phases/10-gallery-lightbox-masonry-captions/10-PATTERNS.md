# Phase 10: GALLERY — Lightbox + Masonry + Captions — Pattern Map

**Mapped:** 2026-05-04
**Files analyzed:** 5 (1 NEW + 4 MODIFY)
**Analogs found:** 5 / 5 (100%)

---

## File Classification

| File | Status | Role | Data Flow | Closest Analog | Match Quality |
|------|--------|------|-----------|----------------|---------------|
| `content/gallery/index.md` | MODIFY | content (page-bundle frontmatter) | static config | itself (existing 6-line front matter) + `content/about/index.md` for `type:`-routed leaf bundle pattern | exact-self |
| `themes/minimal/layouts/gallery/single.html` | MODIFY | template (Hugo `{type}/single.html`) | request-response (build-time render) | itself (28 LOC); siblings `themes/minimal/layouts/about/single.html`, `_default/single.html` | exact-self |
| `themes/minimal/static/js/lightbox.js` | NEW | client script (page-scoped IIFE) | event-driven (DOM events: click, keydown, touchstart/end) | `themes/minimal/layouts/_default/baseof.html` lines 39–58 (theme-toggle IIFE) | exact role + exact data flow |
| `themes/minimal/static/css/style.css` | MODIFY | stylesheet (single-file, scoped sections) | static config | self — `/* === Theme toggle === */` (lines 102–157) for button rules; `/* === Gallery === */` (lines 311–339) for grid replacement; `@media (max-width: 600px)` (lines 535–568) for mobile add | exact-self |
| `.github/workflows/deploy.yml` | MODIFY | CI config (GitHub Actions step) | request-response (CI gate) | self — existing `Install Hugo` / `Build with Hugo` step structure | exact-self |

---

## Pattern Assignments

### `themes/minimal/static/js/lightbox.js` (NEW — IIFE, event-driven)

**Analog:** `themes/minimal/layouts/_default/baseof.html` lines 39–58 (end-of-body theme-toggle IIFE) — the project's canonical chrome IIFE.

**IIFE shell + early-return guard** (baseof.html:39–42):
```javascript
(function () {
  const toggle = document.querySelector('.theme-toggle');
  if (!toggle) return;
  // ... bind listeners, set initial state
```
Apply: `lightbox.js` opens with `(function () {`, queries `dialog#gallery-lightbox` and `.gallery-grid`, returns early if either is missing (page may render without photos).

**addEventListener / no-globals pattern** (baseof.html:50–57):
```javascript
toggle.addEventListener('click', function () {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  toggle.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
  toggle.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  try { localStorage.setItem('theme', next); } catch (_) { /* Safari private mode */ }
  // ...
});
```
Apply pattern to lightbox.js:
- One IIFE; no leaked globals.
- `const`/`let` only (CONVENTIONS — no `var`).
- `try { } catch (_) { }` for any potentially-throwing API (e.g. `localStorage` precedent — N/A here, but pattern-shape is "wrap in try/catch with `_` ignored err").
- `setAttribute('aria-label', ...)` on dynamic state change (D-17 → `dialog.setAttribute('aria-label', \`Photo ${n} of ${total}\`)`).

**Action-oriented aria-label idiom** (baseof.html:48):
```javascript
toggle.setAttribute('aria-label', initial === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
```
Apply: lightbox aria-labels describe the target action — `'Close gallery'`, `'Previous photo'`, `'Next photo'` (per UI-SPEC § Copywriting Contract). Static on buttons (set in template); dynamic on `<dialog>` itself.

**Comment style for behavior rationale** (baseof.html:34–38):
```javascript
// Theme toggle — single click handler. JS writes only documentElement.dataset.theme;
// CSS reads it (icon visibility, palette swap). aria-label is action-oriented:
// it describes the click target, not the current state (D-03, D-08, D-10).
// The icon SVGs are never touched by JS — visibility is 100% CSS (Pitfall 22 mitigation).
```
Apply: lead `lightbox.js` with a header comment block citing decisions D-08, D-09, D-10, D-11, D-15, D-16, D-17, D-18.

**Loaded with `defer` page-scoped (NOT in baseof.html)** — D-14 / Gate 2 assertion #5. Template precedent: existing `<link rel="stylesheet" href="{{ "css/style.css" | absURL }}">` (baseof.html:24) demonstrates the `{{ "path" | absURL }}` idiom. Apply in `gallery/single.html`: `<script src="{{ "js/lightbox.js" | absURL }}" defer></script>`.

---

### `themes/minimal/layouts/gallery/single.html` (MODIFY — template, request-response)

**Analog:** itself (current 28 LOC) — only 4 surgical edits per CONTEXT § Integration Points.

**Existing imports / range pattern to preserve** (gallery/single.html:1–9):
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
```
**Edit 1 (Gate 1 assertion #6 — sort by weight):** replace line 9 `{{ range $idx, $photo := . }}` with weight-sorted iteration. Per Hugo `sort` docs (RESEARCH.md) + Phase 10 D-04:
```go-html-template
{{ range $idx, $photo := sort . "Params.weight" "asc" }}
```
Note: the surrounding `{{ with .Resources.Match "photos/*" }}` rebinds the dot to the resource collection, so `sort .` operates on it. Hugo 0.157.0 `sort` signature: `sort COLLECTION FIELD ORDER`. Photos with no `weight` sort first (Hugo treats missing as zero) but D-04 mandates every photo has one.

**Existing image.Process directives** (gallery/single.html:10–11):
```go-html-template
{{ $thumb := $photo.Process "fill 600x400 Smart webp q75" }}
{{ $full  := $photo.Process "fit 1200x1200 webp q78" }}
```
**Edit 2 (Gate 1 assertion #7 — width-only Resize):** change line 10 thumb directive (D-05). Line 11 stays verbatim (D-06):
```go-html-template
{{ $thumb := $photo.Process "Resize 600x webp q75" }}
{{ $full  := $photo.Process "fit 1200x1200 webp q78" }}
```

**Existing `<a class="gallery-item">` wrapper** (gallery/single.html:12–14):
```go-html-template
<a class="gallery-item"
   href="{{ $full.RelPermalink }}"
   aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size">
```
**Edit 3 (Gate 1 assertion #8 — emit data-attrs):** preserve all three existing attributes (D-19, D-28); add `data-caption` and `data-alt`:
```go-html-template
<a class="gallery-item"
   href="{{ $full.RelPermalink }}"
   data-caption="{{ $photo.Params.caption }}"
   data-alt="{{ $photo.Params.alt }}"
   aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size">
```

**Edit 4 (Gate 2 assertions #1, #2, #5 — append dialog + script).** After line 25 `</div>` and before line 26 `{{ end }}` (the `with` close), append the `<dialog>` markup and the script tag inside `{{ define "main" }}`. Per D-09 / D-20 / UI-SPEC Gate 2.

Inline SVG inside each button MUST follow the icon convention (next section).

---

### `themes/minimal/layouts/partials/footer.html` — Inline SVG Icon Convention (read-only reference)

**Analog excerpt** (footer.html:7–10, GitHub icon — exact attribute set to copy for chevron-left, chevron-right, X):
```html
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5..."></path>
  <path d="M9 18c-4.51 2-5-2-7-2"></path>
</svg>
```

Apply to lightbox button SVGs (UI-SPEC Gate 2 assertion #3, Gate 4 assertion #8):
- Identical attribute order: `xmlns`, `width`, `height`, `viewBox`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`, `aria-hidden="true"`.
- Difference from footer: `width="24" height="24"` (footer is 18×18; lightbox buttons are 24×24 per UI-SPEC § Spacing Scale).
- Hand-author Lucide path strings inline. Lucide icon names: `x` (close), `chevron-left` (prev), `chevron-right` (next).

Wrapper anchor pattern (footer.html:6 — `aria-label` on parent of SVG):
```html
<a href="..." aria-label="GitHub">
  <svg ... aria-hidden="true">...</svg>
</a>
```
Apply on lightbox buttons: `aria-label` on `<button>`, `aria-hidden="true"` on inner `<svg>` (Sara Soueidan accessible-icon-button pattern).

---

### `themes/minimal/static/css/style.css` (MODIFY — stylesheet)

#### Sub-Pattern A: `body.page-{type}` scoping (D-21, Pitfall 17)

**Analog (existing in same file):**
```css
/* === Gallery === */                          /* line 311 */
body.page-gallery .site-wrapper { max-width: 1100px; }   /* line 312-314 */

/* === About === */                            /* line 341 */
body.page-about .about-hero { ... }            /* line 342-348 */
body.page-about .about-hero-photo img,         /* line 350-356 */
body.page-about .about-hero-img { ... }
```
Apply: every new lightbox / masonry rule MUST start with `body.page-gallery `. Forbidden generic selectors per Gate 6 #10: `.lightbox`, `.modal`, `.close`, `.prev`, `.next`, `.dialog`. Section comments use the established `/* === Section === */` shape; new sub-sections per CONTEXT line 121: `/* === Gallery — Masonry === */` and `/* === Gallery — Lightbox === */`.

#### Sub-Pattern B: Replace existing grid rules (Gate 1 assertions #1, #2, #5)

**Existing block to delete/replace** (style.css:316–339):
```css
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
Apply:
- Replace `.gallery-grid` rule with column-count masonry: `body.page-gallery .gallery-grid { column-count: 3; column-gap: 1rem; margin: 0; }` (Gate 1 #2).
- Update `.gallery-item` to add `break-inside: avoid; margin-bottom: 1rem;` (Gate 1 #5); preserve `display: block; line-height: 0;`; raise `border-radius: 4px` to `border-radius: var(--radius-soft);` (Phase 9 carry-forward per UI-SPEC Gate 6 #5).
- `.gallery-item:focus-visible` is already correct (matches Phase 8 pattern); just re-prefix with `body.page-gallery`.
- `.gallery-img`: keep `width: 100%; height: auto; display: block;`; raise `border-radius: 4px` to `var(--radius-soft);`.

#### Sub-Pattern C: Lightbox button visual rules (Gate 4 — analog: `.theme-toggle`)

**Analog excerpt** (style.css:102–157, Phase 8 theme-toggle — exact precedent for hit-target, button reset, focus-visible):
```css
.theme-toggle {
  /* Hit target ≥ 44×44 CSS-px (D-06, ICON-04 — WCAG 2.5.5 / iOS HIG) */
  display: inline-grid;
  place-items: center;
  min-width: 44px;
  min-height: 44px;
  /* Button reset */
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
  /* Icon color cascade — currentColor inside the SVGs reads from this (D-02) */
  color: var(--text-secondary);
}

/* ... */

.theme-toggle:hover {                          /* line 148-150 */
  color: var(--accent);
}

.site-nav a:focus-visible,
.theme-toggle:focus-visible {                  /* line 152-157 */
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```
Apply verbatim shape to `.gallery-lightbox-close, .gallery-lightbox-prev, .gallery-lightbox-next` (Gate 4 assertions #1–#6):
- Same `display: inline-grid; place-items: center; min-width: 44px; min-height: 44px;`.
- Same button reset (`background: transparent; border: 0; padding: 0; cursor: pointer;`).
- Default `color: var(--text);` (Gate 4 #4 — note: theme-toggle uses `--text-secondary`; lightbox buttons use `--text` because they sit on the `--bg` dialog interior, not in the header).
- `:hover { color: var(--accent); }` outside the media query (Gate 4 #5).
- `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: var(--radius-soft); }` — bump radius from `2px` to `var(--radius-soft)` per UI-SPEC Gate 4 #6.

#### Sub-Pattern D: `prefers-reduced-motion: no-preference` wrap (D-22, Pitfall 9)

**Analog excerpt 1** (style.css:50–56, body color transitions):
```css
@media (prefers-reduced-motion: no-preference) {
  body {
    transition:
      background-color 150ms ease,
      color            150ms ease,
      border-color     150ms ease;
  }
}
```

**Analog excerpt 2** (style.css:138–146, theme-toggle icon cross-fade — closer to lightbox use case):
```css
/* Cross-fade ≤ 150ms — opacity-only, no rotation (D-07, ICON-05).
   Declared ONLY inside prefers-reduced-motion: no-preference (Pitfall 9 mitigation):
   reduced-motion users get an instant swap, not a "tasteful 50ms" fallback. */
@media (prefers-reduced-motion: no-preference) {
  .theme-toggle .icon-sun,
  .theme-toggle .icon-moon {
    transition: opacity 150ms ease;
  }
}
```
Apply: lightbox button `transition: color 150ms ease;` lives ONLY inside `@media (prefers-reduced-motion: no-preference) { body.page-gallery .gallery-lightbox-close, body.page-gallery .gallery-lightbox-prev, body.page-gallery .gallery-lightbox-next { transition: color 150ms ease; } }`. The `:hover { color: var(--accent); }` rule itself stays OUTSIDE (Gate 4 #5 — color change is not motion). Same pattern for any backdrop/dialog open transition (Gate 6 #6, #7).

#### Sub-Pattern E: Mobile breakpoint addition (Gate 1 assertion #4)

**Analog excerpt** (style.css:535–568, existing `@media (max-width: 600px)` block):
```css
@media (max-width: 600px) {
  html { font-size: 16px; }
  /* ... */
  body.page-about .about-hero {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  /* Phase 9 — mobile reflow extensions (REQ ABOUT-07, D-10) */
  body.page-about .about-section,
  body.page-about .about-prose {
    margin-top: 2.5rem;
  }
  /* ... */
}
```
Apply: ADD `body.page-gallery .gallery-grid { column-count: 1; }` inside this existing block. Annotate per Phase 9 precedent: `/* Phase 10 — mobile single-column gallery (REQ GALLERY-02, D-07) */`.

#### Sub-Pattern F: New mid-breakpoint (Gate 1 assertion #3)

NO existing analog for `(min-width: 600px) and (max-width: 899px)` in this file. Insert a NEW `@media` block immediately after the existing `(max-width: 600px)` block (at file end), following the same comment-then-rule convention:
```css
/* Phase 10 — tablet two-column masonry (REQ GALLERY-02, D-07) */
@media (min-width: 600px) and (max-width: 899px) {
  body.page-gallery .gallery-grid { column-count: 2; }
}
```

---

### `content/gallery/index.md` (MODIFY — frontmatter authoring)

**Analog:** itself (current 6-line state) + Hugo docs `[[resources]]` pattern (RESEARCH.md). The page-bundle leaf-bundle convention (`type: "gallery"`) is established; only the `[[resources]]` array is new.

**Existing frontmatter to preserve** (full file, lines 1–6):
```yaml
---
title: "Gallery"
type: "gallery"
build:
  publishResources: false
---
```

Apply (D-01, D-03, D-04, Pitfall 14): convert to TOML or keep YAML and add `[[resources]]` blocks. Hugo accepts both; project precedent (other content files) uses YAML — but `[[resources]]` is a TOML array idiom. Hugo's resolution: use TOML frontmatter (`+++`) OR YAML `resources:` list. Per CONTEXT D-01 explicit phrasing "`[[resources]]` blocks", switch the file to TOML. Filenames must byte-match `content/gallery/photos/` exactly (case-preserved — repo has `.jpg`, `.JPG`, `.jpeg`, `.JPEG` mixed).

Schema per entry (D-01, D-03, D-04):
```toml
[[resources]]
src = "photos/<exact-filename-with-case>"
name = "photos/<exact-filename-with-case>"
[resources.params]
caption = "Optional 1–2 sentence story."
alt = "Required descriptive alt text."
weight = 10
```

Existing 18 photos to author entries for (from `content/gallery/photos/`):
`20210710_132418.jpg`, `5dc795b8-3921-45b8-a651-5b434e405259.jpg`, `60130366-e95c-48a9-b8cd-aa38090c02c2.jpg`, `7eb72991-8aac-44e7-92f7-f71968357ceb.jpg`, `98562fcd-4559-4d91-8020-48ac5dbc9610.jpg`, `DSC09782.JPG`, `DSC09784.JPG`, `f2e6acbb-7e38-4235-aade-b23a22622596.jpg`, `IMG_0256.jpeg`, `IMG_1288.JPG`, `IMG_1299.JPG`, `IMG_1499.jpeg`, `IMG_1646.jpeg`, `IMG_2009.jpeg`, `IMG_5685_Original.JPG`, `IMG_6546.jpeg`, `IMG_7828.jpeg`, `IMG_8113.jpg` (18 total — count matches CONTEXT).

---

### `.github/workflows/deploy.yml` (MODIFY — CI step)

**Analog excerpt** (deploy.yml:27–40, existing build job step structure):
```yaml
      - name: Install Hugo
        run: |
          wget -O ${{ runner.temp }}/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb
          sudo dpkg -i ${{ runner.temp }}/hugo.deb
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v5
      - name: Build with Hugo
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
        run: hugo --minify --baseURL "${{ steps.pages.outputs.base_url }}/"
```

Apply (D-23 layer 2): insert NEW step `Verify EXIF scrub` BETWEEN `Checkout` and `Setup Pages` (pre-build placement catches regression early; planner may also place post-checkout / post-build per D-23 note). Pattern shape (multiline `run:` with bash):
```yaml
      - name: Verify EXIF scrub (gallery)
        run: |
          sudo apt-get update
          sudo apt-get install -y libimage-exiftool-perl
          # Fail if any forbidden EXIF field appears in source photos.
          forbidden='GPSLatitude|GPSLongitude|Make|Model|SerialNumber'
          if exiftool content/gallery/photos/*.{jpg,JPG,jpeg,JPEG} 2>/dev/null | grep -E "^($forbidden)\s*:"; then
            echo "::error::EXIF scrub failed — forbidden fields present in content/gallery/photos/*."
            exit 1
          fi
```
Conventions to copy from existing steps:
- `name:` is human-readable, present-tense imperative ("Install Hugo", "Build with Hugo", "Setup Pages"). Apply: `Verify EXIF scrub (gallery)`.
- `run: |` heredoc for multi-line bash.
- `sudo apt-get install -y` is project precedent (none exist; this is the first apt step but it is the standard ubuntu-latest pattern).
- No new env vars needed.
- ~10 LOC budget per CONTEXT.

---

## Shared Patterns (Cross-Cutting)

### Pattern S1 — IIFE, no globals
**Source:** `themes/minimal/layouts/_default/baseof.html` lines 13–22 (head theme bootstrap) and 39–58 (body theme toggle).
**Apply to:** `lightbox.js` ENTIRE file.
**Excerpt:**
```javascript
(function () {
  // const/let only, never var
  // Early return if required DOM is missing
  // addEventListener for all bindings
})();
```

### Pattern S2 — Action-oriented `aria-label`
**Source:** baseof.html:48 / `partials/footer.html`:6, 12 (parent has `aria-label`, inner SVG is `aria-hidden="true"`).
**Apply to:** all lightbox buttons (`Close gallery`, `Previous photo`, `Next photo`) AND dynamic `dialog.setAttribute('aria-label', \`Photo ${n} of ${total}\`)` in JS.

### Pattern S3 — Hand-authored inline SVG (Lucide visual language)
**Source:** `themes/minimal/layouts/partials/footer.html` lines 7–17.
**Apply to:** chevron-left, chevron-right, X icons inside the three lightbox buttons. Identical attribute set; bump `width="18" height="18"` to `width="24" height="24"`. Anti-feature: NEVER `npm install lucide` — paths are hand-authored inline.

### Pattern S4 — `body.page-{type}` CSS scoping
**Source:** `themes/minimal/layouts/_default/baseof.html` line 26 (`<body class="page-{{ .Type | default "default" }}">`); existing rules in style.css `/* === About === */` (lines 341–356, all prefixed `body.page-about`).
**Apply to:** every new lightbox/masonry CSS rule prefixed `body.page-gallery `.

### Pattern S5 — `prefers-reduced-motion: no-preference` gating
**Source:** style.css lines 50–56 (body), lines 141–146 (theme-toggle icon cross-fade).
**Apply to:** every new `transition:` in the lightbox CSS block. Color/state changes go OUTSIDE; only the `transition` property itself is wrapped.

### Pattern S6 — Existing tokens only (no new hexes)
**Source:** style.css lines 4–34 (`:root` + `:root[data-theme="dark"]`). All existing tokens: `--bg`, `--bg-secondary`, `--text`, `--text-secondary`, `--text-muted`, `--accent`, `--accent-hover`, `--link`, `--border`, `--code-bg`, `--max-width`, `--radius-soft` (Phase 9, line 18).
**Apply to:** lightbox + masonry rules consume these; the ONLY exception is the locked rgba pair `rgba(16, 15, 15, 0.85)` / `rgba(16, 15, 15, 0.6)` for `::backdrop` (D-12, D-13 — theme-invariant by design).

### Pattern S7 — Page-bundle resource access
**Source:** `gallery/single.html:6` (`{{ with .Resources.Match "photos/*" }}`) — directly applicable; no other reference needed.
**Apply to:** template Edit 1 (sort by weight). Note: `themes/minimal/layouts/_default/_markup/render-image.html` (mentioned in canonical_refs as `Page.Resources.GetMatch` precedent) is NOT modified by Phase 10 — gallery iterates `Resources.Match` directly, not via markdown image refs. The render-image hook is read-only context for "how Hugo resolves page-bundle resources" understanding.

---

## No Analog Found

None. Every file in scope has a strong analog:
- 4 of 5 files are MODIFY operations on files whose CURRENT contents are the closest analog to themselves.
- The 1 NEW file (`lightbox.js`) has a near-perfect analog in baseof.html lines 39–58 — same role (chrome IIFE), same data flow (DOM event-driven), same author conventions.

---

## Metadata

**Analog search scope:**
- `themes/minimal/layouts/_default/baseof.html` (full file, 62 LOC)
- `themes/minimal/layouts/partials/footer.html` (full file, 22 LOC)
- `themes/minimal/layouts/gallery/single.html` (full file, 28 LOC)
- `themes/minimal/static/css/style.css` (lines 1–170 + 300–360 + 530–568, total ~270 LOC of 568)
- `content/gallery/index.md` (full file, 6 LOC)
- `.github/workflows/deploy.yml` (full file, 56 LOC)
- `content/gallery/photos/` (directory listing — 18 photos confirmed)

**Files scanned:** 7
**Analogs ranked:** 5 exact-self / role + flow matches; 0 partial; 0 missing
**Pattern extraction date:** 2026-05-04

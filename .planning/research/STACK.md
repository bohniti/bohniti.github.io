# Stack Research — v2.0 Brand & Gallery

**Domain:** Static-site brand identity, theming, and image-heavy gallery for Hugo
**Researched:** 2026-04-28
**Confidence:** HIGH

## Scope Note

This document covers **only stack additions/changes for v2.0 features**. Hugo, the minimal theme, GitHub Actions deploy, and Goldmark `unsafe = true` are already validated (see `.planning/codebase/STACK.md`) and are NOT re-researched. The recommended approach for every v2.0 feature uses **Hugo built-ins, vanilla JS, and CSS custom properties** — zero new runtime dependencies.

## Recommended Stack

### Core Technologies (Already Pinned — No Change)

| Technology | Version | Purpose | Why It Already Fits v2.0 |
|------------|---------|---------|--------------------------|
| Hugo Extended | 0.157.0 (pinned in `.github/workflows/deploy.yml`) | Static site generator | Includes the `image.Process` / `Resize` / `Fill` / `Crop` / `Fit` pipeline used for the gallery and sprite slicing — no upgrade required for v2.0. Latest is 0.160.1 (2026-04-08) but features needed have existed since 0.83. Defer upgrade to a separate housekeeping task. |
| CSS (vanilla) | n/a | Theming via CSS custom properties already declared on `:root` in `themes/minimal/static/css/style.css` (lines 4–18) | The Flexoki light palette is already variable-driven; adding a dark palette is a `[data-theme="dark"]` selector override — no preprocessor or framework needed. |
| Vanilla JS (ES6+) | n/a | Theme-toggle button + no-flash inline `<head>` script | Repository convention is "no JS frameworks" (CLAUDE.md). The toggle is < 30 lines; any library would be larger than the feature itself. |

### New Stack Additions

| Addition | Version | Purpose | Why Recommended |
|----------|---------|---------|-----------------|
| **Hugo `image.Process` pipeline** | bundled with Hugo 0.157.0 | Generate responsive `srcset` thumbnails + full-size variants for the 18 gallery photos | Built-in, cached in `resources/_gen/`, supports `resize`, `fill`, `fit`, `crop`, `qN` quality, anchor (incl. `Smart`), and `webp` output. Eliminates need for an external image pipeline. (Source: gohugo.io image-processing docs) |
| **WebP output format** | via Hugo `image.Process "... webp qN"` | Smaller gallery payloads than JPEG at equivalent quality | Universally supported in 2026 (Safari 14+, all evergreen browsers). Hugo emits WebP natively; no Node/sharp/imagemin dependency. AVIF is NOT yet supported by Hugo's image pipeline — skip it. |
| **CSS custom properties + `[data-theme]` attribute selector** | CSS Level 4 (universal browser support) | Light/dark palette switch with zero runtime cost | Single source of truth for color tokens. Toggling `<html data-theme="dark">` re-cascades all variables instantly. No CSS-in-JS, no theme provider. |
| **Inline `<head>` theme bootstrap script** | ~15 lines of vanilla JS | Apply theme **before first paint** to prevent FOUC ("flash of unstyled content") | Industry-standard pattern (used by MUI, Next.js `next-themes`, every well-built static site). Reads `localStorage.theme` then falls back to `window.matchMedia('(prefers-color-scheme: dark)')`. Must be **inline and synchronous** in `<head>` — external scripts defer past first paint. |
| **`<link rel="icon" type="image/svg+xml">` favicon (preferred)** | HTML5 standard | Single scalable favicon with a CSS `@media (prefers-color-scheme: dark)` clause inside the SVG | Modern browsers (Chrome 80+, Firefox 41+, Safari 16+) support SVG favicons that adapt to OS theme automatically. Falls back to PNG/ICO for older clients. (Source: realfavicongenerator, evilmartians) |
| **Pillow (Python) — one-off only** | 12.2.0 (latest stable, 2026-04-01) | Slice `images/logos.png` (1536×1024 sprite, 2 rows × 4 cols) into 8 individual PNGs | Run once locally, commit the 8 outputs to `images/icon/`, then delete the script (or keep in `scripts/` as documentation). NOT a runtime dependency — never executed during Hugo build or CI. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **None — explicitly** | — | — | The v2.0 milestone introduces **zero new runtime dependencies**. Pillow is a build-time, one-shot tool; everything else is Hugo built-in or vanilla web platform. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Pillow 12.2.0 | One-off sprite slicer (`scripts/slice_logos.py`) | Install in a throwaway venv: `python3 -m venv .venv && .venv/bin/pip install Pillow==12.2.0`. Do NOT add to a `requirements.txt` — there is no project-level Python dependency manifest, and adding one would create false long-term commitments. |
| Hugo CLI | Local preview of gallery image processing | Image processing is build-time; you must `hugo server` (or `hugo`) to see processed assets in `resources/_gen/`. CI uses `hugo --minify` already. |
| `git mv` | Rename `images/galary/` → `images/gallery/` | Single command preserves history. Do not `rm -rf` and re-add. |

## Installation

```bash
# === ONE-OFF: Sprite slicing tooling (build-time only) ===
python3 -m venv .venv
.venv/bin/pip install Pillow==12.2.0
.venv/bin/python scripts/slice_logos.py   # writes 8 PNGs to images/icon/
deactivate
# Optional: rm -rf .venv  (no runtime need for it)

# === RUNTIME: Nothing to install ===
# Hugo image processing, CSS variables, and vanilla JS need zero installs.
```

## Integration Points (Where Each Choice Lands)

| Concern | File | What Changes |
|---------|------|--------------|
| No-flash theme bootstrap | `themes/minimal/layouts/_default/baseof.html` | Add `<script>` block immediately after `<meta charset>` and before `<link rel="stylesheet">` — must be inline, synchronous, in `<head>`. |
| Dark palette tokens | `themes/minimal/static/css/style.css` | Add `[data-theme="dark"] { --bg: ...; --text: ...; ... }` block right after the existing `:root { ... }` block (lines 4–18). |
| Theme toggle button | `themes/minimal/layouts/partials/header.html` | Add `<button class="theme-toggle" aria-label="Toggle color theme">…</button>` between `.site-title` and `.site-nav` (or at the end of the nav). Wire to a small JS file in `themes/minimal/static/js/theme-toggle.js` loaded with `defer`. |
| Wordmark | `themes/minimal/layouts/partials/header.html` | Replace `{{ .Site.Title }}` text in `.site-title a` with two `<img>` tags (light + dark variants), one shown via CSS per `[data-theme]`. Or use a single `<picture>` with `<source media="(prefers-color-scheme: ...)">` — but theme toggle overrides OS preference, so the `[data-theme]` CSS approach is more correct. |
| Favicon set | `themes/minimal/layouts/_default/baseof.html` | Add `<link rel="icon">` tags inside `<head>` after the `<title>` element. |
| Gallery page | `content/gallery/_index.md` (branch bundle) + `themes/minimal/layouts/gallery/list.html` (new) | Branch bundle so photos can be co-located as page resources accessed via `.Resources.Match "*.jpg"`. New layout file uses `range` over `.Resources.ByType "image"` + `image.Process`. |
| Gallery photos | `content/gallery/photos/*.jpg` (moved from `images/galary/`) | Hugo page bundles want resources adjacent to `_index.md` for `.Resources` access. Top-level `images/` is `static/`-style and bypasses the resource pipeline. **Move them into the bundle.** |
| About page photos | `content/about.md` → convert to leaf bundle `content/about/index.md` with adjacent photos | Same rationale: resource pipeline access. |

## Detailed Recommendations

### 1. No-Flash Theme Toggle (Vanilla JS + CSS Custom Properties)

**Pattern (verified — see whitep4nth3r, bram.us, MUI):**

1. **Inline `<head>` bootstrap** in `baseof.html` (BEFORE the stylesheet link):
   ```html
   <script>
     (function() {
       try {
         var saved = localStorage.getItem('theme');
         var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
         var theme = saved || (prefersDark ? 'dark' : 'light');
         document.documentElement.setAttribute('data-theme', theme);
       } catch (e) {
         document.documentElement.setAttribute('data-theme', 'light');
       }
     })();
   </script>
   ```
   - Must be inline (external scripts don't run before first paint reliably).
   - Wrapped in IIFE + try/catch (private browsing can throw on `localStorage`).
   - Sets `data-theme` on `<html>`, not `<body>` — matches CSS variable cascade root.

2. **CSS** in `style.css`:
   ```css
   :root, [data-theme="light"] { --bg: #FFFCF0; /* … */ }
   [data-theme="dark"] {
     --bg: #100F0F;
     --bg-secondary: #1C1B1A;
     --text: #FFFCF0;
     /* Flexoki dark palette */
   }
   ```

3. **Toggle button** loaded with `defer` (or at end of body) — only handles user click; OS preference + persistence are already done by the bootstrap.

**Why not `prefers-color-scheme` alone:** Spec ties the site to the OS. Users want override. The bootstrap script gives both.

**Why not a CSS-only toggle (`<input type="checkbox">` + `:has()`):** Doesn't persist, doesn't read OS preference, fails on first paint after preference change.

### 2. Hugo Image Processing for Gallery

**Recommended pipeline (verified — gohugo.io):**

```go-html-template
{{/* themes/minimal/layouts/gallery/list.html */}}
{{ $photos := .Resources.Match "photos/*.{jpg,jpeg,png}" }}
<ul class="gallery-grid">
  {{ range $photos }}
    {{ $thumb := .Process "fill 600x400 Smart webp q75" }}
    {{ $full  := .Process "fit 1600x1600 webp q82" }}
    <li>
      <a href="{{ $full.RelPermalink }}">
        <img
          src="{{ $thumb.RelPermalink }}"
          width="{{ $thumb.Width }}"
          height="{{ $thumb.Height }}"
          loading="lazy"
          decoding="async"
          alt="{{ .Name }}">
      </a>
    </li>
  {{ end }}
</ul>
```

**Key choices:**
- `fill 600x400 Smart` — Hugo's `Smart` anchor uses entropy detection to pick the most interesting crop region. Avoids decapitated portraits.
- `webp q75` for thumbs, `q82` for full-size — verified Hugo syntax. WebP cuts ~30% off JPEG at matched perceptual quality.
- `loading="lazy" decoding="async"` — native browser lazy-loading, supported everywhere since 2022. No IntersectionObserver shim needed.
- Explicit `width`/`height` attributes from `$thumb.Width/Height` — prevents CLS (Cumulative Layout Shift).

**Source images:** 18 photos, 150 KB → 7.2 MB. Total raw = ~50 MB; processed thumbs will be ~50 KB × 18 = ~900 KB. Hugo caches in `resources/_gen/` so build only re-processes on source change.

**Why not Hugo Pipes / `resources.Get`:** `Get` is for `assets/` directory single files (e.g., a global CSS file). Page bundles use `.Resources.Match` which is correct for per-page galleries.

**Why not a JS lightbox library (PhotoSwipe, glightbox):** Adds 30+ KB JS. Native `<a href="$full">` opening in a new tab is sufficient for this milestone. If a lightbox is wanted later, **defer to a separate phase** with explicit cost/benefit.

### 3. Favicon + Brand Asset Wiring

**Recommended HTML (in `<head>` of `baseof.html`):**

```html
<link rel="icon" href="{{ "favicon.ico" | absURL }}" sizes="32x32">
<link rel="icon" href="{{ "favicon.svg" | absURL }}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{{ "apple-touch-icon.png" | absURL }}">
```

**File set in `static/`** (served as-is, root URLs):
- `favicon.ico` — 32×32 multi-res ICO (compatibility fallback for older browsers / pinned-tab scenarios)
- `favicon.svg` — single SVG with embedded `@media (prefers-color-scheme: dark)` to swap colors automatically (browser-level, independent of site toggle)
- `apple-touch-icon.png` — 180×180 PNG (iOS home-screen)

**Skip:** Multi-size PNG fleet (16/48/96/144/...), `manifest.json`, MS tile config. Not needed for a personal site without PWA install requirements. The 3-file set above covers > 99% of real-world contexts in 2026 (verified — evilmartians, realfavicongenerator).

**Source:** Generate `favicon.ico` and `favicon.svg` from the Favicon column of the sliced sprite (the "TB in circle" variants). The light variant becomes the visible glyph; dark-mode swap can either be handled in-SVG via CSS or by serving a separate URL — in-SVG is simpler.

### 4. Sprite Slicing — Recommended: Pillow One-Off Script

**The `images/logos.png` source is 1536×1024 = 384×256 per cell** (2 rows × 4 cols).

**Two viable options — pick one. Recommendation: Pillow.**

#### Option A (RECOMMENDED): Python + Pillow one-off script

```python
# scripts/slice_logos.py
from PIL import Image
from pathlib import Path

SRC = Path("images/logos.png")
OUT = Path("images/icon")
OUT.mkdir(parents=True, exist_ok=True)

cols = ["logo", "icon", "minimum", "favicon"]
rows = ["dark", "light"]  # row 0 = dark variants, row 1 = light variants

img = Image.open(SRC)
cell_w, cell_h = img.width // 4, img.height // 2  # 384 × 256

for r, row_name in enumerate(rows):
    for c, col_name in enumerate(cols):
        box = (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)
        crop = img.crop(box)
        crop.save(OUT / f"{col_name}-{row_name}.png", optimize=True)
        print(f"wrote {OUT}/{col_name}-{row_name}.png")
```

**Pros:**
- Runs once, commit the 8 PNGs, done. No build-time cost on every Hugo run.
- Trivial to inspect outputs visually before committing.
- Pillow's `optimize=True` produces smaller PNGs than Hugo's pipeline for this case.
- Pillow already used elsewhere in Python community; matches existing Python convention (PEP 8, `pathlib.Path`, `if __name__ == "__main__"` from CLAUDE.md).
- Straight crop on a known grid — Pillow is a 2-line API for this.

**Cons:**
- Requires a one-time `pip install Pillow` in a venv.
- The slicing logic isn't in version control as part of the build.

#### Option B: Hugo `image.Crop` from a global resource

```go-html-template
{{ $sprite := resources.Get "images/logos.png" }}
{{ $logoLight := $sprite.Process "crop 384x256 r0 c0" }}  {{/* approximate — see caveat */}}
```

**Pros:**
- Pure Hugo, no Python.
- Slicing logic is version-controlled in the template.

**Cons (CRITICAL):**
- **Hugo's `Process` syntax is "ACTION DIMENSIONSxDIMENSIONS ANCHOR FORMAT qQUALITY".** The anchor is an enum (`TopLeft`, `Top`, `TopRight`, `Center`, ..., `Smart`) — **NOT pixel offsets**. Cropping a specific (col, row) cell from a sprite requires either offset coordinates (which Hugo's Process action does NOT accept) or 8 separate "anchor"-based crops with manually-tuned target sizes — fragile and unintuitive.
- For an asymmetric sprite, you'd need either pre-resize tricks or a custom approach. The Hugo image API is designed for "give me the interesting region of one image" not "give me the (2,3) cell of a grid."
- Adds runtime build cost on every Hugo build (cached, but still part of the resource graph).
- 8 separate logo files are referenced from many places (header, favicon, manifest); having them as static files at known paths is simpler than pulling them through resource pipelines every time.

**Verdict:** Pillow one-off wins. Sprite slicing is an artifact-creation step, not a per-request transformation. Run it once, commit the 8 PNGs, treat them as static assets. The Hugo image pipeline is the right tool for the gallery (where source images change and we want responsive variants); it is the wrong tool for chopping a fixed grid into 8 named files.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Vanilla JS theme toggle | `next-themes`, `theme-change` (npm), Alpine.js | Never — they bring a build step + dependency manifest the project explicitly avoids. |
| CSS custom properties + `[data-theme]` | Tailwind `dark:` classes, SCSS theme maps | Never for this project — Tailwind is a framework rebuild; SCSS isn't currently used despite Hugo Extended being available. |
| Hugo `image.Process` | Cloudinary, imgix, Vercel Image Optimization | Never — adds a network dependency and external account; Hugo's pipeline is sufficient for 18 photos. |
| Hugo `image.Process "... webp"` | sharp/imagemin via Hugo Pipes / Node script | Never — would add Node.js to the project for no measurable benefit. |
| WebP | AVIF | When Hugo gains AVIF encoder support (not yet — confirmed via Hugo image-processing docs). Revisit in 2027+. |
| SVG favicon (in-SVG dark-mode `@media`) | Two separate favicon URLs swapped by JS | If targeting iOS Safari < 16 specifically. The SVG approach is now baseline-supported. |
| Native lazy-loading + `<a>` to full-size | PhotoSwipe / glightbox JS lightbox | When users explicitly request swipe gestures, captions, or zoom. Defer to later milestone with concrete cost. |
| Pillow one-off slicer | Hugo `image.Crop` | Never for this sprite — Hugo's anchor-based cropping isn't designed for grid extraction. |
| Pillow one-off slicer | ImageMagick CLI | Pillow is more readable Python and matches existing repo Python convention. ImageMagick is fine if a dev doesn't want Python — but project already has Python scripts. |

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **`next-themes`, `theme-change`, or any npm theme library** | Requires Node.js, `package.json`, build step. The project has none of these by design (CLAUDE.md: "no JS frameworks"). | Inline `<head>` script + CSS variables (~30 lines total). |
| **Tailwind CSS** | Full framework rebuild. Project uses a single hand-written `style.css`. | Extend the existing `:root` variables with a `[data-theme="dark"]` block. |
| **SCSS/Sass** | Hugo Extended supports it, but the existing stylesheet is plain CSS. Introducing SCSS for this milestone would be churn without benefit. | CSS custom properties already do everything needed. |
| **Cloudinary / imgix / external image CDN** | Hugo's built-in pipeline handles 18 photos trivially; external services add account dependency, latency, cost, and a runtime third party. | `.Resources.Match` + `.Process "fill 600x400 Smart webp q75"`. |
| **AVIF output** | Hugo image pipeline does not yet emit AVIF (verified — only `bmp/gif/jpeg/png/tiff/webp` listed). | WebP (universal browser support, ~30% smaller than JPEG). |
| **`<picture>` with `<source>` for theme switching** | OS preference is only one input; user's manual toggle must override. `<picture media="(prefers-color-scheme: dark)">` cannot be overridden by JS without DOM surgery. | Two `<img>` tags toggled by `[data-theme]` CSS, OR a single `<img>` whose `src` is set by JS after toggle. |
| **PhotoSwipe / glightbox / any JS lightbox** | 30+ KB JS for a personal gallery is gold-plating. | `<a href="$full" target="_blank">` — opens full-size in new tab. Defer lightbox to a later phase if user feedback demands it. |
| **`manifest.json`, `browserconfig.xml`, full multi-size PNG fleet (16/48/96/144/192/512)** | Personal blog without PWA install or pinned-tile requirements doesn't need them. They balloon the file count for negligible coverage gain. | 3-file set: `favicon.ico` (32) + `favicon.svg` + `apple-touch-icon.png` (180). |
| **Adding Pillow to a `requirements.txt`** | Project has no `requirements.txt`; creating one implies a runtime Python dependency. The slicer is one-off — run, commit outputs, optionally delete the venv. | Document install in the slicer script's docstring. Keep Pillow off the build path. |
| **Hugo `image.Crop` for the sprite** | Hugo's crop anchors are enums, not coordinates — wrong tool for grid extraction. | Pillow one-off `crop((x1, y1, x2, y2))`. |
| **Mixing the Pillow slicer into CI/Hugo build** | Adds Python to the deploy environment for a one-shot task already done. | Run locally, commit outputs to `images/icon/`, never run again. |
| **External fonts for the wordmark** | The wordmark is a bitmap glyph (sliced from `logos.png`), not live text. Loading a custom font would be redundant and add a network request. | Use the sliced PNG/SVG as an `<img>`. |

## Stack Patterns by Variant

**If the wordmark sprite cells turn out to have transparency issues after slicing:**
- Re-export `favicon-light.png` / `favicon-dark.png` as PNG-32 (Pillow `optimize=True` preserves alpha by default for RGBA mode)
- Or trace into SVG (Inkscape `Trace Bitmap`) — only if the bitmap looks soft at favicon sizes

**If Hugo build time grows uncomfortable when processing all 18 photos:**
- Hugo caches in `resources/_gen/images` — first build is slow, incrementals are fast
- Already in CI: `HUGO_CACHEDIR` is set to runner temp, but caching across CI runs would require GitHub Actions cache step
- If this becomes a real problem, add an `actions/cache@v4` step keyed on `images/gallery/**` hash. **Defer until measured.**

**If the user wants the gallery photos to load progressively (LQIP / blur-up):**
- Hugo can emit a tiny base64 JPEG via `images.Filter` + base64 encoding in a `style="background-image:..."` attribute
- Adds template complexity. **Defer to a later milestone** unless 7 MB photos cause actual perceived-load complaints.

## Version Compatibility

| Component | Requires | Notes |
|-----------|----------|-------|
| Hugo `image.Process "... webp ..."` | Hugo 0.83+ | Pinned 0.157.0 is far past this; safe. |
| Hugo `Smart` crop anchor | Hugo 0.83+ | Same; safe. |
| Native `loading="lazy"` on `<img>` | All evergreen browsers since 2022 | Safe baseline. |
| `prefers-color-scheme` media query | All evergreen browsers since 2019 | Safe baseline. |
| SVG favicon (`type="image/svg+xml"`) | Chrome 80+ (2020), Firefox 41+ (2015), Safari 16+ (2022) | Safari 14/15 falls back to `favicon.ico`. Acceptable. |
| CSS custom properties | All evergreen browsers since 2017 | Safe baseline. |
| Pillow 12.2.0 | Python 3.10+ | macOS dev box has Python 3.x; verify with `python3 --version` before running slicer. |
| WebP `<img>` | All evergreen browsers since 2020 (incl. Safari 14+) | Safe baseline; no JPEG fallback `<picture>` needed. |

## CDN / External Asset Strategy

**The v2.0 milestone adds NO new CDN scripts.** Existing CDN includes (Leaflet, Plotly, Mermaid, Instagram embed.js) live inline in specific blog posts and are out of scope. The brand+gallery feature set is fully self-hosted: sliced PNGs, Hugo-processed WebP variants, and inline JS/CSS.

If a future feature requires a CDN script (e.g., a lightbox), use the existing convention: `<script src="https://cdn.example.com/lib@x.y.z/dist/lib.min.js" integrity="sha384-..." crossorigin="anonymous"></script>` with a pinned version + SRI hash, loaded only on the page that needs it (not globally).

## Sources

- **Hugo image processing** — https://gohugo.io/methods/resource/process/ (verified syntax: `ACTION DIMENSIONSxDIMENSIONS ANCHOR FORMAT qQUALITY`; anchors `TopLeft..BottomRight, Center, Smart`; formats `bmp, gif, jpeg, png, tiff, webp`; quality 1–100). HIGH confidence.
- **Hugo image-processing overview** — https://gohugo.io/content-management/image-processing/ (Resize/Fill/Fit/Crop semantics, WebP support, build caching). HIGH confidence.
- **Hugo page bundles** — https://gohugo.io/content-management/page-bundles/ (`.Resources.Match` proximity rules, leaf vs branch). HIGH confidence.
- **Hugo releases** — https://github.com/gohugoio/hugo/releases (latest 0.160.1 on 2026-04-08; pinned 0.157.0 has every needed feature). HIGH confidence.
- **Pillow 12.2.0 release notes** — https://pillow.readthedocs.io/en/stable/releasenotes/index.html (released 2026-04-01; quarterly cadence; basic `Image.crop / save` API stable across versions). HIGH confidence.
- **Favicon best practice 2026** — https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs and https://faviconstudio.com/blog/favicon-sizes-complete-guide (3-file baseline: `favicon.ico` + `favicon.svg` + `apple-touch-icon.png`; SVG with embedded `@media (prefers-color-scheme: dark)` for OS-level theme adaptation). MEDIUM confidence (multiple credible secondary sources agree; no single canonical authority).
- **No-flash dark mode pattern** — https://whitep4nth3r.com/blog/best-light-dark-mode-theme-toggle-javascript/ and https://www.bram.us/2020/04/26/the-quest-for-the-perfect-dark-mode-using-vanilla-javascript/ (inline `<head>` IIFE, `data-theme` attribute on `<html>`, localStorage + matchMedia cascade). MEDIUM confidence (well-established community pattern, multiple independent sources).
- **Existing repo state** — `themes/minimal/static/css/style.css` lines 4–18 (Flexoki light palette already on `:root`); `hugo.toml` (Hugo 0.157.0 pinned, `unsafe = true`); `.planning/codebase/STACK.md` (existing stack baseline). HIGH confidence.

---
*Stack research for: v2.0 Brand & Gallery — additions only*
*Researched: 2026-04-28*

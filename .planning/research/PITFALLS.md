# Pitfalls Research

**Domain:** Hugo personal blog adding brand identity (theme toggle, logos, favicon, wordmark) + photo gallery
**Researched:** 2026-04-28
**Confidence:** HIGH (verified against official Hugo docs, web.dev, MDN, Evil Martians 2026 favicon guide; integration pitfalls grounded in this repo's actual structure)

> Scope reminder: this is a SUBSEQUENT milestone. The dangerous pitfalls here are mostly *integration* pitfalls — adding theming, brand assets, and a gallery to a site that already has live content, an established CSS palette, and Mermaid/Plotly/Leaflet inline scripts in posts.

---

## Critical Pitfalls

### Pitfall 1: Flash of Unstyled Theme (FOUC / FOIT-equivalent for color schemes)

**What goes wrong:**
On hard reload, the site paints in the *default* CSS palette (light) for 50–500 ms before the theme JavaScript runs and swaps the body to dark. Users on dark-mode browsers see a jarring white flash. On slower devices it's worse — sometimes a full second.

**Why it happens:**
The theme-toggle script is loaded as a normal `<script>` near `</body>`, or worse, defer/async. By the time it executes, the browser has already done first paint with `--bg: #FFFCF0`. Even putting the script at the *end* of `<head>` is too late if the stylesheet has already been parsed.

This site is especially exposed because:
- `baseof.html` currently has `<link rel="stylesheet" href=".../style.css">` and no inline theme bootstrap.
- The Flexoki light palette is hardcoded in `:root` (`themes/minimal/static/css/style.css` lines 4–18), so anything except light is a deliberate override that must happen *before* paint.

**How to avoid:**
1. Inline a tiny synchronous script as the **first** child of `<head>` (before `<link rel="stylesheet">`), reading `localStorage` first, then `window.matchMedia('(prefers-color-scheme: dark)')`, then setting `document.documentElement.dataset.theme = 'dark'` (or a class).
2. Drive the palette from a `[data-theme="dark"] :root { --bg: ...; }` override block in CSS, NOT from a JS-applied inline style.
3. Make the inline script byte-budget small (<500 bytes). Do not minify-on-server or load-from-file — it must arrive in the initial HTML response.
4. Add `<meta name="color-scheme" content="light dark">` so the browser uses the correct default for native form controls and scrollbars during the brief pre-script window.

**Warning signs:**
- Visible color flicker on hard refresh in DevTools network throttling (Slow 3G)
- Lighthouse "Avoid non-composited animations" / paint timing complaints
- Users report "the page flashes white when I open it"

**Phase to address:**
Phase 2 (Theme Toggle) — must be implemented in the *first* version of the toggle, never as a follow-up polish item. Adding a toggle without FOUC prevention is technical debt by design.

---

### Pitfall 2: Gallery page weight blowup (shipping 7.5 MB photos as-is)

**What goes wrong:**
The 18 photos in `images/galary/` total ~50 MB unprocessed (verified: largest is `IMG_1646.jpeg` at 7.5 MB, two more above 5 MB, several above 3 MB). If the gallery template renders `<img src="/images/gallery/IMG_1646.jpeg">` directly, every gallery visit downloads the full set. On a 4G connection that's ~30 seconds; on rural mobile, minutes. Lighthouse score collapses.

**Why it happens:**
- `images/galary/` is in the project root, NOT in `assets/` — Hugo's `image.Resize` only works on resources fetched via `resources.Get` from `assets/` or page-bundle `Resources`.
- Putting images under `static/` (or `images/` referenced as static) bypasses Hugo image processing entirely; they ship at original size.
- Easy to forget that `loading="lazy"` is a *latency* optimization, not a *bandwidth* one — a viewport-visible 7.5 MB image still downloads immediately.

**How to avoid:**
1. Move gallery sources to `assets/gallery/` (NOT `static/gallery/` and NOT `images/gallery/` at root).
2. Use `resources.Match "gallery/*"` then `.Resize "800x webp q80"` (or `.Fill` for square thumbnails) to generate processed variants Hugo deduplicates and fingerprints.
3. Generate a thumbnail size (~400 w) for the grid and a larger size (~1600 w) for full view, with `srcset` between them.
4. Strip EXIF aggressively (Hugo's image processor strips most non-orientation EXIF by default in v0.157.0; verify).
5. Set a hard ceiling: gallery page total transfer should be <2 MB on first paint. Run `du -sh public/gallery/` after `hugo --minify` and fail the check above 3 MB.

**Warning signs:**
- `public/images/gallery/` directory sums to >5 MB after build
- Lighthouse "Properly size images" or "Serve images in next-gen formats" warnings
- Network panel showing >2 MB transferred on `/gallery/` page load

**Phase to address:**
Phase 4 (Gallery) — image-processing pipeline must be the *first* commit of that phase, before any layout/CSS work. Layout on un-optimized images creates a fake "it works" signal that hides the real problem.

---

### Pitfall 3: GPS/EXIF metadata leak from personal photos

**What goes wrong:**
Smartphone JPEGs from `images/galary/` carry GPS coordinates accurate to ~5 m, plus device serial, software version, and capture timestamps. Shipping them unprocessed publishes Timo's home address, climbing crag locations, and travel timeline. This is the kind of mistake that ends up on r/privacy.

**Why it happens:**
- "I'll just resize them" — resizing alone doesn't strip EXIF in many tools.
- Hugo's image processing *does* strip most EXIF when re-encoding, but the behavior changed across versions and is configurable via `[imaging.exif]`.
- If anyone bypasses Hugo and copies originals to `static/gallery/` for "convenience," every byte of EXIF ships verbatim.

**How to avoid:**
1. Always route gallery images through Hugo image processing (see Pitfall 2). Re-encoding to WebP/JPEG via Hugo strips the GPS fields by default.
2. Add a build-time sanity check: run `exiftool -GPS:all public/images/gallery/*.{jpg,webp}` after build; expect empty.
3. In `hugo.toml`, explicitly set:
   ```toml
   [imaging.exif]
     disableLatLong = true
     excludeFields = "GPS|Make|Model|Software|Serial.*"
   ```
   (This controls what Hugo *reads*; combined with re-encoding, output files are clean.)
4. Never publish from `static/` — that path bypasses image processing.

**Warning signs:**
- `exiftool` on output files shows `GPSLatitude`, `GPSLongitude`, or device serials
- Original filename patterns (`IMG_xxxx.jpeg`, `DSC09782.JPG`) appear in published URLs — likely means originals shipped untouched
- File size of published image ≈ source file size (re-encoding always changes size meaningfully)

**Phase to address:**
Phase 4 (Gallery) — pair with Pitfall 2. Same image-processing setup solves both. Add `exiftool` check to the milestone's "Definition of Done."

---

### Pitfall 4: Folder rename `images/galary/` → `images/gallery/` produces 404s in already-published URLs

**What goes wrong:**
The current site already deploys with `images/galary/` paths in any place that references them. After the rename, any inbound link, bookmark, RSS attachment, or social-share preview pointing at `tbohnstedt.cloud/images/galary/...` returns 404. GitHub Pages aggressively caches the directory listing too, so even a force-push doesn't immediately resolve.

**Why it happens:**
- Mass rename without a grep audit across `content/`, `themes/`, `hugo.toml`, and any inline Markdown image references.
- Forgetting that the typo may already be in archived RSS feeds, sitemap entries, or third-party caches.
- GitHub Pages 404 handling on a renamed path: the old URL serves a real 404 (not a redirect) until cache TTLs expire.

**How to avoid:**
1. **Before renaming**, grep the entire repo for `galary` (no other word collides with this typo, so a literal grep is safe). Verified at time of writing: zero matches in `content/`, `themes/`, `hugo.toml` — the typo is confined to the directory name itself. This is the rare "safe rename" case.
2. **Still** keep the old folder around as a redirect for at least one deploy cycle. Hugo's alias mechanism (`aliases:` in front matter) doesn't help for raw image paths — instead, add a 1-line `static/images/galary/index.html` with a meta-refresh, or accept that raw image deep-links will break (low risk for this site since photos are new content).
3. Rename in ONE commit with the folder move and any related code changes — never in two steps.
4. After deploy, hit a few old paths with `curl -I` to confirm expected 404 behavior is bounded.

**Warning signs:**
- Grep for `galary` returns hits in `content/` after the rename (forgot something)
- Search Console "Coverage > 404" spike after deploy
- Hugo build warnings about missing resources

**Phase to address:**
Phase 4 (Gallery) — do the rename as the FIRST commit of the gallery phase, in isolation, before adding new gallery code. Easier to revert and easier to reason about.

---

### Pitfall 5: Cumulative Layout Shift (CLS) from images without dimensions

**What goes wrong:**
The gallery grid (and the new About-page inline images, and the header wordmark) render `<img src="...">` with no `width`/`height` attributes. As each image loads asynchronously, the page reflows; the user's scroll position jumps; they mis-tap links. Lighthouse CLS score crashes from <0.1 (good) to >0.25 (poor).

This is the #1 cause of CLS on the web (62% of mobile pages have at least one unsized image per web.dev's 2026 data).

**Why it happens:**
- Markdown image syntax `![](image.jpg)` doesn't emit width/height.
- Default Hugo image render hook also omits them unless explicitly added.
- The existing `.page-content img { max-width: 100%; height: auto; }` rule (CSS line 167–172) tells the browser "compute height from width once loaded" — perfect for *layout sizing*, but useless for *layout-shift prevention* because the browser still doesn't know the aspect ratio until the bytes arrive.

**How to avoid:**
1. Use Hugo image processing (`.Resize`) — the resulting `Resource` has `.Width` and `.Height`, which you emit as HTML attributes.
2. For the gallery: write a partial that always outputs `<img src="..." width="{{ .Width }}" height="{{ .Height }}" loading="lazy" decoding="async">`.
3. For the header wordmark: hard-code the dimensions in the `<img>` tag (the SVG/PNG dimensions are known at build time).
4. For About page inline images: same partial as gallery, or write a Markdown render hook (`layouts/_default/_markup/render-image.html`) that injects dimensions for any `![]()` in any post — gives every existing post the benefit too.
5. Verify with Lighthouse Mobile run; CLS must be <0.1.

**Warning signs:**
- Lighthouse CLS >0.1 on `/gallery/`, `/about/`, or homepage
- Visible reflow on slow connections
- DevTools "Layout shift regions" highlights image areas

**Phase to address:**
Phase 3 (Wordmark) for the header; Phase 4 (Gallery) for the grid; Phase 5 (About) for inline photos. A single Markdown render hook in Phase 3 or 4 covers Phase 5 transitively.

---

### Pitfall 6: Theme toggle accessibility regressions

**What goes wrong:**
The toggle ships as a clickable `<div>` with no role, no `aria-label`, no keyboard handler, and no `aria-pressed`/`aria-checked` state. Screen reader users hear "clickable" with no context. Keyboard-only users can't reach it. Users with `prefers-reduced-motion: reduce` get the fade animation anyway and feel queasy.

**Why it happens:**
- "It's just a button, how hard can it be" — but the toggle has more state than a normal button.
- Mixing up `aria-pressed` (toggle button on/off, on a `<button>`) vs. `aria-checked` (a switch with `role="switch"`). Both work; using neither is the actual bug.
- Forgetting that `prefers-reduced-motion` is a real user setting, not theoretical.

**How to avoid:**
1. Use a real `<button type="button">`, NOT a div or a span.
2. Pick ONE pattern and stick with it:
   - **Toggle button:** `<button aria-pressed="false" aria-label="Switch to dark mode">` — toggle `aria-pressed` between `"true"` and `"false"` and update `aria-label` based on state.
   - **Switch:** `<button role="switch" aria-checked="false" aria-label="Dark mode">` — toggle `aria-checked`.
   - For a binary theme toggle in 2026, `aria-pressed` on a regular `<button>` is the simplest correct choice (W3C APG Switch Pattern is also valid; don't mix them).
3. Wrap any transitions in `@media (prefers-reduced-motion: no-preference) { .theme-toggle { transition: ... } }` — i.e., default to no animation, opt-IN only when the user has not asked for reduced motion.
4. Verify with VoiceOver (macOS), TalkBack (Android), or NVDA (Windows).
5. Tab order: toggle should be reachable in a logical position (suggestion: end of `<nav>` before menu items, or as the last `<header>` child).

**Warning signs:**
- Toggle is a `<div>` or `<span>` in the DOM
- No `aria-pressed` or `aria-checked` attribute mutates on click
- Tab key skips the toggle entirely
- Animation runs even with `Reduce Motion` enabled in System Settings

**Phase to address:**
Phase 2 (Theme Toggle) — the toggle ships accessible from day 1 or it ships broken. There is no "we'll add ARIA later" version that works.

---

### Pitfall 7: Stale `meta theme-color` after toggle

**What goes wrong:**
On mobile Safari and Chrome, the URL bar / status bar color is driven by `<meta name="theme-color">`. Set once to a light value, then the user toggles to dark — the URL bar stays light. Looks broken.

**Why it happens:**
The simplest pattern, two `<meta>` tags with media queries:
```html
<meta name="theme-color" content="#FFFCF0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1C1B1A" media="(prefers-color-scheme: dark)">
```
…works for *system* preference changes but does NOT update when the user manually toggles theme via the in-page button (the media query still reflects OS state).

**How to avoid:**
Two-pronged approach:
1. Ship both `<meta name="theme-color">` tags with media queries (handles users who don't toggle).
2. In the toggle's JS handler, also update a *single* canonical `<meta name="theme-color">` element programmatically:
   ```js
   document.querySelector('meta[name=theme-color][data-managed]').setAttribute('content', isDark ? '#1C1B1A' : '#FFFCF0');
   ```
   Add a `data-managed` attribute to one `<meta>` tag and let the script own it. Keep the media-query tags as the OS-sync fallback.

**Warning signs:**
- iPhone Safari URL bar color desyncs from page background after toggling
- Android Chrome status bar wrong color after toggle
- This bug only shows on real mobile devices, NOT in DevTools mobile emulation

**Phase to address:**
Phase 2 (Theme Toggle) — bundle with the toggle implementation.

---

### Pitfall 8: Logo sprite slicing produces inconsistent dimensions / lossy re-encoding

**What goes wrong:**
The 8 outputs from `images/logos.png` come out at slightly different dimensions (e.g., 256×256, 257×255, 254×258) because the slicing tool used pixel-snapping or floating-point bounding boxes. Or worse — the source PNG is re-saved through a JPEG roundtrip somewhere, dropping transparency on the dark variants. Header wordmark looks one pixel off; favicon edges go fuzzy.

**Why it happens:**
- Manual cropping in Preview / "Export Selection" introduces 1-pixel jitter.
- Many tools default to JPEG when "exporting selected" — silently dropping the alpha channel.
- The source `images/logos.png` (398 KB) is the only authority; if it's not pixel-aligned, every output inherits the misalignment.

**How to avoid:**
1. Inspect `images/logos.png` first: confirm it's a 2-row × 4-column grid with exact integer cell dimensions. If the cells aren't exactly equal, trim the source canvas to be evenly divisible (e.g., 1024×512 → cells of 256×256) BEFORE slicing.
2. Use a deterministic CLI tool for slicing: ImageMagick `convert logos.png -crop 256x256 +repage tile_%d.png` or Python Pillow with explicit integer crop boxes — never manual GUI selection.
3. Always export to PNG (preserves alpha). Only convert to JPEG/WebP for *web delivery*, downstream of the master slice.
4. Run `identify -format "%wx%h\n" *.png` (ImageMagick) on the 8 outputs and verify dimensions match the design intent.
5. Compare visually at 100% zoom — any off-by-one on the crop box ruins the icon.

**Warning signs:**
- Sliced outputs have varying dimensions (`identify` shows different `WxH` per file)
- Dark-variant logos have white halos (alpha was dropped, then PNG re-saved with white background)
- File size is identical for all 8 outputs (suggests the slicer didn't actually crop, just re-saved)

**Phase to address:**
Phase 1 (Brand Asset Slicing) — this is the foundational deliverable; everything downstream (favicon, wordmark, About images that reference the icon) depends on these 8 files being correct.

---

### Pitfall 9: Favicon set incomplete or built for 2014 instead of 2026

**What goes wrong:**
Following an old "complete favicon" tutorial generates 12+ files including `mstile-*.png`, `browserconfig.xml`, `safari-pinned-tab.svg`, and `mask-icon` — most of which were deprecated 5+ years ago. The site ships with bloat, confusing meta tags, and *still* has a missing `apple-touch-icon` because the tutorial linked to one filename and the actual file uses another.

**Why it happens:**
- "Favicon generator" services lag the standard by years.
- Microsoft's `msapplication-*` tags were for Windows 8 live tiles — Windows 11 (2021) removed live tiles entirely.
- Safari's pinned-tab `mask-icon` was deprecated when Safari 12 started accepting regular favicons for pinned tabs.
- Apple Touch Icon is still relevant but the *minimum* set in 2026 is much smaller than older guides suggest.

**How to avoid:**
The 2026 minimum-viable set (per Evil Martians' updated guide and Safari 15.4+ behavior):
- `favicon.ico` (multi-resolution: 16, 32, 48) — for legacy and bookmark UI
- `icon.svg` — modern browsers prefer SVG
- `apple-touch-icon.png` (180×180) — iOS home screen
- `manifest.webmanifest` referencing `192×192` and `512×512` PNGs — Android home screen / PWA install
- `<meta name="theme-color">` tag(s) — already handled in Pitfall 7

Skip:
- `safari-pinned-tab.svg` / `mask-icon` (Safari uses regular favicons since v12)
- `mstile-*.png` / `browserconfig.xml` (Windows live tiles are gone)
- `shortcut icon` link (use `rel="icon"`, the `shortcut` keyword has been non-standard for a decade)

In `baseof.html` `<head>`:
```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
```

**Warning signs:**
- More than 6 favicon-related lines in `<head>`
- Files like `mstile-150x150.png` or `safari-pinned-tab.svg` in `static/`
- `<meta name="msapplication-*">` tags

**Phase to address:**
Phase 1 (Brand Asset Slicing) generates the source PNGs; Phase 3 (Wordmark + Favicon Wiring) installs them into `<head>`. Don't split favicon generation across multiple phases.

---

### Pitfall 10: Header wordmark CLS + double-load of light + dark variants

**What goes wrong:**
Two failure modes that often appear together:
1. The wordmark `<img>` has no `width`/`height` → header reflows when the logo loads → page jumps.
2. The "swap on theme" implementation loads BOTH the light variant and the dark variant (one hidden via `display: none`), wasting bandwidth on every page load and doubling the download for users who only ever see one.

**Why it happens:**
- "Just put both images and toggle CSS visibility" feels simple, but `display: none` doesn't prevent the browser from fetching the `<img src>`.
- Forgetting that the header is on EVERY page — the cost compounds across the site.

**How to avoid:**
1. Render ONE `<img>` element. Use a CSS variable that holds the image URL, swapped per theme:
   ```css
   :root { --wordmark: url('/images/icon/wordmark-light.svg'); }
   [data-theme="dark"] { --wordmark: url('/images/icon/wordmark-dark.svg'); }
   .site-title { background-image: var(--wordmark); /* ...with sized box */ }
   ```
   …OR use a `<picture>` element with `<source media="(prefers-color-scheme: dark)">` — but note this only swaps on OS preference, NOT manual toggle; for manual toggles, CSS background or a single `<img>` whose `src` is set by the theme JS is better.
2. Best for accessibility: keep an `<img>` with a meaningful `alt="Timo Bohnstedt"` (or `alt=""` if it's purely decorative beside accessible site title text), and swap `src` in JS:
   ```js
   wordmarkImg.src = isDark ? '/images/icon/wordmark-dark.svg' : '/images/icon/wordmark-light.svg';
   ```
3. Always set explicit `width` and `height` on the wordmark element (CSS or HTML). The script wordmark dimensions are known at build time — bake them in.
4. Prefer SVG for the wordmark — single file, scales perfectly, smaller than PNG, no need for srcset.

**Warning signs:**
- Network tab shows both `wordmark-light.svg` and `wordmark-dark.svg` downloaded on every page
- Header height jumps after wordmark loads
- Wordmark is blurry on retina displays (means PNG without `srcset` or `2x`)

**Phase to address:**
Phase 3 (Wordmark + Favicon Wiring) — directly tied to header markup changes.

---

### Pitfall 11: Coexistence with existing inline scripts (Mermaid / Plotly / Leaflet) breaks under theme toggle

**What goes wrong:**
After theme toggle ships, blog posts that use Mermaid (climbing-routes post), Plotly charts, and Leaflet maps render with hardcoded light-theme colors against a dark page background. Mermaid diagrams have black text on dark gray. Charts are unreadable. The user toggles theme and these elements DON'T re-render.

**Why it happens:**
- Existing inline scripts (verified in `content/blog/2026-03-05-climbing-routes/index.md`) run once on page load with whatever theme is current and then never react to changes.
- Mermaid has a `theme` option (`default`, `dark`, `forest`, etc.) that defaults to light.
- Plotly accepts `layout.template` for theming but isn't dynamically re-rendered on toggle.
- Leaflet basemap tiles are URL-based; light/dark tile sources differ.

**How to avoid:**
1. Decide explicitly: do existing posts react to theme changes, or do they ship in a fixed theme?
2. **Recommended for v2.0:** Mermaid and Plotly stay theme-agnostic for now (use Flexoki accent colors that read OK on both backgrounds). Document this as a known limitation. Add to backlog: "theme-aware diagrams" as future work.
3. If you DO want theme-reactive diagrams, fire a `theme-change` custom event from the toggle and let each script subscribe — but this expands the toggle's blast radius. Skip in v2.0.
4. At minimum, audit the Mermaid Flexoki theme used in v1.0 — confirm fg/bg colors have AA contrast on BOTH light AND dark site backgrounds.
5. Add a smoke-test page to the milestone: "load `/blog/2026-03-05-climbing-routes/` in dark mode, screenshot, eyeball it."

**Warning signs:**
- Mermaid text invisible against dark page background
- Plotly chart axes/labels invisible
- Leaflet tiles look out of place against dark page chrome
- User reports "the chart broke after I switched themes"

**Phase to address:**
Phase 2 (Theme Toggle) — must be acknowledged and decided BEFORE shipping toggle. Either fix it or document the constraint.

---

## Moderate Pitfalls

### Pitfall 12: localStorage write fails silently in private browsing / quota-exceeded

**What goes wrong:**
Safari Private mode and some embedded browsers throw on `localStorage.setItem()`. Theme persists for the session via in-memory state, but throws an unhandled exception that could break the rest of the toggle handler.

**How to avoid:**
Wrap `localStorage` access in `try/catch`. If write fails, fall back to in-session state only. Don't display an error.

**Phase to address:** Phase 2.

---

### Pitfall 13: About-page inline images use page-bundle-relative paths in a non-bundle page

**What goes wrong:**
`content/about.md` is currently a *single page*, NOT a leaf bundle. Adding `![](my-photo.jpg)` referencing a sibling file fails because there is no sibling — `about.md` lives alone in `content/`. Image either 404s or works only locally.

**How to avoid:**
Convert `content/about.md` to a leaf bundle: rename to `content/about/index.md`, then drop personal photos in `content/about/`. Markdown image syntax then works as page-bundle-relative. Hugo image processing also becomes available.

**Phase to address:** Phase 5 (About Enrichment) — the conversion is the first step of the phase.

---

### Pitfall 14: Theme toggle button placement breaks mobile responsive header

**What goes wrong:**
On mobile (<600px), the existing CSS sets `.site-header { flex-direction: column; gap: 0.5rem; }` (line 261). Adding a theme toggle as a third flex item makes the header three rows tall on mobile, eating up scarce screen real estate.

**How to avoid:**
Place the toggle inside `.site-nav` (the existing nav cluster) so it flows with menu items. Re-run mobile breakpoint tests at 320, 375, 414, 600 px viewports.

**Phase to address:** Phase 2 (Theme Toggle) — coupled with header markup changes.

---

### Pitfall 15: GitHub Pages caches old favicon for weeks

**What goes wrong:**
After deploying new favicons, browsers show the old `favicon.ico` because of aggressive favicon caching (separate from regular cache; Chrome stores it in its own DB). Cache-busting via versioned URLs (`?v=2`) is the standard fix — but GitHub Pages doesn't let you set custom Cache-Control headers.

**How to avoid:**
1. Use unique filenames per version (`icon-v2.svg` instead of `icon.svg?v=2`) so the browser fetches a fresh file. Update `<link rel="icon">` accordingly.
2. Accept that `/favicon.ico` will be cached aggressively — that's fine for the canonical, stable favicon.
3. For the SVG variant (which is more likely to evolve), version the filename.
4. Manually purge browser cache during testing; don't rely on Ctrl+F5 alone (favicons often persist past hard refresh).

**Warning signs:**
- After deploy, your tab still shows the old icon for days
- Lighthouse and web-checker tools show new icon, browser shows old icon

**Phase to address:** Phase 3 (Favicon wiring). Add to commit message: "if updating later, bump filename suffix."

---

### Pitfall 16: Lazy-loading the first gallery image hurts LCP

**What goes wrong:**
Adding `loading="lazy"` to ALL gallery images, including the first row that's above the fold. The first image (likely the LCP candidate) is then lazy-deferred, which delays Largest Contentful Paint.

**How to avoid:**
First row of images: `loading="eager"` and consider `fetchpriority="high"` on the very first one. Below-the-fold: `loading="lazy"`. Hugo template can detect index: `{{ if lt (index .Page.Resources.Match "gallery/*" $i) 3 }}eager{{ else }}lazy{{ end }}`.

**Phase to address:** Phase 4 (Gallery).

---

### Pitfall 17: Image processing fails or stalls on large source files in CI

**What goes wrong:**
`IMG_1646.jpeg` is 7.5 MB. Hugo image processing on a memory-constrained CI runner (GitHub-hosted runners are 7 GB RAM, usually fine) can spike memory while resampling several 5+ MB JPEGs in parallel. Build times balloon from 20s to several minutes on first run; Hugo cache helps subsequent builds.

**How to avoid:**
1. The existing `.github/workflows/deploy.yml` already sets `HUGO_CACHEDIR` to `${{ runner.temp }}/hugo_cache` — verify this is preserved across runs (it usually isn't on `runner.temp`; consider `actions/cache` for `/tmp/hugo_cache` keyed on source hashes).
2. Pre-shrink source files to ≤2000 px wide before adding to repo. The 7.5 MB original buys nothing for an 800-px gallery thumbnail.
3. Time the first build locally before pushing — if `hugo` takes >2 min on M-series Mac, CI will be worse.

**Phase to address:** Phase 4 (Gallery) — verify CI build time after the gallery ships.

---

## Minor Pitfalls

### Pitfall 18: Site title accessibility regression after wordmark replaces text

**What goes wrong:**
Replacing the text "Timo Bohnstedt" with an `<img>` removes a textual h1/heading link. Screen readers and SEO crawlers lose the site name signal.

**How to avoid:**
Keep an accessible name: `<a href="/"><img src="..." alt="Timo Bohnstedt"></a>`. The `alt` IS the site name to assistive tech.

**Phase to address:** Phase 3 (Wordmark).

---

### Pitfall 19: Theme toggle icon swap causes jitter

**What goes wrong:**
Sun icon for light, moon icon for dark. If the two icons aren't the same dimensions, the button width changes when theme changes → minor layout shift in header.

**How to avoid:**
Use ONE icon container with fixed `width` and `height`. Swap inner SVG paths only, not the outer dimensions. Or use a single SVG with two paths and toggle visibility internally.

**Phase to address:** Phase 2.

---

### Pitfall 20: `prefers-color-scheme` misread when no explicit choice exists

**What goes wrong:**
The "preference cascade" logic checks `localStorage` first, then `prefers-color-scheme`. If localStorage has a stale `'auto'` or empty string value (from an aborted earlier impl), the logic short-circuits and ignores OS preference.

**How to avoid:**
Treat ONLY `'dark'` and `'light'` as explicit user choices. Everything else (null, undefined, `''`, `'auto'`) falls through to `matchMedia('(prefers-color-scheme: dark)')`. Reset stale values defensively.

**Phase to address:** Phase 2.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Ship gallery images from `static/` instead of `assets/` | Skip Hugo image processing setup; "just works" today | EXIF leak, 50 MB page weight, no responsive sizes, no WebP | Never — image processing is the whole point of using Hugo Extended |
| Toggle script at end of `<body>` instead of inline `<head>` | Easier to test, simpler code split | Permanent FOUC visible to every visitor | Never for this milestone — FOUC is a launch-blocking bug |
| Two `<img>` tags for light/dark wordmark | Trivial to implement | Doubles header asset weight on every page | Acceptable in MVP if wordmark is <5 KB each AND lazy-load the inactive one (but easier to use CSS variable) |
| Skip the rename of `galary` → `gallery` | Avoid potential 404 risk | Typo ships in URLs forever; mortifying when noticed | Never — fix the typo before any URL is published externally |
| Don't strip EXIF (rely on file size reduction "probably" stripping it) | Save 5 minutes of config | GPS coordinates leak, real privacy harm | Never |
| Skip the favicon manifest.json | "Browsers will use favicon.ico anyway" | Android home-screen shortcut shows generic icon, PWA install broken | Acceptable if PWA is explicitly out of scope AND only desktop users matter — neither is true here |
| Hardcode dark-mode colors in CSS without `[data-theme="dark"]` selector, just media query | Simpler CSS | User can't manually override OS preference; toggle is purely cosmetic | Acceptable IF the toggle is dropped from scope, but then "manual toggle" requirement isn't met |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Hugo image processing + GitHub Actions | Forgetting to cache `resources/_gen/` between runs → builds re-process every image every time | Add `actions/cache` keyed on hash of source images, or accept long first-build times after asset changes |
| Existing CSS palette + new dark mode | Defining all dark-mode colors via `@media (prefers-color-scheme: dark)` only, then trying to add a manual toggle | Drive ALL palette via CSS variables on `:root` and `[data-theme="dark"]`; let the JS toggle set the attribute; media query is a fallback for first-load before localStorage check |
| Hugo unsafe HTML (already enabled) + theme toggle script | Putting the toggle script inside a content file as raw HTML | Keep the toggle in `themes/minimal/layouts/partials/header.html`, not in content. Site-wide concerns belong in templates. |
| Mermaid in existing posts + dark theme | Diagrams use `mermaid.initialize({ theme: 'default' })` set at script start, never re-runs | Either ship Mermaid in a single Flexoki-neutral theme (current approach) and accept that diagrams don't toggle, OR fire a custom event and re-init Mermaid (out of scope for v2.0) |
| Page bundle paths + non-bundle pages | About page is `content/about.md` (single), not `content/about/index.md` (leaf bundle) — page-bundle-relative image paths fail | Convert About to a leaf bundle before adding images; this ALSO unlocks Hugo image processing for About images |
| Plotly + dark mode | Charts hardcoded with light backgrounds | Out of scope for v2.0; document as known limitation |
| GitHub Pages + custom Cache-Control | Trying to set Cache-Control via meta tags (no effect) or expecting `_headers` files (Cloudflare Pages, not GitHub Pages) | Use versioned filenames for cache busting; `meta http-equiv="Cache-Control"` is mostly ignored |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Unprocessed gallery images shipped | LCP >4s, 50 MB transfer, Lighthouse score <40 | Hugo image processing pipeline (Pitfall 2) | Immediately on first gallery visit on mobile |
| Header wordmark fetched on every page without HTTP cache headers | High repeat-visit weight | SVG wordmark inline in template (zero requests) OR rely on default GitHub Pages caching | Affects repeat visitors on slow connections |
| Both light + dark wordmark fetched | Double header asset weight | Single `<img>` whose `src` is JS-managed, OR CSS background-image with custom-property URL | Every page load, every visitor |
| Theme toggle re-renders entire `<body>` content | Visible repaint flash on toggle | CSS variable swap only — never re-render DOM | On toggle (instant for users) |
| Lazy-loaded LCP image | Delayed first contentful paint | First gallery image: `loading="eager"`, `fetchpriority="high"` | Gallery page only |
| No `srcset` on gallery thumbnails | 4× over-fetching on retina mobile | Hugo `image.Resize` at multiple widths + `srcset` | Mobile retina users (most users) |
| Image-processing cache lost between CI runs | 5-minute builds become normal | `actions/cache` for `resources/_gen/` keyed on source hash | Every CI run after asset changes |

---

## Security / Privacy Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| GPS EXIF leaks home address via gallery photos | Real-world stalking risk; cannot be undone once published | Always re-encode through Hugo image processing (strips most EXIF), verify with `exiftool` post-build |
| Device serial / capture timestamps leak personal usage patterns | Lower-severity privacy: reveals device upgrade timeline, daily routine | Same as above — Hugo re-encoding strips by default; explicit `[imaging.exif]` config to be thorough |
| Original filenames leak (`IMG_xxxx`, `DSC09782`) | Minor — reveals camera, sometimes shot order | Rename via Hugo (image processing produces hashed/processed filenames in `public/images/`) or rename manually before ingestion |
| Toggle script reading from external CDN | Supply-chain risk; adds blocking dependency before paint | Inline the toggle script directly in `baseof.html` (small enough — <500 bytes) |
| Manifest.webmanifest exposes internal site structure | Negligible for personal site | None needed |
| Allowing `unsafe = true` in Goldmark (already enabled) | Already accepted risk for embeds (Instagram, Plotly, Leaflet) | No new risk introduced by this milestone |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Toggle has no visual indication of current state | User clicks blindly to test what theme is active | Sun/moon icon that always shows the *target* state ("Switch to dark") OR fixed icon with `aria-pressed` reflecting state |
| Theme toggles instantly with no transition vs. transitions on initial load | Initial load animates from light → dark, looks broken | Set transitions only AFTER a user-triggered toggle (set `data-theme-loaded` on body after first paint, scope `transition` to `[data-theme-loaded]`) |
| Gallery has no captions / context | "Why am I looking at these photos?" | Lightweight caption per image (alt-derived OK), or a small intro paragraph on `/gallery/` |
| Gallery clicking image goes to full-resolution monster file | Mobile user opens 5 MB image → page hangs | Click → larger processed image (max ~1600 px), not the source |
| Theme toggle is too small / no hover affordance | Hard to find / hard to tap on mobile | Min 44×44 px tap target (WCAG 2.2 AA), visible focus ring, hover state |
| About page photos break out of 640px max-width | Layout looks awkward on wide displays | Inherit `.page-content img { max-width: 100% }` rule (already in CSS line 167) — verify it applies to About |
| Header wordmark too tall, eats vertical space | Less content above the fold | Constrain to ~32 px height baseline; design wordmark accordingly |

---

## "Looks Done But Isn't" Checklist

- [ ] **Theme toggle:** Often missing inline `<head>` script — verify hard-reload in dark mode produces zero light-flash (record screen, look frame-by-frame)
- [ ] **Theme toggle:** Often missing `aria-pressed` mutation — verify with screen reader, click toggle, listen for state announcement
- [ ] **Theme toggle:** Often missing `prefers-reduced-motion` respect — verify with macOS "Reduce motion" enabled, no animation on toggle
- [ ] **Theme toggle:** Often missing meta theme-color update — verify on real iPhone/Android, not emulator
- [ ] **Theme toggle:** Often missing localStorage persistence test — verify reload preserves manual choice over OS preference
- [ ] **Logo sprite:** Often missing dimension consistency — verify all 8 outputs have identical dimensions (or intended ratios) via `identify`
- [ ] **Logo sprite:** Often missing alpha preservation — verify dark-variant logos have transparent backgrounds (open in image viewer with checkered backdrop)
- [ ] **Favicon set:** Often missing apple-touch-icon — verify on iOS by adding site to home screen, see if icon appears
- [ ] **Favicon set:** Often missing manifest.webmanifest icons — verify Android Chrome "Add to Home Screen" preview
- [ ] **Favicon set:** Often missing post-deploy verification — verify with realfavicongenerator.net checker against live URL
- [ ] **Header wordmark:** Often missing width/height — verify CLS <0.1 in Lighthouse mobile run
- [ ] **Header wordmark:** Often missing alt text — verify with screen reader announces site name
- [ ] **Gallery:** Often missing image processing — verify processed file sizes (each <300 KB for thumbnails)
- [ ] **Gallery:** Often missing EXIF stripping — verify `exiftool public/images/gallery/*.{jpg,webp}` shows no GPS or device fields
- [ ] **Gallery:** Often missing srcset — verify `srcset` attribute present in DOM, multiple sizes generated in `public/`
- [ ] **Gallery:** Often missing CLS prevention — verify `width` and `height` attributes on every gallery `<img>`
- [ ] **Gallery:** Often missing eager-load on LCP image — verify Lighthouse LCP <2.5s
- [ ] **About page:** Often missing leaf-bundle conversion — verify `content/about/index.md` exists, not `content/about.md`
- [ ] **Folder rename:** Often missing grep audit — verify zero `galary` matches in repo after rename
- [ ] **Folder rename:** Often missing Hugo image-processing path update — verify gallery still builds after rename
- [ ] **Existing diagrams:** Often missing dark-mode contrast check — verify all Mermaid/Plotly content readable in dark mode

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| GPS EXIF leaked publicly | HIGH | 1) Immediate: redeploy with stripped images; 2) Force-purge any CDN/proxy caches; 3) Accept that the data may have been scraped — old links may be archived in Wayback/Google cache; 4) Going forward: never bypass image processing |
| FOUC ships to production | LOW | Add inline `<head>` script in next deploy; lasts one push cycle. Embarrassing but reversible. |
| Favicon caches stuck on old icon | MEDIUM (time, not effort) | 1) Bump filename suffix (icon-v2.svg) and update links; 2) Wait 1–2 weeks for browser favicon caches to expire on returning users; 3) Update `<link>` for `apple-touch-icon` similarly. New visitors see new icon immediately. |
| Gallery page weight ballooned (50 MB) post-launch | LOW | Roll back the gallery commit; rework with image processing; redeploy. Site outage limited to gallery page. |
| Folder rename broke published image URLs | LOW–MEDIUM | Restore old folder name OR add static-redirect HTML; minor SEO/social-preview damage but recoverable |
| Theme toggle inaccessible (no ARIA, no keyboard) | LOW | Single follow-up commit; compatibility-clean fix |
| Logo dimensions inconsistent | LOW (if caught before favicon wiring) — MEDIUM (if downstream files already published) | Re-slice with deterministic tool, regenerate favicon set, push new versioned filenames |
| Mermaid/Plotly diagrams unreadable in dark mode | LOW | Two options: 1) document as known limitation, 2) post-launch follow-up to add theme-aware re-init. Existing posts still render — just imperfectly. |

---

## Pitfall-to-Phase Mapping

Suggested phase structure for the roadmapper. Phases are ordered by dependency: brand assets first, then theme infrastructure, then header/favicon wiring, then gallery, then about-page polish.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. FOUC on theme load | Phase 2 (Theme Toggle) | Hard reload in dark mode; screen-record; check for any light-paint frame |
| 2. Gallery page weight | Phase 4 (Gallery) | `du -sh public/gallery/` <3 MB; Lighthouse "Properly size images" passes |
| 3. EXIF/GPS leak | Phase 4 (Gallery) | `exiftool public/images/gallery/*` shows no GPS or device fields |
| 4. Folder rename 404s | Phase 4 (Gallery) — first commit of phase | Grep `galary` returns zero matches in repo; Hugo build succeeds |
| 5. CLS from unsized images | Phase 3 (header), 4 (gallery), 5 (about) | Lighthouse CLS <0.1 on each affected page |
| 6. Theme toggle accessibility | Phase 2 (Theme Toggle) | Screen reader announces state on toggle; keyboard tab reaches toggle; reduced-motion respected |
| 7. Stale meta theme-color | Phase 2 (Theme Toggle) | Mobile Safari URL bar updates color on toggle (real device test) |
| 8. Logo slicing inconsistency | Phase 1 (Brand Asset Slicing) | `identify` confirms all 8 outputs have consistent dimensions |
| 9. Outdated favicon set | Phase 3 (Wordmark + Favicon) | realfavicongenerator.net audit passes; <6 favicon `<link>` tags in head |
| 10. Wordmark CLS + double-load | Phase 3 (Wordmark) | Network panel shows ONE wordmark file per page; Lighthouse CLS <0.1 |
| 11. Existing diagrams in dark mode | Phase 2 (Theme Toggle) | Document decision in milestone notes; visual check on `/blog/2026-03-05-climbing-routes/` |
| 12. localStorage failure handling | Phase 2 (Theme Toggle) | Try-catch wrapping verified by code review |
| 13. About page leaf-bundle conversion | Phase 5 (About Enrichment) — first commit | `content/about/index.md` exists; About images render |
| 14. Mobile header layout regression | Phase 2 (Theme Toggle) | Manual mobile-viewport test at 320, 375, 414 px |
| 15. GitHub Pages favicon caching | Phase 3 (Favicon wiring) | Versioned filename strategy documented in commit |
| 16. Gallery LCP regression | Phase 4 (Gallery) | First image `loading="eager"`; Lighthouse LCP <2.5s |
| 17. CI build time blowup | Phase 4 (Gallery) | GitHub Actions build <3 min; cache hit on resources |
| 18. Site title accessibility regression | Phase 3 (Wordmark) | Screen reader announces "Timo Bohnstedt" via wordmark `alt` |
| 19. Toggle icon swap jitter | Phase 2 (Theme Toggle) | Visual: no header width change on toggle |
| 20. `prefers-color-scheme` misread | Phase 2 (Theme Toggle) | Logic explicitly handles only `'dark'`/`'light'` from localStorage |

---

## Suggested Phase Ordering Rationale

Based on dependency analysis of the pitfalls above:

1. **Phase 1 — Brand Asset Slicing** must come first. Pitfall 8 (slicing) and Pitfall 9 (favicon set) both depend on having the 8 sliced files as deterministic source-of-truth. Theme toggle (Phase 2) and Wordmark (Phase 3) consume these outputs.
2. **Phase 2 — Theme Toggle** is the highest-risk phase (10 of 20 pitfalls cluster here). Doing it second means the wordmark in Phase 3 already has a working theme system to swap against — no chicken-and-egg.
3. **Phase 3 — Wordmark + Favicon Wiring** combines header swap with favicon wiring because they share the same `<head>`/header partial edits and the same brand-asset inputs.
4. **Phase 4 — Gallery** is the highest-bandwidth phase (Pitfalls 2, 3, 4, 5, 16, 17 all live here). Folder rename is the FIRST commit; image-processing pipeline is the SECOND. Layout last.
5. **Phase 5 — About Enrichment** is last because it depends on (a) the leaf-bundle conversion pattern proven in Phase 4, and (b) the Markdown render-image hook (if introduced in Phase 4) covers About transitively.

---

## Sources

**Hugo image processing & EXIF:**
- [Hugo Image Processing — Official Docs](https://gohugo.io/content-management/image-processing/) (HIGH confidence — official, current)
- [Hugo Imaging Configuration](https://gohugo.io/configuration/imaging/) (HIGH)
- [Hugo discourse: Strip EXIF data on build](https://discourse.gohugo.io/t/option-to-strip-exif-data-from-images-upon-build/28441) (MEDIUM)
- [Hugo Issue #5578: EXIF orientation handling](https://github.com/gohugoio/hugo/issues/5578) (MEDIUM)

**Theme toggle / FOUC / accessibility:**
- [Best light/dark mode toggle in JS — whitep4nth3r](https://whitep4nth3r.com/blog/best-light-dark-mode-theme-toggle-javascript/) (MEDIUM)
- [Flashless Dark Mode — vbesse.com](https://www.vbesse.com/en/blog/flashless-dark-mode/) (MEDIUM)
- [Dark Mode in CSS Guide — CSS-Tricks](https://css-tricks.com/a-complete-guide-to-dark-mode-on-the-web/) (MEDIUM)
- [MDN: aria-pressed attribute](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-pressed) (HIGH)
- [W3C APG: Switch Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/switch/) (HIGH)
- [MDN: meta theme-color](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/theme-color) (HIGH)
- [web.dev: Improve dark mode default with color-scheme and meta tag](https://web.dev/articles/color-scheme) (HIGH)

**Favicon set 2026:**
- [Evil Martians — How to Favicon in 2026](https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs) (HIGH — authoritative practitioner reference, regularly updated)
- [Lighthouse Issue #14064: Safari 15.4 manifest icons](https://github.com/GoogleChrome/lighthouse/issues/14064) (HIGH)

**CLS & responsive images:**
- [web.dev: Optimize Cumulative Layout Shift](https://web.dev/articles/optimize-cls) (HIGH — Google official)
- [Hugo discourse: image processing and responsive images](https://discourse.gohugo.io/t/hugo-image-processing-and-responsive-images/43110) (MEDIUM)
- [Bryce Wray: Responsive and optimized images with Hugo](https://www.brycewray.com/posts/2022/06/responsive-optimized-images-hugo/) (MEDIUM — Hugo-specific practitioner reference)

**Hugo page bundles:**
- [Hugo Page Resources — Regis Philibert](https://www.regisphilibert.com/blog/2018/01/hugo-page-resources-and-how-to-use-them/) (MEDIUM — older but accurate)
- [Hugo discourse: Page Bundle relative image paths](https://discourse.gohugo.io/t/page-bundle-relative-image-path-in-rss-feed-wrong/27050) (MEDIUM)

**GitHub Pages caching:**
- [GitHub community: Favicon not updating](https://github.com/orgs/community/discussions/44369) (MEDIUM)
- [GitHub community: Caching assets in GitHub Pages](https://github.com/orgs/community/discussions/11884) (MEDIUM)

**Repo-specific verification (HIGH — direct file inspection):**
- `themes/minimal/static/css/style.css` (current Flexoki light palette)
- `themes/minimal/layouts/_default/baseof.html` (current `<head>` markup)
- `themes/minimal/layouts/partials/header.html` (current header markup)
- `images/galary/` (verified file sizes 152 KB → 7.5 MB)
- `hugo.toml` (current Hugo config; no `[imaging]` section yet)

---
*Pitfalls research for: Hugo personal blog v2.0 Brand & Gallery milestone*
*Researched: 2026-04-28*

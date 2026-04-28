# Feature Research

**Domain:** Personal Hugo blog — brand identity (logo, theming) + photo gallery + richer About page
**Researched:** 2026-04-28
**Confidence:** HIGH (all six target features map to well-established 2026 patterns on personal/static sites)

## Scope

This file scopes the **NEW** v2.0 features only. Existing capabilities (Hugo blog, page bundles, footer social cluster, Mermaid shortcode, single-stylesheet Flexoki light palette, About page text scaffold) are taken as given. The site's aesthetic constraint — **minimal Flexoki, vanilla JS only, no frameworks** — drives every recommendation below: when a "personal blog" pattern and an "enterprise SaaS" pattern diverge, we recommend the personal-blog one.

The six target features are:
1. Light/dark theme toggle in header
2. Logo sprite sliced into 8 individual assets
3. Branded header wordmark (replaces text title, swaps with theme)
4. Browser favicon set wired into `<head>`
5. Standalone `/gallery/` page with 18 photos
6. About page enriched with inline personal photos

## Feature Landscape

### Table Stakes (Users Expect These)

If the site claims "dark mode" or "branded", users penalize the absence of these. They are the bar to clear.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **No-flash theme on first paint** | A theme that flickers on every page load looks broken. The 2026 canonical pattern is an inline `<head>` script that reads `localStorage` then falls back to `prefers-color-scheme`, sets a `data-theme` attribute on `<html>` *before* CSS parses. | M | Inline in `baseof.html` `<head>` *before* the stylesheet link. Set `<html data-theme="dark|light">` synchronously. Use a `class="dark"` or `data-theme` attribute swap rather than `<picture>` media queries — only attribute swap respects the manual toggle. |
| **OS preference detection (default)** | Visitor with system dark mode expects the site to honor it on first visit, with no explicit interaction. | S | `window.matchMedia('(prefers-color-scheme: dark)')` inside the inline init script. Gate behind the localStorage check (manual choice wins). |
| **Persistence across pages and sessions** | Once the user toggles, every page on every visit should remember. | S | `localStorage.setItem('theme', 'dark')`. Read on every page load. Wrap in `try/catch` for private-browsing failures. |
| **CSS variables for theme tokens** | Industry standard in 2026 — single source of color truth, swappable by attribute selector. | S | `:root { --bg: ...; --fg: ...; }` and `[data-theme="dark"] { --bg: ...; }`. Every existing Flexoki color reference in `style.css` becomes a `var(--*)` lookup. |
| **`color-scheme` CSS + meta tag** | Tells the browser to render native UI (form controls, scrollbars) in matching mode and prevents white scrollbar flash. | S | `<meta name="color-scheme" content="light dark">` in `<head>`, plus `:root { color-scheme: light; }` and `[data-theme="dark"] { color-scheme: dark; }` in CSS. |
| **Toggle button in header (right side)** | Convention on every personal blog with theming — same place every time, next to nav. | S | Add to `partials/header.html` after `.site-nav` or as its last item. Single icon button, no labelled switch widget. |
| **Sun/moon icon swap** | The universally-understood theme toggle iconography. Inline SVG, current-color stroke. | S | Two SVGs, one shown per state via CSS (`[data-theme="dark"] .icon-sun { display: none; }`). Inline so they inherit `currentColor` and theme correctly. |
| **`aria-label` + keyboard reachable** | Accessibility floor for any icon-only button. | S | `<button type="button" aria-label="Switch to dark theme" aria-pressed="false">`. Update `aria-pressed` on toggle. Native `<button>` is keyboard-reachable for free. |
| **`prefers-reduced-motion` honored** | Listed as a constraint in PROJECT.md and a 2026 a11y baseline. | S | Wrap any `transition` rules in `@media (prefers-reduced-motion: no-preference)`. |
| **Logo asset slicing (8 files)** | The sprite is unusable as-is for `<img>` tags. Each variant (logo / icon / minimum / favicon × dark / light) needs its own file. | S | Manual slice to PNG once; export SVG if available. Place in `static/images/brand/` (or `themes/minimal/static/`). 8 files total per PROJECT.md. |
| **Wordmark in header swaps per theme** | If the brand only renders correctly in one theme, theming is half-broken. | S | Two approaches — recommend **attribute-driven CSS swap** so it works with the manual toggle (see Pitfalls/Architecture). |
| **Favicon — 16/32 PNG + 180 Apple touch + 192/512 manifest + ICO fallback** | The 2026 baseline matrix per evilmartians and faviconstudio. | S | Six files. `favicon.ico` (multi-size 16/32/48), `favicon-16.png`, `favicon-32.png`, `apple-touch-icon.png` (180), `icon-192.png`, `icon-512.png`. Optionally an SVG with embedded `prefers-color-scheme` media query for dark-aware tab icon (Chrome/Firefox/Edge only). |
| **Favicon `<link>` tags in `<head>`** | Without these, browsers fall back to `/favicon.ico` only and miss the high-DPI / mobile sizes. | S | Six `<link rel="...">` tags in `baseof.html` `<head>`. Add `<link rel="manifest" href="/site.webmanifest">` for PWA install on Android. |
| **Gallery in main nav** | A page nobody can find isn't a feature. | XS | Add to `[[menu.main]]` in `hugo.toml`. |
| **Uniform photo grid (CSS Grid)** | The minimal-aesthetic default. Personal photographers' sites in 2026 overwhelmingly use uniform grids over masonry; masonry implies a portfolio with curation, uniform implies a journal. Fits Flexoki. | S | `display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px;`. Square or 4:3 thumbnails via `aspect-ratio` + `object-fit: cover`. |
| **Lazy-loaded thumbnails** | 18 photos × ~1 MB raw = 18 MB. Native `loading="lazy"` ships in every major browser since 2020. | S | `<img loading="lazy" decoding="async" width="..." height="...">`. **Always** set width/height to prevent CLS. |
| **Web-optimized photos (resize + compress)** | 7.5 MB source images on a personal blog kill mobile data and Lighthouse. Hugo Extended has built-in image processing. | M | Hugo: `{{ $thumb := $img.Resize "640x webp q82" }}` + a larger `1280x` version for `srcset`. Generates responsive sizes at build. |
| **`srcset` + `sizes` for responsive thumbnails** | Same image at 320/640/1280 served per-viewport. Standard 2026 pattern. | M | `<img srcset="thumb-320.webp 320w, thumb-640.webp 640w, thumb-1280.webp 1280w" sizes="(max-width: 600px) 100vw, 33vw">`. Hugo loop builds this. |
| **Inline photos in About page** | Without photos, "richer About" is just text. | XS | Goldmark `unsafe = true` is already on. Use plain Markdown image syntax with relative paths — convert About to a page bundle so images co-locate. |
| **About page becomes a page bundle** | Required to co-locate inline photos with content (matches existing blog post convention). | S | Move `content/about.md` → `content/about/index.md`, add `images/` folder beside it. Hugo URL stays `/about/`. |

### Differentiators (Nice-to-have, Aligned with Core Value)

These add polish without bloating the build. Every one of them stays inside the "minimal Flexoki, vanilla JS only" rails.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Theme toggle CSS view-transition / cross-fade** | A 150 ms color cross-fade on toggle feels deliberate, not jarring. Native `view-transition-name` is supported in Chrome/Edge/Safari 18+ in 2026. Falls back gracefully (no transition) elsewhere. | S | `@view-transition { navigation: none; }` + a JS-triggered transition on `<html>`. Gate behind `prefers-reduced-motion: no-preference`. |
| **Theme-aware inline SVG wordmark** | Instead of swapping two PNGs, ship one SVG wordmark with `fill="currentColor"` and let CSS color it. One asset, infinite themes, perfect on retina. | S | Requires SVG export of wordmark. If only PNG is available, fall back to the two-PNG attribute swap. Recommend asking the designer/keeping the SVG if it exists. |
| **`<link rel="icon" type="image/svg+xml">` with embedded dark-mode media query** | One SVG favicon that adapts to the OS theme in Chrome/Firefox/Edge tabs. Fallback PNGs cover Safari and legacy. | S | SVG must contain `<style>@media (prefers-color-scheme: dark) { .fg { fill: #ECE2D0; } }</style>`. List SVG first, then PNG fallback for Safari. |
| **Gallery captions on hover/focus** | Optional one-line caption per photo (location, date) adds context without cluttering the grid. | S | `<figure><img><figcaption>` with caption visible on hover/focus + always visible on touch. Pure CSS. Skip for the v2.0 launch — add later if photos justify it. |
| **Gallery click-to-zoom (lightbox)** | Lets visitors actually see a photo at full size. **Native HTML `<dialog>` element + a few lines of vanilla JS** delivers a lightbox without any library — no PhotoSwipe, no Lightbox2, no jQuery. Aligns with "no JS framework" constraint. | M | `<dialog>` + JS `dialog.showModal()` on thumbnail click; ESC closes it natively. Skip prev/next arrows in v2 (defer to v3 if requested). |
| **Photo metadata hidden (no EXIF leak)** | EXIF can include GPS coordinates and camera serials. Strip on export to protect privacy. | S | `exiftool -all= image.jpg` once during the optimization step. Document in PITFALLS. |
| **Gallery ordering: chronological reverse or curated** | Defines what the gallery *says*. Reverse-chronological reads as a journal; curated reads as a portfolio. Recommend chronological-reverse using EXIF date or filename prefix. | S | Hugo can read `Lastmod`/`Date` from front matter or sort by name. Frontmatter on each photo bundle = simplest. |
| **About page side-by-side photo + text on desktop** | A small portrait next to the opening paragraph adds personality without dominating. Stacks vertically on mobile. | S | CSS Grid 2-column at `>= 700px`, single column below. One photo only — keep About lean. Inline photos elsewhere are full-width breaks. |
| **Theme toggle remembers across tabs (storage event)** | Toggle in one tab updates open tabs. Tiny touch, low cost. | XS | `window.addEventListener('storage', e => { if (e.key === 'theme') applyTheme(e.newValue); })`. |
| **Manifest file for installable PWA-lite** | If the favicons exist anyway, a 10-line `site.webmanifest` makes the site installable on Android home screens. Aligns with "personal site" identity. | S | `{ "name": "Timo Bohnstedt", "icons": [{src:..., sizes:"192x192"}, ...], "theme_color": "#...", "background_color": "#..." }`. |

### Anti-Features (Tempting, Skip Them)

These get suggested constantly for sites like this — but each one breaks the minimal Flexoki / no-framework / no-flash invariants.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Three-state toggle (light / dark / auto)** | "Respects user choice better." | Triples the UI state, adds a third icon, makes the toggle ambiguous. The two-state + OS-preference-as-default pattern already covers "auto" semantically. | Two-state toggle. Provide a small "Reset to system" link in settings/footer **only if** users actually request it later. v2 ships two-state. |
| **`<picture>` + `prefers-color-scheme` for the wordmark** | Native, no JS. | **Breaks the manual toggle.** `<picture>` only listens to OS preference, not the `data-theme` attribute. A user who manually picked dark on a light-OS system would still see the dark-on-light wordmark. | Class/attribute-driven CSS swap with two `<img>` tags (or one inline SVG with `currentColor`). Documented in Pitfalls. |
| **PhotoSwipe / Lightbox2 / Fancybox / GLightbox** | "Industry-standard galleries use them." | Each ships 30–80 KB of JS + CSS for a feature that native `<dialog>` does in 30 lines. Conflicts with "no JS framework, keep it minimal." | Native `<dialog>`-based lightbox if zoom is wanted, otherwise plain `<a href="full.jpg">` links that open the full image. |
| **Masonry / Pinterest-style gallery** | Visually impressive. | Requires JS layout (or fragile CSS-only hacks), CLS issues, and reads as "portfolio" rather than "journal." Doesn't fit minimal Flexoki. | Uniform CSS Grid with consistent aspect ratio (`aspect-ratio: 4/3` + `object-fit: cover`). |
| **Infinite scroll on the gallery** | "Modern feel." | 18 photos. There's no scroll problem to solve. Infinite scroll breaks the footer, breaks deep-linking, breaks back-button. | Single page, 18 thumbnails, done. If the count grows past ~60, add pagination — not infinite scroll. |
| **Gallery filter/tags/categories** | "Organize photos." | 18 photos doesn't need taxonomy. Filtering UI is more interface than content. | Single chronological grid. Add tags if/when count exceeds 50. |
| **A custom dark-mode-only `theme-color` meta dance** | "Match address bar to the theme." | Browsers honor `<meta name="theme-color" media="(prefers-color-scheme: dark)" content="...">` only against OS preference, not the manual toggle — same trap as `<picture>`. With a manual toggle, the address bar can't be made authoritative without JS swapping the meta tag. | Either ship two static `theme-color` meta tags (OS-bound) and accept the address bar lags the manual toggle, or skip `theme-color` entirely. Recommend skip — keeps the head clean. |
| **Animated theme transition on every element (background, color, border)** | Looks slick on demo videos. | `transition: all 0.3s` causes janky paint storms on every theme toggle and complicates `prefers-reduced-motion` handling. | Transition `background-color` and `color` only on `body`, `0.15s`. Or no transition at all — instant swap is also valid. |
| **Auto-detect dark mode in the toggle button icon (show sun in light mode meaning "switch to dark")** | Common, but ambiguous. | Half of users think the icon represents the *current* state, half think it represents the *target* state. Both interpretations exist in the wild. | Pick one convention (recommend: icon shows the **target** state — a moon when in light mode means "click to go dark") and document with `aria-label="Switch to dark mode"`. |
| **Lazy-loading the LCP image** | "Lazy everything!" | The largest contentful paint image must load eagerly or it hurts Core Web Vitals. On the gallery, the *first row* of thumbnails is in the viewport on most screens. | `loading="lazy"` only on images below the fold. First 3–6 thumbnails: `loading="eager" fetchpriority="high"` for the very first one. |
| **Custom font for the wordmark via `@font-face`** | "Match the script logo elsewhere on the site." | Loading a script font for one wordmark = +50–150 KB and a FOIT/FOUT problem. The wordmark is already a designed image asset. | Render the wordmark as an SVG/PNG (it already exists). Don't re-render the script font in HTML. |

## Feature Dependencies

```
[CSS variables refactor]
    └──required by──> [Theme toggle]
                          ├──required by──> [Wordmark per-theme swap]
                          └──required by──> [Theme-aware code blocks/Mermaid]

[Logo sprite slice → 8 assets]
    ├──required by──> [Wordmark in header]
    └──required by──> [Favicon set]

[Favicon set assets exist]
    └──required by──> [Favicon <link> tags in <head>]
                          └──enhances──> [Optional webmanifest]

[Hugo image processing pipeline]
    └──required by──> [Optimized gallery thumbnails]
                          └──required by──> [Gallery page]

[About page → page bundle]
    └──required by──> [About inline photos]

[Renamed images/galary/ → images/gallery/]
    └──required by──> [Gallery page]
```

### Dependency Notes

- **CSS-variables refactor unblocks every theming feature.** The current `style.css` uses literal Flexoki hex values. Every one becomes a `var(--*)` lookup before the toggle can do anything useful. This is the single largest piece of work in the milestone.
- **Logo slicing unblocks both wordmark and favicons.** Both consume the same source sprite. Slicing is cheap (one-time manual or scripted ImageMagick), but everything downstream waits on it.
- **The toggle and the wordmark swap share an attribute.** Both react to `<html data-theme="...">`. Implementing the toggle first means the wordmark swap is "free" (just two CSS rules).
- **Hugo image processing is independent** of the theming work. Gallery and theme can ship in parallel phases.
- **About-page-as-bundle is a 30-second migration** but every inline image depends on it. Do this first if the About work is touched at all.
- **No conflicts** between the six features — they compose cleanly.

## MVP Definition

### Launch With (v2.0)

These six are the milestone scope per PROJECT.md. All are P1.

- [ ] **CSS variables theme tokens** — non-negotiable foundation for everything theming.
- [ ] **Theme toggle (no-flash, OS-default, persistent, `aria-label`, keyboard, reduced-motion)** — the headline feature.
- [ ] **Logo sprite sliced into 8 assets** — unblocks brand and favicon work.
- [ ] **Header wordmark with attribute-driven theme swap** — replaces text title.
- [ ] **Favicon set: ICO + 16/32 PNG + 180 Apple + 192/512 PWA + `<link>` tags** — table-stakes browser identity.
- [ ] **`/gallery/` page with renamed `images/gallery/` folder, Hugo-optimized thumbnails, uniform grid, native lazy-load, srcset** — the gallery itself.
- [ ] **About page → page bundle, 1–3 inline photos** — minimum to claim "richer About."

### Add After Validation (v2.x)

Differentiators worth picking up only after v2.0 ships and renders well in real use.

- [ ] **Theme view-transition cross-fade** — adds polish; trigger if the abrupt swap feels harsh in practice.
- [ ] **Inline SVG wordmark with `currentColor`** — only if SVG source becomes available (collapses two PNGs to one asset).
- [ ] **SVG favicon with embedded dark-mode media query** — adds one more file but improves OS-tab fidelity.
- [ ] **Gallery click-to-zoom via `<dialog>`** — add when first user asks "can I see this bigger?"
- [ ] **Gallery captions** — only if photos start needing context (location, date).
- [ ] **PWA `site.webmanifest`** — mostly free given the favicon work; ship in v2.1.
- [ ] **Cross-tab theme sync via storage event** — add the day a user mentions it; otherwise skip.

### Future Consideration (v3+)

- [ ] **Per-photo metadata pages** — only if the gallery exceeds ~50 photos and individual photos start mattering.
- [ ] **Tags/filters in gallery** — same threshold.
- [ ] **Lightbox prev/next navigation** — same.
- [ ] **Three-state theme toggle (light/dark/auto)** — defer indefinitely; the two-state pattern with OS-preference default is sufficient.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| CSS variables refactor | HIGH (unblocks everything) | M | P1 |
| Theme toggle (no-flash, persistent, OS-default) | HIGH | M | P1 |
| Logo sprite slicing | HIGH (unblocks brand) | S | P1 |
| Header wordmark swap | HIGH | S | P1 |
| Favicon set + `<link>` tags | HIGH | S | P1 |
| `/gallery/` page with grid + lazy-load + srcset | HIGH | M | P1 |
| About page bundle + inline photos | MEDIUM | S | P1 |
| Theme view-transition cross-fade | LOW (polish) | S | P2 |
| Inline SVG wordmark | MEDIUM (asset hygiene) | S | P2 |
| SVG favicon with dark-mode media query | LOW | S | P2 |
| Gallery `<dialog>` lightbox | MEDIUM | M | P2 |
| Gallery captions | LOW | S | P3 |
| PWA `site.webmanifest` | LOW | S | P3 |
| Cross-tab theme sync | LOW | XS | P3 |

**Priority key:**
- P1: Must have for v2.0 launch
- P2: Add in v2.x if/when there's pull
- P3: Defer to v3+ unless user-driven need emerges

## Convention Reference (Personal-Blog Patterns Used in 2026)

What real personal Hugo/Eleventy/Astro blogs (the bench we're aiming at — not enterprise SaaS) actually do today:

- **Theme toggle:** Single icon button at the right edge of the header, sun↔moon, attribute-driven CSS. Inline `<head>` script for no-flash. CSS variables. `localStorage` + `prefers-color-scheme` fallback.
- **Logo per theme:** Two image assets, attribute-selector CSS swap (or one SVG with `currentColor`). `<picture>` + `prefers-color-scheme` is *not* used when there's a manual toggle.
- **Favicons:** Six-file matrix is the de-facto standard (`favicon.ico` + 16/32/180/192/512 PNG). SVG favicon as optional progressive enhancement.
- **Gallery:** Uniform CSS Grid, `aspect-ratio` + `object-fit: cover`, native `loading="lazy"`, Hugo-generated `srcset`. Lightbox is optional and now done with native `<dialog>` rather than libraries.
- **About:** Page bundle, mostly text, one or two inline photos. Side-by-side portrait next to intro paragraph is the most common above-the-fold layout.

## Sources

Theme toggle / no-flash:
- [Switching off the Lights — Adding Dark Mode to Hugo (Yonkov)](https://yonkov.github.io/post/add-dark-mode-toggle-to-hugo/)
- [Implementing dark mode for static websites (Phelipe Teles)](https://phelipetls.github.io/posts/implementing-dark-mode-for-static-websites/)
- [Adding dark mode to a Hugo static website without learning CSS (Radu Matei)](https://radu-matei.com/blog/dark-mode/)
- [How to Support Dark Mode on Your Hugo Static Website (tiredsg.dev)](https://www.tiredsg.dev/blog/support-dark-mode-hugo-static-website/)
- [The Complete Guide to the Dark Mode Toggle (Ryan Feigenbaum)](https://ryanfeigenbaum.com/dark-mode/)
- [Six levels of dark mode (CSSence)](https://cssence.com/2024/six-levels-of-dark-mode/)
- [Dark Mode in CSS Guide (CSS-Tricks)](https://css-tricks.com/a-complete-guide-to-dark-mode-on-the-web/)

Color-scheme / theme-color meta:
- [Improve dark mode default with color-scheme and a meta tag (web.dev)](https://web.dev/articles/color-scheme)
- [`<meta name="color-scheme">` (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/color-scheme)
- [`<meta name="theme-color">` (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/theme-color)
- [`prefers-color-scheme` (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme)

Logo / image swap per theme:
- [How to have Dark & Light Mode Images that also work with User Choice (Chip Cullen)](https://chipcullen.com/how-to-have-dark-mode-image-that-works-with-user-choice-yo/)
- [How to make images react to light and dark mode (Lars Magnus)](https://larsmagnus.co/blog/how-to-make-images-react-to-light-and-dark-mode)
- [Switch to a darker image when on dark mode! (DEV)](https://dev.to/ziratsu/switch-to-a-darker-image-when-on-dark-mode-2lkh)
- [Dark Mode Favicons: How to Make Your Icon Adapt (Premium Favicon)](https://www.premiumfavicon.com/blog/dark-mode-favicon-guide)

Favicon matrix:
- [How to Favicon in 2026 (Evil Martians)](https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs)
- [Favicon Sizes 2026 (FaviconStudio)](https://faviconstudio.com/blog/favicon-sizes-complete-guide)
- [Favicon Sizes — Complete Guide (Faviconator)](https://www.faviconator.com/blog/favicon-sizes)
- [Favicon Sizes 2026 (favicon.io)](https://favicon.io/tutorials/favicon-sizes/)

Gallery / lightbox / lazy-load:
- [Hugo image processing (Hugo docs)](https://gohugo.io/content-management/image-processing/)
- [Responsive and optimized images with Hugo (BryceWray)](https://www.brycewray.com/posts/2022/06/responsive-optimized-images-hugo/)
- [Lazy Loading Images in Hugo (Henrik Sommerfeld)](https://www.henriksommerfeld.se/lazy-loading-images-in-hugo/)
- [Browser-level image lazy loading (web.dev)](https://web.dev/articles/browser-level-image-lazy-loading)
- [Native Lazy Loading — Can I Use](https://caniuse.com/loading-lazy-attr)
- [Lazy Loading Images and Videos: The Complete Native Guide 2026 (VitalsFixer)](https://vitalsfixer.com/blog/lazy-loading-guide)
- [Hugo Easy Gallery (GitHub) — context for what NOT to use](https://github.com/liwenyip/hugo-easy-gallery)

Accessibility for toggle:
- [Complete Guide to Accessible Toggle Buttons (TestParty)](https://testparty.ai/blog/accessible-toggle-buttons-modern-web-apps-complete-guide)
- [ARIA: button role (MDN)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/button_role)
- [W3C Button Pattern (APG)](https://www.w3.org/WAI/ARIA/apg/patterns/button/)

About page conventions:
- [Modern Personal Site 2026 Guide (ME-Page)](https://me-page.com/blog/industry-use-cases-and-templates/personal-websites-in-2026-what-to-include-and-what-to-skip)
- [40+ Inspiring About Me Page Examples 2026 (SiteBuilderReport)](https://www.sitebuilderreport.com/inspiration/about-me-pages)

---
*Feature research for: Hugo personal blog brand identity + gallery + about*
*Researched: 2026-04-28*

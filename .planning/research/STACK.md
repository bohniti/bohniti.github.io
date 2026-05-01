# Stack Research — v3.0 Design Update

**Domain:** Hugo personal site refinement (icon-button theme toggle, lightbox/masonry gallery, About redesign)
**Researched:** 2026-05-01
**Confidence:** HIGH

> **Scope guardrail.** Only stack additions or changes for the three v3.0 features. The validated v2.0 stack (Hugo Extended 0.157.0, vanilla JS, single CSS file with Flexoki tokens, `image.Process` WebP pipeline, render-image hook, page-bundle layout) is LOCKED — this document does not re-research it.

## Headline Recommendation

**Add zero new runtime dependencies, zero npm packages, zero build tools.** Every feature ships with platform-native primitives that are already used elsewhere in the codebase or that fall inside the existing Hugo + vanilla CSS/JS budget.

| Feature | Recommended primitive | New dependency? |
|---------|----------------------|-----------------|
| (a) SVG icon theme toggle | Inline SVG (Lucide-style, hand-authored) inside existing `<button class="theme-toggle">` | No |
| (b) Lightbox + masonry gallery | Native `<dialog>` + `showModal()` + `::backdrop` blur; CSS `column-count` + `break-inside: avoid` | No |
| (c) About redesign | Existing render-image hook extended; CSS `border-radius` + asymmetric grid + asymmetric column tracks | No |

Rationale: every additive third-party library would dent the Flexoki/Kindle/Obsidian-minimal aesthetic and the "no JS framework, vanilla only" v2.0 invariant. The 2026 web platform has primitives for all three needs.

---

## Recommended Stack

### Core Technologies (existing, LOCKED — listed for context)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Hugo Extended | 0.157.0 | Static site generator + image processing | Already pinned in `.github/workflows/deploy.yml`. Built-in `image.Process` covers all gallery/About image needs. |
| Goldmark with `unsafe = true` | (Hugo bundled) | Markdown renderer that allows raw HTML | Already enabled in `hugo.toml`; needed for `<dialog>` markup if authored inline, but for v3.0 the dialog is wired in the layout template, not in markdown. |
| Vanilla CSS | — | Single stylesheet at `themes/minimal/static/css/style.css` | All v2.0 styling lives here under `:root` / `:root[data-theme="dark"]` token blocks; v3.0 extends this file, does not add a second stylesheet. |
| Vanilla JS | ES6+ | Inline `<head>` IIFE + end-of-body IIFE in `baseof.html` | Same pattern reused for the dialog open/close handler; no module bundler, no transpiler. |

### v3.0 Additions (new patterns, no new packages)

| Pattern | Spec / browser support | Purpose | Why this fits Flexoki + no-framework |
|---------|------------------------|---------|---------------------------------------|
| Native `<dialog>` element with `showModal()` | Chrome 37+, Edge 79+, Firefox 98+, Safari 15.4+ — full support across modern browsers in 2026 ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog)) | Lightbox container for full-size gallery photo | Browser handles focus trap, ESC-to-close, backdrop, top-layer rendering, `aria-modal` automatically. The W3C APA explicitly states focus-trap utility code is no longer needed when using `<dialog>` ([CSS-Tricks](https://css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/)). |
| `::backdrop` pseudo-element + `backdrop-filter: blur(...)` | 92–95% global support; full Chrome 76+, Edge 79+, Firefox 103+, Safari 17+ (Safari 9–16 needs `-webkit-` prefix) ([caniuse](https://caniuse.com/css-backdrop-filter)) | Blurred backdrop behind the lightbox, matching the v3.0 brief | Pure CSS, two declarations (`backdrop-filter` + `-webkit-backdrop-filter`); no JS, no extra DOM nodes. |
| CSS multi-column layout — `column-count` + `column-gap` + `break-inside: avoid` | Stable in every browser since IE10; zero risk in 2026 | Masonry-style gallery preserving each photo's natural aspect ratio | Pure CSS; pairs perfectly with Hugo `Resize "Wx webp q75"` (width-only) which preserves aspect ratio in the rendered `<img>`. CSS Grid `masonry` is too new (Safari 26 only as of 2026 — [CSS-Tricks](https://css-tricks.com/masonry-layout-is-now-grid-lanes/)). |
| Hugo page-resource frontmatter `params` for captions | Hugo 0.157 — stable since 0.31 ([Hugo docs](https://gohugo.io/content-management/page-resources/)) | Author 1–2 sentence caption per photo via `[[resources]]` array in `content/gallery/index.md` frontmatter | One source of truth (frontmatter, not a sidecar JSON), wildcard support (`src = "photos/*.jpg"`), accessed in template as `$photo.Params.caption`. |
| Hand-authored inline SVG icons (Lucide visual language) | — | Sun/moon icons for the theme toggle; matches existing footer GitHub + Instagram icons | The v2.0 footer **already** uses Lucide-style inline SVG (`viewBox="0 0 24 24"`, `stroke-width="2"`, `stroke-linecap="round"`, `currentColor`). Stay consistent — copy the same conventions, do not introduce a different icon family. |

---

## Supporting Libraries

**None recommended.** All three features ship with platform-native primitives.

The following npm/CDN libraries were considered and rejected for the reasons in the "What NOT to Use" section: PhotoSwipe, GLightbox, Tobii, Slightbox, Macy.js, Masonry.js, focus-trap, Lucide-as-package, Heroicons-as-package.

---

## Feature-Specific Recommendations

### (a) SVG Icon Theme Toggle

**Recommendation: hand-authored inline SVG inside the existing `<button class="theme-toggle">`.**

**Why inline SVG (over `<symbol>` sprite, over Hugo asset pipeline, over a `<picture>`/`<img>` swap):**

| Approach | Verdict | Reason |
|----------|---------|--------|
| **Inline SVG** | ✅ Use | Already the codebase pattern (footer GitHub + Instagram icons). `currentColor` recolors via `var(--text)`, exactly like the wordmark. Two icons × ~24 lines = ~48 lines added to `partials/header.html`. No HTTP request. No FOUC. No build step. |
| `<symbol>` sprite + `<use href="#sun">` | ❌ Skip | Adds a sprite file, requires `<use>` indirection, extra Hugo include. Wins only when you have many icons reused on many pages — Timo's site has two icons (sun + moon) on one button. |
| Hugo `resources.Get "icon.svg" \| readFile \| safeHTML` | ❌ Skip | Same effective result as inline, but spreads the icon source across two files instead of one. Use `readFile` only when the SVG is large (the wordmark is 814 LOC — that's the bar). |
| `<img src="sun.svg">` swap via `[data-theme]` | ❌ Skip | Already superseded by Phase 05.1 decision: inline SVG with `currentColor` is the project's chosen pattern. |

**Icon source:** copy the visual language of [Lucide](https://lucide.dev/icons/) (`sun`, `moon` — both 24×24, 2px stroke, round caps, `currentColor`). Do **not** install `lucide` as a package — copy the two SVG path strings directly into the header partial, the same way the GitHub and Instagram paths sit inline in `partials/footer.html` today.

**Why Lucide visual language (not Heroicons / Phosphor / Feather):**
- Existing footer icons already match Lucide conventions — visual consistency demands sun/moon match.
- Lucide is a maintained fork of Feather Icons (1500+ icons, MIT licensed) ([Lucide docs](https://lucide.dev/)).
- Heroicons would need 1.5px stroke (mismatched against existing 2px footer icons).
- Phosphor is heavier (multi-weight) and stylistically inconsistent with the rest.

**Toggle swap pattern (single button, two SVGs, CSS-driven):**

```html
<button type="button" class="theme-toggle" aria-label="Switch to dark mode" aria-pressed="false">
  <svg class="theme-toggle-sun" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>
  </svg>
  <svg class="theme-toggle-moon" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
  </svg>
</button>
```

CSS hides the inactive icon based on `[data-theme]`:

```css
:root[data-theme="light"] .theme-toggle-moon { display: none; }
:root[data-theme="dark"]  .theme-toggle-sun  { display: none; }
```

JS already in `baseof.html` toggles `data-theme`; only change the click handler's `toggle.textContent = next === 'dark' ? 'Light' : 'Dark'` line to `toggle.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode')`.

**Accessibility (verified):** for icon-only buttons, `aria-label` belongs on the button, `aria-hidden="true"` on the inner `<svg>` ([Sara Soueidan: Accessible Icon Buttons](https://www.sarasoueidan.com/blog/accessible-icon-buttons/)).

---

### (b) Lightbox + Masonry Gallery

**Recommendation: native `<dialog>` modal + CSS `column-count` masonry + Hugo frontmatter captions.**

#### Lightbox: native `<dialog>` element

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Modal mechanism | `<dialog>` + `dialog.showModal()` | Browser-native focus trap, ESC-to-close, top-layer rendering, `aria-modal="true"` applied automatically. No JS library needed. Browser support: Chrome 37+, Firefox 98+, Safari 15.4+, Edge 79+ ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog)). |
| Backdrop | `dialog::backdrop { backdrop-filter: blur(12px); background: rgba(16,15,15,0.6); }` (light) / `rgba(255,252,240,0.4)` (dark, via `:root[data-theme="dark"] dialog::backdrop`) | Pure CSS. No extra DOM. `backdrop-filter` 92% supported in 2026 ([caniuse](https://caniuse.com/css-backdrop-filter)); fallback to opaque-ish `background` when unsupported (already implicit). |
| Backdrop click closes | `dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); })` ([Aleksandr Hovhannisyan](https://www.aleksandrhovhannisyan.com/blog/how-to-open-and-close-html-dialogs/)) | One-line handler. The `closedby="any"` attribute is also available in newer Chrome but support is uneven — stick with the click handler. |
| Keyboard navigation | ESC = browser-native via `<dialog>`. Arrow keys = ~10 lines of vanilla JS reading `data-index` on `<dialog>` and updating `<img src>` in place. Tab = browser-native focus trap. | All zero-dependency. |
| Focus return on close | Browser-native — `<dialog>` returns focus to the trigger button. | Zero JS needed. |
| Number of `<dialog>` elements in DOM | **One**, mutated in place per click (single `<img>` and `<figcaption>` swapped) | Keeps DOM weight constant regardless of gallery size. 18 photos = 1 dialog, not 18. |

**Why not a JS lightbox library?**
- PhotoSwipe is 40+ KB minified gzipped — exceeds the entire current first-paint CSS budget.
- GLightbox / Tobii / Slightbox are smaller (5–15 KB) but still violate "no third-party libs unless essential", and `<dialog>` covers everything they do.
- The W3C APA confirms `<dialog>` makes focus-trap utilities obsolete ([CSS-Tricks](https://css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/)) — the historical reason to reach for a library is gone.

#### Masonry: CSS `column-count`

**Recommendation: `column-count: 3` + `column-gap: 1rem` + `break-inside: avoid` on `.gallery-item`.**

| Layout option | Verdict | Reason |
|---------------|---------|--------|
| **CSS `column-count`** | ✅ Use | Stable everywhere since IE10. Items flow into columns top-to-bottom (matches v3.0 "vertical-staggered" Tyler Karow reference). `break-inside: avoid` prevents splitting an `<a>` across columns. |
| CSS Grid `grid-template-rows: masonry` (a.k.a. `display: grid-lanes`) | ❌ Skip | Behind a flag in Chrome and Firefox as of early 2026; only Safari 26 ships stable ([CSS-Tricks](https://css-tricks.com/masonry-layout-is-now-grid-lanes/)). Production-blocking. |
| Flexbox column-direction | ❌ Skip | Requires fixed container height to wrap; doesn't degrade gracefully on responsive resize. |
| JS Masonry library (Macy.js, Masonry.js, Isotope) | ❌ Skip | Pixel-perfect but expensive: layout re-flow on resize, requires JS executing before paint (FOUC risk), 5–20 KB extra payload. CSS columns "good enough" for an 18-photo gallery and free from FOUC. |

**Important DOM-order caveat:** `column-count` flows top-to-bottom, **then** left-to-right (column 1 fills first, column 2 fills second, …). For a deterministic gallery this is fine. For Tyler-Karow-style "randomized" placement, randomize the **DOM order** at build time (Hugo `shuffle` template func) — not at runtime — so each deploy has a stable layout but a fresh shuffle. No JS needed.

**Responsive breakpoints:**

```css
.gallery-grid {
  column-count: 3;
  column-gap: 1rem;
}
@media (max-width: 900px) { .gallery-grid { column-count: 2; } }
@media (max-width: 600px) { .gallery-grid { column-count: 1; } }

.gallery-item {
  display: block;
  break-inside: avoid;            /* don't split a card across columns */
  margin-bottom: 1rem;            /* simulate row gap inside columns */
  border-radius: 4px;
  overflow: hidden;               /* clip rounded corners on the inner img */
}

.gallery-item img {
  width: 100%;
  height: auto;                   /* preserve aspect ratio from Hugo */
  display: block;
}
```

#### Captions: Hugo page-resource frontmatter

**Recommendation: `[[resources]]` array in `content/gallery/index.md` frontmatter with `params.caption`.**

```toml
title = "Gallery"
type  = "gallery"

[[resources]]
src = "photos/IMG_0256.jpeg"
title = "Sunset over the Hohe Tauern"
[resources.params]
caption = "Late summer evening on the descent — golden hour, no filter."

[[resources]]
src = "photos/*.jpg"        # wildcard fallback
[resources.params]
caption = ""                # empty caption is valid; template hides empty <figcaption>
```

Template access:

```go-html-template
{{ range .Resources.Match "photos/*" }}
  {{ $caption := .Params.caption }}
  ... <img ...> ...
  {{ with $caption }}<figcaption>{{ . }}</figcaption>{{ end }}
{{ end }}
```

**Why frontmatter (not a sidecar JSON, not per-photo `.md` files):**
- Single source of truth — one file to edit when adding a photo.
- Hugo-native — no JSON parsing, no `getJSON` round-trip.
- Wildcard `src = "photos/*"` lets you backfill defaults for un-captioned photos.
- Verified via Context7 / Hugo docs ([gohugo.io/methods/resource/Params](https://gohugo.io/methods/resource/Params/)) — confidence HIGH.

**Authoring path:** add a photo file to `content/gallery/photos/`, add a `[[resources]]` block in `index.md` with caption, commit. Done.

#### Image processing for masonry

Replace the current `fill 600x400 Smart` (forces uniform aspect ratio) with `Resize "600x webp q75"` (width-only, **preserves aspect ratio**) for thumbnails. Hugo emits the correct `width` and `height` attributes from the actual processed image, so CLS stays at 0.

```go-html-template
{{ $thumb := $photo.Resize "600x webp q75" }}
{{ $full  := $photo.Fit    "1600x1600 webp q82" }}
<img src="{{ $thumb.RelPermalink }}"
     width="{{ $thumb.Width }}"
     height="{{ $thumb.Height }}"
     loading="lazy" decoding="async" alt="{{ $caption }}">
```

Verified pattern via Hugo docs ([Resize method](https://gohugo.io/methods/resource/resize/), [Fit method](https://gohugo.io/methods/resource/fit/)).

---

### (c) About Redesign — "Dynamic, Rounded" within Flexoki

**Recommendation: extend the existing render-image hook (do not replace it) + asymmetric CSS Grid + softened `border-radius` tokens.**

What stays:
- Leaf-bundle pattern at `content/about/index.md` ✅
- `type: "about"` frontmatter → `body.page-about` class ✅
- Render-image hook keyed off image title (`hero` / `grid` / default) ✅
- Existing 5 EXIF-scrubbed photos ✅

What changes (CSS + content only — no template rewrites needed for hooks):

1. **Soften `border-radius`** site-wide via a token. Add `--radius-soft: 12px` (was 4–6px) to `:root` and apply to `.about-hero-img`, `.about-grid-item`, and the new content cards. This is the single biggest visual lever for "dynamic, rounded" without breaking Flexoki.

2. **Asymmetric section grid** — replace today's two-column `2fr 1fr` hero with a multi-section pattern: alternating wide-text/narrow-image and narrow-text/wide-image rows using `grid-template-columns: 3fr 2fr` and `grid-template-columns: 2fr 3fr` ([Tyler Karow's about page uses this exact magazine pattern](https://www.tylerkarow.com/about)).

3. **Add new render-image hook keyword `card`** (in addition to `hero` / `grid` / default) for medium-format inline portraits inside professional-section blocks. Process spec: `fill 600x450 Smart webp q78`. Append to existing three-arm switch — additive, not breaking.

4. **Content broadening** — markdown structure shifts from "climbing-heavy → professional + climbing balanced". This is a content edit in `content/about/index.md`, not a stack change.

5. **Optional decorative element** — a thin 1px `border` in `var(--border)` with `border-radius: var(--radius-soft)` around content cards adds the "rounded" feel without breaking minimalism. Card backgrounds stay `var(--bg)` (no shadow, no gradient — Kindle/Obsidian aesthetic must hold).

**Why no new template architecture:**
- The render-image hook is already three-armed; adding a fourth arm (`card`) is a 3-line change.
- Leaf bundle + `type: "about"` already gives a unique CSS scope (`body.page-about`).
- All visual changes happen in `themes/minimal/static/css/style.css` under the existing `body.page-about` block — same file, same scope, additive.

**Important constraint:** the dark-theme contrast warning on `.about-pullquote strong` (`#D14D41` on `#1C1B1A` = 3.97:1, passes WCAG AA only because of large bold text) is a load-bearing CSS comment. Any color change in v3.0 must re-check contrast with the WCAG calculator before merging.

---

## Installation

**No installs.** Zero new packages. All work happens in:

| File | Change |
|------|--------|
| `themes/minimal/layouts/partials/header.html` | Replace text "Dark"/"Light" inside `<button>` with two inline `<svg>` blocks. |
| `themes/minimal/layouts/_default/baseof.html` | Update click handler — swap `textContent` mutation for `aria-label` mutation. |
| `themes/minimal/layouts/gallery/single.html` | Add `<dialog>` element with `<img>` + `<figcaption>` + close `<button>`. Replace per-photo `<a href={{ $full.RelPermalink }}>` with `<button data-full="..." data-caption="...">` triggers. |
| `themes/minimal/layouts/_default/_markup/render-image.html` | Add fourth arm: `else if eq $title "card"` → `fill 600x450 Smart webp q78`. |
| `themes/minimal/static/css/style.css` | Add `.theme-toggle-sun/.theme-toggle-moon` rules; replace `.gallery-grid { display: grid }` with column-count rules; add `dialog.lightbox` + `dialog.lightbox::backdrop` rules; add `--radius-soft` token + body.page-about asymmetric section rules. |
| `content/gallery/index.md` | Add `[[resources]]` frontmatter with per-photo captions. |
| `content/about/index.md` | Broaden content beyond climbing; add new `card`-tagged image references. |
| `themes/minimal/layouts/gallery/single.html` | Inline ~30-line vanilla-JS IIFE at end-of-template (or move to baseof.html as a `{{ if eq .Section "gallery" }}` block). Handles dialog open/close, arrow-key navigation, image+caption swap. |

Total estimated LOC delta: **~150 lines added, ~40 lines removed** — comparable to a single v2.0 phase.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Native `<dialog>` lightbox | PhotoSwipe / GLightbox / Tobii | If you need video lightboxing, pinch-zoom on mobile, or programmatic pre-loading. None applies to this site. |
| CSS `column-count` masonry | CSS Grid Lanes (`display: grid-lanes`) | If targeting Safari 26+ only. Re-evaluate end of 2026 when Chrome/Firefox ship stable support. |
| CSS `column-count` masonry | JS Masonry / Macy.js | If photos must be reordered to fill gaps optimally and DOM-order randomization at build time isn't enough. Not the case here. |
| Hand-authored Lucide-style inline SVG | `lucide` npm package + Hugo SCSS pipeline | If the icon count grows past ~10 across the site. With 4 icons total (GitHub, Instagram, Sun, Moon) inline is simpler. |
| Frontmatter `[[resources]]` for captions | Sidecar JSON / one `.md` per photo | If caption text exceeds ~200 chars or needs Markdown-rendered links. v3.0 brief says "1–2 sentences" — frontmatter is fine. |
| Render-image hook (extended) | New shortcode `{{< photo title="…" caption="…" >}}` | If About content needed runtime caption editing in Markdown body. Hook already covers width/height + class assignment cleanly. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `lucide` / `lucide-static` npm packages | Adds Node toolchain to a pure-Hugo project. Two SVG path strings don't justify it. | Hand-author the two paths inline, matching existing footer icon conventions. |
| `@heroicons/*` packages | Same toolchain problem; also 1.5px stroke is inconsistent with existing 2px footer icons. | Lucide-style path strings inline. |
| PhotoSwipe / GLightbox / Tobii / Slightbox / lightbox2 | 5–40 KB JS payload to replicate what `<dialog>` does natively in 2026. | Native `<dialog>` + 30 lines of vanilla JS. |
| `focus-trap` / `focus-trap-react` | W3C APA explicitly stated focus-trap is no longer needed inside `<dialog>` ([CSS-Tricks](https://css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/)). | Native `<dialog>` focus management. |
| Macy.js / Masonry.js / Isotope | Layout in JS = FOUC + reflow on resize + 5–20 KB. Not needed for an 18-photo gallery. | CSS `column-count` + `break-inside: avoid`. |
| CSS Grid `display: grid-lanes` (a.k.a. masonry) | Only Safari 26 ships stable as of early 2026; Chrome/Firefox flagged ([CSS-Tricks](https://css-tricks.com/masonry-layout-is-now-grid-lanes/)). | CSS multi-column. Re-evaluate end of 2026. |
| Tailwind / SCSS / PostCSS pipeline | The site has one CSS file; introducing a build step violates the "keep it minimal" constraint and would require updating GitHub Actions. | Hugo's built-in CSS handling (already configured). |
| Sidecar JSON for captions | Forces `getJSON` template calls, syncs harder, no IDE autocomplete. | Hugo `[[resources]] params.caption` (Hugo-native). |
| Big shadow / gradient / animation libraries for "dynamic" feel | Breaks Kindle/Obsidian-minimal constraint. | Soften `border-radius` token; asymmetric grid; thin 1px border in `var(--border)`. |

---

## Stack Patterns by Variant

**If gallery grows past 50 photos:**
- Re-evaluate column-count masonry — DOM-order limitation may produce visible top-to-bottom-then-left-right "first column tall, last column short" imbalance.
- Mitigation: Hugo `shuffle` template function over `.Resources.Match` at build time so each deploy reshuffles.
- Escalation: only then consider Macy.js (4 KB minified gzipped).

**If About page needs interactive elements (carousel, animated transitions):**
- Stay vanilla JS, follow the same end-of-body IIFE pattern as `baseof.html`.
- Do not introduce a JS framework for animations — `prefers-reduced-motion` already constrains animation budget to "minimal theme-toggle transition".

**If browser-support telemetry shows >5% Safari < 17:**
- Add `-webkit-backdrop-filter` prefix alongside `backdrop-filter`. Trivial 1-line CSS addition.
- Fallback: opaque `background: rgba(16,15,15,0.85)` already provides a usable backdrop on browsers without `backdrop-filter`.

---

## Version Compatibility

| Pattern | Compatible With | Notes |
|---------|-----------------|-------|
| Native `<dialog>` | Hugo Extended 0.157.0 | Hugo doesn't process `<dialog>` — it passes through unchanged. `unsafe = true` is already set in `hugo.toml` so any inline JS handlers work. |
| CSS `column-count` | All browsers since IE10 | No prefix needed in 2026. |
| `backdrop-filter` | Safari 17+ unprefixed; Safari 9–16 needs `-webkit-` prefix | Include both for safety: `backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);` |
| Hugo `Resize "Wx webp"` | Hugo Extended 0.157.0 | Verified via Hugo docs. WebP support requires Extended (already pinned in workflow). |
| Hugo `[[resources]]` frontmatter | Hugo 0.31+ | Stable since 2017. Wildcard `src = "photos/*.jpg"` supported. |
| Render-image hook (existing) | Hugo 0.62.0+ | Already validated in v2.0 Phase 7. Adding a fourth arm to the title-keyword switch is purely additive. |

---

## Sources

### Verified via Context7 (HIGH confidence)
- `/gohugoio/hugo` — page resources frontmatter `[[resources]]` + `params.caption`, `Resize` method aspect-ratio behavior, `Fit` method, render-image hooks
- `/lucide-icons/lucide` (v0.547.0) — confirmed Lucide visual conventions (24×24 viewBox, 2px stroke, round caps, `currentColor`) match existing footer icons

### Verified via official documentation (HIGH confidence)
- [MDN: `<dialog>` element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog) — confirms `showModal()` provides built-in focus trap, ESC-to-close, top-layer rendering, `aria-modal="true"`
- [MDN: `::backdrop` pseudo-element](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/::backdrop) — confirms behavior with `<dialog>` showModal
- [MDN: `backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter) — confirms 92%+ browser support
- [caniuse: backdrop-filter](https://caniuse.com/css-backdrop-filter) — Safari 17+ unprefixed; 9–16 needs `-webkit-` prefix
- [Hugo docs: page resources](https://gohugo.io/content-management/page-resources/) — confirms `[[resources]]` frontmatter + wildcard `src` patterns
- [Hugo docs: Resize method](https://gohugo.io/methods/resource/resize/) — confirms width-only spec preserves aspect ratio
- [Hugo docs: Fit method](https://gohugo.io/methods/resource/fit/) — confirms aspect-ratio preservation when fitting

### Verified via authoritative third-party (MEDIUM-HIGH confidence)
- [CSS-Tricks: There is No Need to Trap Focus on a Dialog Element](https://css-tricks.com/there-is-no-need-to-trap-focus-on-a-dialog-element/) — W3C APA position
- [CSS-Tricks: Masonry Layout is Now grid-lanes](https://css-tricks.com/masonry-layout-is-now-grid-lanes/) — confirms Safari 26 only as of early 2026
- [CSS-Tricks: Approaches for a CSS Masonry Layout](https://css-tricks.com/piecing-together-approaches-for-a-css-masonry-layout/) — `column-count` + `break-inside: avoid` pattern
- [Sara Soueidan: Accessible Icon Buttons](https://www.sarasoueidan.com/blog/accessible-icon-buttons/) — `aria-label` on button + `aria-hidden` on inner SVG
- [Aleksandr Hovhannisyan: How to Open and Close HTML Dialogs](https://www.aleksandrhovhannisyan.com/blog/how-to-open-and-close-html-dialogs/) — backdrop-click close pattern
- [Lucide: Icons](https://lucide.dev/icons/) — sun and moon path data reference

### Visual references (LOW confidence — design inspiration only)
- [Tyler Karow: Gallery](http://tylerkarow.com/gallery) — masonry-with-captions reference (note: actual implementation is Squarespace's proprietary gallery widget; we reverse the visual pattern, not the code)
- [Tyler Karow: About](https://www.tylerkarow.com/about) — asymmetric magazine-style about-page reference

---

## Confidence Summary

| Recommendation | Confidence | Why |
|----------------|------------|-----|
| Inline SVG sun/moon (Lucide visual language) | HIGH | Existing footer icons are Lucide-style; pattern is in-codebase precedent. |
| Native `<dialog>` lightbox | HIGH | Browser support verified via MDN + caniuse; W3C APA position cited. |
| CSS `column-count` masonry | HIGH | Universal browser support; verified via multiple CSS-Tricks references; CSS Grid Lanes alternative explicitly disqualified for 2026. |
| Hugo `[[resources]] params.caption` | HIGH | Verified via Context7 (`/gohugoio/hugo`) + Hugo docs. |
| Render-image hook extension (`card` arm) | HIGH | Pattern already validated in v2.0 Phase 7; additive change. |
| `backdrop-filter` blur | HIGH | 92% support verified via caniuse; `-webkit-` prefix path documented. |
| Soften `border-radius` token + asymmetric grid for About | MEDIUM | Stylistic decision; tested against Flexoki/Kindle constraint via reasoning, not measurement. Recommend visual review during phase planning. |
| DOM-order shuffle at build time for "randomized" gallery | MEDIUM | Hugo `shuffle` is well-documented but the visual outcome depends on photo aspect-ratio mix; may need empirical tweaking during phase execution. |

---

*Stack research for: Hugo personal site v3.0 design refinement*
*Researched: 2026-05-01*

# Phase 5: Wordmark + Favicon Wiring - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Two coordinated wiring tasks built on Phase 3's sliced PNGs and Phase 4's `[data-theme]` attribute:

1. **Wordmark wiring** — Replace the plain text `{{ .Site.Title }}` in `partials/header.html` with two `<img>` tags pointing at `logo-light.png` / `logo-dark.png`, swapped by CSS `[data-theme]` selectors (no FOUC, no JS swap). Each variant carries the per-asset background color from Phase 4's cross-phase contract to mask the seam against `--bg`.

2. **Favicon wiring** — Generate the missing 3-file favicon set (`favicon.ico`, `favicon.svg` with embedded dark-mode `@media`, `apple-touch-icon.png` 180×180) by extending `scripts/build_brand_assets.py`. Wire them via a new `partials/favicon.html` included from `baseof.html` `<head>` immediately after `<title>`.

In scope: the wordmark `<img>` swap (CSS technique, sizing, alt text, seam-masking bg), the favicon asset generation extension, the favicon partial and head wiring, the 3-file favicon set including the PNG-wrapped SVG.

Out of scope: a hand-traced path-based TB monogram SVG (would expand into Phase 3 design work — see Deferred), inline SVG wordmark with `currentColor` (REQUIREMENTS Future Requirements), `<picture>` + `prefers-color-scheme` for the wordmark (explicitly REQUIREMENTS Out of Scope — silently overrides the manual toggle, anti-pattern), PWA `site.webmanifest`, legacy `mstile-*` / `browserconfig.xml`.

</domain>

<decisions>
## Implementation Decisions

### Wordmark CSS Swap Technique

- **D-01:** Two `<img>` tags rendered side-by-side in `partials/header.html`, swapped via `display: none` keyed off `[data-theme]` on `<html>`. Hidden variant exits the layout flow so the visible variant alone determines header height — no CLS once the active `<img>` carries explicit `width`/`height`. Both PNGs load up front (each 20–27 KB; combined ~47 KB) — acceptable for a header asset that ships once per session and is then HTTP-cached.
  ```css
  html[data-theme="light"] .wordmark-dark { display: none; }
  html[data-theme="dark"]  .wordmark-light { display: none; }
  ```
- **D-02:** Both `<img>` tags carry `alt="Timo Bohnstedt"`. `display: none` removes the hidden variant from the accessibility tree so screen readers announce the alt only once. Robust against future swap-technique changes.

### Wordmark Sizing & Placement

- **D-03:** Wordmark rendered at **200×117 px** on desktop (≥ 600px viewport), **160×93 px** under `@media (max-width: 600px)`. Aspect 1.71:1 from the 800×467 source — both render sizes preserve the ratio so no distortion. Explicit `width="200" height="117"` attributes on the `<img>` elements satisfy HEAD-03 and pre-reserve layout to prevent CLS. Mobile size adjustment via CSS, not via separate srcset.
- **D-04:** Wordmark replaces the current `{{ .Site.Title }}` text inside the existing `.site-title` element. The `<a href="{{ .Site.BaseURL }}">` wrapper stays — wordmark remains a clickable home link, mirroring the current behavior. Two `<img>` tags sit inside the anchor.

### Seam-Masking Background (honors Phase 4 D-02 contract)

- **D-05:** Per-variant background color applied **directly to each `<img>` via class**, NOT to a wrapper element or to `.site-title`:
  ```css
  .wordmark-light { background: #FEFEFE; }
  .wordmark-dark  { background: #000000; }
  ```
  This binds the bg color to the asset variant rather than the active theme — stays correct regardless of swap technique and matches Phase 4 D-02's hard cross-phase contract literally (`#FEFEFE` for `-light` PNG, `#000000` for `-dark` PNG, sampled by `scripts/build_brand_assets.py` from corner pixels). Without this, a visible ~5–7% lightness band frames the wordmark against Flexoki `--bg`.

### Mobile Wordmark Variant

- **D-06:** Same full `logo-*` (script "time BOHNSTEDT" with climber) on every viewport. No swap to `minimum-*` or `icon-*` under any breakpoint. Brand consistency across viewports, simpler CSS (single image source per theme), 800px source has plenty of pixel headroom for sub-pixel-smooth rendering at 160×93 px on 1× and 2× DPI screens. The `minimum-*` and `icon-*` variants stay sliced and committed but unused in v2.0 — they're available for future use.

### Favicon SVG Strategy

- **D-07:** `favicon.svg` is a **PNG-wrapped SVG with embedded `@media (prefers-color-scheme: dark)`**. The SVG contains two `<image>` elements (one referencing the light-variant favicon PNG, one the dark) and an inline `<style>` block that flips visibility based on the OS color scheme. Modern browsers (Chrome/Firefox/Safari) honor this for tab favicons. Pragmatic — meets HEAD-04 spec on paper without requiring an SVG redraw. Hand-tracing the TB monogram to real path-based SVG is rejected as scope creep into Phase 3 (see Deferred).
  ```svg
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
    <style>
      @media (prefers-color-scheme: dark) {
        .l { display: none; } .d { display: inline; }
      }
      .d { display: none; }
    </style>
    <image class="l" href="data:image/png;base64,..." width="512" height="512"/>
    <image class="d" href="data:image/png;base64,..." width="512" height="512"/>
  </svg>
  ```
- **D-08:** Both PNGs are **base64-embedded** as `data:image/png;base64,...` URIs inside `<image href>` (NOT external `href` references to `/images/brand/favicon-*.png`). Self-contained — single file, no cross-resource lookup, no risk of browsers blocking external refs in the favicon-loading context. Final SVG size ~75 KB (favicon PNGs are 27/31 KB each, base64 inflates ~33%) — acceptable for a one-time per-session tab-icon load.

### Favicon Asset Generation Pipeline

- **D-09:** Extend `scripts/build_brand_assets.py` (the renamed Phase 3 asset processor) with new output stages: produce `favicon.ico`, `apple-touch-icon.png` (180×180), and `favicon.svg` from the existing `favicon-{light,dark}.png` 512×512 inputs. Reuses the throwaway-Pillow-venv invocation pattern (no new runtime deps, no `requirements.txt`, human-invoked once before Phase 5 wiring work). Single script runs all asset stages.
- **D-10:** **`favicon.ico` source: `favicon-light.png`**. Multi-size `.ico` with embedded 16×16, 32×32, and 48×48 frames generated by Pillow's `.save(format="ICO", sizes=[(16,16),(32,32),(48,48)])`. Browsers don't theme-swap `.ico` — light variant reads cleanly against most browser tab chrome, bookmarks panel, and iOS home-screen. Dark-mode tab adaptation comes from `favicon.svg` (which browsers prefer when present and supported).
- **D-11:** **`apple-touch-icon.png` source: `favicon-light.png`** resized to 180×180 via Pillow `.resize((180, 180), Image.LANCZOS)` then re-pngquanted. iOS home-screen background varies — light variant works against both light and dark wallpapers because the TB sits on a `#FEFEFE` square. No transparent-bg variant attempted (existing PNGs are RGB without alpha; color-keying would risk fringe artifacts on anti-aliased edges).
- **D-12:** Output dir: `themes/minimal/static/` (root of theme static). Hugo serves these at `/favicon.ico`, `/favicon.svg`, `/apple-touch-icon.png`. Co-located with existing `static/css/` and `static/images/brand/` so a future theme switch carries the favicon set with it.

### Favicon Partial & `<head>` Wiring

- **D-13:** New file `themes/minimal/layouts/partials/favicon.html` defines exactly 3 `<link>` tags (no more, no less, per ROADMAP success criterion 3):
  ```html
  <link rel="icon" type="image/svg+xml" href="{{ "favicon.svg" | absURL }}">
  <link rel="icon" type="image/x-icon" href="{{ "favicon.ico" | absURL }}">
  <link rel="apple-touch-icon" href="{{ "apple-touch-icon.png" | absURL }}">
  ```
  Order matters: SVG first so browsers that support it use it (and benefit from dark-mode `@media`); `.ico` is the fallback for legacy tabs and Windows shortcuts; `apple-touch-icon` is keyed by `rel` for iOS home-screen.
- **D-14:** Included from `baseof.html` `<head>` immediately after the `<title>` tag (and before the existing `<meta name="description">`), via `{{ partial "favicon.html" . }}`. Placement matches ROADMAP success criterion 3 verbatim.

### Claude's Discretion

- Exact CSS class names for the wordmark `<img>` tags — `.wordmark`, `.wordmark-light`, `.wordmark-dark` are reasonable but final choice can match existing `.site-*` naming patterns (e.g., `.site-wordmark`).
- Whether the existing `.site-title` element stays as the parent or is renamed — keep `.site-title` for layout-class continuity unless renaming clarifies intent.
- The `.site-title a` typography rules in `style.css` (currently sized as text) need either updating or replacing for the image case — Claude decides whether to keep the existing rule and add `.site-title img` overrides, or refactor.
- Pillow `.ico` API specifics — `Image.save("favicon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48)])` is the standard call; verify Pillow version on the throwaway venv supports the `sizes` kwarg (10.x does).
- pngquant settings for the resized 180×180 apple-touch — within the `--quality=65-90` envelope from Phase 3 D-06; tune if file size feels off.
- favicon.svg `width`/`height`/`viewBox` declared values — `viewBox="0 0 512 512"` matches source dimensions; declaring `width`/`height` is optional for SVG favicons but doesn't hurt.
- Whether to add `type="image/png"` to the apple-touch `<link>` — not required by spec, optional.
- Whether the SVG `<style>` block's class names use single letters (`.l`, `.d`) or descriptive names (`.light`, `.dark`) — single letters keep base64-inflated file slightly smaller; descriptive names are kinder to future-me.

### Folded Todos

None — no pending todos in STATE.md matched this phase's scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & Requirements
- `.planning/ROADMAP.md` § "Phase 5: Wordmark + Favicon Wiring" — phase goal, dependencies (Phase 3 + Phase 4), 4 success criteria
- `.planning/REQUIREMENTS.md` § "Header & Favicon" — HEAD-01 (script wordmark replaces text title), HEAD-02 (two-image CSS toggle, no FOUC, no JS), HEAD-03 (explicit width/height + meaningful alt), HEAD-04 (3-file favicon set including .svg with embedded dark-mode @media), HEAD-05 (favicon partial at `partials/favicon.html` included from baseof.html)
- `.planning/REQUIREMENTS.md` § "Out of Scope" — `<picture>` + `prefers-color-scheme` for wordmark (REJECTED — silently overrides manual toggle, anti-pattern); custom `@font-face` for wordmark (REJECTED — wordmark is a sliced PNG, not a webfont)
- `.planning/REQUIREMENTS.md` § "Future Requirements" — inline SVG wordmark with `currentColor` (deferred), PWA `site.webmanifest` (deferred), view-transition cross-fade on theme toggle (deferred)
- `.planning/PROJECT.md` § "Constraints" — no JS framework, no flash on load, brand consistency: same logo source drives both wordmark and favicon (no manual redraws)
- `.planning/PROJECT.md` § "Key Decisions" — locks: 3-file favicon set (skip legacy `mstile-*`/`browserconfig.xml`), two-image CSS toggle for wordmark (each variant ≤ 30 KB)

### Cross-Phase Contracts (incoming)
- `.planning/phases/03-brand-asset-slicing/03-CONTEXT.md` § "Mid-Execution Deviation" — Phase 3 outputs: 8 PNGs at `themes/minimal/static/images/brand/`, naming `{logo,icon,minimum,favicon}-{light,dark}.png`; favicon variants are 512×512 squares (forced); logo aspect-paired (800×467). Recorded hex values for the seam contract: top-row dark `#000000`, bottom-row light `#FEFEFE`.
- `.planning/phases/04-theming-foundation/04-CONTEXT.md` § "D-01, D-02" + § "Cross-Phase Contracts (outgoing) → To Phase 5" — site `--bg`/`--bg-dark` use Flexoki canonical `#FFFCF0`/`#100F0F` (NOT the corner-pixel hex from Phase 3). The wordmark `<img>` (or wrapper) MUST set per-variant bg matching the PNG's corner pixel (`#FEFEFE` for `-light`, `#000000` for `-dark`) to mask the rectangular seam against Flexoki `--bg`. **Hard cross-phase contract — honored by Phase 5 D-05.**
- `.planning/phases/04-theming-foundation/04-CONTEXT.md` § "D-11" — `[data-theme]` is set on `<html>` (`document.documentElement`) by the head IIFE before stylesheet parse. Phase 5's wordmark CSS keys off `html[data-theme="light"|"dark"]` directly, no JS swap.

### Codebase Conventions & Files
- `themes/minimal/layouts/partials/header.html` (currently 11 lines) — `.site-title > a > {{ .Site.Title }}` text replaced with the two wordmark `<img>` tags inside the existing anchor
- `themes/minimal/layouts/_default/baseof.html` (currently 57 lines) — `{{ partial "favicon.html" . }}` inserted after `<title>` (line 8), before `<meta name="description">` (line 9)
- `themes/minimal/layouts/partials/favicon.html` — NEW file, 3 `<link>` tags
- `themes/minimal/static/css/style.css` (264 lines) — add `.wordmark` / `.wordmark-light` / `.wordmark-dark` rules (display: none swap + per-variant bg), update `.site-title` rules to handle the image case, add mobile size override under existing `@media (max-width: 600px)` block at ~line 259
- `themes/minimal/static/images/brand/` — 8 sliced PNGs from Phase 3 (logo + icon + minimum + favicon × light + dark); Phase 5 consumes `logo-light.png`, `logo-dark.png` for the wordmark and `favicon-light.png` for the .ico/apple-touch generation
- `scripts/build_brand_assets.py` — Phase 3 asset pipeline; extended in Phase 5 with new output stages for `favicon.ico` (multi-size 16/32/48), `apple-touch-icon.png` (180×180), `favicon.svg` (PNG-wrapped with dark-mode `@media`)
- `themes/minimal/static/` — output root for `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`
- `.planning/codebase/CONVENTIONS.md` § "Python Script Conventions" — PEP 8, snake_case, `pathlib.Path`, no type hints, `if __name__ == "__main__"` guard (extension to `build_brand_assets.py` must match)
- `.planning/codebase/CONVENTIONS.md` § "CSS Conventions" — Flexoki palette, `.site-*` naming, single stylesheet (`.wordmark` class additions follow this pattern)

### Cross-Phase Contracts (outgoing)
- **To Phase 6 (Gallery)** and beyond: the favicon partial pattern (`partials/favicon.html` included from `baseof.html`) is the precedent for any future `<head>`-fragment partials. The 3-file favicon set is locked — adding new sizes (e.g., `favicon-96.png`) requires a roadmap decision, not a Phase 5 follow-up.
- **To future phases:** `scripts/build_brand_assets.py` is now a multi-output asset pipeline (sprite/screenshots → 8 PNGs + 3 favicon files). New brand outputs should land here, not in a new script.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/build_brand_assets.py` — Pillow-based asset processor from Phase 3 (renamed via `git mv` from `slice_logos.py` mid-execution). Already handles auto-trim, aspect-pair matching, RGBA→RGB flatten, pngquant subprocess invocation, BRAND-03 30 KB gate, corner-pixel hex sampling. Extending it with `.ico` / 180×180 / SVG-wrapper output stages is purely additive — same throwaway venv, same invocation pattern.
- `themes/minimal/layouts/_default/baseof.html` — already structured for `{{ partial "..." . }}` includes (header.html, footer.html). Adding `{{ partial "favicon.html" . }}` after `<title>` is a one-line insertion.
- `themes/minimal/layouts/partials/header.html` — existing `<a href="{{ .Site.BaseURL }}">{{ .Site.Title }}</a>` anchor stays; only the text content swaps to two `<img>` tags. The wordmark remains a home link.
- `themes/minimal/static/css/style.css` — `.site-title a` rule (lines 74-83) uses `font-size`, `font-weight`, `color: var(--text)`. With wordmark images replacing text, these become irrelevant for the wordmark itself but shouldn't be deleted (anchor styling — link color on hover — still applies).
- `themes/minimal/static/images/brand/` — 8 sliced PNGs ready, all under 30 KB after pngquant per Phase 3's BRAND-03 gate.

### Established Patterns
- Hugo partials for `<head>` and body fragments — adding `partials/favicon.html` follows the existing `header.html` / `footer.html` pattern
- Static-file serving via `themes/minimal/static/` — Hugo serves these at site root, no special config needed for `/favicon.ico` etc.
- Pillow + throwaway-venv for one-off image work — Phase 3 established this; favicon stages extend it
- `pngquant` as a subprocess on each output PNG — Phase 3 D-06; apple-touch-icon.png re-runs the same step
- CSS variables for theming — `.wordmark` rules use `var(--bg)` only if needed; the per-variant masking bg is hardcoded hex (`#FEFEFE`/`#000000`) per Phase 4 D-02 because it must match the PNG corner pixel, not the theme token

### Integration Points
- **`partials/header.html`** — replace `{{ .Site.Title }}` text with two `<img class="wordmark wordmark-light">` and `<img class="wordmark wordmark-dark">` inside the existing `<a>` anchor
- **`baseof.html` `<head>`** — insert `{{ partial "favicon.html" . }}` between `<title>` (line 8) and `<meta name="description">` (line 9)
- **`partials/favicon.html`** — new file, 3 `<link>` tags
- **`style.css`** — add `.wordmark`/`.wordmark-light`/`.wordmark-dark` rules; update `.site-title img` if needed; add mobile size override under existing `@media (max-width: 600px)` at line ~259
- **`scripts/build_brand_assets.py`** — add `build_favicon_ico()`, `build_apple_touch()`, `build_favicon_svg()` functions, call them after the existing PNG output stage; pngquant the apple-touch output; print final sizes for all favicon outputs to stdout (matches Phase 3's "verbose output" convention)
- **`themes/minimal/static/`** — new files committed: `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`

### Hugo-Specific Notes
- Hugo automatically serves `static/favicon.ico` at `/favicon.ico` — no `hugo.toml` config change needed
- `{{ "favicon.svg" | absURL }}` resolves against `baseURL` (`https://tbohnstedt.cloud/`) — produces full URL in production, root-relative in dev
- No new shortcodes needed for this phase

</code_context>

<specifics>
## Specific Ideas

- The wordmark `<img>` tags both render — they're not lazy-loaded, no `loading="lazy"` on the visible variant (they're above-the-fold). The hidden variant (under `display: none`) gets fetched by browsers anyway during a hard reload, so explicit `loading="eager"` is unnecessary.
- Verify the seam-masking bg on a real screen-grab in BOTH themes before declaring HEAD-02 done — the Phase 4 D-02 contract says "without this, a visible ~5–7% lightness band frames each wordmark." Eyeball the wordmark area against `--bg` to confirm the seam disappears.
- The `favicon.svg` PNG-wrapper is genuinely supported (Chrome 80+, Firefox 105+, Safari 15+). Test by force-toggling OS appearance after first load and watching the tab favicon swap. If a browser doesn't support inline `@media` in SVG favicons, it falls back to `.ico` (light variant) — graceful degradation.
- Lighthouse Mobile CLS < 0.1 on `/` (ROADMAP success criterion 2) is structurally guaranteed by the explicit `width`/`height` attributes on the wordmark `<img>` tags. Verify after deploy by running Lighthouse against the live URL.
- After deploy, manually validate the favicon set on at least: Chrome desktop tab, Safari iOS tab, iOS Add-to-Home-Screen (apple-touch). The "no generic Hugo / browser default" success criterion (#4) requires a visual check — automated tooling won't catch a 404'd favicon in tab chrome.
- The `partials/favicon.html` file is small and stable — once shipped, it shouldn't change unless the brand assets change. Treat it as fire-and-forget infrastructure.

</specifics>

<deferred>
## Deferred Ideas

- **Hand-traced TB monogram path SVG** with `currentColor` or `@media`-driven fill — the cleanest favicon implementation, but it's design/illustration work that effectively expands Phase 5 into Phase 3 territory. Already noted in `REQUIREMENTS.md` § "Future Requirements (deferred to v2.x or later)" as "Inline SVG wordmark with `currentColor` (if SVG source becomes available)". Same applies to the favicon: revisit if and when an SVG source is produced.
- **PWA `site.webmanifest`** with theme-color and icons — listed in REQUIREMENTS § Future. Phase 5 ships only the 3-file favicon set; manifest is a separate v2.x concern.
- **`<link rel="mask-icon">` for legacy Safari pinned-tabs** — modern Safari (13+) uses `favicon.svg` and respects `@media (prefers-color-scheme: dark)`; mask-icon is no longer needed for current Safari versions.
- **Wordmark srcset for hi-DPI screens** — the 800×467 source is already 4× larger than the 200×117 desktop render and 5× the mobile render, so 2× DPI screens get full sub-pixel sharpness from the existing PNG. No `srcset` needed in v2.0.
- **Cross-tab favicon sync** — irrelevant; favicons don't have a "state" to sync.
- **View-transition API on wordmark swap** — listed in REQUIREMENTS § Future for the toggle generally; the wordmark inherits whatever Phase 4's transition behavior provides (currently a 150ms color transition under non-reduced-motion). No additional wordmark-specific transition.
- **Removing the `minimum-*` and `icon-*` PNGs from `themes/minimal/static/images/brand/`** — they remain unused in v2.0 but were sliced and committed by Phase 3. Keep them for future phases (potential mobile swap, alternate logo placements, social share images, etc.).
- **`<picture>` + `prefers-color-scheme` for wordmark** — explicitly REQUIREMENTS Out of Scope (silently overrides the manual toggle, research-flagged anti-pattern). Do NOT revisit in Phase 5.

</deferred>

---

*Phase: 05-wordmark-favicon-wiring*
*Context gathered: 2026-04-29*

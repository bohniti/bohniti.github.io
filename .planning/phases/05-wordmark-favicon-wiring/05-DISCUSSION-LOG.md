# Phase 5: Wordmark + Favicon Wiring - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 05-wordmark-favicon-wiring
**Areas discussed:** Wordmark CSS swap technique, Mobile wordmark variant, Favicon SVG strategy, Favicon asset generation pipeline

---

## Wordmark CSS swap technique

### Q1: How should the two wordmark `<img>` tags swap when `[data-theme]` flips?

| Option | Description | Selected |
|--------|-------------|----------|
| `display: none` swap | Both `<img>` rendered, one hidden by `html[data-theme=...] .wordmark-light { display: none }`. Both PNGs load (~20–27 KB each). Hidden variant exits flow so no CLS once dimensions are set. Screen readers ignore `display: none`. | ✓ |
| Absolute-overlay with opacity | Both `<img>` stacked at the same position, opacity flips by `[data-theme]`. Both reserve layout space — no flicker, but parent needs explicit dimensions and `position: relative`. Slightly more CSS, both stay in a11y tree unless `aria-hidden` flipped. | |
| Single `<img>` with `content: url()` | One element, CSS `content: url(...)` swaps source by `[data-theme]`. Smaller DOM. But `content` on `<img>` has known quirks and `<img alt>` may not be honored consistently. | |

**User's choice:** `display: none` swap (Recommended)
**Notes:** Picks the simplest, most accessible path; the marginal cost of loading both 20–27 KB PNGs is acceptable for a once-per-session header asset.

---

### Q2: How should `alt` text be set on the two `<img>` tags?

| Option | Description | Selected |
|--------|-------------|----------|
| Both carry `alt="Timo Bohnstedt"` | `display: none` removes the hidden one from the a11y tree, so no double-announce. Robust if swap technique ever changes. | ✓ |
| Visible has alt, hidden `alt=""` | Belt-and-suspenders against any future a11y-tree quirk, but means alt has to flip if technique changes — fragile. | |
| One alt, one `aria-hidden="true"` | More explicit a11y signal but redundant under `display: none`. Adds attribute juggling per theme. | |

**User's choice:** Both carry `alt="Timo Bohnstedt"` (Recommended)
**Notes:** Robustness wins over redundant explicitness; `display: none` already provides the a11y guarantee.

---

### Q3: What rendered size should the wordmark `<img>` carry?

| Option | Description | Selected |
|--------|-------------|----------|
| 200×117 px — match current text weight | Wordmark height ~28px font equivalent. Matches current `.site-title` text weight, header height stays roughly the same, doesn't compete with nav. Width fits all viewports above 320px. | ✓ |
| 260×152 px — more brand prominence | Wordmark ~36px tall. Stronger glance read. Risks crowding nav at 700–800px before mobile breakpoint. | |
| 160×93 px — tucked tight | Wordmark ~22px tall. Compact, lean header. Brand reads more like an icon than a statement. | |

**User's choice:** 200×117 px (Recommended)
**Notes:** Balances brand prominence with header restraint; preserves the visual weight users already associate with the site.

---

### Q4: Where should the per-variant background color be applied?

| Option | Description | Selected |
|--------|-------------|----------|
| Directly on each `<img>` via class | `.wordmark-light { background: #FEFEFE; }` and `.wordmark-dark { background: #000000; }`. Bg bound to asset variant, not active theme — correct regardless of swap technique. No wrapper needed. | ✓ |
| On a `<span>` wrapper around both imgs | Single `<span class="wordmark">` wraps both `<img>` tags; bg flips on the wrapper by `[data-theme]`. Adds a DOM node and decouples bg from variant. | |
| On `.site-title` directly, theme-keyed | Bg via `html[data-theme=light]` / `[data-theme=dark]` selectors. No new wrapper. But bg extends to full `.site-title` width including unrelated whitespace. | |

**User's choice:** Directly on each `<img>` via class (Recommended)
**Notes:** Cleanest mapping to Phase 4 D-02's hard cross-phase contract; bg color stays bound to the PNG it's masking the seam for.

---

## Mobile wordmark variant

### Q1: What should the wordmark show on narrow viewports (under 600px)?

| Option | Description | Selected |
|--------|-------------|----------|
| Same full `logo-*` at smaller size | Keep the script "time BOHNSTEDT" wordmark on every viewport, just scale down. Simplest — no swap logic, brand consistency, 800×467 source has plenty of pixel headroom. | ✓ |
| Swap to `minimum-*` (script "time" only) | Lighter feel on mobile, less crowded. Adds complexity — four image variants in flight, swap logic combines theme + viewport. | |
| Swap to `icon-*` (TB monogram) | Punchier mobile presence, treats brand as a logo mark rather than a wordmark. Same complexity overhead. | |

**User's choice:** Same full `logo-*` at smaller size (Recommended)
**Notes:** Brand consistency wins; the `minimum-*` and `icon-*` variants stay sliced and available for future phases.

---

### Q2: What rendered size for the wordmark on narrow viewports?

| Option | Description | Selected |
|--------|-------------|----------|
| 160×93 px | Comfortable on viewports as narrow as 320px. ~80% of desktop. Header still reads as branded but doesn't dominate. | ✓ |
| 180×105 px | Slightly larger, brand stays prominent. Risks looking oversized next to column-stacked nav. | |
| Same 200×117 px as desktop | No size adjustment — single rule. May feel oversized on narrowest devices. | |

**User's choice:** 160×93 px (Recommended)
**Notes:** Narrow-viewport breathing room without sacrificing legibility.

---

## Favicon SVG strategy

### Q1: How should we satisfy HEAD-04's `favicon.svg` requirement when brand assets are PNG only?

| Option | Description | Selected |
|--------|-------------|----------|
| PNG-wrapped SVG with media query | SVG containing two `<image href="...">` elements (light/dark PNG) and an embedded `<style>` block with `@media (prefers-color-scheme: dark)` flipping visibility. Modern browsers honor it. ~50–60 KB. Pragmatic — ships now, no design work. | ✓ |
| Drop `favicon.svg`, use only `.ico` + apple-touch | Deviate from HEAD-04. Browser tab stays light-mode-only. Simpler. Document the deviation, note "inline SVG wordmark with `currentColor`" is already in REQUIREMENTS § Future. | |
| Hand-trace TB monogram to real SVG paths | Real path-based SVG with `currentColor` or `@media`-driven fill. Cleanest result — tiny file, true dark-mode swap. But this is design work, not wiring — expands Phase 5 into Phase 3 territory. | |

**User's choice:** PNG-wrapped SVG with media query (Recommended)
**Notes:** Meets HEAD-04 spec on paper without expanding scope into design/illustration work.

---

### Q2: How should the two PNGs be referenced inside `favicon.svg`?

| Option | Description | Selected |
|--------|-------------|----------|
| Base64-embedded (self-contained) | Both PNGs base64-encoded directly into `<image href="data:image/png;base64,...">`. Single file, no external refs. Inflates ~33% (~75 KB total). | ✓ |
| External `href` to brand PNGs | `<image href="/images/brand/favicon-light.png">` referencing existing files. Smaller SVG (<1 KB), browsers fetch PNG separately. But: relative path resolution and security policies for SVG-as-favicon vary. | |

**User's choice:** Base64-embedded (Recommended)
**Notes:** Self-containment trumps file size for a one-time per-session tab-icon load.

---

## Favicon asset generation pipeline

### Q1: How should the missing favicon assets be produced?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `scripts/build_brand_assets.py` | Add output stages to the existing Pillow pipeline (Phase 3 pattern). Reproducible. Fits "one-time human-invoked" convention. Slight scope creep into Phase 3's script but natural extension. | ✓ |
| Standalone `scripts/build_favicons.py` | Separate script. Cleaner separation but two scripts to maintain. | |
| One-shot manual ImageMagick + commit outputs | Run ImageMagick once locally, commit outputs. No new Python. Less reproducible — someone has to remember the commands. | |
| Hugo image processing at build time | `resources.Get` + `.Resize` / `.Process` in `partials/favicon.html`. Hugo can't produce `.ico` — still needs external tool. Couples wiring to Hugo. | |

**User's choice:** Extend `scripts/build_brand_assets.py` (Recommended)
**Notes:** Reproducibility + single-source-of-truth for brand asset processing.

---

### Q2: Which brand variant should the static `.ico` and `apple-touch-icon.png` use?

| Option | Description | Selected |
|--------|-------------|----------|
| `-light` variant (TB on light bg) | Source `favicon-light.png`. Reads against most browser tab chrome, iOS home-screen, bookmarks. Dark-mode adaptation comes from `favicon.svg`. | ✓ |
| `-dark` variant (TB on dark bg) | Best if expecting most chrome to be dark. Risks looking like a black square on light tab bars. | |
| Composite — light TB on transparent bg | Removes `#FEFEFE` background via color-keying, leaving transparent PNG. Adapts to any tab color. But: existing PNGs are RGB (no alpha), keying risks fringe artifacts on anti-aliased edges. | |

**User's choice:** `-light` variant (Recommended)
**Notes:** Matches the most common chrome environments; SVG handles dark-mode swap where supported.

---

### Q3: Where should the favicon files be output?

| Option | Description | Selected |
|--------|-------------|----------|
| `themes/minimal/static/` | Co-locates with existing theme `static/css/` and `static/images/brand/`. Hugo serves at site root. Future theme switch carries the favicon set. | ✓ |
| `static/` at repo root | Repo-root `static/` already exists (CNAME, files/). Hugo merges with theme static. Inconsistent with where Phase 3 placed brand PNGs. | |

**User's choice:** `themes/minimal/static/` (Recommended)
**Notes:** Theme-scoped placement matches where Phase 3 put the brand PNGs.

---

## Claude's Discretion

- Exact CSS class names for the wordmark `<img>` tags (e.g., `.wordmark` vs `.site-wordmark`)
- Whether `.site-title` element stays as parent or is renamed
- Whether to keep existing `.site-title a` typography rules or refactor
- Pillow `.ico` API specifics (sizes kwarg)
- pngquant settings for the resized 180×180 apple-touch (within `--quality=65-90` envelope)
- favicon.svg `width`/`height`/`viewBox` declared values (`viewBox="0 0 512 512"` recommended)
- Whether to add `type="image/png"` to apple-touch `<link>`
- SVG `<style>` class names — single letters (`.l`, `.d`) vs descriptive (`.light`, `.dark`)

## Deferred Ideas

- Hand-traced TB monogram path SVG with `currentColor` — REQUIREMENTS § Future
- PWA `site.webmanifest` — REQUIREMENTS § Future
- `<link rel="mask-icon">` for legacy Safari pinned-tabs — modern Safari uses `favicon.svg`
- Wordmark srcset for hi-DPI screens — 4–5× pixel headroom in existing 800×467 source, not needed
- Cross-tab favicon sync — N/A
- View-transition API on wordmark swap — REQUIREMENTS § Future (toggle generally)
- Removing unused `minimum-*` / `icon-*` PNGs — keep for future phases
- `<picture>` + `prefers-color-scheme` for wordmark — explicitly REQUIREMENTS Out of Scope (anti-pattern)

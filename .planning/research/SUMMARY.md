# Research Summary — v3.0 Design Update

**Project:** Personal Website — v3.0 Design Update
**Domain:** Hugo static site polish (theme-toggle icon, gallery lightbox + masonry, About redesign)
**Researched:** 2026-05-01
**Confidence:** HIGH

---

## Executive Summary

v3.0 is a focused refinement of three rough edges in the v2.0 design — none requiring new dependencies, new build tools, or framework decisions. Every recommendation from the four research streams lands on platform-native primitives that already have codebase precedent: inline SVG icons (following the exact footer pattern), native `<dialog>` for the lightbox (universal browser support since 2024), CSS `column-count` for masonry (universal since IE10), and Hugo `[[resources]]` frontmatter for caption authoring. The total estimated change is ~150 LOC added, ~40 LOC removed — comparable to a single v2.0 phase.

The highest-stakes decision in the milestone is the gallery ordering model. Three of the four research agents weighed in on this and reached different conclusions: STACK recommends Hugo `shuffle` at build time, ARCHITECTURE recommends client-side shuffle for build determinism, and PITFALLS recommends author-controlled deterministic order frozen at authoring time. This conflict is surfaced explicitly below with a recommended resolution. All other technical decisions have full four-agent convergence and should be treated as locked.

The principal risks are accessibility regressions (icon FOUC, missing focus trap, hit-target shrinkage, reduced-motion violations) and a CLS spike if masonry aspect-ratio handling is done incorrectly. Both are well-understood and have concrete prevention patterns documented below. No pitfall requires a structural architecture change — they are all implementation correctness issues addressable within the recommended approach.

---

## Key Findings

### Stack Additions (STACK.md)

Zero new runtime dependencies. Zero npm packages. Zero build tools. All three features ship with primitives already present in the codebase or available natively in the 2026 browser platform.

**New patterns, not new packages:**

| Pattern | New dep? | Rationale |
|---------|----------|-----------|
| Inline SVG sun/moon (Lucide visual language, hand-authored) | No | Footer icons already use Lucide-style 24x24, 2px stroke, `currentColor`. Two paths (~200 bytes each). |
| Native `<dialog>` + `showModal()` + `::backdrop` blur | No | Chrome 37+, Firefox 98+, Safari 15.4+. Browser handles focus trap, ESC, top-layer, `aria-modal` automatically. |
| CSS `column-count` + `break-inside: avoid` | No | Universal since IE10. `grid-template-rows: masonry` is Safari-only in 2026 — blocked. |
| Hugo `[[resources]]` frontmatter `params.caption` | No | Hugo-native since 0.31. Single source of truth for per-photo metadata in `content/gallery/index.md`. |
| Render-image hook extended with `card`/`split`/`feature` arms | No | Additive to the existing three-arm switch validated in v2.0 Phase 7. |

**Stack additions summary: none.** All work happens in existing files (`header.html`, `baseof.html`, `gallery/single.html`, `render-image.html`, `style.css`) plus new content (`content/gallery/index.md` frontmatter, `content/about/index.md` rewrite) and one new layout file (`layouts/about/single.html`).

---

### Feature Table Stakes (FEATURES.md)

#### ICON — Theme Toggle

Must have for v3.0 launch:
- Sun SVG shown in light mode, moon SVG shown in dark mode (icon = current state, not target action)
- `aria-label` on button describes target action ("Switch to dark mode / Switch to light mode")
- `aria-pressed` retained — communicates toggle state to screen readers
- Both SVGs inline in `header.html`, CSS-driven swap via `[data-theme]` — zero FOUC
- `currentColor` on all `fill`/`stroke` attributes — recolors with `var(--text)`
- Tap target >= 44x44 CSS-px (explicit button width/height, not icon intrinsic size)
- `focus-visible` outline preserved on the button element
- Optional 150ms rotate/fade transition, wrapped in `@media (prefers-reduced-motion: no-preference)`

Defer to v3.x:
- Single-SVG morph (sun-with-moon-mask trick) — marginal visual gain over two-SVG approach

#### GALLERY — Lightbox + Masonry + Captions

Must have for v3.0 launch:
- Thumbnail click opens native `<dialog>` modal (not a new page)
- Blurred backdrop via `dialog::backdrop { backdrop-filter: blur(12px) }` with `rgba` fallback
- ESC / backdrop-click / X-button all close modal (ESC is native via `<dialog>`)
- Arrow keys + on-screen prev/next buttons navigate the gallery
- Mobile touch swipe left/right (50px deltaX threshold, ~20 LOC)
- Caption rendered below image in modal; graceful empty state if absent
- Aspect ratio preserved per photo: Hugo `Resize "600x webp q75"` (not `fill 600x400`)
- CSS `column-count: 3` masonry (2 at 600-900px, 1 at <600px)
- `width` + `height` attributes from Hugo emitted on every `<img>` — preserves CLS < 0.1
- Hugo `[[resources]]` frontmatter with `params.caption` (and `params.weight` for ordering)
- `role="dialog" aria-modal="true"`, `aria-label` updated on navigation
- Body scroll locked while modal open; focus restored to trigger on close
- EXIF scrub check carried forward as a CI gate

Defer to v3.x:
- Photo counter "3 / 18" overlay
- Preload next/prev image `<link rel="preload">`

#### ABOUT — Redesign

Must have for v3.0 launch:
- Asymmetric CSS Grid sections (alternating text/image ratios)
- `--radius-soft: 12px` token applied to photos and content cards (up from 4-6px)
- Role cards: `var(--bg-secondary)` tint + `var(--border)` + `border-radius: 12px` — no shadows
- Hero portrait + intro + CV link retained in full
- Professional content balanced with climbing — "Outside Work" section consolidates personal content
- All new CSS scoped under `body.page-about` — no global rule pollution
- Pullquote contrast invariant preserved (`.about-pullquote strong` must remain >= 1.4rem, weight >= 700 in dark mode)
- Mobile reflow: all multi-column layouts collapse to single column at <600px

Defer to v3.x:
- Hover micro-interactions on role cards (only if cards become external links)
- Audience-specific About variants (recruiter / collaborator / friend)

---

### Architecture Approach (ARCHITECTURE.md)

All three features integrate cleanly into the existing layered architecture. No new files need to be created except one optional JS file for the gallery lightbox (`themes/minimal/static/js/lightbox.js`) and one new layout (`themes/minimal/layouts/about/single.html`). The single stylesheet convention holds — `style.css` grows by ~60 lines with section-commented additions.

**Modified components per feature:**

| Component | ICON | GALLERY | ABOUT |
|-----------|------|---------|-------|
| `themes/minimal/layouts/partials/header.html` | Replace text with 2 inline SVGs | — | — |
| `themes/minimal/layouts/_default/baseof.html` | Remove `textContent` mutation | — | — |
| `themes/minimal/layouts/gallery/single.html` | — | Add caption lookup + dialog triggers | — |
| `themes/minimal/layouts/_default/_markup/render-image.html` | — | — | Add `card`/`split`/`feature` arms |
| `themes/minimal/layouts/about/single.html` | — | — | NEW: dedicated about layout |
| `themes/minimal/static/css/style.css` | Icon show/hide rules | Column-count + lightbox rules | `--radius-soft` + section rules |
| `content/gallery/index.md` | — | `[[resources]]` with captions | — |
| `content/about/index.md` | — | — | Markdown rewrite |

**Key patterns to follow:**
1. Inline SVG with `currentColor` — established by footer icons and wordmark. Sun/moon follow the same convention.
2. `body.page-{type}` CSS scoping — `body.page-about` for About rules, `body.page-gallery` for gallery rules. No global rule additions.
3. Page-scoped JS — `lightbox.js` loaded only from `gallery/single.html`, not from `baseof.html`. Keeps all other pages free of unused JS.
4. One source of truth: `dataset.theme` — JS writes only to `documentElement.dataset.theme`; CSS reads it. No imperative icon-class manipulation in JS.

---

### Critical Pitfalls (PITFALLS.md)

The full PITFALLS.md documents 22 pitfalls. The top 8 with the highest consequence for this milestone:

1. **Icon FOUC (Pitfall 1)** — Render both SVGs in HTML; CSS hides the wrong one via `[data-theme]`. The IIFE runs before `<link rel="stylesheet">` so `data-theme` is set before first paint. Do NOT update icons imperatively in JS.

2. **CLS spike from masonry without explicit `width`/`height` (Pitfall 4)** — Hugo `Resize "600x webp q75"` emits `width` and `height` from the processed image. Keep both attributes on every `<img>`. This is the difference between CLS < 0.1 and a broken layout score.

3. **Gallery ordering nondeterminism (Pitfall 5)** — See the conflict resolution section below. Whatever approach is chosen must be decided before any gallery layout work begins.

4. **Lightbox focus trap / ESC / scroll lock (Pitfall 8)** — Use native `<dialog>` with `showModal()`. All three behaviors (focus trap, ESC, scroll lock) are browser-native. No manual implementation needed.

5. **`prefers-reduced-motion` on icon rotation + lightbox transition (Pitfall 9)** — Every new CSS `transition` or `animation` must be wrapped in `@media (prefers-reduced-motion: no-preference)`. Same pattern as `style.css:49-56`.

6. **Render-image hook breakage for new About image shapes (Pitfall 14)** — Enumerate the new layout's image shapes before writing any About markdown. Update the hook first, then write content.

7. **Pullquote contrast regression in dark mode (Pitfall 15)** — `.about-pullquote strong` is currently at 3.97:1 (passes AA as large bold text only). Any change to font-size below 1.4rem or weight below 700 creates a WCAG fail. Re-check contrast on any About CSS change.

8. **Generic CSS class names leaking across pages (Pitfall 17)** — All About-specific CSS must be prefixed `body.page-about`. Use `.about-card`, `.about-hero-circle` — never `.card`, `.hero`.

---

## Conflict Resolution: Gallery Ordering

**The conflict:** Three research streams reached different conclusions on how to randomize gallery order.

| Agent | Recommendation | Reasoning |
|-------|---------------|-----------|
| STACK | Hugo `shuffle` template function at build time | Stable per deploy, no JS needed |
| ARCHITECTURE | Client-side shuffle in `lightbox.js` on `DOMContentLoaded` | Hugo `collections.Shuffle` is non-deterministic across builds (verified: gohugo.io + Hugo issue #5641) |
| PITFALLS | Author-controlled order frozen at authoring time | Non-deterministic = broken deep-links, diff churn, confusion for repeat visitors |
| FEATURES | Author-controlled `weight` in frontmatter | Deterministic; pairs naturally with the caption authoring path |

**Recommended resolution: author-controlled deterministic order via `params.weight` in `[[resources]]` frontmatter.**

Rationale:
- ARCHITECTURE correctly identifies that Hugo `shuffle` is non-deterministic across builds — STACK's recommendation is wrong on this point (the Hugo docs confirm there is no stable seeding primitive).
- Client-side shuffle is technically viable but produces layout reorder after paint (reflow on every visit) and breaks the stable gallery expectation for a personal portfolio.
- Author-controlled `weight` achieves "feels random" by having the author deliberately vary positions when adding photos. The order is intentional, deterministic, and never regresses on deploy.
- The `params.weight` field is already part of the FEATURES.md recommended frontmatter schema.

**Decision to surface to user:** Should the gallery feel "freshly random on each visit" (client-side shuffle, minor reflow) or "deliberately curated and stable" (author-controlled weight)? The research recommends the latter, but this is an aesthetic preference call.

---

## Implications for Roadmap

All four research agents converge on the same build order: ICON then ABOUT then GALLERY (or ICON then GALLERY then ABOUT). Gallery has the most moving parts and the only new JS file; it belongs last. ICON is the smallest and lowest-risk change; it belongs first.

### Phase 1: ICON — SVG Theme Toggle

**Rationale:** Smallest blast radius. Three-file change. Builds confidence in v3.0 before larger surgery. Zero content changes. Zero JS additions.
**Delivers:** Sun/moon SVG icon in header, correct in both themes, no FOUC, accessible.
**Implements:** Inline SVG pattern (Lucide visual language), CSS-driven swap via `[data-theme]`, `aria-label` update in JS click handler.
**Must avoid:** Icon FOUC (P01), hit-target shrinkage (P02), hard-coded fill colors (P03), `prefers-reduced-motion` violation (P09), `theme-color` meta desync (P22).
**Research flag:** No deeper research needed. Pattern is a direct extension of the footer SVG icon convention. HIGH confidence.

REQ categories: `ICON-01` (SVG markup in header.html), `ICON-02` (CSS swap rules), `ICON-03` (aria-label JS update), `ICON-04` (tap target CSS), `ICON-05` (transition guard).

### Phase 2: ABOUT — Dynamic Rounded Redesign

**Rationale:** Template + CSS work with no new JS. Can be scaffolded and visually validated with existing photos before any content rewrite. Independent of gallery — no shared file conflicts.
**Delivers:** Asymmetric CSS Grid layout, `--radius-soft` token, role cards, balanced climbing/professional content, custom `layouts/about/single.html`.
**Implements:** `body.page-about` scoping, render-image hook extension (new arms), shortcodes (split/pullquote/feature).
**Must avoid:** Pullquote contrast regression (P15), CSS leaking across pages (P17), "dynamic" misread as JS widgets (P21), hero cropping on mobile (P19), asymmetric sections collapsing poorly (P20), Kindle/Obsidian aesthetic violated by shadows/gradients (P16), stale professional content (P18).
**Research flag:** Shortcode count (ARCHITECTURE says 3, could be 2 or 4) is a judgment call to validate during planning. Recommend visual comparison against `tylerkarow.com/about` before locking the design.

REQ categories: `ABOUT-01` (layout template), `ABOUT-02` (render-image hook extension), `ABOUT-03` (role cards CSS), `ABOUT-04` (radius token), `ABOUT-05` (content rewrite), `ABOUT-06` (contrast check gate), `ABOUT-07` (mobile reflow check).

### Phase 3: GALLERY — Lightbox + Masonry + Captions

**Rationale:** Most moving parts. Three internal sub-dependencies (caption data then template emits data attrs then JS reads them). First JS file added to the theme. Save for last so a regression does not block the simpler features.
**Delivers:** Native `<dialog>` lightbox, CSS column-count masonry, per-photo captions in frontmatter, touch swipe, keyboard navigation, EXIF CI gate.
**Implements:** `[[resources]]` frontmatter schema, `gallery/single.html` template changes, `lightbox.js` (~80 LOC IIFE loaded page-scoped), CSS masonry rules replacing current uniform grid.
**Must avoid:** CLS spike (P04), nondeterministic ordering (P05), missing captions silently shipping (P06), lazy-load conflict in lightbox (P07), missing focus trap/ESC/scroll-lock (P08), backdrop-filter perf on low-end devices (P10), page weight blowout from preloading fulls (P11), alt text dropped from lightbox primary image (P12), EXIF reintroduced by new photos (P13).
**Research flag:** Gallery ordering decision (author-weight vs. client-shuffle) must be resolved as the first task in this phase, before any layout work. Sub-order within phase: caption frontmatter first, then template, then JS.

REQ categories: `GALLERY-01` (frontmatter schema: caption + weight + alt), `GALLERY-02` (Hugo image processing: Resize not fill), `GALLERY-03` (column-count masonry CSS), `GALLERY-04` (dialog lightbox template), `GALLERY-05` (lightbox JS: open/close/nav/focus), `GALLERY-06` (touch swipe), `GALLERY-07` (EXIF CI gate), `GALLERY-08` (CLS verification gate).

### Phase Ordering Rationale

- ICON first: no content dependency, proves the v3.0 milestone is tracking before committing to larger changes.
- ABOUT second: CSS + template work validates the Flexoki aesthetic extension before gallery adds JS complexity. Content rewrite is editorial and separable from template scaffolding.
- GALLERY last: only feature that adds a new JS file, introduces a new authoring workflow (frontmatter captions), and requires sub-task ordering within the phase. A gallery regression does not block ICON or ABOUT delivery.
- No shared-file conflicts between ICON and ABOUT, or ABOUT and GALLERY (except `style.css`, which section comments handle cleanly).

### Research Flags

No deeper research needed for any phase — all three features have HIGH-confidence documented patterns. Outstanding judgment calls:

- Phase 2 (ABOUT): How many shortcodes? ARCHITECTURE says 3 (split/pullquote/feature). May resolve to 2 if the About design stays simpler than tylerkarow.com. Validate during planning.
- Phase 3 (GALLERY): Gallery ordering model (see Conflict Resolution above). Must be a named decision in REQUIREMENTS.md before Phase 3 planning begins.
- Phase 3 (GALLERY): `backdrop-filter` blur radius. Recommend starting with flat semi-transparent overlay (`rgba(16,15,15,0.85)`) and only adding blur after HUMAN-UAT review explicitly requests it. Avoids GPU perf risk on low-end devices.

---

## Watch Out For (Top 5 Highest-Stakes Pitfalls)

These pitfalls are promoted to milestone-level invariants — they are blocking on any phase that touches them, not soft checks.

1. **FOUC on icon state (Pitfall 1):** Verify with CPU 6x throttle + hard reload in dark mode. If the wrong icon appears for even one frame, it is a FOUC regression. The fix (CSS-driven swap keyed off `[data-theme]`) must be implemented first before the icon phase can close.

2. **CLS regression in masonry (Pitfall 4):** Hugo must emit `width` and `height` attributes from `Resize "600x webp q75"` on every gallery `<img>`. Switching from `fill 600x400` to width-only Resize is required. Measure CLS on the deployed gallery before Phase 3 closes — target < 0.1.

3. **Lightbox accessibility completeness (Pitfall 8):** `<dialog>` with `showModal()` is the recommended implementation. Any deviation (DIV-based modal, class-toggle-only) must implement focus trap, ESC binding, scroll lock, and focus restoration manually. This is a hard verification gate, not a soft check.

4. **Gallery ordering nondeterminism (Pitfall 5):** The ordering model decision must be committed to in writing before gallery layout work begins. Changing it mid-phase invalidates the template and data model. It is a data-model decision, not a CSS decision.

5. **Pullquote contrast on dark theme (Pitfall 15):** The `.about-pullquote strong` CSS comment is load-bearing. Any About phase change that touches `font-size`, `font-weight`, or `color` in that rule must re-run WCAG contrast check with the dark-theme color pair. Encode the constraint in the verification gate.

---

## Stack Additions Summary

Zero new dependencies. For the roadmapper's reference:

| What ships new | How | File |
|---------------|-----|------|
| Sun SVG path | Hand-authored inline, Lucide visual language | `header.html` |
| Moon SVG path | Hand-authored inline, Lucide visual language | `header.html` |
| `<dialog>` lightbox element | Native HTML, no library | `gallery/single.html` |
| Lightbox IIFE | ~80 LOC vanilla JS | `themes/minimal/static/js/lightbox.js` |
| CSS masonry rules | ~10 LOC, `column-count` | `style.css` |
| CSS lightbox rules | ~40 LOC, `dialog.lightbox` + `::backdrop` | `style.css` |
| About layout template | New file, `type: "about"` routing | `layouts/about/single.html` |
| 3 shortcodes | `split`, `pullquote`, `feature` | `layouts/shortcodes/` |
| `--radius-soft` CSS token | Single line in `:root` | `style.css` |

No CDN additions. No npm. No new build pipeline steps.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Zero new dependencies; all patterns verified via MDN, Hugo docs (Context7), and existing codebase precedent. |
| Features | HIGH | Table stakes verified against MDN accessibility docs, reference site fetch (tylerkarow.com), and v2.0 codebase audit. |
| Architecture | HIGH | All touchpoints verified by reading current files. Hugo `shuffle` non-determinism confirmed via gohugo.io + Hugo issue #5641. |
| Pitfalls | HIGH | Grounded in actual code paths in this codebase (specific line numbers in `baseof.html`, `style.css`, `gallery/single.html`). Not generic advice. |

**Overall confidence: HIGH**

### Gaps to Address During Planning

- Gallery ordering model: surfaced as a conflict between STACK, ARCHITECTURE, and PITFALLS research. Recommended resolution is author-controlled `params.weight`. Needs user confirmation before Phase 3 REQUIREMENTS are written.
- About shortcode count: ARCHITECTURE says 3 (split/pullquote/feature). Validate against the final About design before Phase 2 REQUIREMENTS are written. Could be 2 or 4.
- About asymmetric section count: How many alternating image/text rows does Timo want? Content-strategy decision, not architecture.
- Backdrop blur radius: `blur(12px)` or flat rgba? Performance vs. aesthetic. Recommend starting flat and adding blur only if HUMAN-UAT requests it.
- Hugo Smart crop behavior for circular hero: Hugo 0.157.0 Smart cropping is entropy-based (not face-detection). Any circular About hero image must be tested in the build output before the phase closes.

---

## Sources

### Primary — Verified via Context7 / Hugo docs (HIGH confidence)
- `/gohugoio/hugo` — `[[resources]]` frontmatter, `Resize` width-only aspect-ratio behavior, `Fit` method, render-image hooks, `collections.Shuffle` non-determinism
- `/lucide-icons/lucide` (v0.547.0) — sun/moon path data, Lucide conventions (24x24, 2px stroke, round caps, `currentColor`)
- MDN: `<dialog>` element — `showModal()`, focus trap, ESC, `aria-modal`
- MDN: `backdrop-filter` — browser support, `-webkit-` prefix requirement for Safari <17
- Hugo docs: page resources — `[[resources]]` frontmatter + wildcard `src`
- Hugo issue #5641 — confirms no stable seeding primitive for `collections.Shuffle`
- Existing codebase files (read directly): `baseof.html`, `header.html`, `footer.html`, `gallery/single.html`, `render-image.html`, `style.css`, `content/gallery/index.md`, `content/about/index.md`, `hugo.toml`

### Secondary — Verified via authoritative third-party (MEDIUM-HIGH confidence)
- CSS-Tricks: There is No Need to Trap Focus on a Dialog Element — W3C APA position on `<dialog>` native focus trap
- CSS-Tricks: Masonry Layout is Now grid-lanes — confirms CSS Grid masonry is Safari-only in 2026
- Sara Soueidan: Accessible Icon Buttons — `aria-label` on button, `aria-hidden` on inner SVG
- caniuse: backdrop-filter — 92%+ global support; Safari 9-16 needs `-webkit-` prefix

### Tertiary — Visual reference only (LOW confidence — design inspiration, not implementation)
- tylerkarow.com/gallery — masonry + lightbox reference (Squarespace proprietary; visual pattern only)
- tylerkarow.com/about — asymmetric single-column about-page reference

---

*Research completed: 2026-05-01*
*Ready for roadmap: yes*

# Feature Research — v3.0 Design Update

**Domain:** Personal Hugo site polish — three rough edges (theme toggle icon, gallery lightbox + masonry + captions, About redesign) within Flexoki/Kindle/Obsidian-minimal aesthetic
**Researched:** 2026-05-01
**Confidence:** HIGH (existing codebase fully read; UX patterns verified against MDN, web.dev, CSS-Tricks; reference sites tylerkarow.com/{gallery,about} fetched directly)

## Scope Note

v3.0 refines three already-shipped features (v2.0). This research focuses **only** on the deltas:

- (a) **Theme-toggle icon** — replace text "Dark"/"Light" button with SVG sun/moon
- (b) **Gallery refactor** — replace standalone-page navigation with lightbox modal; replace uniform CSS Grid with masonry-like layout; add per-photo captions
- (c) **About redesign** — replace current rigid 2-col hero + 2-col grid with asymmetric, more rounded, professionally-balanced layout

Existing infrastructure to **reuse** (do not re-research):

- `[data-theme]` attribute + Flexoki light/dark CSS variables (`themes/minimal/static/css/style.css:4-33`)
- No-FOUC IIFE in `<head>` (`themes/minimal/layouts/_default/baseof.html:11-23`)
- localStorage `'theme'` key + OS `prefers-color-scheme` fallback
- `aria-pressed` semantics on toggle button (`partials/header.html:11`)
- Hugo `image.Process` page-bundle WebP pipeline at q75/q78/q82 (`gallery/single.html:10-11`, `_markup/render-image.html:7-13`)
- `.theme-toggle:focus-visible` outline pattern (`style.css:117-122`)
- `prefers-reduced-motion` guard on body transitions (`style.css:49-56`)
- About leaf-bundle render-image hook keyed off image title (`hero` / `grid` / default)

---

## Feature Landscape

### Table Stakes (Must-Have for It to Feel "Right")

#### (a) Theme-Toggle Icon Button

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Icon shows current state, not target** | Industry convention (web.dev, MDN, GitHub): sun-when-light, moon-when-dark. Inverting confuses users — they read the icon as "where I am" not "where I'll go". | LOW | Toggle JS already swaps state — just swap which `<svg>` is visible (or use one SVG with CSS) instead of swapping `textContent`. |
| **`aria-label` describes the action (target state)** | Screen-reader convention: "Switch to dark mode" / "Switch to light mode" — the button **does** something, the label says what. Distinct from the visual icon (which shows current state). | LOW | Current button has no `aria-label` — relies on text content. Removing text means adding label. Update label in same JS branch that toggles `aria-pressed`. |
| **`aria-pressed` retained** | Already present — communicates "this is a toggle, currently on/off". Removing it is a regression. | LOW | Keep `aria-pressed="true"` when dark, `"false"` when light. |
| **Keyboard activation works** | `<button>` already gives Enter + Space for free. Don't lose this by switching to `<a>` or `<div>`. | LOW | Keep `<button type="button">`. |
| **`focus-visible` outline preserved** | Existing `.theme-toggle:focus-visible` rule works for any focusable element — keep it. | LOW | No change needed; outline targets the button regardless of inner content. |
| **Same header position + size budget** | Stated milestone constraint. Replacing text "Dark" (≈30px wide) with a 16–20px icon means the header layout shifts unless the button reserves comparable hit area. | LOW | Set explicit button size (e.g., 24×24 or 32×32) so flex gap stays balanced. |
| **No FOUC of icon state** | Same problem as theme FOUC: server HTML can't know which icon to render. Solution: render both, hide the wrong one via CSS keyed on `[data-theme]`, OR have the head IIFE set the icon. | LOW | Cleanest: render both `<svg>` inside button, CSS hides one based on `:root[data-theme="dark"] .icon-sun { display: none }` — works at first paint with the existing IIFE. |
| **Icon respects `currentColor`** | Existing wordmark already uses this pattern (Phase 05.1 D-01). Sun/moon must recolor with `var(--text)` so they read correctly in both themes. | LOW | Use `fill="currentColor"` or `stroke="currentColor"` on inline SVG. Same pattern as wordmark. |
| **Icon visible at 16px** | Must be legible at small sizes — header is compact. Avoid finicky details that vanish. | LOW | Use a 24×24 viewBox with thick strokes (1.5–2px) or solid fills. GitHub Octicons-style works. |
| **Tap target ≥ 24×24 on mobile** | WCAG 2.5.5 (AAA) recommends 44×44, AA recommends 24×24. Current text button is fine; an icon-only button is at risk if styled too tight. | LOW | Pad the button so its hit box is ≥ 24×24 even if the visual SVG is 18×18. |

#### (b) Lightbox Gallery

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Click thumbnail → fullscreen modal opens** | Universal lightbox UX since Lightbox2 (2008). Users assume click = enlarge, not navigate-away. | MEDIUM | Replace current `<a href="full.webp">` pattern with `<button data-lightbox-src="...">`. Hugo template change + new JS handler. |
| **Backdrop dim + (optional) blur** | Focuses attention; signals modal-ness. Current behavior (full-page replace) loses gallery context. | LOW | `position: fixed; inset: 0; background: rgba(0,0,0,0.85);` + optional `backdrop-filter: blur(8px)`. Backdrop-filter has near-universal support in 2026 (Chromium, Firefox 103+, Safari 9+); rgba alone is fine fallback via `@supports`. |
| **Esc key closes** | WAI-ARIA dialog pattern. Users press Esc reflexively. | LOW | Single `keydown` listener while modal is open. |
| **Click outside image (on backdrop) closes** | Standard modal pattern. Click *on* image must NOT close (so users can click image to advance, or to inspect). | LOW | Distinguish backdrop click via `event.target === backdropEl`. |
| **Arrow keys navigate prev/next** | Standard image-gallery pattern (Apple Photos, macOS Preview, every lightbox library). | LOW | `keydown` switch on ArrowLeft/ArrowRight. |
| **Visible prev/next buttons** | Mobile users have no arrow keys; tap targets needed. Caret-left/caret-right SVGs in left/right edges of modal. | LOW | Hidden when only 1 photo (n/a here — 18 photos). |
| **Visible close (X) button** | Discoverability — Esc is for keyboard users; visual close is for everyone else. Top-right corner. | LOW | 24×24 X icon, `aria-label="Close gallery"`. |
| **Focus trapped inside modal** | WAI-ARIA dialog pattern. Tab cycles through modal controls (prev / image / next / close), doesn't leak to header nav. | MEDIUM | Listen for Tab; if focus would leave modal, redirect to first/last focusable element. ~15 LOC vanilla. |
| **Focus restored to triggering thumbnail on close** | WAI-ARIA dialog pattern. User pressed Esc — focus must return where they came from, not jump to top. | LOW | Save `document.activeElement` on open; `.focus()` on close. |
| **`role="dialog" aria-modal="true"`** | Screen readers announce modal vs page. Without this, blind users don't know they're in a modal. | LOW | Static attributes on the modal container. |
| **`aria-labelledby` or `aria-label` on dialog** | Screen readers need a name for the dialog ("Photo viewer", "Gallery photo 3 of 18"). | LOW | `aria-label="Gallery photo {n} of {total}"`, updated as user navigates. |
| **Body scroll locked while open** | If page scrolls under modal, users get disoriented. | LOW | `document.body.style.overflow = 'hidden'` on open, restore on close. (Save previous value.) |
| **Caption visible inside lightbox** | The whole point of adding captions is for them to be **readable** in context — at thumbnail size, captions are too small or visually noisy. Lightbox is where captions tell the 1–2-sentence story. | LOW | Caption rendered below image in modal; styled to match site typography. |
| **Aspect ratio preserved per photo** | Portraits and landscapes both look "right" — no awkward letterboxing or cropping. | LOW | Image's intrinsic dimensions drive rendered size; cap with `max-height: calc(100vh - 8rem)` + `max-width: 100%` + `object-fit: contain`. |
| **Keyboard activation of thumbnails** | Thumbnails must be `<button>` (or `<a>` with click handler) so Tab+Enter opens lightbox. | LOW | Already true with current `<a>` pattern; preserve when refactoring. |

##### Masonry Layout (Part of Gallery Refactor)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Aspect ratio preserved per thumbnail** | Reference site (tylerkarow.com/gallery) preserves originals — that's the "feel". Current Hugo template crops to 600×400 via `fill Smart`. Must change to `fit` (no crop) or keep small crops but display at native ratio. | MEDIUM | Change Hugo `image.Process` from `fill 600x400 Smart` to `fit 600x600` (caps longest edge, preserves ratio). Width/height come from processed image. |
| **Multi-column with vertical stacking (no row alignment)** | Defining feature of masonry — items stack as gaps fill, not aligned to rows. CSS Grid Level 1 forces row alignment; CSS Columns gives true masonry behavior. | MEDIUM | Use `column-count: 3; column-gap: 1rem;` + `break-inside: avoid` on each item. Pure CSS, no JS, no library. |
| **Mobile reflow to 1–2 columns** | 3-col masonry on a 375px screen = 100px-wide photos. Unreadable. | LOW | Media queries: `column-count: 1` < 600px; `column-count: 2` 600–900px; `column-count: 3` > 900px. |
| **No layout shift / CLS < 0.1** | Existing v2.0 invariant. CSS Columns + `aspect-ratio` on `<img>` (driven by intrinsic w/h attributes from Hugo) prevents shift. | LOW | Keep `width=` and `height=` attributes from Hugo `$thumb.Width/Height`. Preserves CLS guarantee. |
| **No external masonry library** | Stack constraint: vanilla JS only, no JS frameworks, no npm deps. Masonry.js, Isotope, etc. are out. | N/A | CSS Columns is the answer. (Native CSS Grid `masonry` is in Working Draft as of 2026 but Safari support is partial — not yet safe to rely on without Columns fallback.) |

##### Caption Authoring (Part of Gallery Refactor)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Caption stored next to photo, not in template** | Author-friendly: dropping a new photo + writing 1 sentence shouldn't require touching HTML/JSON outside content/. | LOW | Hugo's native pattern: `resources` array in `content/gallery/index.md` frontmatter, with `params.caption` per photo. **Recommended.** |
| **Photo discovery without explicit listing** | Currently `Resources.Match "photos/*"` auto-discovers all photos in `photos/` — adding a JPG = it appears. Don't break this. | MEDIUM | Frontmatter `resources` entries can use **glob `src` patterns** to assign params to many resources at once, OR be listed individually. For per-photo captions, individual entries are needed (no other way to match caption to file). |
| **Sensible default when caption missing** | If author drops a photo and forgets the caption, gallery shouldn't break. | LOW | Template `{{ with $photo.Params.caption }}…{{ end }}` — caption is optional. Lightbox shows photo without caption section if absent. |
| **1–2 sentences, plain text** | Stated requirement — short story, not a paragraph. | LOW | No markdown processing needed. Plain string. |

#### (c) About Redesign

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Single-column primary axis** | Reference site (tylerkarow.com/about) uses single column with alternating image/text — feels narrative, not dashboard-like. Matches Flexoki/Obsidian/Kindle "long-form reading" aesthetic. | LOW | Current About already vertically structured; keep core flow, just lighten section breaks and rebalance widths. |
| **Professional content present, not buried** | Stated requirement: balance climbing with professional background. Currently, professional content **is** present (Erste Group, Accenture, Siemens, education) but may feel rigid in tabular layout. | LOW | Restructure into prose-style sections with role highlights as soft callouts, not dense bullet lists. |
| **Climbing/personal content present, not dominant** | Stated requirement: post-Phase 7 enrichment is "climbing-heavy". Reduce climbing surface area or weave it into a single "Outside Work" section instead of competing for hero space. | LOW | Move climbing/cycling/running/cooking grid to a smaller, latter section. Keep portrait at top. |
| **Photo-text interleaving** | Reference pattern — photos punctuate prose at narrative breaks, not in a separate "gallery" block. | MEDIUM | Use existing render-image hook (already keys off title); add a 3rd variant ("inline") for photos that sit between text sections. Or use an in-between size that doesn't look like the hero or grid. |
| **Hero portrait + intro retained** | Already shipped, works, on-brand. Don't redo what's working. | LOW | Keep `about-hero` 2-col grid for top section. |
| **CV link visible** | Already present (`Download full CV (PDF)`). Critical professional element — don't lose during redesign. | LOW | Keep prominent in hero or near professional section. |
| **Responsive mobile reflow** | All multi-column/asymmetric layouts must collapse to single column < 600px. Existing pattern is the precedent. | LOW | Existing `@media (max-width: 600px)` rules for `.about-hero` and `.about-grid` already do this. New sections follow same pattern. |
| **No FOUC, no theme break** | Layout changes must preserve dark-mode contrast and Flexoki vars. Pullquote already has a documented contrast quirk (`style.css:335-337`); don't regress. | LOW | All new colors from existing CSS vars. Test both themes. |

---

### Differentiators (Nice-to-Have Signature Touches)

#### (a) Theme-Toggle Icon Button

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Subtle rotate or fade transition between sun ↔ moon** | Tiny delight; signals "something happened". 150ms — same duration as existing body color transition (`style.css:49-56`). | LOW | Wrap in `@media (prefers-reduced-motion: no-preference)`. CSS `transform: rotate(45deg) scale(0)` for outgoing icon, reverse for incoming. ~10 LOC CSS. |
| **`title` attribute as desktop tooltip** | Free hover affordance for desktop users. Mirrors `aria-label`. | LOW | One attribute per state. `title="Switch to dark mode"`. |
| **Single SVG that morphs (mask trick)** | Web.dev pattern: one SVG with sun, animate a circle mask in/out to reveal moon. More elegant than two SVGs. | MEDIUM | Higher complexity for marginal visual gain. Two-SVG-with-CSS-toggle is simpler and equally good. **Recommend deferring.** |

#### (b) Lightbox Gallery

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Photo counter "3 / 18"** | Orientation aid in long galleries. Small text in corner of modal. | LOW | Single `<span>` updated on navigate. Doubles as `aria-label` source. |
| **Preload neighbor images** | Smoother arrow-key navigation; no flash of loading. Set next + prev `<link rel="preload" as="image">` when modal opens. | LOW | ~5 LOC. Note: `image.Process` has already produced files at build time, so this is a network-priority hint. |
| **Touch swipe (left/right) on mobile** | Native mobile gesture; arrow buttons feel desktop-y. | MEDIUM | `touchstart` + `touchend` deltaX, threshold ~50px. ~20 LOC vanilla JS. **Recommend including** — gallery is photo-centric and mobile is a real use case. |
| **Caption fades in slightly after image** | Tiny stagger (50ms delay) so the photo lands first, then the story arrives. Cinematic feel without being precious. | LOW | CSS `transition-delay`. Reduced-motion guarded. |
| **Pinterest-style randomized order** | Stated requirement: "randomized masonry-like layout". Visual variety vs. deterministic-feels-curated tradeoff. | LOW | Two options: (1) Hugo-side: shuffle resources at build (`shuffle` template func) — different on every build, may confuse repeat visitors. (2) Author-side: explicit `weight` per photo in frontmatter `resources` — deterministic, author-controlled. **Recommend (2):** matches the caption authoring path (same frontmatter), gives Timo control. |

#### (c) About Redesign

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Soft rounded corners on photos (8–12px)** | Stated requirement: "more rounded feel". Current is 4–6px. Modest bump = warmer feel without breaking minimal aesthetic. | LOW | CSS `border-radius` change. ~3 lines. |
| **Soft pill-shaped role cards** | Replace dense bullet lists in Experience section with role "cards" — rounded background tint, subtle border, role title + dates + 1-line summary. Single column, full-width, stacked. | MEDIUM | Pure CSS. Tint = `var(--bg-secondary)`, border = `var(--border)`, `border-radius: 12px`. ~15 LOC CSS, content restructure in markdown. |
| **Asymmetric photo widths** | Some photos at full-content-width, some at 60–70% with text wrap or alignment offset. Breaks tabular-grid feel. | MEDIUM | Render-image hook already keys off title. Add `wide`/`narrow` title variants. ~10 LOC template, 5 LOC CSS. |
| **Hover micro-interaction on role cards** | Subtle `transform: translateY(-1px)` + slight border color shift on hover. Signals interactivity even when card itself isn't a link. (Note: if cards aren't links, hover effect may be misleading — only add if cards link to something, e.g. external company page.) | LOW | `@media (prefers-reduced-motion: no-preference)`. Conditional on whether cards link out. |
| **Visible "Outside Work" section break** | A soft heading or callout that frames climbing/cycling/cooking as personal context, not a parallel "second portfolio". Helps balance professional + personal. | LOW | Pure markdown + CSS heading style. |
| **Pullquote retained** | Existing pullquote is on-brand and surfaces a strong stat (40%→95%). Keep. Maybe relocate or restyle. | LOW | No code change needed; possibly wrap in role card. |

---

### Anti-Features (Do NOT Add — Keep It Minimal)

#### Cross-Cutting Anti-Features (All Three)

| Feature | Why Tempting | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| **A JS library/framework (Alpine, Stimulus, lit, React)** | "Easy" reactive state for modal open/close, theme, etc. | Violates stack constraint; first-paint weight; build complexity; doesn't fit Hugo flow. | Vanilla JS — every behavior here is < 50 LOC. |
| **An npm-installed lightbox (Lightbox2, GLightbox, PhotoSwipe, baguetteBox)** | Saves writing modal code; battle-tested. | Adds runtime dep; bloats first-paint (PhotoSwipe core ≈ 30 KB gz); breaks "no JS framework" stack rule; styling fights Flexoki. | Hand-rolled vanilla modal: ~80 LOC JS + ~40 LOC CSS, fully Flexoki-styled, no deps. |
| **A masonry library (Masonry.js, Isotope, Bricks.js, packery)** | Pinterest-style "true" masonry without CSS-Columns column-direction quirk. | Runtime layout JS; CLS risk before init; another runtime dep. | CSS `column-count` + `break-inside: avoid` — pure CSS, zero JS, perfect CLS. |
| **A captions/markdown library** | "Rich captions" with bold/italic/links. | Runtime markdown parsing; XSS surface; overkill for 1–2 sentences. | Plain-text caption in frontmatter; rendered as text. |
| **An animation library (anime.js, GSAP, framer-motion)** | Smooth entrance/exit transitions. | Heavy; fights minimalism. | CSS transitions + `prefers-reduced-motion`. ~5 lines per transition. |
| **An icon library (Lucide, Feather, Heroicons via CDN)** | Saves drawing SVGs. | Runtime CDN; 100 KB+ for two icons; brand inconsistency with hand-drawn wordmark. | Two hand-coded inline SVGs (sun, moon) at ~200 bytes each. Reference Octicons or Heroicons designs but **inline only the two needed paths**. |
| **A web font for the redesigned About** | More "designed" feel. | Network request; FOUT/FOIT; fights `-apple-system` system stack. | Stay on system font stack (already in `style.css:42`). Use weight + size + spacing for hierarchy. |

#### (a) Theme-Toggle Specific

| Feature | Why Tempting | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| **Emoji 🌞 / 🌙** | Free icons, no SVG drawing. | Stated milestone constraint forbids it. Emoji rendering varies by OS — looks unprofessional, may be color (clashes Flexoki). | Inline monochrome SVG with `currentColor`. |
| **A 3rd state ("auto" / "system")** | Respects OS preference more granularly. | Adds UX complexity (3-state toggle, 3 icons); current 2-state already falls back to OS preference when no localStorage value (per head IIFE). User benefit ≈ 0. | Keep 2-state. OS preference is the implicit default until first toggle. |
| **Animated full-circle rotation on toggle** | Looks fancy. | Distracting on every page load if not careful; fights minimalism. | Subtle 90° or 180° rotate, 150ms, reduced-motion guarded. |
| **Toggle as a styled `<input type="checkbox">` "switch"** | Trendy iOS-style toggle. | Fights minimal aesthetic; harder to make accessible than a `<button aria-pressed>`. Existing button pattern is correct. | Keep `<button aria-pressed>`. |

#### (b) Lightbox Gallery Specific

| Feature | Why Tempting | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| **Pinch-to-zoom inside lightbox** | Native iOS Photos behavior. | Significant code; competes with native browser pinch-zoom on the page; rarely used; mobile users can hold + "Add to Photos" if they want detail. | Don't implement. Native browser zoom on the modal image is sufficient. |
| **Slideshow auto-play** | "Cool". | Removes user agency; hostile UX; nobody asked. | Don't implement. |
| **Image rotate / download / share buttons** | "More features". | Overkill for personal gallery; download is browser native (right-click); rotate makes no sense for finished photos. | Don't implement. |
| **Random-on-every-pageload shuffle** | "Fresh feel". | Confuses repeat visitors; breaks deep links; non-deterministic gallery ordering can interact poorly with caching. | Author-controlled `weight` in frontmatter (deterministic). Author can intentionally re-order to feel "random". |
| **Caption overlaid on thumbnail (always visible)** | Quick reference. | Hides photo; adds visual noise to the masonry; competes with photo. Reference site shows captions only on detail. | Caption visible only in lightbox. Optional: alt-text only on thumbnail (already there for a11y). |
| **Caption with HTML/markdown** | Author flexibility. | Trivializes — 1–2 sentences don't need formatting. Adds parser surface. | Plain text. |
| **Per-photo individual content files** | "More structured". | Explosion of files (18+); over-architected for what's effectively a list with metadata. | Single `content/gallery/index.md` with `resources` array. |

#### (c) About Specific

| Feature | Why Tempting | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| **Resume timeline component (vertical line + dots)** | Looks "professional". | Cliché; fights minimal; CSS-heavy; doesn't add real info. | Section heading + role cards with dates. Same info, less furniture. |
| **Skill tags / pill cloud / progress bars** | Shows expertise visually. | Trite; subjective ("Python: 87%"); overcrowds page. Reference site doesn't have it. | Prose mention of skills in role descriptions; user judges from outcomes (e.g. "40%→95% routing accuracy"). |
| **Testimonials section** | Social proof. | Not asked for; not present in reference; feels like a sales page. | Don't add. |
| **Social media cluster on About** | "Connect" affordance. | Already in footer (Phase 2 social-icons). Duplicating creates link rot risk and visual repetition. | Footer is the single source of truth. |
| **Two-column "personal vs professional" split** | Visual representation of the balance request. | Reads as two unconnected lives stitched together — opposite of "balance". Reference site explicitly avoids this. | Single column with interleaved sections; let prose carry the integration. |
| **Heavy card shadows / gradients / glassmorphism** | "Modern" feel. | Fights Flexoki/Kindle/Obsidian — those aesthetics use border + tint, not depth/glow. | Subtle border + `bg-secondary` tint for cards. No shadow. |
| **Hero photo full-bleed (edge-to-edge)** | Magazine-feel. | Breaks `--max-width: 640px` reading column; introduces full-width layout exception that doesn't fit anywhere else. | Keep within content column. |

---

## Feature Dependencies

```
(a) Theme-Toggle Icon
    └──depends on──> [data-theme] attribute (existing, v2.0 Phase 4)
    └──depends on──> No-FOUC IIFE in <head> (existing, v2.0 Phase 4)
    └──depends on──> currentColor SVG pattern (existing, v2.0 Phase 05.1 — wordmark)

(b) Gallery Lightbox + Masonry + Captions
    ├──depends on──> Hugo image.Process pipeline (existing, v2.0 Phase 6)
    ├──change required──> "fill 600x400 Smart" → "fit 600x600" (preserve aspect)
    ├──depends on──> Hugo resources frontmatter pattern (Hugo native, not yet used)
    ├──depends on──> CSS Columns (built-in, no dependency)
    ├──depends on──> backdrop-filter (CSS, with rgba fallback)
    └──depends on──> Vanilla JS DOM APIs (already used for theme toggle)

(c) About Redesign
    ├──depends on──> render-image hook (existing, v2.0 Phase 7)
    ├──may extend──> render-image hook with new image-title variants (e.g., "wide", "narrow", "inline")
    ├──depends on──> CSS variables (existing Flexoki palette)
    └──depends on──> max-width: 640px content column (existing, baseof.html)

Cross-Feature:
- (a) Theme-Toggle and (b) Lightbox both use vanilla JS in <body> end script.
  Both must coexist in the existing baseof.html script block (or new partial).
- (b) Lightbox modal must respect [data-theme] colors — backdrop, caption text, controls.
  Reuses (a)'s theme infrastructure; no new theming work needed.
- (c) About may add new image-title variants in the SAME render-image hook used by gallery.
  No conflict — gallery uses Resources.Match, About uses markdown image rendering.
```

### Dependency Notes

- **Theme-toggle requires no-FOUC IIFE:** The IIFE runs *before* CSS loads and sets `:root[data-theme]`. Icon CSS keys off this attribute → no flash of wrong icon. Without the IIFE, the icon would briefly show wrong state.
- **Lightbox + masonry are technically separable but milestone-bundled:** The lightbox could be added to the current uniform-grid gallery. The masonry could be added without lightbox (each thumbnail still links to a standalone page). They're co-shipped because the milestone requirement bundles them, not because of technical dependency. Keep this in mind for phase splitting if needed.
- **Captions require lightbox:** Caption text is too small/noisy to display under masonry thumbnails (would also break the column flow). Captions are read in the lightbox. → Lightbox phase must precede or co-deliver with captions phase.
- **Aspect-ratio change in masonry breaks current `fill 600x400 Smart` template:** Switching to `fit 600x600` preserves aspect but **changes thumbnail dimensions** Hugo emits. CLS budget (< 0.1) re-validation needed.
- **About redesign does NOT depend on theme-toggle or gallery:** Pure CSS + markdown work. Can ship independently in any phase order.

---

## MVP Definition

### Launch With (v3.0 — Required Scope)

All three feature areas, table-stakes only:

#### (a) Theme-Toggle Icon (Required)

- [ ] Two inline SVGs (sun + moon, ~24×24 viewBox, `currentColor`) inside the existing `.theme-toggle` button — *button stays a `<button aria-pressed>`*
- [ ] CSS shows correct icon based on `[data-theme]` (no FOUC) — *sun in light, moon in dark*
- [ ] `aria-label` set/updated to describe target action ("Switch to dark mode" / "Switch to light mode")
- [ ] `title` attribute mirrors aria-label (desktop tooltip)
- [ ] `focus-visible` outline preserved
- [ ] Optional 150ms rotate/fade transition, reduced-motion guarded
- [ ] Tap target ≥ 24×24 (button padding)
- [ ] Header layout unchanged on desktop and mobile (no shift from text → icon)

#### (b) Gallery: Lightbox + Masonry + Captions (Required)

- [ ] Hugo template change: thumbnails become `<button>` (or `<a>` with JS handler) opening lightbox
- [ ] Hugo `image.Process` change: `fill 600x400 Smart` → `fit 600x600` (aspect preserved)
- [ ] CSS Columns masonry (1/2/3 cols at < 600px / 600–900px / > 900px)
- [ ] Frontmatter `resources` array in `content/gallery/index.md` with per-photo `params.caption` (and optional `params.weight` for ordering)
- [ ] Vanilla JS modal: open on thumbnail click, close on Esc / X / backdrop-click
- [ ] Arrow keys + on-screen prev/next buttons navigate
- [ ] Backdrop dim (rgba 0,0,0,0.85) + `backdrop-filter: blur(8px)` (with `@supports` check)
- [ ] Caption rendered below image in modal (graceful empty state if missing)
- [ ] Photo aspect ratio preserved in modal (no crop)
- [ ] Focus trapped + restored on close
- [ ] `role="dialog" aria-modal="true" aria-label="…"` on modal
- [ ] Body scroll locked while open
- [ ] Mobile touch swipe prev/next (50px deltaX threshold)

#### (c) About Redesign (Required)

- [ ] Restructure markdown: hero retained, role "cards" (soft border + tint, rounded), narrative tone for prose
- [ ] CSS: increase border-radius on photos to 8–12px
- [ ] CSS: role-card pattern (`var(--bg-secondary)` tint, `var(--border)`, `border-radius: 12px`)
- [ ] Personal/climbing content moved to single "Outside Work" section; not dominant
- [ ] At least one photo placed asymmetrically (off-center or non-grid) to break tabular feel
- [ ] All existing content preserved: hero photo, CV link, pullquote, education, certifications, all 5 photos
- [ ] Mobile reflow: all multi-element rows collapse to single column < 600px
- [ ] Both light + dark themes verified (Flexoki vars only)

### Add After Validation (v3.x — Defer)

- [ ] Single-SVG morph for theme toggle (sun-with-moon-mask trick) — *trigger: if two-SVG approach feels visually clunky*
- [ ] Photo counter ("3 / 18") in lightbox header — *trigger: user feedback on disorientation in long galleries*
- [ ] Preload next/prev image — *trigger: noticeable delay on arrow navigation in production*
- [ ] Hover micro-interactions on About role cards — *trigger: cards become links to external company pages*

### Future Consideration (v4+)

- [ ] Photo collections / tagged sub-galleries (e.g. "Climbing", "Cycling") — *defer: 18 photos doesn't need it; reassess at 50+*
- [ ] EXIF re-display in lightbox (camera, lens, location) — *defer: photos are EXIF-scrubbed by design (Phase 6), would require re-introducing metadata in a controlled way*
- [ ] Additional About variants for distinct audiences (recruiter / collaborator / friend) — *defer: scope creep; one good page > three mediocre ones*

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Theme toggle: 2-SVG icon swap | MEDIUM (visual polish, brand consistency with wordmark) | LOW (~30 LOC HTML/CSS, 5 LOC JS update) | P1 |
| Theme toggle: aria-label + title | HIGH (accessibility — only label after losing text) | LOW (~3 LOC) | P1 |
| Theme toggle: rotate transition | LOW (delight only) | LOW (~10 LOC CSS) | P2 |
| Gallery: lightbox modal core | HIGH (primary UX shift; reference-site feel) | MEDIUM (~80 LOC JS, ~40 LOC CSS) | P1 |
| Gallery: focus trap + a11y | HIGH (modal correctness; inclusive UX) | MEDIUM (~15 LOC JS) | P1 |
| Gallery: masonry via CSS columns | HIGH (defining visual change from grid) | LOW (~10 LOC CSS + 1-line Hugo template change) | P1 |
| Gallery: per-photo captions in frontmatter | HIGH (stated requirement, story-telling layer) | LOW (~5 LOC template + content edits to add captions) | P1 |
| Gallery: touch swipe | HIGH on mobile | LOW (~20 LOC JS) | P1 |
| Gallery: photo counter | MEDIUM | LOW | P2 |
| Gallery: preload neighbors | LOW (UX feels same with WebP at q75) | LOW | P3 |
| About: role cards + rounded photos | HIGH (delivers "more rounded, dynamic" requirement) | MEDIUM (~15 LOC CSS, content restructure) | P1 |
| About: balance climbing/professional | HIGH (stated requirement) | LOW (content rewrite, no code) | P1 |
| About: asymmetric photo widths | MEDIUM (delivers "dynamic" feel) | MEDIUM (render-image hook variant + CSS) | P2 |
| About: hover micro-interaction | LOW (cards likely not links) | LOW | P3 |

**Priority key:** P1 = required for v3.0 launch; P2 = should have, ship if time; P3 = defer to v3.x or later.

---

## Caption Authoring Path — Recommended

**Recommendation:** Hugo's native `resources` frontmatter array in `content/gallery/index.md`, with `params.caption` (and optional `params.weight` for deterministic ordering).

**Why this over alternatives:**

| Path | Pros | Cons | Verdict |
|------|------|------|---------|
| **`resources` in `index.md` frontmatter** (recommended) | Hugo native; one file to edit; works with existing page-bundle resource model; supports glob `src` patterns; per-photo `params` extensible (caption today, alt-text tomorrow) | Manual entry per photo (no auto-discovery for params) | ✓ Recommended |
| Per-photo individual `.md` files (one per photo) | Strong file-locality; fits leaf-bundle model | 18+ tiny files; over-architected; resources auto-discovery still requires glue | ✗ Over-engineered |
| Sidecar YAML/JSON file (`captions.yml`) | Decoupled from Hugo content model; could be edited as plain data | Two-source-of-truth (file location + caption file); not a Hugo idiom; template needs custom data load | ✗ Non-idiomatic |
| EXIF / IPTC caption embedded in image | Travels with the file | Photos are EXIF-scrubbed (Phase 6 invariant) — adding metadata back contradicts that decision | ✗ Conflicts with v2.0 invariant |
| Caption as filename suffix (e.g. `IMG_1234--my-caption.jpg`) | Single source of truth | Filenames become unwieldy; URL-encoded paths; no support for multi-sentence | ✗ Hostile authoring |

**Authoring flow for a new photo (one-step + one-edit, recommended path):**

1. Drop new image at `content/gallery/photos/<filename>.jpg`
2. Open `content/gallery/index.md`, add to `resources:` array:
   ```yaml
   - src: 'photos/<filename>.jpg'
     params:
       caption: 'One or two sentences telling the story of this photo.'
       weight: 19  # optional; controls position in gallery
   ```
3. Commit. Hugo build picks it up. No template edits.

Photos without `resources` entries still appear (via `Resources.Match "photos/*"` in template), just without captions. Author can add resources entries lazily when ready to caption — gallery never breaks.

---

## Comparison: Reference Site (tylerkarow.com) vs This Site

| Feature | Tyler Karow | This Site (recommended v3.0) |
|---------|-------------|------------------------------|
| Gallery layout | Masonry, aspect-preserved | Same (CSS Columns) |
| Caption position | Below thumbnail AND in lightbox | Lightbox only (less visual noise in grid; matches Flexoki minimalism) |
| Lightbox | Yes, with prev/next/close | Same |
| Backdrop | Dim, no obvious blur | Dim + subtle blur (small differentiator; modern feel) |
| About layout | Single column, interleaved photos, minimal | Same direction; slightly more structure via role cards (we have specific professional roles to surface) |
| About styling | Unornamented | Soft tint cards + rounded corners (slightly warmer; matches "more dynamic and rounded" requirement) |
| Theme toggle | (Tyler's site has no toggle) | Sun/moon icon (this is unique to us) |

---

## Sources

### Reference Sites (Direct Fetch)

- [tylerkarow.com/gallery — masonry + lightbox reference](http://tylerkarow.com/gallery) — confirmed: aspect-ratio preserved, captions visible in both grid and lightbox, dimmed backdrop, prev/next/close controls
- [tylerkarow.com/about — single-column interleaved layout reference](https://www.tylerkarow.com/about) — confirmed: single column, alternating image/text, no pill cards or shadows, professional+personal woven not separated

### Theme-Toggle UX (HIGH confidence)

- [web.dev — Building a theme switch component (Adam Argyle)](https://web.dev/articles/building/a-theme-switch-component) — sun-as-current-state, moon-as-current-state convention; SVG mask morph technique
- [web.dev — Theme switch pattern](https://web.dev/patterns/theming/theme-switch) — accessibility patterns
- [DEV — An Accessible Dark Mode Toggle](https://dev.to/abbeyperini/an-accessible-dark-mode-toggle-in-react-aop) — aria-label describes target action, not current state
- [whitep4nth3r — Best light/dark mode toggle in JavaScript](https://dev.to/whitep4nth3r/the-best-lightdark-mode-theme-toggle-in-javascript-368f) — `aria-pressed` + sun/moon pattern

### Lightbox / Modal Accessibility (HIGH confidence)

- [The A11Y Collective — Mastering Accessible Modals with ARIA and Keyboard Navigation](https://www.a11y-collective.com/blog/modal-accessibility/) — `role="dialog"`, `aria-modal="true"`, focus management
- [UXPin — Building Accessible Modals with Focus Traps](https://www.uxpin.com/studio/blog/how-to-build-accessible-modals-with-focus-traps/) — focus-trap pattern, restore-on-close
- [adropincalm — Modal focus trap in vanilla JavaScript](https://adropincalm.com/blog/modal-focus-trap-in-javascript-and-react/) — vanilla JS reference implementation

### Masonry Layout (HIGH confidence)

- [CSS-Tricks — CSS Masonry & CSS Grid](https://css-tricks.com/css-masonry-css-grid/) — column-count vs grid-rows comparison
- [MDN — Masonry layout (CSS Grid Level 3 — Working Draft)](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout/Masonry_layout) — native CSS masonry support is partial as of 2026, Columns is the safe path
- [Piccalilli — A simple masonry-like composable layout](https://piccalil.li/blog/a-simple-masonry-like-composable-layout/) — CSS Columns approach with `break-inside: avoid`

### Backdrop Filter (HIGH confidence)

- [MDN — backdrop-filter](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter) — wide browser support in 2026 (Chromium, Firefox 103+, Safari 9+)
- [CSS-Tricks — backdrop-filter](https://css-tricks.com/almanac/properties/b/backdrop-filter/) — `@supports` fallback pattern

### Hugo Patterns (HIGH confidence)

- [Hugo docs — Page resources](https://gohugo.io/content-management/page-resources/) — `resources` frontmatter array, `params`, glob `src`
- [Regis Philibert — Hugo Page Resources](https://www.regisphilibert.com/blog/2018/01/hugo-page-resources-and-how-to-use-them/) — patterns for accessing `Params.caption`
- [Hugo discourse — Page resource metadata](https://discourse.gohugo.io/t/page-resource-metadata/51610) — caption pattern via `resources` array

---
*Feature research for: v3.0 Design Update (theme-toggle icon, gallery lightbox + masonry + captions, About redesign)*
*Researched: 2026-05-01*

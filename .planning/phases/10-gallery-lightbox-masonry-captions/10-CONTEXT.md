# Phase 10: GALLERY — Lightbox + Masonry + Captions - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning
**Mode:** `--auto` (Claude picked recommended defaults across all gray areas; single-pass)

<domain>
## Phase Boundary

Replace the v2.0 uniform CSS-Grid + standalone-image-page navigation gallery with three coordinated changes within the existing `content/gallery/` page bundle and `themes/minimal/layouts/gallery/single.html` precedent:

1. **Authoring path** — author per-photo `params.caption`, `params.alt`, `params.weight` via Hugo `[[resources]]` blocks in `content/gallery/index.md` (single source of truth, no sidecar `.md` files).
2. **Layout** — CSS `column-count` masonry preserving each photo's natural aspect ratio (3 columns ≥900 px, 2 at 600–900 px, 1 <600 px), driven by Hugo `Resize "600x webp q75"` (width-only) thumbs.
3. **Lightbox** — native `<dialog>` modal with `showModal()`, `::backdrop` blurred backdrop (rgba fallback), keyboard nav (Esc / ←/→ / Tab focus-trap), touch swipe (50 px deltaX), focus restoration, manual body scroll lock, served from a new page-scoped `themes/minimal/static/js/lightbox.js`.

In scope: the gallery list page (`/gallery/`), the 18 existing photos in `content/gallery/photos/`, `gallery/single.html`, `style.css` `/* === Gallery === */` and new `/* === Gallery Lightbox === */` blocks, `content/gallery/index.md` frontmatter, the new `lightbox.js` file, and the EXIF CI gate carry-forward.

Out of scope (deferred per REQUIREMENTS.md "Future Requirements"): photo counter overlay (`3 / 18`), `<link rel="preload">` for next/prev images, masonry shuffle script, JS framework, lightbox NPM package, CSS Grid `masonry`, Hugo `collections.Shuffle`, EXIF extraction at build time, web fonts, animations beyond ≤150 ms transitions. The 18 existing EXIF-scrubbed photos are reused as-is — no new content authoring beyond captions/alt/weight.

</domain>

<decisions>
## Implementation Decisions

### Authoring Schema (REQ GALLERY-01)
- **D-01 [auto]:** **Per-photo `[[resources]]` blocks in `content/gallery/index.md`** — one TOML array entry per photo with `src = "photos/<filename>"` (exact filename match, case-preserved), `name = "photos/<filename>"`, and `params = { caption = "…", alt = "…", weight = N }`. Listed individually (not glob `src = "photos/*"`) because `caption`, `alt`, and `weight` are unique per photo. **Rejected:** sidecar `.md` per photo (ARCHITECTURE alternative) — chosen-against because it splits caption authoring across 18 files instead of one and the locked decision in REQUIREMENTS.md § Locked Decisions explicitly names `[[resources]]` frontmatter as the authoring model. **Rejected:** YAML data file at `data/gallery.yaml` — divorces caption from photo, breaks page-bundle co-location.

### Caption Optionality (REQ GALLERY-04)
- **D-02 [auto]:** **Captions are optional with graceful empty rendering** — template wraps with `{{ with $photo.Params.caption }}<figcaption class="gallery-lightbox-caption">{{ . }}</figcaption>{{ end }}`. A photo without `params.caption` ships zero caption DOM in the lightbox. REQUIREMENTS-04 explicitly states "gracefully empty if a photo has no caption"; ROADMAP success criterion #3 confirms. **Rejected:** Pitfall 6's `errorf` build-fail on missing caption — would block deploy on a half-authored frontmatter, contradicts REQ-04 graceful-empty contract. The author convention is "ship a caption when you have one"; the build does not enforce.

### Per-Photo Alt Text (Pitfall 12)
- **D-03 [auto]:** **`params.alt` is REQUIRED** for accessibility — the lightbox image is primary content of a `<dialog role="dialog">`. Author convention: every `[[resources]]` entry MUST include `alt = "…"`. The thumbnail `<img>` keeps `alt=""` (decorative, the wrapping `<a aria-label="Open photo …">` provides the accessible name); the lightbox `<img>` swap reads `alt="{{ $photo.Params.alt }}"`. The build does not fail on missing alt, but a verification grep step asserts every `[[resources]]` block has both `alt` and (if appropriate) `caption`.

### Gallery Ordering (REQ GALLERY-03 + Locked Decisions)
- **D-04 [auto]:** **Author-controlled deterministic order via `params.weight`** — locked by REQUIREMENTS.md § Locked Decisions ("Gallery ordering model: Author-controlled deterministic order via `params.weight` in `[[resources]]` frontmatter. Not Hugo build-time shuffle, not client-side random."). Template iteration: `{{ range (sort (.Resources.Match "photos/*") "Params.weight") }}`. Photos without `weight` sort alphabetically (Hugo default) but every shipped photo MUST have a `weight` value to satisfy the deterministic-order invariant. **Rejected:** Hugo `collections.Shuffle` (non-deterministic across builds, gohugo.io issue #5641). **Rejected:** client-side shuffle (causes layout reorder after paint, breaks deep-link expectations). **Rejected:** filename-alphabetical (would be deterministic but loses author control).

### Thumb Image Processing (REQ GALLERY-02 + Pitfall 4)
- **D-05 [auto]:** **`$photo.Process "Resize 600x webp q75"`** (width-only, height proportional) — replaces the v2.0 `Process "fill 600x400 Smart webp q75"` which crops to 3:2. Width-only Resize preserves each photo's intrinsic aspect ratio (REQ-02 requirement: "no uniform-grid crops, no `fill 600x400`"). Hugo emits `width="600"` + `height="N"` per photo from the processed image; CSS `aspect-ratio` reservation is implicit through these attributes (modern browsers since 2024). Pairs with `display: block; width: 100%; height: auto;` on `.gallery-img` (existing rule at style.css:334-339, kept verbatim).

### Full Image Processing (REQ GALLERY-08 + Pitfall 11)
- **D-06 [auto]:** **Keep existing `$photo.Process "fit 1200x1200 webp q78"`** for the lightbox-served full image — exact same directive as v2.0 (gallery/single.html:11). `fit` (not `fill`) preserves aspect ratio with the longest edge ≤ 1200 px. Quality stays at q78 (Pitfall 11: do NOT bump to q82, which appears as a quality drift in milestone context — code is canonical at q78). No `<link rel="preload">` for fulls (deferred GALLERY-FUT-02).

### Masonry Layout (REQ GALLERY-02)
- **D-07 [auto]:** **CSS `column-count` masonry**, replacing the v2.0 uniform CSS-Grid (`grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` at style.css:316-321). Breakpoints:
  - Default (≥900 px): `column-count: 3; column-gap: 1rem;`
  - 600–900 px: `column-count: 2;` (new media query block at the appropriate position in style.css)
  - <600 px: `column-count: 1;` (added to the existing `@media (max-width: 600px)` block)
  - `.gallery-item { break-inside: avoid; margin-bottom: 1rem; }` (vertical rhythm; column-count flows top-to-bottom-then-next-column)
  - `display: grid` rule on `.gallery-grid` (style.css:316-321) is **deleted** and replaced with `column-count` rules under the same `/* === Gallery === */` section comment.
  
  **Rejected:** CSS Grid Level 3 `grid-template-rows: masonry` — Safari-only in 2026, blocked from production per REQUIREMENTS Out of Scope. **Rejected:** JS-driven Pinterest-style masonry — adds runtime layout JS, CLS risk before init, violates "no JS framework" stack rule.
  
  **Pitfall 4 acknowledgment:** the architecture brief at PITFALLS.md:107 advises against `column-count` for screen-reader reading order. ROADMAP and REQUIREMENTS lock `column-count` regardless because (a) gallery photos are visual content with no semantic reading order to preserve, (b) every photo is reachable via Tab in DOM order which equals `weight` order — independent of visual column flow, (c) CSS Grid masonry is unshippable in 2026. Author/visual ordering and screen-reader/keyboard ordering both come from `weight`; visual column flow is acceptable to diverge.

### Lightbox Mechanism (REQ GALLERY-05, GALLERY-06)
- **D-08 [auto]:** **Native `<dialog>` element + `dialog.showModal()`** — browser-native focus trap (free), Esc-to-close (free), top-layer rendering (free), `aria-modal="true"` (free), focus restoration to trigger button on `dialog.close()` (free). Locked by REQUIREMENTS-05 + STACK research. Browser support: Chrome 37+, Firefox 98+, Safari 15.4+, Edge 79+ — all fully shipped in 2026. **Rejected:** DIV-based modal with class-toggle (must reimplement focus trap, Esc, aria-modal, top-layer manually). **Rejected:** Hugo-native solution (none exists at the modal layer).
- **D-09 [auto]:** **One `<dialog>` element in the DOM, mutated in place per click** — single `<dialog id="gallery-lightbox">` emitted at the bottom of `gallery/single.html`'s `{{ define "main" }}` block, after the `.gallery-grid`. Per click: JS sets the dialog's `<img src>` / `<img alt>` / `<figcaption>` text to the clicked photo's full-image URL / alt / caption, then calls `dialog.showModal()`. 18 photos = 1 dialog DOM, not 18. Per STACK research line 116.
- **D-10 [auto]:** **Backdrop click closes** via `dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); })` — one-line handler. Distinguishes click-on-backdrop (closes) from click-on-image (doesn't close). The X button (`<button class="gallery-lightbox-close">`) is the explicit visual close affordance for touch users. Esc key closes natively via `<dialog>`.

### Body Scroll Lock (Pitfall 8)
- **D-11 [auto]:** **Manual body scroll lock** — `<dialog>` does NOT lock body scroll natively. JS sets `document.body.style.overflow = 'hidden'` on dialog open and restores the previous value on close (`document.body.style.overflow = ''`). Required to satisfy REQUIREMENTS-05 ("body scroll-locked while open"). Locked by Pitfall 8 explicit gate.

### Backdrop Strategy (REQ GALLERY-05 + Pitfall 10)
- **D-12 [auto]:** **`backdrop-filter: blur(12px)` with rgba fallback via `@supports`** — locked by ROADMAP success criterion #3 ("blurred backdrop (`backdrop-filter: blur(12px)` with rgba fallback)") and REQUIREMENTS-05. CSS:
  ```css
  /* Default fallback for browsers without backdrop-filter */
  body.page-gallery dialog#gallery-lightbox::backdrop {
    background: rgba(16, 15, 15, 0.85);
  }
  /* Progressive enhancement when supported */
  @supports (backdrop-filter: blur(12px)) {
    body.page-gallery dialog#gallery-lightbox::backdrop {
      background: rgba(16, 15, 15, 0.6);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }
  }
  ```
  Pitfall 10 perf concern (GPU cost on low-end devices) is acknowledged but ROADMAP requirement is explicit. Mitigation: blur only ships when `@supports` matches, fallback always provided. **Note:** `-webkit-` prefix retained for Safari <17 (Safari 17 ships unprefixed `backdrop-filter`; older Safari requires prefix per caniuse).
- **D-13 [auto]:** **Single backdrop background colour** — `rgba(16, 15, 15, 0.85)` matches `--bg` dark hex; reads correctly in both themes (dark scrim works for light pages too because the photo dominates). No theme-specific override needed.

### Lightbox JS File (REQ GALLERY-05, GALLERY-06, GALLERY-07)
- **D-14 [auto]:** **New file `themes/minimal/static/js/lightbox.js`**, ~80 LOC IIFE pattern matching the `baseof.html` end-of-body chrome IIFE shape. **Loaded from `gallery/single.html`** at the bottom of the `{{ define "main" }}` block via `<script src="{{ "js/lightbox.js" | absURL }}" defer></script>` — page-scoped, NOT loaded from `baseof.html`. Reasoning: ARCHITECTURE risk callout — `baseof.html` would ship the JS to every page. Page-scoped load keeps blog/about/home pages JS-free. Locked by ARCHITECTURE recommendation.
- **D-15 [auto]:** **IIFE structure** —
  1. Bind click on every `<a class="gallery-item">` → `e.preventDefault()`, read `a.href` (the full-image URL — Pitfall 7), read `a.dataset.caption` and `a.dataset.alt`, swap into `dialog#gallery-lightbox`, call `dialog.showModal()`.
  2. Track active index by reading the `<a>` element's index in the parent `.gallery-grid` (`Array.from(grid.children).indexOf(a)`) — DOM-walk siblings for prev/next (D-19).
  3. Bind `keydown` on dialog: Arrow Left → prev, Arrow Right → next.
  4. Bind close button click → `dialog.close()`.
  5. Bind backdrop click (D-10).
  6. Bind `touchstart` + `touchend` on dialog: compute `deltaX`, threshold 50 px (REQUIREMENTS-07) → prev / next.
  7. On `dialog` open: store `document.body.style.overflow`, set to `'hidden'` (D-11).
  8. On `dialog.close` event: restore body overflow.
  9. No image preloading (Pitfall 11; deferred GALLERY-FUT-02).

### Prev/Next Data Source (REQ GALLERY-06)
- **D-16 [auto]:** **DOM-walk siblings** — JS reads the active `<a>` element's index in `.gallery-grid`, navigates `prev = grid.children[idx - 1]`, `next = grid.children[idx + 1]`, wraps modulo `grid.children.length`. The DOM order IS the gallery order (already sorted by `weight` in the template). No JS array, no `data-index` attributes. Simpler than data-array; updates automatically if photos re-sort. Locked by ARCHITECTURE preference for minimal data duplication.

### Lightbox Aria Label Updates (REQ GALLERY-06)
- **D-17 [auto]:** **`<dialog aria-label="Photo {n} of {total}">`** updated each navigation — JS sets `dialog.setAttribute('aria-label', \`Photo ${n} of ${total}\`)` on open and on each prev/next. The `aria-label` is the dialog's accessible name for screen-reader announcement on focus. **Rejected:** `aria-labelledby` pointing to the figcaption — figcaption is sometimes empty (D-02 graceful empty), would leave dialog unnamed.

### Touch Swipe (REQ GALLERY-07)
- **D-18 [auto]:** **50 px deltaX threshold** — locked by REQUIREMENTS-07 + ROADMAP success #5. Vertical swipe (deltaY > deltaX) is ignored (preserves native page-scroll-during-modal? No — body scroll is locked. Vertical swipe is a no-op). ~20 LOC inline in lightbox.js.

### Progressive Enhancement (Pitfall 7)
- **D-19 [auto]:** **Keep semantic `<a class="gallery-item" href="$full.RelPermalink">` wrapper** — JS-disabled users get the full image as a separate page navigation (current v2.0 behavior). The lightbox JS calls `e.preventDefault()` and reads `a.href` for the full URL. Existing v2.0 markup at gallery/single.html:12-23 stays in place; only the masonry CSS replacement and the new `data-caption` / `data-alt` data-attributes change. Locked by Pitfall 7 explicit pattern.

### Lightbox Markup (REQ GALLERY-05, GALLERY-06)
- **D-20 [auto]:** **Lightbox DOM** at the bottom of `gallery/single.html`'s `{{ define "main" }}` block:
  ```html
  <dialog id="gallery-lightbox" aria-label="Photo viewer">
    <button type="button" class="gallery-lightbox-close" aria-label="Close gallery">…X SVG…</button>
    <button type="button" class="gallery-lightbox-prev" aria-label="Previous photo">…chevron-left SVG…</button>
    <img class="gallery-lightbox-img" src="" alt="" />
    <figcaption class="gallery-lightbox-caption"></figcaption>
    <button type="button" class="gallery-lightbox-next" aria-label="Next photo">…chevron-right SVG…</button>
  </dialog>
  ```
  Three button + img + figcaption. Native `<dialog>` provides the structural shell; CSS positions the buttons absolutely within. Buttons sit above the backdrop blur. SVG icons follow the Lucide visual language already in `partials/footer.html` (24×24, 2px stroke, currentColor) — Pitfall 3 — no hard-coded fills. Aria-labels describe the *target action* on the buttons (Pitfall 21 carry-forward); aria-label on the dialog gives the screen-reader name (D-17).

### CSS Scoping (Pitfall 17)
- **D-21 [auto]:** **All new lightbox/masonry CSS scoped under `body.page-gallery`** — class names use `.gallery-` prefix (`.gallery-lightbox-img`, `.gallery-lightbox-caption`, `.gallery-lightbox-close`, `.gallery-lightbox-prev`, `.gallery-lightbox-next`). Forbidden generic names: `.lightbox`, `.modal`, `.close`, `.prev`, `.next`. Existing `.gallery-grid`, `.gallery-item`, `.gallery-img` keep their names but their rules move into `body.page-gallery .gallery-grid` etc. (some already are; verify all are scoped after the rewrite). Single `style.css` file; new section comments `/* === Gallery — Masonry === */` and `/* === Gallery — Lightbox === */` under the existing `/* === Gallery === */` header.

### Reduced Motion (Pitfall 9)
- **D-22 [auto]:** **All new transitions wrapped in `@media (prefers-reduced-motion: no-preference)`** — backdrop fade-in / `<dialog>` open transition / button hover. Same pattern as `style.css:49-56` body color transition. Reduced-motion users see instant open/close with no fade, no scale. Locked by Pitfall 9 + REQUIREMENTS § Out of Scope ("Animation libraries / motion frameworks — keep transitions to ≤ 150 ms CSS, gated behind prefers-reduced-motion: no-preference").

### EXIF Gate (REQ GALLERY-09)
- **D-23 [auto]:** **Two-layer gate, both carried forward and one upgraded to CI:**
  1. **Existing layer (kept):** `[imaging.exif] disableLatLong = true` in `hugo.toml:34-36` — Hugo strips lat/lng on processed images. Already in place; verify retained.
  2. **New CI layer:** add a step to `.github/workflows/deploy.yml` after the Hugo build that runs `exiftool` against `content/gallery/photos/*.{jpg,JPG,jpeg,JPEG,JPG}` and fails the build if `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, or `SerialNumber` fields appear. Single bash step using `apt-get install -y libimage-exiftool-perl` on `ubuntu-latest`. ~10 LOC added to deploy.yml.
  
  **Rejected:** standalone `scripts/scrub_exif.py` — REQUIREMENTS-09 specifies "CI gate enforced as in v2.0 Phase 6"; v2.0's gate was source-side scrub via author convention, but REQ-09 + ROADMAP success #8 require the gate to "enforce this on every build" — that is CI by definition. Upgrading to a CI step closes this gap. **Rejected:** running exiftool in the source pre-commit hook — pre-commit hooks aren't enforced for CI builds; CI is the right surface.
  
  **Author convention preserved:** Photos still arrive in-repo EXIF-scrubbed (v2.0 invariant). The CI gate is defensive — catches the regression where a new photo is added without scrubbing.

### CLS Verification (REQ GALLERY-08)
- **D-24 [auto]:** **CLS gate enforced via `<img width=… height=…>` attributes from Hugo `image.Process`** — each `<img>` ships intrinsic dims from Hugo's processed image (`width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"`). Modern browsers translate these into `aspect-ratio` reservation, preventing layout shift as images load. Verification gate: Lighthouse on the deployed `/gallery/` reports CLS < 0.1 (per ROADMAP success criterion #6). Mobile + desktop both checked. Mark as a HUMAN-UAT item (post-deploy walkthrough) if Lighthouse can't be run automatically.

### Dialog Sizing & Aspect Ratio (REQ GALLERY-08, REQ GALLERY-05)
- **D-25 [auto]:** **`.gallery-lightbox-img { max-width: 100%; max-height: calc(100vh - 8rem); object-fit: contain; }`** — preserves aspect ratio per photo, caps at viewport. Caption sits below image. Both dimensions constrained to keep modal within viewport on any device. No `width: 100%` (would distort).

### Phase Sub-Task Order (ARCHITECTURE risk callouts)
- **D-26 [auto]:** **Three-step internal ordering, planner SHOULD respect:**
  1. **Wave 1 — Data:** Author all 18 `[[resources]]` entries in `content/gallery/index.md` with `caption` (where author-provided), `alt`, `weight`. Pure data; no UX impact. Single commit.
  2. **Wave 2 — Template + CSS:** Update `gallery/single.html` (sort by weight, switch to `Resize 600x`, emit `data-caption` / `data-alt` attrs, add `<dialog>` markup, defer-load `lightbox.js`); rewrite `style.css` `/* === Gallery === */` block (delete grid rules, add column-count masonry rules, add lightbox rules); update render-image hook ONLY if a new arm is needed (likely not — the gallery doesn't use markdown-driven images, photos come from `Resources.Match`).
  3. **Wave 3 — JS:** Author `themes/minimal/static/js/lightbox.js` (~80 LOC IIFE per D-15). After Wave 2 ships the data-attrs and dialog markup, the JS has something to read.
  4. **Wave 4 — CI gate:** Add the exiftool step to `.github/workflows/deploy.yml`. Independent of Waves 1-3; can ship in parallel with any of them. Planner's call on placement.
  5. **Wave 5 — Verification:** Run automated gates (`hugo` build success, `exiftool` returns no fields, page renders, masonry breakpoints visible at 320/600/900/1200 px viewports), write `10-HUMAN-UAT.md` for post-deploy browser walkthrough (Lighthouse CLS, focus trap, touch swipe on real device, screen reader announce, dark/light theme dialog backdrop, EXIF check on deployed `.webp`).

### Plan Granularity Hint (Phase Boundary, Goal)
- **D-27 [auto]:** **Suggested plan count: 3** — `10-01 Authoring + Frontmatter`, `10-02 Template + CSS + EXIF CI`, `10-03 Lightbox JS + Verification + HUMAN-UAT`. Final count is the planner's call, but coarse-grain favors 3 plans (Phase 9 used 3, similar size). 4 is acceptable if planner separates EXIF CI from Wave 2.

### Existing Markup to Preserve
- **D-28 [auto]:** **Keep `<a class="gallery-item" href="{{ $full.RelPermalink }}" aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size">`** wrapper from gallery/single.html:12-14 — ARIA label, position semantics, progressive enhancement all preserved (D-19). Add: `data-caption="{{ $photo.Params.caption }}"` and `data-alt="{{ $photo.Params.alt }}"` for the lightbox JS to read. Existing `loading` / `fetchpriority` / `decoding` attributes (lines 19-21) stay.

### Claude's Discretion (handed to planner)
- Exact `gap` values for masonry column-gap (`1rem` default, `0.75rem` mobile? — planner picks visually).
- Exact `padding` / `border-radius` of dialog buttons — within Flexoki / Pitfall 16 envelope (no shadows, soft 8–12 px radius via `var(--radius-soft)` if appropriate).
- Whether to include a hover state on buttons — within `prefers-reduced-motion: no-preference` (D-22).
- CSS authoring order inside the new section block (one big rule vs split per element).
- Whether 3 plans or 4 (D-27 default vs split EXIF CI).
- Exact LOC of `lightbox.js` (~80 LOC budget).
- Whether to include touchcancel handling alongside touchstart/touchend (defensive UX).
- Order of `[[resources]]` entries in `index.md` is by `weight` value the author chooses; planner doesn't pre-curate weights — author iterates after first build.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope & Requirements (Project)
- `.planning/REQUIREMENTS.md` § GALLERY — Lightbox + Masonry + Captions — locked requirements GALLERY-01 through GALLERY-09 (lines 22-32 of REQUIREMENTS.md)
- `.planning/REQUIREMENTS.md` § Locked Decisions — gallery ordering = `params.weight` deterministic (lines 11-15)
- `.planning/REQUIREMENTS.md` § Out of Scope — no JS framework, no lightbox/masonry NPM, no CSS Grid Level 3 `masonry`, no `collections.Shuffle`, no client-side random, no EXIF extraction at build time, no animation libraries
- `.planning/ROADMAP.md` § Phase 10: GALLERY — Lightbox + Masonry + Captions — goal + 8 deployed-site success criteria
- `.planning/PROJECT.md` § Constraints — Flexoki, vanilla JS only, no flash on load, accessible, prefers-reduced-motion, ≤ 2 MB first-paint

### Research (Milestone-Level, Phase 10 Slice)
- `.planning/research/SUMMARY.md` § GALLERY — Lightbox + Masonry + Captions — must-haves + defer list (HIGH confidence)
- `.planning/research/SUMMARY.md` § Conflict Resolution: Gallery Ordering — author-controlled `params.weight` recommendation (resolved + locked)
- `.planning/research/SUMMARY.md` § Phase 3: GALLERY — phase-targeted notes, Pitfalls to avoid (P04, P05, P06, P07, P08, P09, P10, P11, P12, P13)
- `.planning/research/STACK.md` § Lightbox + Masonry Gallery — native `<dialog>`, CSS column-count, `[[resources]]` frontmatter, no new deps
- `.planning/research/STACK.md` § Lightbox: native `<dialog>` element decision table
- `.planning/research/FEATURES.md` § (b) Lightbox Gallery — table-stakes + masonry feature table + caption-authoring feature table
- `.planning/research/FEATURES.md` § Differentiators (Gallery) — touch swipe (recommended include), photo counter (defer), preload (defer), Pinterest-style randomized order (resolved to `weight`)
- `.planning/research/FEATURES.md` § Anti-Features — explicit list of forbidden libraries (PhotoSwipe, GLightbox, Tobii, Masonry.js, focus-trap, Lucide-as-package)
- `.planning/research/PITFALLS.md` Pitfalls 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 — CLS, ordering nondeterminism, caption drift, lazy-load conflict, focus trap/Esc/scroll lock, reduced motion, backdrop perf, page weight, alt text, EXIF reintroduction
- `.planning/research/ARCHITECTURE.md` § (b) Lightbox + randomized masonry gallery — file-modification matrix (gallery/single.html, lightbox.js, style.css, content/gallery/index.md)
- `.planning/research/ARCHITECTURE.md` § Suggested build order — internal sub-ordering (caption sidecars/frontmatter → template → JS); risk callouts (build determinism, caption-data-precedes-JS, column-count vs CSS Grid masonry, `build.publishResources: false`)

### Codebase Maps (Read During Scout)
- `.planning/codebase/CONVENTIONS.md` — single-CSS-file rule, BEM-like naming, kebab-case CSS custom properties, `body.page-{type}` scoping pattern, vanilla JS only, IIFE pattern, image filename casing rule
- `.planning/codebase/STRUCTURE.md` — Hugo theme layout layering; precedent for `layouts/{type}/single.html` (gallery already exists at `themes/minimal/layouts/gallery/single.html`)
- `.planning/codebase/STACK.md` — confirms no Node/npm; Hugo `image.Process` page-bundle pipeline already in use at q75/q78

### Codebase Files (To Be Modified or Created)
- `content/gallery/index.md` — **MODIFY**: add `[[resources]]` blocks for all 18 photos with `caption` (where author-provided), `alt`, `weight` (currently 7 lines: title + type + build.publishResources frontmatter only)
- `themes/minimal/layouts/gallery/single.html` — **MODIFY**: sort `Resources.Match` by `Params.weight`, change thumb processing from `fill 600x400 Smart webp q75` to `Resize 600x webp q75`, emit `data-caption` and `data-alt` data-attributes on `<a class="gallery-item">`, add `<dialog id="gallery-lightbox">` markup at bottom of `{{ define "main" }}`, add `<script src="js/lightbox.js" defer>` at bottom (currently 28 lines)
- `themes/minimal/static/js/lightbox.js` — **NEW** ~80 LOC IIFE (Section D-14, D-15)
- `themes/minimal/static/css/style.css` — **MODIFY**:
  - `/* === Gallery === */` section (lines 311-339): replace `display: grid` rules with `column-count` masonry rules; rewrite `.gallery-item` for `break-inside: avoid` + vertical rhythm; add new `/* === Gallery — Masonry === */` and `/* === Gallery — Lightbox === */` sub-comments
  - `/* === Gallery Lightbox === */` block (NEW, ~50-60 LOC): `dialog#gallery-lightbox` rules, `::backdrop` rules with `@supports (backdrop-filter)` progressive enhancement, button positioning, image sizing (D-25), figcaption styling, prefers-reduced-motion-gated transitions
  - Mobile breakpoint additions: column-count: 1 in existing `@media (max-width: 600px)` block; add new `@media (min-width: 600px) and (max-width: 899px) { ... column-count: 2 ... }` if not already present
  - **Do NOT touch:** `.page-content img` rule at line 305-309 (site-wide; out of phase scope), body transition at 49-56, About rules, blog list rules
- `.github/workflows/deploy.yml` — **MODIFY**: add a build-step that installs `exiftool` and asserts no GPS/Make/Model/Serial fields in `content/gallery/photos/*.{jpg,JPG,jpeg,JPEG}` (D-23 layer 2)

### Codebase Files (Read-Only Reference / Precedent)
- `themes/minimal/layouts/_default/baseof.html` line 26 — `body.page-{Type}` class auto-emits (`page-gallery` activates automatically; no template change needed)
- `themes/minimal/layouts/_default/baseof.html` lines 34-58 — chrome IIFE pattern (precedent for `lightbox.js` IIFE shape)
- `themes/minimal/layouts/about/single.html` — Phase 9 precedent for `type`-routed dedicated layout (gallery already follows the same pattern at `gallery/single.html`)
- `themes/minimal/layouts/partials/footer.html` — Lucide-style inline SVG icon precedent (24×24, 2px stroke, `currentColor`, `aria-hidden="true"`); chevron-left, chevron-right, X icons for lightbox buttons follow this exact pattern
- `themes/minimal/layouts/_default/_markup/render-image.html` — title-keyed image arms (currently `hero`/`grid`/`split`/`feature`/default; gallery doesn't use markdown image refs, so this hook is NOT modified by Phase 10)
- `hugo.toml` lines 34-36 — `[imaging.exif] disableLatLong = true` (D-23 layer 1; verify retained, not modified)
- `content/gallery/photos/` — 18 EXIF-scrubbed photos (filenames already in repo, case-preserved; D-01 `[[resources]]` blocks must match filename casing exactly per Pitfall 14 echo)
- `themes/minimal/static/css/style.css` lines 49-56 — `prefers-reduced-motion: no-preference` wrap precedent (D-22)
- `themes/minimal/static/css/style.css` lines 311-339 — current `/* === Gallery === */` block (full pre-edit state for diff context)

### Prior Phase Context (Carry-Forward)
- `.planning/phases/06-*/06-CONTEXT.md` (if present) — v2.0 Phase 6 established the page-bundle gallery, EXIF source-side scrub, `[imaging.exif] disableLatLong`, `body.page-gallery` scoping, Hugo `image.Process` WebP pipeline at q75/q78, lightbox-href progressive enhancement (current state)
- `.planning/milestones/v2.0-ROADMAP.md` § Phase 6 (lines 21, 119, 124-127) — historical context for the EXIF gate and page-bundle migration
- `.planning/phases/09-about-dynamic-rounded-redesign/09-CONTEXT.md` — Phase 9 establishes `--radius-soft: 12px` token (Phase 10 lightbox buttons MAY use `var(--radius-soft)` if rounded; planner's call within D-21 prefix)
- `.planning/phases/08-icon-svg-theme-toggle/08-CONTEXT.md` — Phase 8 establishes inline-SVG-with-currentColor precedent (Phase 10 lightbox buttons follow same pattern; chevron + X SVGs hand-authored, Lucide visual language, no library)
- `.planning/STATE.md` § Deferred Items — UAT for Phase 6 + 7 still pending post-deploy walkthrough; Phase 10 should NOT block on these (they're separate gates)

### External References
- http://tylerkarow.com/gallery — visual reference for masonry + lightbox aesthetic (Squarespace proprietary; visual pattern only — no code lifted)
- MDN: `<dialog>` element — `showModal()`, focus trap, ESC, `aria-modal`, `::backdrop` pseudo-element
- MDN: `backdrop-filter` — browser support, `-webkit-` prefix requirement for Safari <17
- caniuse: `backdrop-filter` — 92%+ global support 2026
- CSS-Tricks: There is No Need to Trap Focus on a Dialog Element — W3C APA position on `<dialog>` native focus trap
- CSS-Tricks: Masonry Layout is Now grid-lanes — confirms CSS Grid masonry is Safari-only in 2026 (not shippable)
- Sara Soueidan: Accessible Icon Buttons — `aria-label` on button, `aria-hidden` on inner SVG (chevron + X)
- WCAG 2.1 SC 2.4.3 (Focus Order) — relevant for tabbing within `<dialog>`
- WCAG 2.1 SC 2.5.5 / 2.5.8 — touch-target size for lightbox buttons (44×44 on mobile)
- Hugo docs: page resources — `[[resources]]` frontmatter + wildcard `src` (Hugo 0.31+; pinned at 0.157.0)
- Hugo docs: `image.Process` — `Resize`, `Fit`, quality parameters
- Hugo issue #5641 — confirms no stable seeding primitive for `collections.Shuffle` (rationale for D-04 `weight`)
- Aleksandr Hovhannisyan: How to Open and Close HTML Dialogs — backdrop-click pattern (D-10)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`baseof.html` line 26 — `body.page-{Type}` auto-class**: Already emits `class="page-gallery"` for `type: "gallery"` content. New CSS rules just prefix with `body.page-gallery` and they're scoped automatically. No layout change needed to activate scoping.
- **`gallery/single.html` precedent**: Phase 6 already proved the `layouts/{type}/single.html` routing pattern works. The current file has `Resources.Match "photos/*"` iteration — extending it with `sort` by `Params.weight` is a single-line change.
- **`baseof.html` end-of-body chrome IIFE pattern (lines 34-58)**: Direct precedent for `lightbox.js` shape — `(function () { … })();` IIFE, single-pass DOM bind on load, addEventListener for clicks/keys. Same conventions: `const`/`let`, `const ref = document.querySelector(...)`, early-return guards.
- **18 EXIF-scrubbed photos at `content/gallery/photos/`**: v2.0 Phase 6 sourced + processed these via source-side scrub. Reusable verbatim. No new authoring or scrub work for the photos themselves — only `[[resources]]` metadata is new.
- **Existing 600 px breakpoint (`@media (max-width: 600px)` block in style.css)**: Already defines mobile rules for hero/grid/header. New `column-count: 1` rule joins this block following the established pattern.
- **Flexoki palette tokens (`--bg`, `--bg-secondary`, `--text`, `--text-secondary`, `--border`, `--accent`, `--radius-soft`)**: All exist in both `:root` and `:root[data-theme="dark"]`. Lightbox buttons + caption text consume them directly — no new palette work, automatic theme support.
- **Lucide-style inline SVG precedent in `partials/footer.html`** (GitHub, Instagram icons at 18×18, 2px stroke, `currentColor`): exact pattern for chevron-left, chevron-right, X icons in the lightbox buttons. Hand-author the path strings; do NOT install Lucide as a package.
- **Hugo `image.Process` pipeline already wired**: existing `gallery/single.html:10-11` produces `$thumb` and `$full`. Switching `$thumb` from `fill 600x400 Smart webp q75` to `Resize 600x webp q75` is a single-token edit; `$full` stays at `fit 1200x1200 webp q78`.
- **`[imaging.exif] disableLatLong = true` in `hugo.toml:34-36`**: D-23 layer 1 already in place. Phase 10 verifies and extends with CI step.
- **`build: { publishResources: false }` in `content/gallery/index.md`**: Prevents originals from being copied to `public/`. Only Hugo-processed `_gen/images/*.webp` ship. EXIF is scrubbed by Hugo's pipeline (with `disableLatLong`); CI gate validates source-side scrub of the originals before they're processed.

### Established Patterns
- **`body.page-{type}` CSS scoping (Pitfall 17)**: Locked since Phase 6 (`body.page-gallery`). Every new gallery rule prefixes `body.page-gallery`. Generic names (`.lightbox`, `.modal`, `.close`, `.prev`) are forbidden — use `.gallery-lightbox-img`, `.gallery-lightbox-close`, etc.
- **Hugo title-keyed render-image hook**: Validated Phase 7 + 9. NOT used by Phase 10 — the gallery template iterates `Resources.Match` directly, not markdown image references. Hook stays untouched.
- **Page-scoped JS loading**: New pattern formalized in Phase 10 — `lightbox.js` loads from `gallery/single.html`, not `baseof.html`. Pattern reusable for any future page-specific JS.
- **Single-stylesheet section comments**: `/* === Gallery === */` is the existing block. New rules join under sub-section comments (`/* === Gallery — Masonry === */`, `/* === Gallery — Lightbox === */`); no new top-level files.
- **`prefers-reduced-motion: no-preference` wrap**: Universal pattern from style.css:49-56. Lightbox transitions inside this guard.
- **Single source of color truth via CSS custom properties**: All lightbox colors come from existing tokens. No hex literals in new rules (Pitfall 3 carry-forward) — except the rgba backdrop colour pair (D-12), which uses literal `16, 15, 15` (matches `--bg` dark mode hex `#100F0F`) — acceptable because the backdrop is theme-invariant.
- **IIFE chrome pattern**: `(function () { ... })();` end-of-body or page-scoped. Self-executing, no globals leaked. Lightbox.js follows this shape.
- **Image-attr emission via Hugo**: `width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"` already in use. Switching to `Resize 600x` produces variable `height` per photo (the masonry shape) — pattern unchanged.

### Integration Points
- **`content/gallery/index.md`**: gains 18 `[[resources]]` array entries, each with `src`, `name`, and `params { caption?, alt, weight }`. Frontmatter only — no body content. The existing `title`, `type`, `build.publishResources` keys are preserved.
- **`themes/minimal/layouts/gallery/single.html`**: 4 specific edits — (1) `range` becomes `range (sort (.Resources.Match "photos/*") "Params.weight")`, (2) `$thumb` directive changes from `fill 600x400 Smart` to `Resize 600x` (3 chars effectively edited), (3) `<a class="gallery-item">` gains `data-caption="{{ $photo.Params.caption }}"` and `data-alt="{{ $photo.Params.alt }}"` attributes, (4) at the bottom of `{{ define "main" }}`, `<dialog id="gallery-lightbox">` markup + `<script src="{{ "js/lightbox.js" | absURL }}" defer></script>` are appended.
- **`themes/minimal/static/js/lightbox.js`**: NEW file at the static-assets root. Hugo serves it from `/js/lightbox.js`. The IIFE binds on `DOMContentLoaded` (or runs immediately if `defer` ensures DOM-ready by execution time).
- **`themes/minimal/static/css/style.css`**:
  - `/* === Gallery === */` section gets ~30 lines of column-count masonry replacement.
  - New `/* === Gallery — Lightbox === */` block gets ~50-60 lines.
  - Mobile breakpoint at `@media (max-width: 600px)` gets `body.page-gallery .gallery-grid { column-count: 1; }` added.
  - New `@media (min-width: 600px) and (max-width: 899px)` block (or addition to existing one) gets `body.page-gallery .gallery-grid { column-count: 2; }`.
  - Total file growth: ~80-100 lines.
- **`.github/workflows/deploy.yml`**: gains a single named step `Verify EXIF scrub` between checkout and Hugo build (or after build; placement is planner's call, but pre-build catches issues earlier). Installs `libimage-exiftool-perl` via apt-get, runs exiftool, fails if forbidden fields appear. ~10 LOC added.
- **`hugo.toml`**: NOT modified. `[imaging.exif] disableLatLong = true` (lines 34-36) verified retained.
- **`content/gallery/photos/`**: NOT modified. The 18 photos are reused as-is.
- **No JS files modified except the new `lightbox.js`.** Theme toggle handlers, head IIFE, render-image hook all untouched.

### Risk Hotspots
- **Resources.Match sort by weight**: Hugo's `sort` function on a `Resources` collection takes `(coll, "Params.weight", "asc")` — verify exact syntax in template; Hugo's docs cover this but planner should validate against the 0.157.0 API.
- **`$photo.Params.caption` template access**: Confirms whether Hugo exposes resource params on `Process`-d resources or only the original `Resource`. The template iterates the original `Resource` (not the processed image), so `$photo.Params.caption` reads from the original — verify in first build.
- **Filename casing**: Pitfall 14 echo — `[[resources]]` `src` and `name` must byte-match the filename in `content/gallery/photos/`. The repo has both `.jpg` and `.JPG` and `.jpeg` and `.JPEG` cases; author MUST not normalize. Add a build-time grep verification.
- **`backdrop-filter` performance on low-end devices**: Pitfall 10. Mitigation via `@supports` (D-12). HUMAN-UAT post-deploy may report jank; if so, drop the blur and ship rgba-only. Planner SHOULD note this in the verification gate.
- **Touch swipe vs scroll**: While the dialog is open, body scroll is locked (D-11). Touch events on the dialog may still scroll the dialog itself if its content overflows; cap `<img>` height (D-25) prevents this on most devices.
- **CI exiftool installation cost**: ~10s on every deploy. Acceptable for the privacy guarantee. Caching apt packages is possible but adds workflow complexity; defer until measured pain.

</code_context>

<specifics>
## Specific Ideas

- **tylerkarow.com/gallery is the visual North Star** — masonry with preserved aspect ratios, photos visually breathing rather than crammed into a uniform grid, click-to-enlarge with caption surfacing the moment. Phase 10's interpretation: column-count masonry + native `<dialog>` lightbox + frontmatter-authored captions; same vibe, zero JS framework, zero NPM packages.
- **"Native primitives" must be the entire toolkit (REQUIREMENTS Out of Scope)** — `<dialog>` does focus trap, Esc, aria-modal, focus restoration, top-layer for free. Manual implementations of any of these are forbidden — if `<dialog>` doesn't handle it (body scroll lock, backdrop click close), implement minimally and inline.
- **"Author-controlled deterministic" is the gallery's social contract (REQ GALLERY-03)** — every visit shows photos in the same order, every deploy ships the same HTML diff (or no diff), deep-links to "the third photo" stay valid. The `weight` integer is the authoritative ordering — no JS shuffling, no Hugo `shuffle` template, no client-side reordering. Author iterates after first build to find the order they like.
- **Captions tell a 1-2 sentence story (REQ GALLERY-04 + FEATURES.md)** — not technical specs, not EXIF data, not GPS. Plain text in frontmatter, rendered as text in `<figcaption>`. Markdown processing on captions is explicitly out of scope (anti-feature: "captions/markdown library — overkill for 1-2 sentences").
- **Touch swipe on day-one (REQUIREMENTS Locked Decision + FEATURES.md "Differentiators recommend including")** — gallery is photo-centric; mobile is a real use case. 50 px deltaX threshold from REQUIREMENTS-07. ~20 LOC vanilla JS. NOT deferred.
- **Pitfall 4 awareness on column-count screen-reader order** — column-count fills column-by-column, so visual reading order != DOM order. ACCEPTABLE for gallery photos because (a) keyboard tab order matches `weight` (DOM order), (b) screen-readers announce by DOM order which is `weight`-sorted, (c) visual-only users don't have a "reading order" expectation for a photo grid. The trade-off is conscious.
- **Backdrop blur ships on day-one with `@supports` fallback (REQ GALLERY-05 + ROADMAP success #3)** — Pitfall 10 perf concern noted, mitigated by `@supports`-gated rule. HUMAN-UAT may surface jank on a 3-year-old Android; if so, post-phase remediation drops blur.
- **EXIF gate is a CI step, not just config (REQ GALLERY-09)** — REQUIREMENTS-09 says "CI gate enforced as in v2.0 Phase 6" — v2.0's gate was effectively author-discipline + Hugo config; Phase 10 adds the actual CI step in deploy.yml. This closes the gap REQUIREMENTS-09 envisions.
- **No new content authoring beyond frontmatter** — the 18 existing photos are reused as-is. Captions and alt-text are written in `index.md`, not new files. Minimum-viable authoring path.
- **Coarse plan granularity (D-27)** — favor 3 plans over 6. Lightbox JS depends on template depends on frontmatter (tight coupling); coarse plans match the tight coupling. Phase 9's 3-plan precedent is the template.

</specifics>

<deferred>
## Deferred Ideas

- **GALLERY-FUT-01: Photo counter overlay (`3 / 18`)** — already in REQUIREMENTS.md "Future Requirements". Single `<span>` updated on navigate, doubles as `aria-label` source. Useful for orientation in long galleries; the v3.0 surface is 18 photos which is small enough to skip. Defer to v3.x.
- **GALLERY-FUT-02: `<link rel="preload">` for next/prev lightbox image** — already in REQUIREMENTS.md "Future Requirements". Would smooth arrow-key navigation but Pitfall 11 explicitly bans pre-fetching (≤ 2 MB first-paint budget). Even if scoped to "after first navigation", the value is marginal for an 18-photo gallery. Defer to v3.x.
- **One-shot `scripts/shuffle_gallery.py` to author `weight` values** — Pitfall 5's "Option 1: Author-time shuffle, committed". Would write a deterministic-but-author-derived weight sequence. Considered: rejected as over-engineering. Author can hand-pick weights in 18 lines of frontmatter; a script saves maybe 30 seconds. Adds a maintenance dep.
- **Caption fade-in stagger (50 ms after image)** — FEATURES.md "Cinematic feel without being precious". Considered: rejected as scope creep into delight features. Phase 10 ships a functional lightbox; tasteful animations are a v3.x polish phase.
- **Single-SVG morph (sun-with-moon-mask) for theme toggle** — already deferred per ICON-FUT-01; not relevant to Phase 10 but listed for context.
- **Per-photo sidecar `.md` files for caption authoring** — ARCHITECTURE alternative considered, rejected by REQUIREMENTS Locked Decisions. `[[resources]]` frontmatter is the canonical authoring path.
- **Hugo `collections.Shuffle` for gallery order** — explicit anti-feature in REQUIREMENTS Out of Scope (non-deterministic across builds, Hugo issue #5641).
- **Client-side random gallery order on each page load** — explicit anti-feature in REQUIREMENTS Out of Scope (causes layout reflow + CLS risk + breaks deep-links/screenshots).
- **CSS Grid Level 3 `grid-template-rows: masonry`** — explicit anti-feature in REQUIREMENTS Out of Scope (Safari-only in 2026).
- **PhotoSwipe / GLightbox / Tobii / Slightbox / Lightbox2** — explicit anti-features. Native `<dialog>` covers everything they do.
- **Masonry.js / Isotope / Bricks.js / packery** — explicit anti-features. CSS column-count covers the layout.
- **focus-trap NPM package** — explicit anti-feature. Native `<dialog>` provides focus trap.
- **Lucide / Heroicons / Feather / Phosphor as installed packages** — explicit anti-features. Hand-author the chevron-left, chevron-right, X SVG paths inline (Lucide visual language; ~3 paths, ~150 bytes each).
- **A web font for the gallery** — explicit anti-feature. System font stack is locked.
- **Pre-fetching all full-size photos for "snappy UX"** — Pitfall 11. Would blow the ≤ 2 MB first-paint budget. Browser loads on demand only.
- **Bumping full-image quality from q78 to q82** — Pitfall 11 milestone-context drift. Code is canonical at q78; do not introduce a third quality tier.
- **JS-driven masonry layout (Pinterest-style with measurement)** — anti-feature. CSS column-count is sufficient.
- **Per-photo Plotly/Leaflet/interactive embeds** — out of scope; gallery is static photos with captions.
- **Comments on photos / e-commerce / CMS / backend services** — out of scope per project constraints.

### Reviewed Todos (not folded)

None — `gsd-sdk query todo.match-phase 10` returned `todo_count: 0`. No pending todos to fold or review.

</deferred>

---

*Phase: 10-gallery-lightbox-masonry-captions*
*Context gathered: 2026-05-04*

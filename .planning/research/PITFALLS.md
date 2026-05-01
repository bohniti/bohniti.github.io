# Pitfalls Research

**Domain:** Hugo personal website — v3.0 Design Update (theme-toggle SVG icon, lightbox+masonry gallery, About redesign)
**Researched:** 2026-05-01
**Confidence:** HIGH (specific to this codebase — files read in `themes/minimal/layouts/`, `themes/minimal/static/css/style.css`, `content/about/index.md`, `content/gallery/index.md`, `.planning/PROJECT.md`, `.planning/STATE.md`)

This document catalogues mistakes that are *specific to adding the three v3.0 features to THIS site* — not generic web-dev advice. Every pitfall is grounded in code that exists today (the inline `<head>` IIFE in `baseof.html`, the dual-IIFE click handler at end-of-body, the render-image hook keyed off image title, the `data-theme` attribute on `<html>`, and the Hugo `image.Process` page-bundle pipeline). Prior gotchas from v2.0 are referenced where they apply (Phase 7 P02 pullquote contrast, Phase 7 P01 case-sensitive `cooking.JPG`, Phase 6 EXIF scrub at source).

---

## Critical Pitfalls

### Pitfall 1: Icon FOUC — head IIFE updates `data-theme` but not the SVG icon

**What goes wrong:**
The current head IIFE at `baseof.html:13-23` resolves the theme and writes `document.documentElement.dataset.theme` + the `theme-color` meta — but the visible toggle UI is a `<button>Dark</button>` with text content updated *only* by the end-of-body IIFE (`baseof.html:36-56`). When that text button is replaced by an SVG sun/moon, the server-rendered HTML will ship one icon (say sun) and the end-of-body script will swap to the other (moon) on dark themes. The user sees the wrong icon for one paint frame, exactly the FOUC pattern v2.0 spent Phase 4 P02 eliminating for the page chrome.

**Why it happens:**
The existing two-IIFE split (head sets theme, end-of-body syncs the toggle button) was designed for a text label where the visual delta is small. With an SVG icon, the visual delta is the entire control. Devs add the SVG to header.html and assume the existing sync code is enough — but it runs *after* first paint.

**How to avoid:**
Server-render the icon with a Hugo conditional that mirrors the head IIFE's *worst-case assumption*, then sync inside the head IIFE itself before first paint. Two concrete options:

1. **Inline both icons in the SVG, hide via CSS keyed off `[data-theme]`.** Ship `<svg>...<g class="sun">...</g><g class="moon">...</g></svg>`; CSS rule `[data-theme="dark"] .sun { display: none } :root:not([data-theme="dark"]) .moon { display: none }`. Theme is on `<html>` *before* style sheet applies because the head IIFE sets it before the `<link rel="stylesheet">` at `baseof.html:24`. Zero JS for visibility — pure cascade.
2. **Move icon-state mutation into the head IIFE.** Have the head script also set a `data-icon="sun|moon"` attribute on the toggle (requires the toggle to exist by then — it doesn't, since the IIFE runs in `<head>` before `<body>`). This is fragile and rules option 1 out as the simpler fix.

Pick option 1. It's the same pattern the wordmark already uses (`currentColor` recolor through `var(--text)` — see Phase 05.1 D-01, D-02 in PROJECT.md).

**Warning signs:**
- Open DevTools, throttle CPU 6× slowdown, hard-reload `/about/` in dark mode → look for icon flicker on first frame.
- Diff first-paint screenshot vs. final-paint screenshot at theme = dark.
- Check `<svg>` is in the initial HTML response, not injected by JS.

**Phase to address:** Theme-icon phase (likely Phase 1 of v3.0). MUST be a verification gate, not a "we'll catch it in UAT" — the v2.0 Phase 4 P02 retrospective is the precedent for treating FOUC as blocking.

---

### Pitfall 2: Hit-target shrinkage — text "Dark" → 24px icon kills mobile tap target

**What goes wrong:**
The current `.theme-toggle` (`style.css:101-115`) inherits text styling and is roughly 30-35px wide × 22px tall (text "Dark" at 0.95rem font-size). Replacing with a bare 24×24 SVG icon shrinks the tap target below the 44×44 CSS-pixel iOS HIG / WCAG 2.5.5 (Level AAA) recommendation, and below the 24×24 minimum of WCAG 2.5.8 (Level AA, WCAG 2.2). Mobile users mis-tap onto adjacent nav links.

**Why it happens:**
Devs treat the icon's intrinsic size as the button's size. CSS without explicit padding leaves the click area equal to the SVG bounding box. The desktop experience looks correct because the cursor is precise; mobile testing reveals it.

**How to avoid:**
Set the toggle's *click target* to ≥ 44×44 explicitly:
```css
.theme-toggle {
  width: 2.5rem;          /* ~42px at 17px root, 40px at 16px mobile */
  height: 2.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;             /* margin-collapsed by flex centering */
}
.theme-toggle svg { width: 1.25rem; height: 1.25rem; }  /* ~21px visual icon */
```
This keeps the *visual* icon at GitHub-toggle size (~20-24px) while the *clickable* area meets 44px. Verify with browser inspector "Show ruler" or the iOS simulator's accessibility inspector. The existing `.site-nav { gap: 1.5rem }` at `style.css:87` already provides separation, but with a wider toggle the mobile reflow at `@media (max-width: 600px)` (`style.css:399`) needs a sanity check — the header switches to `flex-direction: column` so adjacent-link mistap is moot, but the desktop case still matters.

**Warning signs:**
- `getBoundingClientRect()` of `.theme-toggle` returns width or height < 44 in Chrome DevTools mobile emulation.
- Lighthouse Accessibility audit flags "Touch targets do not have sufficient size or spacing."

**Phase to address:** Theme-icon phase. Add to that phase's verification gate as a measured pixel check.

---

### Pitfall 3: SVG icon hard-coded fill breaks dark mode

**What goes wrong:**
The icon is downloaded from a SVG library (Heroicons, Feather, etc.) with `fill="#000000"` baked into the path. In light mode it looks fine; in dark mode the icon is invisible because `--text` is now `#CECDC3` and the icon is still rendering as black-on-near-black.

**Why it happens:**
SVG editors and icon libraries default to explicit fill values, not `currentColor`. Devs paste the markup directly without auditing.

**How to avoid:**
Mandatory contract for any SVG that lives in the chrome: **all `fill` and `stroke` values must be `currentColor` or omitted** (defaults to `currentColor` in inline SVG context). Add a CSS rule:
```css
.theme-toggle svg { color: var(--text-secondary); }
.theme-toggle:hover svg { color: var(--accent); }
```
The wordmark already does exactly this — see `style.css:124-130`. Same pattern, same source of truth.

**Warning signs:**
- View `<svg>` source: any literal `fill="#..."` or `stroke="#..."` is a smell.
- Toggle the theme and verify the icon visibly recolors in DevTools without a hard-reload.

**Phase to address:** Theme-icon phase. Trivial verification: `grep -E 'fill="#|stroke="#"' themes/minimal/static/images/brand/*.svg` should return zero results for chrome icons.

---

### Pitfall 4: CLS spike — masonry without explicit aspect-ratio

**What goes wrong:**
The current `/gallery/` is uniform CSS-Grid with `grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` and `height: auto` on `.gallery-img` (`style.css:281-304`). Each thumbnail is processed to `fill 600x400` so all thumbs are 3:2 — height is implicit and predictable. Switching to a *masonry* layout that **preserves each photo's aspect ratio** means thumbs are no longer uniform; widths still snap to columns but heights become per-photo. If `width` and `height` attributes aren't both set on each `<img>` *and* CSS doesn't reserve space via `aspect-ratio`, every image load shifts the layout below it.

The v2.0 Phase 6 success metric was CLS < 0.1 — a masonry refactor that re-introduces CLS would directly violate the milestone-locked invariant in PROJECT.md.

**Why it happens:**
Masonry libraries (or hand-rolled CSS columns) typically rely on `position: absolute` after measurement, or on CSS columns where the browser reflows when each image's intrinsic size becomes known. The first paint shows whatever `<img>` height the browser assumes (0, until image bytes arrive).

**How to avoid:**
- Continue to emit `width="{{ $thumb.Width }}"` and `height="{{ $thumb.Height }}"` from Hugo — the gallery layout already does this (`gallery/single.html:17-18`). Hugo's `image.Process` returns intrinsic dims at build time, before any pixel is shipped.
- For masonry **preserve aspect ratio per photo** — process each photo with a target *width* and `Resize` (not `fill 600x400`), e.g. `$photo.Process "600x webp q75"`. The height becomes per-photo; the `width="..." height="..."` Hugo emits is the per-photo intrinsic.
- Use CSS `aspect-ratio: attr(width) / attr(height)` (now interoperable as of 2024 — Chrome 125, Safari 18) or simply set `.gallery-img { height: auto }` paired with `width="X" height="Y"` attributes, which all modern browsers translate into an implicit aspect-ratio reservation. The existing CSS is correct; the change is the Hugo `Process` directive.
- **Do NOT use `column-count` CSS columns for masonry.** It breaks reading order for screen readers (top-to-bottom-then-next-column), and image-load shifts cascade across the whole column.
- Prefer either (a) JS-free CSS Grid masonry-lite using `grid-auto-rows: 10px` + computed `grid-row: span N` from each image's aspect ratio (computed in Hugo at build, no JS measurement), or (b) the new native CSS `display: grid; grid-template-rows: masonry` only behind a feature query (`@supports`) with the grid fallback above as default. Native masonry shipped in Safari 17.4 in 2024 but is still in CSS Grid Level 3 draft and **not** in Chromium as of Q1 2026 — don't ship it as the only path.

**Warning signs:**
- Run Lighthouse on a deployed `/gallery/` — CLS > 0.05 fails.
- DevTools Performance panel records "Layout Shift" entries during image loads.
- Local PageSpeed comparison: v2.0 (uniform 3:2 grid) baseline vs. masonry build.

**Phase to address:** Gallery phase. Should be a phase verification gate, not a soft check.

---

### Pitfall 5: Random masonry order changes on every build → diff churn + broken deep-links

**What goes wrong:**
A naive `randomize` (Hugo's `shuffle` template function or JS `Math.random`-on-load) re-orders photos every build or every page load. Result: (a) git diff churns the rendered HTML on every `hugo --minify` run, (b) deep-links to "third photo in the gallery" or screenshots taken for the v3.0 retrospective become invalid by the next deploy, (c) the lightbox's "next/prev" relationship between photos changes between visits, confusing returning users.

This site explicitly values "future-me as the audience" — non-deterministic builds violate that.

**Why it happens:**
Devs reach for `Math.random()` or Hugo's `shuffle` to satisfy the "randomized layout" requirement without recognizing that *visual variety* is achieved once at authoring time, not per-request.

**How to avoid:**
**Randomize once, freeze the order.** Two clean options:

1. **Author-time shuffle, committed.** Run a one-shot `scripts/shuffle_gallery.py` that reads the photo filenames, shuffles, and writes an explicit `order:` array to `content/gallery/index.md` front matter. Hugo iterates the array; build is deterministic. Re-shuffle is opt-in (run the script when a new photo arrives).
2. **Build-time deterministic shuffle by seed.** Use Hugo's `shuffle` *with a stable input order* — that's still non-deterministic across builds. Reject this option; fall back to (1).

Add an explicit `caption:` field in the same front matter array so caption authoring travels with order:
```yaml
photos:
  - file: IMG_8113.jpg
    caption: "Bouldering at Schöckl, summer 2024."
  - file: DSC09782.JPG
    caption: "Dachstein traverse, bivvy at sunrise."
```
Hugo iterates the array and resolves each `file` against `Resources.GetMatch` — same pattern as the render-image hook (`render-image.html:1`). This **also fixes Pitfall 6** (caption authoring drift).

**Warning signs:**
- `git diff public/gallery/index.html` after two consecutive builds shows reordered `<a>` blocks.
- Two browser tabs open at `/gallery/` show different photo positions.

**Phase to address:** Gallery phase. The data-model decision (front matter array of `{file, caption}`) is foundational — make it the first task in that phase before any layout work.

---

### Pitfall 6: Caption authoring drift — silent missing captions ship as empty strings

**What goes wrong:**
Without an authoring contract, photos arrive in `content/gallery/photos/` and get rendered with no caption (or worse, with a duplicate filename as caption). One photo without a caption looks like a bug; users wonder if it's missing or intentional.

This is a v2.0 known shape: PROJECT.md Phase 7 Key Decisions show the render-image hook *requires* a `title` field on every image markdown ref to pick the right size — same problem class. Without enforcement, authors forget.

**Why it happens:**
Hugo doesn't fail builds on missing front matter fields. Authors add a photo, forget the caption, push, deploy — only the user notices.

**How to avoid:**
- Define the data model as an array (Pitfall 5) so missing `caption:` is structurally visible (not an absent field on a hidden Resource).
- Add a Hugo build-time check: in `gallery/single.html`, wrap the iteration in `{{ if not .caption }}{{ errorf "Photo %s has no caption" .file }}{{ end }}`. Hugo's `errorf` aborts the build — CI fails fast, before deploy.
- Author check: `scripts/check_gallery.py` that reads front matter and asserts every entry has a non-empty caption + a file that exists in `photos/`. Run in CI.

**Warning signs:**
- `git diff content/gallery/index.md` adds a new entry with `caption: ""` or no caption key.
- A deployed photo shows no caption while siblings do.

**Phase to address:** Gallery phase, same task as Pitfall 5's data model.

---

### Pitfall 7: Lightbox lazy-load conflict — opens a placeholder/empty src

**What goes wrong:**
Current `gallery/single.html:19` lazy-loads thumbnails after the third photo. If the lightbox is wired naively to read the `<img src>` of the clicked thumbnail and inject it into the modal as the full-size image:

- Bad: lightbox shows the thumb URL (low-res) blown up on the modal.
- Worse: lightbox reads a *transparent placeholder* if the thumb hasn't loaded yet (some intersection-observer libraries leave the `src` blank until visible — Hugo's native `loading="lazy"` doesn't do this, but a misuse pattern of `data-src` does).

The current single.html already separates `$thumb` and `$full` Hugo Resources (`gallery/single.html:10-11`) — the `<a href>` points to `$full.RelPermalink`. The lightbox must follow this contract: open the *anchor href*, not the inner img src.

**Why it happens:**
JS-first thinking: "give me the clicked element, find the image inside, show it bigger." Devs read `event.target.querySelector('img').src` because it's one line. The semantic `<a href>` already encodes the right URL.

**How to avoid:**
Lightbox click handler operates on the `<a>` element:
```js
document.querySelectorAll('.gallery-item').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    openLightbox(a.href, a.querySelector('img').alt, a.dataset.caption);
  });
});
```
Progressive enhancement: with JS disabled, the `<a href>` still serves the full image directly. (The current site has zero JS dependencies for the gallery — preserve that as a fallback.)

**Warning signs:**
- Disable JS in DevTools → click a thumbnail → expect to navigate to the full image as a new page (works), not get a broken modal.
- Slow 3G network: open lightbox before thumb 5 has loaded → expect the full image to load, not a stretched thumb.

**Phase to address:** Gallery phase, lightbox sub-task.

---

### Pitfall 8: Focus trap missing / Esc not closing / scroll not locked

**What goes wrong:**
Three sibling failures of the same modal-correctness contract. Without a focus trap, Tab moves focus into the underlying page (header nav, footer links) which is now visually hidden behind a blurred backdrop but still focusable — keyboard users tab into nothing. Without Esc-to-close, users are stuck. Without `body { overflow: hidden }`, the page scrolls behind the modal when the user scrolls inside it.

The site's current accessibility bar is high — Phase 4 P03 made the theme toggle keyboard-reachable, aria-pressed, prefers-reduced-motion. A new modal that drops below that bar regresses the project.

**Why it happens:**
Devs implement open/close as a CSS class toggle and stop. Focus management, Esc binding, and scroll lock each look like extra work. Each missing piece is a known accessibility-test fail.

**How to avoid:**
Implement these as a single inline IIFE pattern at end-of-body, mirroring the existing theme-toggle IIFE shape (`baseof.html:34-56`):
```js
(function () {
  const overlay = document.querySelector('.lightbox-overlay');
  const closeBtn = overlay.querySelector('.lightbox-close');
  let lastFocus = null;

  function open(href, alt, caption) {
    lastFocus = document.activeElement;
    document.body.style.overflow = 'hidden';   // scroll lock
    overlay.hidden = false;
    closeBtn.focus();                          // focus enters modal
  }
  function close() {
    overlay.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();          // focus restoration
  }
  // Esc to close
  overlay.addEventListener('keydown', e => {
    if (e.key === 'Escape') close();
    if (e.key === 'Tab') {
      // focus trap: keep Tab inside overlay
      const focusables = overlay.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])');
      const first = focusables[0], last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    }
  });
  // ... wire open() to .gallery-item click
})();
```
Use semantic `<dialog>` element instead if browser support is comfortable — Chrome 37+, Safari 15.4+, Firefox 98+ all ship it as of Q1 2026, and `<dialog>` provides built-in focus trap, Esc handling, and inert siblings. Recommendation: use `<dialog>` with `showModal()` — it gives you all three behaviors free, and the polyfill story for browsers ≥ 4 years old is irrelevant for a personal site. (Confidence: HIGH — verify against MDN at build time; flag in roadmap.)

**Warning signs:**
- Open lightbox, press Tab repeatedly → focus visibly leaves the modal.
- Open lightbox, press Esc → modal stays open.
- Open lightbox, scroll inside → page scrolls behind.
- Open lightbox, click close → focus jumps to top of page instead of returning to the thumbnail.

**Phase to address:** Gallery phase — these are all hard verification gates, not soft. Each gets a Playwright/manual checklist item.

---

### Pitfall 9: prefers-reduced-motion violations on icon rotation + lightbox transition

**What goes wrong:**
Icon-toggle rotation animations (sun ↔ moon spin) and lightbox open/close transitions (fade-in, scale-up) are visual delight on default systems but vestibular triggers for users with `prefers-reduced-motion: reduce`. Phase 4 P03 codified this contract for theme transitions (`style.css:49-56` only enables transitions inside `@media (prefers-reduced-motion: no-preference)`).

**Why it happens:**
Devs add `transition: transform 200ms ease` directly on the icon or modal. The motion media query is an opt-in *negative* condition — easy to forget.

**How to avoid:**
**All new transitions must be wrapped in `@media (prefers-reduced-motion: no-preference)`** — same pattern as the existing body transition:
```css
@media (prefers-reduced-motion: no-preference) {
  .theme-toggle svg { transition: transform 200ms ease; }
  .lightbox-overlay { transition: opacity 200ms ease; }
}
```
For the lightbox, "no transition" means it appears instantly when reduced-motion is set — that's the correct behavior. Don't try to be clever with a 50ms "tasteful" transition; the spec intent is *zero* unrequested motion.

**Warning signs:**
- macOS System Settings → Accessibility → Display → Reduce motion ON → site still animates icon spin or modal fade.
- DevTools Rendering panel → "Emulate CSS media feature prefers-reduced-motion: reduce" → motion still occurs.

**Phase to address:** Theme-icon phase + Gallery phase. Same pattern, two contexts.

---

### Pitfall 10: backdrop-filter blur kills performance on low-end devices

**What goes wrong:**
`backdrop-filter: blur(20px)` is GPU-expensive — it requires the browser to rasterize everything behind the modal and apply a Gaussian blur per frame. On older Android, low-end iOS, and laptops without a discrete GPU, this drops frame rate during the modal-open transition and makes the modal feel laggy. On some Linux+Firefox configurations with hardware acceleration off, it falls back to CPU and stalls.

It also **doubles GPU memory** for the duration of the modal because the browser keeps two compositor layers around.

**Why it happens:**
Designers love the look (Apple-style frosted glass). Devs ship it without measuring.

**How to avoid:**
- Prefer **a flat semi-transparent overlay** (`background: rgba(16, 15, 15, 0.85)`) by default. Looks correct in both themes (the dark hex matches `--bg` in dark mode), zero GPU cost.
- If blur is required for the design language, **scope it to the no-reduced-motion + supports queries** and provide a fallback:
```css
.lightbox-overlay { background: rgba(16, 15, 15, 0.85); }
@supports (backdrop-filter: blur(20px)) {
  @media (prefers-reduced-motion: no-preference) {
    .lightbox-overlay {
      background: rgba(16, 15, 15, 0.5);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
    }
  }
}
```
- **Test on a 3-year-old Android.** If you can't, drop the blur. The aesthetic is "Kindle/Obsidian-minimal" — solid overlay is more on-brand than frosted glass anyway.

**Warning signs:**
- DevTools Performance recording during modal-open: paint time > 16ms.
- Frame rate drops below 60fps during open/close.
- User-reported jank on lower-end devices.

**Phase to address:** Gallery phase. Recommend deciding **upfront** to use the flat semi-transparent overlay and only add blur if a HUMAN-UAT review specifically asks for it. Avoids over-engineering.

---

### Pitfall 11: Page weight blowout — opening many lightbox photos doubles transfer

**What goes wrong:**
The v2.0 invariant is ≤ 2 MB first-paint. Current `/gallery/` ships thumbs only on first paint (`gallery/single.html:10` — `fill 600x400 webp q75`). The full-size `fit 1200x1200 webp q78` images are referenced via `<a href>` but only fetched on click (browser doesn't pre-fetch). Ship a lightbox and users will browse — opening 18 photos → 18 × ~250KB = ~4.5 MB additional transfer. That's fine for the per-session budget (each open is a deliberate user action), but two failure modes lurk:

1. **Pre-fetching all fulls "for snappy UX"** (some lightbox tutorials do this) blows the first-paint budget by ~5 MB.
2. **Ship the q82 fulls as the rendered modal image** when a q78 q-percentage suffices. The current code uses q78 for fulls (`gallery/single.html:11`); the milestone context describes "q82 fulls" — there's a 4-point quality drift in the roadmap context. Settle which is canonical and stick to it.

**Why it happens:**
Devs treat "user clicks → show big" as license to pre-load. Or they bump quality on the rationale that "the user is choosing to see this image, so make it good" — without measuring file-size delta.

**How to avoid:**
- **Never preload `fit 1200x1200 webp q78` photos.** No `<link rel="preload">`, no `<link rel="prefetch">`, no JS warmup. The browser loads on demand when the user clicks.
- **Reuse the existing `$full` Hugo Resource processed at q78.** Don't introduce a third quality tier (q82 from milestone context) — STATE.md confirms the shipped pipeline is q75/q78. Bring the milestone context in line with the code, not the other way around.
- **Add a build-time check:** total size of `public/gallery/photos/*` (fulls only) — fail if any single full > 400 KB. Prevents one badly-compressed photo from inflating the catalog.

**Warning signs:**
- Network tab on `/gallery/` first-paint shows full-size photo requests.
- Total transfer for 18 fulls > 5 MB.
- Quality `q82` appears anywhere in code while STATE.md says `q78`.

**Phase to address:** Gallery phase. Add the size-budget check to the Phase verification gate.

---

### Pitfall 12: ALT text dropped from thumbnail → not propagated to lightbox view

**What goes wrong:**
Current `gallery/single.html:22` ships `alt=""` (decorative — appropriate when the `<a>` has an aria-label). With a lightbox, the modal image is no longer "decorative inside a labeled link" — it becomes the *primary content* of the dialog. An empty alt on a primary image is an a11y violation. Screen-reader users hear "image" with no description.

**Why it happens:**
The thumbnail-as-link pattern correctly uses `aria-label` on the `<a>` to describe the link; `alt=""` on the image avoids redundant announcement. The lightbox changes the image's role from "decoration inside link" to "main content inside dialog" — but devs copy the same `alt=""` because it's already there.

**How to avoid:**
- **Author per-photo alt text** (separate from caption — alt is for screen readers, caption is for sighted users). Add to the front-matter array (Pitfall 5):
```yaml
photos:
  - file: IMG_8113.jpg
    alt: "Climber on overhanging route at Schöckl crag"
    caption: "Bouldering at Schöckl, summer 2024."
```
- The thumbnail keeps `alt=""` (it's still inside an `aria-label`-ed link). The lightbox image gets `alt="{{ .alt }}"`.
- If alt and caption converge on the same content for some photos, *that's fine* — the rendering layer chooses which to use where.

**Warning signs:**
- VoiceOver / NVDA announces the lightbox image as "image, image" (no description).
- Front matter has `caption:` but no `alt:` field.

**Phase to address:** Gallery phase, same data-model task as Pitfall 5/6.

---

### Pitfall 13: Lightbox displays full image with EXIF reintroduced

**What goes wrong:**
v2.0 Phase 6 + Phase 7 both established **EXIF scrub at source** — photos arrive in-repo already stripped of GPS/Make/Model/Serial (PROJECT.md Key Decisions). The privacy invariant holds because Hugo `image.Process` doesn't *add* EXIF — it just resizes pixel data and emits WebP. But two regression paths exist:

1. **A new gallery photo lands in `content/gallery/photos/` without scrubbing** because the v3.0 milestone introduces a new authoring flow (random-shuffle script, caption authoring) and the EXIF check is buried in v2.0 Phase 6 verification, not the new phase's gates.
2. **Hugo `image.Process` with WebP-q-high preserves EXIF** in some build configurations. Safe-by-default in 0.157.0 (verified Phase 6), but if v3.0 changes the process directive (e.g. switches to `Resize` for masonry — see Pitfall 4), re-verify.

**Why it happens:**
Privacy gates that ran once during v2.0 don't auto-run on new content. Authors assume "the gallery is already private" and skip the check.

**How to avoid:**
- Bring the Phase 6 verification gate forward into the v3.0 Gallery phase as a recurring CI check:
```bash
exiftool -GPS:all -Make -Model -SerialNumber content/gallery/photos/*.{jpg,JPG,jpeg,JPEG} | grep -iE 'gps|make|model|serial' && exit 1 || exit 0
```
Runs on every PR, fails build if any forbidden field appears. (PROJECT.md notes Phase 7 P03 used a similar pattern — D-27 verification gate.)
- Document the authoring flow: "Drop photo → run `scripts/scrub_exif.py` → commit." Make scrubbing part of the script that adds the photo to front matter.
- **Verify the lightbox-served full image is the same WebP Hugo emits** — not the original JPEG. Hugo's `Process` output goes to `resources/_gen/images/` and is served from `/gallery/photos/...webp`. The original JPEG in `content/gallery/photos/` is never served because `gallery/index.md` has `build: { publishResources: false }` (`content/gallery/index.md:5`).

**Warning signs:**
- `exiftool public/gallery/photos/IMG_*.webp | grep -i gps` returns hits.
- A new photo lands in the repo without an entry in `scripts/scrub_exif.py`'s log.

**Phase to address:** Gallery phase. Cross-cutting privacy gate — runs in CI on every push.

---

### Pitfall 14: Render-image hook breakage when About introduces new image classes

**What goes wrong:**
The render-image hook at `themes/minimal/layouts/_default/_markup/render-image.html` keys off the markdown image's `title` attribute (`hero` → 480×600 q80, `grid` → 400×300 q75, default → 800×600 q78). The About redesign will likely need new layout shapes — e.g. a "circle portrait" or "wide banner" or "side-by-side pair." Two failure modes:

1. **Adding a new title keyword without updating the hook.** Author writes `![...](images/portrait.jpg "circle")` — hook doesn't recognize `circle`, falls through to default (800×600 q78). Image renders at wrong size, no class applied for the new circular CSS rule.
2. **Adding a new title keyword that *collides* with hero/grid.** Author writes `"hero-circle"` — hook does `eq $title "hero"` which is false for `"hero-circle"`. No partial match. Same fallthrough.

The hook *also* handles `Page.Resources.GetMatch` — case-sensitively. PROJECT.md Phase 7 P01 already burned a day on `cooking.JPG` vs `cooking.jpg` filename casing. The same trap applies to any new image added in v3.0.

**Why it happens:**
The render-image hook is a single point of coupling between markdown authoring and CSS layout. Devs forget it exists when adding new About sections — the markdown looks like normal markdown.

**How to avoid:**
- **Extend the hook explicitly for v3.0.** Add new arms for whatever shapes the About redesign introduces. Keep the three-arm switch pattern from Phase 7 P01:
```go-html-template
{{- $isCircle := eq $title "circle" -}}
{{- $isWide := eq $title "wide" -}}
...
{{- if $isCircle -}}
  {{- $processed = $resource.Process "fill 200x200 Smart webp q80" -}}
  ... class="about-circle-img"
{{- end -}}
```
- **Audit at the start of the About phase**: enumerate every image that will appear in the new layout, decide its shape, then update the hook *first*. Don't write the markdown until the hook is updated.
- **Preserve the defensive passthrough fallback** at `render-image.html:19-21` — it's the load-bearing safety net for any image that slips through without a recognized title.
- **Filename casing rule:** any new About image must match its markdown ref byte-for-byte. Add a build-time check via a Hugo template that warns on case mismatches (or rely on the existing `errorf` Hugo emits when `GetMatch` returns nil).

**Warning signs:**
- About page renders an image at default size when the design called for a different shape.
- `[render-image]` log entries show fallthrough to default arm.
- A new image breaks because of `cooking.JPG` vs `cooking.jpg` style mismatch (Phase 7 P01 echo).

**Phase to address:** About phase. First task in that phase: enumerate the new layout's image shapes and update the render-image hook.

---

### Pitfall 15: Pull-quote contrast regression on dark theme (Phase 7 P02 echo)

**What goes wrong:**
The current About has **one** documented WCAG-borderline element: `.about-pullquote strong` at `style.css:335-341` ships `#D14D41` on `#1C1B1A` = 3.97:1, passing AA *only* because it inherits `1.4rem + font-weight: 700` (qualifies as "large text" ≥ 14pt bold). The CSS comment at `style.css:335-337` is **load-bearing** — anyone who reduces the font-size or font-weight without re-checking contrast silently regresses to a WCAG fail.

The About redesign explicitly says "more dynamic and rounded layout." This invites: smaller pull-quotes, subtler color accents, lighter font weights — every one of which can break the 3.97:1 → 3.0:1 cliff.

**Why it happens:**
The borderline state isn't visible in light mode (the same color on cream is well above 4.5:1). Devs adjust the typography in light mode, ship, and the dark-mode failure surfaces only in HUMAN-UAT or worse, never.

**How to avoid:**
- **Retain the load-bearing comment.** Any CSS edit to `.about-pullquote strong` must re-run a contrast check on the dark-theme color pair.
- **Add a contrast-budget rule to the About phase:** any new About element using `var(--accent)` or `var(--accent-hover)` on `var(--bg-secondary)` background must declare the dark-mode contrast in a comment, the same way Phase 7 P02 did.
- **Run an automated contrast audit** as part of the phase verification gate — `axe-core` or `pa11y` against the deployed dark-mode `/about/`. Both tools catch the 3:1 vs 4.5:1 thresholds correctly when text-size hints are present.
- **Don't reduce font-size of `.about-pullquote` below 1.4rem and don't drop weight below 700** — encode this as a comment alongside the existing one. Or change the *color* (use `var(--text)` plus an underline for emphasis — passes contrast trivially).

**Warning signs:**
- DevTools Accessibility inspector flags `.about-pullquote strong` contrast on dark theme.
- Lighthouse Accessibility audit drops from 100 in dark mode.
- A CSS PR touches `.about-pullquote` without mentioning contrast in the commit message.

**Phase to address:** About phase. Verification gate item.

---

### Pitfall 16: "Dynamic and rounded" turning into bloat that violates Kindle/Obsidian-minimal feel

**What goes wrong:**
The brief is "more dynamic and rounded" — easy to mis-translate into: rounded card containers with shadows, animated section reveals, gradient backgrounds, decorative icons, multi-column hero with parallax. Each of those is a step *away* from Kindle/Obsidian minimalism. The aesthetic invariant is locked in PROJECT.md ("Aesthetic stays Flexoki — site should still feel 'like a Kindle or Obsidian'").

**Why it happens:**
"Dynamic" reads as "more moving parts." It actually means *content variety* — climbing + professional, vs. climbing-only — not visual variety.

**How to avoid:**
- **Anchor the redesign to the reference URL** mentioned in PROJECT.md (`tylerkarow.com/about`). Open that page, screenshot it, list the five most distinctive features. Translate each to a Flexoki equivalent. Anything that doesn't translate cleanly → cut.
- **Borrow no more than one new visual primitive.** E.g. add rounded photo crops *or* asymmetric grid *or* an inline call-to-action — pick one. Adding all three is bloat.
- **Forbid:** drop shadows beyond 1px, gradient backgrounds, parallax, scroll-triggered animations, decorative SVG flourishes, custom fonts beyond the system stack.
- **Ratify the design intent in a written paragraph in `.planning/REQUIREMENTS.md`** before any CSS is written. Re-read at every commit. (Phase 7 P02's "RESEARCH amendment 1" comment in `style.css:355` is precedent for documenting design constraints in code.)

**Warning signs:**
- About page CSS grows by > 50 LOC.
- New CSS uses `box-shadow`, `linear-gradient`, `animation`, or `transform` outside an interactive state.
- The About page no longer renders visually similar to the rest of the site.

**Phase to address:** About phase. Define the constraint **before** layout work starts.

---

### Pitfall 17: New About CSS leaks into other pages via overly-generic class names

**What goes wrong:**
The About redesign introduces classes like `.hero`, `.card`, `.intro`, `.profile-photo` — generic names that already appear or are likely to appear elsewhere. CSS bleeds: a new blog post that styles a `.card` element gets the About page's rules applied. The current codebase carefully scopes via `body.page-about` (`style.css:307-358`) — Phase 7 P02 explicitly added the `type: "about"` front matter (PROJECT.md Phase 07 P02 decision) so `body.page-about` resolves at runtime.

**Why it happens:**
Authors copy CSS from a Codepen / Tailwind tutorial that uses generic class names. The classes feel meaningful in isolation.

**How to avoid:**
- **All About-specific CSS must be prefixed with `body.page-about`** — match the existing pattern (`style.css:307`, `:343`, `:350`).
- **Use page-prefix namespacing for new utility classes:** `.about-card` not `.card`, `.about-hero-circle` not `.hero-circle`.
- **Lint rule:** `grep -E '^\.(card|hero|intro|profile|bio|skill)' themes/minimal/static/css/style.css` should return zero results outside `body.page-about` scopes.

**Warning signs:**
- A blog post or `/gallery/` page renders with About-page styling.
- New CSS rule starts with `.something {` instead of `body.page-about .something {`.

**Phase to address:** About phase. Verification gate item.

---

### Pitfall 18: Professional content dates fast (specific job titles vs. broader narrative)

**What goes wrong:**
The current About lists specific roles, dates, and metrics ("40% → 95%", "7,000 daily users", "(since 09/2023)" at `content/about/index.md:29-33`). The redesign brief says "balance climbing with professional background" — the temptation is to *add more* specific bullets and certs. But specifics rot: a year from now the dates feel old, the metrics need updating, the certs expire (the Power MBA *(2021)* is already four years stale).

A redesign is a chance to shift toward **narrative that doesn't expire** — "I build AI platforms in Vienna" reads correctly in 2026 and 2030. "Senior Data Science Consultant since 09/2023" doesn't.

**Why it happens:**
LinkedIn-style résumé phrasing is the default. It's optimized for recruiters scanning, not for "future-me reading my own About in 2030."

**How to avoid:**
- **Top of page = evergreen narrative.** "I'm Timo — I build AI platforms and climb mountains." (No date, no metric, no title.)
- **Specifics live below in a clearly-dated section.** "Recent work (2026)" header — visually marks the content as time-bound, future-me can update or rotate without restructuring.
- **Link out for specifics that change frequently.** CV PDF (`/files/timo-bohnstedt-cv.pdf` already exists at `content/about/index.md:15`) is the right home for dated bullets — *that* file gets updated; the About page narrative doesn't.

**Warning signs:**
- About page has more dated specifics than the v2.0 version.
- A specific metric in the About is stale within six months.

**Phase to address:** About phase. Content-strategy decision before layout decisions.

---

### Pitfall 19: Hero image cropping breaks across viewports

**What goes wrong:**
Current hero is 480×600 (`render-image.html:8`) — 4:5 portrait. Works on desktop (2fr 1fr column grid → ~213px wide rendered) and stacks to single column on mobile (`style.css:402-405`). A redesign that uses a *wider* hero (e.g. 16:9 banner) or a *circular* hero (1:1) needs explicit Smart-fill anchoring or the face will be cropped off on some viewports.

**Why it happens:**
Hugo's `image.Process "fill 800x800 Smart webp q80"` uses Smart cropping (entropy-based + face detection in newer versions, but Hugo 0.157.0's Smart algorithm is entropy-only — confidence MEDIUM; verify against Hugo docs). Entropy cropping can clip faces if the visually-busy region is offset from the subject.

**How to avoid:**
- **Process hero photos at the *intended display ratio*, not a generic 4:3 or 16:9.** If the design renders the hero at ~300×300 circular, process at `fill 600x600 Smart webp q80`.
- **Use Hugo's anchor argument when Smart is unreliable**: `$image.Process "fill 600x600 center webp q80"` or test individual photos with `top`, `bottomLeft`, etc. (`image.Process` supports anchor as the third token.)
- **Inspect every processed hero in the build output** before merging — `public/about/portrait_hu*.webp`. If a face is clipped, switch to manual anchor or pre-crop the source.

**Warning signs:**
- Face/subject visibly clipped on mobile but not desktop, or vice versa.
- Hero image's intrinsic aspect ratio doesn't match the rendered slot (browser stretches or letterboxes).

**Phase to address:** About phase. Inspect-the-build verification gate.

---

### Pitfall 20: Asymmetric sections collapse poorly on mobile

**What goes wrong:**
"Dynamic and rounded" likely means asymmetric layouts — e.g. text-left + image-right, then image-left + text-right, then full-width pull-quote. On desktop the alternation reads rhythmically. On mobile, all sections collapse to single column — and the natural reading order (top-down, image then text or text then image) inverts depending on the section's *desktop* layout. Suddenly mobile readers see image-text-image-text or all-text-then-all-images.

The current About already deals with this for the hero (`style.css:402-405` flips to single column on `max-width: 600px`) and for the grid (`:407-409`). New asymmetric sections need the same treatment.

**Why it happens:**
Devs design desktop first, add a mobile breakpoint, and don't audit reading order through the breakpoint.

**How to avoid:**
- **Default mobile to source order.** In CSS Grid, source order is preserved unless explicitly reordered. Don't use `grid-row` / `grid-column` to swap visual order on desktop without checking mobile.
- **Audit each new section at `max-width: 600px`** — read it top-to-bottom on a phone-shaped browser window. Does the narrative flow?
- **For sections where desktop puts image-right but mobile narrative needs image-after-text**, the mobile single-column collapse is fine. For sections where desktop puts image-left and mobile needs the same image-first order, *write the markdown image-first* and reverse on desktop with `grid-template-areas` — keeps source-order = mobile-order.

**Warning signs:**
- Mobile About reads as a wall of text followed by a wall of images, or vice versa.
- DevTools mobile emulator shows stacked sections in a different order than the markdown.

**Phase to address:** About phase. Each new section gets a mobile read-order check.

---

### Pitfall 21: Adding interactive JS to About creates a one-off pattern

**What goes wrong:**
The redesign brief says "more dynamic" — easy to interpret as *interactive*. Drop in a "click to expand bio" or "tabbed interest section" or "scroll-triggered timeline." Each one needs JS. The site is currently:
- Theme toggle: vanilla JS, end-of-body IIFE.
- Gallery: zero JS (just `<a href>` to full image).
- Blog post `2026-03-05-climbing-routes`: heavy JS for Plotly/Leaflet, but contained to that one post bundle.

An About-only JS pattern would be a fourth flavor — neither chrome-IIFE, nor zero-JS-content, nor blog-post-page-bundle. Maintenance creep.

**Why it happens:**
"Dynamic" is conflated with "JavaScript." A static page can absolutely feel dynamic via typography rhythm, alternating layouts, photo-rich content, and asymmetric whitespace.

**How to avoid:**
- **Reject all interactive widgets on About** unless they're solving a content problem CSS can't (CSS can do tabs via `:target` or `<details>` — neither requires JS).
- If JS is genuinely needed, **reuse the chrome-IIFE pattern** — single-file end-of-body IIFE in `baseof.html` — not a per-page script in `content/about/`.
- Bias toward `<details><summary>` for any "expand more" need. Built-in keyboard support, no JS, accessible by default.

**Warning signs:**
- A new `.js` file appears in `content/about/` or `themes/minimal/static/`.
- About page has any `addEventListener` outside the existing two IIFEs.

**Phase to address:** About phase. Constraint stated up-front.

---

### Pitfall 22: theme-color meta tag desync with new icon swap timing

**What goes wrong:**
The end-of-body IIFE updates the `theme-color` meta synchronously inside the click handler (`baseof.html:53`). The head IIFE also does it on first load (`baseof.html:21`). With an SVG icon driven by CSS keyed off `[data-theme]` (Pitfall 1's recommended fix), the icon updates instantly because `dataset.theme` is the same write that already triggers the cascade. **No new theme-color logic needed** — but a mistake mode is to *also* update the icon imperatively, leaving two paths and risking a desync if one is missed.

**Why it happens:**
Belt-and-suspenders thinking: "let me also update the icon's class in JS to be safe." Now there are two sources of truth.

**How to avoid:**
- **One source of truth: `dataset.theme` on `<html>`.** Both icons live inline in the SVG; CSS shows/hides via `[data-theme]` selector. JS only writes `dataset.theme`.
- **Don't add JS to update the icon.** If CSS-only swap doesn't render correctly, fix the CSS, don't reach for JS.

**Warning signs:**
- Click handler in `baseof.html` grows to update icon class/state.
- Icon and theme-color meta visibly out of sync (icon says dark, address bar says light).

**Phase to address:** Theme-icon phase.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Use a third-party lightbox library (PhotoSwipe, Lightbox2, Fancybox) | Cuts modal implementation to ~5 LOC | Adds 30-100KB JS to a no-JS-framework site; violates v2.0 invariant; couples to upstream's CSS | Never — lightbox correctness is ~80 LOC of vanilla JS, well within scope |
| Inline-style the new About layout instead of adding to `style.css` | Faster iteration during design | Style drift between About and rest of site; can't theme in dark mode without `:root[data-theme="dark"]` rules | During a 1-day spike, then move to stylesheet before merge |
| Use `column-count` for masonry | Pure CSS, no measurement | Breaks tab order for keyboard users; image-load shifts; can't preserve insertion order across columns | Never for content galleries |
| Pre-fetch full-size gallery images for "snappy lightbox" | Lightbox feels instant | Blows the 2 MB first-paint budget by 5+ MB | Never — user's click is the prefetch trigger |
| Random-shuffle gallery in JS at page-load | "Real" randomness; one-line fix | Non-deterministic builds; broken deep-links; CLS on every visit; SEO crawl confusion | Never |
| Add `prefers-reduced-motion` only to user-initiated animations | "Implicit motion is fine, like loading spinners" | Vestibular triggers fire without user action; spec-violating | Never — spec applies to all motion |
| Bake job title and date into About hero | Easy copy from LinkedIn | Stale within 6-12 months; About becomes a maintenance task | When a CV PDF is the canonical source and About just summarizes |
| Use generic `.card`, `.hero`, `.intro` class names | Reads like Bootstrap, familiar | CSS bleeds into other pages; refactor pain | Never in this codebase — page-prefix is the established pattern |
| Skip alt text for decorative gallery thumbs assuming a11y is "covered" by aria-label | Less authoring overhead | Lightbox primary image has empty alt; AA fail | Only when image is *purely decorative* and no modal exposes it directly |

---

## Integration Gotchas

Common mistakes when connecting to existing site systems.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Inline `<head>` IIFE | Reading from a not-yet-parsed `<body>` element | Head IIFE only writes to `document.documentElement` (always available); end-of-body IIFE handles `<button>` |
| Render-image hook | Adding new image without updating the title-keyword switch | Audit the hook *before* adding markdown refs; extend the switch first |
| Hugo `Resources.GetMatch` | Mismatched filename casing (`cooking.JPG` vs `cooking.jpg`) | Match markdown ref to filesystem byte-for-byte; Phase 7 P01 burned a day on this |
| `[data-theme]` attribute | Adding new themed colors without `:root[data-theme="dark"]` override | Every new `var(--*)` reference needs both `:root` and `:root[data-theme="dark"]` definitions |
| Hugo `image.Process` | Switching from `fill` to `Resize` and losing emit of `width`/`height` | Always emit `width="{{ .Width }}" height="{{ .Height }}"` regardless of process directive |
| `baseof.html` `<head>` script ordering | Inserting a new `<script>` before the theme bootstrap IIFE | New chrome scripts go *after* the theme IIFE and *before* the stylesheet link, or at end-of-body |
| `body.page-{type}` body class | Forgetting `type:` front matter on a new page bundle | Every new content type with custom CSS needs explicit `type:` (Phase 7 P02 fix); Hugo 0.157.0 doesn't auto-derive |
| EXIF scrub | Assuming new gallery photos inherit Phase 6 verification | Re-run scrub on every new photo; CI gate it |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| `backdrop-filter: blur` on lightbox overlay | Modal-open jank, low frame rate | Default to flat semi-transparent overlay; gate blur behind `@supports` + `prefers-reduced-motion: no-preference` | Low-end Android, older iPhones, Linux+Firefox without HW accel |
| Pre-fetch gallery fulls | First-paint > 2 MB | No preload/prefetch; user click is the trigger | Always — direct violation of milestone invariant |
| JS-measured masonry layout | Thrashes on resize, CLS during load | Hugo emits intrinsic `width`/`height` per photo; CSS reserves space via attribute-derived aspect ratio | Whenever images > 10 in a single grid |
| Loading all 18 fulls in a slideshow JS preview | 4+ MB sustained transfer | Lightbox loads single full per click; no auto-advance/preload | Always |
| About page hero processed at q90 vs q80 | Bigger first-paint, no visible quality gain | Match existing q80 ceiling; don't bump quality without measuring delta | When About hero > 100 KB |
| Multiple Hugo `Process` calls per image (e.g. thumb + medium + full) for the gallery | Build time grows, `resources/_gen` bloats | Two tiers (thumb + full) is sufficient; no `srcset` needed for fixed-size lightbox | When build time > 30s on CI |

---

## Security Mistakes

Domain-specific issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| New gallery photo lands without EXIF scrub | GPS coordinates of climbing locations leak | CI exiftool gate on every push (Pitfall 13); script wraps "add photo" workflow |
| Lightbox opens an `<img>` whose `src` is built from `location.hash` or query params | Reflected XSS via crafted URL | Lightbox only opens hrefs from the page's own `.gallery-item` elements; never trust URL params |
| About PDF (`/files/timo-bohnstedt-cv.pdf`) contains EXIF/metadata revealing more than the public bio | PII leak | Run `exiftool -all=` on the PDF before commit; document in `scripts/build_brand_assets.py` neighbor |
| Hugo `markup.goldmark.renderer.unsafe = true` (already enabled) used to embed user-derived HTML | XSS if any content source becomes user-derived | Treat `unsafe = true` as "trusted authoring only"; never accept content from external sources without review |
| New SVG icon copied from third-party with embedded `<script>` | Inline script execution at chrome level | Strip all `<script>` tags from any committed SVG; use `cairosvg` pipeline (already in use) for sanitized output |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Theme toggle icon doesn't visibly change on click | User can't tell if click registered | CSS `[data-theme]` selector swaps visible icon synchronously with the same write |
| Lightbox has no "next/prev" affordance | Users who want to browse all photos can't | Tap-left / tap-right zones + keyboard arrow keys; if scope is too big for v3.0, single-photo lightbox is acceptable but document the tradeoff |
| Caption appears below the photo on desktop, hidden on mobile (or vice versa) | Inconsistent narrative across devices | Caption is part of the modal's flow; appears in same relative position regardless of viewport |
| Closing the lightbox jumps the page back to top | User loses scroll position | `lastFocus` restoration restores both focus *and* scroll context (browser handles scroll-into-view on focus) |
| About hero image cropped differently on desktop vs. mobile | Subject's face clipped on one viewport | Process at the rendered display ratio; use explicit anchor; verify in build |
| Theme toggle is below or beside another nav link with no visual separation | Mis-tap target | `.site-nav { gap: 1.5rem }` (existing) is sufficient; verify after icon swap |
| About narrative starts with job title | Reads as résumé, not a person | Lead with name + identity; demote dated specifics |
| Gallery photos load in a different order on every visit | Returning user can't find the photo they remembered | Order is stable; randomized once at authoring time |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Theme icon toggle:** Visible icon flips, but verify head-IIFE-applied CSS also swaps the icon for the *first paint* (not the post-JS sync). Hard-reload in dark mode with throttled CPU.
- [ ] **Theme icon toggle:** Icon visible in light mode — verify dark mode by toggling and inspecting fill/stroke, not just light-mode screenshot.
- [ ] **Theme icon toggle:** Tap target ≥ 44×44 — verify with DevTools, not eyeball.
- [ ] **Theme icon toggle:** `aria-label` present and correct ("Toggle dark mode" or similar); `aria-pressed` reflects current state.
- [ ] **Theme icon toggle:** `prefers-reduced-motion` respected — toggle in macOS settings, verify no rotation/transition.
- [ ] **Lightbox modal:** Esc closes — keyboard test, not click test.
- [ ] **Lightbox modal:** Tab loops within modal — test with keyboard only.
- [ ] **Lightbox modal:** Body doesn't scroll behind modal — long-press scroll inside modal on mobile.
- [ ] **Lightbox modal:** Focus returns to triggering thumbnail on close.
- [ ] **Lightbox modal:** Works with JS disabled (falls back to navigating to full image).
- [ ] **Lightbox modal:** Uses semantic `<dialog>` or has correct ARIA (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`).
- [ ] **Gallery masonry:** No CLS — verify via Lighthouse and DevTools Performance recording.
- [ ] **Gallery masonry:** Order is deterministic across builds — `git diff public/gallery/index.html` after rebuild = empty.
- [ ] **Gallery captions:** Every photo has a non-empty caption — build fails otherwise.
- [ ] **Gallery alt text:** Every photo has a non-empty alt — separate from caption.
- [ ] **Gallery EXIF:** `exiftool` reports zero GPS/Make/Model/Serial in `public/gallery/photos/*.webp`.
- [ ] **About redesign:** Pull-quote contrast ≥ 3:1 (large text) on dark theme — automated audit.
- [ ] **About redesign:** All new CSS scoped under `body.page-about` — grep verifies.
- [ ] **About redesign:** No new JS introduced — `find content/about themes/minimal/static -name '*.js'` = pre-v3.0 baseline.
- [ ] **About redesign:** Hero image not face-clipped on any viewport — visual inspection.
- [ ] **About redesign:** Source-order matches mobile reading order — read top-to-bottom on phone-shaped emulator.
- [ ] **All three features:** Existing v2.0 invariants hold — first-paint ≤ 2 MB, CLS < 0.1, no FOUC, theme persists.

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Icon FOUC (Pitfall 1) | LOW | Move icon visibility into CSS keyed off `[data-theme]`; ship inline SVG with both icons; remove any JS icon-mutation |
| Hit target too small (Pitfall 2) | LOW | Add `width: 2.5rem; height: 2.5rem` + flex-center to `.theme-toggle` |
| CLS from masonry (Pitfall 4) | MEDIUM | Add `width="X" height="Y"` attributes per photo from Hugo `Process`; if masonry uses CSS columns, replace with grid + computed `grid-row: span` |
| Non-deterministic gallery order (Pitfall 5) | MEDIUM | Add `photos:` array to front matter; commit; remove any JS or Hugo `shuffle` calls |
| Missing caption silent ship (Pitfall 6) | LOW | Add `errorf` build check to `gallery/single.html`; backfill captions for existing photos |
| Lightbox a11y regression (Pitfall 8) | MEDIUM | Refactor to native `<dialog>` element with `showModal()` — gives focus trap + Esc + inert-siblings free |
| backdrop-filter jank (Pitfall 10) | LOW | Replace with flat `rgba(16, 15, 15, 0.85)` overlay; remove blur entirely |
| EXIF re-introduced (Pitfall 13) | LOW | Re-run scrub script; force-rebuild Hugo resources; verify via `exiftool` |
| Render-image hook miss (Pitfall 14) | MEDIUM | Add new arm to switch; rebuild; verify image processed at expected size |
| Pull-quote contrast regression (Pitfall 15) | LOW | Bump font-weight back to 700 OR change color to `var(--text)` + underline; re-run contrast audit |
| About CSS leak (Pitfall 17) | MEDIUM | Audit all non-scoped rules; prefix with `body.page-about`; verify via grep |
| About has stale specifics (Pitfall 18) | LOW | Move dated bullets to "Recent (2026)" section; lead with evergreen narrative |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Icon FOUC | Theme-icon phase | DevTools throttled hard-reload in dark mode; first-paint screenshot diff |
| 2. Tap target shrinkage | Theme-icon phase | `getBoundingClientRect()` ≥ 44 × 44; Lighthouse a11y |
| 3. SVG hard-coded fill | Theme-icon phase | `grep -E 'fill="#' themes/minimal/static/images/brand/*.svg` returns 0 hits |
| 4. CLS from masonry | Gallery phase | Lighthouse CLS < 0.05; Performance panel "Layout Shift" entries = 0 |
| 5. Non-deterministic order | Gallery phase | `git diff public/gallery/index.html` between rebuilds = empty |
| 6. Missing caption ship | Gallery phase | Hugo `errorf` build check; CI fails on missing |
| 7. Lazy-load lightbox conflict | Gallery phase | Slow 3G test: open lightbox before thumb 5 loads → verify full-size loads |
| 8. Focus trap / Esc / scroll-lock | Gallery phase | Keyboard-only walkthrough; VoiceOver/NVDA audit |
| 9. Reduced-motion violations | Theme-icon + Gallery phase | macOS reduce-motion ON → no animation on toggle/modal |
| 10. backdrop-filter performance | Gallery phase | DevTools Performance recording during open/close; frame rate ≥ 60fps |
| 11. Page weight blowout | Gallery phase | Total `public/gallery/photos/*.webp` size + first-paint Network panel |
| 12. ALT text dropped | Gallery phase | Front-matter array has `alt:` for every photo; VoiceOver test |
| 13. EXIF reintroduced | Gallery phase (cross-cutting) | CI exiftool gate on every push |
| 14. Render-image hook breakage | About phase | All About images render at expected size; build log has no fallthrough warnings |
| 15. Pull-quote contrast regression | About phase | Automated contrast audit (axe-core/pa11y) on dark `/about/` |
| 16. Bloat violating minimal aesthetic | About phase | Visual side-by-side with existing pages; CSS LOC delta ≤ 50 |
| 17. About CSS leaks | About phase | grep audit: all new rules under `body.page-about` |
| 18. Stale professional content | About phase | Content review: identify any specific in narrative; move to "Recent" or CV PDF |
| 19. Hero image cropping | About phase | Inspect every viewport breakpoint in build output |
| 20. Mobile reading order | About phase | Phone-emulator read-top-to-bottom audit per section |
| 21. About interactive JS one-off | About phase | `find content/about -name '*.js'` returns nothing new |
| 22. theme-color desync | Theme-icon phase | Toggle theme rapidly; verify `<meta name="theme-color">` matches `[data-theme]` always |

---

## Cross-Cutting Phase Concerns

Three pitfalls span multiple phases or apply globally:

- **EXIF privacy gate (Pitfall 13)** — should be a CI check in `.github/workflows/deploy.yml` or a pre-commit hook, not just a phase verification. Once added, it protects all future content additions.
- **Reduced-motion media query (Pitfall 9)** — applies to any new transition/animation across all phases. Codify as a CSS lint rule or PR review checklist item.
- **Generic class-name leak (Pitfall 17)** — affects About phase specifically but the principle applies to any future page redesign. Add `body.page-{type}` prefix as a stylesheet contribution rule.

---

## Sources

- `.planning/PROJECT.md` (Key Decisions table — Phase 4 P03 IIFE patterns, Phase 6 EXIF scrub, Phase 7 P01 case-sensitive filenames, Phase 7 P02 pullquote contrast, Phase 05.1 SVG `currentColor` recolor pattern)
- `.planning/MILESTONES.md` (v2.0 close summary — accessible toggle, no-FOUC inline IIFE, render-image hook keyed off image title, EXIF-scrubbed at source, ≤ 2 MB first-paint, CLS < 0.1)
- `.planning/STATE.md` (Recent decisions affecting current work — Phase 04 P03 dark-first conditional form, no-DOMContentLoaded end-of-body, Phase 7 P02 explicit `type: about` for `body.page-about` resolution, Phase 7 P02 dual-selector pattern for render-image rendering paths)
- `themes/minimal/layouts/partials/header.html` (current toggle is text `<button>Dark</button>`)
- `themes/minimal/layouts/_default/baseof.html` (head IIFE writes `data-theme` + theme-color meta; end-of-body IIFE syncs button text + aria-pressed; both scripts inline, no external JS)
- `themes/minimal/layouts/_default/_markup/render-image.html` (three-arm switch on title — hero/grid/default; defensive passthrough fallback)
- `themes/minimal/layouts/gallery/single.html` (current uniform 600×400 thumbs + 1200×1200 fulls; `aria-label` on `<a>`, `alt=""` on `<img>`)
- `themes/minimal/static/css/style.css` (Flexoki palette, `:root[data-theme="dark"]`, `body.page-about` scoping, load-bearing pullquote contrast comment at line 335-337, `prefers-reduced-motion: no-preference` gate at line 49)
- `content/about/index.md` (current hero/pullquote/grid markdown structure, dated bullets, CV PDF link)
- `content/gallery/index.md` (gallery has `build: { publishResources: false }` — originals not served)
- [How to Build Accessible Modals with Focus Traps (UXPin, 2026)](https://www.uxpin.com/studio/blog/how-to-build-accessible-modals-with-focus-traps/)
- [Modal focus trap in JavaScript and React (adropincalm)](https://adropincalm.com/blog/modal-focus-trap-in-javascript-and-react/)
- [Using JavaScript to trap focus in an element (Hidde de Vries)](https://hidde.blog/using-javascript-to-trap-focus-in-an-element/)
- [Image Aspect Ratio & Browser Quirks: Improve CLS Score (Jonathan Lau)](https://blog.jonathanlau.io/posts/layout-shifts---ssr-vs-spa-strategies-for-images/)
- [How to Fix Cumulative Layout Shift (CLS) in 2025 (Natclark)](https://natclark.com/how-to-fix-cumulative-layout-shift-cls-in-2025/)
- [Masonry layout — CSS (MDN Web Docs)](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout/Masonry_layout)

---
*Pitfalls research for: Hugo personal website v3.0 Design Update*
*Researched: 2026-05-01*

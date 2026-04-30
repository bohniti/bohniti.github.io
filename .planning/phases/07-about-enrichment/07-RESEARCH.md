# Phase 7: About Enrichment — Research

**Researched:** 2026-04-30
**Domain:** Hugo render-image hooks + image processing + leaf-bundle URL routing + Flexoki theming validation
**Confidence:** HIGH (all 10 research-flagged assumptions verified against authoritative sources or computed deterministically)

## Summary

CONTEXT.md is exhaustively prescriptive — verbatim CSS rules, full hook source, locked HTML structure, decision-by-decision audit log. This research validates the technical assumptions that the planner needs to act with confidence and surfaces three real risks that must be reflected in the plan: (1) Hugo's `Fill` action **does upscale** smaller sources by default, so a sub-480×600 portrait will be enlarged unless the plan adds a guard; (2) the dark-theme accent strong on `--bg-secondary` measures **3.97:1**, which fails WCAG AA-normal but passes AA-large — acceptable given the locked `font-size: 1.4rem; font-weight: 500`, but worth recording; (3) two of the four existing blog posts use markdown image refs with **URL-encoded spaces** (e.g., `images/Chaotic%20timeline.png`), so the render-image hook's path resolution must be validated against percent-encoded `.Destination` values during cold-build smoke.

Everything else CONTEXT.md asserts is correct as locked. The hook file location, the `.Page.Resources.GetMatch` lookup pattern, the `.Title` accessor for the `![alt](src "title")` third-tuple, the body-class scoping, the EXIF dual-defense, and Hugo's URL routing for `/about/` are all confirmed. Whitespace control with `{{- }}` works as documented. Flexoki tokens for the pull-quote read correctly in both themes (light is comfortable, dark is borderline-but-acceptable for the locked typography).

**Primary recommendation:** Proceed to plan as CONTEXT.md specifies. Add three line-item guards to whichever plan touches the render-image hook: (a) document the upscaling caveat in a comment near the `$resource.Process` call so future authors don't blindly drop a 320-px source into the hero slot, (b) verify cold-build doesn't error on the four existing blog posts that use `images/...` references with percent-encoded characters, (c) note the dark-theme contrast measurement in the HUMAN-UAT theme-parity gate (D-28) — the planner should not lower the pull-quote font-size below 1.4rem without re-checking contrast.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| URL routing for `/about/` | Hugo content router (build-time) | — | Hugo derives URL from `content/about/index.md` leaf-bundle path; no client/server logic |
| Image format conversion (JPEG → WebP) | Hugo image pipeline (build-time) | — | `image.Process` runs in Go at `hugo --minify`, output is static files |
| Image dimension declaration (CLS prevention) | Hugo render-image hook (build-time) | Browser layout (runtime) | `.Width`/`.Height` baked into `<img>` at build; browser reserves the space pre-paint |
| Lazy-loading scheduling | Browser (runtime) | — | `loading="lazy"` is a native HTML attribute; the hook only emits it |
| Theme-aware photo borders / pull-quote bg | CSS custom properties (browser runtime) | Phase 4 IIFE (browser, pre-paint) | `var(--bg-secondary)`, `var(--accent)` resolve from `[data-theme]` set by the head IIFE |
| EXIF metadata stripping | exiftool (commit-time, source-side) | Hugo WebP encoder (build-time) | Source-side strip is load-bearing; encoder drop is belt-and-suspenders |
| Markdown → HTML rendering with raw HTML wrappers | Goldmark (build-time) | — | `markup.goldmark.renderer.unsafe = true` enables wrappers; no client-side parser |
| Class-as-sizing-hint dispatch | Render-image hook (build-time) | — | Hook reads `.Title` from AST and switches on the literal value before processing |

All capabilities resolve at build time except (a) lazy-loading scheduling and (b) theme-aware CSS variable resolution — both of which are pure browser-runtime behaviors. There is no API tier, no database tier, no SSR distinction (Hugo is fully static).

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Delete `content/about.md`, replace with `content/about/index.md` leaf bundle. Order: create new bundle, verify `/about/` builds, then delete legacy file.
- **D-02:** Front matter is `title: "About"` only — no date/draft/summary/description.
- **D-03:** No new layout file. `_default/single.html` continues to render `/about/`. Structural richness via raw HTML wrappers in markdown.
- **D-04:** CSS scoping via `body.page-about` (Phase 6 D-10's body-class hook is already live in `baseof.html` line 26 — no edit required).
- **D-05:** New Hugo render-image hook at `themes/minimal/layouts/_default/_markup/render-image.html`.
- **D-06:** Title-attribute convention for class+sizing hints. `"hero"` → `fill 480x600 Smart webp q80`, `"grid"` → `fill 400x300 Smart webp q75`, default → `fill 800x600 Smart webp q78`.
- **D-07:** Hero portrait gets `loading="eager" fetchpriority="high"`. Grid + default get `loading="lazy" decoding="async"`.
- **D-08:** Hero markup is locked HTML wrapping intro + portrait image ref.
- **D-09:** Hero CSS locked: 2fr/1fr CSS Grid, 2rem desktop gap, 6px border-radius, mobile collapses to 1 column.
- **D-10:** Hero does NOT widen page canvas. About stays at `--max-width: 640px` (gallery's 1100px override remains gallery-only).
- **D-11:** One pull-quote inside Erste Group block, "40% → 95% routing accuracy", `<aside class="about-pullquote">` element.
- **D-12:** Pull-quote CSS locked: `font-size: 1.4rem`, `font-weight: 500`, `color: var(--text)`, `border-left: 4px solid var(--accent)`, `background: var(--bg-secondary)`, `border-radius: 0 4px 4px 0`. Strong tag uses `var(--accent)` + `font-weight: 700`.
- **D-13:** Photo grid at end of Interests section. 4 photos (climbing, cycling, running, cooking) wrapped in `<div class="about-grid">`.
- **D-14:** Grid CSS locked: `repeat(2, 1fr)` desktop, 1 column mobile, 0.75rem gap, 4px border-radius.
- **D-15:** 4 photos (1 per outdoor interest). Reading is omitted from grid.
- **D-16:** User must provide 5 source photos. HUMAN-UAT blocker if not selected at plan-execute time.
- **D-17:** EXIF scrub recipe identical to Phase 6 D-13: `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original` over `content/about/images/*.{jpg,jpeg,png}`, run after photos land and before commit.
- **D-18:** Hook file at `themes/minimal/layouts/_default/_markup/render-image.html`. Applies site-wide.
- **D-19:** Hook source locked verbatim (whitespace-trimming, three-arm switch on `.Title`, `<img>` with explicit width/height + lazy/eager + fetchpriority + class).
- **D-20:** Render-image hook is global — defensive fallback for non-bundle resources. Cold-build smoke on 3 named blog posts is mandatory regression guard.
- **D-21:** `/* === About === */` section in style.css placed between `/* === Gallery === */` and `/* === Footer === */`. Mobile overrides append into existing `@media (max-width: 600px)` block.
- **D-22:** No new CSS variables. About consumes existing Flexoki tokens.
- **D-23:** Verbatim copy preservation. Only structural additions: hero wrapper, pull-quote, grid wrapper.
- **D-24:** CV download link stays inline at top of hero text block.
- **D-25 → D-30:** Six verification gates (URL preservation, CLS, EXIF, theme parity, blog-post regression, content/about.md deletion).

### Claude's Discretion

- Pull-quote target metric (D-11 picks "40% → 95%"; "7,000 daily users" is alternative).
- Hero photo border-radius (6px per D-09 vs 4px matching gallery).
- Whether to add `aria-label` on grid photos (recommend NO — they don't click through).
- Whether render-image hook adds a class on the default arm (recommend NO — preserves existing `.page-content img` cascade).
- Whether to add `<picture>` srcset (recommend NO at v2.0 — single 480x600 is sufficient).
- Whether to use `body.page-about .about-hero-photo img` vs `.about-hero-img` selector (both work; class-based is more explicit).
- Grid columns: `repeat(2, 1fr)` (D-14 default) vs `repeat(auto-fit, minmax(180px, 1fr))` (recommend D-14).
- `.gitkeep` in `content/about/images/` (probably unnecessary).
- Placeholder portrait commit (recommend NO — block on real photos).

### Deferred Ideas (OUT OF SCOPE)

- Per-photo captions on hero or grid.
- Per-experience photo callouts (one photo per company in Experience section).
- Native `<dialog>` lightbox.
- `srcset` / `<picture>` for hi-DPI.
- AVIF format (Hugo 0.157 doesn't support).
- Title-keyword extension beyond `"hero"` / `"grid"` / default (additive future work).
- Generalized `.pullquote` class family.
- CV download as button-style link.
- Two-column Experience section.
- Custom 404 page.
- Lighthouse before/after delta tracking.
- Hugo render-link hook for outbound links.
- Splitting About content into structured front-matter sections.
- Photo-set rotation / randomization.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ABOUT-01 | `content/about.md` converted to `content/about/index.md` leaf bundle; URL `/about/` unchanged | § "URL Routing for /about/" (item 4) confirms both source shapes produce the same URL; Hugo emits a "pick one" warning if both exist transiently; deletion order in D-01 is correct |
| ABOUT-02 | About page displays multiple personal photos in a richer layout (second column / photo grid / pull-quote rules added to style.css) | § "CSS Interaction Risks" (item 6) confirms the locked rules in D-09/D-12/D-14 don't conflict with `.page-content img` cascade once the new classes are scoped via `body.page-about`; § "Theme Parity for Pull-Quote" (item 9) validates color-token contrast |
| ABOUT-03 | All About-page images have explicit width/height; live in `content/about/images/` as page-bundle resources | § "Hugo Image Processing for Portrait" (item 2) confirms `.Width`/`.Height` reflect processed output dimensions; § "CLS Guarantees" (item 8) confirms `<img width="480" height="600">` is sufficient for CLS < 0.1 with the hero shrink-on-mobile pattern |

## Project Constraints (from CLAUDE.md)

- **Tech stack:** Hugo static site, no JS frameworks, vanilla JS only — Phase 7 ships zero JS, fully complies.
- **Theme:** Must remain Flexoki-inspired in light + dark — Phase 7 reuses existing tokens, complies.
- **Mermaid:** Already wired (Phase 1) — Phase 7 unaffected.
- **Icon:** Should be simplistic — Phase 7 ships no icons.
- **GSD Workflow Enforcement:** All file edits must originate from a GSD command — research itself is read-only, no enforcement issue.

## Research Findings (10 items per `<research_focus>`)

### 1. Hugo render-image hook semantics

**Status:** **CONFIRMED** with one minor tightening recommendation.

- **File location:** `themes/minimal/layouts/_default/_markup/render-image.html` is the standard location for a global hook. Both `layouts/_markup/` and `layouts/_default/_markup/` work; `_default/_markup/` is the more explicit and more commonly used pattern (Bep's own `portable-hugo-links` reference repo uses it). CONTEXT.md D-18 is correct as written. [CITED: gohugo.io/render-hooks/images/, github.com/bep/portable-hugo-links]
- **Resource lookup:** `.Page.Resources.GetMatch .Destination` is the canonical form. The `printf "%s" .Destination` wrapper in D-19's locked source is **unnecessary** — `.Destination` is already a string in Hugo's hook context. The hook works either way; the planner can drop the `printf` for cleaner code or keep it for paranoid type coercion. Both are defensible. [CITED: gohugo.io/functions/resources/getmatch/, github.com/bep/portable-hugo-links/blob/master/layouts/_default/_markup/render-image.html]
- **`.Title` accessor:** Confirmed — `![alt](src "title")` makes `"title"` available as `.Title` (verified in Hugo docs example: `{{- with .Title }}<figcaption>{{ . }}</figcaption>{{ end -}}`). The three-arm switch on `eq $title "hero"` / `eq $title "grid"` / default is correct. [CITED: gohugo.io/render-hooks/images/]
- **Site-wide scope:** Confirmed — the hook fires for every markdown image reference unless overridden at a more-specific layout (e.g., `layouts/blog/_markup/render-image.html`). D-20 is correctly identified as a global change. [CITED: gohugo.io/render-hooks/images/]
- **Whitespace control:** `{{- }}` and `{{ -}}` work inside the hook body. The Hugo docs explicitly recommend whitespace-trimming "to prevent whitespace between adjacent inline elements." [CITED: gohugo.io/render-hooks/images/]
- **Defensive fallback:** The locked source in D-19's `else` arm (`<img src="{{ .Destination | safeURL }}" alt="{{ .Text }}">`) matches Bep's canonical pattern. Hugo will not throw if the lookup returns nil — the conditional handles it gracefully. [VERIFIED: github.com/bep/portable-hugo-links]

**Caveat for planner:** The `printf "%s" .Destination` in D-19 is harmless but redundant. Optional cleanup; not load-bearing.

### 2. Hugo image processing for portrait orientation

**Status:** **PARTIALLY CONFIRMED** — one real risk surfaces.

- **`fill 480x600` on a typical phone source:** Confirmed — `Fill` always crops to exactly the target dimensions regardless of source aspect ratio. A 4032×3024 landscape source crops to 480×600 (portrait); a 3024×4032 portrait source crops to 480×600 (also portrait, less aggressive). [CITED: gohugo.io/methods/resource/fill/]
- **`Smart` crop semantics:** Hugo's `Smart` anchor uses the **muesli/smartcrop** library. The library is described as "content aware" and includes "face-detection" capabilities, BUT it is primarily entropy + edge-detection-based, NOT OpenCV-grade face detection. In practice it gravitates toward high-entropy regions of the image — faces typically have high entropy (eyes, mouth contrast) so the centroid usually lands on or near a face, but it can miss when the face is small relative to a busy background. **For a portrait shot framed face-forward against a plain background, `Smart` will reliably crop on the face.** For a wide-angle landscape shot of a person standing in a climbing crag, it might prefer the wall texture over the climber's face. [CITED: github.com/muesli/smartcrop, discourse.gohugo.io/t/manually-set-anchor-point/16654]
- **Upscaling behavior — RISK:** **`Fill` DOES upscale by default** when the source is smaller than the target. A 320×480 source asked for `fill 480x600` produces a 480×600 output by interpolating up — the result is blurry. Hugo discourse explicitly confirms this and recommends pre-checking source dimensions. [CITED: discourse.gohugo.io/t/why-does-resize-increase-the-image-size-even-when-the-original-asset-size-is-smaller/56244]
- **`.Width` / `.Height` on processed resource:** Confirmed — both reflect the **processed (output)** dimensions, not the source. So `<img width="{{ $processed.Width }}" height="{{ $processed.Height }}">` correctly emits `width="480" height="600"` for the hero. [CITED: gohugo.io/methods/resource/fill/, gohugo.io/methods/resource/width/]

**Caveat for planner:** Add a planning task or verification step that confirms the user-provided portrait source is **at least 480 px wide and 600 px tall** to avoid silent upscaling. Practically: any modern phone shot will easily exceed this; the risk is only if the user crops a thumbnail or hands over a low-res profile pic. A one-line `identify content/about/images/portrait.jpg` (ImageMagick) or a Python `Pillow` check during the photo-arrival task is sufficient.

### 3. Markdown image title-tuple parsing

**Status:** **CONFIRMED**.

- `![alt](src "title")` is **CommonMark / GFM standard syntax** — the third tuple position is the title attribute. Goldmark passes it unchanged to the render-image hook as `.Title`. The Hugo docs example shows it explicitly: `{{- with .Title }}<figcaption>{{ . }}</figcaption>{{ end -}}`. [CITED: spec.commonmark.org §6.4 Images, gohugo.io/render-hooks/images/]
- An empty title (`![alt](src)`) sets `.Title = ""`. The `else` arm in D-19's three-way switch correctly catches this case.

**Caveat for planner:** None. The CONTEXT.md convention is on solid ground.

### 4. Hugo URL routing transition

**Status:** **CONFIRMED** with documented transient warning.

- Both `content/about.md` and `content/about/index.md` produce URL `/about/`. [CITED: gohugo.io/content-management/organization/]
- **When BOTH exist:** Hugo emits the warning `"Content directory have both index.* and _index.* files, pick one"` (the warning text mentions `_index.*` but the same condition triggers for `about.md` + `about/index.md` because they collide on the same destination URL). The leaf bundle (`content/about/index.md`) **wins** in Hugo's resolution order, but the warning is loud and CI/CD pipelines that treat warnings as errors will fail. [CITED: discourse.gohugo.io/t/warning-both-index-and-index-files-pick-one/32224]
- **Order of operations safe:** D-01's prescription is correct. Create `content/about/index.md`, run `hugo --minify` once to verify it builds and `/about/` is served from the bundle (the warning is acceptable for this transient verification step), then delete `content/about.md` and rebuild. The deployed build (the actual `git push` commit) must NOT contain both files.

**Caveat for planner:** The plan should split "create bundle" and "delete legacy" into two distinct commits OR a single commit that does both atomically. A transient state where both files coexist in committed history is acceptable only if it doesn't ship to production. Recommend the single-commit-both-changes pattern for minimum surface area.

### 5. Cross-page render-hook risk (D-20)

**Status:** **CONFIRMED with one new finding**.

Existing markdown image references in blog posts (grep `!\[.*\](images/` over `content/blog/`):

| Post | Markdown image refs (count) | Path notes |
|------|----------------------------|------------|
| `/blog/2026-03-05-activity-overview/` | 1 | `images/activities_by_year.png` — clean ASCII |
| `/blog/2026-03-15-intervals-copilot/` | 2 | `images/latest-activity.png`, `images/summary.png` — clean ASCII |
| `/blog/2026-03-27-video-editing-journey/` | 5 | **3 with URL-encoded spaces:** `images/Chaotic%20timeline.png`, `images/Clip%20catalog%20spreadsheet.png`, `images/Insta360%20+%20DaVinci%20side-by-side.png`. **2 clean:** `images/before-color.png`, `images/after-color.png` |
| `/blog/2026-03-05-climbing-routes/` | 0 | Uses inline `<div>` + `<script>` for Leaflet/Plotly viz, no markdown images |

**No raw `<img>` tags in any blog post** (verified by grep `<img` over `content/blog/` — zero hits). All blog images go through Goldmark → render-image hook.

**The percent-encoding finding is new and load-bearing:** the hook receives `.Destination = "images/Chaotic%20timeline.png"`. Hugo's `.Page.Resources.GetMatch` is **glob-pattern-based** and the underlying matching logic does NOT URL-decode by default. The actual resource on disk is `images/Chaotic timeline.png` (literal space). The lookup may fail because the glob pattern matches `Chaotic%20timeline.png` against a file named `Chaotic timeline.png`. The hook would then fall through to the default fallback arm (which is correctly defensive — it emits a plain `<img src="images/Chaotic%20timeline.png">`, and the browser URL-decodes the path on fetch, so the image still renders). However, this means **those three images would NOT get the Hugo-WebP-convert + lazy-load treatment** — they'd fall back to passthrough JPEG/PNG.

**For Phase 7's narrow scope, this is acceptable** — those three images already render correctly today (they hit the fallback arm and produce identical output to the pre-hook behavior). The cold-build smoke (D-29) will verify this. Phase 7 does not need to fix the percent-encoding gap; that's an opportunistic future improvement.

[VERIFIED: grep results above; gohugo.io/functions/resources/getmatch/]

**Caveat for planner:** During the cold-build smoke (D-29), explicitly verify that `/blog/2026-03-27-video-editing-journey/` renders all 5 images correctly (look for any 404s in the network tab and any visually missing images). If the percent-encoded files break, the hook needs an additional `urlPath := .Destination | urlUnescape` step before `GetMatch` — but this is a **regression-only fix**, not a planned work item.

### 6. CSS interaction risks

**Status:** **CONFIRMED safe**.

The existing rule at `style.css:222` is:
```css
.page-content img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 1.5rem 0;
}
```

The locked About hero CSS in D-09 is:
```css
body.page-about .about-hero-photo img {
  width: 100%;
  height: auto;
  border-radius: 6px;
  display: block;
}
```

**Specificity analysis:**
- `.page-content img` → specificity (0,1,1) = 11
- `body.page-about .about-hero-photo img` → specificity (0,2,2) = 22
- `body.page-about .about-grid img` → specificity (0,2,1) = 21

About's selectors win every contest. The `width: 100%` declaration overrides `max-width: 100%` (both work to size to the container; `width: 100%` is more emphatic, no conflict). The `border-radius: 6px` overrides the inherited `4px` cleanly. The `display: block` is additive (not in the base rule).

**One actual risk:** `.page-content img { margin: 1.5rem 0 }` cascades onto About's hero and grid images because the new About rules don't reset margin. For the hero, this adds 1.5rem top+bottom inside the grid cell — **probably what we want** (separates the photo from the cell edges in the 2fr/1fr layout). For the grid, `margin: 1.5rem 0` would create huge vertical gaps between rows in the 2-column grid layout. **The planner should add `margin: 0` to `body.page-about .about-grid img`** to neutralize this, OR rely on the `display: block` to suppress the inline margin (CSS Grid items have no margin collapse but still respect inline margin, so the explicit reset is the safe move).

[VERIFIED: codebase grep at style.css:222]

**Caveat for planner:** Add `margin: 0` to the `body.page-about .about-grid img` rule. Either include this in the locked CSS (D-14 should be amended) or add as a planning sub-task. This is a one-property addition; no design impact.

### 7. EXIF stripping verification

**Status:** **CONFIRMED**.

- Hugo's WebP encoder (powered by `golang.org/x/image/webp`) does NOT preserve JPEG EXIF metadata during format conversion — by default, the EXIF block is dropped because WebP and JPEG use different metadata containers. [CITED: pkg.go.dev/golang.org/x/image/webp, gohugo.io/content-management/image-processing/ "Metadata is not preserved during image transformation"]
- However, this is **format-conversion-side** behavior — if the source JPEG remains in `content/about/images/` (it does, as the originals are committed alongside the bundle), then `git show` and `exiftool content/about/images/*.jpg` would still expose EXIF on the source files. **Source-side strip is the load-bearing layer for git-history privacy** (D-17 prescription is correct).
- `[imaging.exif] disableLatLong = true` (already in `hugo.toml` from Phase 6) only affects the EXIF block embedded in the rare cases where Hugo DOES preserve metadata (e.g., JPEG → JPEG resize without `webp` keyword). For WebP output it's a no-op belt-and-suspenders.
- The verification gate (`exiftool public/about/images/*.webp` reports zero GPS/Make/Model/Serial) is a strict downstream check; Phase 6's gate passed, so the same recipe applies cleanly here.

**Caveat for planner:** None — D-17 mirrors Phase 6 D-13 verbatim and Phase 6 already validated.

### 8. CLS guarantees

**Status:** **CONFIRMED**.

- `<img width="480" height="600">` with browser-default CSS produces an aspect-ratio-locked layout box: the browser uses the width/height attributes to compute the implied `aspect-ratio: auto 480/600` and reserves the correct vertical space pre-paint. [CITED: web.dev/learn/design/responsive-images/, web.dev/articles/optimize-cls/]
- The CSS rule `width: 100%; height: auto` (D-09) **does NOT break this** — modern browsers compute the aspect ratio from the width/height attributes first, then apply CSS to scale within that ratio. The image fluidly sizes to the container width while maintaining the aspect ratio. CLS stays at 0.
- **At the mobile breakpoint** (the hero column shrinks from `2fr/1fr` to `1fr` single-column at 600px), the photo's rendered width grows from ~213 px (1/3 of 640 px content width minus gap) to ~600 px (full mobile content width). The reserved height adjusts proportionally — the layout shift is during the breakpoint flip, not during page paint. CLS is measured during paint, so this doesn't count against the metric.

[VERIFIED: web standards behavior, no codebase risk]

**Caveat for planner:** None — the hook emitting `.Width`/`.Height` from the processed resource is the correct CLS-prevention mechanism.

### 9. Theme parity for the pull-quote

**Status:** **PARTIALLY CONFIRMED — one borderline AA-normal failure flagged**.

Computed WCAG contrast ratios using the standard sRGB → relative luminance formula (W3C WCAG 2.1 algorithm):

| Pairing | Foreground | Background | Ratio | AA-normal (≥4.5) | AA-large (≥3.0) |
|---------|-----------|-----------|-------|------------------|-----------------|
| Light: pull-quote text on bg-secondary | `#100F0F` | `#F2F0E5` | **16.74:1** | PASS | PASS |
| Light: accent strong on bg-secondary | `#AF3029` | `#F2F0E5` | **5.61:1** | PASS | PASS |
| Dark: pull-quote text on bg-secondary | `#CECDC3` | `#1C1B1A` | **10.77:1** | PASS | PASS |
| Dark: accent strong on bg-secondary | `#D14D41` | `#1C1B1A` | **3.97:1** | **FAIL** | PASS |
| Light: accent left-border on page bg | `#AF3029` | `#FFFCF0` | **6.23:1** | PASS | PASS |
| Dark: accent left-border on page bg | `#D14D41` | `#100F0F` | **4.42:1** | PASS (barely) | PASS |

**Real risk: dark-mode `<strong>` accent text inside the pull-quote measures 3.97:1.** This is below WCAG AA-normal (4.5:1) but above AA-large (3:1). WCAG defines "large text" as **≥18pt OR ≥14pt bold**. The locked CSS for `<strong>` is `font-weight: 700` at the inherited 1.4rem (≈22.4px ≈ 16.8pt). At 16.8pt **bold**, this clears the 14pt-bold threshold and qualifies as large text — so it **does pass AA at the locked typography**. If the planner ever lowers the pull-quote `font-size` below 1.4rem or drops `<strong>`'s weight below 700, the dark-theme strong text falls below AA. Worth a comment in the CSS or a HUMAN-UAT note.

[VERIFIED: WCAG 2.1 contrast formula, computed in Python; W3.org WCAG 2.1 §1.4.3]

**Caveat for planner:** Add a code comment in the CSS section at the `body.page-about .about-pullquote strong` rule:
```css
/* Dark-mode #D14D41 on #1C1B1A measures 3.97:1 — passes WCAG AA only because the
   inherited 1.4rem + font-weight:700 qualifies as "large text". Do not reduce
   font-size or font-weight here without re-checking contrast. */
```
Also note in the D-28 theme-parity HUMAN-UAT gate: visually verify the dark-mode pull-quote strong text remains readable at typical viewing distance.

### 10. Project-skill check

**Status:** **CONFIRMED no project-local skills exist**.

- `ls .claude/skills/` returns no directory.
- `ls .agents/skills/` returns no directory.
- The only `.claude/` content is `worktrees/` and `settings.local.json` — no skill rules to load.

[VERIFIED: filesystem inspection]

**Caveat for planner:** None — proceed with the standard GSD workflow without project-skill overrides.

## Standard Stack

### Core (already in place — no installs)

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Hugo Extended | 0.157.0 | Static site generation, image processing, render hooks | Pinned in `.github/workflows/deploy.yml`; required for `image.Process` WebP support |
| Goldmark | bundled with Hugo 0.157 | Markdown → HTML with `unsafe = true` for raw HTML wrappers | CommonMark + GFM compliance; fires render hooks on every image |
| muesli/smartcrop | bundled with Hugo's image pipeline | `Smart` anchor entropy-based crop centroid | Hugo default for content-aware crop |
| exiftool | system binary, version-agnostic | Pre-commit EXIF strip on source JPEG/PNG | Phase 6 validated; standard privacy hygiene tool |

### Supporting (already in place)

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| Python 3 + Pillow | system | Optional pre-commit dimension check on user-provided photos | If automating "is portrait source ≥ 480×600?" guard from item 2 |
| ImageMagick `identify` | system | Same purpose as Pillow | Lighter-weight one-liner; either works |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Render-image hook | Per-image Hugo shortcode (`{{< photo src="..." class="hero" >}}`) | Shortcode is more verbose in markdown but more explicit. Hook stays in plain markdown — better. |
| `.Title` switch on `"hero"` / `"grid"` | Front-matter `photos:` array with class metadata | Front-matter array is more flexible but requires layout-template support. Title-attribute is zero-template-change. Better. |
| `image.Process` Smart anchor | Manual focal-point per photo via `.Anchor` | Manual is more reliable for tricky compositions but requires per-photo curation. Smart is good enough for portrait + standard-composition outdoor candids. |
| Source-side exiftool scrub | Hugo `[imaging.exif]` block alone | `[imaging.exif] disableLatLong` only handles GPS for the rare format-preserving path. Source-side is load-bearing for Make/Model/Serial. Both together = belt-and-suspenders (Phase 6 D-13 pattern). |

**Installation:** None. All required tools are already on the system (Hugo via CI, Python+Pillow via stdlib, exiftool already validated in Phase 6).

**Version verification:** Hugo Extended 0.157.0 confirmed pinned in `.github/workflows/deploy.yml`. No `npm install` step required for Phase 7. [VERIFIED: codebase inspection]

## Architecture Patterns

### System Architecture Diagram

```
                        AUTHOR
                           │
                ┌──────────┴───────────┐
                │ Edit Markdown        │
                │ + place photos       │
                └──────────┬───────────┘
                           │
                  ┌────────▼─────────┐
                  │ exiftool scrub   │  ← pre-commit, source-side
                  │ (D-17)           │
                  └────────┬─────────┘
                           │
                       git commit
                           │
                           ▼
                  ┌──────────────────┐
                  │ hugo --minify    │  ← BUILD-TIME
                  └────────┬─────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────────┐     ┌──────────────────────┐
    │ Goldmark         │     │ Static asset copy    │
    │ Markdown parser  │     │ (CSS, fonts, etc.)   │
    └────────┬─────────┘     └──────────┬───────────┘
             │                          │
             │ ![alt](images/x "hero")  │
             ▼                          │
    ┌──────────────────────┐            │
    │ render-image.html    │            │
    │ HOOK (D-19)          │            │
    │                      │            │
    │ - GetMatch resource  │            │
    │ - Switch on .Title   │            │
    │   ├─ "hero" → 480×600│            │
    │   ├─ "grid" → 400×300│            │
    │   └─ default → 800×600│           │
    │ - image.Process      │            │
    │   webp + Smart crop  │            │
    │ - Emit <img> with    │            │
    │   .Width/.Height +   │            │
    │   loading + class    │            │
    │ - Fallback to plain  │            │
    │   <img> if no resource           │
    └────────┬─────────────┘            │
             │                          │
             ▼                          │
    ┌──────────────────────┐            │
    │ public/about/index.html  ◄────────┤
    │ public/about/images/*.webp │      │
    │ public/css/style.css      ◄───────┘
    └──────────┬───────────┘
               │ git push
               ▼
       GitHub Pages CDN
               │
               ▼
            BROWSER
   ┌────────────────────────────┐
   │ Phase 4 head IIFE:         │
   │   set [data-theme]         │
   │ CSS resolves Flexoki tokens│
   │   for active theme         │
   │ Browser layout reserves    │
   │   width/height pre-paint   │
   │ Lazy images deferred       │
   │   until viewport intersect │
   │ Hero image fetched eager   │
   │   with fetchpriority=high  │
   └────────────────────────────┘
```

### Recommended Project Structure

```
content/
└── about/                          # NEW leaf bundle (D-01)
    ├── index.md                    # NEW — front matter + raw-HTML-wrapped markdown (D-23)
    └── images/                     # NEW page-bundle resource dir (D-16)
        ├── portrait.jpg            # 1 portrait, EXIF-scrubbed
        ├── climbing.jpg            # 4 candids
        ├── cycling.jpg
        ├── running.jpg
        └── cooking.jpg

themes/minimal/
├── layouts/
│   └── _default/
│       ├── baseof.html             # READ-ONLY (Phase 6 already has body-class)
│       ├── single.html             # READ-ONLY (renders /about/ unchanged)
│       └── _markup/
│           └── render-image.html   # NEW (D-05, D-19)
└── static/css/
    └── style.css                   # EDIT — append /* === About === */ section (D-21)

content/about.md                    # DELETE after bundle verified (D-30)
```

### Pattern 1: Render-image hook with title-keyword switch

**What:** Read `.Title` from the markdown image's third tuple, switch on the literal string, dispatch to different `image.Process` specifications.

**When to use:** Whenever a single hook needs to vary processing per image without authoring shortcodes or restructuring content into front matter.

**Example:** [Source: D-19 locked verbatim, validated against gohugo.io/render-hooks/images/]
```go-html-template
{{- $resource := .Page.Resources.GetMatch .Destination -}}
{{- if $resource -}}
  {{- $title := .Title | default "" -}}
  {{- $processed := "" -}}
  {{- if eq $title "hero" -}}
    {{- $processed = $resource.Process "fill 480x600 Smart webp q80" -}}
  {{- else if eq $title "grid" -}}
    {{- $processed = $resource.Process "fill 400x300 Smart webp q75" -}}
  {{- else -}}
    {{- $processed = $resource.Process "fill 800x600 Smart webp q78" -}}
  {{- end -}}
  <img src="{{ $processed.RelPermalink }}"
       width="{{ $processed.Width }}"
       height="{{ $processed.Height }}"
       alt="{{ .Text }}"
       {{- if eq $title "hero" }} class="about-hero-img" loading="eager" fetchpriority="high"
       {{- else if eq $title "grid" }} class="about-grid-item" loading="lazy" decoding="async"
       {{- else }} loading="lazy" decoding="async"{{ end -}}>
{{- else -}}
  <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}"{{ with .Title }} title="{{ . }}"{{ end }}>
{{- end -}}
```

### Pattern 2: Body-class CSS scoping (Phase 6 inheritance)

**What:** `<body class="page-{{ .Type | default "default" }}">` in `baseof.html` (already shipped Phase 6 line 26) emits `page-about` on About, enabling `body.page-about .x` selectors to scope without affecting other pages.

**When to use:** Any page-type-specific styling (gallery did wider canvas; about does hero/grid/pullquote).

**Example:** [Source: codebase verified, baseof.html:26]
```css
body.page-about .about-hero { display: grid; grid-template-columns: 2fr 1fr; ... }
body.page-about .about-grid { display: grid; grid-template-columns: repeat(2, 1fr); ... }
body.page-about .about-pullquote { background: var(--bg-secondary); ... }
```

### Pattern 3: Raw HTML class hooks in markdown

**What:** Wrap markdown content with `<div class="...">` to add layout structure without splitting content into front-matter fields.

**When to use:** When the content is best authored as flowing markdown (paragraphs, lists, headings) but needs structural CSS hooks (grid, flex, callout). Requires `markup.goldmark.renderer.unsafe = true` (already enabled).

**Example:** [Source: D-08 locked]
```html
<div class="about-hero">
  <div class="about-hero-text">

## Hi, I'm Timo.

Markdown content stays as markdown — Goldmark renders inner blocks
because of the blank lines around them and `unsafe = true`.

  </div>
  <div class="about-hero-photo">

![Portrait of Timo](images/portrait.jpg "hero")

  </div>
</div>
```

### Anti-Patterns to Avoid

- **Per-image shortcode** (`{{< photo src="..." class="hero" >}}`) — verbose, requires authors to remember a non-markdown idiom, and breaks if the shortcode template needs editing later. The render-image hook is invisible to the author and stays in plain markdown.
- **Splitting About content into front-matter sections** — would force a custom `layouts/about/single.html` template iterating through experiences/education/certifications arrays. Larger refactor with no rendering benefit (D-03 prohibits).
- **Using `<picture>` with srcset for the hero** — adds template complexity for a single-image use case where the rendered widths stay below 480 px on desktop and 100% screen width on mobile (≤ ~430 px on a typical phone). Hi-DPI gain is marginal at this scale (Web.dev: "When in doubt, omit srcset"). Out of scope per CONTEXT.md.
- **Manual `<img>` HTML inside markdown** — bypasses the render-image hook entirely. Loses CLS-safe width/height + lazy-loading + WebP conversion. Use the markdown image syntax + title-attribute hint instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image format conversion (JPEG → WebP) | A custom Python pre-processor or a build-time JS task | Hugo's `image.Process "... webp ..."` | Already in Hugo, already validated Phase 6, integrated with the resource cache, atomic with the markdown render hook |
| EXIF stripping at the JPEG level | Custom Python script with `piexif` | `exiftool` CLI (Phase 6 D-13 pattern) | Battle-tested, audited recipe, supported on macOS/Linux/Windows, fast |
| Smart crop centroid detection | OpenCV face-detection script + manual focal-point picker | Hugo `Smart` anchor (muesli/smartcrop) | Built into Hugo image pipeline; entropy-based crop is good enough for portrait + outdoor candid shots |
| CLS-safe image sizing | A JS script that measures `naturalWidth`/`naturalHeight` and writes `<img width=... height=...>` post-hydration | `<img width="{{ .Width }}" height="{{ .Height }}">` emitted at build by the render hook | Build-time emission means no JS, zero CLS, native browser support |
| Lazy-loading with intersection observer | Custom IntersectionObserver script | Native `loading="lazy"` attribute | Browser-native, supported in Chrome 76+, Safari 15.4+, Firefox 75+; one HTML attribute |
| Theme-aware photo borders | JS that listens for theme toggle and updates border colors | CSS custom properties (`var(--border)`) inside the rule | Phase 4's `[data-theme]` already drives token resolution; CSS handles the swap with no JS |

**Key insight:** Phase 7 introduces zero new runtime infrastructure — every dynamic behavior (theme switch, lazy-load, CLS prevention) is either build-time (Hugo render hook + image.Process) or browser-native (CSS custom properties, native HTML attributes). The render-image hook is the only new piece of "code," and it's a 25-line Go template that executes once per `hugo --minify`.

## Common Pitfalls

### Pitfall 1: `Fill` upscales smaller sources silently

**What goes wrong:** A user-provided portrait at 320×480 gets upscaled by `Fill` to 480×600, producing a blurry hero image.

**Why it happens:** Hugo's `Fill` action does NOT short-circuit when the source is smaller than the target — it interpolates pixels.

**How to avoid:** Verify source dimensions before plan-execute commits photos. One-line check: `python3 -c "from PIL import Image; im=Image.open('content/about/images/portrait.jpg'); print(im.size)"` — confirm ≥ 480×600 for the portrait, ≥ 400×300 for grid candids.

**Warning signs:** The hero photo looks softer than the source preview. Compare pixel-peep at 100% in the deployed `/about/` against the source file.

### Pitfall 2: Render-image hook silently breaks legacy blog images on percent-encoded paths

**What goes wrong:** Blog images like `images/Chaotic%20timeline.png` (with URL-encoded space) fail `GetMatch` lookup because the literal filename on disk is `Chaotic timeline.png` (no encoding). The hook falls through to the fallback arm — image still renders, but as the original PNG, not as a Hugo-WebP-converted lazy-loaded variant. Phase 7 doesn't break the page; it just doesn't get the upgrade.

**Why it happens:** Hugo's `Resources.GetMatch` is glob-pattern-based and does NOT URL-decode the path before matching.

**How to avoid:** Either (a) accept the limitation for Phase 7 (the fallback is correct and the page still works), or (b) add `{{ $path := .Destination | urlUnescape }}` and pass `$path` to `GetMatch`. CONTEXT.md doesn't mandate (b); planner can defer it.

**Warning signs:** During cold-build smoke (D-29), open `/blog/2026-03-27-video-editing-journey/` and check if the three percent-encoded images load as `.png` (passthrough) instead of `.webp` (upgraded). Either is acceptable for Phase 7 — `.png` passthrough is the same behavior as before the hook landed.

### Pitfall 3: Both `content/about.md` and `content/about/index.md` exist in a deploy commit

**What goes wrong:** Hugo builds, emits the "pick one" warning, the leaf bundle wins, but CI/CD pipelines that treat warnings as errors fail the build. Even without strict CI, the warning is noisy in logs.

**Why it happens:** Author creates the bundle, runs `hugo` to verify, forgets to delete the legacy file before commit.

**How to avoid:** D-01's order of operations is correct. Plan should commit the deletion atomically with the bundle creation, OR ensure the deletion lands before `git push`.

**Warning signs:** `hugo --minify` outputs a warning containing `pick one` or `both index.* and _index.*`. Grep build output for "WARN" before pushing.

### Pitfall 4: Margin cascade from `.page-content img` adds vertical gaps to the photo grid

**What goes wrong:** The existing `.page-content img { margin: 1.5rem 0 }` rule cascades onto About's `.about-grid img`. In a 2-column grid, this adds 1.5rem above and below each grid cell — making the grid look airy and broken.

**Why it happens:** The new About CSS in D-14 doesn't reset margin. Specificity is correct (About wins); the issue is About just doesn't override the margin property.

**How to avoid:** Add `margin: 0` to `body.page-about .about-grid img` (and arguably `body.page-about .about-hero-photo img`, though there 1.5rem is plausibly desirable as inner padding).

**Warning signs:** Visual smoke shows the grid photos visually disconnected with too much space between rows. Inspect the grid `<img>` element's computed style and look for `margin: 24px 0` (1.5rem default).

### Pitfall 5: Pull-quote dark-mode strong text borderline contrast

**What goes wrong:** Dark-mode `<strong>40% → 95%</strong>` measures 3.97:1 against `#1C1B1A` bg-secondary. Passes AA-large (because `font-size: 1.4rem` × `font-weight: 700` qualifies as large text per WCAG), but only by virtue of the bold weight. If a future edit reduces the weight or font-size, contrast slips below AA.

**Why it happens:** Flexoki's dark accent (`#D14D41`) is intentionally muted to avoid eye strain on dark surfaces; the tradeoff is reduced contrast against a near-black bg.

**How to avoid:** Add a code comment in the CSS at the `body.page-about .about-pullquote strong` rule warning future authors. Verify visually during D-28 theme-parity HUMAN-UAT.

**Warning signs:** Dark-mode `<strong>` text appears washed-out or hard to read at typical viewing distance. WebAIM Contrast Checker (or `python -c "..."` formula) shows ratio < 3.0 if the typography is reduced.

## Code Examples

### Example 1: The full render-image.html hook (D-19 source, validated)

```go-html-template
{{- /*
  Render-image hook (Phase 7 D-19).
  Resolves bundle-relative markdown image refs to Hugo-processed WebP <img> tags
  with explicit width/height (CLS-safe), lazy/eager loading, and optional class.

  Title-attribute convention (third tuple of ![alt](src "title")):
    "hero"  → fill 480x600 Smart webp q80, eager + fetchpriority=high, class="about-hero-img"
    "grid"  → fill 400x300 Smart webp q75, lazy + decoding=async, class="about-grid-item"
    (none)  → fill 800x600 Smart webp q78, lazy + decoding=async, no extra class

  Out-of-bundle resources (static/, external URLs, percent-encoded paths that don't match)
  fall through to a passthrough <img> — preserves existing blog post behavior.
*/ -}}
{{- $resource := .Page.Resources.GetMatch .Destination -}}
{{- if $resource -}}
  {{- $title := .Title | default "" -}}
  {{- $processed := "" -}}
  {{- if eq $title "hero" -}}
    {{- $processed = $resource.Process "fill 480x600 Smart webp q80" -}}
  {{- else if eq $title "grid" -}}
    {{- $processed = $resource.Process "fill 400x300 Smart webp q75" -}}
  {{- else -}}
    {{- $processed = $resource.Process "fill 800x600 Smart webp q78" -}}
  {{- end -}}
  <img src="{{ $processed.RelPermalink }}"
       width="{{ $processed.Width }}"
       height="{{ $processed.Height }}"
       alt="{{ .Text }}"
       {{- if eq $title "hero" }} class="about-hero-img" loading="eager" fetchpriority="high"
       {{- else if eq $title "grid" }} class="about-grid-item" loading="lazy" decoding="async"
       {{- else }} loading="lazy" decoding="async"{{ end -}}>
{{- else -}}
  <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}"{{ with .Title }} title="{{ . }}"{{ end }}>
{{- end -}}
```

### Example 2: The locked About CSS section (D-09, D-12, D-14, with margin-reset addition from item 6)

```css
/* === About === */
body.page-about .about-hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: start;
  margin-bottom: 2.5rem;
}

body.page-about .about-hero-photo img,
body.page-about .about-hero-img {
  width: 100%;
  height: auto;
  border-radius: 6px;
  display: block;
}

body.page-about .about-pullquote {
  font-size: 1.4rem;
  font-weight: 500;
  line-height: 1.4;
  color: var(--text);
  border-left: 4px solid var(--accent);
  padding: 0.5rem 0 0.5rem 1.25rem;
  margin: 1.75rem 0;
  background: var(--bg-secondary);
  border-radius: 0 4px 4px 0;
}

body.page-about .about-pullquote strong {
  color: var(--accent);
  font-weight: 700;
  /* Dark-mode #D14D41 on #1C1B1A measures 3.97:1 — passes WCAG AA only because the
     1.4rem font-size + 700 weight qualifies as "large text". Do not reduce font-size
     or font-weight here without re-checking contrast. */
}

body.page-about .about-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin: 1.5rem 0 0;
}

body.page-about .about-grid img,
body.page-about .about-grid-item {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
  margin: 0;     /* override .page-content img { margin: 1.5rem 0 } cascade */
}

/* === Footer === */ (existing — no edit)

/* === Responsive === */ (existing — append two rules)
@media (max-width: 600px) {
  /* ... existing rules ... */
  body.page-about .about-hero { grid-template-columns: 1fr; gap: 1.5rem; }
  body.page-about .about-grid { grid-template-columns: 1fr; }
}
```

### Example 3: Pre-commit photo dimension check (Pillow one-liner)

```bash
python3 -c "
from PIL import Image
import sys
mins = {'portrait.jpg': (480, 600), 'climbing.jpg': (400, 300),
        'cycling.jpg': (400, 300), 'running.jpg': (400, 300),
        'cooking.jpg': (400, 300)}
ok = True
for name, (mw, mh) in mins.items():
    p = f'content/about/images/{name}'
    try:
        w, h = Image.open(p).size
        if w < mw or h < mh:
            print(f'FAIL {name}: {w}x{h} (need >= {mw}x{mh}) — Hugo Fill will upscale, expect blurriness')
            ok = False
        else:
            print(f'OK   {name}: {w}x{h}')
    except FileNotFoundError:
        print(f'MISSING {p}')
        ok = False
sys.exit(0 if ok else 1)
"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Plain `<img src=...>` in markdown without dimensions | Render-image hook emits explicit width/height | Hugo 0.62 (2020) added image render hooks; widely adopted by 2022 | CLS-safe by default; no JS needed |
| Per-image shortcode for processing | Default render hook with title-attribute hint | Hugo 0.93+ encouraged hooks over shortcodes for image markdown | Plain markdown stays plain; authors don't memorize shortcodes |
| `srcset` + `<picture>` for every responsive image | Single Hugo-processed WebP with CSS `width: 100%; height: auto` | 2023 Web.dev guidance: "When in doubt, omit srcset" | Simpler markup; hi-DPI gain is marginal at small rendered sizes |
| OS-specific image converters (sips, ImageMagick scripts) | Hugo's built-in `image.Process` with WebP encoder | Hugo 0.83+ unified image processing | Cross-platform, cached, integrated with content pipeline |
| Manual EXIF strip post-hoc | exiftool source-side strip + Hugo `[imaging.exif] disableLatLong` | Phase 6 (this codebase) validated 2026-04-30 | Audit-friendly; source files clean in git |

**Deprecated/outdated:**

- `<img loading="lazy">` polyfills (lozad.js, lazysizes) — native `loading="lazy"` is supported in all modern browsers; polyfills add JS for marginal benefit.
- Per-image shortcodes for resource lookup — render hooks let authors stay in plain markdown.
- AVIF — Hugo 0.157 doesn't support; revisit when Hugo upgrades (likely 0.158+, no firm date).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Hugo's WebP encoder drops JPEG EXIF Make/Model/Serial as a side effect of format conversion | item 7 | Low — D-17 source-side scrub is the load-bearing layer; encoder behavior is belt-and-suspenders. Phase 6 already validated empirically. |
| A2 | The dark-theme pull-quote `font-size: 1.4rem; font-weight: 700` qualifies as "large text" per WCAG | item 9 | Low — 1.4rem ≈ 22.4px ≈ 16.8pt with bold weight clearly clears the 14pt-bold threshold. If the planner reduces typography, the contrast drops below AA. |
| A3 | A typical user-provided portrait phone shot is ≥ 480×600 in the cropped/native output | item 2 | Medium — modern phones produce ≥ 3024×4032; the only failure mode is if the user crops to a thumbnail before placement. The Pillow check (Example 3) detects this. |
| A4 | The percent-encoded blog post image references in `/blog/2026-03-27-video-editing-journey/` will fail `GetMatch` and fall through to the passthrough fallback (rendering correctly but unconverted) | item 5 | Low — even if the failure mode is different, the fallback arm is defensive and emits a working `<img>`. Cold-build smoke (D-29) validates. |

If the planner wants to eliminate A3's medium-risk assumption, add a sub-task to the photo-arrival plan that runs the Pillow dimension check before commit.

## Open Questions

1. **Whether the planner includes the percent-encoding `urlUnescape` fix**
   - What we know: the existing fallback handles it correctly (renders unconverted), so the page works.
   - What's unclear: whether the planner considers it Phase 7 scope to give those three blog images the WebP-conversion + lazy-load upgrade.
   - Recommendation: defer. The fallback is correct; the upgrade is opportunistic. Track as a future follow-up.

2. **Whether the cold-build CI cache invalidates on the new render-hook landing**
   - What we know: `resources/_gen/images/` is gitignored and CI uses `HUGO_CACHEDIR` per Phase 6 D-21. The first build with the hook active reprocesses every blog post image (~10–20s expected per Phase 6 estimate). After that, cached.
   - What's unclear: whether GitHub Actions' temp-dir cache survives across runs (likely no — fresh runner each time).
   - Recommendation: accept the one-time cold-build cost; it's bounded and only matters for the first deploy with the hook active.

3. **Pull-quote target metric**
   - What we know: D-11 picks "40% → 95%". Alternatives: "7,000 daily users", "2nd place at hackathon".
   - What's unclear: user preference. Each is defensible.
   - Recommendation: ship "40% → 95%" per D-11; surface as a one-line variation point in HUMAN-UAT — easy revert if user prefers another.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Hugo Extended | Build pipeline (CI) | ✓ (CI) / ✗ (local — per CLAUDE.md "Hugo is NOT installed locally") | 0.157.0 (CI pinned) | Local dev: install Hugo via `brew install hugo` or run via Docker. Production untouched (CI-driven). |
| Python 3 + Pillow | Pre-commit dimension check (Example 3) | ✓ Python 3 system; Pillow stdlib NOT included | system Python | If Pillow missing: `python3 -c "from PIL import Image"` → `ModuleNotFoundError`. Fallback: `identify content/about/images/*.jpg` (ImageMagick) if available, or skip the check (treat as risk per item 2). |
| exiftool | EXIF source-side scrub (D-17) | ✓ (Phase 6 already used) | system | None — Phase 6 validated; no fallback needed. |
| ImageMagick `identify` | Alternative pre-commit dimension check | unknown | system | Equivalent to Pillow; either is fine. |

**Missing dependencies with no fallback:** None — all critical-path tools (Hugo via CI, exiftool) are confirmed available.

**Missing dependencies with fallback:** Local Hugo install (CI is the source of truth; local builds optional). Pillow/ImageMagick (the dimension check is a guard against pitfall #1, not a hard-required step).

## Validation Architecture

> Skipped — `.planning/config.json` would need inspection to confirm `workflow.nyquist_validation`. Cursory check: no `.planning/config.json` discovered in standard inspections; based on Phase 6 plan structure (which used HUMAN-UAT gates and verification commands without a formal test framework), this codebase is **manual-verification-driven, not test-framework-driven**. The validation strategy for Phase 7 is the six gates D-25 through D-30 (URL preservation, CLS Lighthouse, EXIF check, theme parity, blog regression, content/about.md deletion). No `pytest` / `vitest` / `jest` infrastructure exists.

If `.planning/config.json` does set `nyquist_validation: true`, the Validation Architecture should document each gate as a manual-only verification command (`hugo --minify`, `exiftool`, Lighthouse Mobile, visual smoke). I've intentionally not synthesized a full Validation Architecture table without confirming the config flag — including a fabricated test-framework table would be worse than omitting the section.

**Per-gate commands (extracted from D-25–D-30 for direct planner consumption):**

```bash
# D-25 URL preservation gate
hugo --minify
test -f public/about/index.html && head -20 public/about/index.html | grep -q 'about-hero'

# D-26 CLS gate (manual Lighthouse Mobile run on /about/, target CLS < 0.1)

# D-27 EXIF gate
exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber \
  public/about/images/*.webp 2>/dev/null
# Expected: zero matching field reports

# D-28 Theme parity gate (manual: load /about/, toggle light↔dark, eyeball check
#   hero photo + pullquote + grid)

# D-29 Blog post regression gate
rm -rf resources && hugo --minify
# Manually verify /blog/2026-03-05-climbing-routes/, /blog/2026-03-05-activity-overview/,
# /blog/2026-03-27-video-editing-journey/ render images correctly

# D-30 content/about.md deletion gate
test ! -f content/about.md
grep -r "content/about\.md" . --include="*.md" --include="*.toml" --include="*.html" 2>/dev/null
# Expected: zero hits (or only references in .planning/ historical context)
```

## Security Domain

> `security_enforcement` setting not inspected (no `.planning/config.json` discovered). Treating as enabled per default.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Static site, no auth surface |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | All pages public |
| V5 Input Validation | partial | User-provided photos go through Hugo's image pipeline (build-time, trusted source); markdown content is authored by the site owner |
| V6 Cryptography | no | No crypto operations |
| V7 Error Handling | partial | Hugo build errors surface in CI logs; render-hook fallback prevents broken-image errors at runtime |
| V12 Files and Resources | yes | Static assets served from GitHub Pages CDN; `static/` and `public/` are the only writable surfaces (committed via git) |
| V14 Configuration | yes | `hugo.toml`, GitHub Actions workflow, GitHub Pages settings — all in version control |

### Known Threat Patterns for Hugo + GitHub Pages + EXIF

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| EXIF metadata leak (GPS / camera serial) revealing personal location & equipment | Information Disclosure | exiftool source-side strip (D-17) + `[imaging.exif] disableLatLong` (already in hugo.toml) |
| Render-hook breaking on adversarial markdown input | Denial of Service (build-time) | Defensive `else` arm (D-19); hook never throws on missing resources |
| XSS via raw HTML in markdown (`unsafe = true`) | Tampering | Content is authored by site owner only; no user-submitted markdown. `unsafe = true` is the existing site setting and Phase 7 doesn't change the threat surface. |
| Path-traversal via `.Destination` in render hook | Tampering | `GetMatch` operates within page bundle scope; cannot escape the resource directory. Hugo enforces this. |
| Stale image cache exposing old EXIF after a re-scrub | Information Disclosure | `resources/_gen/images/` is gitignored; CI builds fresh, so deployed output reflects the latest scrubbed sources. Local stale cache only affects the developer's machine. |

**Privacy hard launch gate (D-27):** zero matches for `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, `SerialNumber`, `InternalSerialNumber` on `public/about/images/*.webp` after `hugo --minify`. Block ship on any hit. Same scrutiny as Phase 6 GAL-06.

## Sources

### Primary (HIGH confidence)

- [Hugo Image Render Hooks Reference](https://gohugo.io/render-hooks/images/) — confirmed `.Title`, `.Text`, `.Destination`, file location, whitespace control, fallback behavior
- [Hugo Image Processing Reference](https://gohugo.io/content-management/image-processing/) — confirmed `Process` method, `Fill` action, `Smart` anchor, supported actions
- [Hugo `Resources.GetMatch` Reference](https://gohugo.io/functions/resources/getmatch/) — confirmed glob-pattern matching, no URL-decoding behavior
- [Hugo `Fill` Method Reference](https://gohugo.io/methods/resource/fill/) — confirmed `Fill` always crops to exact target dimensions; upscaling caveat documented in discourse
- [Bep `portable-hugo-links` GitHub repo (Hugo author's reference implementation)](https://github.com/bep/portable-hugo-links/blob/master/layouts/_default/_markup/render-image.html) — confirmed canonical `Resources.GetMatch .Destination` pattern + fallback shape
- [Hugo Content Organization Reference](https://gohugo.io/content-management/organization/) — confirmed `content/about.md` and `content/about/index.md` produce same URL
- [WCAG 2.1 §1.4.3 Contrast (Minimum)](https://www.w3.org/TR/WCAG21/#contrast-minimum) — large text definition (≥14pt bold or ≥18pt regular), AA threshold (4.5:1 normal, 3:1 large)
- [CommonMark Specification §6.4 Images](https://spec.commonmark.org/0.31.2/#images) — confirmed `![alt](src "title")` syntax with title attribute
- Codebase inspection: `themes/minimal/layouts/_default/baseof.html`, `single.html`, `static/css/style.css`, `content/about.md`, `hugo.toml`, `content/blog/*/index.md` — verified body-class hook on line 26, current CSS rules, existing image refs

### Secondary (MEDIUM confidence)

- [Hugo discourse: "Why does .Resize increase image size when source is smaller?"](https://discourse.gohugo.io/t/why-does-resize-increase-the-image-size-even-when-the-original-asset-size-is-smaller/56244) — confirmed Fill upscales by default (community-confirmed; not in primary docs)
- [Hugo discourse: "WARNING: both index.* and _index.* files, pick one"](https://discourse.gohugo.io/t/warning-both-index-and-index-files-pick-one/32224) — confirmed warning text and behavior when both exist
- [Hugo discourse: "Manually set anchor point for Image Processing"](https://discourse.gohugo.io/t/manually-set-anchor-point-for-image-processing/16654) — Smart anchor behavior community description
- [muesli/smartcrop GitHub README](https://github.com/muesli/smartcrop) — content-aware crop algorithm description (entropy + edge-detection + face-detection-light)
- WCAG contrast ratios computed via standard sRGB → relative luminance formula in Python (deterministic; result-equivalent to WebAIM Contrast Checker)

### Tertiary (LOW confidence — cross-verified)

- None — all findings have at least two corroborating sources or direct codebase inspection.

## Metadata

**Confidence breakdown:**

- **Standard stack:** HIGH — Hugo 0.157.0 pinned in CI, exiftool validated Phase 6, render-image hook is core Hugo functionality with reference implementation by Hugo's author
- **Architecture patterns:** HIGH — render-image hook + body-class scoping + raw-HTML-in-markdown are all established Hugo patterns with codebase precedent (Phase 6)
- **Pitfalls:** HIGH — Fill upscaling, percent-encoding gap, CSS margin cascade, contrast borderline are all verified through docs + codebase inspection + deterministic computation
- **CSS interaction:** HIGH — specificity calculations are deterministic; codebase already-shipped Phase 6 validates body-class-scoping pattern
- **Theme parity:** HIGH — WCAG ratios computed deterministically; the dark-mode AA-normal failure is a real measurement, not a guess

**Research date:** 2026-04-30
**Valid until:** 2026-05-30 (30 days for Hugo + render-hook semantics; Hugo 0.157 is pinned so no version drift expected)

## RESEARCH COMPLETE

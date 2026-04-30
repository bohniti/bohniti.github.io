# Phase 6: Gallery - Research

**Researched:** 2026-04-30
**Domain:** Hugo Extended 0.157.0 image processing pipeline + EXIF privacy + CSS Grid
**Confidence:** HIGH on stack; HIGH on empirical photo measurements; MEDIUM on cold-build timing (no local Hugo)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Leaf bundle at `content/gallery/index.md` + `photos/` subdir as page-bundle resources. Front matter: `title: "Gallery"` only.
- **D-02:** Layout file `themes/minimal/layouts/gallery/single.html` (NOT a `_default/single.html` conditional).
- **D-03:** Resource iteration via `.Resources.Match "photos/*"` (glob, not `.ByType "image"`).
- **D-04:** Photos render in alphabetical order by filename (Hugo default for `.Resources.Match`).
- **D-05:** First 3 photos load `eager`; remaining 15 load `lazy`.
- **D-06:** `fetchpriority="high"` on the first photo only.
- **D-07:** Each thumbnail wrapped in `<a>` linking to full-size processed WebP `.RelPermalink`. No JS lightbox, no `target="_blank"`.
- **D-08:** Grid markup `<div class="gallery-grid">` of 18 `<a class="gallery-item">` children. CSS locks `repeat(auto-fill, minmax(220px, 1fr))`, `gap: 1rem`. `.gallery-item` uses `display: block; line-height: 0`. `.gallery-img` uses `width: 100%; height: auto; display: block; border-radius: 4px`.
- **D-09:** `body.page-gallery .site-wrapper { max-width: 1100px; }` — wider canvas scoped to gallery only.
- **D-10:** `<body class="page-{{ .Type | default "default" }}">` added in `baseof.html`. One-line edit.
- **D-11:** Mobile breakpoint at `@media (max-width: 600px)` — `auto-fill` "naturally collapses to 1 column at narrow viewports because `minmax(220px, 1fr)` won't fit two 220 px columns in 600 px minus padding". **NOTE: empirically wrong — see § Open Questions Q1; collapses to 1 col only below ~488 px viewport.**
- **D-12:** `[[menu.main]]` Gallery entry: `name = "Gallery", url = "/gallery/", weight = 2`. About bumps to `weight = 3`. Order: Blog → Gallery → About.
- **D-13:** Two-pronged EXIF: (a) `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original` on sources before commit, (b) `[imaging.exif] disableLatLong = true` in `hugo.toml`.
- **D-14:** Verification gate (run before phase commit): `hugo --minify` then `exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber public/gallery/photos/*.{webp,jpg}` — zero matching field reports across all renditions.
- **D-15:** Source filenames preserved during move (no kebab-case normalization, no extension lowercasing).
- **D-16:** `git mv images/galary content/gallery/photos`, then run exiftool scrub in place, then `git add` modified files.
- **D-17:** `images/galary/` fully removed after move. Verified via `test ! -d images/galary` + `grep -r galary content/ themes/ hugo.toml || echo "No hits — clean"`.
- **D-18:** All 18 thumbnails carry `alt=""` (empty, decorative).
- **D-19:** No `[imaging]` quality default — per-call `q75` / `q82` are explicit and auditable. Only `[imaging.exif]` block touched.
- **D-20:** No `srcset` / `<picture>` element — `auto-fill` + `minmax(220px, 1fr)` handles responsive layout.
- **D-21:** Hugo image cache lives at `resources/_gen/images/` (gitignored). CI uses fresh cache via `HUGO_CACHEDIR` per-run.

### Claude's Discretion

- CSS-rule placement in `style.css` — between `/* === Single Post / Page === */` and `/* === Footer === */` (recommended) or after `/* === Responsive === */`.
- `aria-label="Open full-size photo {{ $idx }}"` on `<a class="gallery-item">` since `alt=""`. Recommend yes (the link still needs an accessible name).
- `:focus-visible` outline on `.gallery-item` for keyboard nav. Recommend yes (parity with existing `.site-nav a:focus-visible`).
- `decoding="async"` alongside `loading="lazy"` on lazy thumbnails. Recommend yes (Web.dev guidance).
- `{{ with .Resources.Match "photos/*" }}` guard around resource iteration. Recommend yes (defensive).
- Body class form `page-{{ .Type }}`. Recommend `page-{{ .Type }}` per D-10.
- Pre-CI cold-build smoke test (delete `resources/`, run `hugo --minify`, verify all 36 renditions). Recommend yes.
- Whether to commit `.gitkeep`/`README.md` inside `content/gallery/photos/`. Probably unnecessary if move + commit is atomic.
- Additional exiftool flags (e.g., `-CommonIFD0=`). D-14 verification gate catches leftovers.

### Deferred Ideas (OUT OF SCOPE)

- Native `<dialog>`-based lightbox (REQUIREMENTS § Future).
- Per-photo captions / front-matter `photos:` array (REQUIREMENTS § Future).
- Per-photo curated ordering (REQUIREMENTS § Future).
- `srcset` / `<picture>` for hi-DPI thumbnails (D-20 omits).
- AVIF format (Hugo 0.157 doesn't support).
- Hugo render-image hook for blog post images (out of Phase 6 scope).
- View-transition API on click-through.
- PWA caching of the gallery.
- Filter / search / tag UI (REQUIREMENTS § Out of Scope).
- Photo metadata sidebar (would re-expose EXIF Phase 6 just stripped).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GAL-01 | User can navigate to `/gallery/` from main header navigation | § Hugo Body-class Injection; § Hugo Leaf Bundle (menu integration via `hugo.toml`) |
| GAL-02 | `/gallery/` displays 18 photos in CSS Grid `repeat(auto-fill, minmax(220px, 1fr))` with `max-width` override | § CSS Grid Auto-fill Behavior; § Hugo Body-class Injection |
| GAL-03 | Thumbnails: Hugo `Process "fill 600x400 Smart webp q75"`, lazy/eager mix, explicit width/height | § Hugo Image Processing Reference; § fetchpriority/loading/decoding |
| GAL-04 | Click-through to full-size WebP via `Process "fit 1600x1600 webp q82"` — no JS lightbox | § Hugo Image Processing Reference (Fit semantics) |
| GAL-05 | First-paint ≤ 2 MB; total `public/gallery/` ≤ 3 MB | § Empirical Findings (per-photo size projection) |
| GAL-06 | Zero `GPSLatitude`, `GPSLongitude`, `Make`, `Model`, `Serial*` fields after build | § exiftool Invocation Reference; § Hugo `[imaging.exif]` and EXIF Strategy; § Empirical Findings (which sources have EXIF) |
| GAL-07 | `images/galary/` retired, photos moved to `content/gallery/photos/`, no `galary` references | § Hugo Leaf Bundle + Resource Iteration; D-16 `git mv` strategy |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Tech stack:** Hugo static site, no JS frameworks, keep it minimal.
- **Theme:** Must fit existing Flexoki-inspired minimal aesthetic.
- **Mermaid:** Hugo needs to render Mermaid diagrams (irrelevant to gallery scope).
- **Icon:** Should be simplistic, matching site's minimal design (irrelevant to gallery scope).
- **GSD workflow:** Use `/gsd:execute-phase` for planned work; do not bypass GSD for direct edits.
- **Hugo Extended 0.157.0** pinned in `.github/workflows/deploy.yml`.
- **Single CSS file** at `themes/minimal/static/css/style.css`.
- **Page-bundle convention** for blog posts; same shape applies to gallery.
- **Goldmark `unsafe = true`** allows raw HTML in markdown (irrelevant — gallery template emits raw HTML, not markdown).
- **Privacy settings** disable Disqus, Google Analytics, Twitter/X.
- **No third-party Python packages** required for any utility scripts.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Page rendering (`/gallery/`) | Hugo Build (Static Generation) | — | Fully resolved at build time; output is static HTML |
| Image transcoding (JPEG → WebP) | Hugo Build (libvips/imaging Go pkg) | — | `image.Process` runs at build, output cached at `resources/_gen/images/` |
| EXIF stripping (source-side) | Pre-Build (exiftool one-shot) | Hugo Build (re-encode drops most EXIF) | Manual one-shot during Phase 6 execution; not a recurring pipeline |
| EXIF stripping (output-side) | Hugo Build (`[imaging.exif] disableLatLong`) | — | Belt-and-suspenders for re-encoded output |
| Responsive grid layout | Browser / Client (CSS Grid) | — | `auto-fill` + `minmax` runs in CSS layout engine, no JS |
| Lazy-loading thumbnails | Browser / Client (HTML `loading=lazy`) | — | Native browser feature; no JS, no Intersection Observer |
| Click-through navigation | Browser / Client (`<a href>`) | — | Native HTML link, browser back button restores scroll |
| Theme inheritance (light/dark) | Browser / Client (CSS `var(--*)` via Phase 4 `[data-theme]`) | — | Photos themselves are theme-agnostic; only `.gallery-img` border-radius / focus-outline pick up theme tokens |
| Asset hosting | CDN / Static (GitHub Pages) | — | All output served as-is; no server-side processing |

## Summary

**Phase 6 implements a standalone `/gallery/` Hugo leaf bundle** that processes 18 personal photos into thumbnail (600×400 fill webp q75) and full-size (1600×1600 fit webp q82) WebP renditions, displayed in a CSS Grid with native lazy-loading. The architecture is fully static — every transformation happens at Hugo build time; the browser only renders pre-baked HTML and pre-baked WebP files. There is no JavaScript on the gallery page beyond the existing site-wide theme bootstrap inherited from `baseof.html`.

**Empirical photo audit is the load-bearing finding of this research:** of the 18 source files, 11 still carry full EXIF metadata (Make=Apple/Sony/samsung, Model=iPhone 15 Pro / ILCE-7RM3 / iPhone 14 Pro / iPhone 13 / iPhone 12 / SM-G930F, Software=18.5/v3.10/etc., creation timestamps); 7 UUID-named files appear pre-stripped (likely Telegram-downloaded). Hugo's `image.Process` re-encoding to WebP drops most EXIF as a side effect, but the **source-side `exiftool` scrub is the load-bearing privacy guarantee** — `[imaging.exif] disableLatLong = true` only handles GPS lat/long and only in Hugo's *resource-metadata extraction*, not in the encoded output. macOS `sips` cannot read GPS, so the GPS-presence check requires `exiftool` to run for the first time during phase execution (neither tool is currently installed on the dev machine).

**Primary recommendation:** Install `exiftool` and `hugo` via Homebrew before Phase 6 task execution begins (`brew install exiftool hugo`). Run a cold-build smoke test against the actual 18 photos before committing the layout — this surfaces any Smart-crop failures empirically (Smart has no face detection, only edge/skin/saturation scoring, so the iPhone portrait `5dc795b8…` 720×1280 source is the highest-risk candidate). Total processed-output size is projected at ~700 KB-1.2 MB for thumbnails and ~3-5 MB for full-size renditions; the **2 MB first-paint budget will pass** (only 3 thumbnails load above-fold, ~150 KB), but the **3 MB total budget for `public/gallery/` is at risk** if WebP encoder produces full-size files larger than ~150 KB each on average. Plan a measure-then-adjust loop: if `du -sh public/gallery/` exceeds 3 MB, lower full-size quality from q82 → q78 (cache invalidates automatically via the spec-string cache key).

## Hugo Image Processing Reference

### `Process` Method Syntax `[VERIFIED: gohugo.io/methods/resource/process/]`

The processing specification is "**a space-delimited, case-insensitive list containing one or more of the following options in any sequence**" — token order is **not enforced**.

General form: `action WIDTHxHEIGHT [anchor] [format] [qQUALITY] [other options]`

**Supported actions:** `crop`, `fill`, `fit`, `resize` — "If you specify an action, you must also provide dimensions."
**Supported output formats:** `bmp`, `gif`, `jpeg`, `png`, `tiff`, `webp` (defaults to source format if omitted).
**Quality syntax:** `qQUALITY` where QUALITY is a whole number 1–100 inclusive.

The locked specs `"fill 600x400 Smart webp q75"` and `"fit 1600x1600 webp q82"` are **valid in Hugo 0.157+**. (Cross-verified against gohugo.io/methods/resource/fill/ and gohugo.io/methods/resource/fit/.)

### Fill Semantics (thumbnails) `[VERIFIED: gohugo.io/methods/resource/fill/]`

`Fill` "returns a new image resource cropped and resized" — it always produces output at exactly the specified dimensions, **cropping** the source to fit. For portrait sources scaled to a 600×400 landscape thumbnail, Smart picks the crop centroid.

**Anchor values (9 valid):** `TopLeft`, `Top`, `TopRight`, `Left`, `Center`, `Right`, `BottomLeft`, `Bottom`, `BottomRight`, `Smart`.

### Smart Crop Algorithm `[VERIFIED: github.com/muesli/smartcrop source]`

Hugo's `Smart` anchor delegates to **muesli/smartcrop**, a pure-Go port of Jonas Wagner's smartcrop.js. The scoring function is a weighted combination of three components:

| Component | Weight | What it scores |
|-----------|--------|----------------|
| **Detail (edge detection)** | 0.2 | Lightness differences between adjacent pixels |
| **Skin detection** | 1.8 | Color match against reference skin tone `[0.78, 0.57, 0.44]` with brightness thresholds |
| **Saturation detection** | 0.3 | Vibrant/colorful regions |

Plus rule-of-thirds positioning bonus and an `importance()` weighting that biases toward crop center.

**CRITICAL: Smart crop has NO face detection.** It scores skin tone and edges, not faces. Failure modes:
- Group portraits where faces span the full frame: skin-detection picks the largest skin region (one face), other faces may be cropped out.
- Subjects against busy/colorful backgrounds: the saturation score may pull the centroid toward the background.
- Portrait-orientation photos cropped to landscape (e.g., the `5dc795b8…` 720×1280 source → 600×400 fill): Smart picks the highest-scoring 600×400 window from the 720×800-equivalent vertical slice — most likely the upper-body / face region, but no guarantee.

**Mitigation if Smart fails empirically:** Per-photo override using a non-Smart anchor (`Center`, `Top`, etc.) requires per-resource template logic — not in scope for the alphabetical-iteration loop. Document the failure and ship; add front-matter per-photo anchor overrides as a future enhancement.

### Fit Semantics (full-size) `[VERIFIED: gohugo.io/methods/resource/fit/]`

> "Unlike `Fill` or `Resize`, this method will never upscale an image; if the source image is smaller than the target dimensions, the dimensions of the resulting image are the same as the original."

So `Process "fit 1600x1600 webp q82"` on the 720×1280 portrait source produces 720×1280 WebP at q82 (no upscale). On the 7952×5304 SONY source it produces 1600×1067 WebP. **All 18 sources are fine — none lose detail to upscaling.**

### Width/Height Properties `[VERIFIED: gohugo.io/content-management/image-processing/]`

Processed resources expose `.Width` and `.Height` — these are **post-processing** dimensions, suitable for emitting as HTML attributes to prevent CLS. The CONTEXT.md D-07 markup sample `width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"` is correct.

### Caching Behavior `[VERIFIED: gohugo.io/configuration/caches/]`

- Default cache location: `:resourceDir/_gen` (i.e., `resources/_gen/images/`).
- Default `maxAge: -1` means "never expires."
- The cache key includes the **full processing spec string** — so changing `q75` → q76` produces a new cache entry, the old one stays until `hugo --gc` runs or `resources/` is deleted manually `[VERIFIED: glukhov.org/post/2025/11/hugo-caching-strategies/]`.
- `--minify` does NOT affect image processing — it only minifies HTML, CSS, JS, JSON, SVG, XML output `[VERIFIED: medium.com Sparisoma Viridi article + Hugo discourse]`.

### Format Conversion Side Effects

When Hugo re-encodes JPEG → WebP via `image.Process`, it routes through Go's image/jpeg decoder + the github.com/golang/image/webp encoder (Hugo Extended only — confirmed via the `_extended` build flag in CI). The WebP encoder does **not preserve JPEG EXIF** — most EXIF is dropped as a side effect of format conversion `[ASSUMED based on Go stdlib behavior]`. However, this is an implementation detail, not a guaranteed contract — the source-side exiftool scrub remains load-bearing for the audit trail.

## Hugo `[imaging.exif]` and EXIF Strategy

### Configuration Reference `[VERIFIED: gohugo.io/configuration/imaging/]`

The `[imaging.exif]` block configures **how Hugo extracts EXIF metadata from source files for use in templates** (e.g., `.Exif.Tags.GPSLatitude`). It does **NOT** configure EXIF preservation in processed output — Hugo's WebP encoder produces WebP without EXIF baseline.

| Option | Default | What it does |
|--------|---------|--------------|
| `disableLatLong` | `false` | When `true`, prevents extraction of GPS lat/long from source EXIF — `.Exif.Lat` and `.Exif.Long` are unavailable in templates |
| `disableDate` | `false` | When `true`, prevents extraction of date metadata |
| `excludeFields` | `GPS\|Exif\|Exposure[M\|P\|B]\|Contrast\|Resolution\|Sharp\|JPEG\|Metering\|Sensing\|Saturation\|ColorSpace\|Flash\|WhiteBalance` | Regex pattern of EXIF tag fields excluded from extraction |
| `includeFields` | `""` | Regex pattern of EXIF tag fields to explicitly include |

### What `disableLatLong = true` Actually Guarantees

**For the gallery use case where Phase 6 does not read EXIF in templates at all (no `.Exif.*` invocations):** `disableLatLong = true` is **functionally a no-op** — Hugo isn't writing extracted EXIF anywhere; the field already gets dropped during WebP encoding regardless.

**Why ROADMAP success criterion 3 mandates it anyway:** belt-and-suspenders. The setting is a documented, auditable signal in `hugo.toml` that the build pipeline is privacy-conscious. If a future template ever does `{{ with .Exif.Lat }}…{{ end }}`, the setting prevents accidental lat/long leakage.

**Source files are NEVER touched by Hugo's imaging config.** All EXIF stripping on the source files (which are committed to git) requires the **source-side exiftool scrub** (D-13 prong 1).

### What This Means for the Audit Trail

| Layer | What it strips | What it does NOT strip |
|-------|---------------|------------------------|
| **Source-side `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original`** | All GPS tags, Make, Model, SerialNumber, InternalSerialNumber from source JPEGs in `content/gallery/photos/` (committed to git) | Other potentially-identifying tags (LensSerialNumber, BodySerialNumber, OwnerName, Artist, Copyright, Software, DateTimeOriginal) — see § exiftool Invocation Reference for completeness audit |
| **Hugo `[imaging.exif] disableLatLong = true`** | GPS lat/long from EXIF *extraction in templates* — only matters if templates read `.Exif.Lat` | All other EXIF (Hugo doesn't strip from output; the WebP encoder happens to drop most of it as a side effect) |
| **Hugo WebP encoder (side effect)** | All EXIF — encoder produces WebP without EXIF baseline `[ASSUMED]` | None known |

## exiftool Invocation Reference

### Tool Availability `[VERIFIED: which exiftool]`

`exiftool` is **NOT installed** on the current dev machine (`brew info exiftool` confirms `Not installed`). Phase 6 execution must begin with:

```bash
brew install exiftool   # installs exiftool 13.55+
exiftool -ver           # verify install (expect 13.x)
```

### Source-Side Scrub Command (D-13)

The CONTEXT.md-locked invocation:

```bash
cd content/gallery/photos
exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original ./*
```

`[VERIFIED: exiftool.org/exiftool_pod.html]`:
- `-TAG=` (no value) deletes the tag.
- `-GPS:All=` deletes all tags in the GPS group (equivalent to `-GPS:*=`).
- `-overwrite_original` "overwrite the original FILE (instead of preserving it by adding `_original` to the file name)" — implemented as a temp-file rename.
- Wildcards `*` and `?` work in tag names — so `-Serial*=` would match SerialNumber, InternalSerialNumber, LensSerialNumber, BodySerialNumber.

### Field Coverage Audit

The locked invocation covers Make, Model, SerialNumber, InternalSerialNumber explicitly. **Potentially-missed fields that warrant consideration:**

| Field | Risk | Recommendation |
|-------|------|----------------|
| `LensSerialNumber` | Camera-identifying | Add `-Serial*=` to collapse all Serial variants `[VERIFIED]` |
| `BodySerialNumber` | Camera-identifying | Covered by `-Serial*=` |
| `OwnerName` | User-identifying (some Apple/Sony cameras populate) | Add `-OwnerName=` |
| `Artist` | User-identifying (rare on phones; common on DSLR) | Add `-Artist=` |
| `Copyright` | User-identifying (rare on phones) | Add `-Copyright=` |
| `Software` | Camera/OS version (low risk, but identifying) | Optional `-Software=` |
| `DateTimeOriginal` | Time-of-capture (low privacy risk; Phase 6 doesn't use it for ordering) | Leave intact (D-04 uses alphabetical, not date-based) |

**Recommended hardened invocation** (covers ROADMAP success criterion 3 with margin):

```bash
exiftool \
  -GPS:All= \
  -Make= -Model= \
  -Serial*= \
  -OwnerName= -Artist= -Copyright= \
  -overwrite_original \
  ./*
```

Wildcard `-Serial*=` collapses SerialNumber, InternalSerialNumber, LensSerialNumber, BodySerialNumber into one rule. Adding `-OwnerName= -Artist= -Copyright=` is cheap insurance against camera firmware that auto-populates these from settings.

**Nuclear option (if absolute minimum metadata is preferred):** `exiftool -all= -overwrite_original ./*` strips ALL metadata. Tradeoff: also drops orientation (rotation flag), color profile, and date — but Hugo's `images.AutoOrient` filter and embedded color profile are not relied on by Phase 6 (alphabetical sort, not date; and re-encoding to WebP normalizes color space). **Caveat:** deleting orientation EXIF before Hugo processes the image may cause portraits to render sideways if the JPEG had `Orientation: Rotated 90 CW` and the actual pixel data wasn't pre-rotated. Sample 1-2 photos with `-all=` first to verify.

### Verification Gate (D-14)

```bash
hugo --minify

# Verify zero matching fields across all output renditions
exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber \
  public/gallery/photos/*.{webp,jpg} 2>/dev/null
# Expected output: each file lists tags it CONTAINS — empty output = zero matches = PASS
```

Note: `exiftool -TAG file.webp` prints `TAG: value` only when the tag is present. **An empty stdout block is the success signal.** A non-empty line means a tag survived; treat as ship-blocker.

**Edge case:** the glob `public/gallery/photos/*.{webp,jpg}` may not match if the shell is `sh` (no brace expansion). The CI runs bash (`defaults: run: shell: bash`), and macOS zsh supports it natively. Document the bash dependency.

## Hugo Leaf Bundle + Resource Iteration

### Lookup Order for `Type=gallery` `[VERIFIED: gohugo.io/templates/lookup-order/]`

For `content/gallery/index.md` (leaf bundle), Hugo sets:
- `.Section = "gallery"` (top-level section)
- `.Type = "gallery"` (inferred from section name unless front-matter override)
- `.Kind = "page"` (leaf bundle is always Kind=page)

Layout lookup chain for the gallery single page (most-specific first):
1. `layouts/gallery/single.html` ← **D-02 target**
2. `layouts/_default/single.html`

Hugo resolves `gallery/single.html` first when it exists. No front-matter `layout:` override needed (per CONTEXT.md D-02).

### Type Quirk: Homepage `[VERIFIED: discourse.gohugo.io/t/home-page-type-is-unexpected/25200]`

Hugo's `.Type` documentation: "Is value of `type` if set in front matter, else it is the name of the root section. **It will always have a value, so if not set, the value is 'page'.**"

**Implication for D-10:** `<body class="page-{{ .Type | default "default" }}">` produces:

| Page | `.Type` | Body class |
|------|---------|------------|
| Homepage `/` | `"page"` | `page-page` |
| `/gallery/` | `"gallery"` | `page-gallery` ← target for D-09 CSS |
| `/about/` (current `content/about.md`) | `"page"` | `page-page` |
| Blog post `/blog/2026-03-27-video-editing-journey/` | `"blog"` | `page-blog` |
| Blog list `/blog/` | `"blog"` | `page-blog` |

**The `default "default"` fallback never fires** because `.Type` always has a value. This is harmless — the body class is always valid — but planners should be aware: the "homepage gets `page-default`" mental model is wrong. Homepage gets `page-page`. (If the user later wants a distinct homepage class, use `{{ if .IsHome }}home{{ else }}page-{{ .Type }}{{ end }}` instead.)

### `.Resources.Match "photos/*"` Glob Behavior `[VERIFIED: gohugo.io image-processing docs]`

For a leaf bundle at `content/gallery/index.md` with photos at `content/gallery/photos/*.jpg`:

- `.Resources.Match "photos/*"` returns all resources matching the glob, **sorted alphabetically by name** (Hugo default).
- `*` matches any character except `/` — so `"photos/*"` does NOT recurse into subdirectories. With the flat `photos/` directory (D-15 preserves filenames, no subdirs), this is correct.
- Glob is case-sensitive on the filename pattern (`*` matches `.jpg`/`.JPG`/`.jpeg` equally — extension agnostic). Confirmed via existing CONTEXT.md analysis.

### Iteration Pattern with `$idx` (per D-05/D-06)

```go-html-template
{{ with .Resources.Match "photos/*" }}
  <div class="gallery-grid">
    {{ range $idx, $photo := . }}
      {{ $thumb := $photo.Process "fill 600x400 Smart webp q75" }}
      {{ $full  := $photo.Process "fit 1600x1600 webp q82" }}
      <a class="gallery-item"
         href="{{ $full.RelPermalink }}"
         aria-label="Open photo {{ add $idx 1 }} of {{ len $.Resources }} in full size">
        <img class="gallery-img"
             src="{{ $thumb.RelPermalink }}"
             width="{{ $thumb.Width }}"
             height="{{ $thumb.Height }}"
             loading="{{ if lt $idx 3 }}eager{{ else }}lazy{{ end }}"
             {{ if eq $idx 0 }}fetchpriority="high"{{ end }}
             {{ if ge $idx 3 }}decoding="async"{{ end }}
             alt="">
      </a>
    {{ end }}
  </div>
{{ end }}
```

**Verification points:**
- `{{ range $idx, $photo := . }}` — Hugo Go-template syntax for iterating with index `[VERIFIED]`. The two-value range is identical to Go's `range` over slices.
- `$photo.Process` — `image.Process` is a **method on Resource**, not on `.Site` or anything else. Invoke as `$photo.Process "spec"` or `.Process "spec"` inside a `with` `[VERIFIED]`.
- `add $idx 1` — converts 0-indexed to 1-indexed for human-readable aria-label `[VERIFIED]`.
- `len $.Resources` — `$` references the parent context (page), avoids the `.` rebind from `range` `[VERIFIED]`.

## fetchpriority / loading / decoding

### fetchpriority Browser Support `[VERIFIED: caniuse.com/mdn-html_elements_img_fetchpriority]`

| Browser | Min Version | Notes |
|---------|-------------|-------|
| Chrome | 101+ | First implementation |
| Edge | 101+ | Identical to Chrome |
| Firefox | 132+ | Added October 2024 |
| Safari (Desktop) | 17.2+ | Added Dec 2023 |
| Safari iOS | 17.2+ | Same as desktop |

Global usage as of March 2026: **93.28%** `[VERIFIED: caniuse]`. Older browsers ignore the attribute gracefully — no breakage, just no priority hint.

### Values

| Value | Meaning |
|-------|---------|
| `high` | Fetch this resource at high priority relative to other resources of the same type |
| `low` | Fetch at low priority |
| `auto` | Default — no preference |

**Web.dev guidance `[CITED: web.dev/articles/fetch-priority]`:** Use sparingly. The classic LCP pattern is "exactly one above-fold image with `fetchpriority='high'`" — adding `high` to multiple images creates contention for the same priority slot and can starve the CSS download. CONTEXT.md D-06 (`fetchpriority="high"` on first photo only) matches this guidance exactly.

### loading=lazy / loading=eager

`loading="eager"` is the **default** on `<img>` — adding it explicitly to the first 3 photos (D-05) is functionally redundant but **harmless and self-documenting** (a future maintainer reading the template doesn't have to know the default). The CONTEXT.md markup sample emits the explicit attribute.

`loading="lazy"` defers fetch until the image approaches the viewport. Browser heuristics:
- Chrome / Safari / Firefox respect `loading="lazy"` for offscreen images.
- Some browsers (Chrome 77-89 era) had quirky behavior loading lazy images that were within ~3000px of viewport — modern browsers (2025+) have tightened to ~1250px or use Intersection Observer-equivalent thresholds.
- **`loading="lazy"` may be ignored if the browser determines the image is above-the-fold during initial layout.** Not a correctness issue — just means the image loads anyway, which is fine.

### decoding=async

`decoding="async"` `[VERIFIED: web.dev guidance]` tells the browser to decode the image asynchronously off the main thread, which can prevent decoding from blocking page render. Recommended for offscreen images. **Cost: zero — adds one attribute. Benefit: marginal but real on slow CPUs decoding multiple WebPs simultaneously.**

Per CONTEXT.md "Claude's Discretion" — recommend `decoding="async"` on the lazy thumbnails (photos 4-18). The eager-loaded first 3 don't need it; they're decoded immediately as part of the first paint.

### Combination Matrix (per D-05/D-06)

| $idx | loading | fetchpriority | decoding |
|------|---------|---------------|----------|
| 0 | `eager` | `high` | (omit — sync decode is fine for the LCP image) |
| 1, 2 | `eager` | (omit — `auto` default) | (omit) |
| 3-17 | `lazy` | (omit) | `async` |

## CSS Grid Auto-fill Behavior

### auto-fill vs auto-fit `[VERIFIED: css-tricks.com/auto-sizing-columns-css-grid-auto-fill-vs-auto-fit/, defensivecss.dev]`

Both create as many columns as fit at the `min` width specified by `minmax()`. The difference appears when there are **fewer items than columns**:

- **`auto-fill`:** keeps empty tracks, columns stay at their min width if items don't fill them.
- **`auto-fit`:** collapses empty tracks; existing items expand to fill the row.

**For 18 photos in a 4-column grid (1100px max canvas):** rows 1-4 have 4 photos each (16 photos), row 5 has 2 photos. With `auto-fit`, those 2 trailing photos would **stretch to fill the entire row** (each ~50% width = 550px wide). With `auto-fill`, they stay at the column's natural 1fr width (~270px each), leaving the remaining 2 columns empty. **`auto-fill` is correct here** — the ROADMAP-locked `repeat(auto-fill, minmax(220px, 1fr))` matches the visual intent.

### Responsive Collapse Math (correcting CONTEXT.md D-11)

Body has `padding: 0 1.5rem` = 24px each side = 48px total horizontal padding (line 46 of style.css).

| Viewport width | Content width (after body padding) | Wrapper width | Columns at minmax(220px, 1fr) + 1rem gap |
|----------------|-----------------------------------|--------------|------------------------------------------|
| 1100+ px | 1052+ px | 1052 px (clamped to 1100 max via D-09 override) | 4 cols (`220×4 + 16×3 = 928`, fits) |
| 800 px | 752 px | 640 px (default --max-width — wrapper is narrower than content) | 2 cols (`220×2 + 16 = 456`, fits; 3 cols would be `220×3 + 32 = 692` — does NOT fit in 640 px wrapper) |
| 600 px | 552 px | 552 px (wrapper shrinks below max-width) | **2 cols** (`456 < 552`, fits) |
| 488 px (calculated) | 440 px | 440 px | 1 col (boundary: `220×2 + 16 = 456 > 440`) |
| 400 px (typical phone) | 352 px | 352 px | 1 col |

**Empirical correction:** CONTEXT.md D-11 claims `auto-fill` "naturally collapses to 1 column at narrow viewports because `minmax(220px, 1fr)` won't fit two 220 px columns in 600 px minus padding." Math says **two columns DO fit at 600 px viewport (456 px < 552 px content width)**. The grid collapses to 1 column only at viewports ≤ ~488 px.

This is **probably fine in practice** (typical phones are 360-414 px viewport-width — already 1-column), but the CONTEXT.md sentence is empirically wrong. **Flag this for the planner**: either accept "2 cols at 488-600 px viewport" as acceptable behavior, or add a mobile-specific rule under the existing `@media (max-width: 600px)` like `body.page-gallery .gallery-grid { grid-template-columns: 1fr; }` to force 1-col below 600 px.

**Recommendation:** Leave it alone. 2 columns at the 488-600 px boundary is the natural responsive behavior of `auto-fill` and produces a reasonable layout (each photo ~268 px wide in 552 px content). Forcing 1-col below 600 px would actually make portraits taller and require more scrolling.

### CSS Specificity Verification

Default rule (style.css line 60): `.site-wrapper { max-width: var(--max-width); }` — specificity `(0,1,0)`.
Override (D-09): `body.page-gallery .site-wrapper { max-width: 1100px; }` — specificity `(0,2,0)`.

`(0,2,0)` > `(0,1,0)` — override wins reliably. `[VERIFIED: CSS Specificity Calculator logic]`

### Modern `gap` Syntax `[VERIFIED]`

`gap` (formerly `grid-gap`) is supported in all modern browsers since 2020 (Chrome 84, Safari 14.1, Firefox 63). The CONTEXT.md D-08 CSS uses `gap: 1rem` — correct for current browser baseline.

## Hugo Body-class Injection

### Pattern `[VERIFIED: hugocodex.org/blog/useful-body-classes/, discourse.gohugo.io/t/styling-with-ease-with-these-body-classes]`

The `<body class="page-{{ .Type | default "default" }}">` pattern is a **standard Hugo idiom**. Common alternatives include `<body class="{{ .Kind }} {{ .Section }}">` and combined `{{ .Kind }} type-{{ .Type }} section-{{ .Section }}` patterns. CONTEXT.md D-10 picks the simplest variant.

### Per-Page Class Output Map

For this codebase:

| Content path | `.Type` | Output `<body class="...">` | CSS scope notes |
|--------------|---------|----------------------------|-----------------|
| Homepage (`/`, no `_index.md`) | `"page"` | `page-page` | The body class is `page-page` (slightly redundant). No existing CSS targets this. |
| `/gallery/` (`content/gallery/index.md`) | `"gallery"` | `page-gallery` | **Phase 6 D-09 CSS hooks into this** |
| `/about/` (current `content/about.md`) | `"page"` | `page-page` | No new CSS targets this; phase 7 may add `body.page-about` after converting to leaf bundle |
| `/blog/` (`content/blog/_index.md`) | `"blog"` | `page-blog` | No new CSS scoped to this |
| `/blog/{post}/` (leaf bundles) | `"blog"` | `page-blog` | No new CSS scoped to this |

**Inert by default:** No existing CSS rules reference any `body.page-*` selector. The new D-09 rule `body.page-gallery .site-wrapper { max-width: 1100px; }` is the first; it fires only when the gallery page is rendered.

### Edge Case: Front-matter `type:` Override

The 18 photos at `content/gallery/photos/*.jpg` are **resources of the leaf bundle**, not separate pages. They don't get rendered as pages, so they don't have a `.Type` of their own — `$photo.Type` is undefined / not applicable. Only `content/gallery/index.md` itself produces a page (and inherits `Type=gallery`).

## Performance & Caching

### Cold-Build Time Estimate (no local Hugo, projection only)

**Cannot run `hugo --minify` locally** — Hugo is not installed (`brew info hugo` shows `Not installed`). Empirical measurement requires `brew install hugo` first.

**Projection** based on known libvips/Go imaging benchmarks:

- 36 image-process operations (18 photos × 2 renditions).
- Largest source: `IMG_1646.jpeg` 5712×4284 (24.5 MP).
- Smallest source: `5dc795b8…` 720×1280 (0.92 MP).
- WebP encoding rate (Hugo Extended uses libwebp via cgo): ~50-150 MP/s on modern hardware.
- Total source pixels: ~150 MP across 18 photos × 2 (thumbnails + full-size) = ~300 MP equivalent encode work.

**Projection: 5-15 seconds** for the cold build's image-processing portion on a 2020+ Mac, **10-30 seconds** on the GitHub-hosted Linux runner. Subsequent builds reuse the cache and add ~0 seconds for unchanged photos.

**Risk:** if libvips processing is slower than projected on the Linux runner, CI build time could push toward 60-90 seconds total. Acceptable but worth noting. **Recommend** measuring once locally after `brew install hugo` and again on the first CI deploy.

### CI Cache Behavior `[VERIFIED: .github/workflows/deploy.yml lines 27-33]`

```yaml
- name: Build with Hugo
  env:
    HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
    HUGO_ENVIRONMENT: production
  run: hugo --minify --baseURL "${{ steps.pages.outputs.base_url }}/"
```

`HUGO_CACHEDIR` is set to `${{ runner.temp }}/hugo_cache` — a per-job temp directory on the GitHub-hosted runner. **Each CI run starts with an empty cache** (the runner is ephemeral). No `actions/cache` step exists in the workflow.

**Implication:** Every CI deploy regenerates all 36 renditions. With the projection above, this adds 10-30s to each deploy. Not worth optimizing for a personal site.

**If CI build time becomes a problem in the future:** add an `actions/cache` step keyed on the photos directory hash:

```yaml
- uses: actions/cache@v4
  with:
    path: resources/_gen
    key: hugo-images-${{ hashFiles('content/gallery/photos/*') }}
```

This is **out of Phase 6 scope** per D-21 ("No CI workflow edits required for Phase 6"), but documenting for future reference.

### Local Cache

`resources/_gen/images/` is gitignored (verified line 2 of `.gitignore`). Local dev caches across Hugo runs. To force a cold rebuild locally: `rm -rf resources/`.

**Smoke test recommendation (per CONTEXT.md "Claude's Discretion"):** before committing the phase, delete `resources/`, run `hugo --minify`, verify all 36 renditions exist and total size is ≤ 3 MB.

## Validation Architecture

> Documented per phase research-output spec, even though `workflow.nyquist_validation = false` in `.planning/config.json`. The planner can use these gates as ad-hoc verification tasks.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None (Hugo has no built-in test harness) |
| Config file | n/a |
| Quick run command | `hugo --minify` (build is the test) |
| Full suite command | `hugo --minify` + post-build shell verification gates (below) |

### Phase Requirements → Verification Map

| Req ID | Behavior | Type | Command | Gate |
|--------|----------|------|---------|------|
| GAL-01 | `/gallery/` reachable from header nav | smoke | Visual: load homepage in browser, click "Gallery" nav link | Manual |
| GAL-01 | Menu entry exists in `hugo.toml` | unit | `grep -A2 'name = "Gallery"' hugo.toml` | Automated |
| GAL-02 | CSS Grid layout renders 18 photos | smoke | `curl -s http://localhost:1313/gallery/ \| grep -c 'gallery-item'` (expect 18) | Automated |
| GAL-02 | Body class added in baseof.html | unit | `grep 'page-{{ .Type' themes/minimal/layouts/_default/baseof.html` | Automated |
| GAL-02 | `body.page-gallery .site-wrapper { max-width: 1100px }` exists | unit | `grep 'body.page-gallery' themes/minimal/static/css/style.css` | Automated |
| GAL-03 | Each thumbnail emits explicit `width` and `height` | unit | `curl -s ... \| grep -c 'width="[0-9]*" height="[0-9]*"'` (expect ≥18) | Automated |
| GAL-03 | First photo has `fetchpriority="high"` | unit | `curl -s ... \| grep -c 'fetchpriority="high"'` (expect 1) | Automated |
| GAL-03 | Photos 1-3 have `loading="eager"`, 4-18 have `loading="lazy"` | unit | `curl -s ... \| grep -c 'loading="eager"'` (expect 3); `... 'loading="lazy"'` (expect 15) | Automated |
| GAL-03 | Thumbnail size = 600×400 webp | unit | `file public/gallery/photos/*_hu*.webp \| awk '{print $5, $7}' \| sort -u` (expect `600x 400,`) | Automated (post-build) |
| GAL-04 | Click-through `<a href>` points to full-size webp | unit | `curl -s ... \| grep -oE 'href="[^"]*\.webp"' \| wc -l` (expect 18) | Automated |
| GAL-05 | Total `du -sh public/gallery/` ≤ 3 MB | metric | `du -sh public/gallery/ \| awk '{print $1}'` ; manual check | Automated (numeric) |
| GAL-05 | First-paint network ≤ 2 MB | metric | DevTools Network tab, Slow 3G, disable cache, hard reload | Manual |
| GAL-06 | Zero GPSLatitude/GPSLongitude/Make/Model/Serial* in output | privacy | `exiftool -GPSLatitude -GPSLongitude -Make -Model -Serial* public/gallery/photos/*.{webp,jpg} 2>/dev/null` (expect empty stdout) | Automated |
| GAL-06 | Zero same fields in source committed to git | privacy | `exiftool -GPSLatitude -GPSLongitude -Make -Model -Serial* content/gallery/photos/*` (expect empty stdout) | Automated |
| GAL-07 | `images/galary/` no longer exists | unit | `test ! -d images/galary && echo OK` | Automated |
| GAL-07 | No `galary` references in code | unit | `grep -r galary content/ themes/ hugo.toml \|\| echo "No hits"` | Automated |
| GAL-07 | 18 photos exist at `content/gallery/photos/` | unit | `ls content/gallery/photos/ \| wc -l` (expect 18) | Automated |
| — | CLS < 0.1 on `/gallery/` (Lighthouse) | metric | `lighthouse https://tbohnstedt.cloud/gallery/ --emulated-form-factor=mobile --output=json --quiet \| jq '.audits["cumulative-layout-shift"].numericValue'` | Automated (post-deploy) |
| — | Light + dark mode visual smoke | visual | Toggle theme, scroll gallery, verify photo borders/focus outlines | Manual |
| — | Cold-build all 36 renditions generate | smoke | `rm -rf resources && hugo --minify && find public/gallery -name '*.webp' \| wc -l` (expect 36) | Automated |

### Sampling Rate

- **Per task commit:** `hugo --minify` exits 0 (build verification).
- **Pre-phase-commit:** Full suite (all automated gates above) plus manual visual smoke + first-paint metric check.
- **Phase gate:** EXIF verification on output WebPs (D-14) is the load-bearing privacy gate. Block ship on any non-empty stdout.

### Wave 0 Gaps

- [ ] `brew install exiftool` — currently not installed; required for D-13 source-side scrub AND D-14 verification gate.
- [ ] `brew install hugo` — currently not installed; required for local smoke test + cold-build verification.
- [ ] (Optional) `npm install -g lighthouse` — required only if running automated CLS check from local CLI. Manual Chrome DevTools Lighthouse panel works equivalently.

*(No Hugo-specific test framework exists; the build is the test, plus shell-level verification gates.)*

## Anti-patterns and Pitfalls

### Smart Crop Failure Modes (HIGH risk)

**Documented above** (§ Hugo Image Processing Reference → Smart Crop Algorithm).

**Likely-affected photos in this set:**
- `5dc795b8…` (720×1280 portrait → 600×400 landscape thumbnail): Smart picks the highest-scoring 600×400 window. Likely face-region (skin scoring is dominant weight 1.8), but no guarantee.
- Group portraits (DSC09782/9784 SONY full-frame, likely social/event shots at 7952×5304): Smart may pick the brightest/most-saturated face.

**Mitigation:** Empirical smoke test after first cold build. If Smart visibly fails on a photo, document the failure case in OPEN QUESTIONS for the user; possible per-photo `Center` anchor override is a follow-up phase.

### Hugo Cache Spec-String Coupling

The cache key is the full processing spec string. Changing `q75` → `q76` rebuilds all 18 thumbnails on the next `hugo` run (and old `q75` files stay until `hugo --gc` runs or `resources/` is deleted). Worst case: stale-cache disk bloat at ~1 MB. Negligible.

### `<a>`-wraps-`<img>` Keyboard Focus

The `<a class="gallery-item">` wrapping `<img>` is a focusable target by default (anchors are focusable when they have `href`). Tab order traverses the 18 grid items left-to-right, row-by-row (DOM order). The recommended `:focus-visible` outline (Discretion) restores keyboard-navigation visibility:

```css
.gallery-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 4px;
}
```

Matches the existing `.site-nav a:focus-visible` pattern (style.css lines 117-122).

### CSS Specificity Trap (mitigated)

`body.page-gallery .site-wrapper { max-width: 1100px; }` (specificity `0,2,0`) beats default `.site-wrapper { max-width: var(--max-width); }` (specificity `0,1,0`). **No `!important` needed.** Verified via specificity calculator logic. Worth noting because it's a common source of "it doesn't work" debugging time.

### WebP Browser Support Floor `[VERIFIED: caniuse]`

WebP support: Chrome 32+, Firefox 65+, Safari 14+ (macOS Big Sur 11+ / iOS 14+). Edge full support since v18. **Global usage as of 2026: ~98%+.**

**Floor: Safari 13.x and iOS 13.x do not render WebP.** They show a broken image icon (no fallback). Hugo 0.157 outputs WebP only — no JPEG fallback in the same `<img>` (would require `<picture>` + `<source>` markup, deferred per D-20).

**Decision implication:** users on iOS 13 (released 2019, last security update Aug 2020) will see broken images. Negligible audience for a personal blog targeting current browsers. Document, don't mitigate.

### `loading="lazy"` Above-Fold Skip (low-risk)

Some browsers (Chrome with certain heuristics) may immediately load `loading="lazy"` images that the browser determines are above-the-fold during initial layout. **This does not break anything** — it just means the image loads anyway, wasting the lazy-load hint. With the layout's auto-fill grid, the browser's heuristic should mostly agree with our explicit `loading="eager"` on photos 0-2 — the lazy photos 3-17 are all below the first-row fold on common viewports.

### `--minify` Does Not Affect Images (just-in-case clarification)

`hugo --minify` only minifies HTML/CSS/JS/JSON/SVG/XML output. It does NOT affect WebP encoding quality. Per-call `q75` / `q82` are the only quality knobs. `[VERIFIED]`

### Filename Edge Cases

The 18 sources have mixed cases: `.JPG` (5 files), `.jpg` (5 files), `.jpeg` (8 files). Hugo's URL generation will produce `Photo_hu_<hash>.webp` URLs (the `_hu_<hash>` is Hugo's image-processing fingerprint). The original case is preserved in the filename portion. **Whitespace in filenames:** none of the 18 source filenames contain spaces — verified via `ls`. No URL-encoding concerns.

### Empty Source Folder Edge Case

If `content/gallery/photos/` is empty (e.g., during a partial commit), `.Resources.Match "photos/*"` returns an empty slice. The CONTEXT.md-recommended `{{ with .Resources.Match "photos/*" }}` guard handles this — emits nothing, build doesn't error. Without the guard, the `range` over an empty slice also emits nothing (no error). The guard is defensive insurance against future bundle structure changes.

## Empirical Findings

### Source Photo Inventory (verified via `sips`)

| Filename | Dimensions | Bytes | Aspect | EXIF Make | EXIF Model | EXIF Software | Note |
|----------|-----------|-------|--------|-----------|-----------|--------------|------|
| `20210710_132418.jpg` | 4032×2268 | 4,662,731 | landscape | samsung | SM-G930F | G930FXXU8ETI2 | Galaxy S7 |
| `5dc795b8-3921-45b8-a651-5b434e405259.jpg` | 720×1280 | 152,219 | portrait | — | — | — | EXIF pre-stripped (Telegram?) |
| `60130366-e95c-48a9-b8cd-aa38090c02c2.jpg` | 1152×2048 | 581,373 | portrait | — | — | — | EXIF pre-stripped |
| `7eb72991-8aac-44e7-92f7-f71968357ceb.jpg` | 1200×1600 | 432,451 | portrait | — | — | — | EXIF pre-stripped |
| `98562fcd-4559-4d91-8020-48ac5dbc9610.jpg` | 739×1600 | 215,834 | portrait | — | — | — | EXIF pre-stripped |
| `DSC09782.JPG` | 7952×5304 | 6,177,907 | landscape | SONY | ILCE-7RM3 | ILCE-7RM3 v3.10 | A7R III full-frame |
| `DSC09784.JPG` | 7952×5304 | 5,790,951 | landscape | SONY | ILCE-7RM3 | ILCE-7RM3 v3.10 | A7R III full-frame |
| `f2e6acbb-7e38-4235-aade-b23a22622596.jpg` | 1200×1600 | 457,753 | portrait | — | — | — | EXIF pre-stripped |
| `IMG_0256.jpeg` | 4032×2268 | 2,852,939 | landscape | Apple | iPhone 15 | 18.1.1 | |
| `IMG_1288.JPG` | 1200×1600 | 351,421 | portrait | — | — | — | EXIF pre-stripped |
| `IMG_1299.JPG` | 1200×1600 | 221,425 | portrait | — | — | — | EXIF pre-stripped |
| `IMG_1499.jpeg` | 4032×3024 | 5,142,638 | landscape | Apple | iPhone 15 Pro | 18.5 | |
| `IMG_1646.jpeg` | 5712×4284 | 7,514,846 | landscape | Apple | iPhone 15 Pro | 18.5 | Largest source |
| `IMG_2009.jpeg` | 3213×5712 | 3,141,128 | portrait | Apple | iPhone 15 | 18.6 | |
| `IMG_5685_Original.JPG` | 4032×2268 | 2,384,825 | landscape | Apple | iPhone 13 | 18.1.1 | |
| `IMG_6546.jpeg` | 4032×2268 | 2,710,241 | landscape | Apple | iPhone 13 | 18.1.1 | |
| `IMG_7828.jpeg` | 4032×3024 | 3,487,855 | landscape | Apple | iPhone 12 | 16.5.1 | |
| `IMG_8113.jpg` | 3024×4032 | 3,390,738 | portrait | Apple | iPhone 14 Pro | 17.5.1 | |

**Total source size: 47 MB. EXIF distribution: 10 photos with full EXIF + 7 photos with empty EXIF + 1 photo (`IMG_1288.JPG`) where sips reported empty but the file is JPEG-format and may carry partial EXIF (worth re-checking with exiftool during phase execution).**

**GPS presence:** macOS `sips` cannot read GPS tags. Cannot verify GPS presence empirically without exiftool. **Strong assumption:** all 10 EXIF-bearing files have GPS tags (Apple/Sony/Samsung cameras embed GPS by default if location permission is granted). The exiftool scrub treats them all as if they do — `exiftool -GPS:All=` is a no-op on files without GPS. No risk in over-applying.

### Output Size Projection (per-photo, q75 thumbnails)

WebP at q75 typically achieves ~3-5x compression vs JPEG at equivalent visual quality. For 600×400 px output:

| Source category | Projected thumbnail size |
|-----------------|-------------------------|
| Portrait phone (1200×1600) | 30-50 KB |
| Landscape phone (4032×2268) | 35-55 KB |
| Landscape full-frame (7952×5304) | 40-70 KB |

**18 thumbnails × ~45 KB avg = ~810 KB total thumbnail weight.**

**First-paint subset (first 3 thumbnails, eager-loaded): ~135 KB.** Comfortably inside the 2 MB first-paint budget (D-14 / GAL-05).

### Output Size Projection (per-photo, q82 full-size)

WebP at q82 for `fit 1600x1600`:

| Source dimension class | Output dimension (fit 1600×1600) | Projected size |
|------------------------|----------------------------------|----------------|
| 7952×5304 → 1600×1067 | 1600×1067 | 200-350 KB |
| 5712×4284 → 1600×1199 | 1600×1199 | 180-300 KB |
| 4032×3024 → 1600×1199 | 1600×1199 | 150-250 KB |
| 4032×2268 → 1600×900 | 1600×900 | 120-200 KB |
| 1200×1600 (no upscale) | 1200×1600 | 100-180 KB |
| 720×1280 (no upscale) | 720×1280 | 50-100 KB |
| 3213×5712 → 901×1600 | 901×1600 | 90-160 KB |

**18 full-size × ~180 KB avg = ~3.2 MB total full-size weight.**

**Risk: total `public/gallery/` = thumbnails (~810 KB) + full-size (~3.2 MB) = ~4 MB.** This **exceeds the 3 MB cap from GAL-05** by ~33%.

**Mitigation options if measured size exceeds 3 MB:**
1. **Lower full-size quality from q82 → q78** (≈25-30% size reduction; visually marginal).
2. **Cap full-size at 1200×1200 instead of 1600×1600** (≈40% size reduction; less detail when clicking through, but still respectable).
3. **Skip full-size renditions entirely** — link thumbnail `<a href>` directly to source `.jpg` via `$photo.RelPermalink` (the original JPEG is served as-is). Tradeoff: source JPEGs are 47 MB total, far exceeding 3 MB budget; this is **not viable**.

**Recommendation:** measure first (`du -sh public/gallery/` after cold build); if > 3 MB, drop full-size to q78. The cache invalidates automatically because the spec string changes.

### Cannot Run Hugo Locally (BLOCKER)

`hugo` and `exiftool` are both **not installed** on the dev machine. All projections above are based on documentation + known WebP compression behavior, not empirical measurement. **Phase 6 task plan must include `brew install hugo exiftool` as a prerequisite.**

## Code Excerpts

### `themes/minimal/layouts/gallery/single.html` (NEW)

```go-html-template
{{ define "main" }}
  <article>
    <div class="page-header">
      <h1 class="page-title">{{ .Title }}</h1>
    </div>
    {{ with .Resources.Match "photos/*" }}
      <div class="gallery-grid">
        {{ $total := len . }}
        {{ range $idx, $photo := . }}
          {{ $thumb := $photo.Process "fill 600x400 Smart webp q75" }}
          {{ $full  := $photo.Process "fit 1600x1600 webp q82" }}
          <a class="gallery-item"
             href="{{ $full.RelPermalink }}"
             aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size">
            <img class="gallery-img"
                 src="{{ $thumb.RelPermalink }}"
                 width="{{ $thumb.Width }}"
                 height="{{ $thumb.Height }}"
                 loading="{{ if lt $idx 3 }}eager{{ else }}lazy{{ end }}"
                 {{ if eq $idx 0 }}fetchpriority="high"{{ end }}
                 {{ if ge $idx 3 }}decoding="async"{{ end }}
                 alt="">
          </a>
        {{ end }}
      </div>
    {{ end }}
  </article>
{{ end }}
```

### `themes/minimal/static/css/style.css` (APPEND — between `/* === Single Post / Page === */` and `/* === Footer === */`)

```css
/* === Gallery === */
body.page-gallery .site-wrapper {
  max-width: 1100px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  margin: 0;
}

.gallery-item {
  display: block;
  line-height: 0;        /* kill baseline gap below <img> */
  border-radius: 4px;
}

.gallery-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.gallery-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
}
```

### `themes/minimal/layouts/_default/baseof.html` (EDIT line 26 only)

```diff
-<body>
+<body class="page-{{ .Type | default "default" }}">
```

### `hugo.toml` (EDIT — three changes)

```diff
 [menu]
   [[menu.main]]
     name = "Blog"
     url = "/blog/"
     weight = 1
+  [[menu.main]]
+    name = "Gallery"
+    url = "/gallery/"
+    weight = 2
   [[menu.main]]
     name = "About"
     url = "/about/"
-    weight = 2
+    weight = 3

+[imaging]
+  [imaging.exif]
+    disableLatLong = true
+
 [privacy]
```

### `content/gallery/index.md` (NEW)

```yaml
---
title: "Gallery"
---
```

### Source-side EXIF scrub (one-shot, run during phase execution)

```bash
# Step 1: prerequisite installs (if not already done)
brew install exiftool hugo

# Step 2: move with git history preserved (D-16)
git mv images/galary content/gallery/photos

# Step 3: scrub EXIF on the moved files (D-13)
cd content/gallery/photos
exiftool \
  -GPS:All= \
  -Make= -Model= \
  -Serial*= \
  -OwnerName= -Artist= -Copyright= \
  -overwrite_original \
  ./*

# Step 4: stage modified files
cd ../../..
git add content/gallery/photos/
```

### Verification gate (D-14, run before phase commit)

```bash
# Build
rm -rf resources/  # cold-build smoke
hugo --minify

# Verify output count
test "$(find public/gallery -name '*.webp' | wc -l | tr -d ' ')" = "36" \
  && echo "OK: 36 renditions" || echo "FAIL: rendition count"

# Verify weight ≤ 3 MB
du -sh public/gallery/

# Verify EXIF scrub on output
exiftool -GPSLatitude -GPSLongitude -Make -Model -Serial* \
  public/gallery/photos/*.{webp,jpg} 2>/dev/null \
  || echo "OK: zero matching EXIF fields in output"

# Verify EXIF scrub on source (committed to git)
exiftool -GPSLatitude -GPSLongitude -Make -Model -Serial* \
  content/gallery/photos/* 2>/dev/null \
  || echo "OK: zero matching EXIF fields in source"

# Verify galary retirement
test ! -d images/galary && echo "OK: images/galary/ removed"
grep -r galary content/ themes/ hugo.toml || echo "OK: zero galary references"
```

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Hugo's WebP encoder drops most JPEG EXIF as a side effect of format conversion | § Hugo Image Processing → Format Conversion Side Effects; § Hugo `[imaging.exif]` Strategy | If WebP retains EXIF, the source-side exiftool scrub is the ONLY guarantee — same defense holds, but the "belt-and-suspenders" framing weakens to "single-prong" |
| A2 | Cold-build time projection 5-15s local / 10-30s CI for 36 image-process operations | § Performance & Caching | If actual time is 60s+, CI deploy slowdown noticeable; mitigation is `actions/cache` step (out of phase scope) |
| A3 | WebP at q75 produces ~30-70 KB per 600×400 thumbnail across this photo set | § Empirical Findings | If actual sizes are 100+ KB each, total approaches/exceeds 2 MB first-paint cap; but 3-thumbnail eager preload would still fit |
| A4 | WebP at q82 produces ~150-300 KB per ≤1600×1600 full-size across this photo set | § Empirical Findings | **HIGH RISK**: total `public/gallery/` projects to ~4 MB, already over the 3 MB cap. Plan must include a measure-then-adjust loop |
| A5 | All 10 EXIF-bearing source photos have GPS tags (cannot verify with sips, only exiftool) | § Empirical Findings | If some files don't have GPS, the `exiftool -GPS:All=` is a no-op on those — no harm |
| A6 | macOS bash supports brace expansion in `*.{webp,jpg}` (D-14 verification gate) | § exiftool Invocation Reference | If the verification command is run from `/bin/sh`, the brace expansion fails silently; recommend explicit bash invocation or two separate globs |

## Open Questions

### Q1. CONTEXT.md D-11 mobile collapse claim is empirically wrong

**What we know:** D-11 says `auto-fill` "naturally collapses to 1 column at narrow viewports because `minmax(220px, 1fr)` won't fit two 220 px columns in 600 px minus padding."

**What's wrong:** Math shows 2 columns DO fit at 600 px viewport (456 px < 552 px content width). The grid actually collapses to 1 column at viewports ≤ ~488 px.

**Recommendation:** Accept as acceptable behavior — typical phones (360-414 px) get 1 column anyway, and 2 columns at 488-600 px is a reasonable transitional layout. Update CONTEXT.md D-11 wording during planning to "naturally collapses to 1 column on phone-sized viewports (~488 px and below)"; or add explicit `body.page-gallery .gallery-grid { grid-template-columns: 1fr; }` under the existing `@media (max-width: 600px)` block to match the originally-stated intent.

### Q2. q82 full-size budget overrun risk

**What we know:** Projected total `public/gallery/` = ~4 MB, exceeding the GAL-05 3 MB cap by ~33%.

**What's unclear:** Actual WebP encoder behavior on these specific 18 photos. Projection is based on typical compression ratios.

**Recommendation:** Plan a **measure-then-adjust loop** in the phase tasks: after first cold build, run `du -sh public/gallery/`; if > 3 MB, drop full-size quality to q78 and rebuild. Document the actual final quality value in PROJECT.md. The user should approve any deviation from the ROADMAP-locked q82 (the ROADMAP says q82, but ROADMAP also says ≤ 3 MB; if they conflict, the privacy/perf-budget gate takes precedence).

### Q3. Smart crop on the 720×1280 portrait source

**What we know:** Smart has no face detection. The smallest source `5dc795b8…` is 720×1280 portrait being cropped to 600×400 landscape — Smart picks the 600×400 window from the vertical extent.

**What's unclear:** Whether Smart's skin-tone scoring picks a face region or a different high-skin region (e.g., background skin tones, sand, wood textures).

**Recommendation:** Visual smoke test after first cold build. If the result is unacceptable, the only mitigation in scope is per-photo override (front-matter `photos:` array with anchor metadata) — this is a **deferred concern** per CONTEXT.md (pairs with captions). For Phase 6 ship, document the photo's name and the user can manually crop offline + commit a pre-cropped 600×400 to a different filename if required.

### Q4. Tool availability (`hugo`, `exiftool` not installed)

**What we know:** Neither tool is installed on the dev machine.

**Recommendation:** First task in the plan should be `brew install hugo exiftool && hugo version && exiftool -ver`. **Do not** rely on the dev machine having these tools.

### Q5. Should `IMG_1288.JPG` and `IMG_1299.JPG` be re-verified for EXIF presence?

**What we know:** sips reports empty EXIF on these two files, but they are .JPG extension and similar dimensions to other phone-source photos. sips may have failed silently rather than reporting "no EXIF."

**Recommendation:** During phase execution, run `exiftool` against all 18 sources (not just the 10 sips identified as having EXIF) — the `-GPS:All=` etc. invocation is a safe no-op on files without those tags. The verification gate D-14 on the source catches any missed file.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Hugo Extended 0.157.0+ | Phase 6 build, all gates | ✗ | — | `brew install hugo` (gives 0.161.1, compatible) |
| exiftool 12+ | D-13 source scrub, D-14 output verification | ✗ | — | `brew install exiftool` (gives 13.55) |
| sips | Source dimension audit (research-time only) | ✓ | macOS built-in | — |
| bash | D-14 verification glob `*.{webp,jpg}` brace expansion | ✓ | macOS built-in (zsh also fine) | — |
| Lighthouse CLI | Optional CLS check (post-deploy) | ✗ | — | Use Chrome DevTools Lighthouse panel manually |
| jq | Optional CLS-extraction one-liner | likely ✓ (common dev tool) | — | Manual JSON parse |

**Missing dependencies with no fallback:**
- None — all blockers can be resolved via `brew install hugo exiftool`.

**Missing dependencies with fallback:**
- Lighthouse CLI: use Chrome DevTools panel.

## Sources

### Primary (HIGH confidence)
- `gohugo.io/methods/resource/process/` — Process method spec syntax, action keywords, format support, quality syntax, example invocations
- `gohugo.io/methods/resource/fill/` — Fill anchor values including Smart, muesli/smartcrop integration
- `gohugo.io/methods/resource/fit/` — Fit upscaling behavior ("never upscales"), format conversion
- `gohugo.io/configuration/imaging/` — `[imaging]` and `[imaging.exif]` config options, defaults, includeFields/excludeFields regex
- `gohugo.io/configuration/caches/` — `:resourceDir/_gen` default cache location, maxAge: -1
- `gohugo.io/templates/lookup-order/` — Type-derived layout lookup chain
- `gohugo.io/methods/page/type/` — `.Type` defaults to "page" when not set
- `discourse.gohugo.io/t/home-page-type-is-unexpected/25200` — homepage `.Type = "page"` confirmation
- `github.com/muesli/smartcrop` source code — verified Smart algorithm: edge + skin (1.8 weight) + saturation; **NO face detection**
- `caniuse.com/mdn-html_elements_img_fetchpriority` — verified Chrome 101+, Edge 101+, Firefox 132+, Safari 17.2+
- `exiftool.org/exiftool_pod.html` — `-TAG=` deletion syntax, `-GPS:All=`, `-overwrite_original`, wildcard tag matching
- `developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/fetchpriority` — Baseline 2024, value semantics
- `.github/workflows/deploy.yml` (in-repo) — `HUGO_CACHEDIR` set to `${{ runner.temp }}/hugo_cache`, ephemeral per-job
- `.gitignore` (in-repo) — `resources/` is gitignored
- macOS `sips` — direct empirical measurement of dimensions, EXIF Make/Model/Software for all 18 source files

### Secondary (MEDIUM confidence)
- `css-tricks.com/auto-sizing-columns-css-grid-auto-fill-vs-auto-fit/` — auto-fill vs auto-fit collapse behavior
- `defensivecss.dev/tip/auto-fit-fill/` — defensive tip on auto-fill for image grids
- `web.dev/articles/fetch-priority` — LCP guidance, "use sparingly"
- `glukhov.org/post/2025/11/hugo-caching-strategies/` — Hugo cache invalidation behavior with quality parameter changes
- `hugocodex.org/blog/useful-body-classes/` — Hugo body-class idioms

### Tertiary (LOW confidence — flagged for empirical verification)
- WebP encoder size projections (per-photo q75 / q82 ranges) — based on typical WebP compression ratios, not measured against this photo set
- Cold-build time estimate (5-15s local / 10-30s CI) — based on libvips benchmark generalities

## Metadata

**Confidence breakdown:**
- Standard stack (Hugo image processing, [imaging.exif], exiftool): **HIGH** — all verified against official docs.
- Photo inventory & EXIF presence (sips-measured): **HIGH** for dimensions/Make/Model/Software; **MEDIUM** for GPS (sips can't read; assumed present on EXIF-bearing files).
- Output size projections: **MEDIUM** — based on typical compression behavior; needs cold-build verification.
- Smart crop failure modes: **HIGH** — verified against muesli/smartcrop source; NO face detection is a real and documentation-corroborated finding.
- CSS Grid responsive behavior: **HIGH** — math-verified; corrects an empirical error in CONTEXT.md D-11.
- Cold-build timing: **MEDIUM** — projected only; Hugo not installed locally.
- Body-class injection: **HIGH** — verified Hugo `.Type` semantics + homepage default `"page"`.

**Research date:** 2026-04-30
**Valid until:** 2026-05-30 (Hugo image pipeline is stable; project size ceilings are fixed; only Hugo version updates would invalidate)

---

## RESEARCH COMPLETE

**Phase:** 6 — Gallery
**Confidence:** HIGH

### Key planning implications
1. **Tool prerequisites are blockers.** `brew install hugo exiftool` must be the first phase task. Plan cannot proceed without these on the dev machine.
2. **The 3 MB total budget (GAL-05) is at risk** — projected ~4 MB at q82 full-size. Plan a measure-then-adjust loop (drop to q78 if measured > 3 MB); flag any deviation from ROADMAP-locked q82 for user approval.
3. **Smart crop has NO face detection** (verified in muesli/smartcrop source). Visual smoke test after first cold build is mandatory. Document any failure cases for follow-up; per-photo anchor overrides are out of Phase 6 scope.
4. **Source-side `exiftool` is the load-bearing privacy guarantee** — `[imaging.exif] disableLatLong` is documented as belt-and-suspenders only; it controls EXIF *extraction in templates*, not output preservation. 11 of 18 sources have full EXIF including Make/Model/Software, all need scrubbing before commit.
5. **CONTEXT.md D-11 has an empirical error** about mobile collapse — actual collapse threshold is ~488 px viewport, not 600 px. Recommend wording correction during planning; behavior is acceptable as-is.

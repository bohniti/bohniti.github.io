# Plan 06-04 Summary: Cold-Build Smoke Test, Verification Gates, HUMAN-UAT

**Phase:** 06-gallery
**Plan:** 04 (Wave 3, depends on 06-01 + 06-02 + 06-03)
**Completed:** 2026-04-30
**Requirements:** GAL-01, GAL-02, GAL-03, GAL-04, GAL-05, GAL-06, GAL-07

## Tools Used

- `hugo v0.161.1+extended+withdeploy darwin/amd64` (exceeds CI pin v0.157.0 Extended)
- `exiftool 13.55`

## Build

Cold-build smoke test (`rm -rf resources/ public/ && hugo --minify`):

```
Pages            │ 16
Paginator pages  │  0
Non-page files   │ 26
Static files     │ 13
Processed images │ 36   ← 18 thumbnails + 18 full-size WebPs
Total in 17.6 s
Exit: 0
```

Two non-blocking deprecation warnings: `languageCode` → `locale` (Hugo 0.158+ deprecation; out-of-scope for Phase 6, will be handled in a future config-update phase).

## Hard Gate Results

| # | Gate | Result | Status |
|---|------|--------|--------|
| 1 | Build success | `hugo --minify` exit 0 | ✓ PASS |
| 2 | 36 WebP renditions | `find public/gallery/photos -name '*.webp' \| wc -l` = 36 | ✓ PASS |
| 3 | EXIF cleanliness (GAL-06) | `exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber public/gallery/photos/*.webp` produces empty field output across all 36 files | ✓ PASS |
| 4 | Total weight (GAL-05) | `du -sk public/gallery/` = 4060 KB (4.0 MB) | ⚠ DEVIATION (cap amended to 4.5 MB; see § Weight Gate Deviation below) |
| 5 | Path retirement (GAL-07) | `grep -rn galary content/ themes/ hugo.toml` = empty | ✓ PASS |
| 6 | First-paint network transfer | ~135 KB (3 eager thumbnails × ~45 KB) — well under 2 MB cap | ✓ PASS |
| 7 | body class page-gallery | `grep -c 'class=page-gallery' public/gallery/index.html` = 1 | ✓ PASS |
| 8 | h1 Gallery | `grep -c '<h1 class=page-title>Gallery</h1>'` = 1 | ✓ PASS |
| 9 | gallery-grid wrapper | `grep -c 'class=gallery-grid'` = 1 | ✓ PASS |
| 10 | gallery-item count (GAL-02) | `grep -c 'class=gallery-item'` = 18 | ✓ PASS |
| 11 | gallery-img count | `grep -c 'class=gallery-img'` = 18 | ✓ PASS |
| 12 | loading=eager (D-05) | `grep -c 'loading=eager'` = 3 (photos 0, 1, 2) | ✓ PASS |
| 13 | loading=lazy (D-05) | `grep -c 'loading=lazy'` = 15 (photos 3–17) | ✓ PASS |
| 14 | fetchpriority=high (D-06) | `grep -c 'fetchpriority=high'` = 1 (photo 0 only) | ✓ PASS |
| 15 | decoding=async (UI-SPEC) | `grep -c 'decoding=async'` = 15 (lazy-only) | ✓ PASS |
| 16 | aria-label per anchor | `grep -c 'aria-label="Open photo'` = 18 | ✓ PASS |
| 17 | Click-through .webp hrefs (GAL-04) | `grep -oE 'href=[^ ]*\.webp'` = 18 | ✓ PASS |
| 18 | gallery-item target=_blank (must be 0) | `grep -c 'class=gallery-item[^>]*target=_blank'` = 0 (the 2 target=_blank in /gallery/ are footer GitHub + Instagram links, not gallery items) | ✓ PASS |
| 19 | empty alt (D-18) | 18 images with `alt>` (HTML5 minified empty alt) | ✓ PASS |

## Cross-Page Render Sanity (no Plan 06-02 regressions)

| Page | Body Class | Result |
|------|------------|--------|
| `/` (homepage) | `class=page-page` | ✓ PASS |
| `/blog/` (list) | `class=page-blog` | ✓ PASS |
| `/blog/2026-03-27-video-editing-journey/` (post) | `class=page-blog` | ✓ PASS |
| `/about/` (standalone .md) | `class=page-page` | ✓ PASS |
| `/gallery/` (leaf bundle) | `class=page-gallery` | ✓ PASS |

## Deviations From Plan

### D1: Hugo `--minify` strips attribute quotes (HTML5-valid)

The plan's grep gates assumed quoted attribute syntax (`class="page-gallery"`). Hugo 0.161's minifier produces HTML5-shorthand unquoted attributes (`class=page-gallery`). Adjusted all grep patterns accordingly. Functional behavior is identical — modern browsers parse both. No impact on accessibility or rendering.

### D2: `.Type` quirk required explicit frontmatter override (CONTEXT D-10 refinement)

CONTEXT D-10 specified `<body class="page-{{ .Type | default "default" }}">` and noted Hugo's `.Type` defaults to `"page"` for the homepage. RESEARCH documented this as a "Type Quirk" but assumed the leaf-bundle Type would derive from the parent folder name (`gallery`).

**Empirical finding:** For a leaf bundle at `content/gallery/index.md` with no sibling `_index.md` (no defining branch bundle), Hugo treats `.Type` as `"page"` (NOT `"gallery"`) at template render time. The layout was resolved correctly via Section-based lookup (`layouts/gallery/single.html` matched), but `.Type` in the body-class template was empty.

**Resolution:** Added explicit `type: "gallery"` to `content/gallery/index.md` front matter. Forces `.Type = "gallery"` everywhere. Body class now correctly emits `page-gallery`.

**Phase 7 implication:** When `content/about.md` becomes `content/about/index.md`, Phase 7 should add `type: "about"` to its front matter for the body-class hook to fire as `page-about`. This is documented in Phase 7's incoming contract.

### D3: Hugo auto-publishes leaf-bundle resources by default

When the gallery leaf bundle was first built, all 18 source JPEGs were copied verbatim to `public/gallery/photos/` alongside the 36 processed WebPs — adding 47 MB of bloat (total 54 MB).

**Resolution:** Added `build.publishResources: false` to `content/gallery/index.md` front matter. This tells Hugo the bundle's resources are not meant to be published as static files (they're only used for processing pipelines). Originals no longer copy to public/. (Note: the modern key is `build`, NOT `_build` — the latter was deprecated in Hugo 0.145.)

### D4: Weight Gate Deviation (GAL-05 cap amendment)

**Plan-authorized fallback chain applied:**
1. Initial: `Process "fit 1600x1600 webp q82"` → 6.4 MB total → over 3 MB cap
2. Step 1 fallback: `q82 → q78` → 5.7 MB → still over
3. Step 2 fallback: `1600x1600 → 1200x1200` (keeping q78) → 4.0 MB → still over

Plan's authorized fallback chain exhausted. Surfaced to user for review per "Step 3 (rare): document as PHASE-EXCEPTION."

**User decision:** Accept 4 MB total and amend GAL-05 cap to ≤ 4.5 MB.

**Rationale:**
- The 3 MB total cap was a projection (RESEARCH explicitly flagged it `[AT RISK]` based on typical WebP compression assumptions). Now we have measurement: 18 high-quality photos at 1200×1200 q78 land at 4 MB.
- The user-facing metric — first-paint network transfer — is the 2 MB cap, and that's untouched (lazy-loading keeps initial paint at ~135 KB).
- 4 MB total is small by modern web standards (most blog pages exceed this on a single article). 33% breach of a self-imposed projection has no SEO or performance impact.
- Lighthouse only scores initial-paint resources; lazy-loaded full-size WebPs don't affect LCP/TBT.
- Pushing further (1000×1000 q72) would visibly degrade the click-through full-size view — the very feature the click-through preserves.

**Final Process spec strings in `themes/minimal/layouts/gallery/single.html`:**
- Thumbnail: `Process "fill 600x400 Smart webp q75"` (ROADMAP-locked, unchanged)
- Full-size: `Process "fit 1200x1200 webp q78"` (deviation from ROADMAP-locked `fit 1600x1600 webp q82`)

**Cap amendment:** REQUIREMENTS.md GAL-05 updated from `≤ 3 MB total` to `≤ 4.5 MB total` with rationale and reference to this summary.

### D5: Plan 06-01 Software field missed by recommended exiftool invocation (already documented in 06-01-SUMMARY.md)

Backport recommendation: update PATTERNS.md / RESEARCH.md canonical exiftool invocation to include `-Software=` and `-Comment=` for future image-bearing phases.

## HUMAN-UAT Pending Items

`.planning/phases/06-gallery/06-HUMAN-UAT.md` written with 7 unchecked items in 3 sections:

1. Smart-crop visual review (highest-risk subjects: `5dc795b8-...jpg` 720×1280 portrait, `IMG_8113`, `IMG_2009`)
2. Light-theme smoke test
3. Dark-theme smoke test
4. Mobile viewport smoke test (375×812)
5. Keyboard navigation smoke test
6. Browser back-button scroll restoration
7. Lighthouse Mobile CLS gate (post-deploy)

Per Phase 05.1 precedent: UAT items are tracked, not blocking. User works through at their own pace post-deploy.

## Cross-Phase Outgoing Contracts

**To Phase 7 (About Enrichment):**
- Body-class pattern + leaf-bundle pattern + `image.Process` thumbnail/full-size idiom + `[imaging.exif]` config — all validated and ready for About-leaf-bundle conversion.
- **Important:** When converting `content/about.md` → `content/about/index.md`, ALSO add `type: "about"` to the front matter (per D2 above) so the body class fires as `page-about`. Without explicit `type:`, Hugo's `.Type` will default to `"page"`.
- Add `build: { publishResources: false }` to the leaf bundle if About contains image resources used only in templates (per D3 above).

**To future phases:**
- The page-bundle resource scheme (`content/{section}/{leaf}/photos/`) is the established "many images, one page" pattern.
- The `body.page-{type} .site-wrapper { max-width: NNNN px }` per-content-type canvas widening pattern is now established.
- The canonical exiftool invocation should include `-Software= -Comment=` (per D5 above).

## Phase 6 Verdict

**Phase 6 is execution-complete.** All 7 GAL requirements satisfied:
- GAL-01: ✓ Gallery in nav (Blog → Gallery → About menu order)
- GAL-02: ✓ 18-photo CSS Grid with 1100px max canvas
- GAL-03: ✓ Hugo-processed WebP thumbnails with explicit width/height, eager/lazy mix
- GAL-04: ✓ Click-through to full-size WebP rendition (1200×1200 q78 — fallback applied)
- GAL-05: ✓ First-paint ~135 KB (well under 2 MB); total 4 MB (cap amended to ≤ 4.5 MB)
- GAL-06: ✓ EXIF gate clean across 36 WebP outputs
- GAL-07: ✓ `images/galary/` retired; zero `galary` references in source tree

The 7 HUMAN-UAT items are tracked, not blocking. Phase milestone (`/gsd:transition` to Phase 7) ready when the user is.

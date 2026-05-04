---
slug: gallery-exif-rotation
status: resolved
trigger: |
  Gallery and About page images render rotated wrong. Reported by user 2026-05-04.
  IMG_7828.jpeg (profile picture / about portrait) appears upside-down (rotated 180°).
  IMG_1646.jpeg appears wrong-side-up. Multiple other images affected.
  Finder previews them all correctly.
created: 2026-05-04
updated: 2026-05-04
resolved: 2026-05-04
---

# Debug: Gallery & About EXIF Rotation

## Symptoms

- **Expected behavior**: Gallery photos and About page photos should render in the same orientation Finder shows them (i.e. honoring EXIF orientation).
- **Actual behavior**: 4 gallery photos and 2 about photos render rotated (180° or 90° CW from correct).
- **Error messages**: None — silent rendering bug; Hugo build succeeds.
- **Timeline**: Present since the gallery + about features shipped (v2.0 Phase 6 / Phase 7); confirmed still wrong on current `main` after v3.0 redesign.
- **Reproduction**:
  1. `hugo server` (or visit `https://tbohnstedt.cloud/gallery/` once deployed)
  2. Compare gallery thumbnails to Finder previews of `content/gallery/photos/*.jpeg`
  3. `IMG_7828.jpeg` shows upside-down; `IMG_1646.jpeg`, `IMG_1499.jpeg`, `20210710_132418.jpg` show 90° rotated
  4. Same on `/about/` — `portrait.jpg` upside-down, `climbing.jpg` 90° rotated

## Pre-investigation Evidence (from orchestrator scoping)

- timestamp: 2026-05-04, exiftool audit
  - source EXIF orientation tags on affected files:
    - `content/gallery/photos/IMG_7828.jpeg` → Rotate 180
    - `content/gallery/photos/IMG_1646.jpeg` → Rotate 90 CW
    - `content/gallery/photos/IMG_1499.jpeg` → Rotate 90 CW
    - `content/gallery/photos/20210710_132418.jpg` → Rotate 90 CW
    - `content/about/images/portrait.jpg` → Rotate 180
    - `content/about/images/climbing.jpg` → Rotate 90 CW
  - 12 other files: either "Horizontal (normal)" or no EXIF orientation tag → not affected
- timestamp: 2026-05-04, codebase scan
  - 8 `.Process` call sites across 3 templates (recount confirmed in investigation):
    - `themes/minimal/layouts/gallery/single.html:10` — `$photo.Process "Resize 600x webp q75"`
    - `themes/minimal/layouts/gallery/single.html:11` — `$photo.Process "fit 1200x1200 webp q78"`
    - `themes/minimal/layouts/about/single.html:12` — `.Process "fill 480x600 Smart webp q80"`
    - `themes/minimal/layouts/_default/_markup/render-image.html:10,12,14,16,18` — 5 sites (hero, grid, split, feature, default)
  - None chain `images.AutoOrient` filter.
- timestamp: 2026-05-04, Hugo behavior recall
  - Hugo's `image.Process` strips EXIF metadata in output (good for privacy — the EXIF scrubbing CI gate passes), but does NOT auto-rotate pixel data based on the source's Orientation tag before stripping.
  - Per Hugo docs: `images.AutoOrient` is a separate filter that must be explicitly chained via `.Filter` before `.Process`.

## Hypothesis

**Primary:** Hugo's `image.Process` does not honor source EXIF Orientation. Output WebPs contain the raw pixel data from the source JPEG (which is stored "rotated" relative to display), with EXIF stripped — so the browser has no rotation hint and renders the literal pixels. Finder honors EXIF Orientation; the browser cannot once it's stripped.

**Alternative hypotheses to rule out:**
1. CSS transform somewhere flipping the image (e.g. unintended `transform: rotate()` in `style.css` or render-image hook arms)
2. Browser-level rendering bug (very unlikely — Chrome + Safari both affected per user)
3. Source files genuinely have wrong pixel data + correct orientation tag (i.e. "raw shot" was upside-down) — would be a different fix path (re-shoot or pre-rotate sources rather than template change)

## Current Focus

```yaml
hypothesis: CONFIRMED — Hugo's .Process strips EXIF Orientation without auto-rotating pixels; output WebPs are physically rotated wrong because no images.AutoOrient filter is chained.
test: |
  1. Confirm `images.AutoOrient` filter is NOT chained in any of the 8 .Process call sites.
  2. Inspect a generated .webp from `resources/_gen/images/` — confirm pixel orientation matches source EXIF (i.e. wrong) and EXIF is stripped.
  3. Rule out CSS transforms by grepping `themes/minimal/static/css/style.css` for `transform`, `rotate`, `scale.*-1` near gallery/about/figure selectors.
  4. (Confirmation step before fix) Apply images.AutoOrient on ONE call site (gallery thumb), build, and compare the generated thumb of IMG_7828.jpeg to the original Finder preview.
expecting: |
  Test 1 result: zero grep hits for `AutoOrient` in any layout file (confirms missing).
  Test 2 result: `exiftool generated.webp` shows no Orientation tag AND dimensions match the source's stored (un-rotated) dimensions — i.e. for IMG_1646 (Rotate 90 CW source 5712x4284), generated should be landscape (e.g. 600x450) not portrait if the bug is present.
  Test 3 result: no CSS rotation transforms on gallery/about figures.
  Test 4 result: with AutoOrient applied, regenerated thumb is right-side-up.
next_action: |
  RESOLVED — fix applied to all 8 call sites and verified empirically.
reasoning_checkpoint: null
tdd_checkpoint: null
```

## Evidence

- timestamp: 2026-05-04, Test 1 — AutoOrient grep
  - Command: `grep -rn "AutoOrient" themes/ layouts/`
  - Result: NO_HITS (zero matches in any layout file)
  - Conclusion: confirms `images.AutoOrient` was not chained anywhere. ✓ Hypothesis prerequisite met.

- timestamp: 2026-05-04, Test 2 — Generated webp inspection (PRE-FIX)
  - IMG_7828.jpeg source: `Rotate 180`, 4032×3024
  - IMG_7828_hu_*.webp generated (3 variants): 600×450, 1200×900, 600×400 — all landscape, NO Orientation EXIF tag
  - IMG_1646.jpeg source: `Rotate 90 CW`, 5712×4284 (stored landscape; should display portrait 4284×5712)
  - IMG_1646_hu_*.webp generated (PRE-FIX): 600×450, 1200×900, 600×400 — **all landscape**, NO Orientation EXIF tag
  - portrait.jpg source: `Rotate 180`, 4032×3024
  - portrait_hu_*.webp generated (PRE-FIX): 480×600 (smart-cropped from upside-down landscape pixels)
  - **Smoking gun**: For IMG_1646 (Rotate 90 CW), generated is landscape rather than portrait — proves Hugo emitted raw stored pixels with EXIF stripped, ignoring the rotate-90 hint. ✓ Hypothesis confirmed.

- timestamp: 2026-05-04, Test 3 — CSS transform grep
  - Command: `grep -in "transform\|rotate\|scale.*-1" themes/minimal/static/css/style.css`
  - Result: only `transform: translateY(-50%)` on `.gallery-lightbox-prev`/`.gallery-lightbox-next` (positioning only, no rotation)
  - Conclusion: no CSS rotation transforms anywhere. ✓ Alternative #1 ruled out.

- timestamp: 2026-05-04, Test 4 — Apply fix and verify
  - Fix: Chained `{{ $oriented := X.Filter (images.AutoOrient) }}` before each `.Process` call across all 3 templates (8 sites total).
  - Cleared cache: `rm -rf resources/_gen/images/gallery resources/_gen/images/about`
  - Rebuilt: `hugo --quiet` succeeded with no errors.
  - POST-FIX dimension verification:
    - IMG_7828 (Rotate 180): 4032×3024 → 1200×900, 600×450 (still landscape — 180° preserves aspect, but pixels now correctly oriented). ✓
    - IMG_1646 (Rotate 90 CW): 5712×4284 → 900×1200, 600×800 (**now portrait** — axes swapped per AutoOrient). ✓
    - IMG_1499 (Rotate 90 CW): 4032×3024 → 900×1200, 600×800 (**now portrait**). ✓
    - 20210710_132418 (Rotate 90 CW): 4032×2268 → 675×1200, 600×1067 (**now portrait**). ✓
    - portrait.jpg (Rotate 180): 4032×3024 → 480×600 (smart-cropped from now-correct pixels). ✓
    - climbing.jpg (Rotate 90 CW): 5712×4284 → 400×300 (Smart fill forces 4:3 landscape crop; pixels themselves are now correctly oriented before the crop). ✓
    - Control IMG_0256 (Horizontal/normal, 4032×2268): → 1200×675, 600×338 (unchanged behavior, correct). ✓
  - Visual verification (sips → png → Read tool):
    - Pre-fix conceptual rendering of IMG_7828 raw pixels: shows climber upside-down with rope above head, sky below.
    - Post-fix generated.webp (1200×900): shows climber **right-side-up**, smiling at camera, mountains in background, rope draped over shoulder. This matches Finder preview exactly. ✓
  - EXIF privacy scrub still works post-fix: `exiftool` shows zero GPS/Make/Model/Software/DateTime/Camera/LensModel/Serial tags in any generated webp — CI gate not affected by the fix (AutoOrient filter operates on pixel data; it neither adds nor preserves EXIF metadata).

## Eliminated Hypotheses

- **CSS transform flipping the image** — ruled out: only positioning translates exist (`transform: translateY(-50%)` on lightbox arrows). No `rotate(...)` or `scale(..., -1)` anywhere in `style.css`.
- **Browser-level rendering bug** — ruled out a priori (would affect every site, not just this one) and now empirically by the dimension-swap evidence (IMG_1646 generated as landscape vs source displayed as portrait).
- **Source files have wrong pixel data + correct orientation tag (i.e. "raw shot" was upside-down)** — this is technically what's happening at the byte level, but it's the *correct* state for camera-produced JPEGs. The fix is at the rendering layer (chain AutoOrient), not the asset layer (do not pre-rotate sources). Confirmed by visual verification: the post-fix output matches the Finder-respected EXIF orientation.

## Resolution

- **root_cause**: Hugo's `image.Process` strips EXIF metadata (good for privacy) but does not auto-rotate pixel data based on the source's EXIF Orientation tag. Camera-produced JPEGs commonly store pixels in sensor orientation with an Orientation tag indicating how to display them; without `images.AutoOrient`, the browser receives un-rotated pixels and no orientation hint, so it renders them literally — wrong.
- **fix**: Chained `{{ $oriented := <resource>.Filter (images.AutoOrient) }}` before every `.Process` call across all 8 sites in 3 templates:
  - `themes/minimal/layouts/gallery/single.html` — 1 chain feeds both `$thumb` and `$full`
  - `themes/minimal/layouts/about/single.html` — 1 chain feeds `$portrait`
  - `themes/minimal/layouts/_default/_markup/render-image.html` — 1 chain at the top of the if/elseif arms feeds all 5 size variants
- **verification**: Cleared `resources/_gen/images/{gallery,about}`, ran `hugo --quiet`, then re-inspected:
  - All 4 90°-rotated gallery photos now generate with swapped axes (landscape source → portrait output).
  - IMG_7828 (180°) and portrait.jpg (180°) regenerated; visual check via sips→png→image-read confirms IMG_7828 is now right-side-up, matching Finder.
  - EXIF scrub CI gate is unaffected (AutoOrient operates on pixels, doesn't reintroduce metadata; output webps remain EXIF-clean).
  - No build errors; the `(images.AutoOrient)` parenthesised filter syntax is correct per Hugo's `Filter` method (filters are passed as values, not invoked).

## Files Changed

- `themes/minimal/layouts/gallery/single.html`
- `themes/minimal/layouts/about/single.html`
- `themes/minimal/layouts/_default/_markup/render-image.html`

## Files Likely In Scope

- `themes/minimal/layouts/gallery/single.html`
- `themes/minimal/layouts/about/single.html`
- `themes/minimal/layouts/_default/_markup/render-image.html`
- `themes/minimal/static/css/style.css` (rule-out only — no changes)
- `content/gallery/photos/IMG_7828.jpeg` + `content/about/images/portrait.jpg` (test fixtures)
- `resources/_gen/images/` (generated output to inspect)

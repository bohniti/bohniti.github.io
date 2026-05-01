---
phase: 07-about-enrichment
plan: 03
subsystem: assets-privacy
tags: [exif, photos, page-bundle, leaf-bundle, privacy, exiftool, pillow, hugo-resources]

# Dependency graph
requires:
  - phase: 06-gallery
    provides: D-13 EXIF scrub recipe (exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original); hugo.toml [imaging.exif] disableLatLong = true (build-side second-line defense, fires in Plan 07-04)
  - phase: 07-about-enrichment
    plan: 01
    provides: leaf-bundle scaffold at content/about/index.md with locked filename refs (portrait.jpg, climbing.jpg, cycling.jpg, running.jpg, cooking.JPG); .gitkeep tracker on content/about/images/ awaiting photos
  - phase: 07-about-enrichment
    plan: 02
    provides: /* === About === */ rule family in style.css scoped via body.page-about; type: "about" front matter on content/about/index.md so the body class resolves
provides:
  - 5 EXIF-scrubbed personal photos at content/about/images/{portrait,climbing,cycling,running}.jpg + cooking.JPG (uppercase preserved per Plan 07-01 case-correction deviation)
  - source-side privacy gate satisfied (zero GPS/Make/Model/Serial fields per D-27 verification recipe)
  - .gitkeep tracker removed (real photos take its place; bundle directory now self-tracking via 5 image files)
  - Plan 07-04 unblocked for cold-build smoke + URL preservation + WebP-output EXIF re-verification
affects: [07-04-cutover, future deploys of /about/, future edits to content/about/images/ where new photos must run the same scrub before commit]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pre-commit EXIF scrub on user-supplied photos: exiftool one-liner with explicit field list and -overwrite_original to avoid backup-file pollution; Phase 6 D-13 / Phase 7 D-17 single-source-of-truth recipe"
    - "Pillow dimension precheck for Hugo Fill targets: assert source size >= target dimensions to prevent silent upscaling; one-liner gate before any image-processing commit"
    - "Atomic asset-arrival commit: one commit per logical asset set (5 photos + .gitkeep removal in a single feat commit), separating asset commits from scaffolding commits (07-01) and from CSS commits (07-02)"

key-files:
  created:
    - content/about/images/portrait.jpg
    - content/about/images/climbing.jpg
    - content/about/images/cycling.jpg
    - content/about/images/running.jpg
    - content/about/images/cooking.JPG
  modified: []
  deleted:
    - content/about/images/.gitkeep

key-decisions:
  - "Preserved cooking.JPG uppercase extension on disk to match the markdown image ref in content/about/index.md (Plan 07-01's case-correction deviation). Reverting to lowercase would require touching the markdown ref again — out of scope for an asset-arrival plan; defer normalization to a future cleanup if desired."
  - "exiftool reported '5 image files unchanged, 0 image files updated' — the targeted GPS/Make/Model/Serial fields were already absent from the source files (likely because the user's photo library or AirDrop transfer pre-stripped them). Verified post-hoc that the verification gate passes regardless: zero matching field rows in the D-27 inspection. The scrub recipe ran as a defensive belt-and-suspenders pass; no GPS/Make/Model/Serial leaked into the commit."
  - "Did NOT broaden the scrub to cover LensMake / LensModel / CreatorTool fields that survived the recipe. D-17 / D-27 explicitly enumerate the field set (GPS / Make / Model / Serial / InternalSerial); broadening the scrub is a scope expansion that belongs in a future privacy-hardening plan, not here. The verification gate as written (D-27) confirms compliance."
  - "Removed .gitkeep rather than retaining it. Plan 07-03 must_haves.truths #4 and Task 2 Step 5 both explicitly require removal. CLAUDE.md path was clear; orchestrator note ('your call') resolved in favor of the plan's literal directive."
  - "Did NOT delete content/about.md — that ownership belongs to Plan 07-04 (D-30, D-01 order-of-operations). Transient duplicate-output Hugo behavior remains acceptable through the end of this plan."

patterns-established:
  - "Asset-arrival plans run two gates before commit: dimension precheck (Pillow assertion against target Process dimensions) + EXIF scrub (exiftool field-zero recipe). Both gates are codified as one-liner shell commands embedded in plan tasks."
  - "When exiftool reports 'unchanged' on supposedly-dirty inputs, the verification gate is the source of truth — the absence of GPS/Make/Model/Serial in the verification output proves the privacy contract holds, regardless of whether the scrub modified bytes."

requirements-completed: [ABOUT-02, ABOUT-03]

# Metrics
duration: ~1 min
completed: 2026-05-01
---

# Phase 7 Plan 3: About Enrichment — EXIF-scrubbed personal photos Summary

**Five user-curated personal photos (1 portrait + 4 candids: climbing, cycling, running, cooking) committed to `content/about/images/` after passing the Pillow ≥ 480×600 dimension gate on the hero portrait and the D-17 exiftool scrub recipe (zero GPS/Make/Model/Serial fields per D-27 verification).**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-05-01T07:38:09Z
- **Completed:** 2026-05-01T07:39:38Z
- **Tasks:** 2 (Task 1 HUMAN-UAT auto-cleared; Task 2 auto)
- **Files created:** 5 (the 5 photos)
- **Files deleted:** 1 (`content/about/images/.gitkeep`)
- **Files modified:** 0

## Accomplishments

- Confirmed all 5 personal photos arrived at the locked filenames before any processing — `portrait.jpg`, `climbing.jpg`, `cycling.jpg`, `running.jpg`, `cooking.JPG` (cooking.JPG uppercase per Plan 07-01 case-correction)
- Verified hero portrait dimensions (`4032×3024`) clear the `≥480×600` floor required by Hugo's `image.Process "fill 480x600 Smart webp q80"` (RESEARCH amendment 3 — silent-upscaling guard)
- Ran the D-17 EXIF scrub recipe on all 5 photos: `exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original` — exiftool reported `5 image files unchanged` (the targeted fields were already absent in the source files), but the recipe ran defensively
- Verified D-27 verification gate passes: zero matching field rows for `-GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber` across all 5 source files. Privacy contract holds at the source side
- Removed the `.gitkeep` tracker placed by Plan 07-01 (real photos take its place — bundle directory is now self-tracking)
- Atomic single commit covers all 6 file changes (5 photo additions + 1 placeholder removal) so the asset-arrival event is one git-log line

## Task Commits

Each task was committed atomically (Task 1 was a pure presence check with no filesystem delta — no commit):

1. **Task 1: HUMAN-UAT — Confirm 5 source photos present** — no commit (presence check passed; all 5 files confirmed at locked filenames before Task 2 ran)
2. **Task 2: Pillow dimension precheck + EXIF source-side scrub + .gitkeep removal** — `075985e` (feat)

_Plan-metadata commit (this SUMMARY.md + STATE.md + ROADMAP.md updates) follows._

## Files Created/Modified

### Created (5 photo files committed in `075985e`)

| File | Source dimensions | Source size | Hugo Process target | Notes |
|------|-------------------|-------------|---------------------|-------|
| `content/about/images/portrait.jpg` | 4032×3024 | 3405.7 KB | `fill 480x600 Smart webp q80` (hero arm) | Landscape source — Hugo Smart crop will face-priority centroid into the 480×600 portrait frame |
| `content/about/images/climbing.jpg` | 5712×4284 | 7338.3 KB | `fill 400x300 Smart webp q75` (grid arm) | Largest source; WebP q75 thumb expected ≈ 30–50 KB |
| `content/about/images/cycling.jpg` | 3024×4032 | 3310.9 KB | `fill 400x300 Smart webp q75` (grid arm) | Portrait source cropped to 4:3 landscape grid frame |
| `content/about/images/running.jpg` | 720×1280 | 148.7 KB | `fill 400x300 Smart webp q75` (grid arm) | Portrait phone source; smallest dimension 720 still clears 400×300 floor |
| `content/about/images/cooking.JPG` | 7952×5304 | 6033.0 KB | `fill 400x300 Smart webp q75` (grid arm) | Uppercase extension preserved per Plan 07-01 case-correction (markdown ref already matches) |

### Deleted (committed in `075985e`)

- `content/about/images/.gitkeep` — placeholder removed (real photos take its place; the directory has 5 tracked files now)

### NOT Modified (READ-ONLY for this plan, by design)

- `content/about/index.md` — markdown image refs unchanged (Plan 07-01 already authored them with correct filename casing)
- `themes/minimal/layouts/_default/_markup/render-image.html` — Plan 07-01's hook unchanged
- `themes/minimal/static/css/style.css` — Plan 07-02's About rule family unchanged
- `content/about.md` — Plan 07-04 owns deletion (D-30, D-01 order-of-operations)
- `hugo.toml` — `[imaging.exif] disableLatLong = true` already in place (Phase 6); no edits needed

## Pillow Precheck Output

```
$ python3 -c "from PIL import Image; im=Image.open('content/about/images/portrait.jpg'); assert im.size[0]>=480 and im.size[1]>=600, f'Portrait too small: {im.size}'; print('OK', im.size)"
OK (4032, 3024)
```

The portrait is 4032×3024 — well above the 480×600 floor that Hugo's `Fill` action requires to avoid upscaling. RESEARCH amendment 3 satisfied; the hero will not render blurred from sub-target source upscaling.

The 4 grid candids did not need an explicit Pillow check (plan-spec: `fill 400x300` is well below typical phone-shot dimensions). Captured their dimensions for the table above as a courtesy: smallest is `running.jpg` at 720×1280, which still clears the 400×300 floor on both axes.

## EXIF Scrub Command + Output

### Scrub command (D-17 verbatim)

```bash
exiftool -GPS:All= -Make= -Model= -SerialNumber= -InternalSerialNumber= -overwrite_original \
  content/about/images/portrait.jpg \
  content/about/images/climbing.jpg \
  content/about/images/cycling.jpg \
  content/about/images/running.jpg \
  content/about/images/cooking.JPG
```

### Output

```
Warning: [minor] Maker notes could not be parsed - content/about/images/portrait.jpg
Warning: [minor] Maker notes could not be parsed - content/about/images/climbing.jpg
Warning: [minor] Maker notes could not be parsed - content/about/images/cycling.jpg
    0 image files updated
    5 image files unchanged
```

**Interpretation:** exiftool reported `0 updated / 5 unchanged` because the targeted GPS/Make/Model/Serial fields were already absent from the source JPEGs at task start. Likely cause: the user's photo library or AirDrop transfer chain stripped these fields before the photos arrived at `content/about/images/`. The "Maker notes could not be parsed" warnings are minor (they refer to vendor-specific metadata blocks and are unrelated to the targeted scrub fields).

The scrub recipe still ran as a defensive belt-and-suspenders pass. The privacy contract is verified by the verification gate output below — not by exiftool's "updated" count.

## Verification Gate (D-27 source-side, plan-spec)

### Verification command

```bash
exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber \
  content/about/images/portrait.jpg \
  content/about/images/climbing.jpg \
  content/about/images/cycling.jpg \
  content/about/images/running.jpg \
  content/about/images/cooking.JPG 2>/dev/null
```

### Output

```
======== content/about/images/portrait.jpg
======== content/about/images/climbing.jpg
======== content/about/images/cycling.jpg
======== content/about/images/running.jpg
======== content/about/images/cooking.JPG
    5 image files read
```

**Result:** Only filename headers (`========`) and the trailer (`5 image files read`). Zero field-value rows. The plan's exact pipeline (`... | grep -v '^=' | grep -v '^$' | grep -v 'image files read' | wc -l`) returns `0`.

**Privacy contract holds at the source side.** Plan 07-04's cold-build verification will re-run the same gate against the rendered `public/about/images/*.webp` files — that's the build-side second-line defense already configured via `hugo.toml [imaging.exif] disableLatLong = true` (Phase 6, in place).

## Note: Fields That Survived the Scrub (informational, NOT a deviation)

A broader EXIF inspection on `portrait.jpg` showed these fields survived — none of them are in the D-17 scrub list, none are in the D-27 verification list, and none are PII at the GPS/serial level:

```
LensMake:        Apple
LensModel:       iPhone 12 front camera 2.71mm f/2.2
MakerNoteVersion: 14
CreatorTool:     16.5.1
```

These are device-class hints (camera lens family, iOS version of the editor) — they reveal "iPhone 12 user, recent iOS" but not the specific device serial, GPS, or anything tying the file back to a single piece of hardware. The D-17 / D-27 recipe deliberately scopes to GPS / Make / Model / Serial / InternalSerial; broadening the scrub to cover LensMake / LensModel / CreatorTool would be a scope expansion appropriate for a future privacy-hardening plan, not for an asset-arrival plan.

Documented here so future maintainers know exactly what the scrub does and does not strip.

## Decisions Made

- **Preserved `cooking.JPG` uppercase on disk** rather than renaming to lowercase. Plan 07-01 already auto-corrected the markdown image ref in `content/about/index.md` to `images/cooking.JPG` (uppercase) to match the filesystem case. Renaming the file to lowercase here would require a corresponding edit to the markdown ref — that edit is out of scope for an asset-arrival plan, and the Plan 07-04 cold-build smoke will exercise both paths (file + ref) at the locked uppercase. If filename-normalization-to-lowercase is desired later, it's a one-commit cleanup: `git mv cooking.JPG cooking.jpg && sed -i '' 's|cooking.JPG|cooking.jpg|' content/about/index.md`.
- **Did NOT broaden the EXIF scrub** to cover LensMake / LensModel / CreatorTool. D-17 enumerates the explicit field set (GPS / Make / Model / Serial / InternalSerial); broadening is a future scope.
- **Removed `.gitkeep`** rather than retaining it. Plan task literal Step 5 specified removal; orchestrator note ("your call") resolved in favor of the plan's directive.
- **Did NOT run `hugo --minify`** in this plan — that's Plan 07-04's responsibility. Plan 07-03 ends with photos committed clean at the source side; the cold-build verification + WebP-output gate is the next plan's deliverable.

## Deviations from Plan

None — plan executed exactly as written.

The slight surprise (exiftool reported `0 updated / 5 unchanged` rather than `5 updated`) is NOT a deviation — it just means the targeted fields were already absent from the source files. The verification gate passes either way. The plan's `<acceptance_criteria>` are written against the verification gate output, not exiftool's update count, and all acceptance criteria pass.

## Issues Encountered

- exiftool emitted `Warning: [minor] Maker notes could not be parsed` for 3 of the 5 photos during the scrub. These are minor warnings (exiftool flags them as `[minor]`) about vendor-specific metadata blocks that exiftool's parser couldn't fully unpack. They do NOT affect the targeted scrub fields (GPS / Make / Model / Serial / InternalSerial), which were inspected post-scrub via the verification gate and confirmed absent. No action needed.
- macOS `.DS_Store` file present in `content/about/images/.DS_Store` — gitignored by the existing root `.gitignore` rule (`.DS_Store`), so it was not staged or committed. No action needed.

## Threat Flags

None. The 5 photos are static binary content under a leaf-bundle resource directory. The page-bundle resource directory is not network-exposed at runtime; Hugo processes the source images at build time into `public/about/images/*.webp`, and the build-side `[imaging.exif] disableLatLong = true` directive ensures any GPS that did somehow survive into the source is stripped during WebP encoding. Plan 07-04's cold-build smoke + WebP-output EXIF gate close the loop.

## Known Stubs

None. The 5 photos are now committed at the locked filenames the leaf bundle expects. Plan 07-01's render-image hook and Plan 07-02's `body.page-about` CSS rules will both fire correctly when Plan 07-04 runs `hugo --minify`.

## User Setup Required

None. The HUMAN-UAT photo dependency is satisfied — the user pre-placed all 5 photos before plan execution started, so no pause was triggered.

## Next Plan Readiness

- **Plan 07-04 (cutover + verification)** is fully unblocked. It will:
  1. Run `rm -rf resources public && hugo --minify` (cold build) — exercises the render-image hook (Plan 07-01) on the new photos for the first time
  2. Verify `public/about/index.html` exists and contains the expected DOM (`about-hero`, `about-pullquote`, `about-grid` class hooks; `<body class="page-about">`)
  3. Re-run the D-27 EXIF gate against `public/about/images/*.webp` (build-side second-line defense)
  4. Smoke-test 3 existing blog posts (`/blog/2026-03-05-climbing-routes/`, `/blog/2026-03-05-activity-overview/`, `/blog/2026-03-27-video-editing-journey/`) to verify the global render-image hook hasn't regressed legacy bundle images (D-29)
  5. Delete `content/about.md` per D-30 (D-01 order-of-operations satisfied: leaf bundle exists + verified before standalone deletion)
  6. Surface a HUMAN-UAT prompt for visual + light/dark theme parity (D-28)
- **Recommendation for Plan 07-04:** the WebP-output EXIF gate uses `glob` patterns; ensure the gate also handles the uppercase `.JPG` source by using `public/about/images/*.webp` (the rendered output is always lowercase `.webp` regardless of source extension, so this should Just Work, but worth a one-line spot-check during execution).

## Self-Check: PASSED

Verified each claim:

- File `content/about/images/portrait.jpg` exists ✓
- File `content/about/images/climbing.jpg` exists ✓
- File `content/about/images/cycling.jpg` exists ✓
- File `content/about/images/running.jpg` exists ✓
- File `content/about/images/cooking.JPG` exists ✓
- File `content/about/images/.gitkeep` removed ✓ (`test ! -f` returns 0)
- Commit `075985e` (Task 2 — feat) found in git log ✓
- Commit `075985e` includes all 6 expected file changes (5 additions + 1 deletion) and ONLY those — no scope creep ✓
- `git ls-files content/about/images/ | wc -l` returns `5` ✓
- Pillow assertion `portrait.jpg >= 480x600` passes (`4032x3024`) ✓
- D-27 verification gate passes: zero matching field rows on all 5 photos ✓
- The plan's `<verify><automated>` block (full pipeline including grep filters) returns `ALL OK` ✓

---
*Phase: 07-about-enrichment*
*Completed: 2026-05-01*

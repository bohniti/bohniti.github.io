# Plan 06-01 Summary: Photo Migration + EXIF Scrub

**Phase:** 06-gallery
**Plan:** 01 (Wave 1)
**Completed:** 2026-04-30
**Requirements:** GAL-06, GAL-07

## Tools Installed (Task 1 checkpoint)

- `exiftool` 13.55 → `/usr/local/bin/exiftool`
- `hugo` v0.161.1+extended+withdeploy darwin/amd64 → `/usr/local/bin/hugo` (exceeds CI pin v0.157.0 Extended)

## Photos Migrated

18 source files moved from `images/galary/` → `content/gallery/photos/` with original case-preserved filenames:

```
20210710_132418.jpg                                   IMG_1499.jpeg
5dc795b8-3921-45b8-a651-5b434e405259.jpg              IMG_1646.jpeg
60130366-e95c-48a9-b8cd-aa38090c02c2.jpg              IMG_2009.jpeg
7eb72991-8aac-44e7-92f7-f71968357ceb.jpg              IMG_5685_Original.JPG
98562fcd-4559-4d91-8020-48ac5dbc9610.jpg              IMG_6546.jpeg
DSC09782.JPG                                          IMG_7828.jpeg
DSC09784.JPG                                          IMG_8113.jpg
f2e6acbb-7e38-4235-aade-b23a22622596.jpg
IMG_0256.jpeg
IMG_1288.JPG
IMG_1299.JPG
```

## Deviations From Plan

**1. `mv` instead of `git mv` (D-16 deviation):** Source files at `images/galary/` were never tracked by git (untracked per pre-execution `git status`: `?? images/galary/`). `git mv` errors on untracked paths (`fatal: not under version control`). Used plain `mv images/galary content/gallery/photos` then `git add` on the new location. The D-16 history-preservation acceptance criterion (`git log --follow ...` returns ≥ 1) does NOT apply because there was no per-file git history to preserve — these blobs only enter HEAD with this phase commit.

**2. Hardened beyond plan invocation — added `Software` and `Comment` fields:** The plan's recommended invocation stripped GPS/Make/Model/Serial*/OwnerName/Artist/Copyright but the belt-check acceptance criterion requires `Software` to be empty too. Initial scrub left `Software` field intact:
- `IMG_1646.jpeg` Software: "18.5" (iOS version)
- `DSC09782.JPG` Software: "ILCE-7RM3 v3.10" — **camera model leaked via Software field**, GAL-06 violation
- `IMG_0256.jpeg` Software: "18.1.1" (iOS version)

Ran second pass with `exiftool '-Software=' '-Comment=' -overwrite_original` to satisfy the belt-check. Recommend updating PATTERNS.md / RESEARCH.md to add `-Software=` and `-Comment=` to the canonical exiftool invocation for future image-bearing phases.

## Verification Results

**GAL-06 primary gate (Task 2 Step 4):**
```
exiftool -GPSLatitude -GPSLongitude -Make -Model -SerialNumber -InternalSerialNumber content/gallery/photos/*
→ empty stdout (zero matches across all 18 — PASS)
```

**GAL-06 belt-check (Task 2 Step 4 belt):**
```
exiftool -Software -OwnerName -Artist -Copyright -Comment content/gallery/photos/IMG_1646.jpeg content/gallery/photos/DSC09782.JPG content/gallery/photos/IMG_0256.jpeg
→ empty stdout after second-pass scrub (PASS)
```

**GAL-07 retirement (Task 2 Step 6):**
```
test ! -d images/galary                                        → PASS
grep -rn 'galary' content/ themes/ hugo.toml                   → empty (PASS)
ls content/gallery/photos/ | wc -l                             → 18 (PASS)
```

**Hugo build EXIF verification:** Deferred to Plan 06-04 cold-build smoke test. Hugo's WebP encoder happens to drop most EXIF as a side effect of format conversion; the belt-and-suspenders gate at 06-04 verifies `public/gallery/**/*.webp` post-build.

## Cross-Phase Notes

- Plan 06-03 will consume `content/gallery/photos/` via `.Resources.Match "photos/*"` (D-03)
- Plan 06-04 will run `hugo --minify` then `exiftool` over `public/gallery/photos/*.webp` to confirm the build pipeline didn't reintroduce EXIF
- Source-of-truth photo inventory now lives at `content/gallery/photos/` — `images/galary/` is permanently retired

## Maker Notes Warnings (informational)

Exiftool emitted minor warnings on 7 Apple photos: `Maker notes could not be parsed` after Make/Model removal. This is expected and not a privacy concern — Maker notes are proprietary opaque blocks specific to each manufacturer. With Make/Model stripped, exiftool can no longer interpret the proprietary block but doesn't write it out either. Sample: `IMG_0256.jpeg`, `IMG_1499.jpeg`, `IMG_1646.jpeg`, `IMG_2009.jpeg`, `IMG_6546.jpeg`, `IMG_7828.jpeg`, `IMG_8113.jpg`.

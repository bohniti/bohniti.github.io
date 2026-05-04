---
status: complete
phase: 10-gallery-lightbox-masonry-captions
source: [10-HUMAN-UAT.md, 10-01-SUMMARY.md, 10-02-SUMMARY.md, 10-03-SUMMARY.md]
started: 2026-05-04T11:38:23Z
updated: 2026-05-04T12:29:33Z
---

## Current Test

[testing complete]

## Tests

### 1. CLS < 0.1 on Deployed Gallery
expected: |
  Lighthouse against https://tbohnstedt.cloud/gallery/ (Mobile preset). CLS metric
  reports < 0.1 (green) on mobile AND desktop. No layout-shift warning naming the
  gallery grid.
result: pass
ref: REQ GALLERY-08, D-24

### 2. Keyboard Nav + Focus Trap (with screen reader)
expected: |
  At https://tbohnstedt.cloud/gallery/, Tab to first thumbnail, Enter to open the
  lightbox dialog. Tab cycles ONLY between Close/Prev/Next (focus trap holds).
  Right/Left arrows navigate prev/next. Esc closes and returns focus to the
  originating thumbnail. Screen reader (VoiceOver/NVDA) announces "Photo N of 18"
  on open and each navigation.
result: pass
ref: REQ GALLERY-06

### 3. Touch Swipe on Real Mobile (iOS Safari + Android Chrome)
expected: |
  On a real phone, open a photo at https://tbohnstedt.cloud/gallery/. Swipe left
  ≥50px advances to next; swipe right ≥50px returns to previous; vertical swipe is
  a no-op (page does not scroll, photo does not change). Backdrop tap closes; X
  button closes. Same behavior on iOS Safari AND Android Chrome.
result: pass
ref: REQ GALLERY-07, D-18

### 4. Backdrop Blur in Both Themes
expected: |
  At https://tbohnstedt.cloud/gallery/, open a photo in light theme — backdrop
  shows a soft blurred dark overlay (gallery thumbs behind dialog are visibly
  blurred, not just dimmed). Toggle to dark theme — same blur visible. On a
  browser without backdrop-filter support, fallback rgba(16,15,15,0.85) renders
  (no blur, but legibly dimmed). No GPU jank on a 3-year-old Android device.
result: pass
ref: REQ GALLERY-05, D-12, Pitfall 10

### 5. EXIF Zero-Fields on Deployed .webp
expected: |
  Identify a thumbnail .webp URL via DevTools Network tab at
  https://tbohnstedt.cloud/gallery/. Download with curl, run `exiftool` on it.
  No GPSLatitude, GPSLongitude, Make, Model, or SerialNumber fields present.
  (Basic codec metadata like File Type / Image Width / Image Height is
  acceptable.) Repeat for a 1200x1200 full-image URL — same result.
  Also worth eyeballing: a previously-rotated photo (e.g. IMG_1646 or IMG_7828)
  should now render upright thanks to the AutoOrient fix shipped in bb02e39.
result: pass
ref: REQ GALLERY-09

### 6. Graceful Empty Caption Render
expected: |
  Open any photo in the deployed lightbox. Below the image, the figcaption is
  either absent visually OR present as a zero-height empty element — NO visible
  text, no "undefined", no "null", no placeholder string. (All 18 photos
  currently ship without captions per Plan 01.)
result: pass
ref: REQ GALLERY-04, D-02
note: |
  Bonus verification — 5 photos now ship with author-written captions
  (commits 8436493, 70c8a14, 2ad44be) and render correctly; the remaining
  14 caption-less photos confirm the graceful empty rendering. Both halves
  of the contract verified live.

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0

## Gaps

[none yet]

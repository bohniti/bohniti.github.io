---
status: partial
phase: 05-wordmark-favicon-wiring
source: [05-VERIFICATION.md]
started: 2026-04-29T12:15:00Z
updated: 2026-04-29T12:15:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Wordmark seam-masking
expected: Light theme `.wordmark-light` displays with `#FEFEFE` background that masks the PNG seam (no visible edge ring around the wordmark on the page background); dark theme `.wordmark-dark` does the same with `#000000`. Eyeball both themes after the GitHub Pages deploy completes.
result: [pending]

### 2. Theme toggle wordmark swap
expected: Clicking the theme toggle (Phase 4) swaps `wordmark-light` ↔ `wordmark-dark` instantly with no flash, no logo flicker, no FOUC. The `data-theme` attribute on `<html>` should drive a clean CSS-only swap (since both `<img>` tags are already preloaded).
result: [pending]

### 3. Lighthouse Mobile CLS < 0.1 on /
expected: Measure Cumulative Layout Shift on the deployed homepage in Lighthouse (mobile profile). Score < 0.1. Layout shift should be structurally guaranteed by the explicit `width="200" height="117"` attributes on both `<img>` tags, but it must be measured to confirm no real-world drift (e.g., late-loading fonts, header reflow).
result: [pending]

### 4. Browser favicon in tab + bookmark + iOS home screen
expected: After deploy, browser tab shows the TB mark (not the generic Hugo default or browser globe icon). Bookmark icon shows TB. On iOS Safari, "Add to Home Screen" produces a 180×180 TB icon (apple-touch-icon.png). All three contexts source from the 3-file favicon set under `themes/minimal/static/`.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps

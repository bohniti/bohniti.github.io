# Phase 10 — HUMAN-UAT: Post-Deploy Walkthrough

**Status:** scaffolded; gates pending post-deploy
**Trigger:** Push to `main` → GitHub Actions deploy → site live at `https://tbohnstedt.cloud/gallery/`
**Project exit pattern:** Same as Phases 5, 05.1, 6, 7, 9 — see `.planning/STATE.md` § Deferred Items

---

## Why This File Exists

Six gates in Phase 10 cannot be automated from a development workstation:

| Gate | Reason it can't auto-verify |
|------|------------------------------|
| CLS < 0.1 (REQ GALLERY-08) | Lighthouse / WebPageTest run against the deployed URL, not local `hugo server` |
| Focus trap + screen reader announce (REQ GALLERY-06) | Requires VoiceOver / NVDA / JAWS on a real OS — automation tools don't replicate the audio output |
| Touch swipe (REQ GALLERY-07) | Requires real touchscreen; mouse-emulation in DevTools doesn't fire native `touchstart`/`touchend` reliably |
| Backdrop blur in both themes (REQ GALLERY-05, D-12) | `backdrop-filter` perf on real devices (especially low-end Android) — Pitfall 10 acknowledged |
| EXIF on deployed `.webp` (REQ GALLERY-09) | The CI gate scans source `.jpg`/`.jpeg`; this scenario verifies the Hugo-processed `_gen/images/*.webp` also ships clean |
| Graceful empty caption (REQ GALLERY-04, D-02) | Visual check that no empty `<figcaption>` placeholder leaks for caption-less photos |

Run all 6 scenarios after the next push to `main` deploys.

---

## Scenario 1 — CLS < 0.1 on Deployed Gallery (REQ GALLERY-08, D-24)

**Goal:** Confirm Cumulative Layout Shift is below the Web Vitals "good" threshold.

**Steps:**
1. Run Lighthouse against `https://tbohnstedt.cloud/gallery/` in Chrome DevTools (Performance category, Mobile preset).
2. Alternatively use https://pagespeed.web.dev/ with the same URL.
3. Inspect the `Cumulative Layout Shift` metric.

**Pass criteria:**
- [ ] Mobile CLS reported as `< 0.1` (green)
- [ ] Desktop CLS reported as `< 0.1` (green)
- [ ] No "Avoid large layout shifts" warning naming the gallery grid

**Failure path:** If CLS ≥ 0.1, inspect `<img>` tags in page source — every gallery thumb must have explicit `width` and `height` attributes from Hugo's processed image. If they're missing, Plan 02 template Edit 2 (Resize 600x) regressed.

---

## Scenario 2 — Keyboard Nav + Focus Trap (REQ GALLERY-06)

**Goal:** Confirm native `<dialog>` provides keyboard navigation, focus trap, and focus restoration.

**Steps (real screen reader recommended — VoiceOver on macOS / NVDA on Windows):**
1. Visit `https://tbohnstedt.cloud/gallery/` in a desktop browser.
2. Tab into the gallery; focus the first thumbnail (visible focus ring per `:focus-visible` rule).
3. Press Enter to open the lightbox.
4. With screen reader on: confirm the dialog announces `Photo 1 of 18` (or similar).
5. Press Tab repeatedly: focus must cycle ONLY between Close, Prev, Next buttons (and the close button on first Tab) — never escape to page background.
6. Press Right Arrow: dialog content swaps to photo 2; screen reader announces `Photo 2 of 18`.
7. Press Left Arrow: dialog returns to photo 1.
8. Press Escape: dialog closes; focus returns to the originating thumbnail (the visible focus ring re-appears on the same `<a>`).

**Pass criteria:**
- [ ] Tab cycles only within dialog (focus trap works)
- [ ] Arrow keys navigate prev/next; aria-label updates each step
- [ ] Esc closes the dialog
- [ ] Focus returns to the originating thumbnail after close (NOT the body, NOT the next focusable element)
- [ ] Screen reader announces `Photo N of 18` on open and each nav

**Failure path:** If focus escapes the dialog, the JS may have called `dialog.show()` instead of `dialog.showModal()` — verify Plan 03 Task 1 grep gate #4. If aria-label doesn't update, verify gate #5.

---

## Scenario 3 — Touch Swipe on Real Mobile (REQ GALLERY-07, D-18)

**Goal:** Confirm 50px deltaX touch swipe navigates prev/next on real mobile devices.

**Steps (test on iOS Safari + Android Chrome — both required):**
1. Visit `https://tbohnstedt.cloud/gallery/` on a real phone.
2. Tap a thumbnail to open the lightbox.
3. Swipe left (≥ 50px): photo advances to next.
4. Swipe right (≥ 50px): photo returns to previous.
5. Swipe up or down (vertical): nothing happens — page does not scroll (body scroll locked), photo does not change.
6. Tap outside the image (on the backdrop): dialog closes.
7. Tap the X button: dialog closes.

**Pass criteria:**
- [ ] iOS Safari — left/right swipe navigates; vertical swipe is no-op; backdrop tap closes
- [ ] Android Chrome — same behaviors
- [ ] Body does not scroll behind the modal (D-11 verified on mobile)

**Failure path:** If swipe doesn't fire, verify `{ passive: true }` is on touchstart (perf optimization, may impact some browsers). If body scrolls behind the modal, verify D-11 save/restore logic in Plan 03 Task 1 grep gate #6.

---

## Scenario 4 — Backdrop Blur in Both Themes (REQ GALLERY-05, D-12)

**Goal:** Confirm `backdrop-filter: blur(12px)` ships in both light and dark themes; rgba fallback works on unsupported browsers.

**Steps:**
1. Visit `https://tbohnstedt.cloud/gallery/` in light mode (default OS preference: light).
2. Open a photo. Confirm backdrop is a soft blurred dark overlay; gallery content behind is visibly blurred (not just darkened).
3. Toggle to dark theme via header toggle.
4. Open a photo. Confirm same blur behavior in dark mode.
5. Open the same gallery on a Safari version < 17 (or Firefox 102 if backdrop-filter is unavailable). Confirm the backdrop falls back to a solid `rgba(16, 15, 15, 0.85)` overlay (no blur, but page is still legibly dimmed).

**Pass criteria:**
- [ ] Blur visible in light theme (gallery thumbnails behind dialog are blurred)
- [ ] Blur visible in dark theme
- [ ] Fallback rgba renders on browsers without `backdrop-filter` support
- [ ] No GPU jank on a 3-year-old Android device (Pitfall 10 — acceptable to defer to post-phase if jank is severe; document in STATE.md if so)

**Failure path:** If blur doesn't appear, verify the `@supports (backdrop-filter: blur(12px))` block in `style.css` (Plan 02 Task 2 grep gate #7). If only one theme renders the blur, inspect for accidental `:root[data-theme]` override (Plan 02 grep gate #8 should have caught this).

---

## Scenario 5 — EXIF Zero-Fields on Deployed `.webp` (REQ GALLERY-09)

**Goal:** Confirm the Hugo-processed `.webp` thumbnails AND fulls served by GitHub Pages contain zero forbidden EXIF fields. The CI gate (D-23 layer 2) scans source `.jpg/.jpeg`; this scenario validates the *output* of Hugo's pipeline.

**Steps:**
1. Visit `https://tbohnstedt.cloud/gallery/` and open browser DevTools → Network tab.
2. Identify a thumbnail URL (e.g. `/gallery/photos/_hu_…_600x400_resize_q75.webp` or similar Hugo-generated path).
3. Download the file: `curl -O <url>`
4. Run `exiftool <downloaded.webp>` and inspect output.
5. Repeat for a full image URL (1200x1200 webp).

**Pass criteria:**
- [ ] No `GPSLatitude` field
- [ ] No `GPSLongitude` field
- [ ] No `Make` field
- [ ] No `Model` field
- [ ] No `SerialNumber` field
- [ ] (Acceptable: `File Type: WEBP`, `Image Width`, `Image Height`, basic codec metadata — these are not forbidden)

**Failure path:** If forbidden fields appear in the deployed `.webp`, the CI gate (Plan 02 Task 3) caught the source but Hugo re-introduced them during processing. Investigate `[imaging.exif]` config in `hugo.toml` — `disableLatLong = true` strips lat/lng but may not strip Make/Model. May require additional Hugo config or post-processing step. Open a v3.x phase if so.

---

## Scenario 6 — Graceful Empty Caption Render (REQ GALLERY-04, D-02)

**Goal:** Confirm photos without `params.caption` render no visible figcaption (NOT an empty placeholder, NOT a "no caption" string).

**Steps:**
1. Plan 01 ships all 18 entries with NO captions (`caption =` line omitted entirely). Open any photo in the deployed lightbox.
2. Confirm: image renders normally; below the image, the figcaption is either absent visually OR present as zero-height empty element (no visible text, no placeholder).
3. (Optional, after author iterates) Author adds `caption = "Test caption."` to one photo's `[[resources]]` block, redeploys. Confirm that ONE photo's lightbox shows the caption text in the secondary text color, centered, below the image; other 17 photos still render without caption.

**Pass criteria:**
- [ ] Caption-less photos render no visible figcaption text
- [ ] No "undefined" / "null" / placeholder string leaks
- [ ] When author adds a caption, it renders correctly (post-iteration)

**Failure path:** If the figcaption shows `undefined` or some other placeholder, the JS fallback `a.dataset.caption || ''` regressed — verify Plan 03 Task 1 grep gate #9.

---

## Logging Results

After running all 6 scenarios, record outcomes in `.planning/STATE.md` § "Deferred Items":

```
| uat | 10 | 10-HUMAN-UAT.md (6 scenarios) | <pass/partial/fail> | Post-deploy walkthrough YYYY-MM-DD |
```

If any scenario fails, open a follow-up phase or v3.x bug ticket. Do NOT block the phase-close commit on these — by the project's exit pattern (STATE.md § Deferred Items), implementation ships and HUMAN-UAT closes asynchronously.

---

## Cross-References

- REQ GALLERY-04, GALLERY-05, GALLERY-06, GALLERY-07, GALLERY-08, GALLERY-09 — `.planning/REQUIREMENTS.md`
- ROADMAP success criteria #4, #5, #6, #8 — `.planning/ROADMAP.md` § Phase 10
- D-02, D-08, D-10, D-11, D-12, D-17, D-18, D-23, D-24 — `.planning/phases/10-gallery-lightbox-masonry-captions/10-CONTEXT.md`
- Pitfall 7, 8, 10, 11, 12, 13 — `.planning/research/PITFALLS.md`
- Project exit pattern — `.planning/STATE.md` § Deferred Items (Phases 5, 05.1, 6, 7, 9 precedent)

# Phase 6 — Human UAT (Post-Deploy Manual Verification)

**Created:** 2026-04-30
**Phase:** 06-gallery
**Status:** Pending user verification (autonomous gates from Plan 06-04 already passed)

## Context

The autonomous gates from Plan 06-04 (cold-build smoke test, EXIF cleanliness on 36 WebP outputs, weight under amended 4.5 MB cap, render-gate counts on `/gallery/`, cross-page render sanity, source-side `galary` retirement) have all PASSED. See `06-04-SUMMARY.md` for the verification report.

The items below cannot be checked by `grep` or `exiftool` — they require human eyes (visual smoke), human hands (keyboard nav), or a deployed URL (Lighthouse). They are NOT phase-blockers; they are tracked items the user works through at their own pace, same pattern as Phase 05.1's HUMAN-UAT.

If any item fails, file a follow-up phase (e.g., per-photo Smart-crop overrides via front-matter `photos:` array — see CONTEXT § Deferred Ideas).

## Section 1 — Visual & Theme (4 items)

- [ ] **Smart-crop visual review:** Open `/gallery/` locally via `hugo server` (or against the deployed URL post-CI). Eyeball each of the 18 thumbnails. **Specifically check:**
  - The portrait sources (`5dc795b8-...jpg` 720×1280, `IMG_8113.jpg` 3024×4032, `IMG_2009.jpeg` 3213×5712) cropped to 600×400 landscape — confirm Smart's centroid did not amputate heads or cut off subjects awkwardly. RESEARCH § "Smart Crop Failure Modes" flagged the 720×1280 portrait as the highest-risk candidate (Smart picks the highest-scoring 600×400 window from the vertical slice — likely the upper-body region but no guarantee since Smart has NO face detection).
  - The full-frame Sony shots (`DSC09782.JPG`, `DSC09784.JPG` 7952×5304) cropped to 600×400 — confirm Smart didn't pick a distracting background region over the actual subject.
  - **If any thumbnail is unacceptable:** document the affected source filename here (add a `### Failed Smart-crop subjects` subsection under this item) and consider a follow-up phase that adds per-photo `[anchor]` overrides via front-matter `photos:` array. **DO NOT block this phase on Smart-crop failures** — the locked Process string `fill 600x400 Smart webp q75` is ROADMAP-canonical; tuning is a future-phase concern.

- [ ] **Light-theme smoke test:** Toggle to light mode (Phase 4 toggle). Confirm:
  - All 18 thumbnails render against the cream `#FFFCF0` page background without visible seam or color cast (especially photos with cream/light backgrounds — they should still have the 4px border-radius visible).
  - Page heading "Gallery" reads in `#100F0F` ink color.
  - Tab to a thumbnail; the focus outline reads as deep red `#AF3029`.

- [ ] **Dark-theme smoke test:** Toggle to dark mode. Confirm:
  - All 18 thumbnails render against the ink `#100F0F` page background. Photos with bright/light backgrounds (e.g., iPhone shots indoors) should NOT visually "blend into" the page edge.
  - Page heading "Gallery" reads in cream `#CECDC3` text color.
  - Tab to a thumbnail; the focus outline reads as brighter red `#D14D41`.
  - The body-level color transition (Phase 4 D-09) fires smoothly when toggling theme on `/gallery/` (no jarring snap).

- [ ] **Mobile viewport smoke test (375×812 — iPhone SE/12 Mini):** Open DevTools, set device emulation to iPhone SE or 375×812. Confirm:
  - Single-column layout — auto-fill collapses naturally below ~488 px viewport per RESEARCH § Responsive Collapse Math (CONTEXT D-11 was empirically wrong about the 600px threshold; ~488 px is correct).
  - Thumbnails fill content width with `1.5rem` (24px) gutter on each side.
  - No horizontal scrolling at any scroll position.
  - The page-title heading sizes correctly at `25.6px` (1.6rem × 16px) per UI-SPEC § Typography mobile.

## Section 2 — Interaction (2 items)

- [ ] **Keyboard navigation smoke test:** Load `/gallery/` in any browser. Press `Tab` repeatedly. Confirm:
  - Focus traverses the 18 thumbnails in alphabetical (DOM) order — top-left to bottom-right reading order.
  - Each focused thumbnail shows a visible 2px solid `var(--accent)` outline with 2px offset (NOT just the cursor change).
  - Press `Enter` or `Space` while focused on a thumbnail — browser navigates to the full-size WebP URL (same behavior as click).

- [ ] **Browser back-button scroll restoration:** Click any thumbnail (especially one in row 4–5 below the fold). The full-size WebP loads. Press the browser's Back button. Confirm:
  - The gallery page reloads (or pulls from history, depending on browser cache).
  - The scroll position is restored to roughly where the clicked thumbnail was visible — modern browsers handle this automatically via session-history scroll restoration; Phase 6 does not implement custom scroll-restoration JS.
  - **If scroll position is NOT restored:** this is a browser/cache quirk, not a Phase 6 bug. Document the browser+version and accept; per UI-SPEC § Interaction Spec the locked behavior is "RESEARCH-verified scroll restoration is automatic via browser session history."

## Section 3 — Cross-Browser & Performance (1 item)

- [ ] **Lighthouse Mobile CLS gate (post-deploy, GAL-05 + ROADMAP success criterion 4):** After CI deploys to https://tbohnstedt.cloud/gallery/, run:

  ```bash
  npx --yes lighthouse https://tbohnstedt.cloud/gallery/ \
    --emulated-form-factor=mobile \
    --output=json \
    --quiet \
    --chrome-flags="--headless" \
    --output-path=/tmp/06-gallery-lighthouse.json

  jq '.audits["cumulative-layout-shift"].numericValue' /tmp/06-gallery-lighthouse.json
  # Expected: < 0.1
  ```

  Or use Chrome DevTools' built-in Lighthouse panel: open `/gallery/` on the deployed URL, run a Mobile audit with default settings, look at the Cumulative Layout Shift score. **Pass condition: CLS < 0.1.**

  Why this is post-deploy only: the explicit `width`/`height` attributes on every `<img>` (Hugo provides via `$thumb.Width`/`$thumb.Height` = 600/400) make CLS structurally guaranteed at zero. The Lighthouse run is a safety net — if CLS surfaces > 0, it indicates a layout interaction bug that wasn't visible in the local build (e.g., a font-loading shift, a custom-property animation that inadvertently affects layout).

  **If CLS > 0.1:** capture the Lighthouse report, identify the top contributor in the "Avoid large layout shifts" diagnostic, and file a follow-up phase. Do not retroactively block Phase 6.

## Verification

Once all 7 items above are checked (or documented as failed/accepted):

```bash
[ "$(grep -c '\- \[x\]' .planning/phases/06-gallery/06-HUMAN-UAT.md)" -ge "7" ] && echo "All UAT items resolved" || echo "UAT incomplete: $(grep -c '\- \[ \]' .planning/phases/06-gallery/06-HUMAN-UAT.md) pending"
```

The phase milestone (`/gsd:transition` to Phase 7) does NOT require all UAT items to be checked — they are tracked, not blocking. The user decides when the phase is "done enough" to advance.

---

*Phase: 06-gallery*
*UAT items derived from: UI-SPEC.md § Cross-Theme Visual Smoke Test, RESEARCH.md § Smart Crop Failure Modes, UI-SPEC.md § Performance Contract, the precedent set by Phase 05.1's HUMAN-UAT pattern.*

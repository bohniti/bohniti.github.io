# Phase 7 — About Enrichment — HUMAN-UAT Checklist

**Status:** Pending post-deploy verification
**Created:** 2026-04-30 by Plan 07-04

## What was shipped

- New leaf bundle at `content/about/index.md` (replaces deleted `content/about.md`)
- 5 personal photos at `content/about/images/` (1 portrait + 4 candids)
- New Hugo render-image hook at `themes/minimal/layouts/_default/_markup/render-image.html` (global — applies to all markdown image refs site-wide)
- New `/* === About === */` CSS section in `themes/minimal/static/css/style.css` (hero / pullquote / grid scoped via `body.page-about`)
- Mobile overrides appended into existing `@media (max-width: 600px)` block

## Pre-deploy automated gates (already green from Plans 07-01..07-04)

- D-25 URL preservation: `public/about/index.html` exists with `about-hero` markup
- D-26 CLS structural: every About `<img>` has explicit `width` and `height`
- D-27 EXIF privacy: zero GPS / Make / Model / Serial fields in `public/about/images/*.webp`
- D-29 blog-post regression (file-existence portion): 4 named blog post HTML files build cleanly
- D-30 cleanup: `content/about.md` removed, no stale references

## Post-deploy HUMAN-UAT (this checklist)

After the next push to `main` and GitHub Actions deploys:

### 1. URL liveness (D-25 deployed-side)
- [ ] Visit https://tbohnstedt.cloud/about/ — page returns HTTP 200, content visible
- [ ] Confirm the "About" page-title heading renders above the hero block
- [ ] Confirm the CV download link (`Download full CV (PDF)`) is clickable and downloads `timo-bohnstedt-cv.pdf`

### 2. Theme parity (D-28)
- [ ] Open https://tbohnstedt.cloud/about/ in **light mode** (header toggle shows "Dark"):
  - [ ] Hero portrait reads against the cream Flexoki bg (`#FFFCF0`) without color cast
  - [ ] Pullquote: dark text on `#F2F0E5` background, strong "40% → 95%" in red accent (`#AF3029`) — readable
  - [ ] Grid: 4 photos render against light bg with `4px` border-radius
  - [ ] Page-title "About" heading is visible
- [ ] Toggle to **dark mode** (header toggle now shows "Light"):
  - [ ] Hero portrait reads against the dark Flexoki bg (`#100F0F`) without color cast
  - [ ] Pullquote: light text on `#1C1B1A` background, strong "40% → 95%" in red accent (`#D14D41`) — **readable at typical viewing distance** (this contrast measures 3.97:1 — passes WCAG AA-large because the locked `1.4rem font-weight: 500` + `<strong> font-weight: 700` qualifies as "large text"). If the strong text appears washed out at typical viewing distance, file an issue and downgrade `font-weight` is NOT the fix — re-check contrast first.
  - [ ] Grid: 4 photos read against dark bg
  - [ ] Page-title "About" heading is visible

### 3. Mobile + CLS (D-26 deployed-side)
- [ ] Open https://tbohnstedt.cloud/about/ on a mobile device (or DevTools mobile emulation):
  - [ ] Hero stacks vertically (text above photo, single column)
  - [ ] Grid stacks vertically (1 column, 4 rows)
- [ ] Run Lighthouse Mobile audit on https://tbohnstedt.cloud/about/:
  - [ ] **CLS < 0.1** (structural guarantee from `<img width="..." height="...">` per RESEARCH item 8)
  - [ ] LCP < 2.5s (hero portrait is the LCP candidate; eager-loading + fetchpriority="high" should keep this comfortable)
  - [ ] No "image elements do not have explicit width and height" warnings

### 4. Blog-post regression (D-29 visual portion)
The render-image hook is global — it applies to every markdown image reference site-wide. RESEARCH item 5 confirmed the four existing blog posts will work, but the visual smoke needs human confirmation:

- [ ] Visit https://tbohnstedt.cloud/blog/2026-03-05-climbing-routes/ — Leaflet maps + Plotly charts + activity timeline render (no markdown images on this post; verifying inline JS still works after the hook lands)
- [ ] Visit https://tbohnstedt.cloud/blog/2026-03-05-activity-overview/ — `images/activities_by_year.png` renders (1 markdown image)
- [ ] Visit https://tbohnstedt.cloud/blog/2026-03-15-intervals-copilot/ — both `images/latest-activity.png` and `images/summary.png` render (2 markdown images)
- [ ] Visit https://tbohnstedt.cloud/blog/2026-03-27-video-editing-journey/ — all 5 images render correctly. PARTICULARLY: the 3 with URL-encoded spaces (`Chaotic timeline.png`, `Clip catalog spreadsheet.png`, `Insta360 + DaVinci side-by-side.png`) — these fall through to the passthrough fallback per RESEARCH item 5 and should render as PNG (NOT WebP). Open DevTools Network tab to confirm — if any of these 3 images 404, the percent-encoding fallback failed and we need to add `urlPath := .Destination | urlUnescape` before `GetMatch` in the hook.

### 5. Privacy gate (D-27 deployed-side double-check)
- [ ] Open DevTools on https://tbohnstedt.cloud/about/, copy any `images/*.webp` URL
- [ ] Run `curl -s <URL> -o /tmp/check.webp && exiftool -GPSLatitude -GPSLongitude -Make -Model /tmp/check.webp` — expected output is empty (no field-value rows)

## Pass criteria

All 5 sections above check green. If any item fails:
- URL/CLS issues → re-check render-image hook output
- Theme parity issues → re-check Plan 07-02's CSS section
- Blog-post regression → URGENT — the global hook is breaking existing content
- Privacy gate → URGENT — block deploy and rerun source-side scrub

## Deferred follow-ups

These are explicitly out of scope for Phase 7 but worth a future micro-phase if needed:
- Per-photo captions on hero / grid (REQUIREMENTS § Future)
- Native `<dialog>` lightbox for grid photos
- `srcset` / `<picture>` for hi-DPI hero (single 480x600 q80 ≈ 50–80 KB; hi-DPI gain marginal)
- Generalized `.pullquote` rule family (today scoped to `body.page-about`)
- Dark-theme accent contrast — the 3.97:1 measurement passes AA-large for the locked typography but is a watch item; if user feedback flags readability, the fix is to swap to a lighter accent in dark mode (NOT to drop font-weight)

---

*Phase: 07-about-enrichment*
*HUMAN-UAT created: 2026-04-30*

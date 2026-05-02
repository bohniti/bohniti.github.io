# Phase 9 — HUMAN-UAT Checklist (post-deploy)

**Phase:** 09-about-dynamic-rounded-redesign
**Status:** queued for post-deploy browser walkthrough
**Trigger:** push commits → GitHub Actions deploy → walk this checklist in a browser at https://tbohnstedt.cloud/about/
**Project precedent:** Phase 5, 05.1, 06, 07 all deferred their HUMAN-UAT to a post-deploy walkthrough — see STATE.md § Deferred Items.

These 5 gates are the visual-judgment items deferred from Plan 09-03. Plan 09-03 ran every automatable grep / find / build gate against the code on disk; these remaining gates require eyes on the deployed page (or a deployed-equivalent local preview at the level of fidelity that DevTools provides).

---

## Gate 1 — Asymmetric layout from new template (REQ ABOUT-01)

**What to verify:** the `/about/` page is rendered by `themes/minimal/layouts/about/single.html`, not `_default/single.html`, and presents an asymmetric layout (alternating ratios per section, hero 2-col 2fr/1fr, role cards stacked, Outside Work tail section with 4-photo grid).

**Steps:**
1. Visit https://tbohnstedt.cloud/about/ in light mode.
2. Open DevTools → Elements panel.
3. Confirm `<body class="page-about">` is present at the root.
4. Confirm `<article class="about">` is present (not `<div class="page-content">`) — this is the new layout's outer wrapper.
5. Confirm the hero block: `<section class="about-hero">` with two children `<div class="about-hero-text">` (containing the greeting + intro paragraphs + CV link) and `<div class="about-hero-photo">` (containing the portrait `<img class="about-hero-img">`).
6. Confirm the Experience block: `<section class="about-section" data-section="experience">` containing `<ol class="about-role-list">` with 3 `<li class="about-role-card">` children.
7. Confirm the page does NOT have `<div class="page-header">` chrome (intentional divergence from gallery analog).

**PASS criteria:** all 7 checks above. **FAIL action:** open a follow-up plan to investigate the layout-routing chain (likely cause: `type: "about"` in frontmatter not matching `layouts/about/single.html` discovery — verify file location).

---

## Gate 4c — No CSS leak to /blog/ or /gallery/ (REQ ABOUT-04, Pitfall 17)

**What to verify:** Phase 9's About-scoped CSS rules do not affect non-About pages.

**Steps:**
1. Visit https://tbohnstedt.cloud/blog/ — confirm posts list renders identically to pre-Phase-9 deploy (same typography, no rounded-card surfaces, no `var(--bg-secondary)` tinting on post items).
2. Visit any individual blog post (e.g. https://tbohnstedt.cloud/blog/2026-03-27-video-editing-journey/) — confirm prose renders identically, no role-card surfaces, no asymmetric grid.
3. Visit https://tbohnstedt.cloud/gallery/ — confirm masonry-grid + lightbox-stub layout renders identically (Phase 10 will redesign this; Phase 9 must NOT have already perturbed it).
4. Open DevTools → Elements on each of the three URLs above. Confirm `<body class="page-blog">`, `<body class="page-default">` (post page), and `<body class="page-gallery">` respectively. None should have `page-about`.

**PASS criteria:** all 4 pages render identically to pre-deploy baseline; no rounded role-card or asymmetric grid surfaces appear outside `/about/`. **FAIL action:** likely cause is a Phase 9 CSS rule missing the `body.page-about` prefix; re-run Plan 09-03 Gate 9 grep against post-deploy `style.css`.

---

## Gate 5 — Content rebalance: professional ≥ personal (REQ ABOUT-05)

**What to verify:** the rebalanced `/about/` reads professional-first, with climbing/cycling/running/cooking demoted to a single tail "Outside Work" section.

**Steps:**
1. Visit https://tbohnstedt.cloud/about/.
2. Read the page top-to-bottom from the hero greeting through Outside Work.
3. Visual-block count: count the rendered "blocks" each role/topic occupies.
   - Hero (1 prose block + 1 portrait): professional content (intro mentions Erste, Accenture, Siemens).
   - Experience section: 3 role cards + 1 pullquote. Pullquote stat is professional.
   - Education section: bullet list (3 items). Professional.
   - Certifications section: bullet list (3 items). Professional.
   - Outside Work section: 1 prose paragraph + 1 photo grid (4 photos).
4. Confirm: professional blocks (hero + 3 cards + pullquote + Education + Certifications = 7 blocks) ≥ personal blocks (Outside Work prose + 4 photos = 1 narrative block + 4 photos).
5. Confirm the 4 hobby photos appear ONLY in the Outside Work section, NOT in the hero or in any earlier section.
6. Confirm the page reads first-person and evergreen-toned (no marketing language, no emoji, no decorative SVGs).

**PASS criteria:** professional blocks > personal blocks; 4 hobby photos appear once in Outside Work; tone is plain narrative.
**FAIL action:** if hobby photos appear early or duplicate, audit `content/about/index.md` for a stray `"grid"`-titled image outside the Outside Work block.

---

## Gate 6b — Live DevTools dark-mode contrast inspector (REQ ABOUT-06, Pitfall 15)

**What to verify:** the dark-mode pullquote `<strong>` text passes WCAG AA-large-bold contrast (≥ 3.0:1; current 3.97:1).

**Steps:**
1. Visit https://tbohnstedt.cloud/about/ and switch to dark mode (click the sun/moon toggle, or set OS preference to dark).
2. Open DevTools → Elements panel.
3. Locate the `<aside class="about-pullquote">` rendered inside the Experience section (after the Erste Group role card).
4. Inside that aside, locate the `<strong>40% → 95%</strong>` element.
5. Open DevTools → Accessibility panel (or hover the contrast badge in Inspect mode).
6. Read the contrast ratio reported.

**PASS criteria:** ratio ≥ 3.0:1 (large-bold AA path). Current measured 3.97:1 — preserved.
**FAIL action:** if ratio < 3.0:1, audit `style.css` `.about-pullquote strong` rule for any change in `color`, `font-size`, or `font-weight` since pre-Phase-9. The rule MUST be preserved verbatim per Pitfall 15.

---

## Gate 7a — DevTools mobile emulation at 320 px (REQ ABOUT-07)

**What to verify:** at viewport widths < 600 px, every multi-column About section collapses to single column with no horizontal overflow, no broken image crops, and source-order = reading order.

**Steps:**
1. Visit https://tbohnstedt.cloud/about/.
2. Open DevTools → Toggle device toolbar (Cmd+Shift+M / Ctrl+Shift+M).
3. Set viewport to **320 px wide** (use the device dropdown or enter custom dimensions).
4. Scroll the page top-to-bottom.
5. Confirm:
   - No horizontal scroll bar appears (check by sliding the page horizontally — should not move).
   - Hero collapses: portrait stacks below the text (or above; layout source order determines which).
   - Each role card spans the full content column (no horizontal split).
   - Outside Work 4-photo grid collapses from 2×2 to 1×4 (single column of 4 photos stacked vertically).
   - All images render at full column width with their original aspect ratios preserved (no squashed/squished/clipped images).
   - The pullquote stat remains readable and properly indented (asymmetric one-sided radius preserved).
6. Resize to 600 px → confirm at exactly 600 px the layout flips to mobile rules (test the breakpoint boundary).
7. Resize to 900 px → confirm desktop rules return (hero 2-col, grid 2x2).

**PASS criteria:** all 7 sub-checks above. **FAIL action:** likely cause is a mobile rule landed outside the existing `@media (max-width: 600px)` block (RESEARCH "Risk Hotspots" row 6); re-audit Plan 09-02 Task 3 Operation B.

---

## Resolution

- When all 5 gates above PASS in a real browser walkthrough, mark Phase 9 fully shipped: update STATE.md → Deferred Items → row for `09-HUMAN-UAT.md` → Status: `complete`.
- Any FAIL triggers a follow-up plan referencing the failing gate and the specific page/element that broke.

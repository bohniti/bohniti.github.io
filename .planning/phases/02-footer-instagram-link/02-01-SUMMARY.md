---
phase: 02
plan: 01
subsystem: theme
tags: [footer, social-icons, css, accessibility, hugo]
requires:
  - themes/minimal/layouts/_default/baseof.html (existing partial wiring)
  - CSS variables --text-secondary, --accent (existing :root block)
  - .site-footer a / .site-footer a:hover (existing rules)
provides:
  - Footer Instagram icon link visible on every page (SOC-01)
  - Instagram link target https://instagram.com/bohniti (SOC-02)
  - Flexoki-aligned monochrome icon styling (SOC-03)
  - .social-icons CSS cluster wrapper for tight icon pairing
  - External-link safety pattern (target=_blank + rel=noopener noreferrer)
  - Icon-only link accessibility pattern (aria-label on a, aria-hidden on svg)
affects:
  - All pages on the site (every page renders footer.html)
tech-stack:
  added:
    - Inline SVG (Lucide-style, monochrome outline, currentColor)
  patterns:
    - currentColor-driven icon color inheritance (no per-icon color CSS)
    - aria-label + aria-hidden pair for icon-only anchors
    - rel="noopener noreferrer" on all external target=_blank links
key-files:
  created: []
  modified:
    - themes/minimal/layouts/partials/footer.html
    - themes/minimal/static/css/style.css
decisions:
  - D-01 honored: socials = icons, nav (About/Blog) = text
  - D-02 honored: GitHub text link converted to icon (not preserved)
  - D-03 honored: inline SVG, no CDN, no icon font
  - D-04 honored: Lucide-style monochrome outlines, 18x18 px, no gradient
  - D-05 honored: stroke=currentColor + fill=none for color inheritance
  - D-06 honored: order is About | Blog | [GitHub-icon] [Instagram-icon]
  - D-07 honored: .social-icons wrapper with 0.6rem inner gap; outer 1.5rem preserved
  - D-08 honored: no new color/hover CSS for icons; inherit via .site-footer a
  - D-09 honored: rel="noopener noreferrer" on both external anchors (also fixes pre-existing GitHub link missing rel)
metrics:
  duration: 84s
  tasks_completed: 2
  files_modified: 2
  files_created: 0
  completed_date: 2026-04-27
---

# Phase 2 Plan 01: Footer Instagram Link Summary

Replaced the footer's GitHub text link with an inline SVG icon, added a clustered Instagram SVG icon link to https://instagram.com/bohniti, and added a small `.social-icons` CSS rule plus a mobile-spacing safeguard — all using `currentColor` so the icons inherit existing footer link colors without introducing new color CSS.

## What Was Done

### Task 1: Footer markup (`themes/minimal/layouts/partials/footer.html`)

**Before** (7 lines):
```html
<footer class="site-footer">
  <div class="footer-links">
    <a href="/about/">About</a>
    <a href="/blog/">Blog</a>
    <a href="https://github.com/bohniti" target="_blank">GitHub</a>
  </div>
</footer>
```

**After** (21 lines): the text nav (`About`, `Blog`) is preserved; the plain-text GitHub link is replaced by a `<span class="social-icons">` containing two icon-only `<a>` elements (GitHub and Instagram). Each `<a>` carries:
- `target="_blank" rel="noopener noreferrer"` (D-09 — also fixes the pre-existing missing `rel` on the old GitHub link)
- `aria-label="GitHub"` / `aria-label="Instagram"` (icon-only links must announce destination)

Each inner `<svg>` carries:
- `width="18" height="18"` (visually balanced with the 0.82rem footer text — Claude's Discretion in D-04)
- `fill="none" stroke="currentColor" stroke-width="2"` (D-04, D-05 — monochrome outline that inherits parent color)
- `aria-hidden="true"` (prevents duplicate screen-reader announcement)
- Lucide-style glyph paths: octocat-outline for GitHub, camera-square for Instagram

Decisions implemented: D-01, D-02, D-03, D-04, D-05, D-06, D-07 (wrapper class), D-09, plus the accessibility baseline from CONTEXT.md.

Commit: `8f43347` — `feat(02-01): convert footer to icon-based social links`

### Task 2: CSS rules (`themes/minimal/static/css/style.css`)

Added a 7-line block inside the existing `/* === Footer === */` section (between `.footer-links {…}` and the `/* === Responsive === */` divider):

```css
.social-icons {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.social-icons a {
  display: inline-flex;
  align-items: center;
}
```

Added one line inside the existing `@media (max-width: 600px)` block (no new media query):

```css
.footer-links { gap: 1rem; }
```

Decisions implemented: D-07 (0.6rem inner cluster gap, locked verbatim), D-08 (no new color/hover rules for icons — inheritance via `currentColor`), and the mobile-spacing safeguard noted under Claude's Discretion in CONTEXT.md.

Commit: `e582cc9` — `feat(02-01): add .social-icons cluster CSS for footer`

## Verification

### Automated (passed)

**Task 1 — `themes/minimal/layouts/partials/footer.html`:**
- `grep -c '<svg'` returns `2` ✓
- `aria-label="GitHub"` present ✓
- `aria-label="Instagram"` present ✓
- `href="https://instagram.com/bohniti"` present ✓
- `href="https://github.com/bohniti"` present ✓
- `grep -c 'rel="noopener noreferrer"'` returns `2` ✓
- `grep -c 'target="_blank"'` returns `2` ✓
- `class="social-icons"` present ✓
- `grep -c 'stroke="currentColor"'` returns `2` ✓
- `grep -c 'aria-hidden="true"'` returns `2` ✓
- `grep -c 'fill="none"'` returns `2` ✓
- Plain-text `>GitHub</a>` no longer present ✓
- `<a href="/about/">About</a>` and `<a href="/blog/">Blog</a>` preserved ✓
- No external icon asset (`<link>`, `<script>`, icon `src=`) introduced ✓

**Task 2 — `themes/minimal/static/css/style.css`:**
- `.social-icons {` block exists ✓
- `gap: 0.6rem` present ✓
- `.social-icons a {` block exists ✓
- `display: inline-flex` present ✓
- `.footer-links { gap: 1rem; }` mobile rule present ✓
- Single `@media (max-width: 600px)` block (no duplicates) ✓
- `.social-icons` rule appears before `/* === Responsive === */` (still in Footer section) ✓
- No new color/stroke/fill CSS rule introduced for `.social-icons` ✓
- No new vendor prefixes ✓

### Phase Verification (passed)

- **SOC-01 (icon visible on every page):** `themes/minimal/layouts/_default/baseof.html` includes the partial via `{{ partial "footer.html" . }}`; the partial now contains an Instagram `<svg>` inside an `<a aria-label="Instagram">`. Confirmed by grep against baseof.html.
- **SOC-02 (links to https://instagram.com/bohniti):** `grep -q 'href="https://instagram.com/bohniti"'` succeeds.
- **SOC-03 (matches Flexoki minimal aesthetic):** Icons use `stroke="currentColor"` + `fill="none"`, so they render as `var(--text-secondary)` (#6F6E69) at rest and `var(--accent)` (#AF3029) on hover via the existing `.site-footer a` rules. No new color tokens, fonts, or external assets introduced. Glyphs are monochrome outlines (D-04 — explicitly NOT the Instagram brand gradient).

### Build Sanity

Hugo is not installed locally on this machine (per CLAUDE.md note: "Hugo is NOT installed locally"). The CI workflow at `.github/workflows/deploy.yml` will validate the build on push. Risk is minimal because:
- `footer.html` remains pure HTML (no Hugo template directives added).
- `style.css` is a static asset (Hugo passthrough).
- No new shortcodes, partials, or template syntax introduced.

### Manual Verification (recommended next step)

Run `hugo server` (when Hugo is available locally) or push to `main` and visit the deployed site. Manual checks to perform:

1. Load `/`, `/about/`, and a blog post (e.g., `/blog/2026-03-27-video-editing-journey/`) — Instagram icon should appear in the footer of all three.
2. Click the Instagram icon — should open `https://instagram.com/bohniti` in a new tab.
3. Hover the Instagram and GitHub icons — color should shift from muted gray (`#6F6E69`) to red (`#AF3029`), matching the existing About/Blog hover behavior.
4. Tab through the footer with the keyboard — focus rings should remain visible on both icons.
5. Resize the viewport below 600px — the social cluster should remain on a single visual row with the text nav, with comfortable spacing.

## Deviations from Plan

None. Every value (icon dimensions, gap values, glyph paths, attribute set) was locked by the plan; no Rule 1/2/3 auto-fixes were needed during execution. Both tasks were committed exactly as specified.

## Threat Flags

None. The change introduces only client-side markup/CSS; the only network surface is the two outbound external links (`github.com/bohniti`, `instagram.com/bohniti`), both already mitigated by `rel="noopener noreferrer"` (D-09).

## Self-Check: PASSED

**Files claimed modified:**
- `themes/minimal/layouts/partials/footer.html` — FOUND
- `themes/minimal/static/css/style.css` — FOUND

**Commits claimed:**
- `8f43347` (feat(02-01): convert footer to icon-based social links) — FOUND
- `e582cc9` (feat(02-01): add .social-icons cluster CSS for footer) — FOUND

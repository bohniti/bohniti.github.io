# Personal Website Refinements

## What This Is

Timo's personal website and blog, built with Hugo and a custom minimal theme, deployed to GitHub Pages at tbohnstedt.cloud. The site evolves milestone-by-milestone — first as a polished technical reference (v1.0), now into a branded space with a coherent visual identity, theming, and a photo gallery (v2.0).

## Core Value

The blog should be a polished, technical reference that's useful for future-me — clear diagrams over screenshots, precise values over vague descriptions — and feel unmistakably like *Timo's site* in either light or dark mode.

## Current Milestone: v2.0 Brand & Gallery

**Goal:** Establish a cohesive visual identity (logo + dark/light theming) and add a photo gallery — the site looks like *Timo's site* on every page in either theme.

**Target features:**
- Light/dark mode with header toggle, OS-preference detection, persistence, no flash on load
- Split `images/logos.png` sprite into individual logo/icon/minimum/favicon assets (dark + light variants)
- Branded header — script "time BOHNSTEDT" wordmark replaces the text site title, swaps with theme
- Browser favicon set wired into `<head>`
- Standalone `/gallery/` page in nav, grid layout using the 18 photos in `images/galary/` (rename to `gallery/`), web-optimized
- Richer About page — embed personal photos inline

## Requirements

### Validated

- ✓ Hugo static site with custom minimal theme — existing
- ✓ Blog posts with co-located images (page bundles) — existing
- ✓ Markdown content with YAML front matter — existing
- ✓ GitHub Pages deployment via GitHub Actions — existing
- ✓ Header navigation with Blog and About links — existing
- ✓ Unsafe HTML rendering for rich embeds (Instagram, maps, charts) — existing
- ✓ Responsive layout with Flexoki-inspired design — existing
- ✓ Mermaid shortcode renders Flexoki-themed diagrams in posts — Phase 1 (v1.0)
- ✓ Per-node Parameter/Range/Tip tables in DaVinci color grading article — Phase 1 (v1.0)
- ✓ Instagram icon in footer with `.social-icons` cluster CSS — Phase 2 (v1.0)
- ✓ Eight brand asset PNGs at `themes/minimal/static/images/brand/` produced by reproducible Pillow + pngquant pipeline; aspect-pair matched per asset class for theme-toggle parity — Phase 3 (v2.0)
- ✓ Light/dark theme toggle in header with persistence, OS-preference detection, no-FOUC inline IIFE, and reduced-motion support — Phase 4 (v2.0)

### Active (v2.0)

- [ ] Site header shows the script wordmark instead of plain "Timo Bohnstedt" text
- [ ] Favicon set wired into Hugo `<head>` partial
- [ ] `/gallery/` page reachable from main nav with optimized photo grid
- [ ] Renamed `images/galary/` → `images/gallery/`
- [ ] About page enriched with inline personal photos

### Out of Scope

- Full site redesign beyond brand + theme — keep the minimal Flexoki structure
- New blog posts during this milestone — content additions deferred
- Other social media links beyond existing GitHub + Instagram
- E-commerce, CMS, comments, or any backend services
- Animations beyond a minimal theme-toggle transition
- Multi-language support

## Context

- Source brand asset: `images/logos.png` is a 2×4 sprite sheet — top row dark-background variants, bottom row light-background variants. Columns: Logo (script "time BOHNSTEDT" with climber), Icon (TB monogram), Minimum (script "time" only), Favicon (TB in circle).
- Photo source: 18 personal photos in `images/galary/` (typo in folder name — slated for rename). File sizes range 150 KB → 7.5 MB; web optimization is required before serving.
- Existing CSS: single stylesheet at `themes/minimal/static/css/style.css`, Flexoki-inspired light palette only — dark palette must be added.
- Hugo Extended 0.157.0 is pinned (gives us SCSS + image processing if needed).
- Theme files: `themes/minimal/layouts/_default/baseof.html` (head), `partials/header.html`, `partials/footer.html`, `_default/single.html`, `_default/list.html`.
- About page (`content/about.md`) is text-only today — needs image support.
- No JS framework is allowed; theme toggle must be vanilla JS, inline in `<head>` to prevent flash.

## Constraints

- **Tech stack**: Hugo static site, no JS frameworks, vanilla JS only, keep it minimal
- **Theme**: Must remain Flexoki-inspired in both light and dark modes
- **No flash on load**: Theme must apply before first paint — inline `<head>` script reading `localStorage` + `prefers-color-scheme`
- **Performance**: Gallery must not balloon page weight — optimize images via Hugo's `image.Resize` / `image.Fill` + `loading="lazy"`
- **Accessibility**: Theme toggle must be keyboard-reachable, have an `aria-label`, and respect `prefers-reduced-motion`
- **Brand consistency**: Same logo source must drive both header wordmark and favicon — no manual redraws

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Mermaid for diagrams | User preference, renders inline, version-controllable as text | ✓ Validated (Phase 1, v1.0) |
| Instagram icon in footer | Visible on every page, standard placement for social links | ✓ Validated (Phase 2, v1.0) |
| OS preference + localStorage for theme | Respects user's system, preserves explicit choice | ✓ Validated (Phase 4, v2.0) |
| Standalone `/gallery/` page in nav | Gives photos a first-class home, keeps About lean | — Pending |
| Header wordmark replaces text title | Stronger brand presence, swaps cleanly per theme | — Pending |
| Rename `images/galary/` → `images/gallery/` | Fix typo before it ships in URLs | — Pending |
| Hugo image processing for gallery | Built-in, no external dependency, generates responsive sizes | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-29 — Phase 4 complete (light/dark theme toggle with no-FOUC IIFE, persistence, OS-preference detection, reduced-motion support)*

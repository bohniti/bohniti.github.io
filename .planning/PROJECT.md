# Personal Website Refinements

## What This Is

Timo's personal website and blog, built with Hugo and a custom minimal theme, deployed to GitHub Pages at tbohnstedt.cloud. This milestone focuses on refining the latest video editing blog post and adding an Instagram social link.

## Core Value

The blog should be a polished, technical reference that's useful for future-me — clear diagrams over screenshots, precise values over vague descriptions.

## Requirements

### Validated

- ✓ Hugo static site with custom minimal theme — existing
- ✓ Blog posts with co-located images (page bundles) — existing
- ✓ Markdown content with YAML front matter — existing
- ✓ GitHub Pages deployment via GitHub Actions — existing
- ✓ Header navigation with Blog and About links — existing
- ✓ Unsafe HTML rendering for rich embeds (Instagram, maps, charts) — existing
- ✓ Responsive layout with Flexoki-inspired design — existing

### Active

- [ ] Replace Node tree screenshot with inline Mermaid diagram in video editing article
- [ ] Add precise value ranges, practical tips (do/don't) for each color grading node
- [ ] Make node descriptions shorter and more technical
- [ ] Add Instagram icon in site footer linked to instagram.com/bohniti

### Out of Scope

- Full site redesign — this is a targeted refinement
- New blog posts — focus on refining the existing article
- Other social media links — only Instagram requested
- Changes to other blog posts — only the video editing article

## Context

- The video editing article (2026-03-27) has a 5-node DaVinci Resolve color grading template described in text and a screenshot (`Node tree.png`)
- The user wants the screenshot replaced with a Mermaid diagram rendered inline by Hugo
- Node descriptions should include value ranges and practical tips (what should/shouldn't happen in the image)
- The site uses a `minimal` custom theme with partials for header and footer
- No existing social links in footer — this will be the first
- Instagram handle: @bohniti (https://instagram.com/bohniti)
- Hugo config is in `hugo.toml`, theme templates in `themes/minimal/`

## Constraints

- **Tech stack**: Hugo static site, no JS frameworks, keep it minimal
- **Theme**: Must fit the existing Flexoki-inspired minimal aesthetic
- **Mermaid**: Hugo needs to render Mermaid diagrams — may need shortcode or JS include
- **Icon**: Should be simplistic, matching the site's minimal design

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Mermaid for diagram | User preference, renders inline, version-controllable as text | — Pending |
| Instagram icon in footer | Visible on every page, standard placement for social links | — Pending |

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
*Last updated: 2026-03-27 after initialization*

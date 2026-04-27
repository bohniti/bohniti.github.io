# Roadmap: Personal Website Refinements

## Overview

Two focused refinements to the personal site: first, upgrade the video editing blog post from screenshot-based to diagram-based with tighter technical writing; second, add an Instagram social link to the site footer. Both are independent and deliver visible improvements.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Article Refinement** - Replace node tree screenshot with Mermaid diagram and sharpen node descriptions with values and tips
- [ ] **Phase 2: Footer Instagram Link** - Add Instagram icon to site footer matching minimal aesthetic

## Phase Details

### Phase 1: Article Refinement
**Goal**: The video editing article becomes a precise technical reference with an inline diagram and actionable node descriptions
**Depends on**: Nothing (first phase)
**Requirements**: ART-01, ART-02, ART-03, ART-04, ART-05
**Success Criteria** (what must be TRUE):
  1. The video editing article displays a Mermaid diagram showing the 5-node color grading chain instead of the Node tree screenshot
  2. Each node description includes specific parameter value ranges (e.g., Lift, Gamma, Gain values)
  3. Each node includes at least one practical do/don't tip about what the image should look like
  4. Node descriptions are noticeably shorter and more technical than the current prose
**Plans:** 2 plans
Plans:
- [x] 01-01-PLAN.md — Create Hugo `mermaid` shortcode with Flexoki theme variables (Wave 1)
- [x] 01-02-PLAN.md — Rewrite article with Mermaid diagram, per-node Parameter/Range/Tip tables, tighten prose, delete Node tree.png (Wave 2, depends on 01-01)

### Phase 2: Footer Instagram Link
**Goal**: Every page on the site shows an Instagram link in the footer that fits the existing design
**Depends on**: Nothing (independent of Phase 1)
**Requirements**: SOC-01, SOC-02, SOC-03
**Success Criteria** (what must be TRUE):
  1. An Instagram icon is visible in the site footer on every page
  2. Clicking the icon navigates to https://instagram.com/bohniti
  3. The icon's style is consistent with the site's minimal Flexoki-inspired aesthetic
**Plans:** 1 plan
Plans:
- [ ] 02-01-PLAN.md - Add Instagram icon + convert GitHub link to icon in footer.html, add .social-icons cluster CSS (Wave 1)
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Article Refinement | 0/2 | Not started | - |
| 2. Footer Instagram Link | 0/1 | Not started | - |

---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Design Update
status: planning
last_updated: "2026-05-01T09:02:10.619Z"
last_activity: 2026-05-01
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-28)

**Core value:** The blog should be a polished, technical reference -- clear diagrams over screenshots, precise values over vague descriptions -- and feel unmistakably like *Timo's site* in either light or dark mode.
**Current focus:** Phase 07 — about-enrichment

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-05-01 — Milestone v3.0 started

## Performance Metrics

**Velocity (lifetime, all milestones):**

- Total plans completed: 18
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan | Milestone |
|-------|-------|-------|----------|-----------|
| 01 | 2 | - | - | v1.0 |
| 02 | 1 | - | - | v1.0 |
| 04 | 3 | - | - | v2.0 |

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 02 P01 | 84s | 2 tasks | 2 files |
| Phase 04 P01 | 97s | 3 tasks | 1 file |
| Phase 04 P02 | 169s | 2 tasks | 1 file |
| Phase 04 P03 | ~60s | 3 tasks | 2 files |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 07 P01 | 6m | 2 tasks | 3 files |
| Phase 07 P02 | 4m | 2 tasks | 2 files |
| Phase 07 P03 | 1m | 2 tasks | 5 files |
| Phase 07 P04 | 5m | 3 tasks | 4 files |

## Accumulated Context

### Roadmap Evolution

- Phase 05.1 inserted after Phase 5: Swap wordmark + favicon to new SVG sources at `images/brand-source/{logo.svg, fav-icon.svg}` (URGENT)

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.

Recent decisions affecting current work:

- Phase 04 P03: Co-located first-paint button-sync and click handler in one IIFE — single querySelector('.theme-toggle'), single closure, atomic-mutation contract locally readable
- Phase 04 P03: Adopted dark-first conditional form (next === 'dark' ? '#100F0F' : '#FFFCF0') across all writes inside the click handler to mirror the head IIFE's pattern from Plan 02
- Phase 04 P03: No DOMContentLoaded — script sits at end-of-body, parser has already reached the toggle button
- Phase 04 P03: Did not factor the five mutations into helper functions — kept inline so the atomic-side-effect contract is locally readable
- v2.0: OS-preference + localStorage drives theme; no flash on load via inline `<head>` script
- v2.0: Standalone `/gallery/` page (not embedded in About)
- v2.0: Header wordmark replaces text site title
- v2.0: Rename `images/galary/` -> `content/gallery/photos/` (move into Hugo content tree, not just rename in place)
- v2.0: Pillow one-off slicer (not Hugo `Crop`); 8 sliced PNGs committed to `themes/minimal/static/images/brand/`
- v2.0: 3-file favicon set (`.ico` + `.svg` with embedded dark-mode @media + `apple-touch-icon.png`); skip legacy `mstile-*` / `browserconfig.xml`
- v2.0: Two-image CSS toggle for wordmark (not `<picture>` + `prefers-color-scheme`); each variant must be ≤ 30 KB
- v2.0: Hugo `image.Process` page-bundle pipeline for gallery (WebP only, no AVIF — Hugo 0.157 doesn't support it)
- v2.0: Phase 6 (Gallery) recommended for `/gsd-research-phase` during planning; other v2.0 phases use locked-in patterns
- [Phase ?]: Phase 07 P01: Hugo render-image hook with three-arm title-keyword switch (hero 480x600 q80, grid 400x300 q75, default 800x600 q78) plus defensive passthrough fallback — deferred Phase 6 follow-up now codebase-validated infrastructure
- [Phase ?]: Phase 07 P01: Used cooking.JPG (uppercase) in markdown image ref to match filesystem case — Hugo GetMatch is case-sensitive; lowercase would force defensive fallback and lose CLS-clean width/height
- [Phase ?]: Phase 07 P02: Discovered Hugo 0.161 does NOT auto-derive Type from leaf-bundle directory name; added explicit type: about to content/about/index.md so body.page-about resolves at runtime (Rule 2 deviation fix)
- [Phase ?]: Phase 07 P02: Adopted dual-selector pattern so the same CSS rules apply across both DOM rendering paths (wrapper-div+markdown OR render-image-hook-emitted class)
- [Phase ?]: Phase 07 P02: Documented WCAG AA-large caveat on .about-pullquote strong as load-bearing CSS comment — dark-theme contrast is 3.97:1 which passes only because parent text is 1.4rem + 500-weight
- [Phase ?]: Phase 07 P03: Preserved cooking.JPG uppercase extension on disk to match Plan 07-01 case-corrected markdown ref; renaming to lowercase would require touching the markdown which is out of scope for an asset-arrival plan
- [Phase ?]: Phase 07 P03: exiftool reported '5 unchanged' on the D-17 scrub because targeted GPS/Make/Model/Serial fields were already absent from sources (likely AirDrop pre-stripped); D-27 verification gate is source-of-truth and passed with zero matching field rows
- [Phase ?]: Phase 07 P03: Did NOT broaden EXIF scrub to LensMake/LensModel/CreatorTool — D-17 explicitly enumerates GPS/Make/Model/Serial scope; broadening is future privacy-hardening, not asset-arrival
- [Phase ?]: Phase 07 P04: D-26 verify regex used quoted attribute values (`width="N"`) which Hugo --minify strips — verified the underlying invariant (5/5 About images have explicit width + height) directly via minify-aware grep instead of patching the historical plan file
- [Phase ?]: Phase 07 P04: Auto-fixed 2 stale `content/about.md` refs in CLAUDE.md (Rule 2 — D-30 cleanup contract requires zero stale refs in tracked source files) and added `.claude/` to .gitignore (Rule 2 — agent runtime mirror copies should never be tracked)
- [Phase ?]: Phase 07 P04: Phase 7 complete; milestone v2.0 reaches 100% with HUMAN-UAT deferred to post-deploy checklist at .planning/phases/07-about-enrichment/07-HUMAN-UAT.md

### Pending Todos

None yet.

### Blockers/Concerns

(v2.0 blockers cleared at milestone close 2026-05-01 — see `.planning/milestones/v2.0-ROADMAP.md` for historical context.)

## Deferred Items

Items acknowledged and deferred at v2.0 milestone close on 2026-05-01:

| Category | Phase | Item | Status | Resolution Path |
|----------|-------|------|--------|-----------------|
| uat | 05 | 05-HUMAN-UAT.md (4 scenarios) | partial | Post-deploy browser walkthrough |
| uat | 05.1 | 05.1-HUMAN-UAT.md (6 scenarios) | partial | Post-deploy browser walkthrough |
| uat | 06 | 06-HUMAN-UAT.md | unknown | Post-deploy browser walkthrough |
| uat | 07 | 07-HUMAN-UAT.md | unknown | Post-deploy browser walkthrough at https://tbohnstedt.cloud/about/ |
| verification | 05 | 05-VERIFICATION.md | human_needed | Confirm favicon in tab/bookmark/iOS home-screen after deploy |
| verification | 05.1 | 05.1-VERIFICATION.md | human_needed | Confirm SVG favicon prefers-color-scheme swap in real browsers |

All items gated on the same trigger: push commits → GitHub Actions deploy → walk the `*-HUMAN-UAT.md` checklists in a browser. Implementation is shipped; automated gates are green; deferral was the planned exit pattern.

## Session Continuity

Last session: 2026-05-01T07:49:30.000Z
Stopped at: Phase 7 complete; milestone v2.0 100% (HUMAN-UAT pending post-deploy)
Resume file: None

**Next Phase:** None — milestone v2.0 complete. User next action: push commits, watch GitHub Actions deploy, then run `.planning/phases/07-about-enrichment/07-HUMAN-UAT.md` checklist against deployed `https://tbohnstedt.cloud/about/` URL.

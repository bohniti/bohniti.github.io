---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Design Update
status: executing
stopped_at: Phase 10 UI-SPEC approved
last_updated: "2026-05-04T07:26:57.003Z"
last_activity: 2026-05-04 -- Phase 10 planning complete
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 8
  completed_plans: 5
  percent: 63
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-01)

**Core value:** The blog should be a polished, technical reference -- clear diagrams over screenshots, precise values over vague descriptions -- and feel unmistakably like *Timo's site* in either light or dark mode.
**Current focus:** Phase 09 — about-dynamic-rounded-redesign

## Current Position

Phase: 09 (about-dynamic-rounded-redesign) — EXECUTING
Plan: 3 of 3
Status: Ready to execute
Last activity: 2026-05-04 -- Phase 10 planning complete

Progress: [██████████] 100%

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
| 07 | 4 | ~16m | ~4m | v2.0 |

**Recent Trend:**

- Last 5 plans: Phase 07 P01 (6m), P02 (4m), P03 (1m), P04 (5m)
- Trend: Stable around 4-min plan execution

*Updated after each plan completion*
| Phase 08-icon-svg-theme-toggle P01 | 5min | 2 tasks | 2 files |
| Phase 08-icon-svg-theme-toggle P02 | 1min | 1 tasks | 1 files |
| Phase 09-about-dynamic-rounded-redesign P01 | 2 min | 3 tasks | 5 files |
| Phase 09 P02 | 4 min | 3 tasks | 3 files |
| Phase 09 P03 | 2 min | 2 tasks | 2 files |

## Accumulated Context

### Roadmap Evolution

- v3.0 roadmap committed 2026-05-01: 3 phases (8 ICON, 9 ABOUT, 10 GALLERY), 21 requirements, ordered by ascending blast radius
- Locked decisions encoded in roadmap: gallery `params.weight` ordering (no shuffle), About layout+content ship together, lightbox keyboard nav day-one, zero new runtime deps

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.

Recent decisions affecting current work:

- v3.0: Gallery ordering = author-controlled `params.weight` deterministic frontmatter (resolves STACK/ARCHITECTURE/PITFALLS conflict surfaced in research/SUMMARY.md)
- v3.0: About layout redesign + content rewrite ship in same milestone (no two-step rollout)
- v3.0: Lightbox keyboard nav (Esc, ←/→, focus-trap, focus restoration) is day-one scope
- v3.0: Phase ordering ICON → ABOUT → GALLERY justified by ascending blast radius (smallest/no-JS first; only-JS-adding phase last)
- v3.0: Phase 10 NOT split into 10a/10b — coarse granularity favors fewer phases; lightbox JS depends on template depends on frontmatter (tight coupling, no clean half-shipped state with user value)
- v2.0: OS-preference + localStorage drives theme; no flash on load via inline `<head>` script
- v2.0: Hugo render-image hook with title-keyword switch (validated Phase 7) — extends naturally for v3.0 Phase 9 with new arms (`split`, `feature`, `card`)
- [Phase ?]: Phase 8 Plan 01: Used inline-grid stacking + 150ms opacity transition for icon toggle (matches body 150ms transitions; cleaner than position: absolute)
- [Phase ?]: Phase 8 Plan 01: 44×44 hit target via min-width/min-height + place-items: center on button shell — decouples 24px icon size from interactive hit area (WCAG 2.5.5)
- [Phase ?]: Phase 8 Plan 01: CSS-only [data-theme] visibility swap with defensive :root:not([data-theme="dark"]) selector — zero JS in icon swap path
- [Phase 8]: Phase 8 Plan 02: Rewrote end-of-body IIFE — replaced toggle.textContent with toggle.setAttribute('aria-label', …) using action-oriented strings ('Switch to dark mode' / 'Switch to light mode'); preserved dataset.theme/aria-pressed/localStorage/meta theme-color sync verbatim; head IIFE byte-identical to v2.0 (Pitfall 1 contract preserved)
- [Phase 09-about-dynamic-rounded-redesign]: Plan 09-01 ships feature shortcode + hook arm together with pullquote/split (never half-ship per RESEARCH risk-hotspots) — UI-SPEC FLAG recommendation + ~16 LOC slack preserved for HUMAN-UAT follow-ups
- [Phase 09-about-dynamic-rounded-redesign]: render-image hook uses pre-bound boolean variables (isSplit, isFeature) per D-07 — Matches existing isHero/isGrid pattern; UI-SPEC Gate 2 needs adaptation in Plan 09-03 to grep boolean decls instead of inline eq title
- [Phase 09-about-dynamic-rounded-redesign]: split arm uses fit not fill (fit 600x450 webp q78) per Pitfall 19 — Preserves portrait/landscape aspect without cropping faces
- [Phase 09-about-dynamic-rounded-redesign]: All 3 new shortcodes use .Inner | markdownify (NOT safeHTML) per PATTERNS Shared Pattern 5 — Bodies contain markdown (bold, image syntax); mermaid stays on safeHTML because its body is mermaid DSL
- [Phase 09-about-dynamic-rounded-redesign]: radius-soft token declared once in light root only; dark theme inherits via cascade (D-08) — Radius is theme-invariant; CSS custom-property cascade handles inheritance to dark theme without explicit duplication
- [Phase 09]: Layout uses range .Params.roles directly + omits .page-header chrome (intentional divergence from gallery analog per UI-SPEC); pullquote one-sided radius preserved (D-09) — UI-SPEC § Page-level skeleton requires no .page-header chrome on About; D-09 locks one-sided 0 4px 4px 0 as a deliberate visual signal

### Pending Todos

None yet.

### Blockers/Concerns

None yet for v3.0. (v2.0 blockers cleared at milestone close 2026-05-01 — see `.planning/milestones/v2.0-ROADMAP.md` for historical context.)

## Deferred Items

Items deferred from v2.0 close (carried forward; gated on post-deploy browser walkthrough):

| Category | Phase | Item | Status | Resolution Path |
|----------|-------|------|--------|-----------------|
| uat | 05 | 05-HUMAN-UAT.md (4 scenarios) | partial | Post-deploy browser walkthrough |
| uat | 05.1 | 05.1-HUMAN-UAT.md (6 scenarios) | partial | Post-deploy browser walkthrough |
| uat | 06 | 06-HUMAN-UAT.md | unknown | Post-deploy browser walkthrough |
| uat | 07 | 07-HUMAN-UAT.md | unknown | Post-deploy browser walkthrough at https://tbohnstedt.cloud/about/ |
| uat | 09 | 09-HUMAN-UAT.md (5 gates) | partial | Post-deploy browser walkthrough at https://tbohnstedt.cloud/about/ |
| verification | 05 | 05-VERIFICATION.md | human_needed | Confirm favicon in tab/bookmark/iOS home-screen after deploy |
| verification | 05.1 | 05.1-VERIFICATION.md | human_needed | Confirm SVG favicon prefers-color-scheme swap in real browsers |

All items gated on the same trigger: push commits → GitHub Actions deploy → walk the `*-HUMAN-UAT.md` checklists in a browser. Implementation is shipped; automated gates are green; deferral was the planned exit pattern.

## Session Continuity

Last session: 2026-05-04T07:07:52.204Z
Stopped at: Phase 10 UI-SPEC approved
Resume file: .planning/phases/10-gallery-lightbox-masonry-captions/10-UI-SPEC.md

**Next user action:** Run `/gsd-plan-phase 8` to decompose Phase 8 (ICON — SVG Theme Toggle) into plans.

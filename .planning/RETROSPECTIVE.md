# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.0 — Brand & Gallery

**Shipped:** 2026-05-01
**Phases:** 6 (3, 4, 5, 05.1, 6, 7) | **Plans:** 19 | **Commits:** 98 | **Timeline:** 3 days

### What Was Built

- **Theming foundation** — Flexoki dark palette under `:root[data-theme="dark"]`, no-FOUC inline `<head>` IIFE, accessible `<button>` toggle (`aria-pressed`, `prefers-reduced-motion`, `theme-color` meta sync). Mermaid/Plotly/Leaflet readability validated in dark mode.
- **Wordmark + favicon** — Initial Phase 5 PNG-swap implementation, then mid-milestone migration in Phase 05.1 to inline SVG (`readFile + safeHTML` + `currentColor + var(--text)`) and a 4.8 KB native path-based `favicon.svg` with embedded `prefers-color-scheme` rule. Build script slimmed from 205 → 69 LOC via cairosvg pipeline.
- **Gallery** — `/gallery/` page bundle, 18 photos, Hugo `image.Process` WebP pipeline (q75 thumbs / q82 fulls), zero GPS/Make/Model/Serial in published output, ≤ 2 MB first-paint.
- **About enrichment** — Leaf bundle conversion with hero/pullquote/grid render-image hook; 5 EXIF-scrubbed personal photos; `/about/` URL preserved.

### What Worked

- **Mid-milestone insertion of Phase 05.1** — Recognizing that the Phase 5 PNG-swap path was the wrong long-term approach and inserting a decimal-numbered "swap to SVG sources" phase rather than retro-editing Phase 5 kept history honest and the migration auditable. The decimal numbering convention earned its keep here.
- **Source-side EXIF scrub (Phases 6 + 7)** — Stripping privacy-sensitive metadata at photo-arrival time, not at build time, makes leakage structurally impossible. Build can't leak what isn't there.
- **Coarse granularity + yolo mode for solo work** — Auto-approved scope verification kept pace high; no blocking confirmations interrupted execution. Worked because all phases had pre-approved scope from PROJECT.md/ROADMAP.md.
- **Phase 6 research-flagged** — The `Recommend /gsd-research-phase` annotation on Phase 6 (gallery) anticipated empirical thumbnail-dimension/quality tuning correctly. Other v2.0 phases used locked-in patterns and shipped faster.
- **Atomic-side-effect contract for theme toggle** — Co-locating the first-paint sync and click handler in one IIFE (single `querySelector`, single closure, all five mutations inline) made the contract locally readable.

### What Was Inefficient

- **REQUIREMENTS.md traceability drift** — The traceability table accumulated `Pending` markers across Phases 3, 4, 6 even after each phase shipped. Discovered at milestone-close pre-flight: 16/24 v2 rows were stale despite shipped reality. Workflow asks for traceability updates at phase-transition time, but that habit didn't form. **Lesson:** Add traceability-update reminder to phase-completion ritual, or auto-derive Status from PROJECT.md Validated section.
- **Phase 3 (sliced PNGs) was wasted work** — Building the PNG slicer + 8 sliced PNGs only to retire them in Phase 05.1 a day later represents real wasted effort. Root cause: SVG sources weren't on the table during initial scoping; the fact they existed only surfaced after Phase 5 wiring revealed the PNG path's awkwardness (77 KB favicon, two-image swap fragility). **Lesson:** During v2.0 scoping, ask "does a vector source exist?" before locking the asset pipeline shape.
- **HUMAN-UAT scenarios deferred 4 phases deep** — Phases 05, 05.1, 06, 07 all shipped with `*-HUMAN-UAT.md` post-deploy walkthroughs gated on a deploy that hadn't happened yet. By the end of the milestone, six items were stacked waiting on a single deploy push. **Lesson:** For sites with a deploy-only verification mode (browser tabs, iOS home-screens, real GitHub Pages URL), bundle the deploy-and-verify sweep into milestone close, not as a deferred backlog.
- **Phase 1-2 directories not present at archive time** — v1.0 phase directories were already cleaned up before v2.0 close, so there was no live SUMMARY data to extract for the v1.0-ROADMAP.md archive (only retroactive reconstruction from PROJECT.md). Creates an asymmetry between v1.0 and v2.0 archive depth. **Lesson:** Don't run `/gsd-cleanup` until after `/gsd-complete-milestone`, or accept that retro-archived milestones will be summary-only.

### Patterns Established

- **Decimal-phase insertion as a course-correction tool** — Phase 05.1 demonstrates the pattern: when a completed phase reveals the wrong implementation path, insert `N.1` between `N` and `N+1` to migrate, rather than retro-editing `N`. Keeps git history honest.
- **Source-side privacy hardening** — `exiftool` scrub at file-arrival time (Phases 6 + 7) is the structural fix. Build-time scrub is belt-and-suspenders, not the primary defense.
- **Render-image hook with title-keyword switch** — Phase 7 introduced the `themes/minimal/layouts/_default/_markup/render-image.html` pattern with hero/grid/default sizing keyed off image alt-text. Reusable for future image-heavy pages without per-image CSS.
- **Inline `<head>` IIFE with `<= 600 byte` budget** — Phase 04 P02 hit a "raw size exceeded the 600-byte must_haves cap" deviation; pattern is to keep the no-FOUC bootstrap minimal and push everything else to end-of-body.
- **Co-locate atomic side effects** — Phase 4 P03 lesson: when a click handler must mutate 5 things atomically (data-theme, aria-pressed, textContent, localStorage, theme-color meta), keep them in one inline closure. Don't factor into helpers — locality > DRY here.
- **Hugo Type derivation requires explicit frontmatter** — Phase 7 P02 discovered Hugo 0.161 does NOT auto-derive `Type` from leaf-bundle directory name; explicit `type: about` in frontmatter is required for body-class hooks to resolve.

### Key Lessons

1. **Ask "does a vector source exist?" before locking any raster pipeline.** Phase 3 → 05.1 wasted ~1 day. The cost of the question is zero; the cost of not asking is a phase of throwaway work.
2. **Update REQUIREMENTS.md traceability at phase-transition time, not milestone-close time.** A 16/24 stale-row reconciliation at close is a process smell.
3. **Bundle deploy-and-verify into milestone close for static-deploy-only verification work.** Six deferred HUMAN-UAT items stacked waiting on a single push is unnecessary friction — the deploy itself is one git push away.
4. **Decimal-phase insertion is a feature, not a smell.** When a shipped phase reveals the wrong path, name the migration explicitly (Phase N.1) rather than amending Phase N's history.
5. **For solo work with pre-approved scope, yolo mode + coarse granularity is the right default.** No blocked execution; planning gates already satisfied at PROJECT.md/ROADMAP.md scoping time.

### Cost Observations

- Sessions: not tracked in detail; milestone spanned 3 days of focused work.
- Notable: 19 plans across 6 phases at ~3 days suggests ~6 plans/day pace — sustainable because each plan was small (1-3 files, 1-3 tasks). Coarse granularity stays manageable when phases are decomposed at the right grain.
- Model: Opus 4.7 (1M context) used for execution; profile = quality.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Process Change |
|-----------|--------|-------|--------------------|
| v1.0 | 2 | 3 | Initial milestone; targeted refinement scope |
| v2.0 | 6 | 19 | Decimal-phase insertion (05.1); source-side EXIF scrub pattern; render-image hook |

### Cumulative Quality

| Milestone | Code LOC Added | Privacy Gates | Accessibility Gates |
|-----------|----------------|---------------|---------------------|
| v1.0 | (not measured) | — | — |
| v2.0 | +1,173 (49 files) | EXIF scrub (Phases 6 + 7); zero GPS/Make/Model/Serial in published output | `aria-pressed`, `prefers-reduced-motion`, `color-scheme`, `theme-color` meta (Phase 4) |

### Top Lessons (Cross-Milestone)

1. **Reconcile traceability at phase-transition time** — surfaced as a v2.0 close pain point; will validate during v3.0 by checking REQUIREMENTS.md sync at each `/gsd-execute-phase` exit.
2. **Source-side privacy hardening structurally beats build-time scrubbing** — validated on Phases 6 + 7; pattern is portable to any future asset-handling phase.
3. **Decimal-phase insertion preserves history honesty** — validated once on 05.1; expect to use again when shipped paths reveal wrong-direction work.

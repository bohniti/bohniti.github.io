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

## Milestone: v3.0 — Design Update

**Shipped:** 2026-05-04
**Phases:** 3 (8, 9, 10) | **Plans:** 8 | **Tasks:** 13 | **Timeline:** 4 days

### What Was Built

- **ICON (Phase 8)** — Sun/moon Lucide v0.547.0 inline-SVG button replacing the v2.0 text "Dark" button. CSS-only `[data-theme]` visibility swap (zero JS in the swap path), 44×44 hit target via `place-items: center` shell, reduced-motion-gated 150 ms opacity cross-fade. End-of-body IIFE rewritten to set action-oriented `aria-label` ("Switch to dark mode" / "Switch to light mode") while preserving v2.0 persistence/`aria-pressed`/`theme-color` sync verbatim.
- **ABOUT (Phase 9)** — New `themes/minimal/layouts/about/single.html` template, 3 new Hugo shortcodes (`pullquote`, `split`, `feature`), 2 new render-image hook arms (`split`, `feature`), `--radius-soft: 12px` token applied site-wide. Asymmetric alternating text/image layout balancing professional background with climbing/cycling/cooking. WCAG AA-large pullquote contrast preserved in dark theme.
- **GALLERY (Phase 10)** — Native `<dialog>` lightbox (free focus-trap via `showModal()`) with 12 px `backdrop-filter: blur` and rgba fallback, CSS `column-count` masonry (3/2/1 cols at 900/600/<600 px), per-photo `params.weight`-driven deterministic order, optional frontmatter captions with graceful empty rendering, 50 px deltaX touch-swipe nav, page-scoped vanilla-JS IIFE in `lightbox.js`. EXIF scrub CI gate added.
- **Post-execution patches** — `images.AutoOrient` filter chained before every `.Process` call (8 sites in 3 templates) to fix EXIF rotation regression; 5 author-written gallery captions + 1 new photo (Lofoten sunset) added during the milestone-close session.

### What Worked

- **Coarse granularity held up** — 8 plans across 3 phases at 4 days = ~2 plans/day. Same pace as v2.0 (~6/day) but on harder phases (lightbox JS, asymmetric layout) — granularity scales correctly with complexity, not just plan count.
- **HUMAN-UAT bundled into milestone close (lesson from v2.0 carried forward)** — Instead of stacking 6 deferred items waiting on a single push, ran the Phase 10 walkthrough live during the milestone-close session itself (`10-UAT.md`, 6/6 passed). Phase 9's HUMAN-UAT was indirectly verified in the same browser session. The v2.0 lesson #3 ("bundle deploy-and-verify into milestone close") was applied and worked.
- **`/gsd-debug` for the rotation bug** — The EXIF AutoOrient regression was caught and fixed end-to-end inside the milestone-close conversation: scoped via exiftool audit (4 gallery + 2 about photos affected), routed through `/gsd-debug` for systematic verification (template grep, generated artifact inspection, CSS rule-out), fix applied across all 8 `.Process` sites, verified by axis-swap on regenerated thumbs. Single session, zero scope creep.
- **TOML pre-flight validation before push** — When the user added captions with build-breaking errors (leading frontmatter space, missing `=`, missing close-quote, duplicate weight), running `python3 -c "import toml; ..."` caught all of them locally before the GitHub Actions build had a chance to fail. Cheap defensive check; saved a red CI run.

### What Was Inefficient

- **REQUIREMENTS.md traceability drift recurred** — v2.0 lesson #2 ("update traceability at phase-transition time") did NOT carry forward into v3.0. All 9 GALLERY requirements stayed `[ ]` unchecked through Phase 10 close, only ticked during the milestone-close session. **Lesson:** lessons in RETROSPECTIVE.md don't enforce themselves — need a hook or CI gate to mechanize this, not just a written reminder.
- **Pushed `index.md` resource entry without committing the photo file** (`70c8a14`) — Treated `git add content/gallery/index.md` as the whole change when the new `IMG_8985.jpg` resource entry referenced an untracked file. Required a corrective second push (`2ad44be`). **Lesson:** when adding a `[[resources]]` entry, check that the referenced file is tracked in the same commit. A `git status --short` glance before `git push` would have caught it.
- **Source-side EXIF scrub policy not auto-enforced for new photos** — When the user added `IMG_8985.jpg`, it shipped with GPS coordinates (Lofoten location), Make, Model — exactly the fields the v2.0 source-side scrub policy gates against. The CI gate would have caught it on push, but manual `exiftool -GPSLatitude= ... -overwrite_original` was needed to clean it. **Lesson:** the project needs a `scripts/scrub_photo.py` or pre-commit hook so the source-side invariant doesn't depend on author memory.
- **Hugo `image.Process` EXIF Orientation gotcha was not in PITFALLS.md** — The `images.AutoOrient` requirement isn't documented anywhere in the v2.0 research or v3.0 PATTERNS.md, so 6 photos shipped rotated and the bug wasn't surfaced until post-deploy. **Lesson:** add to project pitfalls; any future `.Process` call should automatically chain `AutoOrient`.

### Patterns Established

- **Page-scoped vanilla-JS IIFE for feature behavior** — `lightbox.js` follows D-14/D-15 (page-scoped to avoid global pollution); pattern complements the Phase 4 inline `<head>` IIFE pattern. Two layers: head IIFE for no-FOUC critical-path sync, end-of-body or static-asset IIFE for feature behavior. Reusable for any future page-specific JS.
- **Native `<dialog>` instead of npm modal libraries** — `showModal()` ships focus-trap, scrim, and Escape-to-close for free. Saved Phase 10 from a focus-trap/aria-modal NPM dependency. Pattern: prefer platform primitives over libraries; the trade is "type a few more lines" vs "ship 12 KB of JS + a maintenance liability."
- **Author-controlled deterministic ordering via frontmatter `weight`** — `params.weight` in `[[resources]]` blocks beats both `collections.Shuffle` (non-deterministic per Hugo issue #5641) and client-side random (CLS + deep-link instability). Reusable for any list-of-things page where author intent matters.
- **`images.AutoOrient` filter must be chained before every `.Process` call** — Hugo's `image.Process` strips EXIF metadata in output (good for privacy), but does NOT auto-rotate pixel data based on the source's Orientation tag. Any source with Rotate-90 / Rotate-180 / Rotate-270 EXIF will render wrong without `AutoOrient`. New invariant: every `.Process` call gets `<resource>.Filter (images.AutoOrient)` first.

### Key Lessons

1. **Lessons in RETROSPECTIVE.md need mechanisms, not just text.** v2.0 lesson #2 (REQUIREMENTS.md traceability) was repeated almost verbatim in v3.0. Written lessons that depend on developer memory will drift; either add a `/gsd-execute-phase` exit gate that asks "tick the requirements?" or accept that traceability-at-close is the realistic pattern and stop writing the lesson.
2. **When adding a referenced asset, commit the asset and the reference together.** v3.0 example: pushed `index.md` resource entry, asset file untracked. The fix is procedural — `git status --short` between `git add` and `git push`.
3. **`/gsd-debug` works well as a milestone-close repair tool.** The AutoOrient fix was a real bug discovered post-execution; running it through `/gsd-debug` (rather than monkey-patching) produced a debug artifact (`gallery-exif-rotation.md`) that documents the discovery + fix and is searchable later. Worth defaulting to `/gsd-debug` for any regression caught at close.
4. **Bundle deploy-and-verify into milestone close — confirmed pattern.** v2.0 lesson #3 carried forward and worked. UAT 6/6 passed live during the same close session that reorganized ROADMAP.md. Net result: zero deferred items at close (vs 6 at v2.0 close).
5. **Document the gotchas at the framework boundary.** Hugo's `image.Process`-strips-EXIF-without-rotating is the kind of subtle behavior that pre-existing PITFALLS would have prevented. The cost of writing it down is one paragraph; the cost of not writing it down was a deploy with 6 visibly-broken photos.

### Cost Observations

- Sessions: 4-day window with one extended milestone-close session that bundled UAT walkthrough + EXIF rotation fix + caption authoring + spelling pass + final close.
- Model: Opus 4.7 (1M context) for the close session; profile = quality.
- Notable: the milestone-close session itself was high-leverage — three commits of real product work (rotation fix, captions, new photo) landed in the same conversation as milestone bookkeeping. Combining them in one session avoided context-loading cost.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Process Change |
|-----------|--------|-------|--------------------|
| v1.0 | 2 | 3 | Initial milestone; targeted refinement scope |
| v2.0 | 6 | 19 | Decimal-phase insertion (05.1); source-side EXIF scrub pattern; render-image hook |
| v3.0 | 3 | 8 | HUMAN-UAT bundled into milestone close (zero deferred); `/gsd-debug` for repair-at-close; page-scoped JS IIFE pattern (D-14/D-15) |

### Cumulative Quality

| Milestone | Code LOC Added | Privacy Gates | Accessibility Gates |
|-----------|----------------|---------------|---------------------|
| v1.0 | (not measured) | — | — |
| v2.0 | +1,173 (49 files) | EXIF scrub (Phases 6 + 7); zero GPS/Make/Model/Serial in published output | `aria-pressed`, `prefers-reduced-motion`, `color-scheme`, `theme-color` meta (Phase 4) |
| v3.0 | (~500 estimated) | EXIF scrub CI gate added to deploy.yml (Phase 10); source-side scrub for new photo (manual) | Native `<dialog>` focus-trap; action-oriented `aria-label`; 44×44 hit target (WCAG 2.5.5); reduced-motion-gated transitions; keyboard nav (Esc/←/→) |

### Top Lessons (Cross-Milestone)

1. **Reconcile traceability at phase-transition time** — flagged at v2.0 close, *recurred at v3.0 close*. Written reminders don't enforce themselves; needs a `/gsd-execute-phase` exit gate or a CI-style check that surfaces unticked requirements before milestone close. Two strikes.
2. **Source-side privacy hardening structurally beats build-time scrubbing** — validated on Phases 6 + 7 + the v3.0 CI gate; for new-photo authoring (v3.0 caption session), the source-side step depended on author memory and the v3.0 CI gate caught what would have leaked. Recommend scripting the photo-arrival scrub.
3. **Decimal-phase insertion preserves history honesty** — validated once on 05.1; v3.0 didn't need it (no shipped phases revealed wrong direction). Pattern available when needed.
4. **Bundle deploy-and-verify into milestone close** — flagged at v2.0 close, *applied successfully at v3.0 close*. Net change: 0 deferred items vs 6. Pattern works.
5. **Document framework gotchas in PITFALLS.md before shipping** — v3.0 lesson: Hugo `image.Process` doesn't auto-rotate; absent doc, 6 photos shipped rotated. Cost of writing it down: one paragraph; cost of not: a deploy with visible regression. Cheap insurance.

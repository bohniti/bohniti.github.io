---
phase: 07-about-enrichment
plan: 01
subsystem: hugo-templates
tags: [hugo, render-hooks, leaf-bundle, image-processing, markdown, page-bundles]

# Dependency graph
requires:
  - phase: 06-gallery
    provides: body-class hook in baseof.html (line 26), leaf-bundle pattern, page-bundle resource convention, EXIF dual-defense, hugo.toml unsafe markdown setting
provides:
  - Hugo render-image hook at themes/minimal/layouts/_default/_markup/render-image.html (site-wide markdown image processing with title-keyword switch)
  - About leaf bundle scaffold at content/about/index.md with three locked raw-HTML class wrappers (about-hero, about-pullquote, about-grid)
  - Page-bundle resource directory at content/about/images/ (tracked via .gitkeep; photos arrive in Plan 07-03)
  - Title-keyword convention for markdown image sizing hints ("hero" → 480x600 q80, "grid" → 400x300 q75, default → 800x600 q78)
  - Defensive fallback arm in render-image hook for non-bundle/external image refs (protects existing blog posts)
affects: [07-02-css, 07-03-photos, 07-04-cutover, future blog posts using bundle images, future image-heavy leaf bundles]

# Tech tracking
tech-stack:
  added:
    - Hugo render-image hook (Markdown render hook, build-time)
  patterns:
    - "Title-attribute as image sizing classifier: ![alt](src \"hero\") parsed in render-hook .Title accessor"
    - "Defensive resource lookup with passthrough fallback for legacy/external image refs"
    - "Whitespace-trimmed Go templates ({{- }}) to avoid stray text nodes inside CSS Grid layouts"
    - "Goldmark blank-line discipline around raw-HTML wrappers to keep inner markdown rendering"

key-files:
  created:
    - themes/minimal/layouts/_default/_markup/render-image.html
    - content/about/index.md
    - content/about/images/.gitkeep
  modified: []

key-decisions:
  - "Used cooking.JPG (uppercase extension) in markdown ref to match the actual filesystem case — Hugo's .Page.Resources.GetMatch is case-sensitive on the filesystem, lowercase ref would force the defensive fallback arm and lose CLS-clean width/height + WebP processing"
  - "Did not delete content/about.md per D-01 order-of-operations — deletion is reserved for Plan 07-04 after end-to-end verification; transient duplicate-output Hugo warning during Plans 07-01..07-03 is acceptable"
  - "Created .gitkeep even though photos already exist on disk — satisfies plan's verify check, harmless when photos coexist, and makes the directory's intent explicit until 07-03 commits the photos"
  - "Did not commit the 5 photo files (climbing.jpg, cooking.JPG, cycling.jpg, portrait.jpg, running.jpg) — plan ownership is 07-03 (after EXIF scrub per D-17). Photos remain untracked in working tree at end of 07-01"

patterns-established:
  - "Render-image hook three-arm switch: future image keywords (e.g., 'banner', 'thumb') extend additively in render-image.html only; no content-file changes required"
  - "Page-bundle resource directory tracked via .gitkeep before photos arrive — same pattern usable for any image-heavy leaf bundle that splits scaffolding and asset arrival across plans"

requirements-completed: [ABOUT-01, ABOUT-02]

# Metrics
duration: ~6 min
completed: 2026-04-30
---

# Phase 7 Plan 1: About Enrichment — Hook + Bundle Scaffold Summary

**Hugo render-image hook with hero/grid/default title-keyword switch (480x600 q80 / 400x300 q75 / 800x600 q78) plus About leaf bundle (`content/about/index.md`) with three locked raw-HTML class wrappers and verbatim copy preservation.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-04-30T14:26:13Z (approx — plan execution begin)
- **Completed:** 2026-04-30T14:32:13Z
- **Tasks:** 2
- **Files created:** 3
- **Files modified:** 0

## Accomplishments

- Landed the Hugo render-image hook deferred from Phase 6: site-wide markdown image references are now auto-processed to WebP `<img>` tags with explicit `width`/`height` (CLS-clean), `loading="lazy"|"eager"`, `decoding="async"`, and `fetchpriority="high"` on the hero arm
- Title-keyword convention (`"hero"` / `"grid"` / default) is now a usable codebase pattern; future image-heavy bundles consume it by writing plain markdown image refs with the third-tuple title literal
- Defensive fallback arm guards existing blog posts (e.g., `content/blog/2026-03-05-climbing-routes/`) from any breakage when the global hook becomes active — out-of-bundle and percent-encoded refs render via passthrough `<img>` with `safeURL`
- About leaf bundle scaffolded with verbatim prose preservation (D-23): hero wrapper around intro + CV link + portrait, pullquote callout after Erste Group bullets, 4-image grid at end of Interests
- Body-class scoping (`body.page-about`) materializes automatically because Phase 6's `baseof.html` line 26 hook is already live — zero template churn required for Phase 7

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the Hugo render-image hook** — `efeaa88` (feat)
2. **Task 2: Create the About leaf bundle + .gitkeep** — `9afe6b4` (feat)

_Plan-metadata commit (SUMMARY.md + STATE.md + ROADMAP.md) follows this summary._

## Files Created/Modified

### Created

- **`themes/minimal/layouts/_default/_markup/render-image.html`** — 21-line Hugo render-image hook. Resolves bundle-relative paths via `.Page.Resources.GetMatch`, three-arm switch on `.Title` keyword (hero/grid/default), emits explicit `width`/`height` from processed dimensions, per-arm class + loading + fetchpriority attributes, defensive passthrough fallback with `safeURL` for non-bundle resources.
- **`content/about/index.md`** — 77-line leaf-bundle index. Front matter title-only (`title: "About"`). Three structural raw-HTML wrappers added per D-08, D-11, D-13: `<div class="about-hero">` containing `.about-hero-text` + `.about-hero-photo` halves with the portrait image ref, `<aside class="about-pullquote">` after Erste Group bullets with the 40% → 95% metric, `<div class="about-grid">` at end of Interests with 4 grid-tagged image refs (climbing, cycling, running, cooking).
- **`content/about/images/.gitkeep`** — empty file so git tracks the page-bundle resource directory until Plan 07-03 commits the 5 EXIF-scrubbed photos.

### NOT Modified (READ-ONLY for this plan, by design)

- `themes/minimal/layouts/_default/baseof.html` — body-class hook on line 26 from Phase 6 covers Phase 7's needs
- `themes/minimal/layouts/_default/single.html` — renders About via fallback layout chain
- `hugo.toml` — `[markup.goldmark.renderer.unsafe = true]` already enables raw HTML in markdown; `[imaging.exif] disableLatLong = true` already in place; About menu entry at `weight = 3` already correct
- `themes/minimal/static/css/style.css` — Plan 07-02 owns the `/* === About === */` rule family
- `content/about.md` — Plan 07-04 deletes after end-to-end verification (D-01 order-of-operations)

### NOT Committed (deferred to Plan 07-03)

- `content/about/images/portrait.jpg`, `climbing.jpg`, `cycling.jpg`, `running.jpg`, `cooking.JPG` — present in working tree (user pre-placed) but untracked. Plan 07-03 owns EXIF scrubbing (D-17) and committing.

## Verbatim Hook Source (D-19, copied verbatim)

```go-html-template
{{- $resource := .Page.Resources.GetMatch (printf "%s" .Destination) -}}
{{- if $resource -}}
  {{- $title := .Title | default "" -}}
  {{- $isHero := eq $title "hero" -}}
  {{- $isGrid := eq $title "grid" -}}
  {{- $processed := "" -}}
  {{- if $isHero -}}
    {{- $processed = $resource.Process "fill 480x600 Smart webp q80" -}}
  {{- else if $isGrid -}}
    {{- $processed = $resource.Process "fill 400x300 Smart webp q75" -}}
  {{- else -}}
    {{- $processed = $resource.Process "fill 800x600 Smart webp q78" -}}
  {{- end -}}
  <img src="{{ $processed.RelPermalink }}"
       width="{{ $processed.Width }}"
       height="{{ $processed.Height }}"
       alt="{{ .Text }}"
       {{- if $isHero }} class="about-hero-img" loading="eager" fetchpriority="high"{{ else if $isGrid }} class="about-grid-item" loading="lazy" decoding="async"{{ else }} loading="lazy" decoding="async"{{ end -}}>
{{- else -}}
  <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}"{{ with .Title }} title="{{ . }}"{{ end }}>
{{- end -}}
```

## Structural Diff: `content/about.md` → `content/about/index.md`

Verbatim prose preservation (D-23) — only structural additions, zero rewordings:

1. **Hero wrapper** (D-08): wrapped the opening (Hi heading + 2 narrative paragraphs + CV link) in
   ```html
   <div class="about-hero">
     <div class="about-hero-text"> … intro markdown … </div>
     <div class="about-hero-photo"> ![Portrait of Timo](images/portrait.jpg "hero") </div>
   </div>
   ```
   Goldmark blank-lines around inner markdown blocks ensure the parser re-enters markdown mode.

2. **Pullquote** (D-11): inserted after the Erste Group bullet list (before the Accenture block):
   ```html
   <aside class="about-pullquote">
   Improved message routing accuracy from <strong>40% → 95%</strong>
   </aside>
   ```

3. **Grid** (D-13): appended at the very end of the file (after the Interests paragraph):
   ```html
   <div class="about-grid">
   ![Bouldering at the climbing gym](images/climbing.jpg "grid")
   ![Cycling in the Alps](images/cycling.jpg "grid")
   ![Trail running](images/running.jpg "grid")
   ![Cooking](images/cooking.JPG "grid")
   </div>
   ```
   Note: `cooking.JPG` (uppercase) used to match filesystem case — see deviation below.

4. **Front matter unchanged** (D-02): `title: "About"` only — no date/draft/summary/description added.

## Decisions Made

- **cooking.JPG case correction:** Used uppercase `JPG` extension in markdown image ref to match the actual filename on disk. Hugo's `.Page.Resources.GetMatch` is case-sensitive at the filesystem level; the plan's literal lowercase `cooking.jpg` would have caused the hook to hit the defensive fallback arm — emitting a passthrough `<img src="images/cooking.JPG">` (which would resolve at runtime on case-insensitive macOS file URLs but break on case-sensitive Linux GitHub Pages serving), losing WebP processing, explicit width/height, and the `about-grid-item` class. Per orchestrator critical constraint #6.
- **Created `.gitkeep` despite photos existing:** Plan's frontmatter and verify check both expect `content/about/images/.gitkeep`. Created as zero-byte file to satisfy verify; harmless when photos coexist (plan acknowledges this in Task 2 action: "harmless either way"). Plan 07-03 may delete or leave it.
- **Did not commit photos:** They are placed by the user in the working tree but ownership is Plan 07-03 (after EXIF scrub per D-17). Staged only `content/about/index.md` and `content/about/images/.gitkeep` to keep this plan's commit boundary clean.
- **Did not delete `content/about.md`:** D-01 reserves deletion for Plan 07-04. Transient duplicate-output Hugo warning is acceptable for the verification window.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Cooking image filename case correction**
- **Found during:** Task 2 (About leaf bundle creation)
- **Issue:** Plan literal specified `![Cooking](images/cooking.jpg "grid")` (lowercase `.jpg`) but the actual file on disk is `content/about/images/cooking.JPG` (uppercase `.JPG`). Hugo's `.Page.Resources.GetMatch` is case-sensitive on the filesystem (verified by RESEARCH.md item 5 cross-reference and Hugo docs), so the lowercase ref would resolve to nil and force the hook into the defensive passthrough fallback arm — emitting `<img src="images/cooking.jpg">` (unprocessed, no width/height, no `about-grid-item` class) which violates ABOUT-03 (CLS guarantee) and would 404 on case-sensitive filesystems (Linux GitHub Pages runners).
- **Fix:** Used `images/cooking.JPG` (uppercase extension) in the markdown image reference to match the actual filename. All other photo references (`portrait.jpg`, `climbing.jpg`, `cycling.jpg`, `running.jpg`) already use lowercase that matches their filesystem case.
- **Files modified:** `content/about/index.md`
- **Verification:** Manual `grep -cF '![Cooking](images/cooking.JPG "grid")' content/about/index.md` returns 1; `ls content/about/images/cooking.JPG` exists; `.Page.Resources.GetMatch "images/cooking.JPG"` will resolve at build time to the real resource and the hero/grid arm will fire.
- **Committed in:** `9afe6b4` (Task 2 commit)
- **Plan-side note for downstream:** Plan 07-03 should normalize filenames to lowercase during the EXIF-scrub commit (`mv cooking.JPG cooking.jpg` or equivalent) and update the markdown ref to lowercase to match. If Plan 07-03 normalizes, this deviation is reverted there.

---

**Total deviations:** 1 auto-fixed (1 bug — case-sensitivity mismatch between plan literal and filesystem)
**Impact on plan:** Single-character correction on a single line. No scope creep, no architectural change. Preserves the plan's intent (hero/grid hook arms fire on every photo) while preventing a CLS regression on Linux deploy.

## Issues Encountered

- None — both tasks executed cleanly. The `_markup/` subdirectory under `themes/minimal/layouts/_default/` did not previously exist; created it with `mkdir -p` before writing the hook file.

## Threat Flags

None. The render-image hook is build-time only and does not introduce new network endpoints, auth paths, file-access patterns, or schema changes. The leaf bundle is static markdown. The page-bundle resource directory is gitignored from build outputs (`public/`, `resources/`).

## Known Stubs

None. The leaf bundle markdown references 5 image filenames; those photos exist on disk in the working tree (untracked). At Hugo build time after this plan's commits land:
- If photos remain untracked locally, `hugo --minify` will resolve them via `.Page.Resources.GetMatch` (Hugo treats files in the bundle directory as resources regardless of git tracking) and the hook's hero/grid arms will fire correctly.
- On a fresh clone of `main` HEAD (without the user's untracked photos), the hook will fall through to the defensive fallback arm and emit passthrough `<img>` tags. This is the intentional "won't render correctly until 07-03 lands" state described in the plan's `<verification>` block.
- Plan 07-03 commits the photos and closes this gap.

## User Setup Required

None for this plan. Plan 07-03 will require the user to confirm photo selections before EXIF scrubbing and commit (per D-16 HUMAN-UAT blocker).

## Next Plan Readiness

- **Plan 07-02 (CSS):** Can land in parallel with this plan since it only edits `themes/minimal/static/css/style.css`. The body-class scoping (`body.page-about`) target exists as soon as Hugo builds with the new leaf bundle.
- **Plan 07-03 (photos):** Source photos already pre-placed by the user in `content/about/images/`. Plan 07-03 owns EXIF scrubbing (D-17 recipe) and commit. Recommend Plan 07-03 normalize `cooking.JPG` → `cooking.jpg` filename and update the markdown ref to match (reverts this plan's case-correction deviation).
- **Plan 07-04 (cutover):** Deletes `content/about.md`, runs cold-build smoke + EXIF + theme-parity + blog-post-regression gates (D-25..D-30).

## Self-Check: PASSED

Verified:
- `themes/minimal/layouts/_default/_markup/render-image.html` exists ✓
- `content/about/index.md` exists ✓
- `content/about/images/.gitkeep` exists ✓
- Commit `efeaa88` (Task 1) found in git log ✓
- Commit `9afe6b4` (Task 2) found in git log ✓
- All 10 Task 1 acceptance criteria pass ✓
- All Task 2 acceptance criteria pass (with case-corrected cooking ref) ✓
- `content/about.md` still exists (deletion deferred to 07-04) ✓

---
*Phase: 07-about-enrichment*
*Completed: 2026-04-30*

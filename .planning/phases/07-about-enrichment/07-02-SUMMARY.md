---
phase: 07-about-enrichment
plan: 02
subsystem: theme-css
tags: [css, flexoki, responsive, body-class-scoping, wcag, hugo-page-type]

# Dependency graph
requires:
  - phase: 06-gallery
    provides: body-class hook in baseof.html line 26 (`<body class="page-{{ .Type | default "default" }}">`), Flexoki light + dark palette tokens (--text, --accent, --bg-secondary), section-comment CSS convention
  - phase: 07-about-enrichment
    plan: 01
    provides: About leaf bundle at content/about/index.md with class-hook DOM (.about-hero, .about-pullquote, .about-grid wrappers + render-image-hook-emitted .about-hero-img / .about-grid-item classes)
provides:
  - "/* === About === */ CSS rule family in themes/minimal/static/css/style.css scoped via body.page-about (hero CSS Grid 2fr/1fr, pullquote left-bar + bg-secondary fill, 2-col grid)"
  - mobile overrides for .about-hero (1-col stack) and .about-grid (1-col) appended into the existing @media (max-width: 600px) block — single cascade-coherent media query
  - explicit type: "about" front matter on content/about/index.md so Hugo derives Type = "about" → body.page-about CSS rules actually match the rendered DOM
  - WCAG AA-large compliance comment on .about-pullquote strong (RESEARCH amendment 2 — dark-theme contrast 3.97:1 documented as load-bearing, future-proofing)
  - margin: 0 reset on .about-grid img (RESEARCH amendment 1 — neutralizes inherited .page-content img { margin: 1.5rem 0 } cascade)
affects: [07-03-photos, 07-04-cutover, future themes that touch the About page or generalize the pullquote pattern]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dual-selector pattern for image classes: `body.page-about .about-hero-photo img, body.page-about .about-hero-img` covers both wrapper-div+markdown and render-image-hook-emitted class paths"
    - "Mobile breakpoint discipline: append into existing @media block, never create a parallel breakpoint block"
    - "Explicit type: front matter on top-level Hugo leaf bundles to force Type derivation when body-class scoping depends on it (Hugo 0.161 does NOT auto-derive Type for top-level page bundles)"

key-files:
  created:
    - .planning/phases/07-about-enrichment/07-02-SUMMARY.md
  modified:
    - themes/minimal/static/css/style.css
    - content/about/index.md

key-decisions:
  - "Used the plan's literal CSS verbatim (including `color: var(--text);` on .about-pullquote and dual selectors with .about-hero-img / .about-grid-item) rather than the orchestrator's slightly trimmed paraphrase — the plan-literal version is more defensive (covers both DOM rendering paths) and the executor's job is to follow the plan, not to second-guess its rule list"
  - "Discovered + auto-fixed (Rule 2): plan + 07-CONTEXT D-04 both claim Hugo auto-derives `Type = 'about'` from the leaf-bundle directory; in fact Hugo 0.161 defaults `Type = 'page'` for top-level leaf bundles without explicit `type:` front matter. Without the fix, 100% of the new CSS would be dead code (rendered body had `class=page-page`). One-line `type: \"about\"` front-matter addition mirrors content/gallery/index.md (Phase 6, working in production)."
  - "Did NOT introduce a `layouts/about/single.html` shim despite it being an alternative way to make Hugo derive Type — D-03 explicitly forbids new layout files, and the front-matter fix is strictly less surface area"
  - "Ran a cold Hugo build locally (`rm -rf resources public && hugo --minify`) twice during execution to verify (a) the new CSS lands without breaking the existing build and (b) the type fix actually produces `<body class=page-about>` on the rendered HTML — Plan 07-04 owns the formal cold-build gate, but a sanity check during 07-02 caught the body-class issue early"

patterns-established:
  - "CSS rules that depend on body-class scoping (e.g., body.page-{type}) require BOTH the baseof.html hook AND an explicit type: front-matter line on top-level leaf bundles. The hook alone does not suffice for non-section pages."
  - "When a plan's must_haves.truths reference a rendered DOM property (e.g., `body.page-about selector matches body class derived from .Type='about'`), verify the property holds on the rendered HTML, not just on the source code — the plan can be code-correct yet runtime-wrong"

requirements-completed: [ABOUT-02]

# Metrics
duration: ~4 min
completed: 2026-05-01
---

# Phase 7 Plan 2: About Enrichment — CSS rule family Summary

**Append `/* === About === */` rule family (hero 2fr/1fr CSS Grid + pullquote + 2-col image grid) to style.css scoped via `body.page-about`, plus mobile overrides into the existing `@media (max-width: 600px)` block. Discovered during execution that Hugo 0.161 doesn't auto-derive `Type = "about"` for top-level leaf bundles — added explicit `type: "about"` to content/about/index.md so the body-class hook actually resolves and the new CSS rules apply at runtime.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-01T07:29:49Z
- **Completed:** 2026-05-01T07:33:49Z
- **Tasks:** 2 (plus 1 deviation fix discovered during execution)
- **Files created:** 0 (1 SUMMARY.md, but that's tooling output not feature work)
- **Files modified:** 2 (themes/minimal/static/css/style.css, content/about/index.md)

## Accomplishments

- Landed the full `/* === About === */` rule family in `style.css` between the existing `/* === Gallery === */` and `/* === Footer === */` sections, occupying lines 306–358:
  - `.about-hero`: CSS Grid 2fr/1fr, 2rem gap, `align-items: start`, 2.5rem bottom margin
  - `.about-hero-photo img, .about-hero-img`: width 100%, height auto, 6px border-radius, display block (dual selector covers both DOM rendering paths — wrapper-div+markdown OR render-image-hook-emitted class)
  - `.about-pullquote`: 1.4rem/500-weight text, left-bar accent (4px solid var(--accent)), bg-secondary fill, 1.75rem vertical margin, asymmetric border-radius (0 on left side to flush with the bar)
  - `.about-pullquote strong`: var(--accent) emphasis at 700 weight, **preceded by a 3-line code comment documenting WCAG AA-large compliance** (dark-theme #D14D41 on #1C1B1A is 3.97:1 — passes WCAG only because the inherited 1.4rem + 500-weight qualifies as "large text"; lowering either invalidates the contrast — RESEARCH amendment 2)
  - `.about-grid`: 2-col fixed (`repeat(2, 1fr)`), 0.75rem gap, top margin only
  - `.about-grid img, .about-grid-item`: width 100%, 4px border-radius, **`margin: 0` to neutralize inherited `.page-content img { margin: 1.5rem 0 }` cascade** (RESEARCH amendment 1)
- Appended mobile overrides for `.about-hero` (single-column 1.5rem gap) and `.about-grid` (single-column) **into the existing `@media (max-width: 600px)` block at lines 403–408** — not a separate media query, so the cascade stays coherent
- Discovered and auto-fixed a critical runtime bug: Hugo 0.161 does NOT derive `Type = "about"` from the leaf-bundle directory name alone — `content/about/index.md` needs explicit `type: "about"` in front matter for the body-class hook on `baseof.html` line 26 to render `<body class="page-about">`. Without this, every `body.page-about` selector in the new CSS would have been dead code. Mirror of how Phase 6's `content/gallery/index.md` handled the same issue (it set `type: "gallery"` explicitly).
- Cold-build verification passes: `rm -rf resources public && hugo --minify` builds 16 pages with 46 processed images, no errors. `<body class="page-about">` confirmed on rendered `/about/index.html`. Other pages (home, gallery, blog) retain their existing body classes — no regression.

## Task Commits

Each task committed atomically:

1. **Task 1: Insert `/* === About === */` section between Gallery and Footer** — `fc6b2fa` (feat) — 53 lines added to style.css
2. **Task 2: Append About mobile overrides into the existing @media (max-width: 600px) block** — `b98807e` (feat) — 7 lines added to style.css
3. **Deviation fix: Set `type: "about"` on About leaf bundle so body.page-about resolves** — `69232ef` (fix) — 1 line added to content/about/index.md

_Plan-metadata commit (this SUMMARY.md + STATE.md + ROADMAP.md updates) follows._

## Files Created/Modified

### Modified

- **`themes/minimal/static/css/style.css`** (350 → 410 lines, +60 net)
  - Inserted `/* === About === */` block at lines 306–358 (between Gallery section ending at line 305 and Footer section starting at line 359)
  - Appended 6 lines (mobile rules + closing brace alignment) inside the `@media (max-width: 600px)` block at lines 403–408
  - Zero edits outside these two specific insertion points; existing rules byte-for-byte preserved
- **`content/about/index.md`** (+1 line in front matter)
  - Added `type: "about"` between the existing `title:` line and the closing `---`
  - Front matter now: `title: "About"` + `type: "about"` (was: title-only per Plan 07-01 D-02)
  - This is a deviation-fix change; rationale below in "Deviations from Plan"

### NOT Modified (READ-ONLY for this plan, by design)

- `themes/minimal/layouts/_default/baseof.html` — body-class hook on line 26 unchanged
- `themes/minimal/layouts/_default/single.html` — fallback layout unchanged
- `themes/minimal/layouts/_default/_markup/render-image.html` — Plan 07-01's hook unchanged
- Any layout file under `themes/minimal/layouts/about/` — D-03 forbids creating one; the deviation fix uses front matter instead, preserving D-03
- `hugo.toml` — no config changes needed
- `content/about.md` — Plan 07-04 owns deletion (D-30, D-01 order-of-operations)
- All 5 photo files in `content/about/images/` — Plan 07-03 owns EXIF scrub + commit

## Verbatim CSS Inserted (Tasks 1 + 2)

### Task 1 — `/* === About === */` section (53 lines, inserted between Gallery and Footer)

```css
/* === About === */
body.page-about .about-hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: start;
  margin-bottom: 2.5rem;
}

body.page-about .about-hero-photo img,
body.page-about .about-hero-img {
  width: 100%;
  height: auto;
  border-radius: 6px;
  display: block;
}

body.page-about .about-pullquote {
  font-size: 1.4rem;
  font-weight: 500;
  line-height: 1.4;
  color: var(--text);
  border-left: 4px solid var(--accent);
  padding: 0.5rem 0 0.5rem 1.25rem;
  margin: 1.75rem 0;
  background: var(--bg-secondary);
  border-radius: 0 4px 4px 0;
}

/* Dark-mode #D14D41 on #1C1B1A measures 3.97:1 — passes WCAG AA only because the
   inherited 1.4rem + font-weight:700 qualifies as "large text" (≥14pt bold).
   Do not reduce font-size or font-weight here without re-checking contrast. */
body.page-about .about-pullquote strong {
  color: var(--accent);
  font-weight: 700;
}

body.page-about .about-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin: 1.5rem 0 0;
}

body.page-about .about-grid img,
body.page-about .about-grid-item {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
  margin: 0; /* override .page-content img { margin: 1.5rem 0 } cascade — RESEARCH amendment 1 */
}
```

### Task 2 — Mobile overrides (6 lines, appended inside existing @media block)

```css
  body.page-about .about-hero {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  body.page-about .about-grid {
    grid-template-columns: 1fr;
  }
```

## Specificity Reasoning (dual-selector pattern)

The plan uses two-arm selectors to cover the full DOM rendering path:

| Selector | Specificity | Wins over `.page-content img` (0,1,1=11)? |
|----------|-------------|-------------------------------------------|
| `body.page-about .about-hero-photo img` | (0,2,2)=22 | yes |
| `body.page-about .about-hero-img` | (0,2,1)=21 | yes |
| `body.page-about .about-grid img` | (0,2,1)=21 | yes |
| `body.page-about .about-grid-item` | (0,2,1)=21 | yes |

The hero photo lives inside `<div class="about-hero-photo">` per content/about/index.md; the render-image hook emits `<img class="about-hero-img">` per render-image.html. Both selectors fire on that DOM, the cascade picks the last winning declaration order — which is fine because the rule body is identical for the union. Same shape for grid items.

The grid-img rule's `margin: 0` is the **only** declaration that overrides `.page-content img { margin: 1.5rem 0 }`. Without it, the inherited 1.5rem margin would inject vertical gaps between rows of the 2-col grid, breaking the tight visual rhythm. Specificity alone (21 > 11) is necessary but not sufficient — the explicit reset must be in the rule body. RESEARCH amendment 1 caught this; the plan baked it in; this plan executed it verbatim.

## Decisions Made

- **Adopted plan-literal CSS verbatim**, including the `color: var(--text);` declaration on `.about-pullquote` and the dual selectors (`.about-hero-photo img, .about-hero-img` and `.about-grid img, .about-grid-item`). The orchestrator prompt's "critical constraints" #4 listed a slightly trimmed paraphrase of the rule list (without `color: var(--text);` or the dual selectors); the plan-literal version is more defensive and is what the plan's `<action>` block specifies. Executor follows the plan, not the orchestrator paraphrase, when they diverge.
- **Did not delete `content/about.md`** — D-01 / D-30 reserve deletion for Plan 07-04 after end-to-end verification. The transient duplicate-output Hugo behavior is acceptable through 07-03.
- **Did not commit photos in `content/about/images/`** — those remain untracked; Plan 07-03 owns EXIF scrub + commit.
- **Did NOT introduce a `layouts/about/single.html` shim** as an alternative way to fix the Type derivation. D-03 explicitly forbids new layout files; front-matter `type: "about"` is strictly less surface area and matches Phase 6's gallery solution.
- **Ran a cold Hugo build** locally (Hugo Extended 0.161.1 is installed via Homebrew, contrary to CLAUDE.md's "Hugo NOT installed locally" note — the user upgraded). Used the build to verify the type fix resolved the body-class issue. Plan 07-04 owns the formal cold-build gate; this was a sanity check, not the gate itself.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — Critical missing functionality] Set `type: "about"` on the About leaf bundle so Hugo's body-class hook resolves**

- **Found during:** Post-Task-2 sanity smoke (cold Hugo build + grep for `<body class=page-about>` in rendered `/about/index.html`)
- **Issue:** Plan 07-02 `must_haves.truths` and `key_links.via` both assert: "body.page-about selector matches body class derived from .Type='about'". 07-CONTEXT.md D-04 says: "Hugo derives Type = 'about' automatically from the leaf-bundle directory name, so the body class becomes page-about once the bundle exists. No baseof.html edit required for Phase 7." 07-CONTEXT.md "Hugo-Specific Notes" reaffirms the same. Plan 07-01-SUMMARY.md likewise relies on `Type='about'` materializing automatically.

  **The assertion is wrong on Hugo 0.161.** Top-level leaf bundles (`content/{slug}/index.md`) do NOT auto-derive `Type = "{slug}"`. They default to `Type = "page"` unless either (a) `type:` is set in front matter, or (b) a `layouts/{slug}/` directory exists in the theme. Phase 6's gallery happens to work because `content/gallery/index.md` sets `type: "gallery"` explicitly AND has `themes/minimal/layouts/gallery/single.html`.

  Verification of the bug:
  ```
  $ grep -o '<body class=page-[a-z]*' public/about/index.html
  <body class=page-page    # ← was page-page, NOT page-about
  $ grep -o '<body class=page-[a-z]*' public/gallery/index.html
  <body class=page-gallery # ← gallery works because of explicit type: front matter
  ```

  Without this fix, every `body.page-about` selector in the new CSS would have been dead code — the rendered `<body class="page-page">` does not match `body.page-about`. Plan 07-02's stated goal ("the page-shell exists before photos and HTML wrappers do their part") would have been silently violated, and Plan 07-04's verification gates (especially D-28 theme parity, D-26 CLS — both depending on the new CSS being live) would fail.

- **Fix:** Added a single line `type: "about"` to `content/about/index.md` front matter. Front matter is now:
  ```yaml
  ---
  title: "About"
  type: "about"
  ---
  ```
  Mirrors `content/gallery/index.md` (Phase 6, working in production). One-line change, no structural impact, no new layout file (preserves D-03's "no new layout file" decision).
- **Files modified:** `content/about/index.md`
- **Verification:** `rm -rf resources public && hugo --minify` then `grep '<body class=page-about' public/about/index.html` → matches. Cross-check on other pages: home is still `page-page` (correct — home isn't a leaf bundle), gallery is still `page-gallery`, blog list is still `page-blog`. No regression.
- **Committed in:** `69232ef` (separate from Tasks 1+2 to keep the deviation discoverable in git log)
- **Why this is Rule 2, not Rule 4:** No architectural change. No new template. No library swap. No new infrastructure. It's a one-line content edit that makes the body-class hook actually resolve, which the plan and CONTEXT both already assert should "just work". The plan is code-correct but runtime-wrong; the fix makes it runtime-correct without changing scope or shape.
- **Plan-side note for downstream:** 07-CONTEXT D-04 should be amended in a future docs commit to read "set `type: \"about\"` in front matter to force Type derivation" rather than "Hugo derives Type automatically". 07-01-SUMMARY may want a similar amendment-note. Plans 07-03 and 07-04 are unaffected by this fix (they don't touch front matter and they consume the body class indirectly via the CSS).

---

**Total deviations:** 1 auto-fixed (1 critical missing functionality — the `type:` front-matter line that the plan and CONTEXT both incorrectly assumed Hugo would derive automatically).
**Impact on plan:** Single front-matter line addition; one extra commit. Plan's intent (CSS rules apply to `/about/`) is preserved; without the fix, the intent would silently fail at runtime.

## Issues Encountered

- One earlier parallel `find` command in the initial context-gathering batch errored (likely a shell quoting issue with the special-character file name `Screenshot 2026-04-29 at 14.26.43.png`), which cancelled a parallel Edit operation. Re-ran the Edit cleanly afterward; no impact on plan correctness.

## Threat Flags

None. All changes are static CSS rules + a content front-matter line. No new network endpoints, auth paths, file-access patterns, schema changes, or trust boundaries introduced. The dark-theme contrast caveat on `.about-pullquote strong` (3.97:1 — WCAG AA-large compliant only because of the parent's font size + weight) is documented in a load-bearing CSS comment so future maintainers re-check before reducing font-size or font-weight.

## Known Stubs

None. The new CSS rules apply to a fully-wired DOM (Plan 07-01 created the class hooks; Plan 07-01's render-image hook also emits the matching classes). When Plan 07-03 commits the EXIF-scrubbed photos, the rules will continue to apply with no further code changes — the visual treatment will simply have actual photos to render against instead of broken-image placeholders or fallback `<img>` tags.

## User Setup Required

None for this plan. Plan 07-03 will require the user to confirm photo selections before EXIF scrubbing (per D-16 HUMAN-UAT blocker).

## Next Plan Readiness

- **Plan 07-03 (photos):** Source photos already pre-placed by the user in `content/about/images/`. Plan 07-03 owns EXIF scrubbing (D-17 recipe) and commit. **Recommendation for 07-03:** normalize `cooking.JPG` → `cooking.jpg` filename and update the markdown ref in `content/about/index.md` to match (would revert Plan 07-01's case-correction deviation; keeps filenames lowercase per repo convention).
- **Plan 07-04 (cutover + verification):** Will exercise all 5 verification gates (D-25 URL preservation, D-26 CLS, D-27 EXIF, D-28 theme parity, D-29 blog-post regression smoke), delete `content/about.md` per D-30, and write 07-HUMAN-UAT.md. The body-class fix from this plan ensures D-28 (theme parity, light + dark) actually exercises the new CSS rather than fallback `.page-content` styles.
- **Note for 07-04:** 07-04's cold-build smoke will rebuild `resources/` and `public/` from scratch and exercise the same code path verified here. Expect identical results: 16 pages, ~46 processed images, no errors, `<body class="page-about">` on `/about/`.

## Self-Check: PASSED

Verified each claim:

- File `themes/minimal/static/css/style.css` exists and contains `/* === About === */` section ✓
  ```
  $ grep -c '/\* === About === \*/' themes/minimal/static/css/style.css → 1
  ```
- About section is positioned between Gallery and Footer ✓
  ```
  $ grep -n "=== About\|=== Footer\|=== Gallery" themes/minimal/static/css/style.css
  276:/* === Gallery === */
  306:/* === About === */
  359:/* === Footer === */
  ```
- All 12 acceptance-criteria grep checks for Task 1 pass (verified via the plan's automated verify block — `... && echo OK` returned `OK`) ✓
- Mobile overrides land inside the existing media block (verified via Python balanced-brace scan in Task 2's verify block — returned `OK`) ✓
- Total `body.page-about` occurrences in style.css: 10 (≥7 threshold from orchestrator success criteria) ✓
- File `content/about/index.md` exists and contains `type: "about"` ✓
  ```
  $ grep '^type:' content/about/index.md → type: "about"
  ```
- Commit `fc6b2fa` (Task 1) found in git log ✓
- Commit `b98807e` (Task 2) found in git log ✓
- Commit `69232ef` (Rule 2 deviation fix) found in git log ✓
- Cold Hugo build succeeds (`rm -rf resources public && hugo --minify` → 16 pages, 46 processed images, no errors, only the pre-existing `languageCode` deprecation warnings) ✓
- `<body class="page-about">` confirmed on rendered `public/about/index.html` ✓
- No file deletions in any of the 3 commits (`git diff --diff-filter=D --name-only` per commit returns empty) ✓

---
*Phase: 07-about-enrichment*
*Completed: 2026-05-01*

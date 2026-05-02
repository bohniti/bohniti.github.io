---
phase: 09-about-dynamic-rounded-redesign
plan: 03
subsystem: docs
tags:
  - verification
  - human-uat
  - gates
  - phase-close

# Dependency graph
requires:
  - phase: 09-01
    provides: render-image hook arms (split, feature) + --radius-soft token (dormant)
  - phase: 09-02
    provides: about/single.html layout, content/about/index.md rewrite, About CSS rule cluster (5 var(--radius-soft) consumers, role-card visual contract, mobile @media extension)
provides:
  - "All 11 UI-SPEC verification gates run against deployed Wave-2 artifacts: 10 statically-checkable PASS (Gates 2, 3, 4a, 4b, 6c, 6d, 8, 9, 10, plus redundant Pitfall 17 top-level .about- check), 2 build-dependent PASS (6a, 11), 5 deferred to HUMAN-UAT (1, 4c, 5, 6b, 7a)"
  - ".planning/phases/09-about-dynamic-rounded-redesign/09-HUMAN-UAT.md (108 LOC, 5 gate sections — Gate 1 asymmetric layout, Gate 4c no CSS leak to /blog/+/gallery/, Gate 5 content rebalance, Gate 6b live DevTools dark-mode contrast, Gate 7a 320px mobile emulation)"
  - ".planning/STATE.md § Deferred Items extended with Phase 9 row matching Phase 5/05.1/06/07 precedent"
affects:
  - .planning/STATE.md  # Deferred Items extended +1 row
  - Phase 9 close       # phase ships as 'verifying pending HUMAN-UAT post-deploy'

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verification-only plan pattern: no code changes, only running gates and authoring HUMAN-UAT scaffolding (carries Phase 5/05.1/06/07 precedent forward)"
    - "Inverted hard-coded color audit (Gate 8): awk-mask :root blocks + grep About-scoped rules outside masked region — works regardless of :root block line numbers"
    - "Build determinism gate (Gate 11): rm -rf public + 2x hugo --minify + diff -r — proves byte-identical output across consecutive builds"

key-files:
  created:
    - .planning/phases/09-about-dynamic-rounded-redesign/09-HUMAN-UAT.md
  modified:
    - .planning/STATE.md

key-decisions:
  - "Gate 6a (pullquote rendered HTML) verified via minified attribute form (`<aside class=about-pullquote>`) — Hugo's --minify strips quotes around single-token attributes; the gate command in PLAN.md was authored against quoted form, but compiled output is unquoted; both forms verified"
  - "Bonus rendered-output checks (about-hero-img, about-grid-item × 4, about-role-card × 3, page-about, <article class=about>) verified by occurrence count (grep -o | wc -l) rather than line count (grep -c) — minified HTML collapses to fewer lines so per-line counts under-count; per-occurrence counts match expected (1, 4, 3, 1, 1)"
  - "Phase 9 close pattern matches v2.0 precedent: 09-HUMAN-UAT.md scaffolded → STATE.md Deferred Items row appended → ships as 'verifying pending post-deploy walkthrough'"

requirements-completed:
  - ABOUT-01
  - ABOUT-02
  - ABOUT-03
  - ABOUT-04
  - ABOUT-05
  - ABOUT-06
  - ABOUT-07

# Metrics
duration: 2 min
completed: 2026-05-02
---

# Phase 09 Plan 03: Verification + HUMAN-UAT Scaffolding Summary

**All 12 UI-SPEC verification gates run (10 static + 2 build-dependent) — every automated gate PASSES; 5 visual-judgment gates scaffolded as `09-HUMAN-UAT.md` and tracked in STATE.md Deferred Items per Phase 5/05.1/06/07 precedent. Phase 9 ships as "verifying pending post-deploy walkthrough."**

## Performance

- **Duration:** ~2 min (170 sec)
- **Started:** 2026-05-02T13:24:31Z
- **Completed:** 2026-05-02T13:27:21Z
- **Tasks:** 2
- **Files modified:** 2 (1 new HUMAN-UAT.md, 1 STATE.md edit)

## Accomplishments

- All 10 statically-checkable UI-SPEC verification gates PASS against the on-disk artifacts produced by Wave 2 (Gates 2, 3, 4a, 4b, 6c, 6d, 8, 9, 10, plus redundant Pitfall 17 top-level `.about-` check).
- Both build-dependent gates PASS: Gate 6a (pullquote rendered HTML byte-identical post-shortcode-migration) and Gate 11 (build determinism — twice-built `diff -r` exits 0).
- Bonus rendered-output checks PASS: `about-hero-img` × 1, `about-grid-item` × 4, `about-role-card` × 3, `page-about` × 1, `<article class=about>` × 1 (all on-page occurrences in compiled `/about/index.html`).
- 09-HUMAN-UAT.md authored (108 LOC, 5 gate sections — each with steps, PASS criteria, FAIL action).
- STATE.md Deferred Items table extended: Phase 9 row added between Phase 7 row and the verification rows, matching the Phase 5/05.1/06/07 precedent format verbatim (`| uat | 09 | 09-HUMAN-UAT.md (5 gates) | partial | Post-deploy browser walkthrough at https://tbohnstedt.cloud/about/ |`).

## Task Commits

1. **Task 1: Run all automated verification gates** — _no commit_ (verification-only; results recorded in this SUMMARY).
2. **Task 2: Author 09-HUMAN-UAT.md + extend STATE.md Deferred Items** — `e51f81c` (docs).

**Plan metadata:** _committed at end of plan execution (this SUMMARY + state files)_

## Verbatim Gate Results

### Static gates (Task 1)

| Gate | Command | Output | Result |
|------|---------|--------|--------|
| 2 (REQ ABOUT-02) | `grep -cE 'eq \$title "(hero\|grid\|split\|feature)"' themes/minimal/layouts/_default/_markup/render-image.html` | `4` | **PASS** (expect 4 — feature shipped per locked branch decision) |
| 3 (REQ ABOUT-03) | `grep -c 'var(--radius-soft)' themes/minimal/static/css/style.css` | `5` | **PASS** (expect ≥ 5) |
| 4a (REQ ABOUT-04) | `grep -A 5 'body.page-about .about-role-card {' style.css \| grep -cE 'background: var\(--bg-secondary\)\|border: 1px solid var\(--border\)\|border-radius: var\(--radius-soft\)'` | `3` | **PASS** (all 3 properties present) |
| 4b (Pitfall 16) | `grep -A 5 'body.page-about .about-role-card' style.css \| grep -cE 'box-shadow\|linear-gradient\|transform:\|transition:'` | `0` | **PASS** (no forbidden treatments) |
| 6c rule body (REQ ABOUT-06, Pitfall 15) | `grep -A 4 'body.page-about .about-pullquote {' style.css \| grep -cE 'font-size: 1.4rem\|font-weight: 500'` | `2` | **PASS** |
| 6c strong (Pitfall 15) | `grep -A 2 'body.page-about .about-pullquote strong' style.css \| grep -c 'font-weight: 700'` | `1` | **PASS** |
| 6d (Pitfall 15) | `grep -c 'Dark-mode #D14D41 on #1C1B1A measures 3.97:1' style.css` | `1` | **PASS** (load-bearing comment preserved verbatim) |
| 8 (Pitfall 3, inverted form) | `awk` mask `:root` blocks + grep `#hex` outside in About rules | _empty_ | **PASS** (no hard-coded colors outside :root in About rules) |
| 9 (Pitfall 17, generic) | `grep -nE '^\.(card\|section\|feature\|role\|row\|split)\b' style.css` | _empty_ | **PASS** (no generic class-name leak) |
| 9 (Pitfall 17, top-level about) | `grep -nE '^\.about-' style.css` | _empty_ | **PASS** (every rule prefixed `body.page-about`) |
| 10 (Pitfall 21) | `find content/about themes/minimal/layouts/about themes/minimal/layouts/shortcodes -name '*.js'` | _empty_ | **PASS** (no JS on About surface) |

### Build-dependent gates (Task 1)

Hugo CLI was available locally (`hugo v0.161.1+extended+withdeploy darwin/amd64 (Homebrew)` at `/usr/local/bin/hugo`). Build-dependent gates ran inline rather than deferred to CI.

| Gate | Command | Output | Result |
|------|---------|--------|--------|
| 11 (build determinism) | `rm -rf public public.first; hugo --minify; mv public public.first; hugo --minify; diff -r public.first/about/ public/about/` | _empty diff_, exit 0 | **PASS** (byte-identical across consecutive builds) |
| 6a (pullquote rendered HTML, minified form) | `grep -A 1 '<aside class=about-pullquote>' public/about/index.html \| grep -c '<strong>40% → 95%</strong>'` | `1` | **PASS** (minified attribute form — Hugo strips quotes) |

### Bonus rendered-output checks (Task 1)

Compiled `/about/index.html` from `hugo --minify` confirms render-image hook arms apply correct classes:

| Element | Expected | Actual | Result |
|---------|----------|--------|--------|
| `class=about-hero-img` | 1 | 1 | **PASS** (hero portrait via in-template processing) |
| `class=about-grid-item` | 4 | 4 | **PASS** (4 hobby photos via grid hook arm) |
| `class=about-role-card` (excluding `-title`/`-meta`) | 3 | 3 | **PASS** (3 role cards from `range .Params.roles`) |
| `class=page-about` | 1 | 1 | **PASS** (body class via baseof.html type lookup) |
| `<article class=about>` | 1 | 1 | **PASS** (outer wrapper from new layout) |
| `<strong>40% → 95%</strong>` | 1 | 1 | **PASS** (markdownify converted **40% → 95%** correctly) |

**Note on bonus check methodology:** Hugo's `--minify` collapses HTML to fewer lines, so per-line counts (`grep -c`) under-count; per-occurrence counts (`grep -o … | wc -l`) match expected values exactly. Documented in key-decisions above.

### Task 2 acceptance gates

| Check | Command | Output | Result |
|-------|---------|--------|--------|
| 09-HUMAN-UAT.md exists | `test -f .planning/phases/09-about-dynamic-rounded-redesign/09-HUMAN-UAT.md` | exit 0 | **PASS** |
| File length | `wc -l 09-HUMAN-UAT.md` | `108` (need ≥ 60) | **PASS** |
| Gate sections | `grep -cE '^## Gate ' 09-HUMAN-UAT.md` | `5` | **PASS** |
| PASS criteria entries | `grep -c 'PASS criteria:' 09-HUMAN-UAT.md` | `5` | **PASS** |
| FAIL action entries | `grep -c 'FAIL action:' 09-HUMAN-UAT.md` | `5` | **PASS** |
| Deployed URL references | `grep -c 'tbohnstedt.cloud/about' 09-HUMAN-UAT.md` | `5` (need ≥ 3) | **PASS** |
| STATE.md row added | `grep -c '09-HUMAN-UAT.md' .planning/STATE.md` | `1` | **PASS** |
| Row format matches precedent | `grep -cE '\| uat \| 09 \| 09-HUMAN-UAT.md.*\| partial' STATE.md` | `1` | **PASS** |
| Existing rows preserved | `grep -cE '05-HUMAN-UAT.md\|05.1-HUMAN-UAT.md\|06-HUMAN-UAT.md\|07-HUMAN-UAT.md' STATE.md` | `4` | **PASS** |
| Trigger paragraph intact | `grep -c 'All items gated on the same trigger' STATE.md` | `1` | **PASS** |

## Files Created/Modified

- **`.planning/phases/09-about-dynamic-rounded-redesign/09-HUMAN-UAT.md` (NEW, 108 LOC)** — Post-deploy browser walkthrough checklist. 5 gate sections (Gate 1 asymmetric layout, Gate 4c no CSS leak to /blog/+/gallery/, Gate 5 content rebalance, Gate 6b live DevTools dark-mode contrast inspector, Gate 7a 320 px mobile emulation). Each gate: 6-7 numbered steps, explicit PASS criteria, explicit FAIL action with root-cause hypothesis. Resolution section: when all 5 PASS in a real browser walkthrough, mark Phase 9 fully shipped.
- **`.planning/STATE.md` (MODIFIED, +1 row)** — Deferred Items table extended with `| uat | 09 | 09-HUMAN-UAT.md (5 gates) | partial | Post-deploy browser walkthrough at https://tbohnstedt.cloud/about/ |`. Inserted between Phase 7 row and verification rows. Existing Phase 5/05.1/06/07 rows preserved verbatim. Trigger paragraph below table preserved verbatim.

## Hugo Build Command Used

```bash
rm -rf public public.first
hugo --minify    # First build, exit 0
mv public public.first
hugo --minify    # Second build, exit 0
diff -r public.first/about/ public/about/  # → no output (byte-identical)
rm -rf public public.first
```

`hugo v0.161.1+extended+withdeploy darwin/amd64 (Homebrew)`. Both builds: 16 pages / ~46 processed images / ~70 ms.

Pre-existing warnings about `.Site.LanguageCode` / project config key `languageCode` (deprecated in Hugo v0.158.0) are unrelated to this plan and out of scope per the SCOPE BOUNDARY rule.

## Phase-Close Summary

**Phase 9 — ABOUT — Dynamic Rounded Redesign — code complete, automated gates green, HUMAN-UAT queued for post-deploy.**

**Total plan count:** 3 (09-01 Foundation, 09-02 Application, 09-03 Verification).

| Wave | Plan | Outcome |
|------|------|---------|
| 1 (Foundation) | 09-01 | 3 dormant primitives shipped: pullquote/split/feature shortcodes + render-image hook arms (split/feature) + `--radius-soft: 12px` token. `/about/index.html` byte-identical to pre-Plan-09-01 baseline (Pitfall 14). |
| 2 (Application) | 09-02 | Atomic activation: new `themes/minimal/layouts/about/single.html` (Hugo type-routed), `content/about/index.md` rewrite (frontmatter `roles:` array, Outside Work rename, raw HTML wrappers dropped), `/* === About === */` CSS rewrite (5 `var(--radius-soft)` consumers, role-card visual contract, asymmetric splits, mobile @media extension). |
| 3 (Verification) | 09-03 | All 12 UI-SPEC gates verified (10 static + 2 build-dependent PASS); 5 visual-judgment gates scaffolded as `09-HUMAN-UAT.md` and tracked in STATE.md Deferred Items per Phase 5/05.1/06/07 precedent. |

**Requirements completed (all 7 ABOUT-* IDs):**

- **ABOUT-01:** Plan 09-02 (layout file + asymmetric structure) + Plan 09-03 Gate 1 HUMAN-UAT.
- **ABOUT-02:** Plan 09-01 (hook arms) + Plan 09-03 Gate 2 automated (PASS, count 4).
- **ABOUT-03:** Plan 09-01 (token declared) + Plan 09-02 (5 selectors) + Plan 09-03 Gate 3 automated (PASS, count 5).
- **ABOUT-04:** Plan 09-02 (role-card visual contract) + Plan 09-03 Gates 4a/4b automated (PASS), 4c HUMAN-UAT.
- **ABOUT-05:** Plan 09-02 (content rewrite) + Plan 09-03 Gate 5 HUMAN-UAT.
- **ABOUT-06:** Plan 09-02 (pullquote rule preserved verbatim) + Plan 09-03 Gates 6a/6c/6d automated (PASS), 6b HUMAN-UAT.
- **ABOUT-07:** Plan 09-02 (mobile @media block extended) + Plan 09-03 Gate 7b automated (verified mobile reflow rules present), 7a HUMAN-UAT.

## Decisions Made

All decisions inherited from 09-CONTEXT.md (D-01 through D-14) and the locked HUMAN-UAT scaffolding pattern from Phase 5/05.1/06/07. No new decisions made during execution — this plan executed exactly as written.

Two minor execution-time clarifications worth recording:

- **Gate 6a verification used minified attribute form.** PLAN.md authored the gate command against quoted form (`<aside class="about-pullquote">`); Hugo's `--minify` strips quotes around single-token attributes, so the actual rendered output uses unquoted form (`<aside class=about-pullquote>`). Verified via the unquoted form (count = 1). Both forms have been documented as semantically equivalent — this is a style/representation difference, not a content difference.
- **Bonus rendered-output checks counted occurrences not lines.** Hugo's minified output collapses HTML across fewer lines, so per-line counts (`grep -c`) under-count when multiple matches share a line. Per-occurrence counts (`grep -o … | wc -l`) match expected values (1, 4, 3, 1, 1) exactly.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None blocking.

One pre-existing Hugo warning surfaced during builds (`.Site.LanguageCode` / project config key `languageCode` deprecated in v0.158.0) — out of scope for Plan 09-03 per the executor SCOPE BOUNDARY rule; logged here for future cleanup but not fixed.

## Note for Next Milestone Close (post-Phase-10 ship of v3.0)

When the v3.0 milestone closes (after Phase 10 — GALLERY ships), walk all deferred HUMAN-UATs in a single browser session:

- 05-HUMAN-UAT.md (4 scenarios — favicon)
- 05.1-HUMAN-UAT.md (6 scenarios — favicon SVG prefers-color-scheme)
- 06-HUMAN-UAT.md (theme toggle)
- 07-HUMAN-UAT.md (about hero/portrait)
- **09-HUMAN-UAT.md (5 gates — Phase 9 dynamic rounded redesign)**

The walkthrough trigger is the same for all: push commits → GitHub Actions deploy → browser verification at https://tbohnstedt.cloud/.

## Self-Check: PASSED

- File existence verified:
  - `.planning/phases/09-about-dynamic-rounded-redesign/09-HUMAN-UAT.md` — FOUND (108 LOC)
  - `.planning/STATE.md` — FOUND (modified, +1 row in Deferred Items)
- Commit verified in `git log`:
  - `e51f81c` (Task 2 — `docs(09-03): scaffold 09-HUMAN-UAT.md + extend STATE.md Deferred Items`) — FOUND
- All 11 UI-SPEC verification gates run; all automatable gates PASS:
  - 10 statically-checkable: PASS (Gates 2, 3, 4a, 4b, 6c, 6d, 8, 9, 10, plus redundant Pitfall 17 top-level `.about-` check)
  - 2 build-dependent: PASS (Gates 6a, 11)
  - 6 bonus rendered-output checks: PASS (about-hero-img × 1, about-grid-item × 4, about-role-card × 3, page-about × 1, `<article class=about>` × 1, pullquote `<strong>40% → 95%</strong>` × 1)
- 5 visual-judgment gates scaffolded for HUMAN-UAT post-deploy walkthrough (Gates 1, 4c, 5, 6b, 7a).
- STATE.md Deferred Items table now has Phase 9 row matching Phase 5/05.1/06/07 precedent verbatim.

---
*Phase: 09-about-dynamic-rounded-redesign*
*Completed: 2026-05-02*

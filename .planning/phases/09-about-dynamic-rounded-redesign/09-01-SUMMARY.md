---
phase: 09-about-dynamic-rounded-redesign
plan: 01
subsystem: ui
tags:
  - hugo
  - shortcodes
  - render-hook
  - css-token
  - dormant-primitives

# Dependency graph
requires:
  - phase: 08-theme-toggle
    provides: theme-toggle scaffolding (independent — Phase 9 only co-exists, no shared surfaces touched)
provides:
  - "render-image hook arms for `split` (fit 600x450 webp q78 → about-split-img) and `feature` (fill 1024x576 Smart webp q80 → about-feature-img), symmetrically wired in both the image.Process switch AND the class-attribute mux"
  - "pullquote shortcode emitting `<aside class=\"about-pullquote\">` (byte-identical to current raw HTML in content/about/index.md:35-37)"
  - "split shortcode emitting `<div class=\"about-split about-split--{variant}\">` with .Get 0 / default \"text-first\" fallback"
  - "feature shortcode emitting `<figure class=\"about-feature\">` for full-bleed focal image"
  - "`--radius-soft: 12px` CSS custom property declared inside light :root block (theme-invariant — dark :root inherits via cascade)"
  - "Dormant-primitives invariant verified: /about/index.html byte-identical to pre-Plan-09-01 baseline (no markdown invokes new arms/shortcodes, no CSS consumes new token)"
affects:
  - 09-02-PLAN.md  # consumes shortcodes + hook arms via content rewrite, consumes --radius-soft via ≥5 CSS selectors
  - 09-03-PLAN.md  # carries Hugo build verification + adapts UI-SPEC Gate 2 to grep boolean declarations

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hugo render-image hook with title-keyed arms (pre-bound boolean variables `$isHero`/`$isGrid`/`$isSplit`/`$isFeature`) instead of inline `eq $title` re-checks"
    - "Hugo shortcode `.Inner | markdownify` pipeline (markdownify NOT safeHTML — bodies contain markdown like **bold** and image syntax) per PATTERNS Shared Pattern 5"
    - "Symmetric edit invariant for render-image hook: every new title arm MUST appear in BOTH the image.Process switch AND the class-attribute mux (otherwise image renders at correct dimensions but with no class, silently breaking selectors)"
    - "Pitfall 14 ordering: ship hook arms FIRST (Plan 1, dormant), then content that invokes them (Plan 2) — prevents silent fallback to default 800x600 arm"
    - "Dormant-primitives plan pattern: foundation primitives land without changing rendered output; activation deferred to a single atomic plan"

key-files:
  created:
    - themes/minimal/layouts/shortcodes/pullquote.html
    - themes/minimal/layouts/shortcodes/split.html
    - themes/minimal/layouts/shortcodes/feature.html
  modified:
    - themes/minimal/layouts/_default/_markup/render-image.html  # +14 LOC, -3 LOC; +split, +feature arms
    - themes/minimal/static/css/style.css  # +1 LOC; --radius-soft: 12px in light :root

key-decisions:
  - "Ship `feature` shortcode + hook arm together with `pullquote` and `split` (per UI-SPEC `[FLAG → recommendation]` and RESEARCH 'Risk Hotspots' rule: never half-ship; ~16 LOC of cheap design slack preserved for HUMAN-UAT-driven follow-ups)"
  - "Use pre-bound boolean variables (`$isSplit`, `$isFeature`) in the hook switch rather than inline `eq $title` re-checks (D-07 + UI-SPEC § 'Hook implementation pattern'); this means UI-SPEC Gate 2 (`grep -c \"else if eq \\$title\" ≥ 3`) needs adaptation in Plan 09-03"
  - "split arm uses `fit` not `fill` (`fit 600x450 webp q78`) per Pitfall 19 mitigation — preserves portrait/landscape aspect without cropping faces"
  - "feature arm uses `fill 1024x576 Smart webp q80` — 16:9 banner with smart-crop focal-point detection"
  - "All three new shortcodes use `.Inner | markdownify`, NOT `safeHTML` — bodies contain markdown (**bold**, image syntax); mermaid uses safeHTML because its body is mermaid DSL (PATTERNS Shared Pattern 5)"
  - "`--radius-soft` declared once in light :root, NOT duplicated in `:root[data-theme=\"dark\"]` — radius is theme-invariant and CSS custom-property cascade inherits unchanged values into dark theme (D-08)"
  - "All three Plan-09-01 additions are dormant: no markdown invokes the new arms/shortcodes, no CSS consumes the new token; rendered /about/index.html is byte-identical to pre-plan baseline (Pitfall 14 safety)"

patterns-established:
  - "Title-keyed render-image hook with symmetric edit invariant: each new title arm requires entries in BOTH the image.Process switch AND the class-attribute mux"
  - "Hugo shortcode markdownify pipeline for content callouts (pullquote/split/feature) vs safeHTML for DSL embeds (mermaid)"
  - "Dormant primitive land-then-activate ordering: shortcodes/hook-arms/CSS-tokens land first (Plan N), content+CSS-rules that consume them land atomically next (Plan N+1)"

requirements-completed:
  - ABOUT-02
  - ABOUT-03

# Metrics
duration: 2 min
completed: 2026-05-02
---

# Phase 09 Plan 01: Foundation Summary

**Three Hugo shortcodes (`pullquote`, `split`, `feature`) + two new render-image hook arms (`split`/`feature`) + `--radius-soft: 12px` token landed dormant — `/about/index.html` byte-identical to pre-plan baseline.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-05-02T13:08:48Z
- **Completed:** 2026-05-02T13:11:22Z
- **Tasks:** 3
- **Files modified:** 5 (1 modified template, 3 new shortcodes, 1 CSS edit)

## Accomplishments
- Render-image hook now recognises `split` and `feature` titles symmetrically — both the image.Process switch AND the class-attribute mux carry matching branches
- Three new shortcodes parse without Hugo errors and emit class names that match the existing CSS contract (pullquote) or the upcoming Plan 09-02 contract (split/feature)
- `--radius-soft: 12px` declared in `:root` — dormant token waiting for Plan 09-02 to consume it in ≥ 5 selectors
- Hugo build deterministic across two consecutive `--minify` runs (UI-SPEC Gate 11 carry-forward)
- Dormant-primitives invariant verified: `/about/index.html` byte-identical to pre-Plan-09-01 baseline (30,823 bytes, both rendered via `hugo --minify`)

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend render-image.html with split + feature arms** — `d0f4c0b` (feat)
2. **Task 2: Create pullquote/split/feature shortcodes (markdownify pipeline)** — `aaef4ce` (feat)
3. **Task 3: Declare --radius-soft: 12px in :root (dormant)** — `03b3416` (feat)

**Plan metadata:** _committed at end of plan execution (this SUMMARY + state files)_

## Files Created/Modified
- `themes/minimal/layouts/_default/_markup/render-image.html` — extended from 21 LOC to 32 LOC; added `$isSplit`/`$isFeature` pre-bound vars, two new image.Process branches (`fit 600x450 webp q78` and `fill 1024x576 Smart webp q80`), and matching class-attribute mux branches; hero/grid/default arms and Pitfall 14 passthrough fallback preserved verbatim
- `themes/minimal/layouts/shortcodes/pullquote.html` (NEW, 3 LOC) — `<aside class="about-pullquote">` wrapper, byte-identical to current raw HTML at content/about/index.md:35-37
- `themes/minimal/layouts/shortcodes/split.html` (NEW, 6 LOC) — two-variant grid wrapper; `.Get 0 | default "text-first"` so missing positional arg is safe; emits `about-split about-split--{variant}` two-class output for base+variant CSS rules
- `themes/minimal/layouts/shortcodes/feature.html` (NEW, 5 LOC) — `<figure class="about-feature">` full-bleed wrapper; no `<figcaption>` per UI-SPEC (no decorative furniture / Flexoki bias)
- `themes/minimal/static/css/style.css` — added one line `--radius-soft: 12px;` inside light `:root` block (sibling of `--max-width`); dark `:root[data-theme="dark"]` block untouched (cascade inheritance)

## Verbatim Grep Gate Results

### Task 1 acceptance (render-image.html)
```
split title decl:           1  (eq $title "split")
feature title decl:         1  (eq $title "feature")
about-split-img class:      1  (class="about-split-img")
about-feature-img class:    1  (class="about-feature-img")
fit 600x450 webp q78:       1  (split arm — fit, not fill, per Pitfall 19)
fill 1024x576 Smart webp q80: 1  (feature arm 16:9 banner)
fill 480x600 Smart webp q80:  1  (hero arm preserved verbatim)
fill 400x300 Smart webp q75:  1  (grid arm preserved verbatim)
fill 800x600 Smart webp q78:  1  (default arm preserved verbatim)
safeURL:                    1  (Pitfall 14 passthrough fallback preserved)
=> ALL_PASS
```

### Task 2 acceptance (shortcodes)
```
pullquote.html EXISTS, split.html EXISTS, feature.html EXISTS
class="about-pullquote" in pullquote.html:    1
.Inner | markdownify in pullquote.html:       1
about-split about-split-- in split.html:      1
.Get 0 | default "text-first" in split.html:  1
.Inner | markdownify in split.html:           1
class="about-feature" in feature.html:        1
<figure in feature.html:                      1
.Inner | markdownify in feature.html:         1
safeHTML across all 3 (must be 0):            0
=> ALL_PASS
```

### Task 3 acceptance (style.css :root token)
```
radius-soft: 12px declarations:                                   1
var(--radius-soft) consumers (must be 0 — Plan 09-02 brings ≥ 5): 0
radius-soft inside light :root block:                             1
radius-soft inside dark :root[data-theme="dark"] (must be 0):     0
hugo --minify exit code:                                          0
build determinism (two consecutive runs, diff -r public/about/):  identical
/about/index.html vs pre-Plan-09-01 baseline (diff):              byte-identical
=> ALL_PASS
```

### Plan-level verification gates (after all 3 tasks)
- Gate 1 (`hugo --minify` succeeds): exit 0 — PASS
- Gate 2 (no regression on hero/grid/default arms + safeURL passthrough): all 4 grep counts = 1 — PASS
- Gate 3 (new arms wired symmetrically): `$isSplit` appears 3 times (declaration + switch arm + class-mux arm), `$isFeature` appears 3 times (same pattern), `about-split-img` and `about-feature-img` each appear 1 time — PASS
- Gate 4 (all 3 shortcodes use markdownify): pullquote/split/feature all PASS
- Gate 5 (token declared but dormant): `radius-soft: 12px` count = 1; `var(--radius-soft)` count = 0 — PASS
- Gate 6 (build determinism): two consecutive `hugo --minify` runs produce byte-identical `public/about/` — PASS
- Gate 7 (dormant-primitives invariant): `/about/index.html` byte-identical to pre-Plan-09-01 baseline — PASS

## Hugo Build Command Used

```bash
hugo --minify
# Exit code: 0
# hugo v0.161.1+extended+withdeploy darwin/amd64 (Homebrew)
```

Build determinism check (two consecutive runs):
```bash
rm -rf public public.first
hugo --minify
mv public public.first
hugo --minify
diff -r public.first/about/ public/about/  # → no output = identical
```

## Decisions Made

All decisions were already locked in 09-CONTEXT.md (D-01 through D-14) and surfaced into the plan's `<action>` blocks. No new decisions were made during execution; this plan executed exactly as written. Key locked decisions reaffirmed by execution:

- **D-05** (ship feature alongside pullquote/split): honoured — all three shortcodes shipped together, no half-shipping
- **D-07** (pre-bound booleans in render-image hook): honoured — `$isSplit`/`$isFeature` pattern matches existing `$isHero`/`$isGrid` style
- **D-08** (`--radius-soft` in light :root only, dark inherits via cascade): honoured — single declaration, dark block untouched
- **D-09** (pullquote shortcode emits byte-identical output to current raw `<aside>` HTML): honoured — same class name, same element

## Confirmation: feature shortcode + hook arm shipped together

Per the locked branch decision in `<objective>` and per UI-SPEC `[FLAG → recommendation]` + RESEARCH "Risk Hotspots" never-half-ship rule: BOTH the `feature` shortcode (`themes/minimal/layouts/shortcodes/feature.html`) AND the `feature` render-image hook arm (lines 7, 14-15, 26 of the new `render-image.html`) shipped in this plan. Plan 09-02's content rewrite does not have to invoke `feature`, but the slack is preserved for HUMAN-UAT-driven follow-ups in Plan 09-03 or beyond.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. Hugo was available on PATH (the plan's `[ASSUMED]` clause noted "Hugo is NOT installed locally" per CLAUDE.md, but `command -v hugo` returned `/usr/local/bin/hugo` — Homebrew install of `hugo v0.161.1+extended+withdeploy`), so the build-determinism check was performed inline rather than deferred to Plan 09-03.

## User Setup Required

None — no external service configuration required.

## Notes for Plan 09-02

Plan 09-02 must consume the contracts established here verbatim:

| Contract | Class name(s) | Established by |
|----------|---------------|----------------|
| pullquote | `about-pullquote` | shortcode + existing CSS at style.css:357 |
| split base | `about-split` | new shortcode |
| split text-first variant | `about-split--text-first` | new shortcode (default when no arg) |
| split image-first variant | `about-split--image-first` | new shortcode (when `{{< split "image-first" >}}`) |
| split image inside | `about-split-img` (auto-applied to `![alt](src "split")`) | render-image hook |
| feature wrapper | `about-feature` | new shortcode |
| feature image inside | `about-feature-img` (auto-applied to `![alt](src "feature")`) | render-image hook |
| Soft-radius token | `--radius-soft: 12px` | `:root` declaration |

**Plan 09-02 CSS rewrite must consume `var(--radius-soft)` in ≥ 5 selectors** (UI-SPEC Gate 3 — currently the consumer count is 0, plan-level Gate 5 in this summary).

## Notes for Plan 09-03

UI-SPEC Gate 2 needs adaptation: it expects `grep -c "else if eq \$title" render-image.html` to be ≥ 3, but the locked target template (per D-07) uses pre-bound boolean variables — the actual greppable text is `eq \$title "X"` on the declaration lines plus `else if \$isX` on the switch/class-mux lines. Plan 09-03's Gate 2 command should grep for the boolean declarations (`grep -c '\$isSplit' render-image.html` returns 3, `grep -c '\$isFeature'` returns 3) instead of the literal `else if eq $title` string. The functional intent — "the hook handles the split and feature title arms" — is verified by Plan 09-01's Gate 3 above (`about-split-img` count = 1, `about-feature-img` count = 1, both Process strings present).

If Plan 09-03 still expects to assert Hugo build verification: this plan already ran `hugo --minify` to exit 0 and verified determinism + dormant-primitives invariant. Plan 09-03 may re-run as a confidence check but is not blocked by it.

## Next Phase Readiness

- Plan 09-01 primitives (3 shortcodes, 2 hook arms, 1 token) are landed and dormant
- Plan 09-02 may now atomically: (a) rewrite `content/about/index.md` to invoke `{{< pullquote >}}`, `{{< split >}}`, optionally `{{< feature >}}`, plus markdown image syntax with `"split"` / `"feature"` titles, (b) rewrite the `/* === About === */` CSS block at style.css:340-391 to consume `var(--radius-soft)` in ≥ 5 selectors, (c) extend the mobile reflow block at style.css:431-444 with split/feature responsive rules
- No blockers; no concerns

## Self-Check: PASSED

- File existence verified:
  - `themes/minimal/layouts/_default/_markup/render-image.html` — FOUND
  - `themes/minimal/layouts/shortcodes/pullquote.html` — FOUND
  - `themes/minimal/layouts/shortcodes/split.html` — FOUND
  - `themes/minimal/layouts/shortcodes/feature.html` — FOUND
  - `themes/minimal/static/css/style.css` — FOUND (modified)
- Commits verified in `git log`:
  - `d0f4c0b` (Task 1) — FOUND
  - `aaef4ce` (Task 2) — FOUND
  - `03b3416` (Task 3) — FOUND

---
*Phase: 09-about-dynamic-rounded-redesign*
*Completed: 2026-05-02*

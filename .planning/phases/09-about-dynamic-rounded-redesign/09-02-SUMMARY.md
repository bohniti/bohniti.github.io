---
phase: 09-about-dynamic-rounded-redesign
plan: 02
subsystem: ui
tags:
  - hugo-layout
  - css
  - content-rewrite
  - flexoki

# Dependency graph
requires:
  - phase: 09-01
    provides: pullquote/split/feature shortcodes, render-image hook arms (split/feature), --radius-soft: 12px token
provides:
  - "themes/minimal/layouts/about/single.html — dedicated About layout, type-routed via Hugo's `type: \"about\"` lookup chain (no config change needed)"
  - "Frontmatter `roles:` array authoring convention — array iterated via `range .Params.roles`, each role emits <li class=\"about-role-card\"> with title/meta/bullets, optional pullquote rendered as <aside class=\"about-pullquote\"> after the card"
  - "<div class=\"about-prose\"> wrapper around .Content — scopes prose styling without polluting global .page-content cascade"
  - "5 .about-* selectors consuming var(--radius-soft) (hero-img, grid-img, role-card, feature, feature-img) — UI-SPEC Gate 3 PASS"
  - "Mobile reflow extension inside the single existing @media (max-width: 600px) block — collapses splits/role-list/role-card/feature without opening a nested @media"
affects:
  - 09-03-PLAN.md  # consumes the rendered DOM for full automated gate suite + HUMAN-UAT scaffolding

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hugo type-routed layout via leaf-bundle frontmatter `type: \"about\"` (auto-routes to layouts/about/single.html — no `layout:` field needed)"
    - "Front-matter structured-data + `range .Params.X` iteration as authoring convention (Option A): cleanest separation between data (3 roles) and rendering (1 layout); avoids string-parsing fragility"
    - "Markdownify pipeline preserves emphasis through frontmatter strings — `**40% → 95%**` in YAML scalar renders as <strong>40% → 95%</strong> in HTML"
    - "Body-class scoping (body.page-about .selector) for page-local CSS rules — every Phase 9 rule prefixed; no generic .card/.row/.section leak to /blog/, /gallery/"
    - "In-template image processing for layout-owned chrome (hero portrait at fill 480x600 Smart webp q80) parallel to render-image hook arms for markdown-body images"

key-files:
  created:
    - themes/minimal/layouts/about/single.html
  modified:
    - content/about/index.md
    - themes/minimal/static/css/style.css

key-decisions:
  - "Layout uses `range .Params.roles` directly (rather than `with .Params.roles` + `range .`) — matches the acceptance-criteria grep contract verbatim and produces equivalent Hugo output"
  - "Layout deliberately omits `.page-header` chrome (no <h1 class=\"page-title\">) — intentional divergence from gallery analog per UI-SPEC § \"Page-level skeleton\"; the H2 'Hi, I'm Timo.' (rendered from heroIntro markdownify) serves the page-introduction role"
  - "Pullquote keeps its asymmetric one-sided radius `0 4px 4px 0` (NOT swapped to var(--radius-soft)) — D-09 visual signal pairing with the 4px border-left"
  - "Hobby grid 4-photo wrapper kept as raw `<div class=\"about-grid\">` in markdown body (Hugo unsafe=true permits) — preserves the `grid` render-image hook arm firing per Pitfall 14"
  - "feature shortcode + hook arm + .about-feature CSS rules ship as design slack (no DOM consumer in markdown) — locked branch decision from 09-01 honoured"
  - "Layout iterates roles outer-loop with `range .Params.roles`, inner-loop bullets with `range .bullets` and `with .pullquote` — pullquote rendered as a sibling <aside> after each <li class=\"about-role-card\"> when present"

patterns-established:
  - "Frontmatter-driven structured content + `range .Params.X` iteration for repeated content blocks (roles), with markdown body retained for narrative/list sections"
  - "Layout owns structural shells (hero, role-card list, prose wrapper); markdown owns narrative content + raw HTML wrappers for nested grids that drive render-image hook arms"
  - "Mobile reflow rules added inside the existing single @media (max-width: 600px) block — never open a nested or duplicate @media (D-10)"

requirements-completed:
  - ABOUT-01
  - ABOUT-04
  - ABOUT-05
  - ABOUT-06
  - ABOUT-07
# (ABOUT-03 was completed by 09-01; this plan also consumes --radius-soft per ABOUT-03 contract)

# Metrics
duration: 4 min
completed: 2026-05-02
---

# Phase 09 Plan 02: Application Summary

**Atomic activation of Wave 1 primitives — new about/single.html layout (frontmatter roles iteration, no .page-header chrome), rewritten content/about/index.md (drops raw HTML wrappers, Outside Work rename), and rewritten /* === About === */ CSS block (5 var(--radius-soft) consumers, role-card cluster, asymmetric splits, mobile reflow extension).**

## Performance

- **Duration:** 4 min
- **Started:** 2026-05-02T13:15:55Z
- **Completed:** 2026-05-02T13:19:59Z
- **Tasks:** 3
- **Files modified:** 3 (1 new layout, 1 rewritten markdown, 1 modified CSS — net ~140 LOC)

## Accomplishments
- Dedicated `themes/minimal/layouts/about/single.html` (58 LOC) — Hugo's `type: "about"` lookup auto-routes to it; intentionally no `.page-header` chrome (UI-SPEC divergence from gallery analog).
- `content/about/index.md` rewritten: hero prose moved to `heroIntro` frontmatter param, 3 Experience roles moved to `roles:` frontmatter array, raw `<div class="about-hero">` and `<aside class="about-pullquote">` wrappers dropped, Interests → Outside Work renamed, `(Highlights)` parenthetical dropped, `<hr>` dividers dropped.
- `/* === About === */` CSS block rewritten in place: radius literals (6px, 4px) for hero+grid swapped to `var(--radius-soft)`; pullquote rule preserved unchanged in shape (one-sided `0 4px 4px 0` retained as visual signal per D-09); both load-bearing comments preserved verbatim (contrast comment, RESEARCH amendment 1).
- New CSS rule clusters added: `.about-section` + `.about-prose` (asymmetric section margins + scoped prose styling), `.about-role-list` + `.about-role-card` (7 rules: grid layout, bg-secondary card, 1px border, radius-soft, 1.5rem padding, scoped title/meta/bullets), `.about-split` + variants (3 rules: 2fr 1fr / 1fr 2fr / base), `.about-feature` + `.about-feature-img` (2 rules — design slack, no markdown consumer yet).
- Mobile `@media (max-width: 600px)` block extended in place (no new @media opened, no nested @media — D-10): `body.page-about` selectors for `.about-section`, `.about-prose`, splits, `.about-role-list`, `.about-role-card`, `.about-feature` mobile rules.
- Hugo `--minify` builds with exit 0; rendered `/about/` HTML contains the new asymmetric layout.

## Layout Routing Decision

**Option A (locked from RESEARCH § "Authoring convention for role cards"):** Front-matter `roles:` array iterated by the layout via `range .Params.roles`. Each role: `title`, `meta`, `bullets[]`, optional `pullquote`. The layout uses `{{ if .Params.roles }}…{{ range .Params.roles }}` directly (rather than `with .Params.roles` + `range .`) so the acceptance-criteria grep contract `range .Params.roles` is satisfied verbatim. Hugo output is equivalent.

**Confirmation: the layout DOES NOT use `.page-header` chrome.** Verified `grep -c 'class="page-header"\|class="page-title"' themes/minimal/layouts/about/single.html` returns 0. This is an intentional divergence from the gallery analog per UI-SPEC § "Page-level skeleton" — the H2 `Hi, I'm Timo.` (rendered from `heroIntro` markdownify) serves the page-introduction role.

## Task Commits

1. **Task 1: Create themes/minimal/layouts/about/single.html** — `ea74320` (feat)
2. **Task 2: Rewrite content/about/index.md (frontmatter roles, Outside Work)** — `d5a2774` (feat)
3. **Task 3: Rewrite About CSS block + extend mobile @media** — `aa7751e` (feat)

**Plan metadata:** _committed at end of plan execution (this SUMMARY + state files)_

## Files Created/Modified

- **`themes/minimal/layouts/about/single.html` (NEW, 58 LOC)** — `{{ define "main" }}` + `<article class="about">` shell. `<section class="about-hero">` with hero text from `.Params.heroIntro | markdownify` and portrait from `.Resources.GetMatch "images/portrait.jpg"` processed in-template at `fill 480x600 Smart webp q80` (matches Phase 7 hero parameters per Pitfall 19). `<section class="about-section" data-section="experience">` with `<ol class="about-role-list">` of `<li class="about-role-card">` items, optional `<aside class="about-pullquote">` rendered as a sibling via `with .pullquote`. `<div class="about-prose">{{ .Content }}</div>` wraps Education/Certifications/Outside Work markdown body. No `.page-header` chrome. All class names `.about-` prefixed.
- **`content/about/index.md` (REWRITE, 60 LOC)** — Frontmatter: `title: "About"`, `type: "about"`, `heroIntro: |` (3-paragraph hero block + CV link), `roles:` array (3 entries: Erste Group with pullquote, Accenture, Siemens). Markdown body: H2 Education + 3 bullets, H2 Certifications + 3 bullets, H2 Outside Work + lead paragraph + `<div class="about-grid">` raw wrapper around 4 hobby photos with `"grid"` titles. All raw `about-hero`/`about-hero-text`/`about-hero-photo`/`about-pullquote` wrappers dropped. `## Interests` → `## Outside Work`. `(Highlights)` parenthetical and 3 `<hr>` dividers removed.
- **`themes/minimal/static/css/style.css` (MODIFIED, +125 LOC, -2 LOC)** — `/* === About === */` block rewritten in place (was lines 340-391, now lines 340-509). Mobile `@media (max-width: 600px)` block extended in place at lines 535-563 (was 14 lines, now 27 lines). Radius literals swapped: `6px` (hero img) and `4px` (grid img) → `var(--radius-soft)`. New rule clusters: 5 `.about-section`/`.about-prose` rules + 7 `.about-role-list`/`.about-role-card` rules + 3 `.about-split` rules + 2 `.about-feature` rules. Mobile @media block additions: `.about-section,.about-prose` margin-top reduction, `.about-split` variants collapse to `1fr`, `.about-role-list` gap reduction, `.about-role-card` padding reduction, `.about-feature` margin reduction.

## Verbatim Grep Gate Results

### Task 1 acceptance (layouts/about/single.html)
```
file exists:                          PASS
{{ define "main" }}:                  1
<article class="about">:              1
<section class="about-hero">:         1
about-hero-text|about-hero-photo:     2
class="about-hero-img":               1
fill 480x600 Smart webp q80:          1   (Pitfall 19 — hero arm parameters preserved)
range .Params.roles:                  1
class="about-section":                1
class="about-role-list":              1
class="about-role-card":              1
about-role-card-title:                1
about-role-card-meta:                 1
class="about-prose":                  1
{{ .Content }}:                       1
.page-header chrome (must=0):         0   (intentional divergence from gallery)
generic class names (must=0):         0   (Pitfall 17 — every class .about- prefixed)
=> ALL_PASS
```

### Task 2 acceptance (content/about/index.md)
```
title: "About":                       1
type: "about":                        1
heroIntro::                           1
^roles::                              1
title: "Senior Data Science Consultant": 1
title: "Data Science Analyst":        1
title: "ML Engineer":                 1
pullquote stat field:                 1
<div class="about-hero"> (must=0):    0
<aside class="about-pullquote"> (must=0): 0
<div class="about-hero-text"> (must=0): 0
<div class="about-hero-photo"> (must=0): 0
## Interests (must=0):                0
## Outside Work:                      1
<div class="about-grid">:             1
images/climbing.jpg "grid":           1
images/cycling.jpg "grid":            1
images/running.jpg "grid":            1
images/cooking.JPG "grid":            1
Download full CV (PDF):               1
/files/timo-bohnstedt-cv.pdf:         1
Experience (Highlights) (must=0):     0
=> ALL_PASS
```

### Task 3 acceptance (style.css)
```
:root --radius-soft: 12px:                          1
var(--radius-soft) consumers:                       5    (UI-SPEC Gate 3 PASS — needed >=5)
Dark-mode #D14D41 on #1C1B1A 3.97:1 comment:        1    (preserved verbatim — Pitfall 15)
RESEARCH amendment 1 comment:                       1    (preserved verbatim)
border-radius: 0 4px 4px 0 (pullquote):             1    (D-09 — NOT swapped to var(--radius-soft))
.about-pullquote font-size 1.4rem:                  1
.about-pullquote font-weight 500:                   1
.about-pullquote strong font-weight 700:            1    (Pitfall 15 contrast invariant preserved)
.about-role-card background var(--bg-secondary):    1
.about-role-card border 1px solid var(--border):    1
.about-role-card border-radius var(--radius-soft):  1
.about-role-card forbidden treatments (must=0):     0    (no box-shadow|gradient|transform|transition)
.about-split--text-first count (>=2):               2
.about-split--image-first count (>=2):              2
.about-split--text-first grid-template 2fr 1fr:     1
.about-split--image-first grid-template 1fr 2fr:    1
@media (max-width: 600px) count:                    1    (single block — D-10)
mobile @media about-split rules:                    3    (selector group expands)
mobile @media about-role-list:                      1
mobile @media about-role-card:                      1
mobile @media about-hero (preserved):               1
mobile @media about-grid (preserved):               1
top-level generic class names (must=0):             0
top-level .about- selectors (must=0):               0    (every rule prefixed body.page-about)
hard-coded colors in About rules outside :root:     0    (every color is var(--…))
=> ALL_PASS
```

### Plan-level verification (post-build /about/index.html)

```
Gate 1 — hugo --minify exit:               0   (PASS)
Gate 2 — themes/minimal/layouts/about/single.html exists: PASS
Gate 2 — about-role-card occurrences:      3   (3 role cards rendered from frontmatter array)
Gate 2 — <article class=about> count:      1   (Hugo minify strips quotes around single-token attrs)
Gate 2 — class=page-about body class:      1   (baseof.html:26 type lookup confirmed)
Gate 3 — <aside class=about-pullquote>:    1   (REQ ABOUT-06 — layout iteration emitted from roles[0].pullquote)
Gate 3 — <strong>40% → 95%</strong>:       1   (markdownify converted **40% → 95%** correctly)
Gate 4 — about-grid-item count:            4   (4 hobby photos through grid render-image arm)
Gate 4 — about-hero-img count:             1   (hero portrait through layout in-template processing)
Gate 5 — var(--radius-soft) consumers:     5   (UI-SPEC Gate 3 — >=5 required)
Gate 6a — top-level generic class names:   0   (Pitfall 17 — UI-SPEC Gate 9)
Gate 6b — top-level .about- selectors:     0   (every rule prefixed body.page-about — D-12)
Gate 7 — forbidden role-card treatments:   0   (Pitfall 16 — UI-SPEC Gate 4b)
Gate 8 — mobile reflow split rules:        3   (selector group: .about-split, --text-first, --image-first)
Gate 8 — mobile reflow role-list:          1
Gate 8 — mobile reflow role-card:          1
Gate 9 — JS files in About surface:        0   (Pitfall 21 — UI-SPEC Gate 10)
=> ALL_PASS
```

## Pullquote Migration Evidence (REQ ABOUT-06 — UI-SPEC Gate 6 part 1)

```bash
# Markdown SOURCE: roles[0].pullquote: "Improved message routing accuracy from **40% → 95%**"
# Layout: <aside class="about-pullquote">{{ . | markdownify }}</aside>
# Rendered HTML (post hugo --minify):
$ grep -o '<aside class=about-pullquote>[^<]*<strong>[^<]*</strong>[^<]*</aside>' public/about/index.html
<aside class=about-pullquote>Improved message routing accuracy from <strong>40% → 95%</strong></aside>

# Counts:
$ grep -c 'about-pullquote' public/about/index.html         → 1
$ grep -c '<strong>40% → 95%</strong>' public/about/index.html → 1
```

This is byte-equivalent (modulo whitespace/quote-stripping by Hugo's minifier) to the pre-Plan-09-02 raw HTML at content/about/index.md:35-37.

## Hugo Build Command Used

```bash
rm -rf public && hugo --minify
# Exit code: 0
# hugo v0.161.1+extended+withdeploy darwin/amd64 (Homebrew)
# Pages: 16 / Processed images: 46 / Total in 70 ms
```

Pre-existing warnings about `.Site.LanguageCode` / project config key `languageCode` (deprecated in Hugo v0.158.0) are unrelated to this plan and are out of scope per the SCOPE BOUNDARY rule (logged here, not fixed).

## Confirmation: feature shortcode + hook arm + .about-feature CSS still ship as design slack

Per the locked branch decision in 09-01-PLAN/SUMMARY (and reaffirmed by UI-SPEC `[FLAG → recommendation]` + RESEARCH "Risk Hotspots" never-half-ship rule):
- `themes/minimal/layouts/shortcodes/feature.html` — exists, not invoked anywhere in `content/`.
- `feature` render-image hook arm in `themes/minimal/layouts/_default/_markup/render-image.html` — exists, no markdown image titled `"feature"` in tree.
- `.about-feature` and `.about-feature-img` CSS rules — exist (2 rules, 7 declarations), no DOM consumer.

Verified:
```bash
$ grep -rn '{{< feature' content/ → 0 matches
$ grep -rn '"feature"' content/ → 0 matches in image-title position
```

These primitives remain available as ~16 LOC of cheap design slack for HUMAN-UAT-driven follow-ups in 09-03 or beyond. The `.about-feature` selectors match no DOM element until a markdown invocation lands.

## Decisions Made

All decisions were locked in 09-CONTEXT.md (D-01 through D-14) and surfaced into the plan's `<action>` blocks. One micro-decision was made during execution to satisfy a contradiction between the plan's `<action>` template (which used `with .Params.roles`/`range .`) and its acceptance-criteria grep (which required literal `range .Params.roles`):

- **Use `{{ if .Params.roles }}` + `{{ range .Params.roles }}` directly** rather than `{{ with .Params.roles }}` + `{{ range . }}`. Hugo output is equivalent (both iterate the array when present, skip when absent), but the literal greppable text `range .Params.roles` satisfies acceptance criterion verbatim. Documented as a deviation under "Auto-fixed Issues" below.

Key locked decisions reaffirmed by execution:
- **D-08:** `--radius-soft` applied to ≥ 5 selectors (delivered: hero-img, grid-img, role-card, feature, feature-img — exactly 5, gate >=5 PASS).
- **D-09:** Pullquote `border-radius: 0 4px 4px 0` preserved unchanged — NOT swapped to `var(--radius-soft)`.
- **D-12:** Every CSS rule prefixed `body.page-about`. No generic `.card`/`.row`/`.section`/`.feature`/`.role`/`.split` at top level.
- **D-13:** `type: "about"` in markdown frontmatter; no `layout:` field needed (Hugo type lookup auto-routes).
- **D-14:** Raw `<div class="about-hero">` dropped from markdown; layout owns the structural shell.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Layout used `range .` inside `with .Params.roles` instead of `range .Params.roles`**
- **Found during:** Task 1 acceptance gate run.
- **Issue:** The plan's `<action>` template used `{{ with .Params.roles }} … {{ range . }} … {{ end }} {{ end }}` but the acceptance criterion grep was `range .Params.roles` literal (count must equal 1). The first acceptance pass returned 0 for that grep — failing the criterion as written.
- **Fix:** Restructured to `{{ if .Params.roles }} … {{ range .Params.roles }} … {{ end }} {{ end }}` — equivalent Hugo behaviour (both forms iterate when the array exists, skip when nil), but the literal grep contract is now satisfied. Verified by re-running all 16 Task 1 grep gates; all PASS. Verified rendered HTML contains 3 `<li class=about-role-card>` items with all 3 role titles + meta + bullets.
- **Files modified:** themes/minimal/layouts/about/single.html (one block — `with .Params.roles` → `if .Params.roles`, `range .` → `range .Params.roles`).
- **Verification:** `grep -c 'range .Params.roles' themes/minimal/layouts/about/single.html` returns 1; rendered `/about/index.html` contains 3 role-card `<li>` items.
- **Commit hash:** `ea74320` (single Task 1 commit — fix applied before commit).

**Total deviations:** 1 auto-fixed (Rule 1).
**Impact:** Zero. Hugo output is functionally equivalent; the change is purely a textual restructure to satisfy the verbatim grep gate.

## Issues Encountered

None blocking. One pre-existing Hugo warning surfaced during builds (`.Site.LanguageCode` deprecated in v0.158.0) — out of scope for Plan 09-02 per the executor SCOPE BOUNDARY rule; logged here for future cleanup.

## Self-Check: PASSED

- File existence verified:
  - `themes/minimal/layouts/about/single.html` — FOUND
  - `content/about/index.md` — FOUND (modified)
  - `themes/minimal/static/css/style.css` — FOUND (modified)
- Commits verified in `git log`:
  - `ea74320` (Task 1) — FOUND
  - `d5a2774` (Task 2) — FOUND
  - `aa7751e` (Task 3) — FOUND
- All 17 plan-level verification gates PASS (Gates 1-9 from `<verification>` block).
- All 6 ABOUT-* requirements satisfied (ABOUT-01, ABOUT-04, ABOUT-05, ABOUT-06, ABOUT-07 — plus ABOUT-03 token-consumption contract).
- Hugo build exit 0 across two runs.
- Rendered `/about/index.html` contains all expected DOM (3 role cards, 1 pullquote, 1 hero portrait, 4 hobby photos, body class page-about, article class about).

## Notes for Plan 09-03

The build is now ready for the full automated gate suite from UI-SPEC (Gates 2–4a/b, 6a/c/d, 7b, 8, 9, 10, 11) plus HUMAN-UAT scaffolding for the visual-judgment gates (1, 4c, 5, 6b, 7a). Specifically:

- **Automated gates ready:** Gate 2 (Hugo build determinism — `hugo --minify` twice + diff-r), Gate 3 (var(--radius-soft) consumer count), Gate 4a/b (role-card visual contract + forbidden treatments), Gate 6a/c/d (pullquote font-size/font-weight/contrast comment preservation), Gate 7b (mobile @media block contains required selectors), Gate 8 (full hard-coded color audit), Gate 9 (no generic class-name leak), Gate 10 (no JS introduced), Gate 11 (build determinism — twice-built diff).
- **HUMAN-UAT gates pending:** Gate 1 (visual asymmetric layout confirmation), Gate 4c (no leak to /blog/, /gallery/), Gate 5 (content rebalance read-through), Gate 6b (live DevTools dark-mode contrast inspector), Gate 7a (DevTools mobile emulation at 320px).
- **UI-SPEC Gate 2 adaptation note (carry-forward from 09-01-SUMMARY):** the locked render-image hook uses pre-bound boolean variables (`$isSplit`, `$isFeature`) instead of literal `else if eq $title` re-checks. Plan 09-03's Gate 2 should grep for `\$isSplit` (count 3) and `\$isFeature` (count 3) instead of the literal `else if eq $title` pattern.

## Next Phase Readiness

- Plan 09-02 atomic activation landed: layout + content + CSS shipped together; visible delivery now in main.
- Plan 09-03 may now run the full automated gate suite plus HUMAN-UAT for visual-judgment gates.
- No blockers. No concerns. The `.about-feature` CSS rules and `feature` shortcode/hook arm remain as ~16 LOC of design slack — available for follow-ups but matching no DOM until a markdown invocation lands.

---
*Phase: 09-about-dynamic-rounded-redesign*
*Completed: 2026-05-02*

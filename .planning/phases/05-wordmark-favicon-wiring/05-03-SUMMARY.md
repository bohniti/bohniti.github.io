---
phase: 05-wordmark-favicon-wiring
plan: 03
subsystem: hugo-head-wiring
tags:
  - hugo
  - favicon
  - partial
  - html-head
  - wiring
requires:
  - "themes/minimal/static/favicon.ico (Plan 05-01 output, 5.3 KB)"
  - "themes/minimal/static/favicon.svg (Plan 05-01 output, 75.2 KB, PNG-wrapped with embedded prefers-color-scheme dark @media)"
  - "themes/minimal/static/apple-touch-icon.png (Plan 05-01 output, 4.9 KB, 180x180)"
provides:
  - "themes/minimal/layouts/partials/favicon.html — 3 <link> tags emitted into <head>"
  - "themes/minimal/layouts/_default/baseof.html — single-line partial-include between <title> and <meta name=\"description\">"
affects:
  - "Phase 5 verification step — browser tab favicon, bookmark icon, iOS home-screen icon all become resolvable after deploy"
  - "ROADMAP success criteria 3 + 4 (HEAD-04 closed, HEAD-05 closed)"
tech-stack:
  added: []
  patterns:
    - "Hugo partial-emits-raw-HTML (no define/block) — matches header.html / footer.html"
    - "{{ \"<path>\" | absURL }} pipe over hardcoded relative paths — matches baseof.html line 24 stylesheet precedent"
    - "{{ partial \"name.html\" . }} dot-context include — matches baseof.html lines 28, 32"
key-files:
  created:
    - "themes/minimal/layouts/partials/favicon.html"
  modified:
    - "themes/minimal/layouts/_default/baseof.html"
decisions:
  - "Honored D-13: exactly 3 <link> tags in SVG → ICO → apple-touch order; no 4th link, no mstile/manifest/mask-icon"
  - "Honored D-14: partial-include sits between <title> (line 8) and <meta name=\"description\"> (now line 10)"
  - "Honored project absURL idiom: every href piped through {{ \"<path>\" | absURL }}, no hardcoded /favicon.ico or https:// URLs"
  - "Hugo CLI not on PATH locally (matches CLAUDE.md \"Hugo is NOT installed locally\") — local hugo --minify smoke-test deferred to GitHub Actions CI build (Hugo Extended 0.157.0 per .github/workflows/deploy.yml)"
metrics:
  duration: "~111s"
  completed: "2026-04-29"
  tasks_completed: "2/2"
  files_changed: 2
  commits:
    - "2ebab3c: feat(05-03): add favicon partial with 3 <link> tags (D-13)"
    - "1f267b6: feat(05-03): wire favicon partial into baseof.html <head> (D-14)"
---

# Phase 5 Plan 03: Favicon Partial + `<head>` Wiring Summary

**One-liner:** Created the new `themes/minimal/layouts/partials/favicon.html` partial with exactly 3 `<link>` tags (SVG → ICO → apple-touch, all using the `absURL` pipe) and inserted a single `{{ partial "favicon.html" . }}` line into `themes/minimal/layouts/_default/baseof.html` between the existing `<title>` and `<meta name="description">` tags — wiring the 3-file favicon set Plan 05-01 shipped into the rendered HTML `<head>`.

## What Was Built

### `themes/minimal/layouts/partials/favicon.html` (new — 3 lines)

```html
<link rel="icon" type="image/svg+xml" href="{{ "favicon.svg" | absURL }}">
<link rel="icon" type="image/x-icon" href="{{ "favicon.ico" | absURL }}">
<link rel="apple-touch-icon" href="{{ "apple-touch-icon.png" | absURL }}">
```

- Line 1 — SVG first. Modern browsers (Chrome 80+, Firefox 105+, Safari 15+) honor it for tab favicons; the embedded `@media (prefers-color-scheme: dark)` rule from Plan 05-01's PNG-wrapped SVG kicks in there for dark/light tab adaptation.
- Line 2 — ICO fallback. Multi-size 16/32/48 covers legacy tab chrome, Windows shortcut icons, and any browser that doesn't honor SVG favicons.
- Line 3 — apple-touch keyed by `rel`, no `type="..."` attr (per CONTEXT line 94 — optional and not added). iOS Home-Screen "Add to Home Screen" picks this up at 180x180.

No `{{ define }}` / `{{ block }}` wrapper — partials in this project emit raw HTML at top level (matches `header.html` / `footer.html`). No conditional template logic, no inline `<style>` / `<script>`, no 4th `<link>`.

### `themes/minimal/layouts/_default/baseof.html` (modified — +1 line)

Inserted exactly one new line between current line 8 (`<title>`) and current line 9 (`<meta name="description">`):

```html
  <title>{{ if not .IsHome }}{{ .Title }} — {{ end }}{{ .Site.Title }}</title>
  {{ partial "favicon.html" . }}
  <meta name="description" content="{{ with .Description }}{{ . }}{{ else }}{{ .Site.Params.description }}{{ end }}">
```

- 2-space indent matches surrounding `<head>` body
- Trailing dot-context (`.`) passes the page context per the project's existing partial-inclusion idiom (now-lines 28 and 32 of the same file)
- File grew by exactly one line: 57 → 58
- Phase 4 theme bootstrap IIFE (lines 11-23 post-insert), stylesheet `<link>` (line 24), body partials (lines 28, 32), end-of-body toggle handler IIFE (lines 34-56) — all unchanged

## Verification

### Automated checks (all pass)

**Task 1 — `partials/favicon.html`:**

- `test -f themes/minimal/layouts/partials/favicon.html` → exit 0
- `grep -c '^<link ' themes/minimal/layouts/partials/favicon.html` → `3`
- `grep -c ' | absURL }}' themes/minimal/layouts/partials/favicon.html` → `3`
- `grep -cE '\{\{\s*(define|block|if|with|range)' themes/minimal/layouts/partials/favicon.html` → `0`
- `grep -cE 'mstile|manifest|mask-icon' themes/minimal/layouts/partials/favicon.html` → `0`
- Plan 1 `<automated>` block (the compound `test && grep && grep && grep && echo OK` chain) → `OK`
- Line 1 == `<link rel="icon" type="image/svg+xml" href="{{ "favicon.svg" | absURL }}">` (verbatim)
- Line 2 == `<link rel="icon" type="image/x-icon" href="{{ "favicon.ico" | absURL }}">` (verbatim)
- Line 3 == `<link rel="apple-touch-icon" href="{{ "apple-touch-icon.png" | absURL }}">` (verbatim)

**Task 2 — `baseof.html`:**

- `grep -c '{{ partial "favicon.html" . }}' themes/minimal/layouts/_default/baseof.html` → `1`
- `sed -n '9p' themes/minimal/layouts/_default/baseof.html` → `  {{ partial "favicon.html" . }}` (2-space leading indent)
- `sed -n '8p' …` matches `<title>` ✓
- `sed -n '10p' …` matches `<meta name="description"` ✓
- `grep -c "Theme bootstrap — reads localStorage key 'theme'" …` → `1` (Phase 4 IIFE intact)
- `grep -c '<link rel="stylesheet" href="{{ "css/style.css" | absURL }}">' …` → `1` (Phase 4 stylesheet link intact)
- `wc -l < themes/minimal/layouts/_default/baseof.html` → `58` (was 57, +1 as expected)
- Cross-check: `themes/minimal/layouts/partials/favicon.html` exists ✓
- Plan 2 `<automated>` block (the compound `grep | grep && awk` chain) → `OK`

### Plan 05-01 outputs intact (Wave 1 → Wave 2 dependency)

| File                                                | Size    | Status   |
| --------------------------------------------------- | ------- | -------- |
| `themes/minimal/static/favicon.ico`                 | 5413 B  | unchanged |
| `themes/minimal/static/favicon.svg`                 | 77001 B | unchanged |
| `themes/minimal/static/apple-touch-icon.png`        | 5026 B  | unchanged |

All 3 files referenced by the new partial physically exist on disk in this worktree (verified before and after Task 1+2 commits).

### Local Hugo build (deferred to CI)

`command -v hugo` returns nothing on this dev machine — matches CLAUDE.md "Hugo is NOT installed locally; development may rely on another install method or Docker." Per Task 2 action step 4 ("If `hugo` IS available locally … if `hugo` is NOT on PATH, document this in the SUMMARY and rely on the GitHub Actions CI build"), the end-to-end build smoke-test is deferred to:

- `.github/workflows/deploy.yml` Hugo Extended **0.157.0** build on push to `main`
- Manual visual checks after deploy: browser tab favicon on `/` shows the TB mark (not generic Hugo / browser default); bookmark icon shows the TB mark; iOS "Add to Home Screen" produces a 180×180 TB icon

These post-deploy visual checks are explicitly listed under `<verification>` ("Post-deploy manual checks (deferred to verification phase)") and under the plan's `<specifics>` section ("After deploy, manually validate the favicon set on at least: Chrome desktop tab, Safari iOS tab, iOS Add-to-Home-Screen"). They are out of scope for the executor and into scope for the phase verifier (or Timo's manual visual sweep).

## Deviations from Plan

None — plan executed exactly as written. No bugs found, no missing critical functionality, no blockers, no architectural decisions needed. The Hugo-CLI-not-on-PATH situation is documented in the plan itself (Task 2 action step 4 explicitly contemplates this case and defers to CI).

## Authentication Gates

None — this plan is local template-file work; no auth required.

## CLAUDE.md Compliance

- **Tech stack constraint** ("Hugo static site, no JS frameworks, keep it minimal"): satisfied. The new partial is 3 lines of static HTML with Hugo template pipe expressions; no JS added, no framework introduced. The `baseof.html` change is one line.
- **Theme constraint** ("Must fit the existing Flexoki-inspired minimal aesthetic"): N/A at the HTML-head level; favicon visual rendering is governed by the assets Plan 05-01 produced. The `favicon.svg` already embeds Flexoki-tracked dark/light variants via `@media (prefers-color-scheme: dark)`.
- **HTML Template Conventions** (`baseof.html` is the base layout with `<head>` and `<body>`): preserved. The single-line insertion does not touch the `{{ block "main" . }}` placeholder, the `<header>`/`<main>`/`<footer>` partial pattern, or any `define`/`block` markers.
- **GSD Workflow Enforcement**: this work landed via `/gsd:execute-phase` Wave 2 executor — within the GSD workflow.

## Self-Check: PASSED

- File `themes/minimal/layouts/partials/favicon.html` — FOUND (3 lines, 3 `<link>` tags)
- File `themes/minimal/layouts/_default/baseof.html` — FOUND (modified, 58 lines)
- File `themes/minimal/static/favicon.ico` — FOUND (5413 bytes, Plan 05-01)
- File `themes/minimal/static/favicon.svg` — FOUND (77001 bytes, Plan 05-01)
- File `themes/minimal/static/apple-touch-icon.png` — FOUND (5026 bytes, Plan 05-01)
- Commit `2ebab3c` (Task 1: favicon partial creation) — FOUND
- Commit `1f267b6` (Task 2: baseof.html wiring) — FOUND

## TDD Gate Compliance

Not applicable — `tdd="false"` on both tasks. This plan is HTML-template wiring (a 3-line partial creation + a single-line include insertion) — there is no behavioral surface to test in unit form. End-to-end validation comes from the CI Hugo build + post-deploy visual checks.

## Threat Surface Scan

No new threat surface introduced beyond the threat model in `05-03-PLAN.md`:

- T-05-04 (Cross-Site-Scripting via `<link href="…">`) — accepted; all 3 hrefs are hardcoded relative paths (`favicon.svg`, `favicon.ico`, `apple-touch-icon.png`) piped through Hugo's `absURL`. No user input, no template binding to dynamic data, no XSS surface.

The 3 `<link>` tags reference public static assets shipped by Plan 05-01. No new network endpoints, no new auth paths, no new file-access patterns at trust boundaries. The partial-include line in `baseof.html` is a Hugo template pipe expression with hardcoded partial name — no dynamic dispatch, no path traversal surface.

## Known Stubs

None — every `<link>` tag points at a real, on-disk file shipped by Plan 05-01. The partial is fully wired into the active head layout.

## Requirements Touched

- **HEAD-04** — closed: 3-file favicon set wired into `<head>`. Plan 05-01 shipped the assets; this plan ships the references. Browsers will now request and render `favicon.ico`, `favicon.svg`, and `apple-touch-icon.png` on every page visit.
- **HEAD-05** — closed: `<link>` tags live in the new `themes/minimal/layouts/partials/favicon.html` partial (NOT inlined in `baseof.html`); the partial is included from `baseof.html` `<head>` immediately after `<title>` per ROADMAP success criterion 3 verbatim.

## Success Criteria Status

- ROADMAP success criterion 3 ("exactly 3 `<link>` tags … `favicon.ico` (32-multi), `favicon.svg` (with embedded `@media (prefers-color-scheme: dark)`), `apple-touch-icon.png` (180×180) — included from `baseof.html` `<head>` immediately after the `<title>`"): **satisfied verbatim**.
- ROADMAP success criterion 4 ("post-deploy: browser tab favicon resolves to TB mark, not generic Hugo / browser default"): **structurally satisfied** at template level; final visual confirmation deferred to post-deploy visual sweep.

## Cross-Phase Contracts

This plan honors the **Plan 05-01 → Plan 05-03** consumer contract:

- Plan 05-01 shipped `favicon.{ico,svg}` and `apple-touch-icon.png` at `themes/minimal/static/` (D-12)
- Hugo serves theme static root at site root, so `{{ "favicon.svg" | absURL }}` resolves to e.g. `https://tbohnstedt.cloud/favicon.svg` in production and `/favicon.svg` in dev
- This plan creates the 3 `<link>` tags that exactly reference those 3 paths, with no rename, no path drift, no version mismatch

The cross-phase contract is closed — Phase 5's favicon track (Plans 05-01 + 05-03) is now end-to-end wired. The wordmark track (Plan 05-02, parallel Wave 2) is independent and does not conflict with this plan's file edits.

## Next Plan

Wave 2 wraps after Plans 05-02 (wordmark) and 05-03 (favicon wiring) both complete. The orchestrator will then run phase verification (visual-check checkpoint covering wordmark image swap on theme toggle + favicon visibility in tab/bookmark) and transition to Phase 6 (Gallery).

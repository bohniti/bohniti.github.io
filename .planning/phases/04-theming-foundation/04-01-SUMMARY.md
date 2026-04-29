---
phase: 04-theming-foundation
plan: 01
subsystem: theming
tags:
  - hugo
  - css
  - theming
  - flexoki
  - dark-mode
  - accessibility
  - reduced-motion
requirements:
  - THEME-04
  - THEME-03
dependency_graph:
  requires: []
  provides:
    - ":root[data-theme=\"dark\"] palette block (11 Flexoki dark tokens)"
    - "@media (prefers-reduced-motion: no-preference) body transition rule"
    - ".theme-toggle button rule (typography matched to .site-nav a)"
    - ".theme-toggle:hover rule"
    - ".site-nav a:focus-visible, .theme-toggle:focus-visible combined outline rule"
  affects:
    - "Plan 02 (head IIFE) — IIFE writes [data-theme] on <html>; this plan supplies the palette it flips"
    - "Plan 03 (toggle button + click handler) — uses .theme-toggle class; click handler flips [data-theme]"
tech_stack:
  added: []
  patterns:
    - "CSS custom-property cascade for theming (no hardcoded hex outside :root blocks)"
    - "Attribute-selector :root[data-theme=\"dark\"] for theme override"
    - "Media-query-gated transition rule (prefers-reduced-motion: no-preference) for structural reduced-motion compliance"
    - ":focus-visible outline using existing token (var(--accent))"
key_files:
  created: []
  modified:
    - themes/minimal/static/css/style.css
key_decisions:
  - "Used Flexoki Black #100F0F for dark --bg (not #000000 from Phase 3 corner-pixel hex contract) per D-01/D-02"
  - "Omitted --max-width from dark block per D-04 (theme-agnostic, lives only at un-attributed :root)"
  - "Reduced-motion handled structurally via @media (prefers-reduced-motion: no-preference) gate per D-10 (no transition: none override)"
  - "Combined .site-nav a + .theme-toggle focus-visible into one rule (UI-SPEC § Focus-visible Policy) — minimal scope expansion, capped at nav links + toggle"
  - "font: inherit ordered before font-size: 0.95rem in .theme-toggle to prevent shorthand from clobbering the explicit override"
metrics:
  duration_seconds: 97
  duration_human: "1m 37s"
  tasks_completed: 3
  files_modified: 1
  lines_added: 47
  completed: 2026-04-29
commits:
  - hash: ca4df7c
    message: "feat(04-01): add Flexoki dark palette under :root[data-theme=\"dark\"]"
  - hash: 19933da
    message: "feat(04-01): add prefers-reduced-motion-gated body transition"
  - hash: f8fd614
    message: "feat(04-01): add .theme-toggle button rules and focus-visible outline"
---

# Phase 4 Plan 01: Dark Palette + Body Transition + Toggle Styling Summary

CSS-only foundation for Phase 4 theming: adds the Flexoki dark palette under `:root[data-theme="dark"]`, a reduced-motion-gated 150ms body color transition, and the `.theme-toggle` button styling (typography matched to `.site-nav a`, with a combined focus-visible outline shared with nav links).

## Objective Recap

Establish the structural CSS foundation for Phase 4. Plans 02 and 03 will wire it: Plan 02's IIFE writes `[data-theme]` on `<html>` before first paint; Plan 03's click handler flips it on user interaction. This plan ships the visual contract — the palette tokens, the transition rule, and the button styling — without any JS or template changes.

## What Changed

### `themes/minimal/static/css/style.css` (+47 lines, 264 → 311)

| Block | Lines added | Position | Section |
|-------|-------------|----------|---------|
| `:root[data-theme="dark"]` (11 tokens + 2 framing lines + 1 comment + 1 blank separator) | +15 | After light `:root` (was line 18, now line 19-33) | Reset & Base |
| `@media (prefers-reduced-motion: no-preference) { body { transition: ... } }` | +9 | After body rule, before `=== Layout ===` header | Reset & Base |
| `.theme-toggle` rule + `:hover` + combined `:focus-visible` | +23 | After `.site-nav a:hover`, before `=== Post List ===` header | Header |
| **Total** | **+47** | | |

**Light `:root` block is byte-identical** to its pre-edit state (verified via `grep -c "^  --bg: #FFFCF0;$"` returns 1, all 12 light tokens still present at original positions, lines 4-18).

### Tokens defined under `:root[data-theme="dark"]`

| Token | Light hex | Dark hex | Flexoki name (dark) |
|-------|-----------|----------|---------------------|
| `--bg` | `#FFFCF0` | `#100F0F` | Black |
| `--bg-secondary` | `#F2F0E5` | `#1C1B1A` | Base950 |
| `--text` | `#100F0F` | `#CECDC3` | Base200 |
| `--text-secondary` | `#6F6E69` | `#878580` | Base500 |
| `--text-muted` | `#B7B5AC` | `#575653` | Base700 |
| `--accent` | `#AF3029` | `#D14D41` | Red400 |
| `--accent-hover` | `#D14D41` | `#DA7E76` | Red300 |
| `--link` | `#AF3029` | `#D14D41` | Red400 |
| `--link-hover` | `#D14D41` | `#DA7E76` | Red300 |
| `--border` | `#E6E4D9` | `#282726` | Base900 |
| `--code-bg` | `#F2F0E5` | `#1C1B1A` | Base950 |

`--max-width: 640px` lives only at the un-attributed `:root` (theme-agnostic per D-04).

### Body transition rule

```css
@media (prefers-reduced-motion: no-preference) {
  body {
    transition:
      background-color 150ms ease,
      color            150ms ease,
      border-color     150ms ease;
  }
}
```

Structural reduced-motion compliance: under `prefers-reduced-motion: reduce`, the `@media (prefers-reduced-motion: no-preference)` block does not match, so the rule is not loaded — theme switch is structurally instant, not via a `transition: none` override.

### `.theme-toggle` button rules

```css
.theme-toggle {
  /* match .site-nav a typography (D-08) */
  font: inherit;
  font-size: 0.95rem;
  color: var(--text-secondary);
  /* button reset */
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.theme-toggle:hover {
  color: var(--accent);
}

.site-nav a:focus-visible,
.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```

`font: inherit` precedes `font-size: 0.95rem` deliberately — the inherit shorthand resets font-size to the default, so the explicit `font-size` MUST come after it to take effect.

## Success Criteria Verification

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `:root[data-theme="dark"]` block with all 11 Flexoki dark tokens at locked hex values | PASS (all 11 grep checks succeed) |
| 2 | `--max-width` defined ONLY in light `:root` (not in dark block) | PASS (`! grep -A 14 ":root\[data-theme=\"dark\"\]" ... \| grep -q max-width`) |
| 3 | Light `:root` block byte-identical to pre-edit baseline | PASS (`grep -c "^  --bg: #FFFCF0;$"` returns 1; all 12 light tokens present unchanged) |
| 4 | `@media (prefers-reduced-motion: no-preference)` block with body transition referencing `background-color`, `color`, `border-color` over `150ms ease` | PASS (all 3 transition declarations present, `no-preference` gate confirmed, no `reduce` form used) |
| 5 | `.theme-toggle` rule with `font: inherit; font-size: 0.95rem; color: var(--text-secondary); background: transparent; border: 0; padding: 0; cursor: pointer;` (font: inherit precedes font-size) | PASS (ordering verified via awk on the rule block) |
| 6 | `.theme-toggle:hover` rule sets `color: var(--accent)` | PASS |
| 7 | Combined `.site-nav a:focus-visible, .theme-toggle:focus-visible` rule with `outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px;` | PASS (both selectors and all 3 declarations present) |
| 8 | No out-of-scope focus-visible selectors (`.site-title a`, `.page-content a`, `.post-item-title a`, `.site-footer a`) | PASS (4 negative greps all confirm absence) |
| 9 | No `transition: all` and no `*` selector with transitions | PASS (`! grep -q "transition: all"`; no `*`-with-transition rule) |
| 10 | Braces balance | PASS (`awk '/\{/{n++} /\}/{n--} END{exit (n == 0) ? 0 : 1}'` returns 0) |

## Hardcoded Hex Audit

`grep -nE "#[0-9A-Fa-f]{6}" themes/minimal/static/css/style.css` returns 22 lines — all inside the two `:root` blocks (lines 6-16 light, 22-32 dark). Zero violations of CSS custom-property discipline (no hardcoded hex outside the token blocks).

## Deviations from Plan

None. Every value was locked by D-01..D-16 in CONTEXT.md and the UI-SPEC; the executor copied each block verbatim from the plan's `<action>` section. No bugs encountered, no missing functionality detected, no architectural decisions required.

## Authentication Gates

None — pure CSS edits; no auth, no network, no external dependencies.

## Threat Flags

None. The threat model in the plan (T-04-01..T-04-04) accepts all risks at the CSS layer; this plan introduced no new attack surface beyond what was anticipated. No new endpoints, schema changes, or trust boundaries.

## Cross-Phase Contract Outgoing

Confirmed for Plans 02 and 03 in the same phase:

- **Plan 02 (head IIFE):** the IIFE will set `document.documentElement.dataset.theme = 'dark' | 'light'`. The CSS in this plan keys off exactly that attribute (`:root[data-theme="dark"]`).
- **Plan 03 (toggle button + click handler):** the click handler will mutate the same `[data-theme]` attribute. The button uses class `theme-toggle`, which now has its full styling contract (resting + hover + focus-visible). The handler does not need to add any class or inline style — the CSS is fully wired.

Confirmed for Phase 5:

- The `[data-theme]` attribute is on `<html>` (`document.documentElement`), so Phase 5's wordmark CSS can write `html[data-theme="dark"] .wordmark { ... }` directly, no JS swap needed.

## Self-Check: PASSED

- File `themes/minimal/static/css/style.css` exists (311 lines, was 264).
- Commit `ca4df7c` exists in `git log --oneline` (Task 1: dark palette block).
- Commit `19933da` exists in `git log --oneline` (Task 2: body transition).
- Commit `f8fd614` exists in `git log --oneline` (Task 3: theme-toggle + focus-visible).
- All 10 success criteria verified above.
- No deferred items. No deferred-items.md update needed.

---
phase: 04-theming-foundation
plan: 03
subsystem: theming
tags:
  - hugo
  - html
  - javascript
  - theming
  - accessibility
  - aria
  - localStorage
  - smoke-test
requirements:
  - THEME-01
  - THEME-03
  - THEME-06
dependency-graph:
  requires:
    - "Plan 04-01 (CSS palette + transition + .theme-toggle button styling + focus-visible outline)"
    - "Plan 04-02 (head IIFE writing document.documentElement.dataset.theme; <meta name=\"theme-color\"> anchor; localStorage key 'theme' contract)"
  provides:
    - "Server-rendered <button class=\"theme-toggle\" aria-pressed=\"false\">Dark</button> as last child of nav.site-nav on every page"
    - "End-of-body inline IIFE: first-paint button-sync (textContent + aria-pressed match resolved data-theme) + single click listener performing five atomic mutations (data-theme, aria-pressed, textContent, localStorage, theme-color meta)"
    - "Human-verified THEME-06 smoke-test outcome on /blog/2026-03-05-climbing-routes/ (Mermaid + Plotly + Leaflet readable in dark mode; no-FOUC; persistence; keyboard a11y; reduced-motion all confirmed)"
  affects:
    - "Phase 5 (wordmark/favicon) — html[data-theme=\"dark\"] selector now toggles at runtime via the click handler shipped here, not just at first paint"
    - "Future themable embeds — any new inline-script visualization (Mermaid/Plotly/Leaflet additions) inherits the same Flexoki-token base; readability is currently acceptable without per-library reactivity"
tech-stack:
  added: []
  patterns:
    - "Single-IIFE pattern co-locating first-paint sync and click handler (mirrors head IIFE style from Plan 04-02)"
    - "Atomic-mutation click handler — all five side effects (DOM attr, ARIA attr, text, storage, meta) live in one function so they cannot desync"
    - "Server-rendered initial button state with JS-driven first-paint correction — accessibility-first (button is keyboard-reachable and announces a sensible label even before JS runs) while still honoring stored user preference"
    - "localStorage write guarded by try/catch (Safari private mode parity with the head IIFE read)"
    - "Allowlist-by-construction for theme-color meta content — only two literal hex strings (#100F0F / #FFFCF0) ever flow into setAttribute (T-04-11 mitigation)"
key-files:
  created: []
  modified:
    - themes/minimal/layouts/partials/header.html
    - themes/minimal/layouts/_default/baseof.html
key-decisions:
  - "Co-located first-paint button-sync and click handler in one IIFE — keeps the two writes that touch the same DOM element side-by-side and avoids a second querySelector on the same selector"
  - "Used the dark-first conditional form (next === 'dark' ? '#100F0F' : '#FFFCF0' and 'Light' : 'Dark') across all three writes inside the click handler to keep the script visually parallel with the head IIFE's pattern in Plan 04-02"
  - "Did NOT add DOMContentLoaded — the script is at end of body, so the toggle button is already parsed; the listener attaches synchronously"
  - "Did NOT factor the five mutations into helper functions — kept inline so the atomic-side-effect contract is locally readable (CONTEXT.md § Specifics paragraph 2)"
patterns-established:
  - "End-of-body inline JS for DOM-touching code that needs the parser to have reached the relevant elements (vs. head IIFE for pre-paint)"
  - "Toggle UI pattern for the project: real <button> + visible text + aria-pressed (no icons, no aria-label, no tabindex hacks)"
metrics:
  duration_seconds: 60
  duration_human: "~1m (Tasks 1+2 commits 9:17:24 → 9:18:05; checkpoint resolved out-of-band)"
  tasks_completed: 3
  files_modified: 2
  lines_added: 24
  completed: "2026-04-29"
commits:
  - hash: 7655528
    message: "feat(04-03): append theme-toggle button to .site-nav in header.html"
  - hash: 396e133
    message: "feat(04-03): add end-of-body toggle click handler IIFE in baseof.html"
---

# Phase 4 Plan 03: End-to-End Theming Wiring Summary

**Server-rendered theme-toggle button + single end-of-body IIFE that performs first-paint sync and atomically flips data-theme / aria-pressed / textContent / localStorage / theme-color meta on each click; human-verified Mermaid/Plotly/Leaflet readability in dark mode on the canary blog post.**

## Performance

- **Duration:** ~1 min for the two automated tasks (Task 1 commit 9:17:24, Task 2 commit 9:18:05); the human-verify checkpoint between Task 2 and finalization was resolved out-of-band by the user.
- **Tasks:** 3 (2 automated + 1 human-verify checkpoint)
- **Files modified:** 2

## Accomplishments

- The toggle button is now wired end-to-end across every page: visible in the header nav, keyboard-reachable, persists to localStorage, and updates iOS Safari chrome on click.
- The single click handler performs all five mutations atomically — the five side effects can never desync because they share one function body.
- The first-paint button-sync routine corrects the server-rendered "Dark" / `aria-pressed="false"` to "Light" / `aria-pressed="true"` when the head IIFE resolved dark, using the `data-theme` attribute as the single source of truth (no second localStorage read).
- The human-verified smoke-test on `/blog/2026-03-05-climbing-routes/` confirmed Mermaid + Plotly + Leaflet are all readable in dark mode with no console errors.

## Task Commits

1. **Task 1: Append the theme-toggle button to .site-nav in header.html** — `7655528` (feat)
2. **Task 2: Add end-of-body inline script with DOM-ready button-sync and click handler** — `396e133` (feat)
3. **Task 3: Human smoke-test of dark mode on the canary blog post (THEME-06)** — no commit (manual verification only; user response: "approved")

**Plan metadata:** _committed in this finalization step (`docs(04-03): complete theming end-to-end wiring plan`)._

## Files Created/Modified

### `themes/minimal/layouts/partials/header.html` (+1 line, 10 → 11)

Appended exactly one line as the last child of `nav.site-nav`, after the `{{ end }}` of the menu loop and before `</nav>`:

```html
<button type="button" class="theme-toggle" aria-pressed="false">Dark</button>
```

Constraints honored:

- `<button>` element (not `<a>`, not `<div>`, not a span with role)
- `type="button"` explicit (defensive against form-context submit)
- Single class `theme-toggle` (no utility classes)
- Static initial `aria-pressed="false"` (Task 2's first-paint sync corrects to `"true"` if head IIFE resolved dark)
- Visible text exactly `Dark` (4 chars, capitalized, no trailing space, no localization)
- No `aria-label`, no `title`, no `id`, no `tabindex`, no Hugo template logic inside the button

### `themes/minimal/layouts/_default/baseof.html` (+23 lines, 34 → 57)

Inserted a second `<script>` block immediately before `</body>` (the head IIFE from Plan 02 at lines 10-22 is byte-unchanged):

```html
<script>
  // Theme toggle — single click handler performs five atomic mutations.
  (function () {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    const meta = document.querySelector('meta[name="theme-color"]');

    // First-paint sync: server-rendered HTML always says "Dark"/aria-pressed="false".
    // If the head IIFE resolved dark, update the button to match.
    const initial = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
    toggle.setAttribute('aria-pressed', initial === 'dark' ? 'true' : 'false');
    toggle.textContent = initial === 'dark' ? 'Light' : 'Dark';

    toggle.addEventListener('click', function () {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      toggle.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
      toggle.textContent = next === 'dark' ? 'Light' : 'Dark';
      try { localStorage.setItem('theme', next); } catch (_) { /* Safari private mode */ }
      if (meta) meta.setAttribute('content', next === 'dark' ? '#100F0F' : '#FFFCF0');
    });
  })();
</script>
```

Final script count in `baseof.html`: **2** (head IIFE from Plan 02 + this end-of-body IIFE).

Constraints honored:

- IIFE form `(function () { ... })();` matches head-IIFE style (Plan 02)
- `const` for all four variables (`toggle`, `meta`, `initial`, `next`); no `var`
- Button text strictly swaps between `Light` and `Dark` (4 chars each, capitalized)
- `aria-pressed` set via `setAttribute` (literal strings `'true'` / `'false'`)
- `theme-color` content uses ONLY the two locked literal hex strings (`#100F0F`, `#FFFCF0`); zero user-controlled flow into `setAttribute`
- `localStorage.setItem('theme', next)` wrapped in `try { ... } catch (_) { ... }` for Safari private mode
- All five mutations live in one function body; not split into multiple listeners or helpers
- No `console.log`, no `onclick=` inline attribute, no `DOMContentLoaded` listener (script sits at end-of-body)
- No Hugo `{{ ... }}` template variables inside the script body
- Head IIFE from Plan 02 (lines 10-22) byte-unchanged

## THEME-06 Smoke-Test Result (Task 3)

The smoke-test was performed by the user on `/blog/2026-03-05-climbing-routes/` per the `<how-to-verify>` steps in the PLAN. User response on the human-verify checkpoint:

> "approved — smoke-test passed. Mermaid/Plotly/Leaflet all readable in dark mode, no-FOUC, persistence, keyboard a11y, reduced-motion all confirmed. No console errors. No deferred items to log."

Pass criteria (all confirmed by the user):

| Pass criterion | Status |
|----------------|--------|
| Mermaid diagram text legible in dark mode | PASS (user confirmed) |
| Plotly chart axes and labels legible | PASS (user confirmed) |
| Leaflet map functions (tiles rendered, accepted compromise on tile theme-match) | PASS (user confirmed) |
| No-FOUC verified under hard reload in dark mode | PASS (user confirmed) |
| Toggle works via mouse, keyboard, Tab+Enter, Tab+Space | PASS (user confirmed) |
| Reduced-motion makes the switch instant | PASS (user confirmed) |
| No console errors on click | PASS (user confirmed) |

No deferred-ideas items logged for v2.x — the user explicitly noted "No deferred items to log."

## Success Criteria Verification

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `header.html` contains exactly one button with markup `<button type="button" class="theme-toggle" aria-pressed="false">Dark</button>` as last child of `nav.site-nav` | PASS |
| 2 | `baseof.html` contains exactly two `<script>` blocks (head IIFE from Plan 02 + new end-of-body IIFE) | PASS |
| 3 | End-of-body script queries `.theme-toggle` once, attaches exactly one click listener, performs all five mutations in a single click handler | PASS |
| 4 | localStorage key `'theme'` consistent across head IIFE and click handler | PASS |
| 5 | theme-color meta written ONLY with `'#100F0F'` or `'#FFFCF0'` | PASS |
| 6 | No `var`, no `console.log`, no `onclick=`, no `DOMContentLoaded` | PASS |
| 7 | `localStorage.setItem` wrapped in try/catch | PASS |
| 8 | First-paint button-sync routine lives in same IIFE as click handler | PASS |
| 9 | THEME-06 smoke-test approved by human checker (no blocking readability issues) | PASS (user response: "approved — smoke-test passed") |
| 10 | Body of `baseof.html` unchanged outside new end-of-body script (header partial, main block, footer partial all preserved) | PASS |

## Decisions Made

- Co-located first-paint sync and click handler in one IIFE (single `querySelector('.theme-toggle')`, single closure, single conceptual unit).
- Adopted dark-first conditional form (`next === 'dark' ? '#100F0F' : '#FFFCF0'`, `'Light' : 'Dark'`) to keep the click handler visually parallel with the head IIFE's pattern from Plan 02.
- Did not add a `DOMContentLoaded` listener — the script sits at end-of-body, so the parser has already reached the toggle button by the time the script runs.
- Did not factor the five mutations into named helper functions — keeping them inline preserves the local readability of the atomic-side-effect contract called out in CONTEXT.md § Specifics paragraph 2.

## Deviations from Plan

None — plan executed exactly as written. Both Task 1 and Task 2 were committed verbatim from the plan's `<action>` blocks. Task 3 was a manual checkpoint resolved by the user with an unconditional "approved".

**Total deviations:** 0
**Impact on plan:** None.

## Authentication Gates

None encountered. This plan involves only template-file edits and a manual smoke-test; no auth, no network, no external services.

## Issues Encountered

None.

## Threat Model Compliance

| Threat ID | Disposition | Mitigation Implemented |
|-----------|-------------|------------------------|
| T-04-10 (Tampering — localStorage write) | mitigate | The click handler computes `next` only as `'light'` or `'dark'` based on the current `data-theme` value; no external input path. Two literal strings are the only values ever written. (Pairs with T-04-05 from Plan 02 — IIFE sanitizes on read.) |
| T-04-11 (Tampering — theme-color meta content) | mitigate | The handler writes ONLY one of two literal hex strings (`#100F0F` / `#FFFCF0`) via `setAttribute`; no user input flows into the meta content. (Pairs with T-04-06 from Plan 02.) |
| T-04-12 (Spoofing — aria-pressed value) | accept | A malicious browser extension could mutate aria-pressed, but the user's AT reads the live DOM, so the handler's writes are authoritative. No app-layer mitigation needed. |
| T-04-13 (Information Disclosure — toggle source visible in HTML) | accept | Public-by-design (same rationale as T-04-07). |
| T-04-14 (DoS — click flood) | accept | Each click performs five cheap DOM ops; no debouncing needed. |
| T-04-15 (Repudiation — theme choice attribution) | accept | Theme choice is per-device (localStorage), not tied to any account. |

All `mitigate` dispositions are structurally enforced by the implementation; no runtime checks were skipped.

## Threat Flags

None. The implementation introduced no new attack surface beyond what was anticipated by the plan's threat model. No new endpoints, schema changes, file-access patterns, or auth paths.

## Known Stubs

None. The toggle is fully wired end-to-end (button → click handler → DOM/localStorage/meta update); no placeholder text, no hardcoded empty values, no TODO markers.

## Cross-Phase Outgoing Contracts (still satisfied)

- **To Phase 5 (wordmark + favicon):** `[data-theme]` on `<html>` now flips at runtime via the click handler shipped here (was first-paint-only after Plan 02). Phase 5's wordmark CSS selectors `html[data-theme="dark"] .wordmark { ... }` will respond live to user toggles, no JS swap needed.
- **To future plans:** localStorage key `'theme'` is anchored across the head IIFE (Plan 02) and the click handler (this plan); any future cross-tab `storage` event listener (Future Requirement) keys off the same name.

## Phase Readiness

Phase 4 (theming-foundation) is fully shipped end-to-end:

- Plan 04-01 — CSS palette + transition + `.theme-toggle` styling
- Plan 04-02 — head IIFE + `color-scheme` and `theme-color` meta tags
- Plan 04-03 — toggle button markup + click handler + human-verified smoke-test

Ready for phase verification / completion via the orchestrator. No blockers, no deferred items, no follow-ups beyond the Future Requirements explicitly out-of-scope (cross-tab sync, view-transition cross-fade, per-library reactivity, PWA manifest, three-state toggle).

## Self-Check: PASSED

**Files:**
- `themes/minimal/layouts/partials/header.html` — FOUND (11 lines; verified contains `<button type="button" class="theme-toggle" aria-pressed="false">Dark</button>` as last child of nav.site-nav).
- `themes/minimal/layouts/_default/baseof.html` — FOUND (57 lines; verified contains 2 `<script>` blocks, head IIFE from Plan 02 unchanged, new end-of-body IIFE with single `addEventListener` call).

**Commits (verified via `git log --oneline`):**
- `7655528` — `feat(04-03): append theme-toggle button to .site-nav in header.html` — FOUND
- `396e133` — `feat(04-03): add end-of-body toggle click handler IIFE in baseof.html` — FOUND

**Checkpoint resolution:**
- Task 3 (`checkpoint:human-verify`) — user response "approved — smoke-test passed" — RESOLVED PASS

All claimed files and commits exist. No claim is missing.

---
*Phase: 04-theming-foundation*
*Completed: 2026-04-29*

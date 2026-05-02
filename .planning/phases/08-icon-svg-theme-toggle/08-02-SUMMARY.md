---
phase: 08-icon-svg-theme-toggle
plan: 02
subsystem: ui
tags: [hugo, vanilla-js, accessibility, localstorage, theme-toggle]

# Dependency graph
requires:
  - phase: 08-icon-svg-theme-toggle
    plan: 01
    provides: ".theme-toggle button now contains two SVGs (sun + moon) with initial aria-label='Switch to dark mode' and aria-pressed='false'; CSS visibility swap keyed off [data-theme]"
  - phase: 04-theme-toggle
    provides: "Head IIFE that sets documentElement.dataset.theme before the stylesheet loads (no-FOUC bootstrap)"
provides:
  - "Rewritten end-of-body click handler IIFE — aria-label-driven toggle that announces target action to screen readers"
  - "First-paint reconciliation of aria-pressed AND aria-label (mirrors v2.0 textContent reconciliation pattern)"
  - "Atomic 5-mutation click handler: dataset.theme write → aria-pressed → aria-label → localStorage (try/catch) → meta[name=theme-color] content sync"
affects: [09-about-page, 10-gallery-lightbox]

# Tech tracking
tech-stack:
  added: []   # zero new deps; vanilla JS in inline IIFE preserved
  patterns:
    - "Action-oriented aria-label updated atomically with documentElement.dataset.theme — JS describes the click target, not the current state (D-08)"
    - "aria-pressed continues to report current state ('true' for dark, 'false' for light) — preserved verbatim from v2.0 (D-09)"
    - "JS writes ONLY documentElement.dataset.theme + button attributes + meta theme-color + localStorage — never touches the SVG icons (D-10, Pitfall 22 mitigation)"
    - "First-paint reconciliation block keeps server-rendered defaults (aria-pressed=false, aria-label='Switch to dark mode') in sync with whatever theme the head IIFE resolved"

key-files:
  created: []
  modified:
    - "themes/minimal/layouts/_default/baseof.html (8 insertions, 5 deletions; net 23-line IIFE → 25-line IIFE — two textContent assignments swapped for aria-label setAttribute calls + 4-line comment update describing new responsibility set)"

key-decisions:
  - "Updated the IIFE preamble comment to call out the new contract explicitly: 'JS writes only documentElement.dataset.theme; CSS reads it (icon visibility, palette swap). aria-label is action-oriented' — keeps future-readers from re-introducing imperative SVG mutation"
  - "Kept the existing 'First-paint sync' comment in place (verbatim intent from v2.0, only the trailing example string updated to reference aria-label) — preserves the architectural rationale for the reconciliation block"
  - "Did NOT touch the head IIFE at lines 11-23 — verified byte-identical to v2.0 snapshot via diff (Pitfall 1 / no-FOUC contract preserved)"

patterns-established:
  - "Aria-label-driven toggle button — accessible name describes target action, aria-pressed describes current state, icon depicts current state. Reusable pattern for any future icon-only toggle pair."
  - "Single-source-of-truth dataset.theme write cascades through palette + icon visibility (CSS) + meta theme-color (JS-synced) + button a11y attributes (JS-synced) — zero divergent state paths."

requirements-completed: [ICON-02, ICON-03]

# Metrics
duration: 1min
completed: 2026-05-02
---

# Phase 8 Plan 2: Rewrite Theme-Toggle IIFE — Aria-Label Setter Replaces TextContent Summary

**Two `toggle.textContent = …` lines removed from the end-of-body IIFE, replaced with `toggle.setAttribute('aria-label', …)` calls using action-oriented strings ('Switch to dark mode' / 'Switch to light mode'); all other v2.0 IIFE responsibilities (dataset.theme write, aria-pressed sync, localStorage in try/catch, meta theme-color content sync) preserved verbatim — head IIFE untouched (Pitfall 1 byte-identical).**

## Performance

- **Duration:** ~1 min (single Edit + verification + commit)
- **Started:** 2026-05-02T08:32:02Z
- **Completed:** 2026-05-02T08:33:29Z
- **Tasks:** 1 (`auto`, no TDD)
- **Files modified:** 1

## Accomplishments

- The end-of-body IIFE at `themes/minimal/layouts/_default/baseof.html` lines 34-58 now mutates **only** the button's accessibility attributes (`aria-pressed`, `aria-label`), `documentElement.dataset.theme`, `localStorage.theme`, and `meta[name="theme-color"]` content — never touches the inner SVG icons (D-10, Pitfall 22 mitigation gated by grep).
- Two `setAttribute('aria-label', …)` calls land at the exact two positions the removed `textContent` lines occupied: one in the first-paint reconciliation block (mirroring the existing `aria-pressed` reconciliation), one inside the click handler (atomic with the `dataset.theme` write).
- Aria-label values are the four exact action-oriented strings from UI-SPEC §Copywriting Contract: `'Switch to dark mode'` (light active → click goes to dark) and `'Switch to light mode'` (dark active → click goes to light). The action-orientation contract is enforced — when `next === 'dark'`, label is `'Switch to light mode'`; when `next === 'light'`, label is `'Switch to dark mode'`.
- IIFE preamble comment rewritten to document the new contract explicitly: "JS writes only documentElement.dataset.theme; CSS reads it (icon visibility, palette swap). aria-label is action-oriented: it describes the click target, not the current state (D-03, D-08, D-10). The icon SVGs are never touched by JS — visibility is 100% CSS (Pitfall 22 mitigation)." This guards against future drift toward imperative SVG mutation.
- Head IIFE at lines 11-23 (the no-FOUC bootstrap) is byte-identical to the pre-edit state — verified via `diff` against the in-repo v2.0 snapshot (zero output). Pitfall 1 contract preserved.
- Hugo build smoke (`hugo --minify --quiet`) succeeds locally on Hugo 0.161.1+extended; the minified `public/index.html` end-of-body script contains exactly two `setAttribute("aria-label",…)` calls (Hugo's HTML minifier normalizes single quotes to double quotes — semantically identical).
- Combined with Plan 01, Phase 8 ships ICON-01..05 in a single wave: button is sun/moon SVG (P01), 44×44 hit target (P01), CSS-only icon visibility swap (P01), reduced-motion-gated transition (P01), aria-label/aria-pressed reconciliation + persistence (P02).

## Task Commits

Each task was committed atomically on `main`:

1. **Task 1: Rewrite end-of-body IIFE — remove textContent, add aria-label setter, preserve all other responsibilities** — `7628180` (feat)

**Plan metadata commit:** to follow (docs: complete plan)

## Files Created/Modified

- `themes/minimal/layouts/_default/baseof.html` (+8, -5) — end-of-body IIFE rewritten; head IIFE byte-identical; markup, partials, body wrapper untouched. Net: 23-line IIFE block grew to 25 lines because the preamble comment expanded from 1 line to 4 lines (documenting the new D-08/D-10 contract). The two functional swaps (`textContent` → `setAttribute('aria-label', …)`) are 1-for-1.

## Verification Gates — All PASS

All 11 grep gates from the plan's `<verify>` block, plus the Pitfall 1 byte-identity diff, plus the cross-plan selector contract check, plus the Hugo build smoke:

| Gate | Expected | Actual | Result |
|------|----------|--------|--------|
| 1. `toggle.textContent` count | 0 | 0 | PASS |
| 2. `setAttribute('aria-label'` count | 2 | 2 | PASS |
| 3. `'Switch to dark mode'` literal present | yes | yes | PASS |
| 3. `'Switch to light mode'` literal present | yes | yes | PASS |
| 4. `setAttribute('aria-pressed'` count | 2 | 2 | PASS |
| 5. `document.documentElement.dataset.theme = next` present | yes | yes | PASS |
| 6. `localStorage.setItem('theme', next)` present | yes | yes | PASS |
| 6. `Safari private mode` comment present | yes | yes | PASS |
| 7. `meta[name="theme-color"]` reference count | 2 | 2 | PASS |
| 7. `meta.setAttribute('content', next === 'dark' ? '#100F0F' : '#FFFCF0')` present | yes | yes | PASS |
| 8. Head IIFE bootstrap comment present | yes | yes | PASS |
| 8. Head IIFE matchMedia call present | yes | yes | PASS |
| 9. JS does NOT query `.icon-sun` | true | true | PASS |
| 9. JS does NOT query `.icon-moon` | true | true | PASS |
| 9. JS does NOT classList-manipulate icons | true | true | PASS |
| 10. IIFE wrapper `(function () {` present | yes | yes | PASS |
| 10. Null guard `if (!toggle) return` present | yes | yes | PASS |
| 11. `</body>` and `</html>` present | yes | yes | PASS |
| Pitfall 1: head IIFE lines 11-23 byte-identical to v2.0 | empty diff | empty diff | PASS |
| Cross-plan: `querySelector('.theme-toggle')` in baseof + `class="theme-toggle"` in header | both present | both present | PASS |
| Hugo `--minify` build | exit 0 | exit 0 | PASS |
| Minified output: `setAttribute("aria-label",…)` calls | 2 | 2 | PASS |

## Decisions Made

- **Updated IIFE preamble comment** rather than leaving the v2.0 "single click handler performs five atomic mutations" string. The new comment explicitly names D-03 / D-08 / D-10 and calls out the Pitfall 22 mitigation — this is documentation for future-readers, not for the runtime, and it costs nothing.
- **Kept the "First-paint sync" comment** in place with only the trailing example string updated. The architectural rationale for the reconciliation block (head IIFE may resolve a theme that the server-rendered HTML does not reflect) is preserved verbatim.
- **Did NOT add a defensive guard** around the `setAttribute('aria-label', …)` call — `setAttribute` is universally supported and cannot throw in this context. Adding a try/catch would be cargo-cult.

## Deviations from Plan

None — plan executed exactly as written. The single Edit produced the new block on the first pass; all 11 grep gates passed cleanly; the head IIFE diff returned empty (Pitfall 1 preserved); cross-plan selector contract intact; Hugo build smoke green.

The CLAUDE.md `<stack>` section says "Hugo is NOT installed locally" but in fact Hugo v0.161.1+extended is on PATH via Homebrew (same observation as Plan 01 — non-blocking; the stack doc is stale on this point).

## Issues Encountered

**Hugo `--minify` quote normalization (informational, not a deviation):** When inspecting the rendered `public/index.html`, the literal source `setAttribute('aria-label', …)` (single quotes, with whitespace after the comma) is normalized by Hugo's HTML/JS minifier to `setAttribute("aria-label",…)` (double quotes, no whitespace). This is correct minifier behavior — JavaScript treats single and double quotes interchangeably for string literals — and the runtime semantics are identical. The grep verification used the source file (which retains single quotes); the minified-output check was a separate sanity gate.

## User Setup Required

None — no external service configuration, no new dependencies, no schema changes, no env vars.

## Threat Flags

None — the rewrite stays inside the threat surface declared in the plan's `<threat_model>` (T-08-04 through T-08-07, all dispositioned `mitigate`):

- **T-08-04 (localStorage tampering):** Head IIFE at lines 11-23 is byte-identical to v2.0; the allowlist check (`if (theme !== 'light' && theme !== 'dark')`) that rejects injected values is preserved verbatim.
- **T-08-05 (DOM injection via aria-label):** The two new `setAttribute('aria-label', …)` calls use HARD-CODED string literals selected by a ternary on `next === 'dark'`. No user content, no concatenation, no template literals. `setAttribute` does not parse HTML.
- **T-08-06 (meta theme-color desync, Pitfall 22):** `meta.setAttribute('content', next === 'dark' ? '#100F0F' : '#FFFCF0')` preserved verbatim inside the click handler. `grep -c 'meta\[name="theme-color"\]'` returns 2 (one per IIFE) as the acceptance criterion specifies.
- **T-08-07 (imperative SVG manipulation):** Hard prohibitions enforced by grep gates 9.1, 9.2, 9.3 — JS contains zero references to `.icon-sun`, `.icon-moon`, or `classList.*icon-`.

## Combined-with-Plan-01 Outcome

Phase 8 ships **all five ICON requirements** in Wave 1:

| Requirement | Plan | Mechanism |
|-------------|------|-----------|
| ICON-01 (icon depicts current theme) | 01 | Sun + moon SVGs in markup; `[data-theme]` CSS visibility swap |
| ICON-02 (no FOUC + persistence) | 01 + 02 | Head IIFE (untouched) sets `dataset.theme` pre-stylesheet (no FOUC); end-of-body IIFE writes `localStorage.setItem('theme', next)` in try/catch (persistence) |
| ICON-03 (a11y) | 02 | `aria-label` action-oriented; `aria-pressed` current state; both reconciled on first paint AND atomic with click |
| ICON-04 (44×44 hit target) | 01 | `min-width: 44px; min-height: 44px` on `.theme-toggle` button shell |
| ICON-05 (reduced motion) | 01 | 150 ms opacity cross-fade declared only inside `@media (prefers-reduced-motion: no-preference)` |

## Outstanding HUMAN-UAT (deferred to post-deploy walkthrough)

Per UI-SPEC §Verification Gates and CONTEXT.md `<canonical_refs>`, the following gates require a real browser on the deployed site at `https://tbohnstedt.cloud/`:

1. **ICON-03 screen-reader announcement check** — VoiceOver/NVDA must announce "Switch to dark mode, toggle button, not pressed" in light and "Switch to light mode, toggle button, pressed" in dark; aria-pressed flips on click.
2. **ICON-02 CPU-throttled reload FOUC visual check** — DevTools CPU 6× throttle + hard-reload in dark mode; record first paint; no sun-icon frame visible.
3. **ICON-04 mobile 320 px tap-target physical check** — DevTools mobile emulation; `document.querySelector('.theme-toggle').getBoundingClientRect()` must return both `width >= 44` and `height >= 44`.
4. **ICON-05 prefers-reduced-motion OS-toggle check** — macOS System Settings → Accessibility → Display → Reduce motion ON → click toggle → instant swap, no fade. Toggle setting OFF → click → ≤ 150 ms opacity cross-fade.
5. **Pitfall 22 theme-color meta cross-check** — Click toggle → `<meta name="theme-color">` content attribute updates atomically with `dataset.theme` and visible icon. No mid-click desync.

All five gates are deferred to the existing post-deploy HUMAN-UAT cycle (consistent with the v2.0 deferral pattern called out in STATE.md §Deferred Items). Implementation gates and grep verification are green; deferral is the planned exit pattern.

## Next Phase Readiness

**Phase 8 is complete and ready for verification.** Both plans landed cleanly; all 5 ICON requirements covered. The next milestone-internal step is the post-deploy HUMAN-UAT cycle (deferred — gated on push to `main` → GitHub Actions deploy → browser walkthrough at `https://tbohnstedt.cloud/`).

**Phase 9 (ABOUT — Dynamic Rounded Redesign) is unblocked** in the dependency graph. Phase 9 has no functional dependency on Phase 8 — the ordering is by ascending blast radius (CSS + template only, no JS). Planning for Phase 9 can begin via `/gsd-plan-phase 9`.

No blockers, no deferred items beyond the standard post-deploy HUMAN-UAT cycle.

## Self-Check: PASSED

Verified after writing this SUMMARY:

- `themes/minimal/layouts/_default/baseof.html` — FOUND (modified, contains the new aria-label setter calls)
- Commit `7628180` (Task 1) — FOUND in `git log`
- `.planning/phases/08-icon-svg-theme-toggle/08-02-SUMMARY.md` — FOUND (this file)
- Head IIFE at lines 11-23 byte-identical to v2.0 snapshot — verified via diff (zero output)
- Hugo build smoke (`hugo --minify --quiet`) — exit 0; minified output contains both `setAttribute("aria-label",…)` calls

---
*Phase: 08-icon-svg-theme-toggle*
*Completed: 2026-05-02*

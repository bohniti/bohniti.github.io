# Phase 8: ICON — SVG Theme Toggle - Context

**Gathered:** 2026-05-02
**Status:** Ready for planning
**Mode:** `--auto` (Claude picked recommended defaults across all gray areas)

<domain>
## Phase Boundary

Replace the existing text `<button class="theme-toggle">Dark</button>` in `themes/minimal/layouts/partials/header.html` with two inline SVG icons (sun + moon) sharing the same button. Header position, persistence (`localStorage`), OS-preference detection, and no-FOUC behavior from v2.0 Phase 4 are preserved unchanged. Only the visual presentation of the toggle and its accessibility semantics are in scope. No JS framework introduced. No new dependencies. No changes to the theme bootstrap IIFE in `baseof.html` (lines 11–23) — only the end-of-body click handler (lines 34–56) is rewritten.

</domain>

<decisions>
## Implementation Decisions

### Icon Source & Visual Language
- **D-01:** Hand-author both SVG paths inline using **Lucide v0.547.0** path data for `sun` and `moon`. Match the existing footer icon convention exactly: `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`. Both `<svg>` elements get `aria-hidden="true"` (the button carries the accessible name). This is a direct extension of the GitHub/Instagram footer pattern at `themes/minimal/layouts/partials/footer.html:7-17`.
- **D-02:** Render the SVGs at `width="24" height="24"` intrinsic — recoloring happens via `currentColor` ↔ `var(--text-secondary)` / `var(--accent)` (matching the current `.theme-toggle` color contract at `themes/minimal/static/css/style.css:101-115`). No hard-coded hex colors in the SVG markup.

### Icon-as-Current-State Mapping (ICON-01)
- **D-03:** Sun icon visible in **light** mode; moon icon visible in **dark** mode. The icon depicts the **current** theme, not the action. The `aria-label` carries the action ("Switch to dark mode" / "Switch to light mode") — see D-08. Resolves the FEATURES.md note "icon = current state, not target action" against the v2.0 button's text behavior (`textContent = 'Light'` when dark — that text was action-oriented; the icon flips that convention but the aria-label stays action-oriented).

### Swap Technique (No-FOUC, ICON-02)
- **D-04:** **Both SVGs always present in server-rendered HTML.** CSS hides the wrong one keyed off `[data-theme]` on `<html>`. The head IIFE in `baseof.html:11-23` already sets `dataset.theme` before the stylesheet loads — so by the time the browser paints, the correct icon is the only visible one. Zero JS is involved in icon visibility. JS never adds/removes nodes or toggles an `is-active` class on the SVGs.
- **D-05:** Hide mechanism: stack both SVGs in the same grid cell (`display: grid` on the button, both SVGs in `grid-area: 1 / 1`) and toggle `opacity: 0/1` keyed off `[data-theme]`. This enables the optional cross-fade (D-07) without layout reflow. The hidden SVG additionally gets `pointer-events: none` and `aria-hidden="true"` is set on both at all times (button is the labeled control).

### Tap Target (ICON-04)
- **D-06:** Explicit sizing on the button itself: `min-width: 44px; min-height: 44px; display: inline-grid; place-items: center;`. Do NOT pad the SVG — keep the SVG at intrinsic 24×24 and let the button shell absorb the hit area. This decouples icon size from hit area and makes the 44 CSS-px requirement self-documenting in the CSS rule.

### Transition (ICON-05)
- **D-07:** **Opacity-only cross-fade, ≤ 150 ms, ease.** No rotation. Wrapped in `@media (prefers-reduced-motion: no-preference)` — exactly mirroring the existing `body` transition pattern at `themes/minimal/static/css/style.css:49-56`. Rationale: rotation adds motion that does not improve comprehension and risks vestibular discomfort; the Flexoki/Kindle/Obsidian aesthetic prefers stillness. With reduced-motion users, the swap is instant (opacity transitions are not declared outside the `no-preference` media query).

### Accessibility & JS (ICON-03)
- **D-08:** Button `aria-label` value is **action-oriented**: `"Switch to dark mode"` when current theme is light, `"Switch to light mode"` when current theme is dark. Server-rendered initial value is `"Switch to dark mode"` (matches the IIFE's "no preference saved" fallback to `prefers-color-scheme`-resolved theme — but the end-of-body handler reconciles to actual theme on load, mirroring the existing `textContent` reconciliation at `baseof.html:43-45`).
- **D-09:** Button `aria-pressed` reports the **current state**: `"true"` when dark is active, `"false"` when light is active. (Current button uses this same convention — preserved verbatim.)
- **D-10:** End-of-body JS is the **only** JS that changes — rewrite the existing IIFE at `baseof.html:34-56`. New responsibilities (unchanged from v2.0): mutate `documentElement.dataset.theme`, write `localStorage.setItem('theme', next)`, update `meta[name="theme-color"]`. Removed responsibility: `toggle.textContent = …`. New responsibility: `toggle.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode')`. The icon visibility itself is CSS — JS does NOT touch the SVGs.

### Removed (Cleanup)
- **D-11:** Remove the visible button text `Dark` from `header.html:11`. Remove `toggle.textContent = …` lines from the end-of-body IIFE. Remove the v2.0 button's `font: inherit; font-size: 0.95rem;` rules from `style.css:101-111` since text is no longer rendered (replaced by the SVG color/size rules). Keep `:hover` and `:focus-visible` rules — both still apply to the button shell.

### theme-color Meta Sync (Pitfall 22 mitigation)
- **D-12:** Preserve the existing `meta[name="theme-color"]` sync in both the head IIFE (`baseof.html:20-22`) and the end-of-body click handler. Values stay `#FFFCF0` (light) and `#100F0F` (dark). No change here — flagged in PITFALLS Pitfall 22 as a known regression risk if the toggle handler is rewritten carelessly.

### Claude's Discretion
- Exact opacity transition timing (100 ms vs 150 ms) — within ≤ 150 ms cap from ICON-05; planner picks.
- Whether to use `display: grid` stacking (D-05 default) or `position: absolute` stacking — both produce the same result; planner picks whichever reads cleaner in `style.css`.
- Whether the button gets a `type="button"` attribute (currently present at `header.html:11`) — keep it, but planner can confirm during implementation.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope & Requirements (Project)
- `.planning/REQUIREMENTS.md` § ICON — SVG Theme Toggle — locked requirements ICON-01 through ICON-05
- `.planning/ROADMAP.md` § Phase 8: ICON — SVG Theme Toggle — goal + 5 deployed-site success criteria
- `.planning/PROJECT.md` § Constraints — Flexoki, vanilla JS only, no flash on load, accessible, prefers-reduced-motion

### Research (Milestone-Level, Phase 8 Slice)
- `.planning/research/SUMMARY.md` § ICON — Theme Toggle — must-haves + defer list (HIGH confidence)
- `.planning/research/SUMMARY.md` § Phase 1: ICON — SVG Theme Toggle — phase-targeted notes, "Must avoid" list (P01, P02, P03, P09, P22)
- `.planning/research/STACK.md` § ICON — inline SVG decision rationale, Lucide v0.547.0 path data source
- `.planning/research/FEATURES.md` § ICON — Theme Toggle — table-stakes list, defer list
- `.planning/research/PITFALLS.md` Pitfalls 1, 2, 3, 9, 22 — FOUC, hit target, hard-coded fills, prefers-reduced-motion, theme-color desync
- `.planning/research/ARCHITECTURE.md` § ICON — file-modification matrix (header.html, baseof.html, style.css)

### Codebase Context (Files To Be Modified)
- `themes/minimal/layouts/partials/header.html:11` — current text button (line to replace)
- `themes/minimal/layouts/_default/baseof.html:11-23` — head IIFE (theme bootstrap; **do not modify** — only read)
- `themes/minimal/layouts/_default/baseof.html:34-56` — end-of-body click handler (rewrite)
- `themes/minimal/static/css/style.css:101-122` — current `.theme-toggle` rules (rewrite for icon presentation; keep `:hover` / `:focus-visible`)
- `themes/minimal/static/css/style.css:49-56` — `prefers-reduced-motion` pattern to mirror in icon transition
- `themes/minimal/layouts/partials/footer.html:7-17` — reference pattern for inline Lucide SVG icons (do not modify)

### Codebase Maps Read During Scout
- `.planning/codebase/CONVENTIONS.md` — single-CSS-file rule, BEM-like naming, kebab-case CSS custom properties
- `.planning/codebase/STRUCTURE.md` — theme layout (no separate JS file expected for this phase)
- `.planning/codebase/STACK.md` — confirms no Node/npm; vanilla JS only

### External References (Visual / Spec)
- Lucide icon library v0.547.0 — `sun` and `moon` glyph path data (hand-copied inline; no npm import)
- MDN: `aria-label`, `aria-pressed`, `aria-hidden` on toggle buttons
- WCAG 2.1 SC 2.5.5 — target size 44×44 CSS-px

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Footer SVG icons** (`themes/minimal/layouts/partials/footer.html:7-17`): Establishes the exact inline-SVG convention this phase extends — Lucide visual language, 24×24 viewBox, `currentColor` stroke, 2 px stroke width, round caps. Copy the wrapper pattern verbatim and swap the path data for sun/moon. Footer renders the icons at `width="18" height="18"` for footer scale; header toggle renders at `24` to match menu typography weight.
- **Theme bootstrap IIFE** (`baseof.html:11-23`): Already sets `documentElement.dataset.theme` before the stylesheet loads. This is the no-FOUC mechanism the icon swap relies on. Do NOT touch this code.
- **`prefers-reduced-motion` media query block** (`style.css:49-56`): Mirror this exact pattern for the icon opacity transition — keep all motion declarations inside `@media (prefers-reduced-motion: no-preference) { … }` blocks.
- **`:focus-visible` rule on the existing button** (`style.css:117-122`): Already correct for the new icon button — keep verbatim.

### Established Patterns
- **CSS-driven theming via `[data-theme]` attribute on `<html>`**: Every theme-aware rule keys off `:root[data-theme="dark"] …` (search `style.css`). Icon visibility follows the same pattern: `[data-theme="light"] .theme-toggle .icon-moon { opacity: 0; }`, `[data-theme="dark"] .theme-toggle .icon-sun { opacity: 0; }`.
- **Single source of truth: `dataset.theme`** (per ARCHITECTURE.md): JS writes only to `documentElement.dataset.theme`; CSS reads it; everything else (button visual state, meta theme-color, icon visibility) is downstream of that one mutation. The new click handler must preserve this property.
- **Inline SVG with `currentColor`** (footer pattern + wordmark per `style.css:124-127`): Single source of color truth — the parent's `color` property cascades into the SVG. Icon must use `currentColor` for stroke; do not set explicit color values in the SVG markup.

### Integration Points
- **`themes/minimal/layouts/partials/header.html`** — line 11 is the only line in this file that changes. The wordmark partial (line 4) and the nav `range` block (lines 8–10) are untouched.
- **`themes/minimal/layouts/_default/baseof.html`** — lines 34–56 (end-of-body IIFE) get rewritten. Lines 11–23 (head IIFE) and lines 26–33 (body wrapper / partials) are untouched.
- **`themes/minimal/static/css/style.css`** — modify the existing `.theme-toggle` block at lines 101–122. New rules (icon stacking, opacity, transitions) join this block with section comments. No new top-level sections needed.

</code_context>

<specifics>
## Specific Ideas

- **Lucide visual language is mandatory** — the v3.0 milestone is a polish pass, not a redesign. Sun/moon icons must look like they belong with the existing GitHub/Instagram footer icons (same stroke weight, same cap style, same visual mass at the rendered size). Mixing Heroicons or Feather Icons in the header would visually clash with Lucide in the footer.
- **GitHub-style** is the user's reference (per PROJECT.md "GitHub-style, same header position, no emoji"). GitHub's theme toggle uses an outline sun and outline crescent moon, which matches the Lucide `sun` (rays + circle) and `moon` (crescent) glyphs.
- **No emoji** is an explicit exclusion in PROJECT.md — confirmed; the icons must be SVG, not emoji `☀️ 🌙`.

</specifics>

<deferred>
## Deferred Ideas

- **ICON-FUT-01: Single-SVG sun-with-moon-mask morph trick** (already in REQUIREMENTS.md "Future Requirements"). Marginal visual gain over the two-SVG approach; deferred to v3.x or beyond.
- **System-preference indicator** (third state — "auto" — that follows OS without storing a preference). Not in v2.0, not requested for v3.0; deferred indefinitely. Current behavior: first visit follows OS, then explicit toggle wins forever via `localStorage`.
- **Animated rotate-in transition** for the icon swap. Considered (research mentioned "rotate/fade") but rejected per D-07 — Flexoki/Kindle aesthetic favors stillness. Could be revisited if a user wants more delight, but not in this phase.

</deferred>

---

*Phase: 8-icon-svg-theme-toggle*
*Context gathered: 2026-05-02*

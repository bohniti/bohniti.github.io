# Phase 8: ICON — SVG Theme Toggle - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-02
**Phase:** 8-icon-svg-theme-toggle
**Mode:** `--auto` (no interactive prompts; Claude selected recommended defaults across all areas)
**Areas discussed:** Icon source & visual language, Icon-as-current vs icon-as-target, Swap technique (no-FOUC), Tap target sizing, Transition style, Accessibility / JS responsibilities, Markup cleanup

---

## Icon Source & Visual Language

| Option | Description | Selected |
|--------|-------------|----------|
| Lucide v0.547.0 (`sun` + `moon`), inline | Hand-copy path data; matches existing footer icon library exactly (24×24, 2 px stroke, round caps, `currentColor`) | ✓ |
| Heroicons (outline) | Outline 24×24 set; popular but visually heavier than Lucide; would clash with footer | |
| Feather Icons | Lighter stroke (1.5 px) than current footer convention; introduces a second visual language in the header | |
| Custom hand-drawn paths | Maximum control; cost > benefit for this phase; no design system upgrade in v3.0 scope | |

**Auto-selection rationale:** Footer icons (`themes/minimal/layouts/partials/footer.html:7-17`) already use Lucide-style 24×24, 2 px stroke, `currentColor`. Research SUMMARY.md explicitly pins Lucide v0.547.0. Any other library would visually clash.

---

## Icon-as-Current-State vs Icon-as-Target-Action

| Option | Description | Selected |
|--------|-------------|----------|
| Icon shows current theme (sun in light, moon in dark) | Matches REQ ICON-01 explicitly; matches GitHub's pattern; aria-label carries the action | ✓ |
| Icon shows target action (moon in light, sun in dark) | Common alternative pattern; conflicts with REQ ICON-01 wording | |

**Auto-selection rationale:** REQ ICON-01 is unambiguous: "icon shows current state". Locked.

---

## Swap Technique (No-FOUC)

| Option | Description | Selected |
|--------|-------------|----------|
| Both SVGs in DOM, CSS hides wrong one via `[data-theme]` | No JS in icon-visibility path; head IIFE sets `data-theme` before stylesheet loads → correct icon paints first | ✓ |
| Single SVG, JS replaces innerHTML on theme change | Re-introduces FOUC risk; JS does work CSS already does for free | |
| Single SVG with CSS mask morph | Defer-listed (ICON-FUT-01) — marginal visual gain | |

**Auto-selection rationale:** Pitfall 1 in PITFALLS.md is unambiguous about FOUC prevention via the CSS swap. Lowest risk, simplest implementation, zero JS in the visibility path.

---

## Stacking Mechanism for Both SVGs

| Option | Description | Selected |
|--------|-------------|----------|
| `display: grid` with both SVGs in `grid-area: 1 / 1`, opacity-toggled | Modern, clean; keeps button auto-sized to icon; enables cross-fade with no layout shift | ✓ |
| `position: relative` button + `position: absolute` SVGs | Equivalent visually; slightly more legacy-style | |
| `display: none` / `display: block` toggle | Disables transition (display can't transition); instant snap only | |

**Auto-selection rationale:** Grid stacking is the cleanest pattern; allows the opacity transition (D-07) without layout reflow. `display: none` would block ICON-05's optional transition.

---

## Tap Target Sizing (ICON-04)

| Option | Description | Selected |
|--------|-------------|----------|
| `min-width: 44px; min-height: 44px` on the button + 24×24 SVG inside | Decouples icon size from hit area; self-documenting; matches WCAG 2.1 SC 2.5.5 | ✓ |
| `padding: 10px` on the button (24 + 10 + 10 = 44) | Equivalent geometry; fragile if SVG size ever changes | |
| Render SVG at 44×44 directly | Visually too large; loses Lucide visual proportions | |

**Auto-selection rationale:** Explicit min-dimensions read more clearly than padding-arithmetic and survive future icon size changes.

---

## Transition Style (ICON-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Opacity-only cross-fade, ≤ 150 ms, ease, gated on `prefers-reduced-motion: no-preference` | Subtle, fits Flexoki/Kindle aesthetic; mirrors existing body transition pattern (`style.css:49-56`) | ✓ |
| Rotate-and-fade (sun rotates out, moon rotates in) | More motion; risk of vestibular discomfort; aesthetic mismatch with stillness convention | |
| No transition (instant swap regardless of reduced-motion preference) | Misses the "≤ 150 ms transition" optional requirement in ICON-05 | |

**Auto-selection rationale:** ICON-05 explicitly allows a transition wrapped in `@media (prefers-reduced-motion: no-preference)`. Opacity-only is the minimal motion that satisfies the requirement and matches the Flexoki aesthetic. Rotation adds nothing semantically.

---

## Accessibility & JS Responsibilities (ICON-03)

| Option | Description | Selected |
|--------|-------------|----------|
| `aria-label` action-oriented + `aria-pressed` state-oriented; JS only mutates `aria-label`, `aria-pressed`, `dataset.theme`, `localStorage`, `theme-color` | Matches WAI-ARIA toggle button pattern; preserves existing v2.0 behavior; SVGs get `aria-hidden="true"` | ✓ |
| `aria-label` static ("Theme toggle") + visually hidden `<span>` for current state | Acceptable but more markup; loses target-action announcement | |
| Use `<input type="checkbox">` with CSS-styled label | Different a11y model; more invasive; not v2.0 pattern | |

**Auto-selection rationale:** REQ ICON-03 specifies action-oriented label + `aria-pressed` for state. The current v2.0 button already uses `aria-pressed` — preserve that contract. Sara Soueidan's accessible icon button pattern (cited in research) puts the label on the button and `aria-hidden` on the SVG.

---

## Markup Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Remove `Dark` text from button; remove `toggle.textContent = …` from JS; remove unused `font: inherit` rules | Clean break from v2.0 text-button — no dead code or vestigial styles | ✓ |
| Keep button text as visually-hidden fallback | Redundant with `aria-label`; adds DOM weight for no benefit | |

**Auto-selection rationale:** Visible text is no longer rendered → unused styles and JS branches should be removed (CLAUDE.md "Don't add backwards-compatibility hacks"). Keep `:hover` and `:focus-visible` rules — both apply to the button shell regardless of content.

---

## Claude's Discretion

- Exact opacity transition timing within ≤ 150 ms cap (planner picks 100 vs 120 vs 150 ms)
- Whether to use `display: grid` (default per D-05) or `position: absolute` for SVG stacking — equivalent results; planner picks for code clarity
- Whether button gets `type="button"` (currently present) — keep, but planner can confirm
- CSS class names for the two SVGs (e.g. `.theme-toggle .icon-sun` / `.icon-moon` vs data attributes) — planner picks; either works

## Deferred Ideas

- **ICON-FUT-01:** Single-SVG sun-with-moon-mask morph trick — already in REQUIREMENTS.md "Future Requirements"; deferred to v3.x.
- **System-preference indicator** (third "auto" state that follows OS without storing): not in v2.0, not requested for v3.0.
- **Animated rotate-in transition:** considered (research mentioned "rotate/fade") but rejected per D-07 — Flexoki/Kindle aesthetic favors stillness.

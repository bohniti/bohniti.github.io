# Phase 4: Theming Foundation - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a CSS-variable-driven dark palette under `:root[data-theme="dark"]` and a header toggle button that flips between light and dark modes. The toggle persists to `localStorage`, falls back to OS `prefers-color-scheme` on first visit, applies before first paint via an inline `<head>` IIFE (no FOUC), is keyboard- and screen-reader-accessible, animates smoothly under non-reduced-motion, and updates iOS Safari chrome via a JS-managed `theme-color` meta tag.

In scope: palette tokens, the toggle button + IIFE bootstrap, `<meta name="color-scheme">`, theme-color meta sync, smoke-test of existing chart/diagram embeds in dark mode.

Out of scope: header wordmark wiring (Phase 5), favicon `<link>` tags (Phase 5), per-library reactivity for Mermaid/Plotly/Leaflet (deferred to v2.x), cross-tab `storage` event sync (deferred), view-transition cross-fade on toggle (deferred), three-state auto/light/dark toggle (rejected — see REQUIREMENTS § Out of Scope).

</domain>

<decisions>
## Implementation Decisions

### Background Palette Reconciliation (Cross-Phase Tension)

- **D-01:** Site `--bg` / `--bg-dark` use Flexoki canonical tones (`#FFFCF0` Paper / `#100F0F` Black), **NOT** the corner-pixel hex values printed by Phase 3's `scripts/build_brand_assets.py` (`#FEFEFE` / `#000000`). Rationale: the rest of the palette is tuned around Flexoki Paper/Black; using near-pure white/black site-wide would abandon the warm minimal feel the project is designed around.
- **D-02:** The Phase 3 → Phase 4 hex contract recorded in `03-CONTEXT.md` § "Recorded hex values for Phase 4 cross-phase contract (D-03)" is **superseded for `--bg`/`--bg-dark`**. The seam mitigation moves into Phase 5 as a localized concern: the wordmark `<img>` (or its wrapper) gets a CSS background matching the PNG's corner-pixel hex (`#FEFEFE` for `-light` variants, `#000000` for `-dark` variants) so the wordmark blends only within its own bounding box. The rest of the page bg stays Flexoki. **This is a hard cross-phase note for Phase 5 — do not omit the wrapper bg, the seam will be visible.**

### Dark Palette Tokens

- **D-03:** Dark palette is mapped under `:root[data-theme="dark"]` with the canonical Flexoki dark values listed below. Light tokens at the un-attributed `:root` selector are unchanged from current `style.css`.

  ```
  /* :root[data-theme="dark"] */
  --bg:               #100F0F  Black
  --bg-secondary:     #1C1B1A  Base950
  --text:             #CECDC3  Base200
  --text-secondary:   #878580  Base500
  --text-muted:       #575653  Base700
  --accent:           #D14D41  Red400   (brighter than light's Red600 — needed for contrast on dark bg)
  --accent-hover:     #DA7E76  Red300
  --link:             #D14D41  Red400
  --link-hover:       #DA7E76  Red300
  --border:           #282726  Base900
  --code-bg:          #1C1B1A  Base950
  ```

- **D-04:** `--max-width` (currently 640px) is theme-agnostic and stays in the un-attributed `:root` block — do not duplicate it under `[data-theme="dark"]`.

### Toggle Button Design & Placement

- **D-05:** The toggle is a plain text button labeled `Dark` in light mode and `Light` in dark mode (the label describes the **target state on click**, matching the canonical convention: "click to go dark" / "click to go light").
- **D-06:** The button is appended to `.site-nav` (`themes/minimal/layouts/partials/header.html`) **after** the last nav link rendered by the `range .Site.Menus.main` loop. It inherits the existing `.site-nav` flex `gap: 1.5rem` — no new flex slot, no responsive layout work, and it stacks naturally with the nav under the existing `@media (max-width: 600px) { .site-header { flex-direction: column; } }` rule.
- **D-07:** The button element itself is `<button type="button" class="theme-toggle" aria-pressed="...">` with the visible text inside. `aria-pressed="false"` in light mode, `aria-pressed="true"` in dark mode (semantically: the "dark mode" state is engaged when pressed). No icon.
- **D-08:** Button styling matches the existing `.site-nav a` pattern (`font-size: 0.95rem`, `color: var(--text-secondary)`, no underline, no border, transparent bg) so it visually blends with the nav links. Hover state matches `.site-nav a:hover` (`color: var(--accent)`).

### Transition Behavior

- **D-09:** A targeted color transition fires on `body` (and any element whose color/border-color changes with the theme) — explicitly NOT `transition: all` or `*` selector. Animated properties: `background-color`, `color`, `border-color`. Duration: `150ms ease`.
- **D-10:** The entire transition rule sits inside `@media (prefers-reduced-motion: no-preference) { ... }` so reduced-motion users get an instant snap with no transition rule loaded at all (cleaner than `transition: none` overrides). This satisfies THEME-03's reduced-motion clause structurally rather than as an override.

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

### No-Flash Bootstrap (locked by THEME-02)

- **D-11:** An inline `<script>` IIFE in `baseof.html` `<head>`, placed **before** `<link rel="stylesheet">`, reads `localStorage.getItem('theme')` (or whatever key D-13 settles on) → falls back to `window.matchMedia('(prefers-color-scheme: dark)').matches` → sets `document.documentElement.dataset.theme = 'dark' | 'light'` synchronously. Because it runs before the CSS parses, the first paint already has the correct palette. Inline-script content stays small (<400 bytes after minification) so it doesn't bloat the HTML head.

### Accessibility (locked by THEME-03)

- **D-12:** The toggle is reachable via Tab key naturally (it's a real `<button>`, no `tabindex` needed). Click and Enter/Space activate it via default button semantics. `aria-pressed` mutates on each click. No additional `aria-label` is needed because the button has visible text content ("Dark" / "Light"), and the button's accessible name is that visible text.

### Storage & Meta

- **D-13:** `localStorage` key name: **Claude's discretion**, but should be a single, lowercase, descriptive token (e.g., `theme`). Document the chosen key in the IIFE comment so future-me can find it.
- **D-14:** A static `<meta name="color-scheme" content="light dark">` is added to `<head>` (locked by THEME-05).
- **D-15:** A `<meta name="theme-color">` tag is also added; its `content` attribute is updated by the toggle's click handler to match the active theme bg (`#FFFCF0` for light, `#100F0F` for dark) so iOS Safari's chrome adapts. The IIFE sets the initial value at first paint.

### Cross-Library Readability (THEME-06)

- **D-16:** No code changes to existing inline scripts in blog posts (Mermaid shortcode, Plotly charts, Leaflet maps). Verification is a manual smoke-test of `/blog/2026-03-05-climbing-routes/` in dark mode after Phase 4 ships — eyeball check that text is readable. If anything is illegible, log it to a deferred-ideas note for v2.x; do not block Phase 4 on it.

### Claude's Discretion

- IIFE exact code shape (try/catch around localStorage for Safari private mode, `let`/`const` choice, single-line vs multi-line)
- `localStorage` key name (suggest `theme`)
- Exact `theme-color` meta hex (must match D-01 light/dark `--bg` values: `#FFFCF0` / `#100F0F`)
- Whether the toggle button gets a focus-visible outline beyond browser default (probably yes for accessibility, but visual specifics can match `.site-nav a:focus-visible` if such a rule is added)
- Whether to add `:focus-visible` rules to the rest of the nav at the same time (small cleanup, low cost)
- File where the inline IIFE lives — `baseof.html` is the only sensible host; only question is whether to extract to a Hugo partial (`partials/theme-bootstrap.html`) for cleanliness or inline it directly. Either is fine; partial is slightly cleaner if the script grows.

### Folded Todos

None — no pending todos in STATE.md matched this phase's scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & Requirements
- `.planning/ROADMAP.md` § "Phase 4: Theming Foundation" — phase goal, dependencies (none architecturally; blocks Phase 5), 5 success criteria
- `.planning/REQUIREMENTS.md` § "Theming" — THEME-01..THEME-06 (toggle persistence, no-flash, a11y, dark palette, color-scheme meta, library readability)
- `.planning/REQUIREMENTS.md` § "Out of Scope" — three-state toggle, `<picture>` + `prefers-color-scheme` for wordmark, cookie persistence, server-side anything (all rejected)
- `.planning/REQUIREMENTS.md` § "Future Requirements" — view-transition cross-fade, cross-tab `storage` sync, library reactivity (all explicitly deferred — do NOT implement in this phase)
- `.planning/PROJECT.md` § "Constraints" — no JS framework, vanilla JS only, inline `<head>` script for no-flash, accessibility requirements

### Codebase Conventions & Files
- `themes/minimal/static/css/style.css` (264 lines) — current single stylesheet with light `:root` palette at lines 4-18; dark block must extend, not replace
- `themes/minimal/layouts/_default/baseof.html` (19 lines) — `<head>` host for IIFE, color-scheme meta, theme-color meta
- `themes/minimal/layouts/partials/header.html` (10 lines) — toggle button insertion site (after the `range .Site.Menus.main` loop, inside `<nav class="site-nav">`)
- `.planning/codebase/CONVENTIONS.md` § "JavaScript Conventions" — vanilla ES6+, `const`/`let` (no `var`), camelCase, no framework
- `.planning/codebase/CONVENTIONS.md` § "CSS Conventions" — Flexoki palette discipline, `.site-*` class naming, single stylesheet
- `.planning/codebase/STRUCTURE.md` § theme files layout

### Cross-Phase Contracts (incoming)
- **From Phase 3** (`03-CONTEXT.md` § "Mid-Execution Deviation"): Phase 3 sampled `#FEFEFE` (light bg corner) and `#000000` (dark bg corner) from the brand-asset PNGs and recorded those as the cross-phase hex contract for `--bg`/`--bg-dark`. **Phase 4 deliberately supersedes that contract** for site-wide tokens (see D-01, D-02). The Phase 3 hex values move into Phase 5's responsibility as a localized wordmark-wrapper bg.

### Cross-Phase Contracts (outgoing)
- **To Phase 5** (Wordmark + Favicon Wiring): the wordmark `<img>` (or its wrapper element) MUST set `background: #FEFEFE` for the `-light` variant and `background: #000000` for the `-dark` variant to mask the rectangular seam where the PNG corner-pixel bg differs from Flexoki `--bg`. Failing to do this leaves a visible ~5-7% lightness band framing each wordmark.
- **To Phase 5**: the `[data-theme]` attribute is set on `<html>` (`document.documentElement`) — Phase 5's wordmark CSS selectors (`html[data-theme="dark"] .wordmark { ... }`) key off this attribute directly. No JS swap needed.
- **To future phases**: light tokens stay at the un-attributed `:root` block, dark tokens at `:root[data-theme="dark"]`. Adding new variables (e.g., for gallery card hover) requires defining them in BOTH blocks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `themes/minimal/static/css/style.css` — single CSS file already structured around CSS custom properties at `:root` (lines 4-18). Adding the dark block is purely additive — no refactor needed, no replacement of hardcoded colors, every component-level rule (`.site-title a`, `.post-item-title a`, `.page-content code`, `.site-footer`, etc.) already uses `var(--token)`. This is the cleanest possible foundation for theming.
- `themes/minimal/layouts/partials/header.html` — current header has `.site-nav` as a flex container with gap; appending one more child (the button) needs zero layout work.
- Existing `@media (max-width: 600px)` rule at line 259 already collapses the header to column layout; the toggle will stack naturally with the nav links under the same rule.

### Established Patterns
- CSS custom properties on `:root` for all colors (no hardcoded hex outside `:root`)
- Flexoki palette discipline — every color is a Flexoki Base or Red shade, not arbitrary
- Vanilla JS only, inline scripts allowed in `baseof.html` (consistent with the project's `goldmark.renderer.unsafe = true` posture, though that's about Markdown, not templates)
- Hugo partials for stable header/footer content (`partials/header.html`, `partials/footer.html`)
- No JS bundle, no module system — inline `<script>` is the project's only JS delivery mechanism

### Integration Points
- **CSS:** add `:root[data-theme="dark"] { ... }` block to `style.css` after the existing `:root` block (lines 4-18), and add the `@media (prefers-reduced-motion: no-preference)` transition block once near the body rules (~line 30 after the `body { ... }` block)
- **HTML head:** modify `themes/minimal/layouts/_default/baseof.html` to add the IIFE `<script>` and the two `<meta>` tags (color-scheme + theme-color); IIFE goes BEFORE the stylesheet `<link>` (line 8) so it runs first
- **Header partial:** modify `themes/minimal/layouts/partials/header.html` line ~9 to append `<button class="theme-toggle">` after the menu-loop, inside `<nav class="site-nav">`
- **Toggle styling:** add `.theme-toggle` rules to `style.css` matching `.site-nav a` (font-size, color, hover) plus button reset (no border, no bg, cursor: pointer)
- **Smoke-test target:** `/blog/2026-03-05-climbing-routes/` is the canary page (Mermaid + Plotly + Leaflet all in one) for THEME-06 verification

### Hugo-Specific Notes
- `baseof.html` is in the theme dir (`themes/minimal/layouts/_default/`) — modifying there is correct, no override needed
- Hugo will reload automatically on file change in `hugo server`; if `hugo` is not installed locally (per CLAUDE.md), use the Docker fallback or build via `gh workflow run` against a branch
- No Hugo shortcodes needed for this phase (Mermaid shortcode from Phase 1 is unaffected)

</code_context>

<specifics>
## Specific Ideas

- The IIFE should be small enough to not bother with a separate `theme-bootstrap.html` partial, but if it accumulates more than ~12 lines (try/catch + matchMedia + dataset write + theme-color meta sync), break it out — `baseof.html` is supposed to stay readable.
- The toggle's click handler needs to do four things atomically: flip `data-theme`, flip `aria-pressed`, write to `localStorage`, update `theme-color` meta. Keep these in a single function (not split across multiple event listeners) so the four side effects can never desync.
- Test the no-FOUC requirement by hard-reloading any page in dark mode under DevTools network throttling (Slow 3G) and recording the screen — the success criterion #1 is explicit about this. The IIFE running before stylesheet parse is the structural guarantee.
- Test reduced-motion explicitly via DevTools Rendering panel ("Emulate CSS media feature prefers-reduced-motion: reduce") and verify no transition fires when toggling — the structural guarantee here is that the `@media (prefers-reduced-motion: no-preference)` block doesn't load its `transition` rule at all under reduced-motion.
- The `theme-color` meta value MUST exactly match the active `--bg` (`#FFFCF0` light, `#100F0F` dark) — these are the visible chrome colors on iOS Safari, mismatch is visible.

</specifics>

<deferred>
## Deferred Ideas

- Cross-tab theme sync via `storage` event listener — listed in REQUIREMENTS § Future. Single-tab persistence is sufficient for v2.0.
- View-transition API cross-fade on toggle — listed in REQUIREMENTS § Future. The 150ms color transition (D-09) is enough.
- Per-library reactivity for Mermaid / Plotly / Leaflet — listed in REQUIREMENTS § Future. THEME-06 is satisfied by smoke-testing readability with theme-agnostic Flexoki accents; per-library re-render on toggle is a v2.x concern.
- PWA `site.webmanifest` with theme-color — listed in REQUIREMENTS § Future. Phase 4 only adds the `<meta name="theme-color">` tag, not a manifest file.
- Three-state (light / dark / auto) toggle — explicitly Out of Scope per REQUIREMENTS. Two-state with OS-preference fallback on first visit is the canonical 2026 pattern.
- Cookie-based theme persistence — explicitly Out of Scope. `localStorage` is sufficient; no server involved.
- `<picture>` + `prefers-color-scheme` for the wordmark — explicitly Out of Scope (silently overrides manual toggle, anti-pattern).
- A focus-visible outline rework across the entire nav — Claude's Discretion; could be added as a small cleanup with the toggle's `.site-nav a:focus-visible` rule, but is not required by THEME-* and shouldn't expand scope.

</deferred>

---

*Phase: 04-theming-foundation*
*Context gathered: 2026-04-29*

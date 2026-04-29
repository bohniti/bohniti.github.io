# Phase 4: Theming Foundation - Pattern Map

**Mapped:** 2026-04-29
**Files analyzed:** 3 modified files (zero new files unless IIFE is extracted to a partial)
**Analogs found:** 3 / 3 (100% — every change has an in-repo analog because this phase is purely additive to existing structures)

---

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `themes/minimal/static/css/style.css` (additive: new `:root[data-theme="dark"]` block + `@media (prefers-reduced-motion)` body transition + `.theme-toggle` rules + `:focus-visible` rule) | stylesheet (theme tokens + interactive component) | declarative (CSS cascade) | itself — existing `:root` block (lines 4-18), existing `body` rule (lines 26-32), existing `.site-nav a` rules (lines 66-75) | exact (self-analog) |
| `themes/minimal/layouts/_default/baseof.html` (additive: inline `<script>` IIFE + `<meta name="color-scheme">` + `<meta name="theme-color">`) | base layout template | template render | itself — existing `<head>` block (lines 3-9) | exact (self-analog) |
| `themes/minimal/layouts/partials/header.html` (additive: append `<button class="theme-toggle">` after the menu loop, inside `<nav class="site-nav">`) | partial (header) | template render | itself — existing `<nav class="site-nav">` block (lines 5-9) and the `range .Site.Menus.main` loop | exact (self-analog) |

**No new files** are required. Per CONTEXT.md § "Claude's Discretion" bullet 6, the IIFE *may* optionally be extracted to `themes/minimal/layouts/partials/theme-bootstrap.html` for cleanliness, but this is a stylistic choice. If extracted, that new file mirrors the simplicity of the existing `partials/header.html` (template-only, no logic outside the inline `<script>` body).

---

## Pattern Assignments

### `themes/minimal/static/css/style.css` — additive theming changes

**Self-analog:** the file's own existing structure is the pattern. The codebase is uniquely well-prepared for theming because every component-level rule already uses `var(--token)` (no hardcoded hex outside `:root`). The dark block is structurally identical to the light block.

#### Existing light palette to mirror (lines 4-18)

This is the EXACT shape the new `:root[data-theme="dark"]` block must mirror:

```css
:root {
  /* Flexoki-inspired palette */
  --bg: #FFFCF0;
  --bg-secondary: #F2F0E5;
  --text: #100F0F;
  --text-secondary: #6F6E69;
  --text-muted: #B7B5AC;
  --accent: #AF3029;
  --accent-hover: #D14D41;
  --link: #AF3029;
  --link-hover: #D14D41;
  --border: #E6E4D9;
  --code-bg: #F2F0E5;
  --max-width: 640px;
}
```

**Key constraints from this analog:**
- 11 color tokens to mirror under `[data-theme="dark"]` (every line above except `--max-width`).
- `--max-width: 640px` MUST stay only in the un-attributed `:root` block (D-04 — do not duplicate).
- The leading comment `/* Flexoki-inspired palette */` is the precedent for the dark block's comment style. Suggest `/* Flexoki-inspired dark palette */` for the new block, placed directly after line 18 (before the closing `}` of the light block has already happened — append the new block beginning at the next line, line 19).

#### Existing `body` rule (lines 26-32) — site for the transition `@media` block

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  padding: 0 1.5rem;
}
```

**Pattern note:** `body` already references `var(--bg)` and `var(--text)`. When `[data-theme="dark"]` flips the token values, the body re-paints automatically without any rule changes. The new `@media (prefers-reduced-motion: no-preference) { body { transition: ... } }` block (D-09 / D-10) sits **immediately after** this rule (insert at ~line 33, before the `/* === Layout === */` section header at line 34) so it stays in the "Reset & Base" section thematically.

Exact rule to insert (per UI-SPEC § "Body transition rule"):

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

**Forbidden:** `transition: all`, `*` selector, transitions on layout properties (`width`, `height`, `padding`, `margin`, `transform`), and transitions outside the `prefers-reduced-motion: no-preference` media block (D-09, D-10).

#### Existing `.site-nav a` rules (lines 66-75) — typography/color/hover blueprint for `.theme-toggle`

```css
.site-nav {
  display: flex;
  gap: 1.5rem;
}

.site-nav a {
  font-size: 0.95rem;
  color: var(--text-secondary);
  text-decoration: none;
}

.site-nav a:hover,
.site-nav a.active {
  color: var(--accent);
}
```

**Pattern note for `.theme-toggle` rule (per D-08 + UI-SPEC § Component Inventory):**
- `font-size: 0.95rem` — match `.site-nav a`
- `color: var(--text-secondary)` — match `.site-nav a`
- No `text-decoration` (already none on `<button>`, but `.site-nav a` sets `none` explicitly — for consistency with sibling, no need to set on button)
- Hover: `color: var(--accent)` — match `.site-nav a:hover`
- Plus button reset (the elements `.site-nav a` does NOT need but `<button>` does):
  - `font: inherit` (browser default `<button>` uses a smaller UA font)
  - `background: transparent`
  - `border: 0`
  - `padding: 0`
  - `cursor: pointer`

Exact rule to insert (per UI-SPEC § "Button reset rules"):

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
```

**Insertion site:** directly after the existing `.site-nav a:hover, .site-nav a.active { ... }` rule (after line 75), inside the `=== Header ===` section (whose section comment is at line 41). This keeps all header-related rules grouped per the existing section convention (per CONVENTIONS.md § CSS Conventions).

#### Focus-visible rule (UI-SPEC § "Focus-visible Policy")

```css
.site-nav a:focus-visible,
.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```

**Insertion site:** after the `.theme-toggle:hover` rule, still inside the `=== Header ===` section. This rule is the *only* focus-visible expansion in Phase 4 — do NOT add focus-visible to `.site-title a`, `.page-content a`, `.post-item-title a`, or footer links (UI-SPEC § "Out of Scope").

#### Section-comment convention (CONVENTIONS.md § CSS Conventions)

```css
/* === Section Name === */
```

Existing sections in order: Reset & Base, Layout, Header, Post List (Home), Single Post / Page, Footer, Responsive. **No new section header is needed** for Phase 4 — the dark `:root` block is part of "Reset & Base" (no header for that section in current file; the file opens directly with `*, *::before...` at line 2 and `:root` at line 4), the body transition stays in "Reset & Base", and the `.theme-toggle` rules belong in "Header" alongside `.site-nav a`.

#### Existing responsive breakpoint (lines 259-264) — already covers the toggle

```css
@media (max-width: 600px) {
  html { font-size: 16px; }
  .site-header { flex-direction: column; gap: 0.5rem; }
  .site-wrapper { padding: 2rem 0 4rem; }
  .footer-links { gap: 1rem; }
}
```

**Pattern note:** the `.site-header { flex-direction: column; gap: 0.5rem; }` rule already collapses the header into a column on mobile. Because the `.theme-toggle` is appended to `.site-nav` (which itself is already a flex child of `.site-header`), the toggle stacks naturally under the existing rule. **No new mobile rule is needed.**

---

### `themes/minimal/layouts/_default/baseof.html` — `<head>` additions

**Self-analog:** the existing 19-line file IS the pattern. The current `<head>` (lines 3-9) is the slot for the inline `<script>` IIFE and the two new `<meta>` tags.

#### Existing `<head>` block (lines 1-9)

```html
<!DOCTYPE html>
<html lang="{{ .Site.LanguageCode }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ if not .IsHome }}{{ .Title }} — {{ end }}{{ .Site.Title }}</title>
  <meta name="description" content="{{ with .Description }}{{ . }}{{ else }}{{ .Site.Params.description }}{{ end }}">
  <link rel="stylesheet" href="{{ "css/style.css" | absURL }}">
</head>
```

**Pattern notes for additive insertions (per CONTEXT.md § Integration Points + UI-SPEC § IIFE bootstrap):**

| Element | Insertion Position | Rationale |
|---------|--------------------|-----------|
| `<meta name="color-scheme" content="light dark">` | After line 5 (`<meta name="viewport">`), before `<title>` | Static meta, no JS interaction; logically grouped with other browser-hint metas. |
| `<meta name="theme-color" content="#FFFCF0">` | Immediately after `color-scheme` meta | Initial value MUST match the *light* `--bg` (D-15). The IIFE updates it on first paint if dark theme is active; toggle handler updates it on click. **Must appear ABOVE the IIFE in source order** so the IIFE can `document.querySelector('meta[name="theme-color"]')` synchronously without waiting for `DOMContentLoaded` (UI-SPEC § IIFE bootstrap point 4). |
| Inline `<script>` IIFE | After both `<meta>` tags, **BEFORE** `<link rel="stylesheet">` (line 8) | Critical for no-FOUC (D-11): the IIFE MUST set `document.documentElement.dataset.theme` before the stylesheet parses, so the first paint already has the correct palette. |

**Indentation:** 2 spaces (per CONVENTIONS.md § HTML Template Conventions). Match existing file.

**Hugo template variables in `<head>`:** the existing `{{ .Site.LanguageCode }}`, `{{ if not .IsHome }}{{ .Title }} — {{ end }}{{ .Site.Title }}`, and `{{ with .Description }}{{ . }}{{ else }}{{ .Site.Params.description }}{{ end }}` are pure text-substitution patterns. The inline `<script>` body is plain JS with NO Hugo template logic — keep them separate (the IIFE must work identically across all pages, no per-page variation).

#### IIFE shape (per UI-SPEC § IIFE bootstrap + CONTEXT.md § Specifics)

There is no in-repo analog for an inline `<head>` IIFE — this is the first one in the project. Use UI-SPEC's specification + CONVENTIONS.md § JavaScript Conventions as the pattern source:

- `const`/`let` only (no `var`)
- camelCase
- try/catch around `localStorage.getItem('theme')` (Safari private mode throws on access)
- IIFE form `(function () { ... })();` so identifiers do not leak to the global scope
- Single-line comment at the top documenting the localStorage key (UI-SPEC § Copywriting Contract)
- Size budget: **under 400 bytes minified** (CONTEXT.md § Specifics paragraph 1)

Skeleton (the planner / executor will fill in the exact shape, but this is the pattern frame the IIFE must take):

```html
<script>
  // Theme bootstrap — reads localStorage key 'theme', falls back to OS prefers-color-scheme.
  (function () {
    let theme;
    try { theme = localStorage.getItem('theme'); } catch (_) { /* Safari private mode */ }
    if (theme !== 'light' && theme !== 'dark') {
      theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.dataset.theme = theme;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#100F0F' : '#FFFCF0');
  })();
</script>
```

**Optional partial extraction:** if the IIFE grows beyond ~12 lines (try/catch + matchMedia + dataset write + theme-color meta sync), extract to `themes/minimal/layouts/partials/theme-bootstrap.html` containing just the `<script>` element, then call it from `baseof.html` with `{{ partial "theme-bootstrap.html" . }}`. The partial mirrors the simplicity of `partials/header.html` and `partials/footer.html`. This is Claude's discretion (CONTEXT.md § Claude's Discretion bullet 6).

#### Toggle click handler — where it lives

The click handler is NOT in the IIFE (the IIFE only runs once at first paint). Per UI-SPEC § Interaction Specification, the click handler is a separate function that mutates state on each click. **Recommended host:** a second inline `<script>` block, placed at the end of `<body>` (just before `</body>` on line 18), so it runs after the toggle button has been parsed into the DOM. Alternatively, attach via `DOMContentLoaded` listener if kept inside `<head>`.

**No analog in repo for `<body>`-end inline scripts in templates** (existing inline scripts live only in blog post markdown). The pattern follows CONVENTIONS.md § JavaScript Conventions (vanilla ES6+, `const`/`let`, camelCase, no framework).

The handler MUST atomically perform 5 side effects (per UI-SPEC § Interaction Specification — toggle click handler):
1. Flip `document.documentElement.dataset.theme` between `'light'` and `'dark'`.
2. Flip toggle's `aria-pressed` (`'true'` ↔ `'false'`).
3. Update toggle's visible text content (`Dark` ↔ `Light`).
4. Write to `localStorage.setItem('theme', ...)` wrapped in try/catch.
5. Update `<meta name="theme-color">` `content` to match new `--bg` hex.

All five MUST live in a single function — do NOT split across multiple event listeners (CONTEXT.md § Specifics paragraph 2).

---

### `themes/minimal/layouts/partials/header.html` — append toggle button

**Self-analog:** the existing 10-line partial IS the pattern.

#### Existing partial (lines 1-10)

```html
<header class="site-header">
  <div class="site-title">
    <a href="{{ .Site.BaseURL }}">{{ .Site.Title }}</a>
  </div>
  <nav class="site-nav">
    {{ range .Site.Menus.main }}
      <a href="{{ .URL }}"{{ if $.IsMenuCurrent "main" . }} class="active"{{ end }}>{{ .Name }}</a>
    {{ end }}
  </nav>
</header>
```

**Pattern notes for the toggle insertion (per D-06 + UI-SPEC § Component Inventory):**

| Property | Value |
|----------|-------|
| Insertion site | Inside `<nav class="site-nav">`, **after** the closing `{{ end }}` of the `range .Site.Menus.main` loop (i.e., between line 8 and line 9) |
| Element | `<button type="button" class="theme-toggle" aria-pressed="false">Dark</button>` |
| Initial label / state | `Dark` and `aria-pressed="false"` (light-mode default; the IIFE may have already flipped `[data-theme="dark"]` on `<html>` before this partial renders, but server-side rendering writes the static HTML for light — the click handler / a separate post-IIFE sync step must update the button's text + `aria-pressed` to match the active theme on first paint) |
| Indentation | 2 spaces per HTML template convention; match the indentation of the `<a>` tag inside the `range` loop (4 spaces effective) |

**Server-side rendering caveat:** Hugo renders the button's initial HTML statically with `Dark` / `aria-pressed="false"`. If the IIFE detects that the persisted/preferred theme is dark, the button text and `aria-pressed` are now inconsistent with the dark `[data-theme="dark"]` palette. The bootstrap script (or an additional small sync block) MUST update the button's text content and `aria-pressed` attribute to match the active theme as soon as the button element is parseable. Two implementation options:

1. Run a sync step inside `DOMContentLoaded` from the head IIFE (small additional code in the same script block).
2. Make the click handler the ONLY source of label / `aria-pressed` mutation, and ensure the initial server-rendered HTML matches whatever `[data-theme]` value the IIFE will set. This requires synchronous DOM access to the button before paint, which is not possible from the head IIFE because the button is not yet parsed.

**Recommended:** option 1 — extend the head IIFE (or its companion script) to do a single DOM update of the button's text + `aria-pressed` once the DOM is ready. The body transition rule is `prefers-reduced-motion: no-preference`-gated, so the brief moment of an inconsistent label (Dark text on dark mode for one frame) is the structural compromise — but in practice the IIFE → button-sync sequence runs faster than the user can read.

**Hugo template variable:** none needed inside the button. The button's content is static plain text (`Dark`); JS mutates it on click. Do NOT use `{{ ... }}` template logic for the label.

#### Existing menu loop pattern (lines 6-8) — preserve idiomatic style

```html
{{ range .Site.Menus.main }}
  <a href="{{ .URL }}"{{ if $.IsMenuCurrent "main" . }} class="active"{{ end }}>{{ .Name }}</a>
{{ end }}
```

**Pattern note:** the new `<button>` line goes after the `{{ end }}` and before the closing `</nav>` — at indentation level 2 spaces from the `<nav>` opening (matching the `{{ range }}` line). Do NOT modify the menu loop itself; the toggle is purely additive.

---

## Shared Patterns

### CSS custom-property discipline (every color goes through `var(--token)`)

**Source:** `themes/minimal/static/css/style.css` lines 4-18 (light palette declaration) + every component-level rule (lines 50, 53, 58, 67, 74, 93, 98, 104, 110, 122, 129, 142, 157, 164, 184, 187, 194, 200, 205, 217, 225, 227, 232, 237 — every `var(--*)` reference).

**Apply to:** every new CSS rule in Phase 4. **Never hardcode hex values outside `:root` / `:root[data-theme="dark"]`.** The only exception is the `theme-color` meta JS handler, which must write literal hex strings (`#FFFCF0` / `#100F0F`) because the meta `content` attribute does not accept CSS variables.

```css
/* GOOD — theme-aware */
.theme-toggle:hover {
  color: var(--accent);
}

/* BAD — hardcoded, breaks in dark mode */
.theme-toggle:hover {
  color: #AF3029;
}
```

### Section-comment convention

**Source:** `themes/minimal/static/css/style.css` lines 1, 34, 41, 77, 114, 221, 258 (existing section headers).

**Pattern:**

```css
/* === Section Name === */
```

**Apply to:** any new logically distinct block. For Phase 4, no new section header is needed (the dark `:root` block lives in "Reset & Base", the body transition lives in "Reset & Base", and `.theme-toggle` rules live in "Header").

### Hugo template indentation (2 spaces, no tabs)

**Source:** every file under `themes/minimal/layouts/` — `baseof.html`, `partials/header.html`, `partials/footer.html` (not read here, but referenced in CONVENTIONS.md § HTML Template Conventions).

**Apply to:** all template insertions in `baseof.html` and `header.html`.

### Vanilla JS conventions

**Source:** CONVENTIONS.md § JavaScript Conventions (no in-template-file JS analog exists — the existing inline JS lives only in blog post markdown like `content/blog/2026-03-05-climbing-routes/index.md`).

**Apply to:** the IIFE in `baseof.html` and the toggle click handler.

| Rule | Apply |
|------|-------|
| `const` / `let` only (no `var`) | Yes |
| camelCase for functions / variables | Yes |
| Template literals for HTML string construction | Not applicable — no HTML construction in Phase 4 JS |
| `async`/`await` for data fetching | Not applicable — no fetching in Phase 4 |
| Console logging for debugging | Optional — keep silent for the toggle/IIFE since no error path produces useful info |

### Flexoki palette discipline

**Source:** CONVENTIONS.md § CSS Conventions (the `:root` block is the project's design-token contract).

**Apply to:** the dark palette block. Every dark-mode hex must be a Flexoki Base or Red shade per UI-SPEC § "Dark Palette" (D-03). Do not invent new colors.

---

## No Analog Found

The following Phase 4 elements have no in-repo precedent. Planner should reference UI-SPEC + CONVENTIONS.md instead of searching for analogs:

| Element | Reason | Alternative reference |
|---------|--------|-----------------------|
| Inline `<head>` IIFE for theme bootstrap | First inline `<head>` `<script>` in the project — all existing inline JS is in blog post markdown | UI-SPEC § "IIFE bootstrap" + CONVENTIONS.md § JavaScript Conventions |
| `<button>` element in a Hugo template | First `<button>` in any template — existing interactive elements are `<a>` links | UI-SPEC § "Component Inventory" (button reset rules) |
| `<meta name="color-scheme">` and `<meta name="theme-color">` | First non-trivial meta tags beyond `description` and `viewport` | UI-SPEC § "Theme-color meta sync" (D-14, D-15) |
| `:root[data-theme="dark"]` selector | First attribute-selector use of `:root` | UI-SPEC § "Dark Palette" (D-03) — token-for-token mirror of light `:root` |
| `@media (prefers-reduced-motion: no-preference)` rule | First reduced-motion media query in the project | UI-SPEC § "Body transition rule" (D-09 / D-10) |
| `:focus-visible` pseudo-class | First `:focus-visible` rule in the project | UI-SPEC § "Focus-visible Policy" |
| Optional `themes/minimal/layouts/partials/theme-bootstrap.html` (only if extracted) | Would be the third partial after `header.html` and `footer.html` | `partials/header.html` (10-line, template-only structure) is the closest precedent |

---

## Cross-Phase Pattern Notes

### Incoming from Phase 3 (resolved by D-01 / D-02)

Phase 3 recorded `--bg` / `--bg-dark` corner-pixel hex values (`#FEFEFE` / `#000000`) as a cross-phase contract for Phase 4. **Phase 4 deliberately supersedes** this contract for site-wide tokens — the new dark `--bg` is `#100F0F` (Flexoki Black), not `#000000`. The Phase 3 hex values move to Phase 5's wordmark-wrapper bg as a localized concern (CONTEXT.md § Cross-Phase Contracts).

**Pattern implication for Phase 4:** in `:root[data-theme="dark"]`, write `--bg: #100F0F;` — do NOT use `#000000`.

### Outgoing to Phase 5

Phase 5 selectors will key off `html[data-theme="dark"]` (set by Phase 4's IIFE on `document.documentElement`). The pattern is:

```css
/* Phase 5 will write this — no JS swap needed */
html[data-theme="dark"] .wordmark { /* dark-variant wordmark + #000000 wrapper bg */ }
```

**Pattern implication for Phase 4:** the IIFE MUST write `document.documentElement.dataset.theme` (which Hugo / browser exposes as the `data-theme` attribute). Do NOT write to `<body>` — Phase 5 keys off `<html>`.

---

## Metadata

**Analog search scope:** `themes/minimal/static/css/style.css` (264 lines, fully read), `themes/minimal/layouts/_default/baseof.html` (19 lines, fully read), `themes/minimal/layouts/partials/header.html` (10 lines, fully read), `.planning/codebase/CONVENTIONS.md` (235 lines, fully read).

**Files scanned:** 4 (3 modified files + 1 conventions doc).

**Pattern extraction approach:** since Phase 4 is purely additive to existing structures, every modified file serves as its own analog. The "find closest analog elsewhere in the codebase" step degenerates to "preserve the existing file's local conventions and append cleanly". This is the cleanest possible pattern-mapping outcome — no role/data-flow mismatch, no legacy-vs-current ambiguity, no abstraction gap.

**Pattern extraction date:** 2026-04-29.

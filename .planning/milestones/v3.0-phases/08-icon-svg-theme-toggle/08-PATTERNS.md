# Phase 8: ICON — SVG Theme Toggle - Pattern Map

**Mapped:** 2026-05-02
**Files analyzed:** 3 (modified) / 0 (created)
**Analogs found:** 3 / 3 (all in-codebase, exact or self-reference)

This phase is a **targeted edit pass** — every modified file has a known canonical analog already in the repo. No new file types, no new patterns introduced. The pattern map below is dense with line-anchored excerpts so the planner can write actions like "replace lines 101-115 with the icon-stack rules below" without re-reading source.

---

## File Classification

| File (modify) | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `themes/minimal/layouts/partials/header.html` (line 11) | template (partial) | server-render-only | `themes/minimal/layouts/partials/footer.html:6-18` (inline SVG icon convention) | exact (same Lucide convention, same file family) |
| `themes/minimal/layouts/_default/baseof.html` (lines 34-56) | template (base) + inline JS (IIFE) | event-driven (click) + DOM mutation | **self-reference** — `baseof.html:34-56` (rewriting an existing IIFE; preserve the shape, swap one responsibility) | exact (the file IS the analog) |
| `themes/minimal/static/css/style.css` (lines 101-122) | stylesheet | static cascade | `style.css:20-33` (`[data-theme="dark"]` palette swap — canonical theme-keyed rule) **+** `style.css:49-56` (`prefers-reduced-motion` gate) | exact (two existing patterns composed; both already in this file) |

**Files NOT modified (read for pattern reference only):**
- `themes/minimal/layouts/partials/footer.html` — visual convention source, do not touch
- `themes/minimal/layouts/_default/baseof.html` lines 11-23 — head IIFE bootstrap, do not touch (Pitfall 1 / no-FOUC contract)

---

## Pattern Assignments

### `themes/minimal/layouts/partials/header.html` (template, server-render-only)

**Analog:** `themes/minimal/layouts/partials/footer.html` (line numbers below are 1-based from the file)

**Context — current header (lines 1-13, the line-11 button is the only line that changes):**
```html
<header class="site-header">
  <div class="site-title">
    <a href="{{ .Site.BaseURL }}">
      {{ readFile "themes/minimal/static/images/brand/logo.svg" | safeHTML }}
    </a>
  </div>
  <nav class="site-nav">
    {{ range .Site.Menus.main }}
      <a href="{{ .URL }}"{{ if $.IsMenuCurrent "main" . }} class="active"{{ end }}>{{ .Name }}</a>
    {{ end }}
    <button type="button" class="theme-toggle" aria-pressed="false">Dark</button>     <!-- LINE 11: REPLACE -->
  </nav>
</header>
```

**Inline-SVG icon pattern to copy from `footer.html:6-18` (GitHub icon shown; copy structure, swap path data + width):**
```html
<a href="https://github.com/bohniti" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
       fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5..."></path>
    <path d="M9 18c-4.51 2-5-2-7-2"></path>
  </svg>
</a>
```

**Attributes to copy verbatim:** `xmlns`, `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`, `aria-hidden="true"`.

**Differences for header (per UI-SPEC):**
1. `width="24" height="24"` instead of `18` — header weight matches nav typography (UI-SPEC Spacing Scale).
2. Both SVGs sit **inside** the `<button>`, not anchors — outer container is the existing `.theme-toggle` button, not an `<a>`.
3. Add per-SVG class: `class="icon-sun"` and `class="icon-moon"` — these classes are the CSS visibility selectors (see style.css analog below).
4. Path data is hand-copied Lucide v0.547.0 `sun` (circle + 8 ray paths) and `moon` (single crescent path). Verbatim sources are in UI-SPEC § "Icon Source (D-01, D-02)".

**Replacement target (the new line 11 expands to ~15 lines):**
```html
<button type="button" class="theme-toggle" aria-pressed="false" aria-label="Switch to dark mode">
  <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
       fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- Lucide sun path data — see UI-SPEC -->
  </svg>
  <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
       fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- Lucide moon path data — see UI-SPEC -->
  </svg>
</button>
```

**Audit gates this pattern enforces (Pitfall 3, REQ ICON-03):**
- No literal `fill="#…"` or `stroke="#…"` — only `currentColor` and `fill="none"`.
- Both SVGs `aria-hidden="true"` (button is the labeled control — Sara Soueidan icon-button pattern).
- `aria-label` carries the action (Switch to ___ mode); the inner SVGs are decorative.

---

### `themes/minimal/layouts/_default/baseof.html` (template + inline IIFE, event-driven)

**Analog:** **the same file at lines 34-56** — the existing end-of-body IIFE is the closest analog because it already implements every responsibility we need except the icon-vs-text swap. The rewrite is a targeted edit, not a new pattern.

**Existing IIFE (lines 34-56) — current shape, copy structure, change only the marked lines:**
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
    toggle.textContent = initial === 'dark' ? 'Light' : 'Dark';   // LINE 45: REMOVE

    toggle.addEventListener('click', function () {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      toggle.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
      toggle.textContent = next === 'dark' ? 'Light' : 'Dark';    // LINE 51: REMOVE
      try { localStorage.setItem('theme', next); } catch (_) { /* Safari private mode */ }
      if (meta) meta.setAttribute('content', next === 'dark' ? '#100F0F' : '#FFFCF0');
    });
  })();
</script>
```

**Preserved patterns (must remain identical):**
- IIFE wrapper `(function () { … })();` — module pattern used throughout the codebase
- Null-guard `if (!toggle) return;` — defensive against partial loads
- `try { localStorage.setItem(…) } catch (_) {}` — Safari private mode safety (Pitfall 22 sibling)
- `meta` lookup + content attribute write — `theme-color` meta sync (Pitfall 22, D-12)
- "First-paint sync" reconciliation block — head IIFE may have resolved a theme that the server-rendered HTML does not reflect

**Single-responsibility swap (D-10, D-11):**

| What | From (current) | To (new) |
|------|----------------|----------|
| Initial sync (line 45) | `toggle.textContent = initial === 'dark' ? 'Light' : 'Dark';` | `toggle.setAttribute('aria-label', initial === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');` |
| Click handler (line 51) | `toggle.textContent = next === 'dark' ? 'Light' : 'Dark';` | `toggle.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');` |

**Forbidden additions (Pitfall 22, D-10):**
- Do NOT query the SVG elements (no `.icon-sun` / `.icon-moon` selectors in JS)
- Do NOT toggle classes on either SVG
- Do NOT set `display`, `opacity`, `hidden`, or any visual property on the SVGs
- The icon visibility is **100% CSS-driven** via `[data-theme]` on `<html>` — JS only writes `dataset.theme`

**Lines NOT touched in this file:**
- Lines 1-10 (head metadata)
- Lines 11-23 (head theme-bootstrap IIFE — modifying it is a no-FOUC contract violation)
- Lines 24-33 (stylesheet link, body wrapper, partials, main, footer)

---

### `themes/minimal/static/css/style.css` (stylesheet, static cascade)

**Analogs (two patterns composed):**
1. **`style.css:20-33`** — canonical `:root[data-theme="dark"] { … }` palette-swap pattern. Confirmed via `grep -n 'data-theme'`: this is the **only** existing `[data-theme]` selector in the entire stylesheet. The icon-visibility rules extend this exact selector idiom.
2. **`style.css:49-56`** — canonical `@media (prefers-reduced-motion: no-preference)` gate. Only one such block exists; the icon transition mirrors it.

**Pattern 1 — `[data-theme]`-keyed swap (style.css:20-33):**
```css
:root[data-theme="dark"] {
  /* Flexoki-inspired dark palette */
  --bg: #100F0F;
  --bg-secondary: #1C1B1A;
  --text: #CECDC3;
  --text-secondary: #878580;
  /* … */
}
```
**Application to icon visibility:** the new rules use the same `:root[data-theme="…"]` prefix to scope visibility:
```css
:root[data-theme="dark"] .theme-toggle .icon-sun { opacity: 0; pointer-events: none; }
:root[data-theme="light"] .theme-toggle .icon-moon,
:root:not([data-theme="dark"]) .theme-toggle .icon-moon { opacity: 0; pointer-events: none; }
```
The `:root:not([data-theme="dark"])` fallback is defensive against the (architecturally impossible but cheap-to-cover) case where the head IIFE has not yet written `data-theme`.

**Pattern 2 — `prefers-reduced-motion` gate (style.css:49-56):**
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
**Application to icon transition:** mirror the structure exactly — wrap the opacity transition in the same media query so reduced-motion users get an instant swap (no transition declared at all):
```css
@media (prefers-reduced-motion: no-preference) {
  .theme-toggle .icon-sun,
  .theme-toggle .icon-moon {
    transition: opacity 150ms ease;
  }
}
```
**Pitfall 9 mitigation:** do not declare the `transition` outside this media query and then override it inside — the spec intent is **zero unrequested motion** for reduced-motion users (UI-SPEC §Transition Contract).

**Current `.theme-toggle` block to rewrite (style.css:101-122):**
```css
.theme-toggle {
  /* match .site-nav a typography (D-08) */
  font: inherit;             /* REMOVE — no text rendered (D-11) */
  font-size: 0.95rem;        /* REMOVE — no text rendered (D-11) */
  color: var(--text-secondary);
  /* button reset */
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.theme-toggle:hover {
  color: var(--accent);     /* KEEP verbatim — hover state for icon stroke via currentColor */
}

.site-nav a:focus-visible,
.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);   /* KEEP verbatim — focus ring on button shell */
  outline-offset: 2px;
  border-radius: 2px;
}
```

**New rules to add inside the rewritten block (icon stacking + visibility + transition):**
```css
.theme-toggle {
  display: inline-grid;
  place-items: center;
  min-width: 44px;       /* WCAG 2.5.5 / iOS HIG hit target — D-06, REQ ICON-04 */
  min-height: 44px;
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
  color: var(--text-secondary);
}

.theme-toggle .icon-sun,
.theme-toggle .icon-moon {
  grid-area: 1 / 1;       /* stack in the same grid cell — no layout reflow on swap */
  display: block;
}

/* Icon visibility keyed off [data-theme] on <html> — extends style.css:20 pattern */
:root[data-theme="dark"] .theme-toggle .icon-sun {
  opacity: 0;
  pointer-events: none;
}
:root[data-theme="light"] .theme-toggle .icon-moon,
:root:not([data-theme="dark"]) .theme-toggle .icon-moon {
  opacity: 0;
  pointer-events: none;
}

/* Cross-fade — mirrors style.css:49-56 prefers-reduced-motion pattern */
@media (prefers-reduced-motion: no-preference) {
  .theme-toggle .icon-sun,
  .theme-toggle .icon-moon {
    transition: opacity 150ms ease;
  }
}

.theme-toggle:hover { color: var(--accent); }    /* unchanged */

.site-nav a:focus-visible,
.theme-toggle:focus-visible {                    /* unchanged */
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```

**Mobile reflow note (style.css:399):**
The existing `@media (max-width: 600px) { .site-header { flex-direction: column; … } }` reflows the header into a single column under 600 px. The 44 × 44 hit target on `.theme-toggle` is unaffected — `min-width`/`min-height` survive the column reflow because they are not flex-cross-axis-stretched. Verify during HUMAN-UAT but **do not add a separate mobile rule** — the existing breakpoint is sufficient.

---

## Shared Patterns

### Pattern: Inline SVG with `currentColor`
**Source:** `themes/minimal/layouts/partials/footer.html:7-17` and `themes/minimal/static/css/style.css:124-130` (wordmark — `.site-title svg { color: var(--text); }`)
**Apply to:** All new SVGs in `header.html` (sun + moon)
**Contract:**
- `stroke="currentColor"` and `fill="none"` on the `<svg>` element
- Color comes from the parent's `color` CSS property — set on `.theme-toggle` as `var(--text-secondary)` idle, `var(--accent)` on `:hover`
- No literal `#hex` colors anywhere in the SVG markup (Pitfall 3 audit gate: `grep -E 'fill="#|stroke="#"' themes/minimal/layouts/partials/header.html` must return zero)

### Pattern: `[data-theme]` on `<html>` as single source of truth
**Source:** `themes/minimal/static/css/style.css:20` (only `[data-theme]` selector in the file) + `baseof.html:19` (only place JS writes the attribute)
**Apply to:** Icon visibility rules (CSS reads `[data-theme]`), JS click handler (writes `documentElement.dataset.theme = next` and nothing else theme-related)
**Contract:** JS never touches the SVGs. CSS never reads from JS-set classes. The single mutation `dataset.theme = next` cascades through the palette, the icon visibility, and (via the same handler's meta write) the `theme-color` meta tag.

### Pattern: `@media (prefers-reduced-motion: no-preference)` motion gating
**Source:** `themes/minimal/static/css/style.css:49-56` (the only such block in the file)
**Apply to:** The new icon opacity transition
**Contract:** All `transition` and `animation` declarations for the icon sit **inside** the media query block. Reduced-motion users get an instant swap — no fallback transition is declared.

### Pattern: IIFE click handler with localStorage try/catch
**Source:** `themes/minimal/layouts/_default/baseof.html:36-55` (existing toggle handler) + `baseof.html:13-22` (existing head bootstrap)
**Apply to:** The rewritten end-of-body click handler
**Contract:** `(function () { … })()` wrapper, `if (!toggle) return` null guard, `try { localStorage.setItem(…) } catch (_) {}` for Safari private mode, `meta[name="theme-color"]` content-attribute sync inside the same handler (D-12).

### Pattern: Accessible icon-button (`aria-label` on button + `aria-hidden` on inner SVGs)
**Source:** `themes/minimal/layouts/partials/footer.html:6` (`aria-label="GitHub"` on `<a>`) + `footer.html:7,13` (`aria-hidden="true"` on `<svg>`)
**Apply to:** New `.theme-toggle` button + both inner SVGs
**Contract:** The button is the **labeled control** (`aria-label="Switch to … mode"`); both SVGs are **decorative** (`aria-hidden="true"`). Action-orientation: label describes the click target, icon depicts the current state (D-03, D-08).

---

## No Analog Found

None. Every file modified by this phase has a canonical analog already in the codebase (and in two of three cases the analog is in the very same file). The phase is structurally a "copy the footer SVG convention into the header, extend the existing CSS swap pattern, swap one line in the existing click handler." No greenfield patterns are introduced.

---

## Metadata

**Analog search scope:** `themes/minimal/` (templates, partials, CSS), `.planning/research/` (SUMMARY, ARCHITECTURE references)
**Files scanned:** 4 source files (`header.html`, `footer.html`, `baseof.html`, `style.css`) + 3 planning docs (`08-CONTEXT.md`, `08-UI-SPEC.md`, `SUMMARY.md`)
**Pattern extraction date:** 2026-05-02
**Confidence:** HIGH — every extracted excerpt is verbatim from a current source file with line numbers verified against the live working tree

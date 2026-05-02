# Phase 9: ABOUT — Dynamic Rounded Redesign — Pattern Map

**Mapped:** 2026-05-02
**Files analyzed:** 7 (4 NEW + 3 MODIFIED)
**Analogs found:** 7 / 7 (every new/modified file has at least one in-repo precedent)

---

## File Classification

| New / Modified File | Status | Role | Data Flow | Closest Analog | Match Quality |
|---------------------|--------|------|-----------|----------------|---------------|
| `themes/minimal/layouts/about/single.html` | NEW | layout (Hugo type-routed) | request-response (build-time render) | `themes/minimal/layouts/gallery/single.html` | exact (same role: dedicated `layouts/{type}/single.html`; same data flow: leaf bundle → static HTML; same `{{ define "main" }}` block pattern) |
| `themes/minimal/layouts/shortcodes/split.html` | NEW | shortcode (Hugo template) | transform (markdown body → HTML wrapper) | `themes/minimal/layouts/shortcodes/mermaid.html` | role-match (same role: shortcode template; different data flow — mermaid emits a script-companion, split is pure wrapper) |
| `themes/minimal/layouts/shortcodes/pullquote.html` | NEW | shortcode (Hugo template) | transform (markdown body → HTML wrapper) | `themes/minimal/layouts/shortcodes/mermaid.html` + raw `<aside>` at `content/about/index.md:35-37` | exact (mermaid is the only existing shortcode = the only role analog; the migration target HTML lives at index.md:35-37 — a byte-identical match) |
| `themes/minimal/layouts/shortcodes/feature.html` | NEW (optional) | shortcode (Hugo template) | transform (markdown body → HTML wrapper) | `themes/minimal/layouts/shortcodes/mermaid.html` | role-match (same as split — shortcode template authoring; figure-flavored output) |
| `themes/minimal/layouts/_default/_markup/render-image.html` | MODIFIED | render hook (Hugo) | transform (image resource → sized `<img>`) | itself, lines 1-21 (extend the existing 3-arm switch) | exact (same file; additive `else if` branches) |
| `themes/minimal/static/css/style.css` (`/* === About === */`) | MODIFIED | stylesheet section | declarative (CSS cascade) | itself, lines 340-391 (rewrite in place) + lines 431-444 (mobile reflow extension) | exact (same file, same section, same scoping convention) |
| `content/about/index.md` | MODIFIED | content (Hugo leaf bundle index) | content authoring | itself, lines 1-79 (rewrite per CONTEXT D-02, D-09, D-14) | exact (same file; structural rewrite preserving prose) |

---

## Pattern Assignments

### `themes/minimal/layouts/about/single.html` (NEW — layout, request-response)

**Analog:** `themes/minimal/layouts/gallery/single.html` (entire file, 28 LOC)

**Why this analog:** Both files are dedicated `layouts/{type}/single.html` templates that own a custom structural shell for a specific content type. Gallery (`type: "gallery"`) is the only existing precedent for the type-routed pattern that the new About layout must follow per D-13.

**Block-define pattern** (gallery/single.html:1-2, 27-28):
```go-html-template
{{ define "main" }}
  <article>
    ...
  </article>
{{ end }}
```
The new About layout MUST open with `{{ define "main" }}` and close with `{{ end }}` so it slots into `baseof.html` line 30 (`{{ block "main" . }}{{ end }}`). The outer wrapper element should be `<article>` (gallery uses it; UI-SPEC §"Page-level skeleton" specifies `<article class="about">`).

**Resource access pattern** (gallery/single.html:6, 10-11):
```go-html-template
{{ with .Resources.Match "photos/*" }}
  ...
  {{ $thumb := $photo.Process "fill 600x400 Smart webp q75" }}
  {{ $full  := $photo.Process "fit 1200x1200 webp q78" }}
```
Gallery proves `.Resources.Match` + `image.Process` directly inside the layout template works. About's hero portrait is rendered through the render-image hook (markdown image with `"hero"` title), but if any layout-level image work is needed (e.g., a layout-emitted feature image), the gallery pattern is the precedent.

**Title-as-page-header pattern** (gallery/single.html:3-5):
```go-html-template
<div class="page-header">
  <h1 class="page-title">{{ .Title }}</h1>
</div>
```
About's hero subsumes the page header (the `<h2>Hi, I'm Timo.</h2>` serves the page-introduction role). The new layout deliberately does NOT use `.page-header` — UI-SPEC §"Page-level skeleton" omits it. This is a divergence from the gallery analog and should be noted in the plan: gallery shows what NOT to copy (page-header chrome doesn't fit About's narrative hero).

**Content rendering pattern** (`themes/minimal/layouts/_default/single.html:9-11`):
```go-html-template
<div class="page-content">
  {{ .Content }}
</div>
```
The default single template is the precedent for `{{ .Content }}` rendering of the markdown body. The new About layout will render markdown content but NOT inside a `.page-content` wrapper (UI-SPEC scopes everything under `body.page-about` and uses `.about-*` classes). The `{{ .Content }}` invocation pattern carries forward, but the wrapper class does not.

**Routing confirmation** (`themes/minimal/layouts/_default/baseof.html:26`):
```html
<body class="page-{{ .Type | default "default" }}">
```
Confirms `body.page-about` activates automatically when `type: "about"` is set in front-matter. No JS, no extra config. (Already the case; `content/about/index.md:3` declares `type: "about"`.)

---

### `themes/minimal/layouts/shortcodes/pullquote.html` (NEW — shortcode, transform)

**Analog 1 (role/structure):** `themes/minimal/layouts/shortcodes/mermaid.html` lines 1-3
**Analog 2 (target HTML):** `content/about/index.md:35-37` (raw aside the shortcode replaces)

**Mermaid wrapper pattern** (mermaid.html:1-3):
```go-html-template
<div class="mermaid">
{{ .Inner | safeHTML }}
</div>
```
Direct precedent for a shortcode that wraps `.Inner` in a single classed element. The new pullquote shortcode follows the same shape; the only deltas are:
- element: `<div>` → `<aside>` (semantic for callout)
- class: `mermaid` → `about-pullquote`
- pipeline: `safeHTML` → `markdownify` (so `**40% → 95%**` inside the shortcode body renders as `<strong>40% → 95%</strong>`)

**Target HTML** (`content/about/index.md:35-37`, raw HTML to be replaced):
```html
<aside class="about-pullquote">
Improved message routing accuracy from <strong>40% → 95%</strong>
</aside>
```
The shortcode MUST emit byte-identical HTML to this raw-HTML block (modulo whitespace) per D-09 / REQ ABOUT-06. UI-SPEC §"Pullquote contract" provides the verbatim ~5-LOC template:
```go-html-template
<aside class="about-pullquote">
{{ .Inner | markdownify }}
</aside>
```
The `markdownify` pipe is load-bearing — the markdown body `**40% → 95%**` only renders to `<strong>40% → 95%</strong>` if `markdownify` is applied. Plain `safeHTML` would emit literal asterisks.

**CSS contract preserved** (`themes/minimal/static/css/style.css:357-375`):
```css
body.page-about .about-pullquote {
  font-size: 1.4rem;
  font-weight: 500;
  line-height: 1.4;
  color: var(--text);
  border-left: 4px solid var(--accent);
  padding: 0.5rem 0 0.5rem 1.25rem;
  margin: 1.75rem 0;
  background: var(--bg-secondary);
  border-radius: 0 4px 4px 0;
}

/* Dark-mode #D14D41 on #1C1B1A measures 3.97:1 — passes WCAG AA only because the
   inherited 1.4rem + font-weight:700 qualifies as "large text" (≥14pt bold).
   Do not reduce font-size or font-weight here without re-checking contrast. */
body.page-about .about-pullquote strong {
  color: var(--accent);
  font-weight: 700;
}
```
The contrast comment at lines 369-371 is **load-bearing** — preserve verbatim per D-09 / REQ ABOUT-06 / Pitfall 15.

---

### `themes/minimal/layouts/shortcodes/split.html` (NEW — shortcode, transform)

**Analog (role/structure):** `themes/minimal/layouts/shortcodes/mermaid.html` lines 1-3 (same one-element wrapper around `.Inner`)

**Argument-driven variant pattern (no in-repo precedent, but UI-SPEC-locked):**

Mermaid does not use positional arguments — it has zero. The new split shortcode introduces `.Get 0` for variant selection, which is a Hugo built-in. The closest in-repo precedent for a parametrized template is the render-image hook itself (`render-image.html:3` uses `.Title | default ""`), which the new shortcode mirrors:

**Default-with-fallback pattern** (`render-image.html:3`):
```go-html-template
{{- $title := .Title | default "" -}}
```
The split shortcode applies the same default idiom for its positional arg:
```go-html-template
{{- $variant := .Get 0 | default "text-first" -}}
```

**Full template** (UI-SPEC §"`{{< split >}}` shortcode template" — verbatim target):
```go-html-template
{{- /* Args: (1) variant — "text-first" (default) | "image-first" */ -}}
{{- $variant := .Get 0 | default "text-first" -}}
{{- $class := printf "about-split about-split--%s" $variant -}}
<div class="{{ $class }}">
{{ .Inner | markdownify }}
</div>
```

**`markdownify` over `safeHTML`** rationale: markdown body of split contains a paragraph + a markdown image (e.g., `![alt](images/foo.jpg "split")`). `markdownify` renders the markdown so the image fires the render-image hook. `safeHTML` would emit raw markdown unprocessed.

---

### `themes/minimal/layouts/shortcodes/feature.html` (NEW — optional, shortcode, transform)

**Analog:** `themes/minimal/layouts/shortcodes/mermaid.html` lines 1-3 (same one-element wrapper pattern)

**Full template** (UI-SPEC §"`{{< feature >}}` shortcode template" — verbatim target):
```go-html-template
{{- /* A single full-width focal image with optional caption.
       Markdown body should be image-only or image+single-line caption. */ -}}
<figure class="about-feature">
{{ .Inner | markdownify }}
</figure>
```

**Element choice rationale:** `<figure>` is the semantic primitive for self-contained referenced content (HTML5 spec). Mermaid uses `<div>` because mermaid output is not semantically a figure. Feature is.

**Ship-or-drop:** D-05 + UI-SPEC §"Files Modified by This Phase" mark feature as planner discretion. UI-SPEC recommends shipping the shortcode + hook arm even if unused initially (~16 LOC of cheap design slack). The plan should call this out as the only optional artifact.

---

### `themes/minimal/layouts/_default/_markup/render-image.html` (MODIFIED — render hook, transform)

**Analog:** itself, lines 1-21 — the file is its own pattern. Phase 7 established the title-keyed switch; Phase 9 extends additively per D-07 / Pitfall 14.

**Existing 3-arm switch** (verbatim, lines 1-21 — the contract to preserve):
```go-html-template
{{- $resource := .Page.Resources.GetMatch (printf "%s" .Destination) -}}
{{- if $resource -}}
  {{- $title := .Title | default "" -}}
  {{- $isHero := eq $title "hero" -}}
  {{- $isGrid := eq $title "grid" -}}
  {{- $processed := "" -}}
  {{- if $isHero -}}
    {{- $processed = $resource.Process "fill 480x600 Smart webp q80" -}}
  {{- else if $isGrid -}}
    {{- $processed = $resource.Process "fill 400x300 Smart webp q75" -}}
  {{- else -}}
    {{- $processed = $resource.Process "fill 800x600 Smart webp q78" -}}
  {{- end -}}
  <img src="{{ $processed.RelPermalink }}"
       width="{{ $processed.Width }}"
       height="{{ $processed.Height }}"
       alt="{{ .Text }}"
       {{- if $isHero }} class="about-hero-img" loading="eager" fetchpriority="high"{{ else if $isGrid }} class="about-grid-item" loading="lazy" decoding="async"{{ else }} loading="lazy" decoding="async"{{ end -}}>
{{- else -}}
  <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}"{{ with .Title }} title="{{ . }}"{{ end }}>
{{- end -}}
```

**Extension rules** (Pitfall 14 — applies first, before any markdown rewrite):
1. Add `{{- $isSplit := eq $title "split" -}}` after line 5 (`$isGrid` declaration).
2. Add `{{- $isFeature := eq $title "feature" -}}` after the `$isSplit` declaration (only if feature ships per D-05).
3. Insert `else if $isSplit` branch in the `image.Process` switch BEFORE the default `else`.
4. Insert `else if $isFeature` branch in the `image.Process` switch BEFORE the default `else` (only if feature ships).
5. Append matching class branches to the `<img>` attribute mux (lines 14-18).
6. **Preserve verbatim:** the passthrough fallback at lines 19-21 (`{{- else -}}` … `{{- end -}}`). Pitfall 14 marks this as load-bearing.
7. **Preserve verbatim:** existing `hero` and `grid` arm parameters (`fill 480x600 Smart webp q80`, `fill 400x300 Smart webp q75`) and the default arm (`fill 800x600 Smart webp q78`).

**New arm parameters** (UI-SPEC §"Render-image hook contract" — locked):
| New arm | `image.Process` parameters | Rendered class | Loading |
|---------|----------------------------|----------------|---------|
| `split` | `fit 600x450 webp q78` (no Smart, no fill) | `about-split-img` | `lazy` + `decoding="async"` |
| `feature` (optional) | `fill 1024x576 Smart webp q80` (16:9 wide focal) | `about-feature-img` | `lazy` + `decoding="async"` |

**Final extended template** (UI-SPEC §"Hook implementation pattern" — verbatim target shape):
```go-html-template
{{- $resource := .Page.Resources.GetMatch (printf "%s" .Destination) -}}
{{- if $resource -}}
  {{- $title := .Title | default "" -}}
  {{- $isHero    := eq $title "hero" -}}
  {{- $isGrid    := eq $title "grid" -}}
  {{- $isSplit   := eq $title "split" -}}
  {{- $isFeature := eq $title "feature" -}}
  {{- $processed := "" -}}
  {{- if $isHero -}}
    {{- $processed = $resource.Process "fill 480x600 Smart webp q80" -}}
  {{- else if $isGrid -}}
    {{- $processed = $resource.Process "fill 400x300 Smart webp q75" -}}
  {{- else if $isSplit -}}
    {{- $processed = $resource.Process "fit 600x450 webp q78" -}}
  {{- else if $isFeature -}}
    {{- $processed = $resource.Process "fill 1024x576 Smart webp q80" -}}
  {{- else -}}
    {{- $processed = $resource.Process "fill 800x600 Smart webp q78" -}}
  {{- end -}}
  <img src="{{ $processed.RelPermalink }}"
       width="{{ $processed.Width }}"
       height="{{ $processed.Height }}"
       alt="{{ .Text }}"
       {{- if $isHero }} class="about-hero-img" loading="eager" fetchpriority="high"
       {{- else if $isGrid }} class="about-grid-item" loading="lazy" decoding="async"
       {{- else if $isSplit }} class="about-split-img" loading="lazy" decoding="async"
       {{- else if $isFeature }} class="about-feature-img" loading="lazy" decoding="async"
       {{- else }} loading="lazy" decoding="async"
       {{- end -}}>
{{- else -}}
  <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}"{{ with .Title }} title="{{ . }}"{{ end }}>
{{- end -}}
```

---

### `themes/minimal/static/css/style.css` (MODIFIED — stylesheet section, declarative)

**Analog:** itself — three blocks targeted, each with its own existing pattern.

#### Block 1: `:root` palette declaration (style.css:4-18)

**Existing pattern** (style.css:4-17):
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

**Extension rule (D-08):** Add a single line `--radius-soft: 12px;` inside the `:root` block. UI-SPEC §"`--radius-soft` token contract" recommends placing it adjacent to `--max-width` (line 17) since both are non-color tokens, OR as a sibling under a `/* Radius tokens */` sub-comment if section-comment style is preferred. Plan can pick either; the latter is more readable for future tokens.

**Do NOT touch:** Dark-theme block at `:root[data-theme="dark"]` (lines 20-33). The radius token is theme-invariant.

#### Block 2: `/* === About === */` section (style.css:340-391)

**Existing rules to preserve in shape, with surgical radius swaps:**

`body.page-about .about-hero` (lines 341-347) — UNCHANGED:
```css
body.page-about .about-hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: start;
  margin-bottom: 2.5rem;
}
```
Phase 7 pattern; preserved verbatim per CONTEXT decisions / UI-SPEC §"Hero contract".

`body.page-about .about-hero-photo img, .about-hero-img` (lines 349-355) — RADIUS SWAP only:
```css
/* BEFORE (line 353): border-radius: 6px; */
/* AFTER:             border-radius: var(--radius-soft); */
```

`body.page-about .about-pullquote` (lines 357-367) — UNCHANGED (D-08 explicit; one-sided radius is the visual signal pairing with the 4 px `border-left`).

Contrast comment + `.about-pullquote strong` rule (lines 369-375) — **PRESERVED VERBATIM** (REQ ABOUT-06 / Pitfall 15 hard gate).

`body.page-about .about-grid` (lines 377-382) — UNCHANGED.

`body.page-about .about-grid img, .about-grid-item` (lines 384-391) — RADIUS SWAP only:
```css
/* BEFORE (line 389): border-radius: 4px; */
/* AFTER:             border-radius: var(--radius-soft); */
/* line 390 cascade-override comment "RESEARCH amendment 1" PRESERVED verbatim */
```

**New rules to add (UI-SPEC §"Role-card visual contract", §"Asymmetric ratios", §"`{{< feature >}}`"):**

Role-card cluster (~50 LOC):
```css
body.page-about .about-section { margin-top: 3.5rem; }

body.page-about .about-role-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 1.5rem;
}

body.page-about .about-role-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-soft);
  padding: 1.5rem;
  margin: 0;
}

body.page-about .about-role-card-title {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text);
  margin: 0 0 0.25rem;
}

body.page-about .about-role-card-meta {
  font-size: 0.85rem;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-secondary);
  margin: 0 0 0.75rem;
}

body.page-about .about-role-card ul {
  margin: 0;
  padding-left: 1.25rem;
  list-style: disc;
}

body.page-about .about-role-card li {
  margin: 0 0 0.25rem;
  line-height: 1.6;
  color: var(--text);
}

body.page-about .about-role-card li:last-child { margin-bottom: 0; }
```

Split-row cluster (~10 LOC):
```css
body.page-about .about-split {
  display: grid;
  gap: 2rem;
  align-items: start;
  margin: 2.5rem 0;
}
body.page-about .about-split--text-first { grid-template-columns: 2fr 1fr; }
body.page-about .about-split--image-first { grid-template-columns: 1fr 2fr; }
```

Feature cluster (~10 LOC, only if shortcode ships):
```css
body.page-about .about-feature {
  margin: 2.5rem 0;
  border-radius: var(--radius-soft);
  overflow: hidden;
}
body.page-about .about-feature-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: var(--radius-soft);
  margin: 0;
}
```

**Scoping invariant (D-12, Pitfall 17 hard gate):** Every new rule MUST be prefixed `body.page-about`. Class names MUST use `.about-` prefix. Forbidden generic class names: `.card`, `.section`, `.feature`, `.role`, `.row`, `.split`. Every rule above honors this.

#### Block 3: Mobile reflow `@media (max-width: 600px)` (style.css:431-444)

**Existing pattern** (lines 431-444):
```css
@media (max-width: 600px) {
  html { font-size: 16px; }
  .site-header { flex-direction: column; gap: 0.5rem; }
  .site-wrapper { padding: 2rem 0 4rem; }
  .footer-links { gap: 1rem; }
  .site-title svg { width: 160px; height: 98px; }
  body.page-about .about-hero {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  body.page-about .about-grid {
    grid-template-columns: 1fr;
  }
}
```

**Extension rule (D-10):** Add new collapse rules INSIDE this existing `@media` block. No new breakpoint. UI-SPEC §"Mobile reflow contract" provides verbatim additions:
```css
body.page-about .about-section { margin-top: 2.5rem; }
body.page-about .about-split,
body.page-about .about-split--text-first,
body.page-about .about-split--image-first {
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
body.page-about .about-role-list { gap: 1rem; }
body.page-about .about-role-card { padding: 1.25rem; }
body.page-about .about-feature { margin: 2rem 0; }
```

**Out of scope** (must NOT be touched per D-08, P17):
- `.page-content img` rule at style.css:256-261 (site-wide; affects blog + gallery).
- Body transition at style.css:49-56.
- Gallery rules at style.css:310-338.
- Dark-theme palette block at style.css:20-33.

---

### `content/about/index.md` (MODIFIED — content authoring)

**Analog:** itself, lines 1-79 — rewrite per D-02, D-09, D-14.

**Existing structure** (lines 1-79):
```markdown
---
title: "About"
type: "about"
---

<div class="about-hero">
<div class="about-hero-text">

## Hi, I'm Timo.

I'm a Senior Data Science Consultant at [Erste Group]…

[Download full CV (PDF)](/files/timo-bohnstedt-cv.pdf)

</div>
<div class="about-hero-photo">

![Portrait of Timo](images/portrait.jpg "hero")

</div>
</div>

---

## Experience (Highlights)

**Senior Data Science Consultant** — Erste Group, Vienna *(since 09/2023)*
- Built an AI platform on Azure & Databricks serving 7,000 daily users across five countries
- …

<aside class="about-pullquote">
Improved message routing accuracy from <strong>40% → 95%</strong>
</aside>
…
## Interests

Bouldering, cycling, running, cooking, and reading…

<div class="about-grid">

![Bouldering at the climbing gym](images/climbing.jpg "grid")
…
</div>
```

**Rewrite rules** (D-02, D-09, D-14 + UI-SPEC §"Copywriting Contract"):

1. **Drop** `<div class="about-hero">…</div>` wrapper at lines 6-23 (D-14). Hero shell now lives in `layouts/about/single.html`. Markdown body becomes prose-only inside the hero.
2. **Replace** `<aside class="about-pullquote">…</aside>` at lines 35-37 with `{{< pullquote >}}` shortcode invocation (D-09):
   ```markdown
   {{< pullquote >}}
   Improved message routing accuracy from **40% → 95%**
   {{< /pullquote >}}
   ```
3. **Drop** `<div class="about-grid">…</div>` wrapper at lines 68-78. New layout's "Outside Work" section owns the grid wrapper. The 4 image lines (`![alt](images/x.jpg "grid")`) survive — only the `<div>` wrapper is removed.
4. **Rename** H2 at line 27: `## Experience (Highlights)` → `## Experience` (UI-SPEC: drop the `(Highlights)` parenthetical).
5. **Rename** H2 at line 64: `## Interests` → `## Outside Work` (D-02 framing; UI-SPEC §"Section copy").
6. **Restructure** Experience body (lines 29-44) as 3 role-card data blocks. Authoring convention is planner's call (D-06 "card is NOT a shortcode" — layout reads structured markdown directly). UI-SPEC §"Role-card copy contract" specifies the canonical content for all 3 cards.
7. **Preserve verbatim:** front-matter (`title`, `type: "about"`); CV link (line 15); pullquote stat content; all 4 hobby image alt texts (lines 70-76); all Education + Certifications bullet content (lines 50-60); Outside Work lead paragraph (line 66).

---

## Shared Patterns

### Shared Pattern 1: `body.page-{type}` CSS scoping (Pitfall 17 hard gate)

**Source:** `themes/minimal/layouts/_default/baseof.html:26`
```html
<body class="page-{{ .Type | default "default" }}">
```

**Source CSS precedent:** `themes/minimal/static/css/style.css:341` (existing About rule):
```css
body.page-about .about-hero { … }
```

**Apply to:** Every new CSS rule added by Phase 9 to `style.css`. No exceptions. The lint grep gate is:
```bash
grep -nE '^\.about-' themes/minimal/static/css/style.css
# Must return 0 matches — every .about-* selector must be inside a body.page-about prefixed rule.

grep -nE '^\.(card|section|feature|role|row|split)\b' themes/minimal/static/css/style.css
# Must return 0 matches — generic class names are forbidden.
```

### Shared Pattern 2: Flexoki palette token references (Pitfall 3 carry-forward)

**Source:** `themes/minimal/static/css/style.css:4-33` (`:root` + `:root[data-theme="dark"]`)

**Apply to:** Every new color reference in Phase 9 CSS. Use `var(--bg)`, `var(--bg-secondary)`, `var(--text)`, `var(--text-secondary)`, `var(--accent)`, `var(--border)` — never hex literals.

**Lint grep:**
```bash
grep -nE '#[0-9A-Fa-f]{3,8}' themes/minimal/static/css/style.css \
  | grep -E 'about-|page-about|--radius-soft'
# Must return 0 matches — Phase 9 introduces zero hex literals outside :root palette.
```

### Shared Pattern 3: `prefers-reduced-motion: no-preference` gating

**Source:** `themes/minimal/static/css/style.css:49-56` (existing body transition):
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

**Apply to:** Phase 9 declares ZERO new motion (D-11). If a future override adds any `transition` / `animation` / `transform` / `@keyframes` to About, it MUST be inside a `@media (prefers-reduced-motion: no-preference)` block. The default contract is stillness.

### Shared Pattern 4: Hugo `image.Process` for build-time image work

**Source:** `themes/minimal/layouts/_default/_markup/render-image.html:7-12` (existing arms) and `themes/minimal/layouts/gallery/single.html:10-11` (gallery thumbs+full).

**Apply to:** All new render-image arms (`split`, `feature`). The hook is the only path Phase 9 uses to process About images. Layout templates do NOT call `image.Process` directly for About — they emit markdown image references that the hook intercepts. (Gallery is the exception: it processes images directly in the layout because gallery doesn't have a render-image-keyed authoring model.)

### Shared Pattern 5: Hugo shortcode `.Inner | markdownify` pipeline

**Source (in-repo precedent for `.Inner`):** `themes/minimal/layouts/shortcodes/mermaid.html:2`:
```go-html-template
{{ .Inner | safeHTML }}
```

**Apply to:** All three new shortcodes (pullquote, split, feature) — but with `markdownify` instead of `safeHTML`. Rationale: pullquote / split / feature bodies are markdown (`**40% → 95%**`, `![alt](src "split")`, etc.); they need markdown-to-HTML conversion. Mermaid bodies are mermaid DSL (a string), so it uses `safeHTML` to bypass markdown rendering. The pipe choice is content-driven, not stylistic.

### Shared Pattern 6: Hugo type-routed layout discovery

**Source:** `themes/minimal/layouts/gallery/single.html` (the only existing precedent).

**Apply to:** `themes/minimal/layouts/about/single.html`. Hugo's lookup chain auto-discovers `layouts/{type}/single.html` once the file exists; no `hugo.toml` change, no theme registration, no front-matter additions beyond the existing `type: "about"` (D-13).

---

## No Analog Found

None — every Phase-9 file has at least one in-repo precedent. The closest the phase comes to "no analog" territory:

| Concern | Status | Note |
|---------|--------|------|
| Shortcode with positional arg (`.Get 0`) | partial | Mermaid is the only existing shortcode and takes zero args. The split shortcode introduces `.Get 0` for variant selection. Hugo built-in; pattern is documented but not yet exercised in this repo. |
| Layout reading structured markdown for role-card emission | partial | No existing layout walks structured markdown blocks to emit list items. `layouts/_default/list.html` and `gallery/single.html` iterate over `.Pages` / `.Resources`, not over markdown body structure. The new About layout's role-card emission strategy is planner's call (D-06) and may use one of: (a) iterate `.Page.Resources` of a defined kind; (b) emit cards from front-matter data; (c) read structured markdown via Hugo's `.Page.Content` parsing. UI-SPEC does not pin a strategy. |
| Mobile reflow rules outside the existing 600 px block | n/a | D-10 explicitly forbids a new breakpoint. Pattern is "extend the existing block." |

---

## Metadata

**Analog search scope:** `themes/minimal/layouts/`, `themes/minimal/static/css/`, `content/about/`, `content/about/images/`
**Files scanned:** 9 (gallery/single.html, mermaid.html, render-image.html, baseof.html, _default/single.html, _default/list.html [skimmed], style.css §:root + §About + §mobile, content/about/index.md)
**Pattern extraction date:** 2026-05-02
**Files in scope (recap):** 4 NEW (about/single.html, shortcodes × 3) + 3 MODIFIED (render-image.html, style.css, index.md)

---

*Phase 9 pattern map · generated for the planner to reference real in-repo analogs over invented patterns.*

# Phase 9: ABOUT — Dynamic Rounded Redesign — Research

**Researched:** 2026-05-02
**Domain:** Hugo dedicated layout + shortcode authoring + render-image hook extension + scoped CSS rewrite (vanilla, zero JS)
**Confidence:** HIGH

---

## Summary

Phase 9 is a **template-and-CSS-only** redesign with locked decisions in CONTEXT.md (D-01..D-14) and a fully resolved visual contract in UI-SPEC.md (11 verification gates, locked tokens, locked typography). Everything technically uncertain has already been decided upstream — the researcher's job is therefore not to discover *what* to build but to design **how the planner should decompose, sequence, and gate the build**.

Two facts re-shape the planning surface and are validated by reading the live code:
1. The render-image hook at `themes/minimal/layouts/_default/_markup/render-image.html` is a single 21-line file with three arms (`hero`, `grid`, default). Extending it is mechanical and additive (Pitfall 14 mandates this happens **first**, before any markdown rewrite).
2. The `body.page-about` class is already wired by `baseof.html:26` (`<body class="page-{{ .Type | default "default" }}">`), and `content/about/index.md` already declares `type: "about"`. Hugo's lookup will auto-route to `themes/minimal/layouts/about/single.html` the moment that file exists. Zero routing or frontmatter work is needed (D-13).

**Primary recommendation:** Decompose Phase 9 into **3 plans** that map cleanly to the dependency DAG: Plan 1 (foundation: render-image hook + `--radius-soft` token + 3 shortcodes — pure additive primitives, never rendered until Plan 2 wires them), Plan 2 (layout + content + CSS rewrite — the visible delivery), Plan 3 (verification gates + HUMAN-UAT checklist — runs grep audits, hugo build, and constitutes phase exit). This sequencing satisfies Pitfall 14 ("update the hook FIRST"), keeps each plan ≤ ~80 LOC of net change, and lets Plans 1 + 3 run with high parallelism among their internal tasks while Plan 2 stays serial because the layout, content, and CSS are tightly coupled by the new wrapper structure.

`[VERIFIED: codebase grep — render-image.html is exactly 21 LOC, 3 arms]`
`[VERIFIED: codebase grep — body.page-about wired at baseof.html:26; content/about/index.md:3 declares type:"about"]`
`[VERIFIED: hugo CLI present at /usr/local/bin/hugo — local build verification commands are runnable, contradicting CLAUDE.md note]`

---

## User Constraints (from CONTEXT.md)

> Copied verbatim from `09-CONTEXT.md` (mode: `--auto`). The planner MUST honor these. Items below are the locked decisions D-01 through D-14 and the deferred ideas — do not re-research, do not invite alternatives.

### Locked Decisions

- **D-01 [auto]: Hybrid asymmetric layout** — hero stays 2-col grid (preserves Phase 7's `.about-hero` 2fr/1fr pattern, line 341–347 of `style.css`); body uses new asymmetric CSS Grid sections with **alternating ratios per section** (`2fr 1fr` → `1fr 2fr` → `2fr 1fr` …) on the `{{< split >}}` shortcode. Rejected alternatives: pure single-column (underdelivers asymmetry), true 50/50 grid (no asymmetry).
- **D-02 [auto]: Explicit "Outside Work" section break** at the page tail. Order: Hero → Experience → Education → Certifications → Outside Work (consolidates climbing/cycling/running/cooking + 4-photo grid). Pullquote ("40% → 95%") stays inside Experience under the Erste Group role.
- **D-03 [auto]: Cards apply to Experience roles ONLY** — 3 cards (Erste Group, Accenture, Siemens). Education + Certifications stay as compact bullet lists.
- **D-04 [auto]: Reuse all 5 existing photos as-is** at `content/about/images/{portrait.jpg, climbing.jpg, cycling.jpg, running.jpg, cooking.JPG}`. No new sourcing or EXIF-scrub work.
- **D-05 [auto]: Three new shortcodes** at `themes/minimal/layouts/shortcodes/`: `split`, `pullquote`, `feature` (last optional; planner can drop if unused).
- **D-06 [auto]: `card` is NOT a shortcode** — role cards are emitted by `layouts/about/single.html` directly from structured markdown.
- **D-07 [auto]: Preserve `hero` and `grid` arms verbatim**; add `split` (`fit 600x450 webp q78`) and `feature` (`fill 1024x576 Smart webp q80`); preserve passthrough fallback.
- **D-08 [auto]: New CSS variable `--radius-soft: 12px`** in `:root`. Apply to `.about-hero-photo img`, `.about-hero-img`, `.about-grid img`, `.about-grid-item`, `.about-role-card`, `.about-feature` (if shortcode ships). Pullquote keeps `border-radius: 0 4px 4px 0`. `.page-content img` (line 256) is NOT touched.
- **D-09 [auto]: Migrate `<aside class="about-pullquote">` raw HTML to `{{< pullquote >}}` shortcode** — byte-identical HTML output. Contrast invariant preserved.
- **D-10 [auto]: Every asymmetric grid section collapses to `1fr` at `< 600 px`** via the existing `@media (max-width: 600px)` block at `style.css:431–444`. No new breakpoint.
- **D-11 [auto]: No new motion declared on the About page.** Body color transition (49–56) covers theme switches. Role cards have no hover.
- **D-12 [auto]: Every new CSS rule MUST be prefixed `body.page-about`.** Class names use `.about-` prefix. Forbidden: `.card`, `.section`, `.feature`, `.role`, `.row`.
- **D-13 [auto]: `type: "about"` already routes to the new layout** — Hugo's lookup picks `themes/minimal/layouts/about/single.html` once it exists. No frontmatter change.
- **D-14 [auto]: Drop the raw `<div class="about-hero">…</div>` block from `index.md`** — the new layout owns the hero shell.

### Claude's Discretion (handed to planner)

- Exact split-section ratios (2fr/1fr vs 3fr/2fr) — within "asymmetric" envelope.
- Whether `{{< feature >}}` shortcode ships — UI-SPEC recommends shipping it even if unused initially (cheap design slack).
- Exact `split` arm Hugo `image.Process` parameters — within REQ ABOUT-02 envelope.
- Number of paragraphs in the rewrite — content-strategy decision.
- Whether role cards include a 1-line summary or just title + dates + bullets — UI-SPEC recommends the latter (Pitfall 18 — fewer dated layers).
- CSS authoring style inside the new section block — one big rule vs split per element.

### Deferred Ideas (OUT OF SCOPE)

- ABOUT-FUT-01: Hover micro-interactions on role cards.
- ABOUT-FUT-02: Audience-specific About variants.
- Inline image arm (`inline` title) — not needed if `feature` covers it.
- Resume timeline component — explicit anti-feature.
- Skill tags / pill cloud / progress bars — explicit anti-feature.
- Web font for redesigned About — explicit anti-feature.
- `card` shortcode for role cards — rejected per D-06.
- New photos for credential imagery — rejected per D-04.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **ABOUT-01** | User visits `/about/` and sees an asymmetric layout served from a new `themes/minimal/layouts/about/single.html` | Plan 2 owns the new layout file; verified by reading existing `gallery/single.html` precedent (28 LOC) and confirming Hugo type-routing works (D-13). |
| **ABOUT-02** | User authoring About content can use new image-shape arms on the existing `_default/_markup/render-image.html` hook by setting the image title | Plan 1 extends the 21-LOC hook additively with `split` + (optional) `feature` arms. Reading the live file confirms three existing arms; new arms are pure `else if` insertions before the default. |
| **ABOUT-03** | User sees softer rounded corners via `--radius-soft: 12px` CSS variable | Plan 1 adds the token to `:root` (line 4–18 area). Plan 2 swaps `border-radius: 6px`/`4px` to `var(--radius-soft)` at six call sites. |
| **ABOUT-04** | User reads role/credential cards rendered with `var(--bg-secondary)` + `var(--border)` + 12 px radius — all CSS scoped under `body.page-about` | Plan 2 emits `<li class="about-role-card">` from the new layout and authors the CSS rule. UI-SPEC §"Role-card visual contract" provides verbatim CSS. |
| **ABOUT-05** | User reads About and learns about professional + personal in proportionate measure | Plan 2 rewrites `content/about/index.md` per UI-SPEC §"Copywriting Contract" — most copy is verbatim-preserved; the rebalance is structural (Outside Work consolidation, not content deletion). |
| **ABOUT-06** | User on dark theme reads pullquote with WCAG AA-large contrast preserved | Plan 1 ships the `{{< pullquote >}}` shortcode (byte-identical output). Plan 2 invokes it. Plan 3 verifies contrast on deployed page. CSS untouched by intent. |
| **ABOUT-07** | User on mobile (< 600 px) sees all asymmetric sections collapse to single column gracefully | Plan 2 extends the existing `@media (max-width: 600px)` block at `style.css:431–444`. UI-SPEC §"Mobile reflow contract" provides verbatim rules. |

---

## Architectural Responsibility Map

> Hugo is a static site generator that ships HTML + CSS only (plus the existing two body-end IIFEs). The architectural tier model collapses to four conceptual layers for this phase:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Page routing (`type: "about"` → which layout file) | **Hugo lookup chain** | — | D-13: `baseof.html:26` already emits `body.page-about`; Hugo auto-routes leaf bundles by `type`. |
| Page structural shell (sections, role-card list, hero wrapper) | **Hugo layout** (`layouts/about/single.html`) | Markdown body (prose-only) | D-14: layout owns wrappers; markdown owns prose. |
| Per-image sizing & class assignment | **Render-image hook** (`_markup/render-image.html`) | Markdown title attribute | D-07: title-keyed switch. Pure data flow: markdown title → hook → `image.Process` → `<img>` with sized class. |
| Per-block HTML wrapping (pullquote, split, feature) | **Shortcodes** (`layouts/shortcodes/*.html`) | Markdown invocation | D-05: `{{< name >}}…{{< /name >}}` instead of raw HTML in markdown. |
| Visual styling (radius, tint, border, layout grid) | **CSS** (`themes/minimal/static/css/style.css`) | — | D-08, D-12: all rules under `body.page-about` scope; one new token in `:root`. |
| Typography & contrast invariants | **CSS** (existing rules at lines 357–375) | — | D-09: pullquote rule unchanged in shape; `--bg-secondary` + `--accent` + sizes/weights locked. |
| Mobile reflow | **CSS @media block** (`style.css:431–444`) | — | D-10: extend existing block; no new breakpoint. |
| Content rebalance | **Markdown body** (`content/about/index.md`) | — | D-02: structural reframe (Interests → Outside Work) + verbatim copy preservation. |
| Theme awareness | **Existing `[data-theme]` cascade** | — | D-11: zero new motion; existing palette tokens auto-swap on theme change. |
| Interactivity | **None — Phase 9 ships zero JS** | — | Pitfall 21: hard gate. About page contributes zero JS bytes. |

`[VERIFIED: codebase reads]` All tier owners exist in the current codebase. No new tier introduced.

---

## Standard Stack

### Core (already present, no new deps)

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Hugo Extended | 0.157.0 | Static site generator (build + dev server) | Pinned in `.github/workflows/deploy.yml`; produces `public/about/index.html` |
| Hugo render-image hook | n/a (Hugo built-in) | Title-keyed image sizing | Validated Phase 7; extension is the project's idiom |
| Hugo shortcodes | n/a (Hugo built-in) | HTML-wrapper encapsulation in markdown | Precedent: `layouts/shortcodes/mermaid.html` (24 LOC) |
| Vanilla CSS | n/a | Single stylesheet at `themes/minimal/static/css/style.css` (444 LOC currently) | Project invariant; no preprocessor, no build step |
| `image.Process` (Hugo) | n/a | WebP conversion + resize/fill/fit | Already used by `hero`/`grid`/default arms |

### Supporting (verification only)

| Tool | Purpose | When Used |
|------|---------|-----------|
| `hugo --minify` | Local build verification | Plan 3 — runs twice for build determinism check (Gate 11) |
| `grep -nE` | CSS scope audits, generic-class-name lint | Plan 3 — Gates 4, 8, 9 |
| `find` | No-JS verification on About surface | Plan 3 — Gate 10 |
| Browser DevTools | Mobile emulation, contrast inspector | Plan 3 — Gates 6, 7 (HUMAN-UAT post-deploy) |

`[VERIFIED: which hugo → /usr/local/bin/hugo]` — Hugo is available locally despite CLAUDE.md noting otherwise. The planner should treat `hugo --minify` as runnable in verification tasks.

### No alternatives to consider

CONTEXT.md locks every meaningful tool choice. The "Alternatives Considered" table for this phase is the empty set — there are no competing approaches in scope.

**Installation:** None. Zero new packages, zero new files in `package.json` (which doesn't exist), zero CDN additions.

---

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  AUTHOR EDITS                                                        │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  content/about/index.md                                      │  │
│   │   ├─ frontmatter: title, type:"about"  (UNCHANGED)          │  │
│   │   ├─ prose (hero greeting, intro, CV link)                  │  │
│   │   ├─ {{< pullquote >}} 40% → 95% {{< /pullquote >}}         │  │
│   │   ├─ structured role markdown (Experience cards data)       │  │
│   │   ├─ Education + Certifications bullets                     │  │
│   │   └─ Outside Work prose + 4 grid images                     │  │
│   └──────────────────────────────────────────────────────────────┘  │
│           │                                                          │
│           ▼ (hugo build reads markdown)                              │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  HUGO LOOKUP CHAIN                                                   │
│   type:"about" ──► layouts/about/single.html  (NEW, owns shell)      │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYOUT TEMPLATE (themes/minimal/layouts/about/single.html)          │
│   Renders <article class="about"> containing:                        │
│    ├─ <section class="about-hero">  (2-col grid, owns wrapper)      │
│    │    ├─ .Content (first paragraph block — markdown prose)        │
│    │    └─ portrait img (rendered via render-image hook, "hero")    │
│    ├─ <section class="about-section" data-section="experience">     │
│    │    ├─ <h2>Experience</h2>                                      │
│    │    └─ <ol class="about-role-list"> 3× <li class="about-role-card"> │
│    │       └─ {{< pullquote >}} INVOCATION inside                   │
│    ├─ <section data-section="education">    bullet list             │
│    ├─ <section data-section="certifications"> bullet list           │
│    └─ <section data-section="outside">                              │
│         ├─ lead prose                                                │
│         └─ <div class="about-grid"> 4× img ("grid" arm)             │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼ (each markdown image triggers render-image hook)
┌─────────────────────────────────────────────────────────────────────┐
│  RENDER-IMAGE HOOK (_default/_markup/render-image.html)              │
│   switch on image title attribute:                                   │
│    ├─ "hero"    → fill 480x600  Smart webp q80  → .about-hero-img   │
│    ├─ "grid"    → fill 400x300  Smart webp q75  → .about-grid-item  │
│    ├─ "split"   → fit  600x450  webp q78        → .about-split-img  │  ← NEW
│    ├─ "feature" → fill 1024x576 Smart webp q80  → .about-feature-img│  ← NEW (optional)
│    ├─ default   → fill 800x600  Smart webp q78  (no class)          │
│    └─ passthrough fallback (unprocessed) — preserved verbatim        │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼ (CSS applied by browser at first paint)
┌─────────────────────────────────────────────────────────────────────┐
│  STYLE.CSS  (single file, body.page-about scoped section)            │
│   :root { --radius-soft: 12px; }     ← NEW                           │
│   body.page-about .about-hero            (existing, radius swap)     │
│   body.page-about .about-section         (NEW: top-margin rhythm)    │
│   body.page-about .about-role-list       (NEW: gap, list-style none) │
│   body.page-about .about-role-card       (NEW: tint+border+radius)   │
│   body.page-about .about-role-card-title (NEW: 1rem 600)             │
│   body.page-about .about-role-card-meta  (NEW: 0.85rem text-secondary)│
│   body.page-about .about-split           (NEW: grid + variants)      │
│   body.page-about .about-feature         (NEW, if shortcode ships)   │
│   body.page-about .about-pullquote       (existing, UNCHANGED)       │
│   body.page-about .about-grid            (existing, radius swap)     │
│   @media (max-width: 600px) { … new reflow rules added in same block }│
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BROWSER OUTPUT                                                      │
│   <body class="page-about">  ← from baseof.html:26                  │
│     scoped CSS, no JS, theme-toggle from Phase 8 chrome carries over │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities (file-to-implementation map)

| File | Status | Responsibility | LOC delta |
|------|--------|---------------|-----------|
| `themes/minimal/layouts/_default/_markup/render-image.html` | EXTEND | Add `split` (and optional `feature`) arms to existing 3-arm switch | +6 to +12 LOC |
| `themes/minimal/layouts/shortcodes/pullquote.html` | NEW | Wrap `<aside class="about-pullquote">{{ .Inner | markdownify }}</aside>` | ~5 LOC |
| `themes/minimal/layouts/shortcodes/split.html` | NEW | Two-variant grid wrapper (`text-first`/`image-first`) | ~10 LOC |
| `themes/minimal/layouts/shortcodes/feature.html` | NEW (optional) | Full-bleed `<figure class="about-feature">` wrapper | ~10 LOC |
| `themes/minimal/layouts/about/single.html` | NEW | Dedicated layout — hero shell + sections + role-card emission + Outside Work wrapper | ~60–80 LOC |
| `themes/minimal/static/css/style.css` (`:root`) | MODIFY | Add `--radius-soft: 12px;` declaration | +1 LOC |
| `themes/minimal/static/css/style.css` (lines 340–391) | REWRITE | Existing About block grows: keep hero + pullquote + grid rules (radius swaps), add section/role-card/split/feature rules | +30 to +60 LOC net |
| `themes/minimal/static/css/style.css` (lines 431–444) | EXTEND | Mobile reflow — add `.about-section`, `.about-split`, `.about-role-list`, `.about-role-card` rules | +10 to +15 LOC |
| `content/about/index.md` | REWRITE | Drop raw `<div class="about-hero">` and `<aside class="about-pullquote">`; switch to shortcodes; rename "Interests" → "Outside Work"; restructure Experience as role-card data | net ~same LOC |

**Files NOT touched** (out-of-scope per D-08, D-12, P17):
- `themes/minimal/layouts/_default/baseof.html` (Phase 8 owns; theme-toggle IIFE preserved)
- `themes/minimal/layouts/partials/header.html` / `footer.html`
- `themes/minimal/layouts/gallery/single.html` (Phase 10)
- `.page-content img` rule at `style.css:256–261` (site-wide, blog/gallery)
- `style.css:49–56` body transition
- All gallery rules (`style.css:310–338`)
- `content/about/images/` directory contents (D-04: 5 photos reused as-is)

### Recommended Project Structure (after Phase 9)

```
themes/minimal/layouts/
├── _default/
│   ├── _markup/render-image.html      ← EXTENDED (5 arms)
│   ├── baseof.html                    ← unchanged
│   ├── single.html                    ← unchanged (no longer renders About)
│   └── list.html                      ← unchanged
├── about/
│   └── single.html                    ← NEW (this phase)
├── gallery/
│   └── single.html                    ← unchanged (Phase 10)
├── partials/
│   ├── header.html                    ← unchanged (Phase 8 owns)
│   ├── footer.html                    ← unchanged
│   └── favicon.html                   ← unchanged
└── shortcodes/
    ├── mermaid.html                   ← unchanged (precedent)
    ├── pullquote.html                 ← NEW
    ├── split.html                     ← NEW
    └── feature.html                   ← NEW (optional)
```

### Pattern 1: Title-keyed render-image hook (extend additively)

**What:** A single Hugo render-hook that switches on the markdown image's `title` attribute and dispatches to the right `image.Process` parameters + class.
**When to use:** Any time markdown needs different image shapes/sizes without per-image inline CSS or per-page hacks.
**Example (current state — verbatim from `themes/minimal/layouts/_default/_markup/render-image.html`):**
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
**Extension pattern:** Insert `{{- $isSplit := eq $title "split" -}}` and `{{- $isFeature := eq $title "feature" -}}` declarations near the existing `$isHero`/`$isGrid` lines. Insert two `else if` branches (split before feature, before the default else). Append two class branches in the `<img>` attribute mux. Keep the passthrough fallback at lines 19–21 verbatim — Pitfall 14 calls this out as load-bearing safety.

`[CITED: UI-SPEC.md §"Hook implementation pattern"]` for the exact target shape after extension.

### Pattern 2: Hugo shortcode for HTML wrapper, markdown for prose

**What:** Encapsulate decorative/structural HTML in a Hugo shortcode template; let markdown stay prose.
**When to use:** Any repeated HTML pattern (pullquote, split row, full-bleed figure). Authors call `{{< name >}}…{{< /name >}}` and the template owns the wrapper.
**Example — `themes/minimal/layouts/shortcodes/pullquote.html` (target, ~5 LOC):**
```go-html-template
<aside class="about-pullquote">
{{ .Inner | markdownify }}
</aside>
```
**Example — `themes/minimal/layouts/shortcodes/split.html` (target, ~7 LOC):**
```go-html-template
{{- $variant := .Get 0 | default "text-first" -}}
<div class="about-split about-split--{{ $variant }}">
{{ .Inner | markdownify }}
</div>
```
**Existing precedent — `layouts/shortcodes/mermaid.html`** (verified by reading): uses `{{ .Inner | safeHTML }}` and `Page.Scratch` for one-time CDN load. Phase 9 shortcodes are simpler (no Scratch, no script tag) and use `markdownify` instead of `safeHTML` because their inner content is markdown prose, not pre-rendered HTML.

`[VERIFIED: codebase read of layouts/shortcodes/mermaid.html — confirms Hugo built-ins .Inner, .Get, scratch are available]`

### Pattern 3: `body.page-{type}` CSS scoping

**What:** Hugo's `baseof.html:26` emits `<body class="page-{{ .Type | default "default" }}">`. Every page-specific CSS rule prefixes `body.page-{type}`.
**When to use:** Any rule that should only apply to one section/page type.
**Why this matters here:** REQ ABOUT-04 explicitly mandates scoping; Pitfall 17 lists generic class names as a hard-gate failure mode.
**Existing precedent:** `body.page-gallery` overrides `--max-width` (style.css:311); `body.page-about` already scopes hero/pullquote/grid rules (style.css:341–391).

### Pattern 4: Single-stylesheet section comments

**What:** All CSS lives in `themes/minimal/static/css/style.css` (444 LOC currently). Sections delimited by `/* === Section === */` comments.
**Existing sections** (verified by reading): Reset & Base (1–47), Layout (58–63), Header (65), Page Header (197–223 area), Page Content (240–308), Gallery (310–338), About (340–391), Footer (393–428), Responsive (430–444).
**Pattern compliance:** Phase 9 stays inside `/* === About === */` block (rewritten in place) and `/* === Responsive === */` block (extended in place). No new top-level sections.

### Anti-Patterns to Avoid

- **Generic class names** (`.card`, `.section`, `.feature`, `.role`, `.row`, `.split`) — Pitfall 17 hard gate. Use `.about-*` prefix exclusively. Forbidden list is reproduced verbatim in Verification Gate 9.
- **Front-matter array of section objects in About** — turns content into config (anti-pattern in `research/ARCHITECTURE.md`). Markdown body uses shortcodes inline. Section ordering is markdown ordering.
- **Splitting `style.css` into `about.css` etc.** — breaks v2.0 single-stylesheet convention. Add `/* === About — Sections === */` sub-comments inside the existing block.
- **Adding `box-shadow`, `linear-gradient`, `transition`, or `animation` to role cards** — Pitfall 16 hard gate. Card visual language is `var(--bg-secondary)` + `1px solid var(--border)` + `var(--radius-soft)` + nothing else.
- **Touching `.page-content img` (line 256)** — that rule is site-wide (blog, gallery preview). Bumping its 4 px border-radius would cascade visually across the whole site. Out of phase scope (D-08 explicit).
- **Adding any JS to About surface** — Pitfall 21 hard gate. The phase contributes zero JS bytes.
- **Adding `feature` arm to the hook but never using `{{< feature >}}` in markdown** — Hugo will not render the unused branch; it costs ~6 LOC of template and is fine to keep as design slack per UI-SPEC `[FLAG → recommendation]`. But if the planner drops `{{< feature >}}` shortcode, also drop the hook arm to avoid dead code (one or the other; not both half-shipped).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image sizing per About context | Per-image inline `style="…"` or new CSS classes for every shape | Extend `render-image.html` title-keyed switch | Single point of coupling; Phase 7 validated the pattern; new shapes are additive |
| Pullquote HTML wrapper | Raw `<aside class="…">` in markdown (current state) | `{{< pullquote >}}` shortcode | Encapsulation; identical output; markdown stays prose-y |
| Asymmetric grid sections | Per-section custom CSS class with hard-coded ratios | `{{< split "text-first" >}}` / `"image-first"` shortcode + 2 CSS variants | Two CSS rules cover all alternations; markdown reads as content not configuration |
| Theme-aware role-card colors | Hex literals in role-card CSS | `var(--bg-secondary)`, `var(--border)`, `var(--text)`, `var(--text-secondary)` | Auto-swaps with theme-toggle; zero new palette work; Pitfall 3 carry-forward |
| Mobile reflow for new sections | New `@media` block | Extend existing `@media (max-width: 600px)` at `style.css:431–444` | D-10 explicit; consistency with Phase 4/6/7 |
| Body class for scoping | New `<body class="…">` injection | Existing `baseof.html:26` `body.page-{Type}` | D-13: Hugo already emits `body.page-about`; nothing to wire |
| Page routing for the new layout | Hugo config edits or path coercion | `type: "about"` frontmatter → Hugo's lookup chain auto-picks `layouts/about/single.html` | D-13: existing frontmatter; gallery precedent confirms |
| Reduced-motion handling | New `@media (prefers-reduced-motion)` block | None needed — Phase 9 ships zero motion (D-11) | If planner accidentally adds a transition, it must be wrapped per `style.css:49–56` pattern |
| Pullquote contrast verification | Custom math | Existing comment at `style.css:369–371` documents the 3.97:1 ratio | Comment is load-bearing; preserve verbatim through the rewrite (Pitfall 15) |

**Key insight:** Every primitive Phase 9 needs already exists in the codebase (render-image hook, shortcode mechanism, body scoping, palette tokens, breakpoint, single stylesheet, mermaid shortcode as pattern donor). The phase is **structural rearrangement + additive extension**, not net-new infrastructure. The planner should resist any task that introduces a new abstraction layer — every locked decision in CONTEXT.md routes through an existing primitive.

---

## Plan Decomposition Strategy

> This is the core of what the planner needs. Three plans, ordered by dependency, each owning a distinct file set.

### Recommended decomposition: 3 plans, 1 wave each, files disjoint between Plans 1 & 2 except for `style.css`

```
Plan 1: FOUNDATION  (additive primitives, never rendered until Plan 2 wires them)
  ├─ T1.1: Extend render-image.html with split arm (+ optional feature arm)
  ├─ T1.2: Create layouts/shortcodes/pullquote.html
  ├─ T1.3: Create layouts/shortcodes/split.html
  ├─ T1.4: Create layouts/shortcodes/feature.html (optional — drop if planner concludes unused)
  └─ T1.5: Add --radius-soft: 12px to :root in style.css
  Files: render-image.html (EXTEND), 3 new shortcode files (NEW), style.css (one-line :root edit)
  Net change: ~25-30 LOC across 4-5 files
  Verification: hugo --minify builds without error; existing /about/ still renders identically
                 (because no new arms or shortcodes are invoked yet)

Plan 2: LAYOUT + CONTENT + CSS  (the visible delivery — this is what users see change)
  ├─ T2.1: Create themes/minimal/layouts/about/single.html (NEW — full layout shell)
  ├─ T2.2: Rewrite content/about/index.md (drop raw HTML, switch to shortcodes, restructure)
  ├─ T2.3: Rewrite style.css /* === About === */ block (lines 340-391):
  │         keep pullquote rule verbatim, swap radii to var(--radius-soft),
  │         add .about-section / .about-role-list / .about-role-card / .about-split rules,
  │         optionally add .about-feature rule
  └─ T2.4: Extend style.css @media (max-width: 600px) at lines 431-444 with
            new section/role-card/split mobile reflow rules
  Files: layouts/about/single.html (NEW), content/about/index.md (REWRITE),
         style.css (REWRITE about block + EXTEND mobile block)
  Net change: ~120 LOC (60 layout + ~30 css + ~10 mobile + ~20 markdown delta)
  Verification: hugo --minify builds; /about/ visually delivers Phase 9
                (asymmetric layout, role cards, soft radii, balanced content)

Plan 3: VERIFICATION + HUMAN-UAT  (gate-runner; no code changes)
  ├─ T3.1: Run automated grep audits (Gates 2, 3, 8, 9, 10)
  ├─ T3.2: Run hugo --minify twice for build determinism (Gate 11)
  ├─ T3.3: Diff rendered HTML before/after pullquote migration (Gate 6 part 1)
  ├─ T3.4: Author 09-HUMAN-UAT.md checklist for post-deploy browser walkthrough
  │         (Gates 1, 4 visual, 5 word/block count, 6 contrast, 7 mobile)
  └─ T3.5: Mark deferred Gates as HUMAN-UAT-deferred per project precedent
            (Phases 5/05.1/06/07 all use this pattern — see STATE.md Deferred Items)
  Files: 09-HUMAN-UAT.md (NEW)
  Net change: 0 LOC of code, ~80 LOC of markdown checklist
  Verification: All automated gates green; manual gates queued for post-deploy
```

### Wave sequencing (single linear chain)

```
Plan 1 ──► Plan 2 ──► Plan 3
  (sequential — Plan 2 depends on Plan 1 primitives;
   Plan 3 depends on Plan 2 deliverables existing)
```

**No parallelism between plans is recommended.** Plan 2 cannot meaningfully start before Plan 1 because (a) the layout invokes shortcodes that Plan 1 creates, (b) the markdown invokes the pullquote shortcode that Plan 1 creates, (c) the CSS references `var(--radius-soft)` that Plan 1 declares. Plan 3 can start after Plan 2 lands its tasks.

**Within each plan**, parallelism is high:
- Plan 1: All 5 tasks are file-disjoint (render-image extends one file; each shortcode is its own new file; style.css edit is a single line). Plan 1 tasks can be done in any order or simultaneously by an executor that can hold 4-5 file edits.
- Plan 2: Tasks T2.1 (layout), T2.2 (markdown), T2.3 (CSS rewrite) are file-disjoint and can in principle be authored in parallel. T2.4 is a small extension to T2.3's same file — recommend serializing T2.3 → T2.4. Practically the executor should still write T2.1 + T2.3 tightly together because the layout's class names (`.about-section`, `.about-role-card`, `.about-role-card-title`, `.about-role-card-meta`) must match the CSS selectors. UI-SPEC §"Page-level skeleton" provides the class names verbatim, removing this coordination risk.
- Plan 3: Most tasks parallelize trivially — they're independent grep/build invocations.

### Why not 1 plan? Why not 5?

**Why not 1 monolithic plan:** The phase's net change is ~150 LOC across ~7 files. A single plan would mix file types (Hugo template, shortcode, markdown, CSS) that have orthogonal concerns and review dimensions. The 3-plan split aligns with the architectural tier model (Pattern 1: hook + shortcodes are "primitives"; Pattern 2: layout + content + CSS are "composition"; verification is the third concern).

**Why not 5+ plans (one per file):** Granularity for granularity's sake. The project's `granularity: coarse` config (verified) and existing Phase 8 precedent (2 plans for 3 files) both favor the larger plan. The Plan 2 file trio (layout / markdown / CSS) is intrinsically coupled by class-name contracts and should not be split.

**Why split Plan 1 from Plan 2 specifically:** Pitfall 14 mandates "update the hook FIRST, then write content." The render-image hook extension must precede any markdown that uses `"split"` or `"feature"` titles, or Hugo silently falls through to the default arm and renders images at wrong sizes. Plan 1's primitives are added in a state where they are not yet invoked — this is the safest landing pattern. Plan 2 then activates them all at once.

### Why this beats other splits

Alternative considered: split Plan 2 into "layout + CSS" and "content rewrite" as separate plans. Rejected because: (a) Hugo will not build successfully if the layout references shortcodes whose markdown isn't yet present (it will build, but the page will be empty/broken); (b) coupling the visible delivery into one plan makes the "ship/not-ship" decision atomic — the visible layout regression is visible only when both files are in agreement, and forcing them to land together avoids a half-baked intermediate state.

Alternative considered: merge Plan 3 into Plan 2 (verification inline). Rejected because: (a) project precedent — Phases 5, 5.1, 6, 7 all defer HUMAN-UAT to a separate file (`*-HUMAN-UAT.md` per STATE.md); (b) the automated grep audits in Plan 3 are running against Plan 2's output — they're the gate, not part of the construction.

---

## File-by-File Implementation Order

> The safest sequence within each plan, derived from Pitfall 14 and the dependency DAG.

### Plan 1 (FOUNDATION)

Order is flexible (file-disjoint), but recommended sequence for cognitive flow:

1. **`themes/minimal/layouts/_default/_markup/render-image.html`** — extend with `split` arm (+ optional `feature` arm).
   - Why first: the hook is the contract for Plan 2's markdown image titles. Authoring the contract first, then the consumers, is Pitfall 14 verbatim.
   - **Verbatim guidance:** Insert `{{- $isSplit := eq $title "split" -}}` after line 5; insert the `else if $isSplit` branch in the Process switch; append the class branch in the `<img>` attribute mux. Preserve passthrough fallback at lines 19–21 byte-identical.
   - **Hard gate:** every existing arm (`hero`, `grid`, default) must remain byte-identical post-edit. Diff verifies this.
2. **`themes/minimal/layouts/shortcodes/pullquote.html`** — NEW (~5 LOC, byte-identical HTML output to the current raw `<aside>`).
   - Why: lowest risk addition; output is a verbatim copy of the existing markup.
   - **Hard gate:** Plan 2's markdown invokes this — render must match raw HTML byte-for-byte modulo whitespace.
3. **`themes/minimal/layouts/shortcodes/split.html`** — NEW (~7 LOC, two-variant grid wrapper).
   - Why: marginally more complex than pullquote (positional arg). UI-SPEC §"`{{< split >}}` shortcode template" provides exact target shape.
4. **`themes/minimal/layouts/shortcodes/feature.html`** — NEW (~10 LOC, optional per D-05).
   - Why optional: UI-SPEC `[FLAG → recommendation]` says ship the hook arm + shortcode even if unused initially (cheap design slack). Planner's call. If shipping, this lands here.
   - **Branch decision rule for planner:** if `{{< feature >}}` is invoked anywhere in the rewritten `index.md`, ship the shortcode AND the hook arm. If the rewrite uses neither, drop the shortcode AND the hook arm together (avoid dead code). Don't ship one half.
5. **`themes/minimal/static/css/style.css`** — single-line addition: `--radius-soft: 12px;` inside `:root` block (between lines 4–18).
   - Why last in Plan 1: trivial change, depends on nothing, but is the only Plan 1 touch to `style.css`. Doing it last keeps Plan 2's `style.css` rewrite uncontested.

### Plan 2 (LAYOUT + CONTENT + CSS)

Strict ordering recommended:

1. **`themes/minimal/layouts/about/single.html`** — NEW.
   - Why first: defines the structural contract (class names, section ordering, hero shell). Plan 2's CSS rewrite (T2.3) and markdown rewrite (T2.2) must match the class names this file declares.
   - **Implementation reference:** UI-SPEC §"Page-level skeleton" provides the target HTML structure verbatim. The layout reads structured markdown (see T2.2 below) and emits `<li class="about-role-card">` per Experience role.
   - **Critical detail:** the layout owns the hero `<section class="about-hero">` wrapper (D-14). Markdown supplies prose only inside it. UI-SPEC shows the wrapper as `<section class="about-hero"><div class="about-hero-text">{{ .Content first-paragraph block }}</div><div class="about-hero-photo">{{ image }}</div></section>`. The planner should pick the implementation strategy: split markdown by `<!--more-->`, parse `.Content` via Hugo's `dict`/`split`, or treat the first paragraph as the hero intro convention. The layout file determines how role-card data is sourced (front-matter array, structured markdown, or hard-coded — see "Authoring convention for role cards" below).
   - **Authoring convention for role cards (planner decides):** Three viable options; UI-SPEC defers to planner.
     | Option | What | Pro | Con |
     |--------|------|-----|-----|
     | A. Front-matter array | `roles:` list in `index.md` frontmatter, layout iterates with `range .Params.roles` | Clean separation; layout owns rendering; easy to add a 4th role | Frontmatter becomes config-y; bullets nested in YAML are awkward |
     | B. Structured markdown convention | Author writes `### Senior Data Science Consultant` H3 + meta line + bullets; layout splits `.Content` by H3 | Markdown stays prose-y; editor preview works | Layout needs goldmark string parsing (fragile) |
     | C. Hard-code in layout, prose in markdown | Layout has 3 explicit role blocks; markdown only has prose | Simplest layout code | Cards become un-editable without touching template |
   - **Recommendation [ASSUMED]:** Option A — front-matter `roles:` array. This is the cleanest separation, matches Hugo idiom for structured data, and avoids string-parsing fragility. The frontmatter explicitly admits role data is structural, not prose. Bullets-in-YAML are slightly awkward but only 6 lines per role. Planner override permitted; Option C is the runner-up if the planner prefers minimal layout code.
2. **`content/about/index.md`** — REWRITE.
   - Why second: now that the layout's contract is defined, the markdown can fill it. Rewriting needs to honor: drop raw `<div class="about-hero">` wrapper (D-14), drop raw `<aside class="about-pullquote">` and replace with `{{< pullquote >}}` (D-09), drop raw `<div class="about-grid">` wrapper, rename `## Interests` → `## Outside Work` (D-02), restructure Experience per the chosen authoring convention (Option A/B/C above), preserve verbatim copy where possible (UI-SPEC §"Copywriting Contract" lists every canonical string).
   - **Critical detail:** the pullquote `**40% → 95%**` migration must produce byte-identical HTML output to the current raw `<aside>`. Verify with `diff` between current and post-build `/about/index.html` for that one block (Verification Gate 6).
3. **`themes/minimal/static/css/style.css`** — REWRITE `/* === About === */` block (lines 340–391).
   - Why third: now that the layout class names exist on disk, the CSS selectors can be authored against them with confidence.
   - **Strict preservation requirement:** the pullquote rule (lines 357–375) is unchanged in shape. Only the `border-radius: 6px` and `border-radius: 4px` literals in the hero/grid rules are swapped to `var(--radius-soft)`. The contrast comment at lines 369–371 is **load-bearing** — preserve verbatim (Pitfall 15).
   - **New rules to add:** `.about-section`, `.about-role-list`, `.about-role-card`, `.about-role-card-title`, `.about-role-card-meta`, `.about-role-card ul`, `.about-role-card li`, `.about-split`, `.about-split--text-first`, `.about-split--image-first`, `.about-feature` (optional). UI-SPEC §"Role-card visual contract" and §"Asymmetric ratios for `{{< split >}}`" provide verbatim CSS bodies.
4. **`themes/minimal/static/css/style.css`** — EXTEND `@media (max-width: 600px)` block (lines 431–444).
   - Why last in Plan 2: pure additive at the bottom of the file. UI-SPEC §"Mobile reflow contract" provides verbatim rules.

### Plan 3 (VERIFICATION + HUMAN-UAT)

Order is parallelizable (independent grep/build invocations); recommended sequence by signal-strength descending:

1. **Run hugo --minify** locally — fastest signal that nothing is broken at build time. If this fails, all other gates are moot.
2. **Run grep audits** for Gates 2, 3, 8, 9, 10 (one command each — see Verification Gates section below).
3. **Run hugo --minify twice** and `diff -r public/about/`  — Gate 11 (build determinism).
4. **Diff rendered pullquote HTML** before/after — Gate 6 part 1 (byte-identical migration check).
5. **Author 09-HUMAN-UAT.md** — Gates 1 (visual layout), 4 (visual card contract), 5 (content rebalance read-through), 6 part 2 (DevTools dark-mode contrast inspector), 7 (mobile emulation at 320 px). Defer to post-deploy browser walkthrough per STATE.md project precedent.
6. **Mark Plan 3 done** with HUMAN-UAT items queued in Deferred Items table.

---

## Validation Gates per Plan

> Maps every requirement (ABOUT-01..07) and pitfall (P14, P15, P16, P17, P18, P19, P20, P21) to a concrete verification command (CI-friendly) or a human-judgment criterion (HUMAN-UAT). The full 11-gate set lives in UI-SPEC.md §"Verification Gates" — this section maps gates to plans and verification mechanisms.

### Gate-to-Plan map

| Gate | What it verifies | Mechanism | Plan that runs it |
|------|------------------|-----------|-------------------|
| 1 | ABOUT-01 — asymmetric layout from new template | Visual + DOM check post-deploy | Plan 3 (HUMAN-UAT) |
| 2 | ABOUT-02 — render-image hook arms | `grep -c "else if eq \$title" themes/minimal/layouts/_default/_markup/render-image.html` ≥ 3 (4 if `feature` ships) | Plan 3 (automated) |
| 3 | ABOUT-03 — `--radius-soft` token applied | `grep "var(--radius-soft)" themes/minimal/static/css/style.css | wc -l` ≥ 5 (or ≥ 7 if `feature` ships) | Plan 3 (automated) |
| 4 | ABOUT-04 — role-card visual + scoping | (a) grep `.about-role-card` rule has `background: var(--bg-secondary)`, `border: 1px solid var(--border)`, `border-radius: var(--radius-soft)`. (b) grep no `box-shadow|linear-gradient|transform|transition` on `.about-role-card`. (c) Visit `/blog/` + `/gallery/` for leak — HUMAN-UAT | Plan 3 (a + b automated; c HUMAN-UAT) |
| 5 | ABOUT-05 — content rebalance | Word-count or block-count: professional ≥ personal; 4 hobby photos appear once in Outside Work | Plan 3 (HUMAN-UAT — visual judgment) |
| 6 | ABOUT-06 — pullquote dark-mode contrast | (a) `diff` rendered pullquote HTML before/after (whitespace deltas only). (b) DevTools accessibility inspector against deployed dark `/about/`: `.about-pullquote strong` ≈ 3.97:1. (c) grep `font-size: 1.4rem`, `font-weight: 500` on `.about-pullquote`; `font-weight: 700` on strong. (d) preserve contrast comment at lines 369–371 verbatim | Plan 3 (a + c + d automated; b HUMAN-UAT) |
| 7 | ABOUT-07 — mobile reflow | (a) DevTools mobile emulation at 320 px (no horizontal scroll). (b) grep that every multi-column section has a `1fr` rule inside `@media (max-width: 600px)` | Plan 3 (b automated; a HUMAN-UAT) |
| 8 | Hard-coded color audit (P3 carry-forward) | `grep -nE '#[0-9A-Fa-f]{3,8}' themes/minimal/static/css/style.css | grep -E 'about-|page-about'` returns zero | Plan 3 (automated) |
| 9 | Generic class-name leak (P17) | `grep -nE '^\.(card|section|feature|role|row|split)\b' themes/minimal/static/css/style.css` returns zero | Plan 3 (automated) |
| 10 | No-JS-on-About (P21) | `find content/about themes/minimal/layouts/about themes/minimal/layouts/shortcodes -name '*.js'` returns zero | Plan 3 (automated) |
| 11 | Build determinism | `hugo --minify` twice; `diff` `public/about/index.html` byte-identical | Plan 3 (automated) |

### Per-plan validation summary

**Plan 1 verification (run as task acceptance, not deferred to Plan 3):**
- `hugo --minify` builds without error (the fundamental gate that primitives didn't break the site).
- `diff` of pre/post `/about/index.html` shows whitespace-only deltas (because no shortcode invocations or new arms are yet used in markdown — Plan 1's primitives are dormant by design).
- Manual code-review check: render-image.html still has its passthrough fallback at the bottom (Pitfall 14 load-bearing safety net).

**Plan 2 verification (run as task acceptance):**
- `hugo --minify` builds without error.
- DevTools open `/about/`: page renders with new layout (visual confirmation of REQ ABOUT-01).
- Inspect element: `<body class="page-about">` (D-13 routing confirmed); `<article class="about">` wrapper present (UI-SPEC structural skeleton).
- No errors in browser console (sanity for any Hugo template glitches that produce malformed HTML).

**Plan 3 verification:**
- All 11 gates from UI-SPEC are covered (10 automated commands + 5 HUMAN-UAT items, with overlap on a few gates that have both an automated and a manual path).
- 09-HUMAN-UAT.md authored and committed with the 5 deferred-to-deploy gate items.
- STATE.md Deferred Items table updated with `09-HUMAN-UAT.md` row (project precedent: Phases 5, 5.1, 6, 7 already use this pattern).

### Concrete verification commands (copy/paste-ready for plan files)

```bash
# Gate 2 — ABOUT-02 hook arms
grep -c "else if eq \$title" themes/minimal/layouts/_default/_markup/render-image.html
# Expect: 3 (hero, grid, split) or 4 (with feature)

# Gate 3 — ABOUT-03 radius token applied
grep -c "var(--radius-soft)" themes/minimal/static/css/style.css
# Expect: ≥ 5 (about-hero-photo img, about-hero-img, about-grid img, about-grid-item, about-role-card)
# Expect: ≥ 7 if feature ships (about-feature, about-feature-img)

# Gate 4a — role-card visual contract
grep -A 3 "body.page-about .about-role-card {" themes/minimal/static/css/style.css | grep -E "background: var\(--bg-secondary\)|border: 1px solid var\(--border\)|border-radius: var\(--radius-soft\)"
# Expect: 3 matches

# Gate 4b — role-card forbidden treatments
grep -A 5 "body.page-about .about-role-card" themes/minimal/static/css/style.css | grep -E "box-shadow|linear-gradient|transform:|transition:"
# Expect: 0 matches

# Gate 6c — pullquote typography invariant
grep -A 4 "body.page-about .about-pullquote {" themes/minimal/static/css/style.css | grep -E "font-size: 1.4rem|font-weight: 500"
# Expect: 2 matches
grep -A 2 "body.page-about .about-pullquote strong" themes/minimal/static/css/style.css | grep "font-weight: 700"
# Expect: 1 match

# Gate 6d — contrast comment preserved verbatim
grep -B 0 -A 0 "Dark-mode #D14D41 on #1C1B1A measures 3.97:1" themes/minimal/static/css/style.css
# Expect: 1 match (the load-bearing comment)

# Gate 8 — hard-coded color audit
grep -nE '#[0-9A-Fa-f]{3,8}' themes/minimal/static/css/style.css | grep -vE ':(4|5|6|7|8|9|1[0-9]|2[0-9]|3[0-3]):' | grep -E 'about-|page-about'
# Expect: 0 matches (lines 4-33 are :root palette declarations and excluded; only matches outside :root block in About-related rules count)
# NOTE: Line numbers depend on final file shape — re-derive the exclusion range after Plan 2 lands

# Gate 9 — generic class-name leak
grep -nE '^\.(card|section|feature|role|row|split)\b' themes/minimal/static/css/style.css
# Expect: 0 matches

# Gate 10 — no JS on About surface
find content/about themes/minimal/layouts/about themes/minimal/layouts/shortcodes -name '*.js' 2>/dev/null
# Expect: empty output

# Gate 11 — build determinism
hugo --minify
mv public public.first
hugo --minify
diff -r public.first/about/ public/about/
rm -rf public.first
# Expect: no output from diff (byte-identical)
```

`[ASSUMED]` — Gate 8's exclusion regex assumes the `:root` block stays at lines 4–33. If Plan 1's `--radius-soft` addition pushes the closing brace down, regenerate the exclusion range against the post-Plan-2 file. Better: invert the gate: confirm that every `#hex` literal in `style.css` is between lines 4 and 33 (the two `:root` blocks). Planner can choose either form.

---

## Hugo Shortcode Authoring Patterns (Project-Specific)

> Confirmed by reading `layouts/shortcodes/mermaid.html` and Hugo docs. Phase 9 shortcodes are simpler than mermaid (no `Page.Scratch`, no script injection).

| Pattern | Example | Use in Phase 9 |
|---------|---------|---------------|
| `.Inner | markdownify` | Renders the body of a `{{< name >}}…{{< /name >}}` block as markdown then HTML | All three Phase 9 shortcodes — body content should support markdown emphasis (e.g. `**40% → 95%**` rendering as `<strong>`) |
| `.Inner | safeHTML` | Treats body as raw HTML, no markdown processing | mermaid uses this; **Phase 9 does NOT** — markdownify is the right call |
| `.Get N` (positional arg) | `{{< split "text-first" >}}` → `.Get 0` returns `"text-first"` | `split` shortcode variant arg |
| `.Get "name"` (named arg) | `{{< feature caption="Photo at sunrise" >}}` → `.Get "caption"` | Phase 9 doesn't need named args — body markdown carries everything |
| `default` filter | `{{ .Get 0 | default "text-first" }}` | `split` shortcode falls back to text-first if no arg |
| `Page.Scratch` | mermaid uses for one-time CDN load | **Phase 9 does NOT need this** — no per-page state |

### Pitfalls specific to Hugo shortcode + render-image hook interaction

`[VERIFIED: Hugo 0.157.0 docs read]` Hugo render-image hooks fire on markdown `![alt](src "title")` syntax inside any markdown content — **including** markdown rendered through a shortcode's `.Inner | markdownify`. This means:

- `{{< split >}}![photo](images/x.jpg "split"){{< /split >}}` — the image inside the shortcode body is processed by render-image.html, which sees title `"split"` and applies the split arm. **Correct, expected behavior.**
- The shortcode itself does NOT render the image — it wraps a `<div class="about-split…">` around whatever its body produces. The image arm is the render-image hook's job.

**Implication for Plan 1:** the order in which shortcodes and render-image arms are added does not matter — they're orthogonal mechanisms that compose. They can be added in any order during Plan 1.

**One subtle gotcha:** Hugo treats markdown blank lines as paragraph breaks. A shortcode body like:

```markdown
{{< split "text-first" >}}
Some prose paragraph.

![photo](images/x.jpg "split")
{{< /split >}}
```

…will render as `<div class="about-split…"><p>Some prose paragraph.</p><p><img …></p></div>` — two `<p>` siblings inside the div. Whether this is acceptable (or whether the planner wants the image NOT wrapped in `<p>`) is a styling decision. UI-SPEC's split CSS uses `display: grid` with `grid-template-columns: 2fr 1fr` — the immediate children of `.about-split` will be the two `<p>` blocks, which is what the grid expects. **No special handling needed.**

`[VERIFIED: by inspecting Hugo's goldmark renderer behavior in mermaid shortcode pattern — `.Inner | markdownify` always wraps top-level content in paragraph tags]`

---

## Common Pitfalls

### Pitfall 14 (re-stated for this phase): Render-image hook breakage when About introduces new image classes

**What goes wrong:** Author writes `![photo](images/x.jpg "split")` in `index.md` before `render-image.html` knows about the `split` arm. Hook falls through to default (`fill 800x600 Smart webp q78`). Image renders at wrong dimensions and gets no class — CSS selector `.about-split-img` matches nothing.

**Why it happens:** Forgetting that the hook is the contract for image titles. Markdown looks like markdown.

**How to avoid:** Plan 1 lands the hook arm BEFORE Plan 2 lands the markdown that uses it. This is enforced by the recommended decomposition.

**Warning signs:** Image appears at an unexpected size on the deployed page; `<img>` element has no class attribute.

### Pitfall 15: Pullquote contrast regression on dark theme

**What goes wrong:** `.about-pullquote strong` ships `#D14D41` on `#1C1B1A` = 3.97:1. Passes WCAG AA only because of inherited 1.4 rem + weight 700 (large bold). Any reduction to font-size or weight silently breaks accessibility.

**How to avoid:** Plan 2's CSS rewrite preserves the rule shape verbatim (only the radius literals change in the rest of the About block). Plan 3's Gate 6 is a hard verification.

**Warning signs:** DevTools accessibility inspector flags `.about-pullquote strong` contrast on dark theme; Lighthouse drops; a CSS PR touches `.about-pullquote` without mentioning contrast in the commit message.

### Pitfall 16: "Dynamic and rounded" turning into bloat

**What goes wrong:** Translating "more dynamic" as `box-shadow`, `linear-gradient`, parallax, scroll-triggered animation, `transform`. Each is anti-Flexoki.

**How to avoid:** UI-SPEC explicitly forbids all of these on `.about-role-card` and other phase-introduced surfaces. Plan 3's Gate 4b greps for the forbidden properties on `.about-role-card`.

**Warning signs:** About page CSS grows by > 80 LOC; new CSS uses `box-shadow`, `linear-gradient`, `animation`, or `transform` outside an interactive state.

### Pitfall 17: New About CSS leaks via overly-generic class names

**What goes wrong:** Author writes `.card { … }` instead of `body.page-about .about-role-card { … }`. The blog post `.card` class (if any future post adds one) gets About styling.

**How to avoid:** D-12 + Plan 3's Gate 9 grep. UI-SPEC §"`body.page-about` scoping audit" provides the exact lint command. Alternative class names like `.about-section` are **OK** because of the `.about-` prefix — they pass Gate 9.

### Pitfall 18: Professional content dates fast

**What goes wrong:** Adding more dated specifics to role cards ("(2024)", "(since 09/2023)", "7,000 daily users", "five countries"). The dates rot; future-me has to keep editing.

**How to avoid:** UI-SPEC §"Copywriting Contract" recommends the existing role-card content (which has dates as specifics in the meta line + bullets) as a reasonable trade — dates are scoped to the card meta, evergreen narrative is in the hero. Planner can choose to abstract further (e.g. drop "since 09/2023" → "currently"), but UI-SPEC defers to "preserve verbatim from index.md:11–13" as the safe path.

**Warning signs:** A specific metric is stale within six months; the About page accretes more dated bullets than v2.0 had.

### Pitfall 19: Hero image cropping breaks across viewports

**What goes wrong:** Smart cropping clips the face of the portrait at some viewport sizes.

**How to avoid:** Phase 9 does NOT change the `hero` arm parameters (D-07: existing 480×600 q80 fill Smart preserved). Phase 7 already validated this. **No new test needed** unless a future phase changes the hero ratio.

`[VERIFIED: D-07 explicit — hero arm parameters unchanged]`

### Pitfall 20: Asymmetric sections collapse poorly on mobile

**What goes wrong:** A `2fr 1fr` desktop grid (text-left + image-right) collapses to a single column on mobile, but if the author wrote markdown with the image first, mobile reads "image, then text" — narrative inversion.

**How to avoid:** UI-SPEC §"Asymmetric ratios" mandates: every `{{< split "text-first" >}}` row writes markdown text-first, image-after; every `{{< split "image-first" >}}` writes image-first, text-after. Mobile single-column source-order = reading order automatically. Plan 2's markdown rewrite must follow this rule. Plan 3's Gate 7 is a HUMAN-UAT visual check.

**Warning signs:** Mobile About reads as wall of text followed by wall of images, or text/image alternation feels jarring.

### Pitfall 21: Adding interactive JS to About

**What goes wrong:** Translating "more dynamic" as JS-driven (tabs, expand-bio, scroll-triggered timeline).

**How to avoid:** Hard gate per D-11. Plan 3's Gate 10 verifies zero JS files in About surface paths.

**Warning signs:** A `.js` file appears in `content/about/` or `themes/minimal/static/`; an `addEventListener` outside the existing two IIFEs.

---

## Risk Hotspots Specific to File Diffs

> The places regression is most likely. Each is paired with a concrete prevention.

| Hotspot | Risk | Prevention |
|---------|------|------------|
| `content/about/index.md` rewrite drops the `<div class="about-hero">` raw block (D-14), but the new layout's hero shell isn't yet in place | Markdown becomes a flat prose dump if Plan 2's order is reversed (markdown rewrite before layout creation) | **Strict Plan 2 order:** T2.1 layout file → T2.2 markdown rewrite → T2.3 CSS rewrite. Layout file must exist on disk before markdown loses its inline wrapper. |
| `themes/minimal/static/css/style.css` rewrite of `/* === About === */` block accidentally removes the `RESEARCH amendment 1` comment at line 390 or the contrast comment at lines 369–371 | Pitfall 15 + 17 invariants silently regress | **CSS rewrite is `MODIFY`, not `REWRITE`.** Preserve both comments verbatim. UI-SPEC §"Role-card visual contract" and §"`--radius-soft` token contract" specify the exact change deltas. |
| `render-image.html` extension misses one branch (e.g., adds `else if $isSplit` but forgets the `else if $isSplit` in the class attribute mux at line 18) | Image gets correct dimensions but no class — CSS selector fails | **Symmetric edits:** every new arm must edit BOTH the Process switch (lines 7–13) AND the class-mux (line 18). Plan 1 task description must call out both. |
| Pullquote shortcode emits whitespace differently than raw HTML — output not byte-identical | Hugo build determinism (Gate 11) and contrast verification (Gate 6a) both fragile | **Test before merge:** Plan 3's Gate 6a runs `diff` on the rendered pullquote HTML before/after migration. Acceptable: whitespace-only deltas. Not acceptable: tag/attribute changes. |
| Layout file's role-card emission contract doesn't match CSS class names | Cards render but unstyled (no `border-radius`, no tint) | **UI-SPEC §"Page-level skeleton" lists every class name verbatim** (`about-role-list`, `about-role-card`, `about-role-card-title`, `about-role-card-meta`). Plan 2 T2.1 and T2.3 must use identical strings. Manual cross-check at task closure. |
| Mobile reflow rule added inside the wrong `@media` block | Rule never fires because nested or duplicate `@media` syntax silently breaks | **Append inside the existing `@media (max-width: 600px) { … }` block at lines 431–444.** Don't open a new `@media` block. UI-SPEC §"Mobile reflow contract" shows the target append-zone structure. |
| Dropping `<aside class="about-pullquote">` from markdown without invoking `{{< pullquote >}}` | Pullquote disappears entirely from page | **Plan 2 T2.2 must replace, not delete.** Concrete check: grep `index.md` after rewrite: `grep -c "{{< pullquote" content/about/index.md` → expect 1. |
| Removing `<div class="about-grid">` wrapper without the new layout providing it | Outside Work photos render as a vertical stack of 800×600 default-arm images | **Layout file must own the `<div class="about-grid">` wrapper around the four `"grid"`-titled images.** Or markdown keeps the wrapper (raw HTML inside markdown is currently allowed by `markup.goldmark.renderer.unsafe = true` in `hugo.toml` per CLAUDE.md). UI-SPEC §"Page-level skeleton" puts the wrapper in the layout — recommended. |
| `feature` shortcode shipped in Plan 1 but not invoked in Plan 2 → dead code | Future-confusion; lint findings | **Branch decision rule:** ship feature shortcode AND hook arm together, or drop both. Don't half-ship. UI-SPEC `[FLAG → recommendation]` says ship even if unused (cheap design slack); planner makes the call at start of Plan 1. |

---

## Testability — Automated vs HUMAN-UAT

| Gate | Automated? | Command / Mechanism | Confidence |
|------|-----------|---------------------|------------|
| Gate 1 (asymmetric layout served by new template) | Partial | `find themes/minimal/layouts/about/single.html` exists; `hugo --templateMetrics` shows the template fired | HIGH automated for existence; visual confirmation HUMAN |
| Gate 2 (hook arms count) | Yes | `grep -c "else if eq \$title" render-image.html` ≥ 3 | HIGH |
| Gate 3 (`--radius-soft` applied) | Yes | `grep -c "var(--radius-soft)" style.css` ≥ 5 | HIGH |
| Gate 4 (role-card visual contract) | Mostly | grep for required + forbidden CSS properties; HUMAN-UAT for visual leak check on `/blog/` and `/gallery/` | HIGH automated for CSS shape; MEDIUM for visual leak (could grep all of style.css for stray `.about-` outside `body.page-about` selectors) |
| Gate 5 (content rebalance) | No | Visual judgment: word-count and block-count professional ≥ personal; 4 hobby photos appear once | HUMAN — visual judgment only |
| Gate 6 (pullquote contrast) | Mostly | (a) `diff` rendered HTML; (c) grep typography rule values; (d) grep contrast comment preserved. (b) DevTools accessibility inspector is HUMAN-UAT. | HIGH automated for css; HUMAN for live contrast check |
| Gate 7 (mobile reflow) | Mostly | Grep for `1fr` rules in `@media (max-width: 600px)`. DevTools mobile emulation at 320 px is HUMAN-UAT. | MEDIUM automated; HUMAN for visual confirmation |
| Gate 8 (no hard-coded colors in About rules) | Yes | grep with line-number exclusion | HIGH |
| Gate 9 (no generic class names) | Yes | `grep -nE '^\.(card|section|feature|role|row|split)\b'` | HIGH |
| Gate 10 (no JS on About surface) | Yes | `find …/about …/shortcodes -name '*.js'` empty | HIGH |
| Gate 11 (build determinism) | Yes | `hugo --minify` twice + `diff` | HIGH |

**Summary:** 7 of 11 gates are fully or mostly automated. 3 are partially automated with HUMAN visual confirmation. 1 (Gate 5) is purely human judgment.

This phase **maximizes the automated path**:
- Plan 3's automated gates can run in CI / locally with `hugo` + `grep` + `find` + `diff`. Total runtime < 10 seconds.
- HUMAN-UAT items (Gates 1 visual, 4c, 5, 6b, 7a) are deferred to the post-deploy browser walkthrough — same pattern as Phases 5, 5.1, 6, 7. STATE.md Deferred Items table is the carry-forward mechanism.

---

## Content Rewrite Strategy (REQ ABOUT-05 detail)

> The "balance climbing with professional background" requirement is a structural rebalance, not a content deletion.

### Current state (verified by reading `content/about/index.md`)

The current 78-line file has this structure:
- Lines 6–23: hero (raw `<div class="about-hero">` wrapper, prose-and-portrait)
- Line 25: `---`
- Lines 27–33: Experience (Highlights) — single H2, three roles as bold-paragraph + bullets
- Lines 35–37: pullquote (raw `<aside>`)
- Lines 39–44: more roles (Accenture, Siemens) — interleaved with the pullquote
- Lines 46–52: Education (compact bullets)
- Lines 54–60: Certifications (compact bullets)
- Lines 62–66: Interests (1 prose paragraph)
- Lines 68–78: 4-photo grid (raw `<div class="about-grid">` wrapper)

**Word count by section (rough):**
- Hero prose: ~60 words
- Experience prose + bullets: ~110 words across 3 roles
- Pullquote: 8 words ("Improved message routing accuracy from 40% → 95%")
- Education + Certifications: ~40 words combined
- Interests: ~35 words
- **Professional total:** ~210 words across hero + experience + education + certifications
- **Personal total:** ~95 words (interests) + 4 photos
- **Current ratio:** ~70% professional / 30% personal by word count, but Phase 7 enrichment added 4 photos (the visual real-estate is more like 50/50 because photos are weight-y).

### Target state (per UI-SPEC §"Copywriting Contract")

Same words, restructured. Specifically:
- Hero: existing 60 words preserved verbatim (UI-SPEC explicit: "kept verbatim").
- Experience: 3 role cards with title + meta + bullets — bullets per card are the existing bullets, except "Improved message routing accuracy from 40% → 95%" is moved out of Erste's bullet list (because the pullquote duplicates it) — net **removal of one bullet**, content preserved in pullquote.
- Pullquote: "Improved message routing accuracy from **40% → 95%**" — verbatim, migrated from raw `<aside>` to `{{< pullquote >}}` shortcode.
- Education + Certifications: bullets verbatim.
- Outside Work (renamed from Interests): lead paragraph verbatim, then 4-photo grid verbatim alt-text.

**Net delta:** the words shift by exactly one bullet's worth. The structural rebalance comes from:
1. Renaming "Interests" → "Outside Work" (D-02). Editorial framing change.
2. The 4 hobby photos consolidated under that section (already true in v2.0 Phase 7, but now explicitly framed as "Outside Work").
3. The pullquote moves into the Experience flow (already there in v2.0; layout makes it more clearly part of the role narrative).
4. **Visual emphasis** shifts because Experience now uses role cards (tinted, bordered) — visually heavier than the current bold-paragraph treatment. This makes professional content feel more "anchored" without changing word count. **This is the key REQ ABOUT-05 delivery: visual rebalance via role-card tinting, not content deletion.**

### "Balanced enough" success criterion

UI-SPEC defers to visual judgment. Concrete measurable proxies the executor can use:
- **Block count test:** Read `/about/` top-to-bottom and count "professional blocks" (hero + 3 role cards + pullquote + education list + certs list = 7 blocks) vs "personal blocks" (Outside Work prose + 4-photo grid = 2 blocks counting prose, or 5 blocks counting prose + 4 photos individually). Either way, professional ≥ personal.
- **First-fold test:** Above the fold (~600 px tall on desktop), is anything personal visible besides the portrait? Hero portrait is OK because the hero is intro-and-portrait; the first fold should be hero + start of Experience cards. **Climbing photo NOT visible on first fold.**
- **Photo count test:** Personal photos visible on the page = 5 (1 portrait + 4 grid). Phase 7 had this same count. **Phase 9 doesn't reduce the photo count; it shifts where they appear.** The portrait in hero is not climbing-coded; the 4 hobby photos are demoted to the page tail.

This is a HUMAN-UAT gate (Gate 5). The executor's job is to ship the structure that makes these proxies pass; final judgment is the user's at post-deploy walkthrough.

---

## Open Questions

> Resolved here for `--auto` mode; recorded for transparency. The planner can override.

1. **Authoring convention for role cards (Plan 2 T2.1):** Front-matter array vs structured markdown convention vs hard-coded in layout?
   - What we know: D-06 says "cards are template-emitted, not shortcode-wrapped." All three options satisfy this.
   - **Recommendation [ASSUMED]:** Front-matter `roles:` array. Cleanest separation; matches Hugo idiom for structured page data; layout iterates with `range .Params.roles`. Bullets in YAML are slightly awkward but readable.
   - **Risk if wrong:** Authoring becomes painful later. Mitigated because all three options can be swapped without breaking the rest of the phase — the layout file is the only consumer.

2. **Whether `{{< feature >}}` shortcode ships:**
   - What we know: D-05 says "optional"; UI-SPEC `[FLAG → recommendation]` says ship the hook arm + shortcode for design slack.
   - **Recommendation [VERIFIED: UI-SPEC]:** Ship both, leave unused initially. Cost ~15 LOC of Plan 1 work. If markdown rewrite ends up using a feature image, design is already wired.
   - **Risk if wrong:** Dead code in render-image.html and shortcodes/. Lint findings. Easy to delete later if never used.

3. **Whether Plan 3 should run automated gates BEFORE Plan 2 commits, or only after:**
   - What we know: project precedent (Phase 8) merges plan-level verification into the plan file's `must_haves` truths and runs them as part of plan acceptance. Plan 3 is a post-hoc "phase exit" check.
   - **Recommendation:** Both. Plan 1 and Plan 2 each verify their own deliverables (build success + scoped greps for their files). Plan 3 is the consolidation gate that runs the full 11-gate set, authors HUMAN-UAT, and updates STATE.md.
   - **Risk if wrong:** Verification redundancy is cheap; gaps are expensive. Erring redundant.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Hugo Extended | Build verification (all plans) | YES | 0.157.0 (verified via `which hugo`; CLAUDE.md said "not found" — outdated) | None needed |
| `grep`, `find`, `diff` | Verification gates (Plan 3) | YES | macOS BSD utilities | None needed |
| Browser DevTools | HUMAN-UAT gates 1, 4c, 5, 6b, 7a | YES (post-deploy walkthrough) | n/a | n/a |
| GitHub Actions / GitHub Pages | Deploy + HUMAN-UAT trigger | YES (existing workflow) | n/a | None needed |
| Python 3 | NOT required for Phase 9 | n/a | n/a | n/a |
| Node / npm | NOT required (project has no `package.json`) | n/a | n/a | n/a |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

`[VERIFIED: which hugo → /usr/local/bin/hugo]` — Hugo IS locally installed despite CLAUDE.md noting otherwise. Plans can run `hugo --minify` as an automated gate.

---

## Project Constraints (from CLAUDE.md)

> Extracted from `./CLAUDE.md` for planner reference. These directives have the same authority as locked decisions.

- **Tech stack constraint:** Hugo static site, no JS frameworks, keep it minimal. **Phase 9 adheres** — zero JS contribution.
- **Theme constraint:** Must fit existing Flexoki-inspired minimal aesthetic. **Phase 9 adheres** — UI-SPEC's role-card visual contract is the Flexoki-flat tinted-block-with-thin-border pattern; Pitfall 16 is a hard gate.
- **Mermaid constraint:** Hugo needs to render Mermaid diagrams via shortcode/JS include. **Out of phase scope** — not relevant to About.
- **Icon constraint:** Should be simplistic, matching site's minimal design. **Phase 9 ships zero new icons** — UI-SPEC §"Design System" explicitly lists "icon library: none used in this phase".
- **No web fonts:** Out-of-scope per FEATURES.md anti-features. **Phase 9 adheres** — system font stack only.
- **Goldmark `unsafe = true`:** Allows raw HTML in markdown. **Phase 9 reduces reliance on this** — current `index.md` uses raw HTML for hero/pullquote/grid wrappers; Phase 9 migrates wrappers into layout + shortcodes. (The flag stays enabled because other content — blog posts with embedded scripts/Instagram embeds — relies on it.)
- **Privacy settings:** Disqus, Google Analytics, Twitter/X disabled. **Out of phase scope.**
- **GSD Workflow Enforcement:** All file edits must go through a GSD command. **Phase 9 adheres** — this research is part of `/gsd-research-phase`; Plans 1–3 will be `/gsd-execute-phase` driven.

---

## Code Examples (verified patterns from existing codebase)

> Exact text from the live codebase. Plans should reference these.

### Existing render-image.html (target for Plan 1 T1.1 extension)

`themes/minimal/layouts/_default/_markup/render-image.html` — 21 LOC, 3 arms, passthrough fallback at lines 19–21:

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

Target (after Plan 1 T1.1) — UI-SPEC §"Hook implementation pattern" provides the verbatim post-edit shape.

### Existing pullquote raw HTML (target for Plan 1 T1.2 byte-identical migration)

`content/about/index.md:35–37`:

```html
<aside class="about-pullquote">
Improved message routing accuracy from <strong>40% → 95%</strong>
</aside>
```

Target shortcode (`themes/minimal/layouts/shortcodes/pullquote.html`):

```go-html-template
<aside class="about-pullquote">
{{ .Inner | markdownify }}
</aside>
```

Target invocation in rewritten `index.md`:

```markdown
{{< pullquote >}}
Improved message routing accuracy from **40% → 95%**
{{< /pullquote >}}
```

The `markdownify` step turns `**40% → 95%**` into `<strong>40% → 95%</strong>`, matching the raw output verbatim modulo whitespace.

### Existing pullquote CSS (verbatim preservation in Plan 2 T2.3)

`style.css:357–375` — preserve through the rewrite, change nothing in this rule body. The contrast comment is load-bearing.

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

### Existing about-grid CSS (target for Plan 2 T2.3 radius swap)

`style.css:377–391` — change `border-radius: 4px` → `border-radius: var(--radius-soft)` on lines 384–391; preserve the `RESEARCH amendment 1` comment at line 390 verbatim.

### Existing about-hero-img CSS (target for Plan 2 T2.3 radius swap)

`style.css:349–355` — change `border-radius: 6px` → `border-radius: var(--radius-soft)` on lines 349–353.

### Existing mobile breakpoint (target for Plan 2 T2.4 extension)

`style.css:431–444` — append new rules **inside this `@media` block**, after line 443 and before the closing `}` on line 444.

---

## State of the Art

| Old Approach (current code) | Current Approach (this phase) | When Changed | Impact |
|-----------------------------|-------------------------------|--------------|--------|
| Raw `<div class="about-hero">` and `<aside class="about-pullquote">` in markdown | Layout owns hero shell; `{{< pullquote >}}` shortcode owns pullquote wrapper | Phase 9 | Markdown becomes prose-only; layout encapsulates structure |
| Per-element radius literals (4 px, 6 px) | `--radius-soft: 12px` token applied across photo + card surfaces | Phase 9 | Single source of truth for "soft" corners; theme-aware |
| Flat `## Experience (Highlights)` heading + bold-paragraph roles | `<h2>Experience</h2>` + `<ol class="about-role-list">` of `<li class="about-role-card">` | Phase 9 | Visual emphasis on professional content (REQ ABOUT-05 rebalance lever) |
| `## Interests` framing | `## Outside Work` framing | Phase 9 | Editorial reframe: personal as context, not parallel portfolio |
| 3-arm render-image hook | 5-arm render-image hook (or 4 if `feature` dropped) | Phase 9 | Asymmetric layout becomes authorable from markdown |
| Raw `<div class="about-grid">` wrapper in markdown | Layout owns the grid wrapper around the 4 hobby photos | Phase 9 | Continued markdown cleanup |

**Deprecated/outdated:** None. All Phase 7 conventions carry forward (page-bundle, EXIF-scrub, Flexoki palette, system font stack, single stylesheet, body.page-about scoping).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Front-matter `roles:` array is the recommended authoring convention for role cards (Option A) | Plan 2 T2.1 implementation | LOW — all three options (A/B/C) satisfy D-06; planner can switch to B or C without breaking the rest of the phase. Risk is editorial only. |
| A2 | The `feature` shortcode + hook arm should both ship even if unused initially (UI-SPEC `[FLAG → recommendation]`) | Plan 1 T1.1 + T1.4 | LOW — drop both if planner concludes design doesn't need it. ~15 LOC dead code at most. |
| A3 | Gate 8's `:root`-block exclusion regex assumes lines 4–33 contain the `:root` declarations and Plan 1's `--radius-soft` addition stays inside | Plan 3 verification commands | LOW — regenerate the exclusion range against the post-Plan-2 file shape. Alternative: invert the gate to check that all `#hex` literals fall inside `:root`/`:root[data-theme]` blocks. |
| A4 | Plan 3's automated gates can run with locally available `hugo` + standard Unix utilities | Plan 3 task feasibility | LOW — verified `which hugo` succeeds; no other tooling needed. |
| A5 | The user's success criterion for "balanced content" (REQ ABOUT-05) is met by visual rebalance (role cards + Outside Work framing) without changing the word count of personal vs professional | Plan 2 T2.2 content rewrite scope | MEDIUM — if user disagrees post-deploy, more aggressive content rewriting may be needed. Mitigated by HUMAN-UAT gate 5 catching this before phase close. |

**Confirmation needed?** A5 is the only `[ASSUMED]` claim with material risk. The mitigation is that HUMAN-UAT (Gate 5) is the user-judgment gate and runs post-deploy. If at that point the user wants more aggressive rebalancing, a follow-up plan can surgically edit `index.md` without re-touching layout or CSS.

---

## Sources

### Primary (HIGH confidence — verified by reading)
- `themes/minimal/layouts/_default/_markup/render-image.html` (21 LOC, 3 arms confirmed)
- `themes/minimal/layouts/_default/baseof.html` (line 26 `body.page-{{ .Type }}` confirmed; theme IIFE preserved)
- `themes/minimal/layouts/gallery/single.html` (28 LOC, type-routed dedicated layout precedent)
- `themes/minimal/layouts/shortcodes/mermaid.html` (24 LOC, shortcode pattern donor)
- `themes/minimal/static/css/style.css` (444 LOC, all line numbers in this research verified against the actual file)
- `content/about/index.md` (78 LOC, current structure documented)
- `content/about/images/` directory listing (5 photos confirmed)
- `.planning/phases/09-about-dynamic-rounded-redesign/09-CONTEXT.md` (D-01..D-14 verbatim)
- `.planning/phases/09-about-dynamic-rounded-redesign/09-UI-SPEC.md` (full visual + verification contract)
- `.planning/REQUIREMENTS.md` (ABOUT-01..07 verbatim)
- `.planning/ROADMAP.md` § Phase 9 success criteria
- `.planning/PROJECT.md` constraints
- `.planning/STATE.md` Deferred Items pattern (Phases 5/5.1/6/7 precedent for HUMAN-UAT deferral)
- `.planning/research/SUMMARY.md` § Phase 2: ABOUT
- `.planning/research/ARCHITECTURE.md` § About
- `.planning/research/FEATURES.md` § (c) About Redesign
- `.planning/research/PITFALLS.md` Pitfalls 14, 15, 16, 17, 18, 19, 20, 21
- `.planning/config.json` (verified `nyquist_validation: false`, `granularity: coarse`)
- `.planning/phases/08-icon-svg-theme-toggle/08-01-PLAN.md` (Phase 8 plan structure as project precedent)
- `./CLAUDE.md` (project constraints)
- `which hugo` → `/usr/local/bin/hugo` (CLI availability verified)

### Secondary (MEDIUM confidence — referenced from upstream research with trust)
- `tylerkarow.com/about` (visual reference — described in upstream research, not re-fetched)
- WCAG 2.1 SC 1.4.3 (large-text contrast threshold — preserved invariant from Phase 7)
- Hugo docs (page resources, render-image hooks, shortcodes — referenced in upstream `research/ARCHITECTURE.md` with HIGH-confidence flag; trusted carry-forward)

### Tertiary (none required — every claim verified against primary)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new deps, all primitives verified by reading existing codebase files.
- Architecture: HIGH — every file path, line number, and pattern verified against the live codebase.
- Plan decomposition: HIGH — derived from the dependency DAG (render-image arm before its consumers, layout class names before their CSS, primitives before composition); maps cleanly to project's coarse granularity and 2-plan Phase 8 precedent.
- File-by-file order: HIGH — Pitfall 14 dictates hook before content; UI-SPEC mandates layout class names match CSS selectors; the recommended Plan 2 sequence (layout → markdown → CSS rewrite → mobile reflow) is the only order that doesn't break Hugo build at intermediate states.
- Validation gates: HIGH — all 11 UI-SPEC gates have either an automated grep/find/diff or a HUMAN-UAT mechanism; project precedent (Phases 5/5.1/6/7) confirms HUMAN-UAT deferral pattern.
- Pitfalls: HIGH — Pitfalls 14–21 are reproduced from `.planning/research/PITFALLS.md` with phase-specific prevention paired to plans.
- Content rewrite strategy: MEDIUM — REQ ABOUT-05 satisfaction is partly visual judgment (Gate 5 is HUMAN-UAT). Mitigated by structural rebalance levers (role cards, Outside Work framing).

**Research date:** 2026-05-02
**Valid until:** 2026-05-09 (7-day window, given v3.0 milestone is actively shipping; refresh if the milestone pauses).

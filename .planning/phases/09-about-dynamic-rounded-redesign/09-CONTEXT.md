# Phase 9: ABOUT — Dynamic Rounded Redesign - Context

**Gathered:** 2026-05-02
**Status:** Ready for planning
**Mode:** `--auto` (Claude picked recommended defaults across all gray areas)

<domain>
## Phase Boundary

Replace the v2.0 About leaf bundle's flat hero+grid layout with an asymmetric, rounded layout served from a new `themes/minimal/layouts/about/single.html` (mirroring the precedent at `themes/minimal/layouts/gallery/single.html`). The existing leaf bundle at `content/about/index.md` (+ `content/about/images/`) is rewritten to use new Hugo shortcodes; raw HTML wrappers (`<div class="about-hero">`, `<aside class="about-pullquote">`) move out of markdown and into the layout/shortcodes. A new `--radius-soft: 12px` CSS variable replaces 4–6 px values across About-scoped rules. The render-image hook at `themes/minimal/layouts/_default/_markup/render-image.html` gains new title-keyed arms. Existing 5 photos at `content/about/images/` are reused (no new content authoring or EXIF-scrub work). All About CSS stays scoped under `body.page-about` — no global pollution. No new JS, no new runtime deps, no animation libraries. Pullquote contrast invariant (`.about-pullquote strong` ≥ 1.4 rem, weight ≥ 700, dark-mode 3.97:1) is preserved through the shortcode migration. Phase 7's enrichment (5 personal photos, current copy) is the input — Phase 9 rebalances it; it does not delete it.

</domain>

<decisions>
## Implementation Decisions

### Layout Pattern (REQ ABOUT-01)
- **D-01 [auto]:** **Hybrid asymmetric layout** — hero stays 2-col grid (preserves Phase 7's `.about-hero` 2fr/1fr pattern, line 341–347 of `style.css`); body uses new asymmetric CSS Grid sections with **alternating ratios per section** (`2fr 1fr` → `1fr 2fr` → `2fr 1fr` …) on the `{{< split >}}` shortcode. This satisfies the literal requirement language ("alternating text/image grid ratios per section") while keeping tylerkarow.com/about's narrative single-column rhythm via prose-heavy proportions. **Rejected:** Pure single-column narrative (would underdeliver against REQ-01's explicit "asymmetric"). **Rejected:** True 50/50 grid (no asymmetry, defeats the requirement).

### Section Structure & Content Rebalance (REQ ABOUT-05)
- **D-02 [auto]:** **Explicit "Outside Work" section break** at the page tail. Order: **Hero (intro + portrait + CV link) → Experience → Education → Certifications → "Outside Work"** (consolidates climbing/cycling/running/cooking + 4-photo grid). This demotes climbing from "competing for hero space" to a single curated personal-context block, satisfying REQ ABOUT-05 ("not climbing-dominant as in v2.0 Phase 7"). Existing pullquote ("40% → 95%") stays inside Experience under the Erste Group role. **Rejected:** Weave personal+professional throughout (would scatter the climbing photos across sections, increase hook complexity, break the "Outside Work" framing P21 explicitly endorses).

### Role/Credential Card Scope (REQ ABOUT-04)
- **D-03 [auto]:** **Cards apply to Experience roles ONLY** — 3 cards (Erste Group, Accenture, Siemens), each tinted with `var(--bg-secondary)`, bordered with `var(--border)`, `border-radius: var(--radius-soft)`, no shadows, no gradients. Education and Certifications stay as compact bullet lists — they are factual reference material, not narrative blocks; carding them would create visual busyness and trip Pitfall 16 ("Dynamic and rounded turning into bloat that violates Kindle/Obsidian-minimal feel"). **Rejected:** Card every block (busy). **Rejected:** Card nothing (would not satisfy REQ ABOUT-04's explicit role-card visual contract).

### Photo Set
- **D-04 [auto]:** **Reuse all 5 existing photos as-is** at `content/about/images/{portrait.jpg, climbing.jpg, cycling.jpg, running.jpg, cooking.JPG}`. `portrait.jpg` anchors the hero (existing `hero` arm, 480×600). The remaining four feed the "Outside Work" 4-photo grid (existing `grid` arm, 400×300). Phase 7 already EXIF-scrubbed and validated these assets — adding new photos requires new sourcing + EXIF-scrub work and risks slipping the v3.0 ship date. With the 4-photo grid demoted to "Outside Work", climbing represents 1/4 of the grid (down from a hero-competing position) — REQ ABOUT-05 satisfied via layout, not via photo deletion.

### Shortcode Set (Architecture Research, Validated)
- **D-05 [auto]:** **Three new shortcodes** at `themes/minimal/layouts/shortcodes/`:
  - `{{< split >}}…{{< /split >}}` — two-column text+image row with alternating ratios (auto-tracks the parent section's odd/even index for ratio direction). Used in Experience and Education narrative sections if needed.
  - `{{< pullquote >}}…{{< /pullquote >}}` — wraps the existing `<aside class="about-pullquote">` raw HTML. Direct replacement; preserves the dark-mode contrast invariant (Pitfall 15).
  - `{{< feature >}}…{{< /feature >}}` — full-bleed focal image with caption (used at the top of "Outside Work" or for a hero-cap photo). Reserved for the layout's structural needs; if planning concludes it isn't needed, drop it. Planner's call.
- **D-06 [auto]:** **`card` is NOT a shortcode** — role cards are emitted by the `layouts/about/single.html` template directly from front-matter data (or from a structured markdown convention chosen by planner). Reasoning: cards have repeated structure (title + dates + bullets), shortcode-per-role would proliferate.

### Render-Image Hook Arms (REQ ABOUT-02)
- **D-07 [auto]:** **Preserve existing arms `hero` and `grid`** (Phase 7 sizing — 480×600 q80 fill Smart, 400×300 q75 fill Smart) with their current class output (`.about-hero-img`, `.about-grid-item`). **Add `split`** (image side of `{{< split >}}` row, ~600×450 fit Smart webp q78 — final dimensions decided by planner from final design). **Add `feature`** only if `{{< feature >}}` shortcode survives D-05 review. **Default arm** (no title) stays at 800×600 q78 for any unmarked image. The hook stays a single switch on image title (Pitfall 14 — enumerate arms before writing markdown content).

### `--radius-soft: 12px` Scope (REQ ABOUT-03)
- **D-08 [auto]:** **New CSS variable `--radius-soft: 12px`** declared in `:root` of `style.css`. Apply to:
  - `body.page-about .about-hero-photo img` and `.about-hero-img` (currently `border-radius: 6px` at lines 349–355) → `var(--radius-soft)`
  - `body.page-about .about-grid img` and `.about-grid-item` (currently `border-radius: 4px` at lines 384–391) → `var(--radius-soft)`
  - New `body.page-about .about-role-card` rule → `border-radius: var(--radius-soft)`
  - New `body.page-about .about-feature` rule (if shortcode lives) → `var(--radius-soft)`
  - **Pullquote stays at `border-radius: 0 4px 4px 0`** (line 366) — asymmetric one-sided radius is the visual signal that it's a left-bordered callout, not a card; bumping to 12px breaks the visual relationship with the 4 px `border-left`. Pitfall 15 contrast comment stays load-bearing above this rule.
  - **`.page-content img` at line 337 (4 px) is NOT touched** — that rule applies site-wide (blog posts, gallery) and is out of phase scope (P17).

### Pullquote Treatment (REQ ABOUT-06)
- **D-09 [auto]:** **Migrate `<aside class="about-pullquote">` raw HTML in `index.md` to `{{< pullquote >}}`** shortcode. The shortcode emits byte-identical HTML — same `<aside>`, same `class`, same inner `<strong>`. CSS at lines 357–375 of `style.css` is **unchanged in shape** (selector + properties). Pitfall 15 contrast invariant preserved verbatim: `font-size: 1.4rem`, `font-weight: 500` on `.about-pullquote`, `font-weight: 700` on `.about-pullquote strong`. The "40% → 95%" stat content stays. Re-run dark-theme contrast check (3.97:1 against `--bg-secondary`) after migration as the verification gate, per P15.

### Mobile Reflow (REQ ABOUT-07)
- **D-10 [auto]:** **Every asymmetric grid section collapses to `1fr` at `< 600 px`** via the existing `@media (max-width: 600px)` block at `style.css:431–444`. Add one rule per new section (`.about-section[data-split]`, `.about-role-card` if its internal grid exists, etc.) to that block. **No new breakpoint** — Phase 4/6/7 all key on the same 600 px boundary; consistency over precision.

### Reduced Motion (Implicit Across All Phases)
- **D-11 [auto]:** **No new motion declared on the About page.** Body color transition at `style.css:49–56` (already wrapped in `@media (prefers-reduced-motion: no-preference)`) covers theme switches. Role cards have **no hover micro-interactions** in this phase (defers ABOUT-FUT-01 — only justified if cards become external links per FEATURES.md). About is layout + content only.

### `body.page-about` Scoping (REQ ABOUT-04, P17)
- **D-12 [auto]:** **Every new CSS rule MUST be prefixed `body.page-about`.** Class names use `.about-` prefix (`.about-section`, `.about-role-card`, `.about-feature`, `.about-split-row`). Forbidden generic names: `.card`, `.section`, `.feature`, `.role`, `.row`. This is enforced by Pitfall 17 and is a hard verification gate.

### Layout Routing (REQ ABOUT-01)
- **D-13 [auto]:** **`type: "about"` already routes to the new layout** — `content/about/index.md` line 3 already declares `type: "about"`; Hugo's lookup picks `themes/minimal/layouts/about/single.html` once it exists (verified via `gallery/single.html` precedent). No frontmatter change. The old `_default/single.html` rendering path is bypassed for About on first build of this phase.

### Hero Wrapper Markup
- **D-14 [auto]:** **Drop the raw `<div class="about-hero">…</div>` block from `index.md`** — the new `layouts/about/single.html` owns the structural hero shell. The markdown becomes prose-only inside hero (intro paragraph + CV link). Avoids the "two `.about-hero` divs in DOM" hidden-coupling risk flagged in research/ARCHITECTURE.md line 146.

### Claude's Discretion (handed to planner)
- Exact split-section ratios (2fr/1fr vs 3fr/2fr) — within "asymmetric" envelope; planner picks based on final visual.
- Whether `{{< feature >}}` shortcode ships — depends on whether the final layout uses a full-bleed image; planner can drop it if the design doesn't need it.
- Exact `split` arm Hugo `image.Process` parameters — `fit` vs `fill`, exact dimensions, quality. Within REQ ABOUT-02 envelope.
- Number of paragraphs in the rewrite (REQ ABOUT-05) — content-strategy decision; balance is the goal, not a paragraph count.
- Whether role cards include a 1-line summary or just title+dates+bullets — visual density call; Pitfall 18 ("Professional content dates fast") favors evergreen narrative over dated specifics.
- CSS authoring style inside the new section block (one big rule vs split per element) — planner picks whichever reads cleaner in `style.css`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope & Requirements (Project)
- `.planning/REQUIREMENTS.md` § ABOUT — Dynamic Rounded Redesign — locked requirements ABOUT-01 through ABOUT-07
- `.planning/ROADMAP.md` § Phase 9: ABOUT — Dynamic Rounded Redesign — goal + 6 deployed-site success criteria
- `.planning/PROJECT.md` § Constraints — Flexoki, vanilla JS only, no flash on load, accessible, prefers-reduced-motion
- `.planning/PROJECT.md` § Key Decisions — Hugo render-image hook with title-keyword switch (validated Phase 7) extends naturally with new arms

### Research (Milestone-Level, Phase 9 Slice)
- `.planning/research/SUMMARY.md` § ABOUT — Redesign — must-haves + defer list (HIGH confidence)
- `.planning/research/SUMMARY.md` § Phase 2: ABOUT — Dynamic Rounded Redesign — phase-targeted notes, Pitfalls to avoid (P15, P16, P17, P18, P19, P20, P21)
- `.planning/research/STACK.md` § ABOUT — zero new deps, all native primitives
- `.planning/research/FEATURES.md` § (c) About Redesign — table-stakes + differentiators + anti-features
- `.planning/research/FEATURES.md` § Comparison: Reference Site (tylerkarow.com) vs This Site
- `.planning/research/PITFALLS.md` Pitfalls 14, 15, 16, 17, 18, 19, 20, 21 — render-image hook arms, pullquote contrast, bloat, CSS leak, dated content, hero crop, mobile reflow, no JS on About
- `.planning/research/ARCHITECTURE.md` § About — file-modification matrix (single.html, shortcodes, render-image, style.css, index.md)

### Codebase Maps (Read During Scout)
- `.planning/codebase/CONVENTIONS.md` — single-CSS-file rule, BEM-like naming, kebab-case CSS custom properties, `body.page-{type}` scoping pattern
- `.planning/codebase/STRUCTURE.md` — Hugo theme layout layering; precedent for dedicated `layouts/{type}/single.html` (gallery exists)
- `.planning/codebase/STACK.md` — confirms no Node/npm; Hugo `image.Process` page-bundle pipeline already in use

### Codebase Files (To Be Modified or Created)
- `content/about/index.md` — REWRITE: drop raw HTML wrappers, switch to shortcodes, rebalance content per ABOUT-05 (currently 79 lines)
- `themes/minimal/layouts/about/single.html` — **NEW** dedicated layout, owns hero shell + section structure + role-card emission
- `themes/minimal/layouts/shortcodes/split.html` — **NEW** ~10 LOC, two-column asymmetric row
- `themes/minimal/layouts/shortcodes/pullquote.html` — **NEW** ~5 LOC, replaces raw `<aside>`
- `themes/minimal/layouts/shortcodes/feature.html` — **NEW** ~10 LOC, full-bleed focal image (planner may drop if unused)
- `themes/minimal/layouts/_default/_markup/render-image.html` — **EXTEND** the title switch to add `split` arm (and `feature` if D-05 keeps it); preserve existing `hero`/`grid`/default arms verbatim
- `themes/minimal/static/css/style.css` — **MODIFY**:
  - `:root` block (lines 1–47): add `--radius-soft: 12px;`
  - `/* === About === */` section (lines 340–391): rewrite for asymmetric sections, role cards, new radius token
  - Mobile reflow block (lines 431–444): add new section reflow rules
  - **Do NOT touch:** `.page-content img` rule at line 337, body transition at 49–56, gallery rules

### Codebase Files (Read-Only Reference)
- `themes/minimal/layouts/_default/baseof.html` line 26 — confirms `body.page-{Type}` class is wired (`page-about` activates automatically)
- `themes/minimal/layouts/gallery/single.html` — precedent for `type`-routed dedicated layout (used by Phase 6 gallery; structurally similar)
- `content/about/images/` — 5 existing EXIF-scrubbed photos (portrait.jpg, climbing.jpg, cycling.jpg, running.jpg, cooking.JPG)

### Prior Phase Context (Carry-Forward)
- `.planning/phases/07-*/07-CONTEXT.md` (if present) — Phase 7 enriched About to leaf bundle with 5 photos; Phase 9 inherits this state
- `.planning/phases/08-icon-svg-theme-toggle/08-CONTEXT.md` — Phase 8 establishes `--radius-soft`-style token discipline (no token bumps without :root declaration); same convention applies here

### External References
- https://www.tylerkarow.com/about — visual reference for narrative single-column flow + soft rounded photos + woven personal/professional content
- WCAG 2.1 SC 1.4.3 — large-text contrast (1.4 rem bold qualifies as "large", 3:1 minimum) — pullquote invariant
- MDN: CSS `column-count`, CSS Grid `grid-template-columns` — for asymmetric section ratios
- Hugo docs: shortcodes, render-image hook, page bundle resources — all primitives already in use elsewhere in this codebase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`baseof.html` line 26 — `body.page-{Type}` auto-class**: Already emits `class="page-about"` for `type: "about"` content. New CSS rules just prefix with `body.page-about` and they're scoped automatically. No layout change needed to activate scoping.
- **`themes/minimal/layouts/_default/_markup/render-image.html`**: Existing title-keyed switch (`hero` / `grid` / default) — the contract Phase 7 validated. Extending it adds new arms without breaking existing markdown. Width/height attributes come free from `image.Process`, so CLS-safe images are inherited (REQ ABOUT-07 mobile reflow concern is layout-level, not image-level).
- **`gallery/single.html` precedent**: Phase 6 already proved the `layouts/{type}/single.html` routing pattern works. About follows the same path — Hugo lookup auto-picks the new file once it exists.
- **5 EXIF-scrubbed photos at `content/about/images/`**: Phase 7 sourced + processed these. Reusable verbatim. No new authoring work, no new build pipeline, no new EXIF gate runs.
- **Existing `.about-pullquote` CSS rules (lines 357–375)**: Contrast-validated comment at lines 369–371 is load-bearing — keep verbatim. Migration to shortcode is a markup move only; selectors and properties unchanged.
- **Existing 600 px breakpoint (lines 431–444)**: Already collapses `.about-hero` and `.about-grid` to single column. Extending this block with new section rules follows established pattern.
- **Flexoki palette tokens (`--bg-secondary`, `--border`, `--text`, `--accent`)**: All exist in both `:root` and `:root[data-theme="dark"]`. Role cards consume them directly — no new palette work, automatic theme support.

### Established Patterns
- **`body.page-{type}` CSS scoping (Pitfall 17)**: Locked since Phase 6 (`body.page-gallery`) and Phase 7 (`body.page-about`). Every new About rule prefixes `body.page-about`. Generic names (`.card`, `.row`, `.feature`) are forbidden — use `.about-card`, `.about-split-row`, `.about-feature`.
- **Hugo title-keyed render-image hook**: Validated Phase 7. Extends linearly — add a new `else if eq $title "split"` arm; existing arms stay byte-identical.
- **Shortcode encapsulation**: Precedent in existing `mermaid` shortcode and v2.0's brand sourcing. Shortcodes own HTML wrappers so markdown stays prose-y. Each new shortcode is 5–10 LOC.
- **Single-stylesheet section comments**: `/* === About === */` is an existing block at `style.css:340`. New rules join this block under section sub-comments (e.g., `/* === About — Asymmetric Sections === */`); no new top-level files.
- **`prefers-reduced-motion: no-preference` wrap**: Universal pattern from style.css:49–56. About declares no new motion in this phase, so no new wrap is needed — but if planner adds any transition, it must be inside a `no-preference` block.
- **Single source of color truth via CSS custom properties**: All About colors come from existing tokens. No hex literals in new rules (Pitfall 3 carry-forward).

### Integration Points
- **`content/about/index.md`**: Loses raw `<div class="about-hero">` and `<aside class="about-pullquote">` HTML. The structural shell migrates into `layouts/about/single.html`; the inline pullquote migrates into `{{< pullquote >}}`. The intro/CV-link/role-narrative copy moves into shortcode bodies and clean prose. Frontmatter (`title`, `type: "about"`) unchanged.
- **`themes/minimal/layouts/about/single.html`**: New file. Likely structure: outer wrapper → hero block (renders intro from `.Content` first paragraph or from a specific shortcode call) → Experience role-card list → Education list → Certifications list → "Outside Work" section with `{{< feature >}}` or grid. Planner decides exact composition.
- **`themes/minimal/layouts/_default/_markup/render-image.html`**: Single-file edit. Add 1–2 `else if` branches before the default `else`. Branch order within the if-chain doesn't matter (titles are unique).
- **`themes/minimal/static/css/style.css`**:
  - `:root` block (top of file) gets `--radius-soft: 12px;` declaration.
  - `/* === About === */` section gets ~30–60 new lines (asymmetric sections, role cards, "Outside Work", new section comments).
  - Mobile block at the bottom gets ~5 new reflow rules.
  - Total file growth: ~60–80 lines.
- **No JS files modified or created.** About is layout + CSS only.

</code_context>

<specifics>
## Specific Ideas

- **tylerkarow.com/about is the visual North Star** — narrative single-column flow with photos punctuating prose breaks, no shadows, no pill cards, soft rounded corners, professional + personal woven (not separated into two parallel portfolios). Phase 9's "hybrid asymmetric" interpretation: keep tylerkarow.com's narrative single-column rhythm, but use literal asymmetric grid ratios (2fr/1fr ↔ 1fr/2fr) for image+text rows so REQ ABOUT-01's "alternating ratios" language is honored.
- **"Dynamic" must NOT become "JS-driven" (Pitfall 21)** — REQ language uses "dynamic and rounded" but the redesign is layout-dynamic (asymmetric sections, varying ratios, soft corners), NOT interaction-dynamic (no hover effects, no animations, no JS widgets). About has zero JS contribution from this phase. Reduce-motion users see the same page as full-motion users.
- **Kindle/Obsidian-minimal feel is the aesthetic gate (Pitfall 16)** — no shadows, no gradients, no pill clouds, no progress bars, no skill tags, no resume timeline cliché. Role cards are tinted blocks with a thin border and 12 px radius — that's the entire visual language.
- **Climbing demoted, not deleted (REQ ABOUT-05)** — the 4 hobby photos and the climbing/cycling/running/cooking content survive verbatim, but consolidated under a single tail "Outside Work" section. The page should read professional-first without erasing personal context.
- **CV link stays in the hero (FEATURES.md)** — `[Download full CV (PDF)](/files/timo-bohnstedt-cv.pdf)` at index.md:15 is a critical professional surface. Keep in hero, near intro.
- **Preserve the "40% → 95%" pullquote (FEATURES.md)** — strong stat, on-brand, contrast-validated. Migrate markup, preserve content + visual.
- **No emoji, no decorative icons** — Phase 8 banned emoji from the toggle; same constraint applies to About body. Bullets stay as Markdown `-`.

</specifics>

<deferred>
## Deferred Ideas

- **ABOUT-FUT-01: Hover micro-interactions on role cards** (already in REQUIREMENTS.md "Future Requirements"). Only justified if cards become external links — currently they aren't. Deferred indefinitely.
- **ABOUT-FUT-02: Audience-specific About variants (recruiter / collaborator / friend)** (already in REQUIREMENTS.md). Out of v3.0 scope — not requested for this milestone.
- **Inline image arm (`inline` title)** for photos sitting between text sections without a `split` row. Considered (FEATURES.md "Photo-text interleaving") but not needed if `{{< feature >}}` covers the punctuation use-case. Planner can add it if the final design needs an unsplit, unframed photo.
- **Resume timeline component** (vertical line + dots) — explicit anti-feature (FEATURES.md anti-feature list, Pitfall 16). Cliché, fights minimalism. Permanently rejected for this milestone.
- **Skill tags / pill cloud / progress bars** — explicit anti-feature. Trite, subjective, overcrowds page. Permanently rejected.
- **Web font for redesigned About** — explicit anti-feature. System font stack is locked (style.css line 42).
- **`card` shortcode for role cards** — considered as one of 4 shortcodes; rejected per D-06. Cards are template-emitted, not shortcode-wrapped.
- **New photos to add professional/credential imagery** — considered. Rejected per D-04: existing 5 photos are sufficient once "Outside Work" consolidation rebalances them.
- **`feature` shortcode** — included in D-05 but optional per planner's call. May be dropped if final design doesn't need a full-bleed image block.

### Reviewed Todos (not folded)

None — `gsd-sdk query todo.match-phase 9` returned `todo_count: 0`. No pending todos to fold or review.

</deferred>

---

*Phase: 09-about-dynamic-rounded-redesign*
*Context gathered: 2026-05-02*

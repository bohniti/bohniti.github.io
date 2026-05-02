# Phase 9: ABOUT — Dynamic Rounded Redesign - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-02
**Phase:** 09-about-dynamic-rounded-redesign
**Mode:** `--auto` (Claude picked recommended defaults across all gray areas; no AskUserQuestion calls)
**Areas discussed:** Layout pattern, Section structure & content rebalance, Role card scope, Photo set, Shortcode set, Render-image hook arms, `--radius-soft` scope, Pullquote treatment, Mobile reflow, Reduced motion, Body scoping, Layout routing, Hero wrapper markup

---

## Layout Pattern (REQ ABOUT-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid asymmetric | Hero stays 2-col grid; body uses asymmetric CSS Grid sections with alternating ratios per section (`2fr 1fr` ↔ `1fr 2fr`) on `{{< split >}}` shortcode | ✓ |
| Pure single-column narrative | Image-then-text-then-image stacked, no side-by-side asymmetry — closest to tylerkarow.com/about literal pattern | |
| True 50/50 grid | Equal-column text+image rows | |

**Auto-selected:** Hybrid asymmetric.
**Rationale:** Pure single-column would underdeliver against REQ ABOUT-01's literal "alternating text/image grid ratios per section" language. True 50/50 has no asymmetry. Hybrid honors both REQ ABOUT-01 (asymmetric grid) and tylerkarow.com's narrative rhythm.

---

## Section Structure & Content Rebalance (REQ ABOUT-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit "Outside Work" tail section | Hero → Experience → Education → Certifications → "Outside Work" (consolidates climbing/cycling/running/cooking) | ✓ |
| Weave personal+professional throughout | Interleave climbing/cycling photos and stories among Experience/Education sections | |
| Keep current order, rebalance density only | Hero → Experience → Education → Certifications → Interests + grid (as today, but trimmer) | |

**Auto-selected:** Explicit "Outside Work" tail section.
**Rationale:** FEATURES.md research recommendation: "Move climbing/cycling/running/cooking grid to a smaller, latter section." Demotes climbing from "competing for hero space" to single curated personal-context block. Weave option scatters photos across sections, breaks the consolidation FEATURES.md endorses.

---

## Role/Credential Card Scope (REQ ABOUT-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Cards for Experience roles only | 3 cards (Erste / Accenture / Siemens); Education + Certifications stay as compact bullet lists | ✓ |
| Card every block | All Experience + Education + Certifications carded | |
| Card nothing | Pure prose with role titles as headings | |

**Auto-selected:** Cards for Experience only.
**Rationale:** REQ ABOUT-04 locks the visual contract for cards (`var(--bg-secondary)` + `var(--border)` + 12 px radius), so "card nothing" would underdeliver. "Card everything" trips Pitfall 16 (bloat that violates Kindle/Obsidian-minimal feel). Education + Certifications are factual reference material — narrative carding adds visual noise without information gain.

---

## Photo Set

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse all 5 existing photos as-is | portrait.jpg (hero) + climbing/cycling/running/cooking.JPG (Outside Work grid) | ✓ |
| Drop one of climbing/running, swap in non-sport photo | Reduces climbing density via deletion | |
| Add 1–2 new professional photos | E.g., conference, workspace, etc. | |

**Auto-selected:** Reuse all 5 as-is.
**Rationale:** Phase 7 already EXIF-scrubbed and Hugo-processed the 5 photos. Adding new photos requires sourcing + EXIF-scrub + processing work and risks slipping the v3.0 ship date. With grid demoted to "Outside Work", climbing represents 1/4 of the grid — already non-dominant via layout rebalance, no photo deletion needed.

---

## Shortcode Set

| Option | Description | Selected |
|--------|-------------|----------|
| Three shortcodes: split / pullquote / feature | ARCHITECTURE.md recommendation; minimum to express asymmetric flow without proliferation; `feature` may be dropped by planner if unused | ✓ |
| Two shortcodes: split / pullquote | Skip `{{< feature >}}` — full-bleed images handled inline | |
| Four shortcodes: split / pullquote / feature / card | Add `card` shortcode for role cards | |

**Auto-selected:** Three shortcodes (with `feature` as planner's call to drop).
**Rationale:** ARCHITECTURE.md research recommendation. `card` shortcode rejected (D-06): role cards have repeated structure (title + dates + bullets), shortcode-per-role would proliferate; cards are template-emitted from front-matter or markdown convention.

---

## Render-Image Hook Arms (REQ ABOUT-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve `hero`+`grid`, add `split` (+ `feature` if shortcode lives) | Phase 7 sizing untouched; new arms only for new use-cases | ✓ |
| Replace existing arms with all-new sizing | Re-derive `hero` and `grid` dimensions for the redesign | |

**Auto-selected:** Preserve existing, additive.
**Rationale:** Phase 7 sizing (480×600 for hero, 400×300 for grid) was validated; redoing it risks visual regression on the 5 existing photos. New arms for new use-cases follows the additive Phase 7 → Phase 9 evolution.

---

## `--radius-soft: 12px` Scope (REQ ABOUT-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Apply to all About-scoped images and cards; leave `.page-content img` (line 337) untouched | New token in `:root`, replaces 4–6 px in About rules; pullquote keeps asymmetric `0 4px 4px 0` (visual signal of left-bordered callout) | ✓ |
| Apply globally including `.page-content img` | Site-wide 12 px on every content image | |
| Apply only to new role cards | Existing About images keep their 4–6 px | |

**Auto-selected:** All About-scoped images and cards; `.page-content img` and pullquote excluded.
**Rationale:** Site-wide application risks visual regression in blog posts and gallery (out of phase scope, P17). Pullquote's one-sided radius is a deliberate visual signal — making it 12 px breaks the relationship with the 4 px `border-left`. Cards-only would leave hero/grid photos visually inconsistent with the "rounded redesign" goal.

---

## Pullquote Treatment (REQ ABOUT-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Migrate to `{{< pullquote >}}` shortcode, byte-identical HTML output | Selectors + properties unchanged; contrast invariant preserved | ✓ |
| Keep as raw `<aside>` HTML in markdown | No migration | |
| Restyle as a role-card variant | Bigger visual change | |

**Auto-selected:** Migrate to shortcode.
**Rationale:** D-05's shortcode set already includes `pullquote`. Markup migration only — no CSS shape change, no contrast risk. Re-run dark-mode contrast check (3.97:1) as the verification gate per Pitfall 15.

---

## Mobile Reflow (REQ ABOUT-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Single 600 px breakpoint, every section collapses to `1fr` | Mirrors existing `@media (max-width: 600px)` block at lines 431–444 | ✓ |
| Per-section custom breakpoints | Different breakpoints for hero, sections, role cards | |

**Auto-selected:** Single 600 px breakpoint.
**Rationale:** Phase 4/6/7 all key on the same 600 px boundary; consistency over precision. Per-section breakpoints add complexity without UX benefit at this content volume.

---

## Claude's Discretion

Items handed to planner with bounded envelopes:

- Exact split-section ratios (2fr/1fr vs 3fr/2fr)
- Whether `{{< feature >}}` shortcode ships (depends on final layout)
- Exact `split` arm Hugo `image.Process` parameters (fit/fill, dimensions, quality)
- Number of paragraphs in the rewrite (REQ ABOUT-05)
- Whether role cards include 1-line summary or just title+dates+bullets
- CSS authoring style inside the new section block (one big rule vs split per element)

---

## Deferred Ideas

- **ABOUT-FUT-01**: Hover micro-interactions on role cards (already in REQUIREMENTS.md "Future Requirements"; only justified if cards become external links)
- **ABOUT-FUT-02**: Audience-specific About variants (already in REQUIREMENTS.md; out of v3.0 scope)
- **Inline image arm** (`inline` title) for unsplit photos between text sections — planner adds if needed
- **Resume timeline component** — explicit anti-feature (FEATURES.md, Pitfall 16); permanently rejected
- **Skill tags / pill cloud / progress bars** — explicit anti-features; permanently rejected
- **Web font for About** — explicit anti-feature; system font stack locked
- **`card` shortcode** — rejected per D-06; cards are template-emitted
- **New photos for professional imagery** — rejected per D-04; existing 5 are sufficient post-rebalance

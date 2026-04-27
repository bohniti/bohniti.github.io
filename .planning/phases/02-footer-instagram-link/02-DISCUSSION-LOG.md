# Phase 2: Footer Instagram Link - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 02-footer-instagram-link
**Areas discussed:** Visual treatment, Icon source, Layout & order, External link safety

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Visual treatment | Icon-only? Text 'Instagram'? Icon + text? Does GitHub also become an icon? | ✓ |
| Icon source | Inline SVG vs file vs icon library | ✓ |
| Layout & order | Append to row vs separate social row | ✓ |
| External link safety | rel='noopener noreferrer' fix for the existing GitHub link | ✓ |

**User's choice:** All four areas selected.

---

## Visual treatment

| Option | Description | Selected |
|--------|-------------|----------|
| Icons for socials, text for nav | About/Blog stay text. GitHub becomes icon. Instagram is icon. (Recommended) | ✓ |
| All icons | About and Blog also become icons. Lose readability. | |
| Add Instagram as text | Simplest — text link alongside others. No new SVG pattern. | |
| Icon + text for socials only | "⊙ GitHub", "⊙ Instagram" — explicit but heavier. | |

**User's choice:** Icons for socials, text for nav.
**Notes:** Most polished and most aligned with the minimal aesthetic. Drives the decision to convert the existing GitHub text link to an icon for consistency.

---

## Icon source

| Option | Description | Selected |
|--------|-------------|----------|
| Inline SVG in footer.html | Paste SVG markup directly. Zero HTTP requests, color via currentColor. (Recommended) | ✓ |
| Standalone .svg files in static/icons/ | Files loaded via `<img>` tags. Color-via-CSS-mask trick needed for hover. | |
| Hugo partial per icon | partials/icons/instagram.html and github.html. Reusable but more files. | |
| Icon font (Font Awesome / Lucide) | External CDN load. Heaviest payload. | |

**User's choice:** Inline SVG in footer.html.

---

## Icon style

| Option | Description | Selected |
|--------|-------------|----------|
| Simple-Icons / Lucide outline | Single-color outline glyph. Open source. (Recommended) | ✓ |
| Official Instagram gradient | Brand-faithful pink/purple/orange. Loud against Flexoki muted palette. | |
| Solid filled glyph | Single-color solid. Heavier weight than outline. | |

**User's choice:** Simple-Icons / Lucide outline.

---

## Layout & order

| Option | Description | Selected |
|--------|-------------|----------|
| Same row, socials at end | About \| Blog \| [GH] [IG]. Compact. (Recommended) | ✓ |
| Two rows: text on top, icons below | Stacked. Footer ~30% taller. | |
| Same row, socials at start | [GH] [IG] \| About \| Blog. Less conventional. | |

**User's choice:** Same row, socials at end.

---

## Spacing

| Option | Description | Selected |
|--------|-------------|----------|
| Tight pair, slight gap from text | ~0.6rem between icons, 1.5rem gap to text nav. (Recommended) | ✓ |
| Same 1.5rem gap throughout | Even spacing — icons treated as siblings. | |

**User's choice:** Tight pair, slight gap from text.

---

## External link attributes

| Option | Description | Selected |
|--------|-------------|----------|
| target='_blank' rel='noopener noreferrer' on both | Standard secure pattern. Fix existing GitHub link too. (Recommended) | ✓ |
| target='_blank' rel='noopener' on both | Same minus noreferrer. Allows referrer for analytics. | |
| Match existing GitHub style | target='_blank' only, no rel. Leaves security gap. | |
| Open in same tab | No target='_blank'. Visitor leaves site on click. | |

**User's choice:** target='_blank' rel='noopener noreferrer' on both.
**Notes:** Fixes existing GitHub link in the same edit.

---

## Hover behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Match text-link hover — color shifts to accent red | currentColor + existing rule = free hover. (Recommended) | ✓ |
| Subtle opacity change (0.7 → 1.0) | Different hover style than text links. | |
| Both — color shift AND scale up slightly | Color + transform: scale(1.1). More playful. | |

**User's choice:** Match text-link hover — color shifts to accent red.

---

## Continuation

| Option | Description | Selected |
|--------|-------------|----------|
| Ready for context | Write CONTEXT.md, remaining details to Claude's discretion. | ✓ |
| Discuss accessibility | Talk through aria-label, focus styles. | |
| Discuss icon dimensions & mobile | Pin down icon size and mobile behavior. | |

**User's choice:** Ready for context.

---

## Claude's Discretion

- Exact icon dimensions (~16–18px target)
- SVG stroke width (use upstream default)
- Mobile spacing tweaks if cluster looks cramped on narrow screens
- Implementation choice for tight icon pairing (sub-flex wrapper vs CSS adjacency)
- aria-label text remains required (not discretionary), but exact wording is Claude's call

## Deferred Ideas

- Other social platforms (LinkedIn, Twitter/X, Mastodon) — out of scope per REQUIREMENTS.md
- Site-wide icon component / partial system — premature for two icons

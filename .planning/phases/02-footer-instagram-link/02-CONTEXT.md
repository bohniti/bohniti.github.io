# Phase 2: Footer Instagram Link - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Add an Instagram link to the site footer, visible on every page, linking to https://instagram.com/bohniti, styled to match the existing minimal Flexoki aesthetic. As part of this work, the existing GitHub text link is converted to an icon for consistency, since the chosen visual pattern is "socials as icons, nav as text." No other footer changes (other social platforms, layout redesigns) are in scope.

</domain>

<decisions>
## Implementation Decisions

### Visual Treatment
- **D-01:** Socials display as icons; navigation links (About, Blog) stay as text. Clear separation: nav = text, social = icons.
- **D-02:** Existing GitHub text link is converted to an icon as part of this phase — required for visual consistency with the new Instagram icon.

### Icon Source
- **D-03:** Icons are inline SVG markup pasted directly into `themes/minimal/layouts/partials/footer.html`. No external file, no CDN, no icon font.
- **D-04:** Use Lucide / Simple-Icons style: monochrome outline glyph, no gradient, no fill color. Render at small size cleanly.
- **D-05:** SVG `fill` / `stroke` set to `currentColor` so icons inherit the link's CSS color and respond to hover via the existing `.site-footer a` rules.

### Layout & Order
- **D-06:** All links remain on a single flex row inside `.footer-links`: `About | Blog | [GitHub-icon] [Instagram-icon]`.
- **D-07:** The two social icons form a tight visual cluster — smaller gap between them (~0.6rem) than the 1.5rem gap separating them from the text nav. Implemented either by wrapping the two icon `<a>`s in a sub-flex container or by per-element margin overrides.

### Hover Behavior
- **D-08:** Icons inherit the existing footer-link hover rule: rest color = `var(--text-secondary)` (#6F6E69), hover color = `var(--accent)` (#AF3029). No new hover style introduced.

### External Link Safety
- **D-09:** Both the GitHub and Instagram links use `target="_blank" rel="noopener noreferrer"`. The existing GitHub link (currently `target="_blank"` without `rel`) is fixed while we're editing the file.

### Accessibility (Claude's Discretion, but baseline expectations)
- Each icon link must have an `aria-label` so screen readers announce destination ("GitHub", "Instagram"). Visual text is not present, so this is required, not optional.
- Focus state should remain visible — do not strip default browser focus styling without replacement.

### Claude's Discretion
- Exact icon dimensions (target ~16–18px to match the 0.82rem footer text size; final value Claude's call).
- Stroke width of the SVG glyph (default to whatever the upstream Lucide/Simple-Icons spec uses).
- Mobile spacing adjustments inside the existing `@media (max-width: 600px)` block if the cluster looks cramped.
- Whether to introduce a small wrapper element (`<span class="social-icons">`) or to use CSS-only adjacency selectors to achieve D-07's tight pairing.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Footer template
- `themes/minimal/layouts/partials/footer.html` — File being edited; currently has `About | Blog | GitHub` as plain text links inside `.footer-links`.

### Site styling
- `themes/minimal/static/css/style.css` §`/* === Footer === */` (lines 221–246) — Existing footer rules: text-secondary color, accent on hover, flex layout with 1.5rem gap, centered.
- `themes/minimal/static/css/style.css` §`:root` (lines 4–18) — Flexoki CSS variables (`--text-secondary`, `--accent`, `--border`) the icons inherit.
- `themes/minimal/static/css/style.css` §`@media (max-width: 600px)` (lines 248–252) — Mobile responsive block; icon row may need a tweak here.

### Project context
- `.planning/PROJECT.md` — Constraints: minimal aesthetic, Flexoki-inspired, no JS frameworks, simplistic icon matching the design.
- `.planning/REQUIREMENTS.md` — SOC-01 (icon visible on every page), SOC-02 (links to instagram.com/bohniti), SOC-03 (style matches Flexoki).

### No external specs
No ADRs or external design docs — requirements fully captured in REQUIREMENTS.md (SOC-01 through SOC-03) and decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.footer-links` flex container already supports horizontal link layout — Instagram link is one more child element.
- `.site-footer a` already defines text-secondary rest color and accent hover color — icons using `currentColor` inherit this for free.
- Flexoki CSS variables (`--text-secondary`, `--accent`) are already in use — no new color tokens needed.

### Established Patterns
- The footer partial is a single shared template rendered by every page via `{{ partial "footer.html" . }}` in `_default/baseof.html` — editing this one file delivers SOC-01 (icon on every page) automatically.
- No existing SVGs anywhere in the repo. This phase introduces inline SVG into the theme template; no `static/icons/` directory is being created.
- External links in this codebase have used `target="_blank"` without `rel` (existing GitHub link in footer). This phase establishes the safer `target="_blank" rel="noopener noreferrer"` pattern as the new convention.

### Integration Points
- Single file edit: `themes/minimal/layouts/partials/footer.html` — replace the inner `<div class="footer-links">` content.
- CSS additions (if any — e.g., `.social-icons` wrapper rules, icon sizing, mobile tweaks) go in the existing footer section of `themes/minimal/static/css/style.css`.

</code_context>

<specifics>
## Specific Ideas

- "Socials as icons, nav as text" — chosen pattern keeps the footer feeling like a personal site, not a corporate megafooter.
- Tight social cluster ("⊙ ⊙") visually separated from text nav signals "these are different kinds of links" without needing a divider character or label.
- Instagram glyph: outline camera-square style, monochrome — explicitly NOT the brand gradient (which would clash with the muted Flexoki palette).

</specifics>

<deferred>
## Deferred Ideas

- Adding other social platforms (LinkedIn, Twitter/X, Mastodon, etc.) — out of scope per REQUIREMENTS.md.
- A site-wide icon component / partial system — only two icons exist, not enough to justify abstraction. Revisit if a 3rd icon is ever added.

</deferred>

---

*Phase: 02-footer-instagram-link*
*Context gathered: 2026-04-27*

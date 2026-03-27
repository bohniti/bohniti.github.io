# Phase 1: Article Refinement - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the node tree screenshot with an inline Mermaid diagram and sharpen the 5-node DaVinci Resolve color grading descriptions with precise value ranges and practical do/don't tips. Tighten surrounding prose to match the more technical tone.

</domain>

<decisions>
## Implementation Decisions

### Mermaid Diagram Style
- **D-01:** Left-to-right (LR) flow direction — matches how DaVinci Resolve displays the node chain horizontally
- **D-02:** Nodes show name + key parameters (e.g., "Primary Correction / Lift/Gamma/Gain") — not just names, not full details
- **D-03:** Plain styling, no custom node colors — default Mermaid shapes
- **D-04:** Custom Flexoki theme applied via Mermaid theme variables — diagram should feel native to the site's color palette

### Node Description Format
- **D-05:** Each node gets a one-line intro sentence + a parameter table (Parameter | Range | Tip)
- **D-06:** Existing value ranges from the current shared table are accurate — redistribute into per-node tables
- **D-07:** Each tip column entry includes a practical do/don't (what should happen visually, what to avoid)

### Mermaid Integration
- **D-08:** Create a Hugo shortcode (`mermaid`) for rendering Mermaid diagrams — no shortcodes exist yet, this will be the first
- **D-09:** Mermaid JS loaded only on pages that use the shortcode (not site-wide) — performance-conscious
- **D-10:** Load Mermaid from CDN (`cdn.jsdelivr.net/npm/mermaid`) — consistent with how Leaflet and Plotly are loaded in other posts

### Content Scope
- **D-11:** Remove the ASCII tree block (current lines 79-103) — Mermaid diagram replaces it entirely
- **D-12:** Remove the shared parameter table (current lines 106-114) — values redistributed into per-node tables
- **D-13:** Delete `images/Node tree.png` and its markdown reference (line 123) — Mermaid diagram fully replaces it
- **D-14:** Tighten the intro and outro prose around the node section to match the more technical tone

### Claude's Discretion
- Exact Mermaid theme variable mappings from Flexoki CSS to Mermaid config
- Shortcode implementation details (how to conditionally load JS)
- How much to shorten the surrounding prose — use judgment for readability

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Article Content
- `content/blog/2026-03-27-video-editing-journey/index.md` — The blog post being refined (node section starts at line 77)

### Theme Templates
- `themes/minimal/layouts/_default/baseof.html` — Base layout (for understanding where shortcode JS fits)
- `themes/minimal/layouts/partials/footer.html` — Footer partial (context only, not modified in this phase)
- `themes/minimal/static/css/style.css` — Site CSS with Flexoki-inspired variables (needed for Mermaid theme mapping)

### Hugo Config
- `hugo.toml` — Hugo configuration (unsafe HTML enabled, theme settings)

### No External Specs
No external ADRs or specs — requirements fully captured in decisions above and REQUIREMENTS.md (ART-01 through ART-05).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No existing shortcodes — the `mermaid` shortcode will be the first (`themes/minimal/layouts/shortcodes/` directory needs creation)
- `themes/minimal/static/css/style.css` has Flexoki-inspired CSS custom properties that can be mapped to Mermaid theme variables

### Established Patterns
- Other posts embed third-party JS (Leaflet, Plotly) via inline `<script>` tags in Markdown — the shortcode approach is a step up from this pattern
- CDN loading from `cdn.jsdelivr.net` and `unpkg.com` is established practice
- Hugo's `unsafe = true` Goldmark setting allows raw HTML in Markdown (required for shortcode JS output)

### Integration Points
- New shortcode goes in `themes/minimal/layouts/shortcodes/mermaid.html`
- Diagram replaces content in `content/blog/2026-03-27-video-editing-journey/index.md` lines 77-123
- `images/Node tree.png` to be deleted from page bundle

</code_context>

<specifics>
## Specific Ideas

- Node diagram preview agreed upon: `graph LR` with nodes like `A["Primary Correction\nLift/Gamma/Gain"]`
- Per-node table format: heading → one-liner → table with Parameter | Range | Tip columns
- The before/after color grading images (lines 118-119) stay — only the node tree screenshot is removed

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-article-refinement*
*Context gathered: 2026-03-27*

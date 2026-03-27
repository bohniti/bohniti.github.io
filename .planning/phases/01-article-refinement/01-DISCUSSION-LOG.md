# Phase 1: Article Refinement - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-27
**Phase:** 01-article-refinement
**Areas discussed:** Mermaid diagram style, Node description format, Mermaid integration, Content scope

---

## Mermaid Diagram Style

### Flow Direction

| Option | Description | Selected |
|--------|-------------|----------|
| Left-to-right (LR) | Matches DaVinci Resolve's horizontal node chain display | ✓ |
| Top-to-bottom (TD) | Vertical flow, fits narrow screens but less like Resolve UI | |

**User's choice:** Left-to-right (LR)
**Notes:** None

### Node Detail Level

| Option | Description | Selected |
|--------|-------------|----------|
| Name only | Clean and readable, details in text below | |
| Name + key params | Each node includes 1-2 key parameters, more info at a glance | ✓ |
| Numbered nodes | Short numbered labels with legend below | |

**User's choice:** Name + key params
**Notes:** None

### Styling

| Option | Description | Selected |
|--------|-------------|----------|
| Plain (no colors) | Default Mermaid styling, fits minimal aesthetic | ✓ |
| Subtle node colors | Light background colors to group nodes visually | |
| You decide | Claude picks | |

**User's choice:** Plain (no colors)
**Notes:** None

---

## Node Description Format

### Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Table per node | Compact table per node: Parameter, Range, Tip | ✓ |
| Bullet list per node | Short paragraph + bullet points | |
| You decide | Claude determines | |

**User's choice:** Table per node
**Notes:** None

### Intro Line

| Option | Description | Selected |
|--------|-------------|----------|
| One-liner + table | Single sentence explaining the node, then the table | ✓ |
| Table only | Just heading and table, maximum density | |

**User's choice:** One-liner + table
**Notes:** None

### Value Accuracy

| Option | Description | Selected |
|--------|-------------|----------|
| Values are accurate | Keep existing ranges, redistribute into per-node tables | ✓ |
| I'll provide updated values | User supplies corrected ranges during execution | |
| Claude can refine | Claude adjusts based on best practices | |

**User's choice:** Values are accurate
**Notes:** None

---

## Mermaid Integration

### Integration Method

| Option | Description | Selected |
|--------|-------------|----------|
| Hugo shortcode | Create a reusable `mermaid` shortcode, cleanest authoring | ✓ |
| Inline script in post | Add script tag directly in Markdown, simpler but less reusable | |
| You decide | Claude picks | |

**User's choice:** Hugo shortcode
**Notes:** None

### JS Loading

| Option | Description | Selected |
|--------|-------------|----------|
| Only when used | Shortcode includes the script tag, pages without diagrams don't load JS | ✓ |
| Site-wide in baseof.html | Always available but loads on every page | |

**User's choice:** Only when used
**Notes:** None

### Theme

| Option | Description | Selected |
|--------|-------------|----------|
| Mermaid default | Built-in theme, consistent with other embeds | |
| Custom Flexoki theme | Configure Mermaid theme variables to match site palette | ✓ |
| Mermaid 'neutral' theme | Grayscale, minimal, closest to site without custom CSS | |

**User's choice:** Custom Flexoki theme
**Notes:** User wants diagram to feel native to the site

---

## Content Scope

### ASCII Tree Block

| Option | Description | Selected |
|--------|-------------|----------|
| Remove it | Mermaid diagram + per-node tables replace it entirely | ✓ |
| Keep as fallback | Wrap in details collapse for text-only fallback | |
| You decide | Claude determines | |

**User's choice:** Remove it
**Notes:** None

### Shared Parameter Table

| Option | Description | Selected |
|--------|-------------|----------|
| Remove it | Values redistributed into per-node tables | ✓ |
| Keep as summary | Quick-reference summary after per-node sections | |

**User's choice:** Remove it
**Notes:** None

### Node Tree Screenshot

| Option | Description | Selected |
|--------|-------------|----------|
| Remove image + reference | Delete PNG and markdown reference, Mermaid replaces it | ✓ |
| Keep file, remove reference | Remove markdown reference but keep PNG in images folder | |
| Keep as comparison | Show both diagram and screenshot | |

**User's choice:** Remove image + reference
**Notes:** None

### Surrounding Prose

| Option | Description | Selected |
|--------|-------------|----------|
| Leave as-is | Prose provides context and narrative, only node descriptions tightened | |
| Tighten it | Shorten intro/outro to match more technical tone | ✓ |
| You decide | Claude judges readability | |

**User's choice:** Tighten it
**Notes:** None

---

## Claude's Discretion

- Exact Mermaid theme variable mappings from Flexoki CSS
- Shortcode implementation details
- How much to shorten surrounding prose

## Deferred Ideas

None — discussion stayed within phase scope

# Coding Conventions

> Last updated: 2026-03-27

## Project Type

This is a Hugo static site (personal blog) with a custom theme. The codebase is primarily Markdown content, HTML templates, CSS, and a small number of utility scripts. There is no application-level JavaScript framework, no package manager, and no build tooling beyond Hugo itself.

## Content Authoring Conventions

### Blog Post Structure

**Directory pattern:** `content/blog/YYYY-MM-DD-slug-name/index.md`

Each blog post is a Hugo page bundle: a directory containing `index.md` and an `images/` subdirectory for post-specific assets.

**Frontmatter format:** YAML (delimited by `---`), with these fields:

```yaml
---
title: "Human-Readable Title With Proper Casing"
date: 2026-03-27
draft: false
summary: "One-sentence description shown on the blog listing page."
---
```

- `title`: Always quoted, title case
- `date`: ISO date (`YYYY-MM-DD`), sometimes with `T10:00:00Z` time suffix
- `draft`: Explicitly set to `false` for published posts; omit or set `true` for drafts
- `summary`: Optional but used by all recent posts; a single sentence in quotes

Reference posts:
- `content/blog/2026-03-27-video-editing-journey/index.md` - narrative blog post
- `content/blog/2026-03-05-climbing-routes/index.md` - data-driven interactive post
- `content/blog/2026-03-15-intervals-copilot/index.md` - project showcase post
- `content/blog/2026-03-05-activity-overview/index.md` - short data visualization post

### Image References

Images are stored in the post's `images/` subdirectory and referenced with relative paths:

```markdown
![Alt text description](images/filename.png)
```

Filenames use spaces (URL-encoded as `%20` in markdown links when needed):
- `images/Chaotic timeline.png`
- `images/Clip catalog spreadsheet.png`

**Recommendation for new posts:** Use kebab-case for image filenames (`chaotic-timeline.png`) to avoid URL encoding issues, though existing posts use spaces.

### Standalone Pages

Non-blog pages live directly in `content/`:
- `content/about.md` - minimal frontmatter (title only, no date)
- `content/blog/_index.md` - section index, title-only frontmatter

### Archetype

The default archetype at `archetypes/default.md` uses TOML frontmatter (`+++`), but actual blog posts use YAML (`---`). **Use YAML frontmatter for all new content** to match the established pattern.

## HTML Template Conventions

### Template Language

Hugo Go templates. All templates live under `themes/minimal/layouts/`.

**Indentation:** 2 spaces in HTML templates.

**Template structure:**
- `_default/baseof.html` - base layout with `<head>`, `<body>`, and `{{ block "main" . }}` placeholder
- `_default/single.html` - single page/post layout, defines `{{ define "main" }}`
- `_default/list.html` - list/home layout, defines `{{ define "main" }}`
- `partials/header.html` - site header with nav
- `partials/footer.html` - site footer with links

**Date formatting:** Use `"January 2, 2006"` (Hugo's reference date format) for all displayed dates.

**Pattern for conditionals:**
```html
{{ if .Date }}
  <div class="page-date">{{ .Date.Format "January 2, 2006" }}</div>
{{ end }}
```

**Pattern for summary display (with fallback):**
```html
{{ with .Params.summary }}
  <div class="post-item-summary">{{ . }}</div>
{{ else }}
  {{ with .Summary }}
    <div class="post-item-summary">{{ . | plainify | truncate 160 }}</div>
  {{ end }}
{{ end }}
```

## CSS Conventions

**Single file:** `themes/minimal/static/css/style.css`

**Design system:** Flexoki-inspired color palette using CSS custom properties in `:root`.

**Naming:** BEM-like with `.site-` and `.page-` prefixes, kebab-case throughout:
- `.site-wrapper`, `.site-header`, `.site-nav`, `.site-footer`
- `.page-header`, `.page-title`, `.page-date`, `.page-content`
- `.post-list`, `.post-item`, `.post-item-title`, `.post-item-date`, `.post-item-summary`
- `.footer-links`

**Section organization with comments:**
```css
/* === Section Name === */
```

Sections in order: Reset & Base, Layout, Header, Post List, Single Post/Page, Footer, Responsive.

**Custom properties (always use these, do not hardcode colors):**
```css
:root {
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

**Responsive breakpoint:** Single breakpoint at `max-width: 600px`.

## JavaScript Conventions

JavaScript is embedded inline in Markdown blog posts (not in separate `.js` files), used for interactive data visualizations. There is no module system or build step.

**Pattern:** `<script>` blocks at the bottom of markdown content files.

**Style:**
- `const` and `let` (no `var`)
- camelCase for functions and variables
- Template literals for HTML string construction
- `async/await` for data fetching
- Console logging for debugging (left in production)

**External libraries loaded via CDN:**
- Leaflet for maps
- Plotly for charts
- Mermaid for diagrams

Reference: `content/blog/2026-03-05-climbing-routes/index.md` (lines 25-455)

## Python Script Conventions

Utility scripts live in `scripts/` and project root.

**Style:**
- PEP 8 compliant
- `snake_case` for functions and variables
- `UPPER_CASE` for module-level constants
- Type hints not used
- Docstrings on modules (single-line)
- `pathlib.Path` for file paths
- `if __name__ == "__main__":` guard

**Pattern:**
```python
#!/usr/bin/env python3
"""Brief description of what the script does."""

import csv
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "static" / "files" / "dataset.csv"

def main():
    # ...
    pass

if __name__ == "__main__":
    main()
```

Reference: `scripts/transform_climbing_csv.py`

## Configuration Conventions

### Hugo Configuration

Single file: `hugo.toml` (TOML format).

Key settings:
- `markup.goldmark.renderer.unsafe = true` - allows raw HTML in markdown (required for embedded scripts and Instagram embeds)
- `markup.highlight.style = "monokai"` - code syntax highlighting theme
- Privacy settings disable Disqus, Google Analytics, and Twitter/X embeds
- YouTube uses privacy-enhanced mode

### Deployment

GitHub Actions workflow at `.github/workflows/deploy.yml`:
- Triggers on push to `main` branch
- Uses Hugo extended v0.157.0
- Deploys to GitHub Pages
- No test step in the pipeline

## Import Organization

Not applicable - no module system. External libraries are loaded via CDN `<script>` tags directly in markdown content files.

## Error Handling

**JavaScript (inline):** Try/catch with console.error logging and user-facing error divs injected into the DOM.

**Python scripts:** No explicit error handling; scripts are run manually and fail loudly.

## Comments

**CSS:** Section-level comment headers (`/* === Section Name === */`), no inline comments.

**JavaScript:** Inline comments for section labels (`// Initialize the map`, `// CSV parsing function`).

**Python:** Module docstrings and inline comments for non-obvious logic.

## Formatting Tools

No automated formatting or linting tools are configured. No `.eslintrc`, `.prettierrc`, `.editorconfig`, or equivalent files exist. Formatting is maintained manually.

---

*Convention analysis: 2026-03-27*

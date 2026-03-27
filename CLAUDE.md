<!-- GSD:project-start source:PROJECT.md -->
## Project

**Personal Website Refinements**

Timo's personal website and blog, built with Hugo and a custom minimal theme, deployed to GitHub Pages at tbohnstedt.cloud. This milestone focuses on refining the latest video editing blog post and adding an Instagram social link.

**Core Value:** The blog should be a polished, technical reference that's useful for future-me — clear diagrams over screenshots, precise values over vague descriptions.

### Constraints

- **Tech stack**: Hugo static site, no JS frameworks, keep it minimal
- **Theme**: Must fit the existing Flexoki-inspired minimal aesthetic
- **Mermaid**: Hugo needs to render Mermaid diagrams — may need shortcode or JS include
- **Icon**: Should be simplistic, matching the site's minimal design
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Go templating (Hugo templates) - Used in all layout files under `themes/minimal/layouts/`
- Markdown - All content in `content/` directory
- CSS - Single stylesheet at `themes/minimal/static/css/style.css`
- JavaScript (ES6+, vanilla) - Inline scripts in blog posts for data visualization (`content/blog/2026-03-05-climbing-routes/index.md`)
- Python 3 - Utility scripts in `scripts/` and root directory (`scripts/transform_climbing_csv.py`, `convert_to_french_fixed.py`, `fix_data_properly.py`)
## Runtime
- Hugo Extended 0.157.0 (pinned in `.github/workflows/deploy.yml`)
- Hugo is NOT installed locally (not found in PATH); development may rely on another install method or Docker
- Python 3.x for utility scripts (no version pinned)
- None. No `package.json`, `Gemfile`, `requirements.txt`, or `pyproject.toml` present
- Hugo themes are vendored directly in `themes/minimal/` (not a git submodule)
## Frameworks
- Hugo 0.157.0 (Extended) - Static site generator
- None detected
- Hugo CLI - `hugo --minify` for production builds
- GitHub Actions - CI/CD pipeline at `.github/workflows/deploy.yml`
## Key Dependencies
- Hugo Extended (required for SCSS support, though currently only plain CSS is used)
- Leaflet 1.9.4 - Interactive maps (`unpkg.com/leaflet@1.9.4`)
- Plotly.js (latest) - Data visualization charts (`cdn.plot.ly/plotly-latest.min.js`)
- Mermaid.js (latest) - Diagram rendering (`cdn.jsdelivr.net/npm/mermaid`)
- Instagram embed.js - Social media embed (`www.instagram.com/embed.js`)
- `csv` (stdlib) - CSV parsing in `scripts/transform_climbing_csv.py`
- `collections.Counter` (stdlib) - Data aggregation
- `pathlib.Path` (stdlib) - File path handling
- No third-party Python packages required
## Configuration
- `baseURL`: `https://tbohnstedt.cloud/`
- `theme`: `minimal`
- `paginate`: 20
- `enableRobotsTXT`: true
- Goldmark renderer: `unsafe = true` (allows raw HTML in Markdown)
- Syntax highlighting: Monokai style
- Privacy: Disqus, Google Analytics, and Twitter/X all disabled
- YouTube: privacy-enhanced mode enabled
- `static/CNAME` contains `tbohnstedt.cloud`
- `HUGO_ENVIRONMENT`: production
- `HUGO_CACHEDIR`: runner temp directory
- Build command: `hugo --minify --baseURL "$base_url/"`
## Platform Requirements
- Hugo Extended 0.157.0 installed locally
- Python 3.x for running utility scripts
- No Node.js or npm required
- No database required
- GitHub Pages (static file hosting)
- Custom domain: `tbohnstedt.cloud`
- No server-side runtime required
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Project Type
## Content Authoring Conventions
### Blog Post Structure
- `title`: Always quoted, title case
- `date`: ISO date (`YYYY-MM-DD`), sometimes with `T10:00:00Z` time suffix
- `draft`: Explicitly set to `false` for published posts; omit or set `true` for drafts
- `summary`: Optional but used by all recent posts; a single sentence in quotes
- `content/blog/2026-03-27-video-editing-journey/index.md` - narrative blog post
- `content/blog/2026-03-05-climbing-routes/index.md` - data-driven interactive post
- `content/blog/2026-03-15-intervals-copilot/index.md` - project showcase post
- `content/blog/2026-03-05-activity-overview/index.md` - short data visualization post
### Image References
- `images/Chaotic timeline.png`
- `images/Clip catalog spreadsheet.png`
### Standalone Pages
- `content/about.md` - minimal frontmatter (title only, no date)
- `content/blog/_index.md` - section index, title-only frontmatter
### Archetype
## HTML Template Conventions
### Template Language
- `_default/baseof.html` - base layout with `<head>`, `<body>`, and `{{ block "main" . }}` placeholder
- `_default/single.html` - single page/post layout, defines `{{ define "main" }}`
- `_default/list.html` - list/home layout, defines `{{ define "main" }}`
- `partials/header.html` - site header with nav
- `partials/footer.html` - site footer with links
## CSS Conventions
- `.site-wrapper`, `.site-header`, `.site-nav`, `.site-footer`
- `.page-header`, `.page-title`, `.page-date`, `.page-content`
- `.post-list`, `.post-item`, `.post-item-title`, `.post-item-date`, `.post-item-summary`
- `.footer-links`
## JavaScript Conventions
- `const` and `let` (no `var`)
- camelCase for functions and variables
- Template literals for HTML string construction
- `async/await` for data fetching
- Console logging for debugging (left in production)
- Leaflet for maps
- Plotly for charts
- Mermaid for diagrams
## Python Script Conventions
- PEP 8 compliant
- `snake_case` for functions and variables
- `UPPER_CASE` for module-level constants
- Type hints not used
- Docstrings on modules (single-line)
- `pathlib.Path` for file paths
- `if __name__ == "__main__":` guard
#!/usr/bin/env python3
## Configuration Conventions
### Hugo Configuration
- `markup.goldmark.renderer.unsafe = true` - allows raw HTML in markdown (required for embedded scripts and Instagram embeds)
- `markup.highlight.style = "monokai"` - code syntax highlighting theme
- Privacy settings disable Disqus, Google Analytics, and Twitter/X embeds
- YouTube uses privacy-enhanced mode
### Deployment
- Triggers on push to `main` branch
- Uses Hugo extended v0.157.0
- Deploys to GitHub Pages
- No test step in the pipeline
## Import Organization
## Error Handling
## Comments
## Formatting Tools
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Content-driven blog with Markdown files as the single source of truth
- Custom Hugo theme (`minimal`) with Flexoki-inspired design, no JavaScript framework
- Hugo page bundles for blog posts (co-located images with content)
- GitHub Actions CI/CD pipeline for automated build and deploy on push to `main`
- Unsafe HTML rendering enabled for embedding rich content (Instagram embeds, Leaflet maps, Plotly charts)
## Layers
- Purpose: All authored content (blog posts, static pages)
- Location: `content/`
- Contains: Markdown files with YAML front matter, co-located images
- Depends on: Nothing
- Used by: Hugo build process, theme templates
- Purpose: HTML templates, CSS styling, layout structure
- Location: `themes/minimal/`
- Contains: Go HTML templates (`baseof.html`, `list.html`, `single.html`), partials (`header.html`, `footer.html`), CSS (`style.css`)
- Depends on: Hugo template engine, content layer data
- Used by: Hugo build process
- Purpose: Files served as-is without Hugo processing
- Location: `static/` and `themes/minimal/static/`
- Contains: PDF files, CSV data files, JavaScript data files, CSS
- Depends on: Nothing
- Used by: Content pages via direct URL references
- Purpose: Automated build and deployment pipeline
- Location: `.github/workflows/`
- Contains: GitHub Actions workflow for Hugo build and GitHub Pages deploy
- Depends on: Hugo v0.157.0 (extended), all other layers
- Used by: GitHub Pages hosting
- Purpose: Data transformation scripts (not part of the site build)
- Location: `scripts/`, root-level Python files
- Contains: Python scripts for CSV data processing
- Depends on: External data sources (Intervals.icu exports)
- Used by: Content authors (manual execution)
## Data Flow
- No client-side state management; purely static HTML
- Some blog posts include inline JavaScript for interactive elements (Leaflet maps, Plotly charts in `content/blog/2026-03-05-climbing-routes/index.md`)
## Key Abstractions
- Purpose: Co-locate a blog post's Markdown and its images in a single directory
- Examples: `content/blog/2026-03-05-activity-overview/`, `content/blog/2026-03-27-video-editing-journey/`
- Pattern: Each post directory contains `index.md` plus an `images/` subdirectory
- Purpose: Hugo's template lookup chain determines which layout renders each page
- Examples: `themes/minimal/layouts/_default/baseof.html`, `themes/minimal/layouts/_default/single.html`
- Pattern: `baseof.html` defines the HTML shell; `list.html` and `single.html` define the `"main"` block
- Purpose: YAML metadata at the top of each Markdown file controls title, date, draft status, and summary
- Examples: All `index.md` files in `content/blog/`
- Pattern: `title`, `date`, `draft`, `summary` fields
## Entry Points
- Location: `hugo.toml`
- Triggers: `hugo` CLI command (locally) or GitHub Actions workflow
- Responsibilities: Reads config, processes all content, applies theme, outputs static site to `public/`
- Location: `.github/workflows/hugo.yml`
- Triggers: Push to `main` branch, or manual `workflow_dispatch`
- Responsibilities: Installs Hugo 0.157.0, builds with `--minify`, deploys to GitHub Pages
- Location: `themes/minimal/layouts/_default/list.html` (the `{{ if .IsHome }}` branch)
- Triggers: Visiting the root URL
- Responsibilities: Lists all blog posts from the `blog` section with title, date, and summary
- Location: `content/blog/_index.md` + `themes/minimal/layouts/_default/list.html` (the `{{ eq .Section "blog" }}` branch)
- Triggers: Visiting `/blog/`
- Responsibilities: Lists all blog posts under the "Blog" heading
- Location: `content/about.md`
- Triggers: Visiting `/about/`
- Responsibilities: Renders static about page content via `single.html`
## Error Handling
- Hugo's `{{ with }}` blocks provide nil-safe access to optional fields (e.g., `.Params.summary`, `.Description`)
- The `{{ if not .IsHome }}` guard in `baseof.html` conditionally prefixes the page title
## Cross-Cutting Concerns
- `enableRobotsTXT = true` in `hugo.toml`
- `<meta name="description">` set from page or site params in `baseof.html`
- Privacy settings disable Disqus, Google Analytics, and X tracking in `hugo.toml`
- Single CSS file with a `@media (max-width: 600px)` breakpoint in `themes/minimal/static/css/style.css`
- Max content width constrained to 640px via `--max-width` CSS variable
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

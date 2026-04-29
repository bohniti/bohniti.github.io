# Architecture

**Analysis Date:** 2026-03-27

## Pattern Overview

**Overall:** Static site generator (Hugo) with a custom minimal theme, deployed to GitHub Pages.

**Key Characteristics:**
- Content-driven blog with Markdown files as the single source of truth
- Custom Hugo theme (`minimal`) with Flexoki-inspired design, no JavaScript framework
- Hugo page bundles for blog posts (co-located images with content)
- GitHub Actions CI/CD pipeline for automated build and deploy on push to `main`
- Unsafe HTML rendering enabled for embedding rich content (Instagram embeds, Leaflet maps, Plotly charts)

## Layers

**Content Layer:**
- Purpose: All authored content (blog posts, static pages)
- Location: `content/`
- Contains: Markdown files with YAML front matter, co-located images
- Depends on: Nothing
- Used by: Hugo build process, theme templates

**Theme/Presentation Layer:**
- Purpose: HTML templates, CSS styling, layout structure
- Location: `themes/minimal/`
- Contains: Go HTML templates (`baseof.html`, `list.html`, `single.html`), partials (`header.html`, `footer.html`), CSS (`style.css`)
- Depends on: Hugo template engine, content layer data
- Used by: Hugo build process

**Static Assets Layer:**
- Purpose: Files served as-is without Hugo processing
- Location: `static/` and `themes/minimal/static/`
- Contains: PDF files, CSV data files, JavaScript data files, CSS
- Depends on: Nothing
- Used by: Content pages via direct URL references

**Build/Deploy Layer:**
- Purpose: Automated build and deployment pipeline
- Location: `.github/workflows/`
- Contains: GitHub Actions workflow for Hugo build and GitHub Pages deploy
- Depends on: Hugo v0.157.0 (extended), all other layers
- Used by: GitHub Pages hosting

**Utility Scripts Layer:**
- Purpose: Data transformation scripts (not part of the site build)
- Location: `scripts/`, root-level Python files
- Contains: Python scripts for CSV data processing
- Depends on: External data sources (Intervals.icu exports)
- Used by: Content authors (manual execution)

## Data Flow

**Content Publishing Flow:**

1. Author creates/edits Markdown file in `content/blog/YYYY-MM-DD-slug/index.md`
2. Images placed alongside in `content/blog/YYYY-MM-DD-slug/images/`
3. Push to `main` triggers `.github/workflows/hugo.yml`
4. Hugo builds static HTML into `public/` directory
5. GitHub Pages deploys the `public/` artifact

**Page Rendering Flow:**

1. Hugo reads `hugo.toml` for site config (title, menus, params)
2. For each content file, Hugo applies `themes/minimal/layouts/_default/baseof.html` as the shell
3. `baseof.html` includes `partials/header.html` (site title + nav from `[menu]` config) and `partials/footer.html`
4. The `{{ block "main" . }}` is filled by either `list.html` (section/home pages) or `single.html` (individual posts/pages)
5. CSS loaded from `themes/minimal/static/css/style.css`

**State Management:**
- No client-side state management; purely static HTML
- Some blog posts include inline JavaScript for interactive elements (Leaflet maps, Plotly charts in `content/blog/2026-03-05-climbing-routes/index.md`)

## Key Abstractions

**Page Bundles:**
- Purpose: Co-locate a blog post's Markdown and its images in a single directory
- Examples: `content/blog/2026-03-05-activity-overview/`, `content/blog/2026-03-27-video-editing-journey/`
- Pattern: Each post directory contains `index.md` plus an `images/` subdirectory

**Template Hierarchy:**
- Purpose: Hugo's template lookup chain determines which layout renders each page
- Examples: `themes/minimal/layouts/_default/baseof.html`, `themes/minimal/layouts/_default/single.html`
- Pattern: `baseof.html` defines the HTML shell; `list.html` and `single.html` define the `"main"` block

**Front Matter:**
- Purpose: YAML metadata at the top of each Markdown file controls title, date, draft status, and summary
- Examples: All `index.md` files in `content/blog/`
- Pattern: `title`, `date`, `draft`, `summary` fields

## Entry Points

**Hugo Build:**
- Location: `hugo.toml`
- Triggers: `hugo` CLI command (locally) or GitHub Actions workflow
- Responsibilities: Reads config, processes all content, applies theme, outputs static site to `public/`

**GitHub Actions Workflow:**
- Location: `.github/workflows/hugo.yml`
- Triggers: Push to `main` branch, or manual `workflow_dispatch`
- Responsibilities: Installs Hugo 0.157.0, builds with `--minify`, deploys to GitHub Pages

**Homepage:**
- Location: `themes/minimal/layouts/_default/list.html` (the `{{ if .IsHome }}` branch)
- Triggers: Visiting the root URL
- Responsibilities: Lists all blog posts from the `blog` section with title, date, and summary

**Blog Section:**
- Location: `content/blog/_index.md` + `themes/minimal/layouts/_default/list.html` (the `{{ eq .Section "blog" }}` branch)
- Triggers: Visiting `/blog/`
- Responsibilities: Lists all blog posts under the "Blog" heading

**About Page:**
- Location: `content/about.md`
- Triggers: Visiting `/about/`
- Responsibilities: Renders static about page content via `single.html`

## Error Handling

**Strategy:** Not applicable for a static site. Hugo fails at build time if templates or content have errors.

**Patterns:**
- Hugo's `{{ with }}` blocks provide nil-safe access to optional fields (e.g., `.Params.summary`, `.Description`)
- The `{{ if not .IsHome }}` guard in `baseof.html` conditionally prefixes the page title

## Cross-Cutting Concerns

**Logging:** Not applicable (static site). Hugo provides build-time logging.

**Validation:** Hugo validates templates and front matter at build time. No runtime validation.

**Authentication:** None. Fully public static site.

**SEO:**
- `enableRobotsTXT = true` in `hugo.toml`
- `<meta name="description">` set from page or site params in `baseof.html`
- Privacy settings disable Disqus, Google Analytics, and X tracking in `hugo.toml`

**Responsive Design:**
- Single CSS file with a `@media (max-width: 600px)` breakpoint in `themes/minimal/static/css/style.css`
- Max content width constrained to 640px via `--max-width` CSS variable

---

*Architecture analysis: 2026-03-27*

# Technology Stack

**Analysis Date:** 2026-03-27

## Languages

**Primary:**
- Go templating (Hugo templates) - Used in all layout files under `themes/minimal/layouts/`
- Markdown - All content in `content/` directory
- CSS - Single stylesheet at `themes/minimal/static/css/style.css`

**Secondary:**
- JavaScript (ES6+, vanilla) - Inline scripts in blog posts for data visualization (`content/blog/2026-03-05-climbing-routes/index.md`)
- Python 3 - Utility scripts in `scripts/` and root directory (`scripts/transform_climbing_csv.py`, `convert_to_french_fixed.py`, `fix_data_properly.py`)

## Runtime

**Environment:**
- Hugo Extended 0.157.0 (pinned in `.github/workflows/deploy.yml`)
- Hugo is NOT installed locally (not found in PATH); development may rely on another install method or Docker
- Python 3.x for utility scripts (no version pinned)

**Package Manager:**
- None. No `package.json`, `Gemfile`, `requirements.txt`, or `pyproject.toml` present
- Hugo themes are vendored directly in `themes/minimal/` (not a git submodule)

## Frameworks

**Core:**
- Hugo 0.157.0 (Extended) - Static site generator
  - Config: `hugo.toml`
  - Theme: Custom "Minimal" theme at `themes/minimal/`

**Testing:**
- None detected

**Build/Dev:**
- Hugo CLI - `hugo --minify` for production builds
- GitHub Actions - CI/CD pipeline at `.github/workflows/deploy.yml`

## Key Dependencies

**Critical:**
- Hugo Extended (required for SCSS support, though currently only plain CSS is used)

**CDN Libraries (loaded in blog post content, not globally):**
- Leaflet 1.9.4 - Interactive maps (`unpkg.com/leaflet@1.9.4`)
- Plotly.js (latest) - Data visualization charts (`cdn.plot.ly/plotly-latest.min.js`)
- Mermaid.js (latest) - Diagram rendering (`cdn.jsdelivr.net/npm/mermaid`)
- Instagram embed.js - Social media embed (`www.instagram.com/embed.js`)

**Python (scripts only):**
- `csv` (stdlib) - CSV parsing in `scripts/transform_climbing_csv.py`
- `collections.Counter` (stdlib) - Data aggregation
- `pathlib.Path` (stdlib) - File path handling
- No third-party Python packages required

## Configuration

**Hugo Config (`hugo.toml`):**
- `baseURL`: `https://tbohnstedt.cloud/`
- `theme`: `minimal`
- `paginate`: 20
- `enableRobotsTXT`: true
- Goldmark renderer: `unsafe = true` (allows raw HTML in Markdown)
- Syntax highlighting: Monokai style
- Privacy: Disqus, Google Analytics, and Twitter/X all disabled
- YouTube: privacy-enhanced mode enabled

**Custom Domain:**
- `static/CNAME` contains `tbohnstedt.cloud`

**Build (CI):**
- `HUGO_ENVIRONMENT`: production
- `HUGO_CACHEDIR`: runner temp directory
- Build command: `hugo --minify --baseURL "$base_url/"`

## Platform Requirements

**Development:**
- Hugo Extended 0.157.0 installed locally
- Python 3.x for running utility scripts
- No Node.js or npm required
- No database required

**Production:**
- GitHub Pages (static file hosting)
- Custom domain: `tbohnstedt.cloud`
- No server-side runtime required

---

*Stack analysis: 2026-03-27*

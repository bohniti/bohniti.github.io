# Codebase Structure

**Analysis Date:** 2026-03-27

## Directory Layout

```
bohniti.github.io/
├── .claude/                    # Claude Code configuration
├── .github/
│   └── workflows/
│       └── hugo.yml            # GitHub Actions: build & deploy to Pages
├── .planning/
│   └── codebase/               # GSD codebase analysis documents
├── archetypes/
│   └── default.md              # Hugo archetype for new content
├── content/
│   ├── about.md                # /about/ page
│   └── blog/
│       ├── _index.md           # Blog section index (title only)
│       └── YYYY-MM-DD-slug/    # Page bundle per blog post
│           ├── index.md        # Post content (Markdown + front matter)
│           └── images/         # Post-specific images
├── scripts/
│   └── transform_climbing_csv.py  # Data transform utility
├── static/
│   └── files/                  # Downloadable files (PDF, CSV, JS)
├── themes/
│   └── minimal/
│       ├── theme.toml          # Theme metadata
│       ├── layouts/
│       │   ├── _default/
│       │   │   ├── baseof.html # Base HTML shell (head, body wrapper)
│       │   │   ├── list.html   # Home page + section list template
│       │   │   └── single.html # Individual post/page template
│       │   └── partials/
│       │       ├── header.html # Site header with nav menu
│       │       └── footer.html # Site footer with links
│       └── static/
│           └── css/
│               └── style.css   # All site styles (Flexoki palette)
├── hugo.toml                   # Hugo site configuration
├── .gitignore                  # Ignores public/, resources/, .DS_Store
├── convert_to_french_fixed.py  # Untracked utility script (root)
└── fix_data_properly.py        # Untracked utility script (root)
```

## Directory Purposes

**`content/`:**
- Purpose: All site content authored in Markdown
- Contains: Static pages (`about.md`) and blog post page bundles
- Key files: `content/about.md`, `content/blog/_index.md`

**`content/blog/`:**
- Purpose: Blog post collection using Hugo page bundles
- Contains: One directory per post, each with `index.md` and optional `images/`
- Key files: Each `index.md` has YAML front matter (`title`, `date`, `draft`, `summary`)

**`themes/minimal/`:**
- Purpose: Custom Hugo theme providing all layout and styling
- Contains: Go HTML templates and CSS
- Key files: `themes/minimal/layouts/_default/baseof.html`, `themes/minimal/static/css/style.css`

**`themes/minimal/layouts/_default/`:**
- Purpose: Core page templates
- Contains: `baseof.html` (HTML shell), `list.html` (homepage + section lists), `single.html` (individual pages)

**`themes/minimal/layouts/partials/`:**
- Purpose: Reusable template fragments included via `{{ partial }}`
- Contains: `header.html` (site title + nav), `footer.html` (footer links)

**`static/`:**
- Purpose: Files served verbatim at site root (no Hugo processing)
- Contains: PDF (CV), CSV data files, JavaScript data file
- Key files: `static/files/timo-bohnstedt-cv.pdf`, `static/files/dataset.csv`, `static/files/climbing-locations.js`

**`scripts/`:**
- Purpose: Offline data transformation utilities (not part of site build)
- Contains: Python scripts for preparing data
- Key files: `scripts/transform_climbing_csv.py`

**`archetypes/`:**
- Purpose: Hugo content templates used by `hugo new`
- Contains: `default.md` with date, draft, and title placeholders

**`.github/workflows/`:**
- Purpose: CI/CD pipeline definition
- Contains: Single workflow file for Hugo build and GitHub Pages deployment
- Key files: `.github/workflows/hugo.yml`

## Key File Locations

**Entry Points:**
- `hugo.toml`: Site configuration (base URL, theme, menus, markup settings, privacy)
- `.github/workflows/hugo.yml`: CI/CD pipeline (Hugo 0.157.0, build + deploy)

**Configuration:**
- `hugo.toml`: All site-level config (base URL, title, author, menu items, markup options)
- `themes/minimal/theme.toml`: Theme metadata (name, license, description)

**Core Templates:**
- `themes/minimal/layouts/_default/baseof.html`: HTML document shell, loads CSS, includes header/footer partials
- `themes/minimal/layouts/_default/list.html`: Renders homepage (all blog posts) and section pages (blog listing)
- `themes/minimal/layouts/_default/single.html`: Renders individual blog posts and standalone pages
- `themes/minimal/layouts/partials/header.html`: Site header with title link and navigation from `[menu.main]`
- `themes/minimal/layouts/partials/footer.html`: Footer with hardcoded links (About, Blog, GitHub)

**Styling:**
- `themes/minimal/static/css/style.css`: Single CSS file, 253 lines, Flexoki color palette, 640px max-width, one responsive breakpoint

**Content:**
- `content/about.md`: About page with CV summary and link to PDF
- `content/blog/_index.md`: Blog section title page (minimal, title only)
- `content/blog/*/index.md`: Individual blog posts

## Naming Conventions

**Blog Post Directories:**
- Pattern: `YYYY-MM-DD-slug-with-dashes/`
- Examples: `2026-03-05-activity-overview/`, `2026-03-27-video-editing-journey/`

**Content Files:**
- Page bundles always use `index.md` as the content file
- Standalone pages use `kebab-case.md` (e.g., `about.md`)

**Image Directories:**
- Pattern: `images/` subdirectory within each page bundle
- Image names: Descriptive, spaces allowed (Hugo handles URL encoding)

**Templates:**
- Hugo convention: `baseof.html`, `list.html`, `single.html` in `_default/`
- Partials: `kebab-case.html` (e.g., `header.html`, `footer.html`)

**CSS:**
- Single file: `style.css`
- CSS classes use `kebab-case` (e.g., `site-header`, `post-item-title`, `page-content`)
- CSS custom properties use `--kebab-case` (e.g., `--bg`, `--text-secondary`, `--max-width`)

## Where to Add New Code

**New Blog Post:**
1. Create directory: `content/blog/YYYY-MM-DD-descriptive-slug/`
2. Create `index.md` with YAML front matter: `title`, `date`, `draft`, `summary`
3. Place images in `content/blog/YYYY-MM-DD-descriptive-slug/images/`
4. Reference images with relative paths: `![alt](images/filename.png)`
5. Or use `hugo new blog/YYYY-MM-DD-slug/index.md` to scaffold from archetype

**New Static Page (e.g., /projects/):**
1. Create `content/projects.md` (or `content/projects/_index.md` for a section)
2. Add YAML front matter with `title`
3. Add menu entry in `hugo.toml` under `[menu]` with appropriate `weight`

**New Template Partial:**
1. Create file in `themes/minimal/layouts/partials/`
2. Include in other templates with `{{ partial "filename.html" . }}`

**New CSS Styles:**
1. Add to `themes/minimal/static/css/style.css`
2. Follow existing pattern: section comment (`/* === Section Name === */`), BEM-like class naming

**New Static Files (downloads, data):**
1. Place in `static/files/`
2. Reference in content as `/files/filename.ext`

**New Utility Script:**
1. Place in `scripts/`
2. Use descriptive `snake_case.py` naming

## Special Directories

**`public/`:**
- Purpose: Hugo build output (generated static site)
- Generated: Yes (by `hugo` command)
- Committed: No (in `.gitignore`)

**`resources/`:**
- Purpose: Hugo resource cache (processed images, etc.)
- Generated: Yes (by Hugo)
- Committed: No (in `.gitignore`)

**`.planning/`:**
- Purpose: GSD planning and codebase analysis documents
- Generated: Yes (by GSD tooling)
- Committed: Yes

---

*Structure analysis: 2026-03-27*

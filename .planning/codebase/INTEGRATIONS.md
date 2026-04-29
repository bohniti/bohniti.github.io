# External Integrations

**Analysis Date:** 2026-03-27

## APIs & External Services

**Map Tiles:**
- OpenStreetMap - Tile server for Leaflet map backgrounds
  - URL pattern: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
  - Used in: `content/blog/2026-03-05-climbing-routes/index.md`
  - Auth: None (public API)
  - Note: Attribution required and included

**Geocoding (referenced, not actively called):**
- OpenStreetMap Nominatim - Referenced as data source for climbing location coordinates
  - Used offline/pre-processed; no live API calls from the site
  - Mentioned in: `content/blog/2026-03-05-climbing-routes/index.md` (About the Data section)

## CDN Dependencies

**JavaScript Libraries (loaded per-page, not globally):**
- Leaflet 1.9.4 - `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`
  - CSS: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.css`
  - Used in: `content/blog/2026-03-05-climbing-routes/index.md`
- Plotly.js (latest) - `https://cdn.plot.ly/plotly-latest.min.js`
  - Used in: `content/blog/2026-03-05-climbing-routes/index.md`
- Mermaid.js (latest) - `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`
  - Used in: `content/blog/2026-03-15-intervals-copilot/index.md`
- Instagram embed.js - `https://www.instagram.com/embed.js`
  - Used in: `content/blog/2026-03-27-video-editing-journey/index.md`

**CDN Providers:**
- unpkg.com (Leaflet)
- cdn.plot.ly (Plotly)
- cdn.jsdelivr.net (Mermaid)
- instagram.com (Instagram embeds)

## Data Storage

**Databases:**
- None. Fully static site with no database.

**File Storage:**
- Static CSV files served from `static/files/`:
  - `static/files/dataset.csv` - Main climbing route dataset (416 routes)
  - `static/files/dataset_old.csv` - Previous version of climbing data
  - `static/files/climbing_journal_import.csv` - Transformed data for Climbers Journal
  - `static/files/climbing-locations.js` - Location data (JavaScript)
  - `static/files/timo-bohnstedt-cv.pdf` - CV document
- Blog post images co-located in `content/blog/*/images/`

**Caching:**
- Hugo build cache (`HUGO_CACHEDIR` in CI only)
- No application-level caching

## Authentication & Identity

**Auth Provider:**
- None. Public static site with no authentication.

## Monitoring & Observability

**Error Tracking:**
- None

**Analytics:**
- Google Analytics explicitly disabled in `hugo.toml` (`[privacy.googleAnalytics] disable = true`)

**Logs:**
- `console.log` / `console.error` in client-side JavaScript for debugging (climbing routes page)
- No server-side logging (static site)

## CI/CD & Deployment

**Hosting:**
- GitHub Pages
  - Custom domain: `tbohnstedt.cloud` (configured via `static/CNAME`)
  - HTTPS enabled (implied by `baseURL = 'https://tbohnstedt.cloud/'`)

**CI Pipeline:**
- GitHub Actions
  - Workflow: `.github/workflows/deploy.yml`
  - Trigger: Push to `main` branch, or manual `workflow_dispatch`
  - Build: Ubuntu latest, Hugo Extended 0.157.0
  - Deploy: `actions/deploy-pages@v4`
  - Concurrency: Single deployment at a time (`cancel-in-progress: false`)

**GitHub Actions Used:**
- `actions/checkout@v4` - Repository checkout
- `actions/configure-pages@v5` - GitHub Pages configuration
- `actions/upload-pages-artifact@v3` - Build artifact upload
- `actions/deploy-pages@v4` - Pages deployment

**Permissions:**
- `contents: read` - Read repository
- `pages: write` - Write to GitHub Pages
- `id-token: write` - OIDC token for deployment

## Environment Configuration

**Required env vars:**
- None for local development (Hugo uses `hugo.toml` for all configuration)
- CI-only: `HUGO_VERSION`, `HUGO_CACHEDIR`, `HUGO_ENVIRONMENT` (set in workflow)

**Secrets:**
- No application secrets required
- GitHub Pages deployment uses OIDC (`id-token: write`), no manual token needed

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Social & External Links

**Outbound references (in templates/content):**
- GitHub profile: `https://github.com/bohniti` (in `themes/minimal/layouts/partials/footer.html`)
- Instagram embeds in blog posts
- No social login or API integration

## Data Sources (Offline/Pre-processed)

**Climbing Data:**
- Vertical Life app export - 404 European climbing routes
- Mountain Project - 12 North American climbing routes
- Data merged and geocoded offline, stored as `static/files/dataset.csv`
- Transform script: `scripts/transform_climbing_csv.py` (converts to Climbers Journal format)

---

*Integration audit: 2026-03-27*

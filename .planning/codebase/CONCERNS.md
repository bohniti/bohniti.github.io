# Codebase Concerns

> Last updated: 2026-03-27

## Tech Debt

**Untracked one-off Python scripts in repo root:**
- Issue: Two utility scripts (`convert_to_french_fixed.py`, `fix_data_properly.py`) sit untracked in the project root. They contain hardcoded absolute paths and appear to be throwaway data-munging scripts that were used once to transform `static/files/dataset.csv`.
- Files: `convert_to_french_fixed.py`, `fix_data_properly.py`
- Impact: Clutters the repo root, confuses contributors about what is part of the project. Hardcoded paths (e.g., `/Users/timo/Development/bohniti.github.io/static/files/dataset.csv`) make them non-portable.
- Fix approach: Either delete them (their work is done), move them to `scripts/` with relative paths, or add them to `.gitignore`.

**Stale `dataset_old.csv` shipped to production:**
- Issue: `static/files/dataset_old.csv` (56 KB, 424 rows) is an older version of the climbing dataset with a different schema (no `grade_uiaa` column, uses country codes like `DE` instead of French grades). It is never referenced by any page but is served publicly.
- Files: `static/files/dataset_old.csv`
- Impact: Wastes bandwidth, ships unnecessary personal data to production, potential confusion about which dataset is canonical.
- Fix approach: Delete `static/files/dataset_old.csv` or move it out of `static/`.

**Unused `climbing-locations.js` shipped to production:**
- Issue: `static/files/climbing-locations.js` defines a `locationCoordinates` map and helper functions (`getLocationCoordinates`, `gradeToNumber`, `getGradeColor`), but the climbing routes blog post (`content/blog/2026-03-05-climbing-routes/index.md`) has its own inline implementations of the same functions and reads coordinates from the CSV `latitude`/`longitude` columns instead.
- Files: `static/files/climbing-locations.js`
- Impact: Dead code served publicly. Duplicated grade-mapping logic between this file and the inline `<script>` in the climbing blog post.
- Fix approach: Delete `static/files/climbing-locations.js` or refactor the climbing post to import it (using a `<script src>` tag) to avoid duplication.

**Duplicate grade-conversion logic:**
- Issue: Grade-to-number mapping is implemented independently in at least three places, each with slightly different mappings and keys.
- Files: `static/files/climbing-locations.js` (lines 58-66), `content/blog/2026-03-05-climbing-routes/index.md` (lines 33-59), `convert_to_french_fixed.py` (lines 24-37)
- Impact: If grade mappings need updating, changes must be made in multiple places. Different implementations may produce inconsistent results.
- Fix approach: Consolidate into one authoritative JS file in `static/` and reference it from the blog post.

## Security Considerations

**Hugo Goldmark `unsafe = true` enabled globally:**
- Risk: The `hugo.toml` setting `[markup.goldmark.renderer] unsafe = true` allows raw HTML in all Markdown content. This is intentional (the climbing post uses inline `<script>` and `<div>` tags), but it means any Markdown content can inject arbitrary HTML/JS.
- Files: `hugo.toml` (line 15)
- Current mitigation: Single-author blog, so the risk is low. All content is authored by the site owner.
- Recommendations: This is acceptable for a personal blog. If guest posts or user-generated content are ever added, revisit this setting.

**Third-party CDN scripts loaded without integrity hashes:**
- Risk: The climbing routes post loads Leaflet and Plotly from unpinned CDN URLs without Subresource Integrity (SRI) hashes. A CDN compromise could inject malicious code.
- Files: `content/blog/2026-03-05-climbing-routes/index.md` (lines 21-23)
  - `https://unpkg.com/leaflet@1.9.4/dist/leaflet.css`
  - `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`
  - `https://cdn.plot.ly/plotly-latest.min.js` (unpinned version!)
- Current mitigation: None.
- Recommendations: Pin Plotly to a specific version (replace `plotly-latest.min.js` with a versioned URL like `plotly-2.x.x.min.js`). Add `integrity` and `crossorigin` attributes to all CDN `<script>` and `<link>` tags.

**Instagram embed script loaded without controls:**
- Risk: The video editing post loads `//www.instagram.com/embed.js` which is a third-party script with full page access.
- Files: `content/blog/2026-03-27-video-editing-journey/index.md` (line 17)
- Current mitigation: None. Standard practice for Instagram embeds.
- Recommendations: Acceptable for a personal blog. No action needed unless privacy is a concern.

## Performance Bottlenecks

**Large unoptimized images in the video editing post:**
- Problem: Three images in the video editing blog post exceed 2 MB each, totaling ~9.6 MB for a single page. These are full-resolution PNG screenshots.
- Files:
  - `content/blog/2026-03-27-video-editing-journey/images/Chaotic timeline.png` (5.0 MB)
  - `content/blog/2026-03-27-video-editing-journey/images/Insta360 + DaVinci side-by-side.png` (2.5 MB)
  - `content/blog/2026-03-27-video-editing-journey/images/Clip catalog spreadsheet.png` (2.1 MB)
- Cause: Raw PNG screenshots not converted to WebP or compressed.
- Improvement path: Convert to WebP or JPEG at reasonable quality (80-90%). Use Hugo's built-in image processing (`{{ $image.Resize }}`) or compress before committing. Target < 300 KB per image. Also rename files to remove spaces (e.g., `chaotic-timeline.webp`).

**Plotly loaded as `plotly-latest.min.js` (full bundle):**
- Problem: The full Plotly.js bundle is ~3.5 MB uncompressed. The climbing post only uses basic bar and scatter charts.
- Files: `content/blog/2026-03-05-climbing-routes/index.md` (line 23)
- Cause: Using the full Plotly bundle instead of a partial build.
- Improvement path: Use `plotly-basic.min.js` (~1 MB) or `plotly.js` partial bundles that include only `scatter` and `bar` trace types.

**CSV fetched and parsed client-side on every page load:**
- Problem: The climbing routes page fetches `dataset.csv` (58 KB) via `fetch()` and parses it with a custom CSV parser on every visit. There is no caching strategy beyond browser defaults.
- Files: `content/blog/2026-03-05-climbing-routes/index.md` (lines 144-188)
- Cause: Data is loaded dynamically rather than pre-rendered at build time.
- Improvement path: For a static site, consider generating the chart data as JSON at build time (via a Hugo data template or a build script), so the page loads pre-processed data instead of raw CSV.

## Fragile Areas

**Custom inline CSV parser:**
- Files: `content/blog/2026-03-05-climbing-routes/index.md` (lines 103-141)
- Why fragile: The hand-rolled CSV parser handles basic quoted fields but does not handle escaped quotes (`""` inside quoted fields), newlines within quoted fields, or BOM markers. If the CSV data ever contains commas or quotes in the `comment` field, parsing will break silently.
- Safe modification: If the CSV data changes, verify parsing manually. Consider switching to Papa Parse or a similar library.
- Test coverage: None. No tests exist anywhere in this project.

**Hardcoded data statistics in blog post:**
- Files: `content/blog/2026-03-05-climbing-routes/index.md` (lines 463-496)
- Why fragile: The "About the Data" section hardcodes statistics like "404 routes", "12 routes", "93 unique climbing areas", "386 out of 416 routes (93% coverage)". These go stale whenever the dataset changes.
- Safe modification: Update the prose whenever the CSV is updated, or generate these numbers dynamically.

## Missing Critical Features

**No `<meta>` tags for social sharing (Open Graph / Twitter Cards):**
- Problem: The `baseof.html` template has only a basic `<meta name="description">` tag. There are no Open Graph (`og:title`, `og:image`, etc.) or Twitter Card meta tags.
- Files: `themes/minimal/layouts/_default/baseof.html`
- Blocks: Blog posts shared on social media will not show rich previews (title, description, image).

**No RSS feed configuration:**
- Problem: Hugo generates RSS by default, but there is no RSS link in the header or footer for discoverability, and no custom RSS template to control what is included.
- Files: `themes/minimal/layouts/partials/header.html`, `themes/minimal/layouts/partials/footer.html`

**No favicon:**
- Problem: No favicon is defined in `baseof.html` or present in `static/`.
- Files: `themes/minimal/layouts/_default/baseof.html`, `static/`

**No 404 page:**
- Problem: No custom `layouts/404.html` template exists. Hugo will generate a default one, but it will be unstyled.
- Files: `themes/minimal/layouts/` (missing `404.html`)

## Test Coverage Gaps

**No tests exist:**
- What's not tested: The entire codebase has zero automated tests. This includes the Python scripts in `scripts/` and the JavaScript in the blog posts.
- Files: All files. No test files, no test framework, no CI test step.
- Risk: Data transformation scripts (`scripts/transform_climbing_csv.py`, `convert_to_french_fixed.py`, `fix_data_properly.py`) can silently corrupt data. The inline JS CSV parser can silently fail on edge cases.
- Priority: Low for a personal blog, but the data transformation scripts would benefit from basic assertions.

## Dependencies at Risk

**Hugo version pinned in CI but not locally enforced:**
- Risk: `deploy.yml` pins Hugo `0.157.0`, but there is no `.hugo-version` file or local version check. Local development may use a different Hugo version, causing build differences.
- Files: `.github/workflows/deploy.yml` (line 25)
- Impact: Potential "works on my machine" issues.
- Migration plan: Add a `.hugo-version` file or use a tool like `hugo-installer` to pin the version locally.

## Configuration Issues

**Image filenames contain spaces:**
- Issue: Several image files contain spaces in their names (e.g., `Chaotic timeline.png`, `Clip catalog spreadsheet.png`). While Hugo handles this, it can cause issues with some tools and requires URL encoding.
- Files: `content/blog/2026-03-27-video-editing-journey/images/`
- Fix approach: Rename to use hyphens (e.g., `chaotic-timeline.png`) and update references in the Markdown.

**`climbing_journal_import.csv` served publicly but is only for export:**
- Issue: `static/files/climbing_journal_import.csv` is an import file generated by `scripts/transform_climbing_csv.py` for use with Climbers Journal. It is not referenced by any page but is publicly accessible.
- Files: `static/files/climbing_journal_import.csv`
- Fix approach: Move to a non-`static` directory if it does not need to be publicly served, or document its purpose.

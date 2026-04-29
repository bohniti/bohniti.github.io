# Phase 5: Wordmark + Favicon Wiring - Pattern Map

**Mapped:** 2026-04-29
**Files analyzed:** 5 (4 modified, 1 new)
**Analogs found:** 5 / 5 (all in-repo)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `themes/minimal/layouts/partials/header.html` (modify) | hugo-partial / template | render-time | self (existing partial) | exact |
| `themes/minimal/layouts/_default/baseof.html` (modify) | hugo-layout / `<head>` host | render-time | self (existing layout) | exact |
| `themes/minimal/layouts/partials/favicon.html` (new) | hugo-partial / `<head>` fragment | render-time | `themes/minimal/layouts/partials/header.html`, `footer.html` | structural-match |
| `themes/minimal/static/css/style.css` (modify) | stylesheet | static-asset | self (existing block-organized CSS) | exact |
| `scripts/build_brand_assets.py` (modify) | utility script (Pillow image pipeline) | batch / file-I/O | self + `scripts/transform_climbing_csv.py` | exact + role-match |

**Note on line numbers:** CONTEXT cited `style.css` lines 74-83 and `@media (max-width: 600px)` ~259, and `baseof.html` lines 8-9. The current files have evolved since then (Phase 4 added the dark palette block, theme-toggle styles, IIFE bootstrap). Verified line numbers below are from the actual on-disk files.

## Pattern Assignments

### `themes/minimal/layouts/partials/header.html` (modify — wordmark replaces text title)

**Analog:** Self. The full file is 11 lines; the change is localized to line 3 (the `{{ .Site.Title }}` text inside `.site-title > a`). Surrounding structure stays.

**Current full content** (lines 1-11):
```html
<header class="site-header">
  <div class="site-title">
    <a href="{{ .Site.BaseURL }}">{{ .Site.Title }}</a>
  </div>
  <nav class="site-nav">
    {{ range .Site.Menus.main }}
      <a href="{{ .URL }}"{{ if $.IsMenuCurrent "main" . }} class="active"{{ end }}>{{ .Name }}</a>
    {{ end }}
    <button type="button" class="theme-toggle" aria-pressed="false">Dark</button>
  </nav>
</header>
```

**Pattern to apply** (D-04: `<a>` wrapper stays; `{{ .Site.Title }}` text becomes two `<img>` tags):
```html
<a href="{{ .Site.BaseURL }}">
  <img class="wordmark wordmark-light" src="{{ "images/brand/logo-light.png" | absURL }}" alt="Timo Bohnstedt" width="200" height="117">
  <img class="wordmark wordmark-dark"  src="{{ "images/brand/logo-dark.png"  | absURL }}" alt="Timo Bohnstedt" width="200" height="117">
</a>
```

**`absURL` precedent in this codebase:** `baseof.html` line 23 uses `{{ "css/style.css" | absURL }}` for the stylesheet `<link>`. Use the same idiom for `<img src>` so the wordmark resolves correctly under any `baseURL`.

**Alt-text precedent:** Footer SVG icons (lines 6, 12 of `footer.html`) use `aria-label="GitHub"` / `aria-label="Instagram"` for empty SVGs. For `<img>` elements, the project uses `alt="..."`. D-02 locks alt to `"Timo Bohnstedt"` on both variants; the hidden one is removed from the a11y tree by `display: none`.

---

### `themes/minimal/layouts/_default/baseof.html` (modify — insert favicon partial in `<head>`)

**Analog:** Self. The change is a single-line insertion in the existing `<head>`; surrounding structure (charset, viewport, color-scheme meta, theme-color meta, title, description, theme-bootstrap IIFE, stylesheet link) all stay intact.

**Current `<head>` opening, lines 3-23** (the relevant range for insertion):
```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#FFFCF0">
  <title>{{ if not .IsHome }}{{ .Title }} — {{ end }}{{ .Site.Title }}</title>
  <meta name="description" content="{{ with .Description }}{{ . }}{{ else }}{{ .Site.Params.description }}{{ end }}">
  <script>
    // Theme bootstrap — reads localStorage key 'theme', falls back to OS prefers-color-scheme.
    (function () {
      ...
    })();
  </script>
  <link rel="stylesheet" href="{{ "css/style.css" | absURL }}">
</head>
```

**Insertion point per D-14** (between `<title>` and `<meta name="description">`):
- `<title>` is currently line **8**
- `<meta name="description">` is currently line **9**

**Insert at the new line 9** (pushing description to 10, etc.):
```html
  {{ partial "favicon.html" . }}
```

**Partial-include precedent in this file:** Lines 27 and 31 use `{{ partial "header.html" . }}` and `{{ partial "footer.html" . }}` with the dot context. Mirror this exactly — Hugo standard.

---

### `themes/minimal/layouts/partials/favicon.html` (new — 3 `<link>` tags)

**Analog:** `themes/minimal/layouts/partials/header.html` (structure of a Hugo partial that emits raw HTML directly without a wrapping `define`/`block`). Also: `baseof.html` line 23's `{{ "css/style.css" | absURL }}` for the URL idiom.

**Structural pattern (from `header.html`):** Hugo partials in this project emit raw HTML at the top level — no `{{ define "main" }}` wrapper, no leading shebang, no front-matter. Just template content. Example (first 4 lines of `header.html`):
```html
<header class="site-header">
  <div class="site-title">
    <a href="{{ .Site.BaseURL }}">{{ .Site.Title }}</a>
  </div>
```

**`absURL` pipe pattern (from `baseof.html` line 23):**
```html
<link rel="stylesheet" href="{{ "css/style.css" | absURL }}">
```

**New partial content per D-13** (3 lines, SVG first per spec):
```html
<link rel="icon" type="image/svg+xml" href="{{ "favicon.svg" | absURL }}">
<link rel="icon" type="image/x-icon" href="{{ "favicon.ico" | absURL }}">
<link rel="apple-touch-icon" href="{{ "apple-touch-icon.png" | absURL }}">
```

**Why this matches the codebase:** Same `absURL` idiom as the existing stylesheet `<link>`. Hugo serves `themes/minimal/static/foo` at `/foo` (root-relative) — the favicon outputs land at the theme static root (D-12), so `"favicon.svg" | absURL` resolves to e.g. `https://tbohnstedt.cloud/favicon.svg`.

---

### `themes/minimal/static/css/style.css` (modify — wordmark styling, mobile override)

**Analog:** Self. The file is block-organized with `/* === SectionName === */` comment headers. Each new rule slots into the existing `/* === Header === */` section.

**Current `.site-title` rules (lines 74-83):**
```css
.site-title a {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
}

.site-title a:hover {
  color: var(--accent);
}
```

**Decision per Claude's Discretion (CONTEXT line 90):** Keep these rules as-is — they still color the anchor (link hover behavior preserved) but `font-size`/`font-weight`/`color` no longer paint visible glyphs once the text is replaced by `<img>`. Add `.site-title a` resets and `.wordmark` rules below the existing block. (Alternative — strip the typography props — is fine but adds churn for no behavior change.)

**Pattern for the dark-theme image swap (D-01) — note that Phase 4 uses `:root[data-theme="dark"]` for palette tokens (style.css line 20), but `[data-theme]` selectors that target descendants must be written `html[data-theme="..."]` per CONTEXT D-01:**
```css
html[data-theme="light"] .wordmark-dark { display: none; }
html[data-theme="dark"]  .wordmark-light { display: none; }
```

**Pattern for per-variant seam-masking bg (D-05, honors Phase 4 D-02 contract):**
```css
.wordmark-light { background: #FEFEFE; }
.wordmark-dark  { background: #000000; }
```

These hex values come from Phase 3's mid-execution-recorded corner-pixel samples (CONTEXT § "Recorded hex values"): `#FEFEFE` for `-light` PNG, `#000000` for `-dark` PNG. Hardcoded — they intentionally do NOT track `--bg`/`--bg-dark` (Flexoki `#FFFCF0`/`#100F0F`).

**Pattern for explicit dimensions (D-03, prevents CLS):**
```css
.wordmark {
  display: block;
  width: 200px;
  height: 117px;
}
```
The CSS dims back up the `width="200" height="117"` HTML attrs on each `<img>` — both must match.

**Existing `@media (max-width: 600px)` block (lines 306-311):**
```css
@media (max-width: 600px) {
  html { font-size: 16px; }
  .site-header { flex-direction: column; gap: 0.5rem; }
  .site-wrapper { padding: 2rem 0 4rem; }
  .footer-links { gap: 1rem; }
}
```
**Mobile override pattern per D-03 — add inside this block:**
```css
  .wordmark { width: 160px; height: 93px; }
```

**Note on alignment:** The header is `display: flex; align-items: baseline` (lines 67-72). `<img>` baseline alignment differs from text — if the wordmark sits oddly relative to the nav, switch `.site-title` or `.site-header` to `align-items: center` or set `vertical-align: middle` on `.wordmark`. This is a Claude's Discretion follow-up if visual QA reveals misalignment.

---

### `scripts/build_brand_assets.py` (modify — add 3 favicon output stages)

**Analog 1 (primary):** Self. Existing functions (`flatten_alpha`, `trim_to_content`, `pad_to_aspect`, `resize_max`, `run_pngquant`, `rgb_hex`, `fmt_kb`) define the helper-function granularity. New `build_favicon_ico`, `build_apple_touch`, `build_favicon_svg` should match this granularity (single-purpose, take `Image`/`Path` inputs, no class hierarchy).

**Analog 2 (style baseline):** `scripts/transform_climbing_csv.py` for top-level Python conventions (single-line module docstring, `pathlib.Path` constants, `if __name__ == "__main__"` guard, no type hints, snake_case).

**Current module docstring (line 2):**
```python
"""Process 8 brand source PNGs into themed light/dark output variants with matched aspects."""
```
**Update for Phase 5 expansion:** Single-line, mentions favicon outputs. E.g. `"""Process brand source PNGs into themed light/dark variants and the 3-file favicon set."""`

**Current constants block (lines 11-31):**
```python
ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "images" / "brand-source"
OUTPUT_DIR = ROOT / "themes" / "minimal" / "static" / "images" / "brand"

# (asset, max_width, force_square)
ASSETS = [
    ("logo",     800, False),
    ("icon",     512, False),
    ("minimum",  500, False),
    ("favicon",  512, True),
]

VARIANTS = ("dark", "light")
DARK_BG = (0, 0, 0)
LIGHT_BG = (253, 253, 253)

WORDMARK_MAX_BYTES = 30 * 1024  # BRAND-03: logo wordmarks <= 30 KB after pngquant
WORDMARK_FILES = ("logo-dark.png", "logo-light.png")

PNGQUANT_CMD = ["pngquant", "--quality=65-90", "--strip", "--force", "--output"]
```
**Pattern to extend:** Add a new `THEME_STATIC_DIR` constant for the 3 favicon outputs (D-12 says they land at `themes/minimal/static/`, NOT `themes/minimal/static/images/brand/`):
```python
THEME_STATIC_DIR = ROOT / "themes" / "minimal" / "static"
APPLE_TOUCH_SIZE = 180
ICO_SIZES = [(16, 16), (32, 32), (48, 48)]
```

**Helper function signature pattern (lines 79-80):**
```python
def run_pngquant(path):
    subprocess.run(PNGQUANT_CMD + [str(path), str(path)], check=True)
```
Mirror this single-line, side-effecting style for the three new stages. Stage signatures (CONTEXT integration-points line):

```python
def build_favicon_ico(source_png_path, out_path):
    """Multi-size .ico from favicon-light.png — 16/32/48 (D-10)."""
    img = Image.open(source_png_path).convert("RGB")
    img.save(out_path, format="ICO", sizes=ICO_SIZES)


def build_apple_touch(source_png_path, out_path):
    """180x180 apple-touch-icon.png from favicon-light.png (D-11)."""
    img = Image.open(source_png_path).convert("RGB")
    img = img.resize((APPLE_TOUCH_SIZE, APPLE_TOUCH_SIZE), Image.LANCZOS)
    img.save(out_path, format="PNG")
    run_pngquant(out_path)


def build_favicon_svg(light_png_path, dark_png_path, out_path):
    """PNG-wrapped SVG with embedded prefers-color-scheme dark @media (D-07, D-08)."""
    import base64
    with open(light_png_path, "rb") as f:
        light_b64 = base64.b64encode(f.read()).decode("ascii")
    with open(dark_png_path, "rb") as f:
        dark_b64 = base64.b64encode(f.read()).decode("ascii")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" '
        'width="512" height="512">'
        '<style>@media (prefers-color-scheme: dark){.l{display:none}.d{display:inline}}'
        '.d{display:none}</style>'
        '<image class="l" href="data:image/png;base64,{light}" width="512" height="512"/>'
        '<image class="d" href="data:image/png;base64,{dark}" width="512" height="512"/>'
        '</svg>'
    ).format(light=light_b64, dark=dark_b64)
    out_path.write_text(svg, encoding="ascii")
```

**Wire-in pattern (extend `main()`, after the existing `for asset, max_w, square in ASSETS` loop completes — around line 135 in the current file, before the `print(...)` block at 136-141):**
```python
    favicon_light = OUTPUT_DIR / "favicon-light.png"
    favicon_dark = OUTPUT_DIR / "favicon-dark.png"

    ico_path = THEME_STATIC_DIR / "favicon.ico"
    apple_path = THEME_STATIC_DIR / "apple-touch-icon.png"
    svg_path = THEME_STATIC_DIR / "favicon.svg"

    build_favicon_ico(favicon_light, ico_path)
    build_apple_touch(favicon_light, apple_path)
    build_favicon_svg(favicon_light, favicon_dark, svg_path)

    sizes.append((ico_path.name, ico_path.stat().st_size))
    sizes.append((apple_path.name, apple_path.stat().st_size))
    sizes.append((svg_path.name, svg_path.stat().st_size))
```

**Verbose-output convention (lines 136-141) — already prints `name -> size`. The favicon outputs slot into the same `sizes` list and therefore the same final report; no new print code needed.**

**Failure-fast pattern (lines 93-97):**
```python
if shutil.which("pngquant") is None:
    sys.exit("pngquant not found - install with 'brew install pngquant' (macOS) or your package manager")
if not SOURCE_DIR.exists():
    sys.exit("Source directory not found: {}".format(SOURCE_DIR))
```
The new code paths reuse `pngquant` (already gated) and read from `OUTPUT_DIR` (created on line 99). No additional gates needed unless `THEME_STATIC_DIR` should be asserted to exist — `themes/minimal/static/` already exists in the repo, so a runtime check is cosmetic.

---

## Shared Patterns

### Hugo `absURL` for static assets
**Source:** `themes/minimal/layouts/_default/baseof.html` line 23
**Apply to:** `partials/favicon.html` (3 `<link>` href attrs), `partials/header.html` (2 `<img>` src attrs)
```html
<link rel="stylesheet" href="{{ "css/style.css" | absURL }}">
```
The same `{{ "<path>" | absURL }}` pipeline produces a fully-qualified URL in production and a root-relative URL in dev. Use it for every asset reference; never hardcode `/foo.png` or `https://...`.

### Hugo partial inclusion with dot-context
**Source:** `themes/minimal/layouts/_default/baseof.html` lines 27, 31
**Apply to:** the favicon-partial inclusion line in `baseof.html` `<head>`
```html
{{ partial "header.html" . }}
{{ partial "footer.html" . }}
```
The trailing `.` passes the page context — required so the partial can access `.Site`, `.Title`, etc. New favicon partial does not currently use page context, but the dot is the project convention and harmless if unused.

### CSS block organization
**Source:** `themes/minimal/static/css/style.css` (whole file)
**Apply to:** Wordmark rules in `style.css`
- Section comments: `/* === Header === */` — the wordmark rules go inside the existing `/* === Header === */` block (lines 65-122), after the `.theme-toggle` rules and before `/* === Post List (Home) === */` at line 124.
- Mobile overrides go inside the existing `@media (max-width: 600px)` block at lines 306-311.
- All colors use `var(--token)` — exception: the per-variant masking bg (`#FEFEFE`/`#000000`) is hardcoded by D-05 because it must match the PNG corner pixel, not a theme token.

### Theme-aware selectors (Phase 4 contract)
**Source:** `themes/minimal/static/css/style.css` line 20 (`:root[data-theme="dark"]`), Phase 4 D-11 (attribute set on `<html>` by IIFE before stylesheet parse)
**Apply to:** `.wordmark-light` / `.wordmark-dark` swap rules
```css
:root[data-theme="dark"] { /* tokens */ }
```
For descendant selectors targeting elements (not `:root`), use `html[data-theme="..."]` form per D-01:
```css
html[data-theme="light"] .wordmark-dark { display: none; }
html[data-theme="dark"]  .wordmark-light { display: none; }
```
The IIFE in `baseof.html` lines 12-21 sets `document.documentElement.dataset.theme` synchronously before the stylesheet parses — no FOUC, no JS swap needed for the wordmark.

### Python script structure (Pillow + pngquant + pathlib)
**Source:** `scripts/build_brand_assets.py` (whole file), `scripts/transform_climbing_csv.py` (style baseline)
**Apply to:** Phase 5 extension of `build_brand_assets.py`
- Module-level constants in UPPER_CASE (`ROOT`, `SOURCE_DIR`, `OUTPUT_DIR`, `ASSETS`, `VARIANTS`)
- Single-purpose helper functions, snake_case, no type hints
- `pathlib.Path` for all paths; never raw strings concatenated with `/`
- `subprocess.run(..., check=True)` for external tools (pngquant)
- `sys.exit("message")` for failure-fast
- `if __name__ == "__main__":` guard
- Verbose `print(...)` to stdout (Phase 3 convention; Phase 5 favicon outputs already piggyback on the existing `sizes` list)
- `from PIL import Image, ImageChops` — standard import; add `import base64` (stdlib) for SVG embedding

## No Analog Found

None — every Phase 5 file has a strong in-repo precedent. The `partials/favicon.html` is structurally novel (first-ever `<head>`-fragment partial in the project) but follows the exact partial-emits-raw-HTML pattern of `header.html` and `footer.html`. The `favicon.svg` PNG-wrapper SVG is a one-off generated artifact, not a class of file with prior art — but the generation code lives in `build_brand_assets.py` and follows that script's helper-function pattern.

## Metadata

**Analog search scope:** `themes/minimal/`, `scripts/`, `.planning/phases/03-*/`, `.planning/phases/04-*/`
**Files scanned:** 8 (`header.html`, `footer.html`, `baseof.html`, `style.css`, `build_brand_assets.py`, `transform_climbing_csv.py`, plus 03/04 CONTEXT)
**Pattern extraction date:** 2026-04-29

## Verified Line-Number Cross-References (corrects CONTEXT)

CONTEXT.md cited several line numbers that have shifted since context was gathered (Phase 4 added the dark-palette block and theme-toggle rules). Use these verified numbers:

| CONTEXT claim | Actual location |
|---------------|-----------------|
| `style.css` is 264 lines | **312 lines** |
| `.site-title a` rules at lines 74-83 | **Still lines 74-83** (unchanged) |
| `@media (max-width: 600px)` at line ~259 | **Lines 306-311** |
| `baseof.html` is 19 lines | **57 lines** (Phase 4 added IIFE + toggle handler) |
| `<title>` at line 8, `<meta name="description">` at line 9 | **Still line 8 / line 9** (unchanged) |
| `header.html` is 11 lines | **11 lines** (10 lines if trailing newline ignored — Phase 4 added the toggle button at line 9) |

These minor drifts do not affect Phase 5 logic — the insertion points and pattern targets all still resolve correctly, and the planner's references to "after `<title>` / before `<meta name=description>`" and "inside the existing `<a>` anchor" remain unambiguous.

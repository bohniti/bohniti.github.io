# Plan 06-02 Summary: Site Infrastructure

**Phase:** 06-gallery
**Plan:** 02 (Wave 1, parallel to 06-01)
**Completed:** 2026-04-30
**Requirements:** GAL-01, GAL-02, GAL-06

## Edits Performed

### Edit 1: `hugo.toml`
- Inserted `[[menu.main]]` Gallery entry (`name = "Gallery"`, `url = "/gallery/"`, `weight = 2`) between Blog and About
- Bumped existing About entry weight from `2` to `3`
- Inserted new `[imaging]` table with `[imaging.exif] disableLatLong = true` between the menu and privacy blocks

Resulting menu order: Blog (1) → Gallery (2) → About (3). All other config (baseURL, languageCode, title, theme, paginate, params, markup, privacy) byte-identical to pre-edit state.

### Edit 2: `themes/minimal/layouts/_default/baseof.html`
- Line 26 changed from `<body>` to `<body class="page-{{ .Type | default "default" }}">`
- All other 57 lines preserved exactly: head IIFE (lines 11-23, Phase 4 D-09), favicon partial (line 9, Phase 5 D-13/D-14), `{{ block "main" . }}` slot (line 30), theme-toggle click-handler IIFE (lines 34-56, Phase 4 D-13)
- File length: 58 lines (unchanged)

### Edit 3: `themes/minimal/static/css/style.css`
- Inserted new `/* === Gallery === */` section between `/* === Single Post / Page === */` (ending at `.page-content hr`) and `/* === Footer === */`
- 5 rules: `body.page-gallery .site-wrapper { max-width: 1100px }`, `.gallery-grid` (locked grid template), `.gallery-item` (line-height 0 + border-radius 4px), `.gallery-item:focus-visible` (mirrors existing `.site-nav a:focus-visible` pattern minus border-radius), `.gallery-img` (width:100% / height:auto / border-radius:4px)
- ZERO `.gallery-item:hover` rule (UI-SPEC § Color: locked)
- Existing `@media (max-width: 600px)` breakpoint untouched (auto-fill handles responsive collapse naturally)

## Verification Gates

```
hugo.toml:
  grep -c '[[menu.main]]'                           = 3   ✓
  grep -c 'name = "Gallery"'                        = 1   ✓
  grep -c 'disableLatLong = true'                   = 1   ✓
  awk Blog weight                                   = 1   ✓
  awk Gallery weight                                = 2   ✓
  awk About weight                                  = 3   ✓ (bump)

baseof.html:
  wc -l                                              = 58  ✓
  grep -c 'class="page-{{ .Type'                    = 1   ✓
  grep -c '^<body>$'                                 = 0   ✓ (bare <body> removed)
  grep -c '{{ block "main" . }}'                    = 1   ✓ (Phase 5 contract)
  grep -c 'partial "favicon.html"'                  = 1   ✓ (Phase 5 D-14)
  grep -c 'document.documentElement.dataset.theme'  = 1   ✓ (Phase 4 IIFE)

style.css:
  grep -c '/* === Gallery === */'                   = 1   ✓
  grep -c 'body.page-gallery .site-wrapper'         = 1   ✓
  grep -c '.gallery-grid'                           = 1   ✓
  grep -c '.gallery-item'                           = 2   ✓ (rule + :focus-visible)
  grep -c '.gallery-img'                            = 1   ✓
  grep -c 'repeat(auto-fill, minmax(220px, 1fr))'  = 1   ✓
  grep -c '.gallery-item:hover'                     = 0   ✓ (LOCKED out)
  brace balance                                      BALANCED ✓
  Gallery section before Footer section              ORDER OK ✓
```

## Cross-Phase Integration

**For Plan 06-03:** When `content/gallery/index.md` produces `Type=gallery`, the body class becomes `page-gallery`, which triggers the `max-width: 1100px` rule. The `.gallery-grid` / `.gallery-item` / `.gallery-img` rules are dormant until Plan 06-03's template emits markup with these class names.

**For Plan 06-04:** Cold-build smoke test (`hugo --minify`) is the integration gate that surfaces any TOML/template/CSS parse error. NOT run by this plan.

**For Phase 7 (About Enrichment):** The body-class pattern is now usable. When `content/about.md` becomes `content/about/index.md` (leaf bundle), the body class shifts from `page-page` to `page-about`, enabling Phase 7's "richer About layout" CSS scoping via `body.page-about` rules.

## Hugo Type Quirk (informational, surfaced by RESEARCH)

Per RESEARCH § Type Quirk: Hugo's `.Type` defaults to `"page"` (NOT empty) for the homepage and standalone `content/{name}.md` pages. So:
- Homepage `/` emits `class="page-page"` (the `default "default"` fallback never fires)
- `/about/` (standalone today) emits `class="page-page"` (will become `class="page-about"` post-Phase-7 leaf-bundle conversion)
- `/blog/` and `/blog/{slug}/` emit `class="page-blog"` (Type derived from section folder)
- `/gallery/` (after Plan 06-03) emits `class="page-gallery"` ← the active D-09 hook

The `default "default"` fallback in the template is documented defensive intent for future maintainers; it never executes in practice.

# Plan 06-03 Summary: Gallery Leaf Bundle + Type-Derived Layout

**Phase:** 06-gallery
**Plan:** 03 (Wave 2, depends on 06-01 + 06-02)
**Completed:** 2026-04-30
**Requirements:** GAL-01, GAL-02, GAL-03, GAL-04

## Files Created

### `content/gallery/index.md` (3 lines)
```markdown
---
title: "Gallery"
---
```
Leaf-bundle index. Title-only frontmatter (mirrors `content/about.md` minimal pattern). No date, no draft, no summary, no body content.

### `themes/minimal/layouts/gallery/single.html` (28 lines)
Type-derived layout — Hugo's lookup chain resolves `Type=gallery` (auto-derived from `content/gallery/index.md`'s parent folder) to this file before falling back to `_default/single.html`. First non-default layout directory in this codebase.

The template iterates `.Resources.Match "photos/*"` (alphabetical default sort) inside a `{{ with }}` guard, processing each photo through Hugo's image pipeline twice (thumbnail + full-size) and emitting the locked grid markup with eager/lazy/fetchpriority/decoding/aria-label attribute mix.

## Pre-Flight Dependency Checks (all PASS)

```
test -d content/gallery/photos                                              ✓
ls content/gallery/photos/ | wc -l = 18                                     ✓ (Plan 06-01)
grep 'class="page-{{ .Type' baseof.html = 1                                 ✓ (Plan 06-02)
grep '.gallery-grid' style.css = 1                                          ✓ (Plan 06-02)
```

## Verification Gates

```
content/gallery/index.md:
  wc -l                                                                    = 3   ✓
  grep -c 'title: "Gallery"'                                               = 1   ✓
  grep -c '^---$'                                                          = 2   ✓

themes/minimal/layouts/gallery/single.html:
  grep -c '{{ define "main" }}'                                            = 1   ✓
  grep -c 'gallery-grid'                                                   = 1   ✓
  grep -c 'gallery-item'                                                   = 1   ✓
  grep -c 'gallery-img'                                                    = 1   ✓
  grep -c 'Process "fill 600x400 Smart webp q75"'                          = 1   ✓ (GAL-03)
  grep -c 'Process "fit 1600x1600 webp q82"'                               = 1   ✓ (GAL-04)
  grep -c 'aria-label="Open photo'                                         = 1   ✓
  grep -c 'fetchpriority="high"'                                           = 1   ✓
  grep -c 'decoding="async"'                                               = 1   ✓
  grep -c 'alt=""'                                                         = 1   ✓
  grep -c '{{ end }}'                                                      = 6   ✓ (block balance)

Locked OUT (all = 0):
  target="_blank"                                                          = 0   ✓
  srcset                                                                   = 0   ✓
  tabindex                                                                 = 0   ✓
  onclick                                                                  = 0   ✓
```

## Block Balance

6 opening Go-template blocks ↔ 6 `{{ end }}` closers:
1. `{{ define "main" }}` ↔ closing `{{ end }}`
2. `{{ with .Resources.Match "photos/*" }}` ↔ closing `{{ end }}`
3. `{{ range $idx, $photo := . }}` ↔ closing `{{ end }}`
4. `{{ if lt $idx 3 }}eager{{ else }}lazy{{ end }}` (inline ternary, has its own `{{ end }}`)
5. `{{ if eq $idx 0 }}fetchpriority="high"{{ end }}` (inline if, has its own `{{ end }}`)
6. `{{ if ge $idx 3 }}decoding="async"{{ end }}` (inline if, has its own `{{ end }}`)

## Per-Attribute Provenance

| Element | Source decision | Note |
|---------|----------------|------|
| `Process "fill 600x400 Smart webp q75"` | D-08 / GAL-03 / ROADMAP locked verbatim | Smart crop has NO face detection — visual smoke test deferred to Plan 06-04 HUMAN-UAT |
| `Process "fit 1600x1600 webp q82"` | D-07 / GAL-04 / ROADMAP locked verbatim | `fit` never upscales (RESEARCH-verified) |
| `width/height` from `$thumb.Width`/`Height` | UI-SPEC § Performance Contract | CLS=0 guarantee — Hugo provides post-processing dimensions |
| `loading=eager-or-lazy` ternary on `$idx<3` | D-05 | First 3 above-fold |
| `fetchpriority="high"` on `$idx==0` | D-06 | Web.dev LCP guidance: exactly one above-fold high-priority |
| `decoding="async"` on `$idx>=3` | UI-SPEC § Loading | Lazy-only; first 3 decode synchronously |
| `alt=""` | D-18 | Decorative; aria-label on `<a>` carries name |
| `aria-label="Open photo {{ add $idx 1 }} of {{ $total }} at full size"` | UI-SPEC § Copywriting Contract | 1-indexed, no filename leakage |
| `{{ with .Resources.Match "photos/*" }}` guard | CONTEXT § Claude's Discretion | Defensive empty-bundle handling |

## What's Next

`/gallery/` is now structurally complete:
- Leaf bundle index ✓ (this plan)
- 18 photos ✓ (Plan 06-01)
- Type-derived layout ✓ (this plan)
- Body-class hook in baseof.html ✓ (Plan 06-02)
- Gallery CSS rules in style.css ✓ (Plan 06-02)

Plan 06-04 will run `hugo --minify` as the integration smoke test, verify EXIF cleanliness on processed WebPs, check the weight gate (≤ 3 MB), and write HUMAN-UAT.md for items requiring user-side eyeball verification (Smart-crop quality, dark/light theme rendering, mobile responsive collapse, keyboard focus visible, deployed Lighthouse CLS).

## Cross-Phase Outgoing Contract

**To Phase 7 (About Enrichment):**
- Type-derived layout pattern (`layouts/{type}/single.html`) is now a validated codebase pattern. If Phase 7 converts `content/about.md` → `content/about/index.md` (leaf bundle), it can introduce `themes/minimal/layouts/about/single.html` for richer About-specific markup.
- `.Resources.Match` + `image.Process` pipeline is validated and reusable for any inline About photos.
- Body-class hook from Plan 06-02 will automatically emit `class="page-about"` post-conversion, enabling Phase 7's "richer About layout" CSS scoping via `body.page-about` rules.

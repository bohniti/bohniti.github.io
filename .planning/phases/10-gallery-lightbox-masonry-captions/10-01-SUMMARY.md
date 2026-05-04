---
phase: 10-gallery-lightbox-masonry-captions
plan: 01
subsystem: gallery-data-layer
tags:
  - hugo
  - frontmatter
  - toml
  - resources
  - gallery
dependency_graph:
  requires:
    - content/gallery/photos/*.{jpg,JPG,jpeg}
  provides:
    - "content/gallery/index.md TOML frontmatter with 18 [[resources]] blocks"
    - "Params.caption / Params.alt / Params.weight readable via .Resources.Match \"photos/*\""
  affects:
    - .planning/phases/10-gallery-lightbox-masonry-captions/10-02-PLAN.md (template reads these Params)
    - .planning/phases/10-gallery-lightbox-masonry-captions/10-03-PLAN.md (JS lightbox reads same Params)
tech_stack:
  added: []
  patterns:
    - "TOML page-bundle frontmatter with [[resources]] array idiom (D-01)"
    - "Optional caption authored via params.caption omission (D-02 graceful-empty contract)"
    - "Required descriptive alt text for accessibility (D-03)"
    - "Required unique integer weight for deterministic order (D-04)"
    - "Filename-casing byte-match (Pitfall 14)"
key_files:
  created: []
  modified:
    - content/gallery/index.md
decisions:
  - "Switched delimiter from YAML (---) to TOML (+++) — required for [[resources]] array idiom (D-01)"
  - "weight assignment: 10..180 in steps of 10 (alphabetic-by-filename-descending) — leaves room for inserts; author can re-iterate post-Plan-02 build"
  - "Captions intentionally omitted on first pass (D-02) — author iterates after Plan 02 ships the rendered gallery"
  - "All 18 src/name byte-match content/gallery/photos/ ls output (Pitfall 14)"
metrics:
  duration_seconds: 83
  completed_date: 2026-05-04
  tasks_completed: 1
  tasks_total: 1
  files_changed: 1
requirements_addressed:
  - GALLERY-01
  - GALLERY-03
  - GALLERY-04
---

# Phase 10 Plan 01: Gallery Frontmatter (TOML + 18 [[resources]]) Summary

**One-liner:** Converted `content/gallery/index.md` from a 6-line YAML stub to TOML page-bundle frontmatter with 18 explicit `[[resources]]` blocks — every photo carrying byte-matched `src`/`name`, descriptive `alt`, and unique integer `weight`, with `caption` omitted on the initial pass per the graceful-empty contract.

## What Shipped

- **`content/gallery/index.md`** — rewritten from `---` YAML to `+++` TOML
  - Preserved keys: `title = "Gallery"`, `type = "gallery"`, `[build] publishResources = false`
  - Added 18 `[[resources]]` entries, each with:
    - `src = "photos/<exact-case-filename>"` (byte-matched per Pitfall 14)
    - `name = "photos/<exact-case-filename>"`
    - `[resources.params].alt` — descriptive alt text (D-03 REQUIRED)
    - `[resources.params].weight` — unique integer 10..180 in steps of 10 (D-04 REQUIRED)
    - `[resources.params].caption` — omitted entirely (D-02; never `caption = ""`)

## Weight Assignment Scheme

Initial pass uses 10..180 in steps of 10, ordered alphabetic-by-filename-descending. This is **documentary, not curatorial** — the author re-iterates ordering after Plan 02 ships the rendered gallery. Step-of-10 spacing leaves room to insert new photos without renumbering everything.

| Weight | Filename                                            |
| -----: | --------------------------------------------------- |
|     10 | IMG_8113.jpg                                        |
|     20 | IMG_7828.jpeg                                       |
|     30 | IMG_6546.jpeg                                       |
|     40 | IMG_5685_Original.JPG                               |
|     50 | IMG_2009.jpeg                                       |
|     60 | IMG_1646.jpeg                                       |
|     70 | IMG_1499.jpeg                                       |
|     80 | IMG_1299.JPG                                        |
|     90 | IMG_1288.JPG                                        |
|    100 | IMG_0256.jpeg                                       |
|    110 | DSC09784.JPG                                        |
|    120 | DSC09782.JPG                                        |
|    130 | 20210710_132418.jpg                                 |
|    140 | 5dc795b8-3921-45b8-a651-5b434e405259.jpg            |
|    150 | 60130366-e95c-48a9-b8cd-aa38090c02c2.jpg            |
|    160 | 7eb72991-8aac-44e7-92f7-f71968357ceb.jpg            |
|    170 | 98562fcd-4559-4d91-8020-48ac5dbc9610.jpg            |
|    180 | f2e6acbb-7e38-4235-aade-b23a22622596.jpg            |

## Captions

**0 captions authored on this pass.** D-02 explicitly contracts captions as optional, with the downstream template (Plan 02) using a `with $photo.Params.caption` guard for graceful-empty rendering. The author will add `caption = "..."` lines in a follow-up commit after the gallery actually renders — easier to write a 1–2-sentence story when looking at the photo in context than when staring at a UUID-named filename.

## Decisions Implemented

- **D-01** — Per-photo `[[resources]]` blocks (NOT a YAML data file, NOT sidecar `.md` files)
- **D-02** — Caption optionality at the data layer (omitted entirely, never empty-stringed)
- **D-03** — `alt` is REQUIRED on every entry
- **D-04** — `weight` is REQUIRED on every entry; values are unique integers
- **Pitfall 14** — `src`/`name` byte-match the filename casing exactly (no lowercase, no extension normalization). 18 / 18 filenames diff-clean against `ls content/gallery/photos/`.

## Requirements Addressed

| Requirement | Description                                  | Status                                                                                           |
| ----------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| GALLERY-01  | Single-file authoring path                   | Complete — one frontmatter file is the source of truth for all 18 photos                         |
| GALLERY-03  | Deterministic order across deploys           | Complete — 18 unique `weight` integers establish a single canonical order                        |
| GALLERY-04  | Caption optionality                          | Complete at the data layer — `caption` omitted entirely; template guard arrives in Plan 02       |

## Verification

All 6 plan-level grep gates pass:

| Gate | Check                                                              | Result            |
| ---- | ------------------------------------------------------------------ | ----------------- |
| 1    | First line is `+++`                                                | OK                |
| 2    | Exactly 18 `[[resources]]` blocks (excluding comment lines)        | 18                |
| 3    | Exactly 18 each of `src =`, `name =`, `alt =`, `weight =`          | 18 / 18 / 18 / 18 |
| 4    | `src` filenames diff-match `ls content/gallery/photos/` (Pitfall 14)| no diff           |
| 5    | All 18 `weight` values unique                                      | 18 unique         |
| 6    | `title = "Gallery"`, `type = "gallery"`, `publishResources = false` preserved | OK |

**Bonus check:** No `caption = ""` empty-string entries (D-02 enforced).

**Bonus build verification:** `hugo --minify` ran clean — 16 pages, 13 non-page files, 11 static files, 46 processed images, build time 15710 ms. Only pre-existing `languageCode` deprecation warnings (unrelated to this plan).

## Deviations from Plan

None — plan executed exactly as written. The action block specified the exact TOML payload and all gates passed on the first write.

## Out-of-Scope / Deferred

- **Caption text authoring** — deferred to a post-Plan-02 follow-up commit; the author writes captions when viewing rendered photos in context.
- **Hugo template wiring** — Plan 02 reads `Params.caption` / `Params.alt` / `Params.weight` from `.Resources.Match "photos/*"`.
- **JS lightbox** — Plan 03 reads the same Params on click events.
- **Pre-existing `languageCode` deprecation warnings** — surfaced by `hugo --minify` but originate in `hugo.toml`, not this plan's files. Logged for a future config cleanup; not in scope here.

## Threat Flags

None — no new security-relevant surface introduced beyond the already-modeled threats in the plan's threat register (T-10-01..T-10-05). The `diff`-against-`ls` Pitfall 14 mitigation (T-10-01) and the unique-weight gate (T-10-03) both passed.

## Self-Check: PASSED

**Files claimed to exist:**
- `content/gallery/index.md` — FOUND (140 insertions, 6 deletions; first line `+++`, 18 `[[resources]]` blocks verified)

**Commits claimed to exist:**
- `edf0967` `feat(10-01): rewrite content/gallery/index.md as TOML with 18 [[resources]] blocks` — FOUND in worktree branch

**Build sanity:**
- `hugo --minify` succeeded; no Resources.Match fatal errors

## Next Plan

**Plan 02** (`10-02-PLAN.md`) — Template + CSS + EXIF CI. Adds `themes/minimal/layouts/gallery/list.html` (and any partials), CSS for the masonry grid, and CI checks for EXIF stripping. Reads `Params.caption` / `Params.alt` / `Params.weight` from the blocks authored here.

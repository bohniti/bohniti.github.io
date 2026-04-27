---
phase: 01-article-refinement
plan: 01
subsystem: theme/shortcodes
tags:
  - hugo
  - shortcode
  - mermaid
  - flexoki
dependency_graph:
  requires: []
  provides:
    - "Hugo `mermaid` shortcode invokable as `{{< mermaid >}}...{{< /mermaid >}}` from any Markdown file"
    - "Per-page once-only Mermaid CDN load via `.Page.Scratch` guard (`mermaidLoaded` key)"
    - "Flexoki-themed Mermaid rendering (background, primaryColor, primaryTextColor, primaryBorderColor, lineColor, secondaryColor, tertiaryColor + fontFamily)"
  affects:
    - "Plan 01-02 (article rewrite) — unblocked; can now invoke `{{< mermaid >}}` instead of duplicating raw `<script>` boilerplate"
    - "Future Mermaid usage anywhere on the site — one-liner shortcode"
tech_stack:
  added:
    - "Hugo shortcodes pattern (first in this repo)"
  patterns:
    - "`.Page.Scratch` once-only-load guard for per-page-conditional asset loading"
    - "`.Inner | safeHTML` to pass Markdown-block content through to a JS runtime parser"
key_files:
  created:
    - "themes/minimal/layouts/shortcodes/mermaid.html"
  modified: []
decisions:
  - id: D-04
    text: "Embed Flexoki palette hex literals directly in `themeVariables` (Mermaid JS does not read CSS custom properties at runtime)"
  - id: D-08
    text: "Encapsulate Mermaid via a Hugo shortcode (first in repo) instead of duplicating inline `<script>` blocks"
  - id: D-09
    text: "Load the Mermaid CDN script only on pages that actually use the shortcode (per-page Scratch guard)"
  - id: D-10
    text: "Use `cdn.jsdelivr.net/npm/mermaid` unpinned, matching the existing intervals-copilot inline pattern and Leaflet/Plotly precedent"
metrics:
  duration_seconds: 36
  duration_human: "<1 minute"
  tasks_completed: 1
  files_changed: 1
  lines_added: 23
  lines_removed: 0
  commits: 1
  completed_date: "2026-04-27"
---

# Phase 01 Plan 01: Mermaid Shortcode Summary

A Hugo `mermaid` shortcode now exists at `themes/minimal/layouts/shortcodes/mermaid.html`, wrapping `.Inner` in `<div class="mermaid">`, loading the Mermaid CDN script once per page via a `.Page.Scratch` guard, and initializing Mermaid with the seven Flexoki theme hex literals plus the site body fontFamily.

## What Was Built

A single-file Hugo shortcode (23 lines) that encapsulates the inline Mermaid pattern previously duplicated in `content/blog/2026-03-15-intervals-copilot/index.md`. Callers now invoke `{{< mermaid >}}graph LR\n  A-->B\n{{< /mermaid >}}` from Markdown and the shortcode emits both the wrapped `<div class="mermaid">` element and (once per page) the Mermaid CDN `<script>` plus a `mermaid.initialize` call with `theme: 'base'` and a `themeVariables` object mapping Mermaid's palette to Flexoki.

This is the first shortcode in this repo — the directory `themes/minimal/layouts/shortcodes/` was created as part of this task.

## How Callers Use It

```markdown
{{< mermaid >}}
graph LR
  A[Source] --> B[Node 1] --> C[Node 2]
{{< /mermaid >}}
```

Multiple `{{< mermaid >}}` blocks on the same page emit only one `<script>` tag thanks to the `.Page.Scratch.Get "mermaidLoaded"` guard.

## Theme Variables Embedded

| Mermaid key          | Flexoki hex | Maps to (`style.css`) |
|----------------------|-------------|------------------------|
| `background`         | `#FFFCF0`   | `--bg`                 |
| `primaryColor`       | `#F2F0E5`   | `--bg-secondary`       |
| `primaryTextColor`   | `#100F0F`   | `--text`               |
| `primaryBorderColor` | `#E6E4D9`   | `--border`             |
| `lineColor`          | `#6F6E69`   | `--text-secondary`     |
| `secondaryColor`     | `#F2F0E5`   | `--bg-secondary`       |
| `tertiaryColor`      | `#FFFCF0`   | `--bg`                 |
| `fontFamily`         | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` | `body` font in `style.css` line 27 |

Hex values are literal strings (not `var(--bg)`) because Mermaid's JS does not resolve CSS custom properties at runtime.

## Decisions Implemented

- **D-04**: Flexoki palette embedded as hex literals — verified consistent with `themes/minimal/static/css/style.css` `:root` block (lines 4-18).
- **D-08**: Hugo shortcode pattern — first shortcode in the repo; sets the precedent for future encapsulation of inline JS embeds (Plotly, Leaflet) if/when refactored.
- **D-09**: Per-page once-only load via `.Page.Scratch` guard with key `mermaidLoaded` — pages without `{{< mermaid >}}` do not load the Mermaid CDN script at all.
- **D-10**: CDN URL `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js` (unpinned), matching the existing intervals-copilot post and the project's general convention of unpinned CDN loads (Leaflet, Plotly).

## Verification Performed

- `test -f themes/minimal/layouts/shortcodes/mermaid.html` — passed
- `grep` for `mermaid.initialize`, `.Inner | safeHTML`, `Scratch`, `cdn.jsdelivr.net/npm/mermaid`, `theme: 'base'`, `startOnLoad: true`, `fontFamily` — all passed
- All seven `themeVariables` keys present (`background`, `primaryColor`, `primaryTextColor`, `primaryBorderColor`, `lineColor`, `secondaryColor`, `tertiaryColor`)
- All five required Flexoki hex literals present (`#FFFCF0`, `#F2F0E5`, `#100F0F`, `#E6E4D9`, `#6F6E69`); palette hex hits = 7
- File line count = 23 (within `[20, 35]`)
- No `<noscript>` block in shortcode (per PATTERNS.md guidance — callers add their own per-instance fallback if desired)
- No whitespace-trim markers (`{{-`, `-}}`)
- Two-space indent and bare `{{ }}` directives match `themes/minimal/layouts/_default/baseof.html` style

End-to-end Hugo build verification is deferred to Plan 01-02 (article rewrite), which will actually invoke the shortcode and trigger a full Hugo build.

## Deviations from Plan

None — plan executed exactly as written. The plan provided literal verbatim file content in its `<action>` block; the file was written byte-for-byte from that spec.

## Threat Model Compliance

All threats in the plan's `<threat_model>` were dispositioned `accept` or `n/a`. No `mitigate` actions were required, so no Rule 2 functionality was added. Specifically:

- T-01-01 (CDN supply chain): accepted — no SRI hash added, consistent with project precedent.
- T-01-03 (XSS via `safeHTML`): accepted — only the site owner authors `.Inner` content; `unsafe = true` is already site-wide.

## Known Stubs

None.

## Threat Flags

None — the shortcode introduces only the Mermaid CDN load and `.Inner | safeHTML` rendering, both of which are explicitly catalogued in the plan's `<threat_model>` (T-01-01, T-01-03). No new untracked surface.

## Commits

| Task | Description                          | Commit  |
|------|--------------------------------------|---------|
| 1    | Add mermaid shortcode (Flexoki theme)| 2c5bc41 |

## Self-Check: PASSED

- FOUND: themes/minimal/layouts/shortcodes/mermaid.html
- FOUND: 2c5bc41 (in `git log --oneline`)

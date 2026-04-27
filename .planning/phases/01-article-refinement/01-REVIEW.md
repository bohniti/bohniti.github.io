---
phase: 01-article-refinement
reviewed: 2026-04-27T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - themes/minimal/layouts/shortcodes/mermaid.html
  - content/blog/2026-03-27-video-editing-journey/index.md
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: clean
---

# Phase 01: Code Review Report

**Reviewed:** 2026-04-27T00:00:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** clean

## Summary

Reviewed the two files modified in Phase 01 (`01-article-refinement`):

1. `themes/minimal/layouts/shortcodes/mermaid.html` — new Hugo shortcode (23 lines, the first shortcode in the repo). Wraps `.Inner` in `<div class="mermaid">`, conditionally loads the Mermaid CDN once per page via `.Page.Scratch`, and initializes Mermaid with seven Flexoki theme variables.
2. `content/blog/2026-03-27-video-editing-journey/index.md` — article rewrite of Step 5 (Color Grading). Replaces an ASCII tree fenced block, a shared parameter table, and a screenshot with a `{{< mermaid >}}` invocation plus five per-node H4 subsections.

Both files match the executed plans (`01-01-PLAN.md` and `01-02-PLAN.md`) precisely. All decisions D-01 through D-14 land where they were specified; the en-dash convention is consistent with existing tables in the same post; image references resolve to existing files; the Mermaid shortcode contract (`graph LR`, double-quoted node labels, `<br/>` separators) matches the existing in-repo Mermaid usage in `content/blog/2026-03-15-intervals-copilot/index.md`.

No critical or warning-level issues found. Two info-level observations are recorded for future hardening, both of which are explicitly accepted in the phase threat model (T-01-01, T-01-03) and consistent with established site-wide patterns (Leaflet, Plotly, Instagram embed all load unpinned from CDNs with `unsafe = true`). They are noted here only so the project has a single place to revisit if the security posture ever changes.

Concrete checks performed:

- Shortcode template style matches `themes/minimal/layouts/_default/baseof.html` (two-space indent, no whitespace-trim markers, no comment headers).
- All seven Flexoki hex literals (`#FFFCF0`, `#F2F0E5`, `#100F0F`, `#E6E4D9`, `#6F6E69`) match the `:root` block in `themes/minimal/static/css/style.css`.
- `Scratch.Get`/`Scratch.Set` guard correctly emits the CDN script and `mermaid.initialize` only on the first invocation per page.
- The article's frontmatter (`title`, `date`, `draft`, `summary`) follows the post-structure convention documented in `CLAUDE.md`.
- All `images/...` references in the article resolve to existing files in the page bundle (`Chaotic timeline.png`, `Clip catalog spreadsheet.png`, `Insta360 + DaVinci side-by-side.png`, `before-color.png`, `after-color.png`). The `Node tree.png` reference and asset are gone, as required by D-13.
- En-dash (U+2013) is used consistently in numeric ranges (`0.98–1.02`, `1.00–1.10`, `0.5–0.7`, `45–55`, `1.00–1.15`); em-dash (U+2014) is used in prose, matching the rest of the post.
- The `Lift` row correctly preserves the hyphen-minus in `-0.02 to 0.00` (negative number, not a range separator).
- Single `{{< mermaid >}}` invocation (verified via grep) — the once-per-page guard is therefore exercised without a multi-instance edge case.
- No `<noscript>` block is added inside the shortcode (per PATTERNS.md) and none is added inline in the article. This is consistent with the threat model (T-01-09 accept: malformed Mermaid produces a visible inline error, not a site outage).

## Info

### IN-01: Unpinned Mermaid CDN URL (no version pin, no SRI)

**File:** `themes/minimal/layouts/shortcodes/mermaid.html:6`
**Issue:** The script tag loads `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js` without a version pin and without a Subresource Integrity (`integrity=`) attribute. Any future jsdelivr release of `mermaid` will be picked up automatically, and a compromised CDN response would execute with full DOM privileges on every page that uses the shortcode.

This is consistent with the existing site-wide pattern (Leaflet, Plotly, Instagram embed all load unpinned) and is explicitly accepted in the phase threat model (T-01-01 in `01-01-PLAN.md`) on the grounds that this is a static personal blog with no auth and no PII, and pinning a hash on an unpinned URL is not workable. Recording here so that if/when the project decides to pin third-party JS, this load gets pinned at the same time as the Leaflet/Plotly loads.

**Fix:** Optional future hardening — pin to a specific Mermaid version and add an SRI hash in one pass across all CDN loads (Mermaid + Leaflet + Plotly):

```html
<script
  src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"
  integrity="sha384-..."
  crossorigin="anonymous"></script>
```

No action required for this phase.

### IN-02: `safeHTML` cast on `.Inner` bypasses Hugo's HTML escaping

**File:** `themes/minimal/layouts/shortcodes/mermaid.html:2`
**Issue:** `{{ .Inner | safeHTML }}` passes the inner shortcode content through unchanged so Mermaid's runtime parser can read raw `<br/>` tags inside node labels. If non-trusted content ever ended up authored as `.Inner` (e.g., user comments, syndicated drafts), this would be an XSS sink.

This is explicitly accepted in the phase threat model (T-01-03 in `01-01-PLAN.md`): the only authors of `.Inner` are the site owner, all Markdown is committed to git, and the site already enables `markup.goldmark.renderer.unsafe = true` site-wide, so this shortcode does not expand the attack surface. Recording so the trust assumption stays visible if the site ever accepts external content.

**Fix:** None for current scope. If `.Inner` ever needs to accept untrusted input, swap to `htmlEscape` and use a structured Hugo-side parser to emit only the Mermaid `<br/>` tag explicitly.

---

_Reviewed: 2026-04-27T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

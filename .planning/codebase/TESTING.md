# Testing Patterns

> Last updated: 2026-03-27

## Overview

**This project has no automated tests.** There is no test framework, no test files, no test configuration, and no test step in the CI/CD pipeline.

This is consistent with the project's nature: a personal Hugo static blog with minimal custom code. The "code" consists of Hugo HTML templates, a single CSS file, inline JavaScript in markdown posts, and a few standalone Python utility scripts.

## Test Framework

**Runner:** None

**Assertion Library:** None

**Config:** None

## Test File Organization

No test files exist anywhere in the repository. Verified by searching for `*.test.*`, `*.spec.*`, `*_test.*`, and common test config files (`jest.config.*`, `vitest.config.*`, `pytest.ini`, `setup.cfg`, `.rspec`).

## CI/CD Pipeline

The GitHub Actions workflow at `.github/workflows/deploy.yml` has two jobs:

1. **build** - Installs Hugo, checks out code, builds with `hugo --minify`, uploads artifact
2. **deploy** - Deploys to GitHub Pages

There is no test, lint, or validation step. The pipeline deploys directly on every push to `main`.

## What Could Be Tested

If testing were to be added, these are the areas with testable logic:

### Python Scripts

**Files:**
- `scripts/transform_climbing_csv.py` - CSV transformation logic (grade mapping, style mapping, date parsing)
- `convert_to_french_fixed.py` (root, untracked) - grade conversion
- `fix_data_properly.py` (root, untracked) - data cleanup

These scripts have pure functions (`transform_row`) that accept a dictionary and return a dictionary, making them straightforward to unit test with `pytest`.

**Potential test approach:**
```python
# tests/test_transform_climbing_csv.py
from scripts.transform_climbing_csv import transform_row, STYLE_MAP

def test_transform_row_basic():
    row = {"date": "2024-06-15T10:00:00", "style": "rp", "location": "Frankenjura", ...}
    result = transform_row(row)
    assert result["tick_type"] == "redpoint"
    assert result["date"] == "2024-06-15"
```

### Hugo Build Validation

The Hugo build itself (`hugo --minify`) acts as an implicit validation step. If templates have syntax errors or content is malformed, the build fails. This is already part of the CI pipeline, though it is not framed as a "test."

### Inline JavaScript

The climbing routes post (`content/blog/2026-03-05-climbing-routes/index.md`) contains approximately 430 lines of JavaScript with functions like `gradeToNumber()`, `parseCSV()`, `numberToFrenchGrade()`, and `getGradeColor()`. These are pure functions that could be extracted and tested, but they currently live inline in a markdown file with no module system.

### Link Validation

Blog posts contain external links (YouTube, GitHub, Instagram). These could be validated with a link checker, but none is configured.

## Coverage

**Requirements:** None enforced

**Current coverage:** 0% (no tests exist)

## Recommendations

Given the project's scope (personal blog, single maintainer), the highest-value testing additions would be:

1. **Hugo build smoke test** - Already implicit in CI; could be made explicit with a named step
2. **Python script unit tests** - Low effort, high value for the CSV transformation logic in `scripts/transform_climbing_csv.py`
3. **HTML validation** - Run an HTML validator on the built `public/` directory as a CI step

---

*Testing analysis: 2026-03-27*

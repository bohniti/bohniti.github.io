#!/usr/bin/env python3
"""Transform Vertical Life dataset.csv into Climbers Journal import format."""

import csv
from collections import Counter
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "static" / "files" / "dataset.csv"
OUTPUT = INPUT.parent / "climbing_journal_import.csv"

STYLE_MAP = {
    "rp": "redpoint",
    "os": "onsight",
    "fl": "flash",
    "f": "flash",
    "go": "attempt",
    "tr": "attempt",
    "redpoint": "redpoint",
    "onsight": "onsight",
    "flash": "flash",
    "fell/hung": "attempt",
}

OUTPUT_COLUMNS = [
    "date", "tick_type", "crag_name", "route_name", "grade",
    "area_name", "tries", "rating", "notes", "partner", "style",
]


def transform_row(row):
    date_raw = row.get("date", "")
    date = date_raw[:10] if len(date_raw) >= 10 else date_raw

    style_code = row.get("style", "").strip().lower()
    tick_type = STYLE_MAP.get(style_code, "attempt")

    stars = row.get("stars", "").strip()
    rating = "" if stars in ("", "0") else stars

    return {
        "date": date,
        "tick_type": tick_type,
        "crag_name": row.get("location", ""),
        "route_name": row.get("route_name", ""),
        "grade": row.get("grade_original", ""),
        "area_name": row.get("sector", ""),
        "tries": row.get("tries", ""),
        "rating": rating,
        "notes": row.get("comment", ""),
        "partner": "",
        "style": "sport",
    }


def main():
    warnings = []

    with open(INPUT, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    transformed = []
    tick_counts = Counter()

    for i, row in enumerate(rows, start=2):
        out = transform_row(row)
        tick_counts[out["tick_type"]] += 1

        if not out["grade"]:
            warnings.append(f"Row {i}: empty grade for '{out['route_name']}'")

        style_code = row.get("style", "").strip().lower()
        if style_code and style_code not in STYLE_MAP:
            warnings.append(f"Row {i}: unknown style '{style_code}' → attempt")

        transformed.append(out)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(transformed)

    print(f"Rows: {len(transformed)}")
    print(f"Tick types: {dict(tick_counts)}")
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
    print(f"\nOutput: {OUTPUT}")


if __name__ == "__main__":
    main()

"""Functions for inspecting CSV data quality."""

import csv
from collections import Counter
from pathlib import Path


def analyze_csv(file_path: str | Path) -> dict[str, object]:
    """Return a basic data-quality summary for a CSV file."""
    path = Path(file_path)

    with path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = reader.fieldnames or []
        rows = list(reader)

    missing_values = {
        column: sum(
            (row.get(column, "") or "").strip() == ""
            for row in rows
        )
        for column in columns
    }

    column_profiles = {}

    for column in columns:
        values = [
            (row.get(column, "") or "").strip()
            for row in rows
        ]
        non_empty_values = [
            value
            for value in values
            if value != ""
        ]

        column_profiles[column] = {
            "non_empty_values": len(non_empty_values),
            "unique_non_empty_values": len(set(non_empty_values)),
        }

    row_keys = [
        tuple(row.get(column, "") for column in columns)
        for row in rows
    ]
    duplicate_rows = sum(
        count - 1
        for count in Counter(row_keys).values()
        if count > 1
    )

    invalid_ages = 0

    for row in rows:
        age_text = (row.get("age", "") or "").strip()

        if age_text == "":
            continue

        try:
            age = int(age_text)
        except ValueError:
            invalid_ages += 1
            continue

        if age < 0 or age > 120:
            invalid_ages += 1

    return {
        "total_rows": len(rows),
        "columns": columns,
        "missing_values": missing_values,
        "column_profiles": column_profiles,
        "duplicate_rows": duplicate_rows,
        "invalid_ages": invalid_ages,
    }
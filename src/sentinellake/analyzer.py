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
        column: sum(row.get(column, "") == "" for row in rows)
        for column in columns
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

    return {
        "total_rows": len(rows),
        "columns": columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
    }
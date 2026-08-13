"""Functions for inspecting CSV data quality."""

import csv
from collections import Counter
from pathlib import Path


def is_valid_email(email_text: str) -> bool:
    """Return whether text has SentinelLake's basic email format."""
    if email_text.count("@") != 1:
        return False

    local_part, domain = email_text.split("@")

    return (
        local_part != ""
        and domain != ""
        and "." in domain
        and not domain.startswith(".")
        and not domain.endswith(".")
    )


def analyze_csv(
    file_path: str | Path,
    unique_columns: list[str] | None = None,
) -> dict[str, object]:
    """Return a basic data-quality summary for a CSV file."""
    path = Path(file_path)

    with path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = reader.fieldnames or []
        rows = list(reader)

    if not columns:
        raise ValueError("CSV file must contain a header row.")

    selected_unique_columns = []

    for column in unique_columns or []:
        if column not in columns:
            raise ValueError(f"Requested unique column not found: {column}")

        if column not in selected_unique_columns:
            selected_unique_columns.append(column)

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

    invalid_emails = 0

    for row in rows:
        email_text = (row.get("email", "") or "").strip()

        if email_text == "":
            continue

        if not is_valid_email(email_text):
            invalid_emails += 1

    unique_column_checks = {}

    for column in selected_unique_columns:
        value_counts = Counter(
            (row.get(column, "") or "").strip()
            for row in rows
            if (row.get(column, "") or "").strip() != ""
        )
        duplicate_values = {
            value: count
            for value, count in value_counts.items()
            if count > 1
        }

        unique_column_checks[column] = {
            "duplicate_values": duplicate_values,
            "duplicate_value_count": len(duplicate_values),
            "duplicate_value_occurrences": sum(
                count - 1
                for count in duplicate_values.values()
            ),
        }

    return {
        "total_rows": len(rows),
        "columns": columns,
        "missing_values": missing_values,
        "column_profiles": column_profiles,
        "duplicate_rows": duplicate_rows,
        "invalid_ages": invalid_ages,
        "invalid_emails": invalid_emails,
        "unique_column_checks": unique_column_checks,
    }
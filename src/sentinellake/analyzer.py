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
    required_columns: list[str] | None = None,
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

    selected_required_columns = []

    for column in required_columns or []:
        if column not in columns:
            raise ValueError(f"Requested required column not found: {column}")

        if column not in selected_required_columns:
            selected_required_columns.append(column)

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

    invalid_age_details = []

    for row_number, row in enumerate(rows, start=2):
        age_text = (row.get("age", "") or "").strip()

        if age_text == "":
            continue

        try:
            age = int(age_text)
        except ValueError:
            invalid_age_details.append(
                {
                    "row_number": row_number,
                    "value": age_text,
                }
            )
            continue

        if age < 0 or age > 120:
            invalid_age_details.append(
                {
                    "row_number": row_number,
                    "value": age_text,
                }
            )

    invalid_email_details = []

    for row_number, row in enumerate(rows, start=2):
        email_text = (row.get("email", "") or "").strip()

        if email_text == "":
            continue

        if not is_valid_email(email_text):
            invalid_email_details.append(
                {
                    "row_number": row_number,
                    "value": email_text,
                }
            )

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

    required_column_checks = {}

    for column in selected_required_columns:
        missing_row_numbers = [
            row_number
            for row_number, row in enumerate(rows, start=2)
            if (row.get(column, "") or "").strip() == ""
        ]

        required_column_checks[column] = {
            "missing_value_count": len(missing_row_numbers),
            "missing_row_numbers": missing_row_numbers,
        }

    issue_summary = {
        "duplicate_row_count": duplicate_rows,
        "invalid_age_count": len(invalid_age_details),
        "invalid_email_count": len(invalid_email_details),
        "selected_duplicate_value_occurrences": sum(
            check["duplicate_value_occurrences"]
            for check in unique_column_checks.values()
        ),
        "missing_required_value_count": sum(
            check["missing_value_count"]
            for check in required_column_checks.values()
        ),
    }
    issue_summary["total_rule_violation_count"] = sum(
        issue_summary.values()
    )

    return {
        "total_rows": len(rows),
        "columns": columns,
        "missing_values": missing_values,
        "column_profiles": column_profiles,
        "duplicate_rows": duplicate_rows,
        "invalid_ages": len(invalid_age_details),
        "invalid_age_details": invalid_age_details,
        "invalid_emails": len(invalid_email_details),
        "invalid_email_details": invalid_email_details,
        "unique_column_checks": unique_column_checks,
        "required_column_checks": required_column_checks,
        "issue_summary": issue_summary,
    }
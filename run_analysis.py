"""Run a SentinelLake CSV data-quality analysis."""

import argparse
from pathlib import Path

from src.sentinellake.analyzer import analyze_csv


def get_csv_path() -> Path:
    """Read the CSV file path supplied by the user."""
    parser = argparse.ArgumentParser(
        description="Create a basic data-quality report for a CSV file."
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the CSV file to analyze.",
    )
    args = parser.parse_args()
    return args.csv_file


def main() -> int:
    """Run the analysis and return a success or error code."""
    csv_path = get_csv_path()

    try:
        report = analyze_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_path}")
        return 1
    except IsADirectoryError:
        print(f"Error: expected a file, but received a folder: {csv_path}")
        return 1

    print("SentinelLake Data Quality Report")
    print("-" * 34)
    print(f"File: {csv_path}")
    print(f"Total rows: {report['total_rows']}")
    print(f"Columns: {', '.join(report['columns'])}")
    print(f"Duplicate rows: {report['duplicate_rows']}")
    print(f"Invalid ages: {report['invalid_ages']}")
    print("Missing values:")

    for column, count in report["missing_values"].items():
        print(f"  - {column}: {count}")

    print("Column profiles:")

    for column, profile in report["column_profiles"].items():
        print(
            f"  - {column}: "
            f"{profile['non_empty_values']} non-empty, "
            f"{profile['unique_non_empty_values']} unique"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
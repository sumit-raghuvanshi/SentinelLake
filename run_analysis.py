"""Run a SentinelLake CSV data-quality analysis."""

import argparse
from pathlib import Path

from src.sentinellake.analyzer import analyze_csv
from src.sentinellake.reporting import write_json_report


def get_arguments() -> argparse.Namespace:
    """Read command-line arguments supplied by the user."""
    parser = argparse.ArgumentParser(
        description="Create a basic data-quality report for a CSV file."
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the CSV file to analyze.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path where a JSON report will be saved.",
    )
    parser.add_argument(
        "--unique-column",
        action="append",
        default=[],
        metavar="COLUMN",
        help="Check that non-empty values in this column are unique. "
        "Use this option again for each additional column.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the analysis and return a success or error code."""
    args = get_arguments()

    try:
        report = analyze_csv(
            args.csv_file,
            unique_columns=args.unique_column,
        )
    except FileNotFoundError:
        print(f"Error: CSV file not found: {args.csv_file}")
        return 1
    except IsADirectoryError:
        print(f"Error: expected a file, but received a folder: {args.csv_file}")
        return 1
    except ValueError as error:
        print(f"Error: invalid CSV file: {error}")
        return 1

    print("SentinelLake Data Quality Report")
    print("-" * 34)
    print(f"File: {args.csv_file}")
    print(f"Total rows: {report['total_rows']}")
    print(f"Columns: {', '.join(report['columns'])}")
    print(f"Duplicate rows: {report['duplicate_rows']}")
    print(f"Invalid ages: {report['invalid_ages']}")
    print(f"Invalid emails: {report['invalid_emails']}")

    if report["invalid_age_details"]:
        print("Invalid age details:")

        for issue in report["invalid_age_details"]:
            print(f"  - Row {issue['row_number']}: {issue['value']}")

    if report["invalid_email_details"]:
        print("Invalid email details:")

        for issue in report["invalid_email_details"]:
            print(f"  - Row {issue['row_number']}: {issue['value']}")

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

    if report["unique_column_checks"]:
        print("Unique column checks:")

        for column, check in report["unique_column_checks"].items():
            print(
                f"  - {column}: "
                f"{check['duplicate_value_count']} repeated value(s), "
                f"{check['duplicate_value_occurrences']} extra occurrence(s)"
            )

            for value, count in check["duplicate_values"].items():
                print(f"    - {value}: {count} rows")

    if args.output is not None:
        saved_path = write_json_report(report, args.output)
        print(f"JSON report saved: {saved_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Tests for SentinelLake CSV analysis."""

import unittest
from pathlib import Path

from src.sentinellake.analyzer import analyze_csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV = PROJECT_ROOT / "data" / "sample_customers.csv"
INVALID_AGES_CSV = PROJECT_ROOT / "data" / "invalid_ages.csv"
INVALID_EMAILS_CSV = PROJECT_ROOT / "data" / "invalid_emails.csv"
DUPLICATE_CUSTOMER_IDS_CSV = (
    PROJECT_ROOT / "data" / "duplicate_customer_ids.csv"
)
EMPTY_CSV = PROJECT_ROOT / "data" / "empty.csv"


class AnalyzeCsvTests(unittest.TestCase):
    def test_sample_csv_report(self) -> None:
        report = analyze_csv(SAMPLE_CSV)

        self.assertEqual(report["total_rows"], 5)
        self.assertEqual(report["duplicate_rows"], 1)
        self.assertEqual(report["invalid_ages"], 0)
        self.assertEqual(report["invalid_age_details"], [])
        self.assertEqual(report["invalid_emails"], 0)
        self.assertEqual(report["invalid_email_details"], [])
        self.assertEqual(
            report["missing_values"],
            {
                "customer_id": 0,
                "name": 0,
                "email": 2,
                "age": 1,
                "city": 1,
            },
        )

    def test_invalid_ages_are_counted(self) -> None:
        report = analyze_csv(INVALID_AGES_CSV)

        self.assertEqual(report["total_rows"], 4)
        self.assertEqual(report["invalid_ages"], 3)
        self.assertEqual(
            report["invalid_age_details"],
            [
                {"row_number": 2, "value": "unknown"},
                {"row_number": 3, "value": "-3"},
                {"row_number": 4, "value": "151"},
            ],
        )

    def test_invalid_emails_are_counted(self) -> None:
        report = analyze_csv(INVALID_EMAILS_CSV)

        self.assertEqual(report["total_rows"], 5)
        self.assertEqual(report["invalid_emails"], 3)
        self.assertEqual(report["missing_values"]["email"], 1)
        self.assertEqual(
            report["invalid_email_details"],
            [
                {"row_number": 2, "value": "aditi.example.com"},
                {"row_number": 3, "value": "vikram@"},
                {"row_number": 4, "value": "@example.com"},
            ],
        )

    def test_duplicate_values_are_found_in_selected_column(self) -> None:
        report = analyze_csv(
            DUPLICATE_CUSTOMER_IDS_CSV,
            unique_columns=["customer_id"],
        )

        self.assertEqual(report["duplicate_rows"], 0)
        self.assertEqual(
            report["unique_column_checks"]["customer_id"],
            {
                "duplicate_values": {"30": 2},
                "duplicate_value_count": 1,
                "duplicate_value_occurrences": 1,
            },
        )

    def test_unknown_unique_column_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Requested unique column not found: account_id",
        ):
            analyze_csv(SAMPLE_CSV, unique_columns=["account_id"])

    def test_column_profiles_are_calculated(self) -> None:
        report = analyze_csv(SAMPLE_CSV)

        self.assertEqual(
            report["column_profiles"]["customer_id"],
            {
                "non_empty_values": 5,
                "unique_non_empty_values": 4,
            },
        )
        self.assertEqual(
            report["column_profiles"]["email"],
            {
                "non_empty_values": 3,
                "unique_non_empty_values": 3,
            },
        )

    def test_empty_csv_without_a_header_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "CSV file must contain a header row.",
        ):
            analyze_csv(EMPTY_CSV)


if __name__ == "__main__":
    unittest.main()
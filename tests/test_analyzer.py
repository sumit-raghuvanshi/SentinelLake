"""Tests for SentinelLake CSV analysis."""

import unittest
from pathlib import Path

from src.sentinellake.analyzer import analyze_csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV = PROJECT_ROOT / "data" / "sample_customers.csv"


class AnalyzeCsvTests(unittest.TestCase):
    def test_sample_csv_report(self) -> None:
        report = analyze_csv(SAMPLE_CSV)

        self.assertEqual(report["total_rows"], 5)
        self.assertEqual(report["duplicate_rows"], 1)
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


if __name__ == "__main__":
    unittest.main()
"""Tests for SentinelLake JSON report writing."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.sentinellake.reporting import write_json_report


class JsonReportTests(unittest.TestCase):
    def test_json_report_is_saved(self) -> None:
        report = {
            "total_rows": 2,
            "duplicate_rows": 0,
            "invalid_ages": 0,
        }

        with TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "reports" / "report.json"

            saved_path = write_json_report(report, output_path)

            self.assertEqual(saved_path, output_path)
            self.assertTrue(output_path.exists())

            with output_path.open(encoding="utf-8") as report_file:
                saved_report = json.load(report_file)

        self.assertEqual(saved_report, report)


if __name__ == "__main__":
    unittest.main()
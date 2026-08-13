"""Tests for the SentinelLake command-line runner."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from run_analysis import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INVALID_AGES_CSV = PROJECT_ROOT / "data" / "invalid_ages.csv"


class RunnerTests(unittest.TestCase):
    def run_main(self, *arguments: str) -> tuple[int, str]:
        """Run the command-line program with test arguments."""
        output = io.StringIO()

        with patch("sys.argv", ["run_analysis.py", *arguments]):
            with redirect_stdout(output):
                exit_code = main()

        return exit_code, output.getvalue()

    def test_analysis_can_complete_with_detected_issues(self) -> None:
        exit_code, output = self.run_main(str(INVALID_AGES_CSV))

        self.assertEqual(exit_code, 0)
        self.assertIn("Detected rule violations: 3", output)
        self.assertIn("Result: analysis completed.", output)

    def test_fail_on_issues_returns_failure_status(self) -> None:
        exit_code, output = self.run_main(
            str(INVALID_AGES_CSV),
            "--fail-on-issues",
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("Detected rule violations: 3", output)
        self.assertIn(
            "Result: failed because rule violations were detected.",
            output,
        )


if __name__ == "__main__":
    unittest.main()
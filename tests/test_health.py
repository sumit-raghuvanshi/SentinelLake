"""Tests for SentinelLake pipeline health checks."""

import unittest

from src.sentinellake.health import evaluate_pipeline_health


class PipelineHealthTests(unittest.TestCase):
    def test_healthy_pipeline_has_no_incidents(self) -> None:
        metrics = {
            "records_ingested": 9,
            "quarantine_rate": 22.22,
        }

        result = evaluate_pipeline_health(
            metrics,
            minimum_expected_records=8,
            maximum_quarantine_rate=25.0,
        )

        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["incident_count"], 0)

    def test_low_volume_and_high_quarantine_create_incidents(self) -> None:
        metrics = {
            "records_ingested": 3,
            "quarantine_rate": 40.0,
        }

        result = evaluate_pipeline_health(
            metrics,
            minimum_expected_records=8,
            maximum_quarantine_rate=25.0,
        )

        self.assertEqual(result["status"], "incident_detected")
        self.assertEqual(result["incident_count"], 2)
        self.assertEqual(
            result["incidents"][0]["incident_type"],
            "volume_anomaly",
        )
        self.assertEqual(
            result["incidents"][1]["incident_type"],
            "high_quarantine_rate",
        )


if __name__ == "__main__":
    unittest.main()
"""Tests for SentinelLake observability metrics."""

import unittest

from src.sentinellake.observability import calculate_pipeline_metrics


class ObservabilityTests(unittest.TestCase):
    def test_pipeline_metrics_are_calculated(self) -> None:
        summary = {
            "records_ingested": 9,
            "records_accepted_before_deduplication": 7,
            "unique_iocs_accepted": 5,
            "duplicate_ioc_records_consolidated": 2,
            "records_quarantined": 2,
        }

        metrics = calculate_pipeline_metrics(summary)

        self.assertEqual(metrics["data_quality_score"], 77.78)
        self.assertEqual(metrics["quarantine_rate"], 22.22)
        self.assertEqual(metrics["deduplication_rate"], 28.57)
        self.assertEqual(metrics["unique_iocs_accepted"], 5)

    def test_metrics_handle_an_empty_run(self) -> None:
        summary = {
            "records_ingested": 0,
            "records_accepted_before_deduplication": 0,
            "unique_iocs_accepted": 0,
            "duplicate_ioc_records_consolidated": 0,
            "records_quarantined": 0,
        }

        metrics = calculate_pipeline_metrics(summary)

        self.assertEqual(metrics["data_quality_score"], 0.0)
        self.assertEqual(metrics["quarantine_rate"], 0.0)
        self.assertEqual(metrics["deduplication_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
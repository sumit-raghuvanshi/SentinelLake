"""Tests for SentinelLake's local threat-intelligence pipeline."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.sentinellake.pipeline import run_local_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_FEED = PROJECT_ROOT / "data" / "demo_feeds" / "ip_reputation_feed.csv"
DOMAIN_FEED = (
    PROJECT_ROOT / "data" / "demo_feeds" / "domain_watchlist_feed.json"
)
INGESTED_AT = "2026-08-13T10:00:00Z"


class LocalPipelineTests(unittest.TestCase):
    def test_pipeline_processes_and_routes_demo_threat_feeds(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            summary = run_local_pipeline(
                IP_FEED,
                DOMAIN_FEED,
                temporary_directory,
                ingested_at=INGESTED_AT,
            )

            accepted_path = Path(summary["accepted_output_path"])
            quarantine_path = Path(summary["quarantine_output_path"])
            summary_path = Path(summary["summary_output_path"])

            self.assertEqual(summary["source_count"], 2)
            self.assertEqual(summary["records_ingested"], 6)
            self.assertEqual(summary["records_accepted"], 4)
            self.assertEqual(summary["records_quarantined"], 2)
            self.assertTrue(accepted_path.exists())
            self.assertTrue(quarantine_path.exists())
            self.assertTrue(summary_path.exists())

            with accepted_path.open(encoding="utf-8") as accepted_file:
                accepted_records = json.load(accepted_file)

            with quarantine_path.open(encoding="utf-8") as quarantine_file:
                quarantined_records = json.load(quarantine_file)

        self.assertEqual(len(accepted_records), 4)
        self.assertEqual(len(quarantined_records), 2)
        self.assertTrue(
            all(
                record["validation_status"] == "accepted"
                for record in accepted_records
            )
        )
        self.assertEqual(
            {
                record["quarantine_reason"]
                for record in quarantined_records
            },
            {"invalid_ipv4_format", "invalid_domain_format"},
        )


if __name__ == "__main__":
    unittest.main()
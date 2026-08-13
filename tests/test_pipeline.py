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
COMMUNITY_FEED = (
    PROJECT_ROOT / "data" / "demo_feeds" / "community_ioc_feed.json"
)
INGESTED_AT = "2026-08-13T10:00:00Z"


class LocalPipelineTests(unittest.TestCase):
    def test_pipeline_processes_and_deduplicates_demo_feeds(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            summary = run_local_pipeline(
                IP_FEED,
                DOMAIN_FEED,
                COMMUNITY_FEED,
                temporary_directory,
                ingested_at=INGESTED_AT,
            )

            accepted_path = Path(summary["accepted_output_path"])
            quarantine_path = Path(summary["quarantine_output_path"])
            summary_path = Path(summary["summary_output_path"])

            self.assertEqual(summary["source_count"], 3)
            self.assertEqual(summary["records_ingested"], 9)
            self.assertEqual(
                summary["records_accepted_before_deduplication"],
                7,
            )
            self.assertEqual(summary["unique_iocs_accepted"], 5)
            self.assertEqual(
                summary["duplicate_ioc_records_consolidated"],
                2,
            )
            self.assertEqual(summary["records_quarantined"], 2)
            self.assertTrue(accepted_path.exists())
            self.assertTrue(quarantine_path.exists())
            self.assertTrue(summary_path.exists())

            with accepted_path.open(encoding="utf-8") as accepted_file:
                accepted_records = json.load(accepted_file)

            with quarantine_path.open(encoding="utf-8") as quarantine_file:
                quarantined_records = json.load(quarantine_file)

        self.assertEqual(len(accepted_records), 5)
        self.assertEqual(len(quarantined_records), 2)

        duplicate_ip_record = next(
            record
            for record in accepted_records
            if record["ioc_type"] == "ipv4"
            and record["ioc_value"] == "185.220.101.34"
        )
        self.assertEqual(duplicate_ip_record["source_count"], 2)
        self.assertEqual(
            duplicate_ip_record["source_names"],
            ["demo_ip_feed", "demo_community_feed"],
        )


if __name__ == "__main__":
    unittest.main()
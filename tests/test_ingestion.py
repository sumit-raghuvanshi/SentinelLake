"""Tests for SentinelLake threat-feed ingestion."""

import unittest
from pathlib import Path

from src.sentinellake.ingestion import load_csv_feed, load_json_feed


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_FEED = PROJECT_ROOT / "data" / "demo_feeds" / "ip_reputation_feed.csv"
DOMAIN_FEED = (
    PROJECT_ROOT / "data" / "demo_feeds" / "domain_watchlist_feed.json"
)


class ThreatFeedIngestionTests(unittest.TestCase):
    def test_csv_feed_is_loaded_with_source_metadata(self) -> None:
        records = load_csv_feed(IP_FEED, "demo_ip_feed")

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["source_name"], "demo_ip_feed")
        self.assertEqual(records[0]["source_format"], "csv")
        self.assertEqual(records[0]["source_record_number"], 1)
        self.assertEqual(
            records[0]["raw_record"]["indicator"],
            "185.220.101.34",
        )

    def test_json_feed_is_loaded_with_source_metadata(self) -> None:
        records = load_json_feed(DOMAIN_FEED, "demo_domain_feed")

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["source_name"], "demo_domain_feed")
        self.assertEqual(records[0]["source_format"], "json")
        self.assertEqual(records[0]["source_record_number"], 1)
        self.assertEqual(
            records[0]["raw_record"]["domain"],
            "evil-example.net",
        )


if __name__ == "__main__":
    unittest.main()
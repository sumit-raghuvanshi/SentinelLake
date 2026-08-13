"""Tests for SentinelLake IOC normalization."""

import unittest
from pathlib import Path

from src.sentinellake.ingestion import load_csv_feed, load_json_feed
from src.sentinellake.normalization import normalize_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_FEED = PROJECT_ROOT / "data" / "demo_feeds" / "ip_reputation_feed.csv"
DOMAIN_FEED = (
    PROJECT_ROOT / "data" / "demo_feeds" / "domain_watchlist_feed.json"
)
INGESTED_AT = "2026-08-13T10:00:00Z"


class ThreatFeedNormalizationTests(unittest.TestCase):
    def test_ip_feed_record_is_normalized(self) -> None:
        source_record = load_csv_feed(IP_FEED, "demo_ip_feed")[0]

        record = normalize_record(source_record, INGESTED_AT)

        self.assertEqual(record["ioc_type"], "ipv4")
        self.assertEqual(record["ioc_value"], "185.220.101.34")
        self.assertEqual(record["threat_category"], "malware")
        self.assertEqual(record["confidence_score"], 85)
        self.assertEqual(record["source_name"], "demo_ip_feed")
        self.assertEqual(record["source_record_id"], "ip-1001")
        self.assertEqual(record["ingested_at"], INGESTED_AT)
        self.assertEqual(record["validation_status"], "pending")

    def test_domain_feed_record_is_normalized(self) -> None:
        source_record = load_json_feed(DOMAIN_FEED, "demo_domain_feed")[0]

        record = normalize_record(source_record, INGESTED_AT)

        self.assertEqual(record["ioc_type"], "domain")
        self.assertEqual(record["ioc_value"], "evil-example.net")
        self.assertEqual(record["threat_category"], "phishing")
        self.assertEqual(record["confidence_score"], 92)
        self.assertEqual(record["source_name"], "demo_domain_feed")
        self.assertEqual(record["source_record_id"], "domain-2001")

    def test_unknown_source_is_rejected(self) -> None:
        source_record = {
            "source_name": "unknown_feed",
            "raw_record": {},
        }

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported threat-feed source: unknown_feed",
        ):
            normalize_record(source_record, INGESTED_AT)


if __name__ == "__main__":
    unittest.main()
"""Tests for SentinelLake IOC deduplication."""

import unittest
from pathlib import Path

from src.sentinellake.deduplication import deduplicate_accepted_records
from src.sentinellake.ingestion import load_csv_feed, load_json_feed
from src.sentinellake.normalization import normalize_record
from src.sentinellake.validation import validate_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_FEED = PROJECT_ROOT / "data" / "demo_feeds" / "ip_reputation_feed.csv"
COMMUNITY_FEED = (
    PROJECT_ROOT / "data" / "demo_feeds" / "community_ioc_feed.json"
)
INGESTED_AT = "2026-08-13T10:00:00Z"


class IocDeduplicationTests(unittest.TestCase):
    def test_same_ioc_from_two_sources_is_consolidated(self) -> None:
        ip_record = load_csv_feed(IP_FEED, "demo_ip_feed")[0]
        community_record = load_json_feed(
            COMMUNITY_FEED,
            "demo_community_feed",
        )[0]

        accepted_records = [
            validate_record(normalize_record(ip_record, INGESTED_AT)),
            validate_record(normalize_record(community_record, INGESTED_AT)),
        ]

        consolidated_records = deduplicate_accepted_records(accepted_records)

        self.assertEqual(len(consolidated_records), 1)

        record = consolidated_records[0]
        self.assertEqual(record["ioc_type"], "ipv4")
        self.assertEqual(record["ioc_value"], "185.220.101.34")
        self.assertEqual(record["record_count_before_deduplication"], 2)
        self.assertEqual(record["source_count"], 2)
        self.assertEqual(
            record["source_names"],
            ["demo_ip_feed", "demo_community_feed"],
        )
        self.assertEqual(record["confidence_score"], 90)
        self.assertEqual(
            record["threat_categories"],
            ["malware", "ransomware"],
        )

    def test_distinct_iocs_remain_separate(self) -> None:
        source_records = load_csv_feed(IP_FEED, "demo_ip_feed")[:2]
        accepted_records = [
            validate_record(normalize_record(record, INGESTED_AT))
            for record in source_records
        ]

        consolidated_records = deduplicate_accepted_records(accepted_records)

        self.assertEqual(len(consolidated_records), 2)
        self.assertTrue(
            all(
                record["record_count_before_deduplication"] == 1
                for record in consolidated_records
            )
        )


if __name__ == "__main__":
    unittest.main()
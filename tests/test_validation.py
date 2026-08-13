"""Tests for SentinelLake IOC validation."""

import unittest
from pathlib import Path

from src.sentinellake.ingestion import load_csv_feed, load_json_feed
from src.sentinellake.normalization import normalize_record
from src.sentinellake.validation import validate_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_FEED = PROJECT_ROOT / "data" / "demo_feeds" / "ip_reputation_feed.csv"
DOMAIN_FEED = (
    PROJECT_ROOT / "data" / "demo_feeds" / "domain_watchlist_feed.json"
)
INGESTED_AT = "2026-08-13T10:00:00Z"


class ThreatFeedValidationTests(unittest.TestCase):
    def test_valid_ipv4_record_is_accepted(self) -> None:
        source_record = load_csv_feed(IP_FEED, "demo_ip_feed")[0]
        record = normalize_record(source_record, INGESTED_AT)

        validated_record = validate_record(record)

        self.assertEqual(validated_record["validation_status"], "accepted")
        self.assertIsNone(validated_record["quarantine_reason"])

    def test_invalid_ipv4_record_is_quarantined(self) -> None:
        source_record = load_csv_feed(IP_FEED, "demo_ip_feed")[2]
        record = normalize_record(source_record, INGESTED_AT)

        validated_record = validate_record(record)

        self.assertEqual(validated_record["validation_status"], "quarantined")
        self.assertEqual(
            validated_record["quarantine_reason"],
            "invalid_ipv4_format",
        )

    def test_invalid_domain_record_is_quarantined(self) -> None:
        source_record = load_json_feed(DOMAIN_FEED, "demo_domain_feed")[2]
        record = normalize_record(source_record, INGESTED_AT)

        validated_record = validate_record(record)

        self.assertEqual(validated_record["validation_status"], "quarantined")
        self.assertEqual(
            validated_record["quarantine_reason"],
            "invalid_domain_format",
        )

    def test_invalid_confidence_score_is_quarantined(self) -> None:
        record = {
            "ioc_type": "domain",
            "ioc_value": "example.org",
            "source_name": "test_feed",
            "ingested_at": INGESTED_AT,
            "confidence_score": 101,
        }

        validated_record = validate_record(record)

        self.assertEqual(validated_record["validation_status"], "quarantined")
        self.assertEqual(
            validated_record["quarantine_reason"],
            "invalid_confidence_score",
        )


if __name__ == "__main__":
    unittest.main()
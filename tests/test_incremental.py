"""Tests for incremental IOC processing."""

import unittest

from src.sentinellake.incremental import (
    build_record_fingerprint,
    mark_incremental_status,
)


class IncrementalProcessingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = {
            "ioc_type": "ipv4",
            "ioc_value": "185.220.101.34",
            "confidence_score": 90,
            "threat_categories": ["malware"],
            "first_seen": "2026-08-13T08:00:00Z",
            "last_seen": "2026-08-13T09:00:00Z",
            "source_count": 1,
            "source_names": ["demo_ip_feed"],
            "source_record_ids": ["ip-1001"],
            "source_evidence": [{"source_name": "demo_ip_feed"}],
            "ingested_at": "2026-08-13T10:00:00Z",
        }

    def test_ingested_at_does_not_change_fingerprint(self) -> None:
        first_fingerprint = build_record_fingerprint(self.record)

        same_record_with_new_ingestion_time = dict(self.record)
        same_record_with_new_ingestion_time["ingested_at"] = (
            "2026-08-13T11:00:00Z"
        )

        second_fingerprint = build_record_fingerprint(
            same_record_with_new_ingestion_time
        )

        self.assertEqual(first_fingerprint, second_fingerprint)

    def test_records_are_classified_as_new_changed_or_unchanged(self) -> None:
        existing_fingerprints = {
            ("ipv4", "185.220.101.34"): build_record_fingerprint(self.record),
            ("domain", "old-example.net"): "old-fingerprint",
        }

        unchanged_record = dict(self.record)

        changed_record = dict(self.record)
        changed_record["ioc_type"] = "domain"
        changed_record["ioc_value"] = "old-example.net"
        changed_record["confidence_score"] = 95

        new_record = dict(self.record)
        new_record["ioc_value"] = "45.155.205.233"

        results = mark_incremental_status(
            [unchanged_record, changed_record, new_record],
            existing_fingerprints,
        )

        self.assertEqual(results[0]["incremental_status"], "unchanged")
        self.assertEqual(results[1]["incremental_status"], "changed")
        self.assertEqual(results[2]["incremental_status"], "new")


if __name__ == "__main__":
    unittest.main()
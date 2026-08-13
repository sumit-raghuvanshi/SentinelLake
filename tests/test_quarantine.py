"""Tests for SentinelLake quarantine routing."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.sentinellake.ingestion import load_csv_feed
from src.sentinellake.normalization import normalize_record
from src.sentinellake.quarantine import (
    split_validated_records,
    write_json_records,
)
from src.sentinellake.validation import validate_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_FEED = PROJECT_ROOT / "data" / "demo_feeds" / "ip_reputation_feed.csv"
INGESTED_AT = "2026-08-13T10:00:00Z"


class QuarantineRoutingTests(unittest.TestCase):
    def get_validated_ip_records(self) -> list[dict[str, object]]:
        """Load, normalize, and validate the demo IP records."""
        source_records = load_csv_feed(IP_FEED, "demo_ip_feed")

        return [
            validate_record(normalize_record(record, INGESTED_AT))
            for record in source_records
        ]

    def test_records_are_split_by_validation_status(self) -> None:
        records = self.get_validated_ip_records()

        accepted_records, quarantined_records = split_validated_records(records)

        self.assertEqual(len(accepted_records), 2)
        self.assertEqual(len(quarantined_records), 1)
        self.assertEqual(
            quarantined_records[0]["quarantine_reason"],
            "invalid_ipv4_format",
        )

    def test_record_collection_is_saved_as_json(self) -> None:
        records = self.get_validated_ip_records()

        with TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "quarantine.json"

            saved_path = write_json_records(records, output_path)

            self.assertEqual(saved_path, output_path)
            self.assertTrue(output_path.exists())

            with output_path.open(encoding="utf-8") as output_file:
                saved_records = json.load(output_file)

        self.assertEqual(saved_records, records)


if __name__ == "__main__":
    unittest.main()
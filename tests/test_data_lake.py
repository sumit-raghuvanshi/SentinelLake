"""Tests for SentinelLake local data-lake helpers."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.sentinellake.data_lake import (
    archive_raw_feed,
    create_run_directories,
    write_json_dataset,
)


class DataLakeTests(unittest.TestCase):
    def test_run_directories_are_created_for_all_zones(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            directories = create_run_directories(
                Path(temporary_directory),
                "20260813T120000Z",
            )

            self.assertEqual(
                set(directories),
                {"raw", "validated", "quarantine", "curated"},
            )

            for directory in directories.values():
                self.assertTrue(directory.is_dir())

    def test_raw_feed_is_archived_without_changing_content(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            source_path = temporary_path / "feed.csv"
            source_path.write_text(
                "indicator,score\n185.220.101.34,90\n",
                encoding="utf-8",
            )

            archived_path = archive_raw_feed(
                source_path,
                temporary_path / "raw",
            )

            self.assertEqual(
                archived_path.read_text(encoding="utf-8"),
                source_path.read_text(encoding="utf-8"),
            )

    def test_json_dataset_is_saved_to_a_zone(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            destination_path = (
                Path(temporary_directory)
                / "curated"
                / "accepted_iocs.json"
            )

            saved_path = write_json_dataset(
                [{"ioc_value": "evil-example.net"}],
                destination_path,
            )

            saved_records = json.loads(
                saved_path.read_text(encoding="utf-8")
            )

            self.assertEqual(
                saved_records,
                [{"ioc_value": "evil-example.net"}],
            )


if __name__ == "__main__":
    unittest.main()
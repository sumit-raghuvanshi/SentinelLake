"""Read raw threat-intelligence feeds from local files."""

import csv
import json
from pathlib import Path


def load_csv_feed(
    file_path: str | Path,
    source_name: str,
) -> list[dict[str, object]]:
    """Load a CSV threat feed and preserve every raw record."""
    path = Path(file_path)
    records = []

    with path.open(encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)

        if not reader.fieldnames:
            raise ValueError("CSV threat feed must contain a header row.")

        for record_number, row in enumerate(reader, start=1):
            records.append(
                {
                    "source_name": source_name,
                    "source_format": "csv",
                    "source_path": str(path),
                    "source_record_number": record_number,
                    "raw_record": dict(row),
                }
            )

    return records


def load_json_feed(
    file_path: str | Path,
    source_name: str,
) -> list[dict[str, object]]:
    """Load a JSON array threat feed and preserve every raw record."""
    path = Path(file_path)

    with path.open(encoding="utf-8") as source_file:
        raw_records = json.load(source_file)

    if not isinstance(raw_records, list):
        raise ValueError("JSON threat feed must contain an array of records.")

    records = []

    for record_number, raw_record in enumerate(raw_records, start=1):
        if not isinstance(raw_record, dict):
            raise ValueError(
                "Each JSON threat-feed record must be an object."
            )

        records.append(
            {
                "source_name": source_name,
                "source_format": "json",
                "source_path": str(path),
                "source_record_number": record_number,
                "raw_record": raw_record,
            }
        )

    return records
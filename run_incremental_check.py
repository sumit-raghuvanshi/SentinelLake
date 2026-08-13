"""Classify current accepted IOCs and save incremental processing history."""

from __future__ import annotations

import json
from pathlib import Path

from src.sentinellake.database import get_database_connection
from src.sentinellake.incremental import mark_incremental_status
from src.sentinellake.incremental_storage import (
    load_saved_fingerprints,
    save_incremental_results,
)


ACCEPTED_IOCS_PATH = Path("runtime/latest_run/accepted_iocs.json")
OUTPUT_PATH = Path("runtime/latest_run/incremental_iocs.json")


def main() -> int:
    if not ACCEPTED_IOCS_PATH.exists():
        print(
            "Error: accepted IOC output not found. "
            "Run python run_threat_pipeline.py first."
        )
        return 1

    accepted_records = json.loads(
        ACCEPTED_IOCS_PATH.read_text(encoding="utf-8")
    )

    with get_database_connection() as connection:
        existing_fingerprints = load_saved_fingerprints(connection)

        classified_records = mark_incremental_status(
            accepted_records,
            existing_fingerprints,
        )

        history_events_saved = save_incremental_results(
            connection,
            classified_records,
        )

    counts = {
        status: sum(
            record["incremental_status"] == status
            for record in classified_records
        )
        for status in ("new", "changed", "unchanged")
    }

    OUTPUT_PATH.write_text(
        json.dumps(classified_records, indent=2),
        encoding="utf-8",
    )

    print("SentinelLake Incremental Processing Report")
    print("-----------------------------------------")
    print(f"Records checked: {len(classified_records)}")
    print(f"New IOCs: {counts['new']}")
    print(f"Changed IOCs: {counts['changed']}")
    print(f"Unchanged IOCs: {counts['unchanged']}")
    print(f"History events saved: {history_events_saved}")
    print(f"Detailed output saved: {OUTPUT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
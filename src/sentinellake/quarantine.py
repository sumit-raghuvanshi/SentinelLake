"""Route validated threat-intelligence records to accepted or quarantine output."""

import json
from pathlib import Path


def split_validated_records(
    records: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Separate accepted records from quarantined records."""
    accepted_records = []
    quarantined_records = []

    for record in records:
        status = record.get("validation_status")

        if status == "accepted":
            accepted_records.append(record)
        elif status == "quarantined":
            quarantined_records.append(record)
        else:
            raise ValueError(
                "Record must be validated before quarantine routing."
            )

    return accepted_records, quarantined_records


def write_json_records(
    records: list[dict[str, object]],
    output_path: str | Path,
) -> Path:
    """Save a collection of records as formatted JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as output_file:
        json.dump(records, output_file, indent=2)
        output_file.write("\n")

    return path
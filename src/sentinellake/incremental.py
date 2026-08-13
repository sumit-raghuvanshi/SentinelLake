"""Helpers for incremental IOC processing."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping


FINGERPRINT_FIELDS = (
    "ioc_type",
    "ioc_value",
    "confidence_score",
    "threat_categories",
    "first_seen",
    "last_seen",
    "source_count",
    "source_names",
    "source_record_ids",
    "source_evidence",
)


def build_record_fingerprint(record: Mapping[str, Any]) -> str:
    """Return a stable fingerprint for the business data of one IOC."""

    tracked_data = {
        field: record.get(field)
        for field in FINGERPRINT_FIELDS
    }

    serialized_data = json.dumps(
        tracked_data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return sha256(serialized_data.encode("utf-8")).hexdigest()


def mark_incremental_status(
    records: list[dict[str, Any]],
    existing_fingerprints: Mapping[tuple[str, str], str],
) -> list[dict[str, Any]]:
    """Label each record as new, changed, or unchanged.

    existing_fingerprints maps:
    (ioc_type, ioc_value) -> previously saved fingerprint
    """

    classified_records: list[dict[str, Any]] = []

    for record in records:
        ioc_type = record["ioc_type"]
        ioc_value = record["ioc_value"]
        record_key = (ioc_type, ioc_value)
        fingerprint = build_record_fingerprint(record)
        previous_fingerprint = existing_fingerprints.get(record_key)

        if previous_fingerprint is None:
            status = "new"
        elif previous_fingerprint == fingerprint:
            status = "unchanged"
        else:
            status = "changed"

        classified_record = dict(record)
        classified_record["record_fingerprint"] = fingerprint
        classified_record["incremental_status"] = status
        classified_records.append(classified_record)

    return classified_records
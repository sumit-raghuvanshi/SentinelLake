"""Metrics used to observe SentinelLake pipeline quality."""

from __future__ import annotations

from typing import Any


def _percentage(part: int, whole: int) -> float:
    """Return a safe percentage rounded to two decimal places."""

    if whole == 0:
        return 0.0

    return round((part / whole) * 100, 2)


def calculate_pipeline_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    """Calculate data-quality and processing metrics from a pipeline summary."""

    records_ingested = int(summary["records_ingested"])
    accepted_before_deduplication = int(
        summary["records_accepted_before_deduplication"]
    )
    unique_iocs_accepted = int(summary["unique_iocs_accepted"])
    duplicate_ioc_records_consolidated = int(
        summary["duplicate_ioc_records_consolidated"]
    )
    records_quarantined = int(summary["records_quarantined"])

    return {
        "records_ingested": records_ingested,
        "records_accepted_before_deduplication": (
            accepted_before_deduplication
        ),
        "unique_iocs_accepted": unique_iocs_accepted,
        "records_quarantined": records_quarantined,
        "data_quality_score": _percentage(
            accepted_before_deduplication,
            records_ingested,
        ),
        "quarantine_rate": _percentage(
            records_quarantined,
            records_ingested,
        ),
        "deduplication_rate": _percentage(
            duplicate_ioc_records_consolidated,
            accepted_before_deduplication,
        ),
    }
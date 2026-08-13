"""Pipeline health checks for SentinelLake."""

from __future__ import annotations

from typing import Any


def evaluate_pipeline_health(
    metrics: dict[str, Any],
    minimum_expected_records: int,
    maximum_quarantine_rate: float,
) -> dict[str, Any]:
    """Evaluate pipeline health and return detected incidents."""

    incidents: list[dict[str, Any]] = []

    records_ingested = int(metrics["records_ingested"])
    quarantine_rate = float(metrics["quarantine_rate"])

    if records_ingested < minimum_expected_records:
        incidents.append(
            {
                "incident_type": "volume_anomaly",
                "severity": "high",
                "message": (
                    f"Only {records_ingested} records were ingested; "
                    f"at least {minimum_expected_records} were expected."
                ),
            }
        )

    if quarantine_rate > maximum_quarantine_rate:
        incidents.append(
            {
                "incident_type": "high_quarantine_rate",
                "severity": "medium",
                "message": (
                    f"Quarantine rate is {quarantine_rate}%, above the "
                    f"allowed {maximum_quarantine_rate}%."
                ),
            }
        )

    status = "healthy" if not incidents else "incident_detected"

    return {
        "status": status,
        "records_ingested": records_ingested,
        "quarantine_rate": quarantine_rate,
        "incident_count": len(incidents),
        "incidents": incidents,
    }
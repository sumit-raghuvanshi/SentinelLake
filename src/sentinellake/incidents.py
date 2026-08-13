"""PostgreSQL storage for SentinelLake pipeline incidents."""

from __future__ import annotations

from typing import Any

import psycopg
from psycopg.types.json import Jsonb


def save_incidents(
    connection: psycopg.Connection[Any],
    health_result: dict[str, Any],
) -> int:
    """Save detected health incidents and return the saved count."""

    incident_context = {
        "records_ingested": health_result["records_ingested"],
        "quarantine_rate": health_result["quarantine_rate"],
    }

    rows = [
        (
            incident["incident_type"],
            incident["severity"],
            incident["message"],
            Jsonb(incident_context),
        )
        for incident in health_result["incidents"]
    ]

    if not rows:
        return 0

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO pipeline_incidents (
                incident_type,
                severity,
                message,
                incident_context
            )
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )

    connection.commit()

    return len(rows)
"""PostgreSQL storage for incremental IOC processing state and history."""

from __future__ import annotations

from typing import Any

import psycopg
from psycopg.types.json import Jsonb


def load_saved_fingerprints(
    connection: psycopg.Connection[Any],
) -> dict[tuple[str, str], str]:
    """Load the most recently saved fingerprint for every IOC."""

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ioc_type, ioc_value, record_fingerprint
            FROM ioc_processing_state
            """
        )
        rows = cursor.fetchall()

    return {
        (ioc_type, ioc_value): record_fingerprint
        for ioc_type, ioc_value, record_fingerprint in rows
    }


def save_incremental_results(
    connection: psycopg.Connection[Any],
    records: list[dict[str, Any]],
) -> int:
    """Save current processing state and history for new or changed IOCs.

    Returns the number of history events saved.
    """

    state_rows = [
        (
            record["ioc_type"],
            record["ioc_value"],
            record["record_fingerprint"],
        )
        for record in records
    ]

    history_rows = [
        (
            record["ioc_type"],
            record["ioc_value"],
            record["incremental_status"],
            record["record_fingerprint"],
            Jsonb(record),
        )
        for record in records
        if record["incremental_status"] in ("new", "changed")
    ]

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO ioc_processing_state (
                ioc_type,
                ioc_value,
                record_fingerprint
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (ioc_type, ioc_value)
            DO UPDATE SET
                record_fingerprint = EXCLUDED.record_fingerprint,
                last_processed_at = NOW(),
                last_changed_at = CASE
                    WHEN ioc_processing_state.record_fingerprint
                        IS DISTINCT FROM EXCLUDED.record_fingerprint
                    THEN NOW()
                    ELSE ioc_processing_state.last_changed_at
                END,
                times_seen = ioc_processing_state.times_seen + 1
            """,
            state_rows,
        )

        if history_rows:
            cursor.executemany(
                """
                INSERT INTO ioc_change_history (
                    ioc_type,
                    ioc_value,
                    change_type,
                    record_fingerprint,
                    record_snapshot
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                history_rows,
            )

    connection.commit()

    return len(history_rows)
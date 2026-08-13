"""Save SentinelLake pipeline results in the PostgreSQL warehouse."""

from typing import Any

from psycopg.types.json import Jsonb

from src.sentinellake.database import get_database_connection


def save_pipeline_results(
    summary: dict[str, object],
    accepted_records: list[dict[str, object]],
    quarantined_records: list[dict[str, object]],
) -> int:
    """Save one completed pipeline run and its IOC records."""
    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pipeline_runs (
                    pipeline_name,
                    status,
                    source_count,
                    records_ingested,
                    records_accepted_before_deduplication,
                    unique_iocs_accepted,
                    duplicate_ioc_records_consolidated,
                    records_quarantined,
                    processing_duration_milliseconds
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING run_id
                """,
                (
                    "local_threat_intelligence_pipeline",
                    "completed",
                    summary["source_count"],
                    summary["records_ingested"],
                    summary["records_accepted_before_deduplication"],
                    summary["unique_iocs_accepted"],
                    summary["duplicate_ioc_records_consolidated"],
                    summary["records_quarantined"],
                    summary["processing_duration_milliseconds"],
                ),
            )
            run_id = cursor.fetchone()[0]

            for record in accepted_records:
                cursor.execute(
                    """
                    INSERT INTO threat_iocs (
                        ioc_type,
                        ioc_value,
                        confidence_score,
                        first_seen,
                        last_seen,
                        first_ingested_at,
                        last_ingested_at,
                        source_count,
                        source_names,
                        source_record_ids,
                        source_evidence,
                        threat_categories
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (ioc_type, ioc_value)
                    DO UPDATE SET
                        confidence_score = EXCLUDED.confidence_score,
                        first_seen = EXCLUDED.first_seen,
                        last_seen = EXCLUDED.last_seen,
                        last_ingested_at = EXCLUDED.last_ingested_at,
                        source_count = EXCLUDED.source_count,
                        source_names = EXCLUDED.source_names,
                        source_record_ids = EXCLUDED.source_record_ids,
                        source_evidence = EXCLUDED.source_evidence,
                        threat_categories = EXCLUDED.threat_categories,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        record["ioc_type"],
                        record["ioc_value"],
                        record.get("confidence_score"),
                        record.get("first_seen"),
                        record.get("last_seen"),
                        record["ingested_at"],
                        record["ingested_at"],
                        record.get("source_count", 1),
                        Jsonb(record.get("source_names", [])),
                        Jsonb(record.get("source_record_ids", [])),
                        Jsonb(record.get("source_evidence", [])),
                        Jsonb(record.get("threat_categories", [])),
                    ),
                )

            for record in quarantined_records:
                cursor.execute(
                    """
                    INSERT INTO quarantined_iocs (
                        run_id,
                        source_name,
                        source_record_id,
                        ioc_type,
                        ioc_value,
                        quarantine_reason,
                        raw_record
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        run_id,
                        record.get("source_name"),
                        record.get("source_record_id"),
                        record.get("ioc_type"),
                        record.get("ioc_value"),
                        record["quarantine_reason"],
                        Jsonb(record["raw_record"]),
                    ),
                )

        connection.commit()

    return run_id
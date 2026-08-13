"""Run SentinelLake's local threat-intelligence processing pipeline."""

import json
from pathlib import Path
from time import perf_counter

from src.sentinellake.deduplication import deduplicate_accepted_records
from src.sentinellake.ingestion import load_csv_feed, load_json_feed
from src.sentinellake.normalization import normalize_record
from src.sentinellake.quarantine import split_validated_records, write_json_records
from src.sentinellake.validation import validate_record


def write_pipeline_summary(
    summary: dict[str, object],
    output_path: str | Path,
) -> Path:
    """Save pipeline metrics as a JSON summary."""
    path = Path(output_path)

    with path.open("w", encoding="utf-8") as output_file:
        json.dump(summary, output_file, indent=2)
        output_file.write("\n")

    return path


def run_local_pipeline(
    ip_feed_path: str | Path,
    domain_feed_path: str | Path,
    community_feed_path: str | Path,
    output_directory: str | Path,
    ingested_at: str | None = None,
) -> dict[str, object]:
    """Ingest, normalize, validate, deduplicate, and route demo feeds."""
    started_at = perf_counter()
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    ip_source_records = load_csv_feed(ip_feed_path, "demo_ip_feed")
    domain_source_records = load_json_feed(
        domain_feed_path,
        "demo_domain_feed",
    )
    community_source_records = load_json_feed(
        community_feed_path,
        "demo_community_feed",
    )
    source_records = (
        ip_source_records
        + domain_source_records
        + community_source_records
    )

    normalized_records = [
        normalize_record(record, ingested_at)
        for record in source_records
    ]
    validated_records = [
        validate_record(record)
        for record in normalized_records
    ]
    accepted_records, quarantined_records = split_validated_records(
        validated_records
    )
    consolidated_records = deduplicate_accepted_records(accepted_records)

    accepted_output_path = write_json_records(
        consolidated_records,
        output_path / "accepted_iocs.json",
    )
    quarantine_output_path = write_json_records(
        quarantined_records,
        output_path / "quarantined_iocs.json",
    )

    duration_milliseconds = round(
        (perf_counter() - started_at) * 1000,
        2,
    )
    summary = {
        "source_count": 3,
        "records_ingested": len(source_records),
        "records_accepted_before_deduplication": len(accepted_records),
        "unique_iocs_accepted": len(consolidated_records),
        "duplicate_ioc_records_consolidated": (
            len(accepted_records) - len(consolidated_records)
        ),
        "records_quarantined": len(quarantined_records),
        "processing_duration_milliseconds": duration_milliseconds,
        "accepted_output_path": str(accepted_output_path),
        "quarantine_output_path": str(quarantine_output_path),
    }
    summary_output_path = write_pipeline_summary(
        summary,
        output_path / "pipeline_summary.json",
    )
    summary["summary_output_path"] = str(summary_output_path)

    return summary
"""Run the SentinelLake threat pipeline with retry and data-lake archiving."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from src.sentinellake.data_lake import (
    archive_raw_feed,
    create_run_directories,
    write_json_dataset,
)
from src.sentinellake.pipeline import run_local_pipeline
from src.sentinellake.recovery import RetryExhaustedError, run_with_retry


IP_FEED_PATH = "data/demo_feeds/ip_reputation_feed.csv"
DOMAIN_FEED_PATH = "data/demo_feeds/domain_watchlist_feed.json"
COMMUNITY_FEED_PATH = "data/demo_feeds/community_ioc_feed.json"
OUTPUT_DIRECTORY = "runtime/latest_run"

ACCEPTED_IOCS_PATH = Path("runtime/latest_run/accepted_iocs.json")
QUARANTINED_IOCS_PATH = Path(
    "runtime/latest_run/quarantined_iocs.json"
)
DATA_LAKE_ROOT = Path("runtime/data_lake")
RECOVERY_EVENT_PATH = Path(
    "runtime/latest_run/recovery_event.json"
)
LOG_PATH = Path("runtime/logs/pipeline_events.jsonl")


def write_recovery_event(event: dict[str, object]) -> None:
    """Write recovery details to JSON output and structured logs."""

    RECOVERY_EVENT_PATH.write_text(
        json.dumps(event, indent=2),
        encoding="utf-8",
    )

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")


def archive_pipeline_run(summary: dict[str, Any]) -> str:
    """Archive source snapshots and pipeline outputs in local data-lake zones."""

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directories = create_run_directories(DATA_LAKE_ROOT, run_id)

    for feed_path in (
        IP_FEED_PATH,
        DOMAIN_FEED_PATH,
        COMMUNITY_FEED_PATH,
    ):
        archive_raw_feed(Path(feed_path), directories["raw"])

    accepted_iocs = json.loads(
        ACCEPTED_IOCS_PATH.read_text(encoding="utf-8")
    )
    quarantined_iocs = json.loads(
        QUARANTINED_IOCS_PATH.read_text(encoding="utf-8")
    )

    validation_summary = {
        "run_id": run_id,
        "records_ingested": summary["records_ingested"],
        "records_accepted_before_deduplication": summary[
            "records_accepted_before_deduplication"
        ],
        "records_quarantined": summary["records_quarantined"],
    }

    write_json_dataset(
        validation_summary,
        directories["validated"] / "validation_summary.json",
    )
    write_json_dataset(
        quarantined_iocs,
        directories["quarantine"] / "quarantined_iocs.json",
    )
    write_json_dataset(
        accepted_iocs,
        directories["curated"] / "accepted_iocs.json",
    )
    write_json_dataset(
        summary,
        directories["curated"] / "pipeline_summary.json",
    )

    return run_id


def main() -> int:
    try:
        retry_result = run_with_retry(
            lambda: run_local_pipeline(
                IP_FEED_PATH,
                DOMAIN_FEED_PATH,
                COMMUNITY_FEED_PATH,
                OUTPUT_DIRECTORY,
            ),
            max_attempts=3,
            delay_seconds=1.0,
        )
    except RetryExhaustedError as error:
        event = {
            "event_name": "pipeline_recovery",
            "status": "failed_after_retries",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "message": str(error),
        }
        write_recovery_event(event)

        print(f"Error: {error}")
        print(f"Recovery event saved: {RECOVERY_EVENT_PATH}")
        return 1

    summary = retry_result.value
    data_lake_run_id = archive_pipeline_run(summary)

    event = {
        "event_name": "pipeline_recovery",
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "attempts_used": retry_result.attempts,
        "recovered_after_failure": bool(retry_result.failure_messages),
        "failure_messages": retry_result.failure_messages,
        "data_lake_run_id": data_lake_run_id,
    }
    write_recovery_event(event)

    print("SentinelLake Resilient Pipeline Run")
    print("-----------------------------------")
    print(f"Attempts used: {retry_result.attempts}")
    print(
        "Recovered after transient failure: "
        f"{'yes' if retry_result.failure_messages else 'no'}"
    )
    print(f"Records ingested: {summary['records_ingested']}")
    print(
        "Unique IOCs accepted: "
        f"{summary['unique_iocs_accepted']}"
    )
    print(f"Records quarantined: {summary['records_quarantined']}")
    print(f"Data-lake run archived: runtime/data_lake/{data_lake_run_id}")
    print(f"Recovery event saved: {RECOVERY_EVENT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
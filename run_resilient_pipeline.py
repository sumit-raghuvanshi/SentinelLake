"""Run the SentinelLake threat pipeline with controlled retry recovery."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from src.sentinellake.pipeline import run_local_pipeline
from src.sentinellake.recovery import RetryExhaustedError, run_with_retry


IP_FEED_PATH = "data/demo_feeds/ip_reputation_feed.csv"
DOMAIN_FEED_PATH = "data/demo_feeds/domain_watchlist_feed.json"
COMMUNITY_FEED_PATH = "data/demo_feeds/community_ioc_feed.json"
OUTPUT_DIRECTORY = "runtime/latest_run"

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

    event = {
        "event_name": "pipeline_recovery",
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "attempts_used": retry_result.attempts,
        "recovered_after_failure": bool(retry_result.failure_messages),
        "failure_messages": retry_result.failure_messages,
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
    print(f"Recovery event saved: {RECOVERY_EVENT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
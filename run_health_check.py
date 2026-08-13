"""Evaluate SentinelLake health metrics and store detected incidents."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from src.sentinellake.database import get_database_connection
from src.sentinellake.health import evaluate_pipeline_health
from src.sentinellake.incidents import save_incidents


OBSERVABILITY_REPORT_PATH = Path(
    "runtime/latest_run/observability_report.json"
)
HEALTH_REPORT_PATH = Path("runtime/latest_run/health_report.json")
LOG_PATH = Path("runtime/logs/pipeline_events.jsonl")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate SentinelLake pipeline health."
    )
    parser.add_argument(
        "--minimum-expected-records",
        type=int,
        default=8,
        help="Minimum acceptable number of ingested records.",
    )
    parser.add_argument(
        "--maximum-quarantine-rate",
        type=float,
        default=25.0,
        help="Maximum acceptable quarantine percentage.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    if not OBSERVABILITY_REPORT_PATH.exists():
        print(
            "Error: observability report not found. "
            "Run python run_observability_report.py first."
        )
        return 1

    observability_report = json.loads(
        OBSERVABILITY_REPORT_PATH.read_text(encoding="utf-8")
    )
    metrics = observability_report["metrics"]

    health_result = evaluate_pipeline_health(
        metrics,
        minimum_expected_records=arguments.minimum_expected_records,
        maximum_quarantine_rate=arguments.maximum_quarantine_rate,
    )

    with get_database_connection() as connection:
        incidents_saved = save_incidents(connection, health_result)

    report = {
        "event_name": "pipeline_health_check",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "thresholds": {
            "minimum_expected_records": arguments.minimum_expected_records,
            "maximum_quarantine_rate": arguments.maximum_quarantine_rate,
        },
        "health": health_result,
        "incidents_saved": incidents_saved,
    }

    HEALTH_REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(report) + "\n")

    print("SentinelLake Pipeline Health Check")
    print("----------------------------------")
    print(f"Pipeline status: {health_result['status']}")
    print(f"Incidents detected: {health_result['incident_count']}")
    print(f"Incidents saved to PostgreSQL: {incidents_saved}")
    print(f"Health report saved: {HEALTH_REPORT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
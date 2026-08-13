"""Generate a SentinelLake observability report from the latest pipeline run."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from src.sentinellake.observability import calculate_pipeline_metrics


SUMMARY_PATH = Path("runtime/latest_run/pipeline_summary.json")
REPORT_PATH = Path("runtime/latest_run/observability_report.json")
LOG_PATH = Path("runtime/logs/pipeline_events.jsonl")


def main() -> int:
    if not SUMMARY_PATH.exists():
        print(
            "Error: pipeline summary not found. "
            "Run python run_threat_pipeline.py first."
        )
        return 1

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    metrics = calculate_pipeline_metrics(summary)

    report = {
        "event_name": "pipeline_observability_report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }

    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(report) + "\n")

    print("SentinelLake Observability Report")
    print("---------------------------------")
    print(f"Records ingested: {metrics['records_ingested']}")
    print(f"Accepted before deduplication: "
          f"{metrics['records_accepted_before_deduplication']}")
    print(f"Unique IOCs accepted: {metrics['unique_iocs_accepted']}")
    print(f"Records quarantined: {metrics['records_quarantined']}")
    print(f"Data quality score: {metrics['data_quality_score']}%")
    print(f"Quarantine rate: {metrics['quarantine_rate']}%")
    print(f"Deduplication rate: {metrics['deduplication_rate']}%")
    print(f"JSON report saved: {REPORT_PATH}")
    print(f"Structured log saved: {LOG_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
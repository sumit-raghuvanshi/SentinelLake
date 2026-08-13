"""Load the latest SentinelLake pipeline output into PostgreSQL."""

import json
from pathlib import Path

from src.sentinellake.warehouse import save_pipeline_results


RUNTIME_DIRECTORY = Path("runtime/latest_run")


def load_json_file(file_name: str) -> object:
    """Read one JSON file from the latest pipeline output folder."""
    path = RUNTIME_DIRECTORY / file_name

    with path.open(encoding="utf-8") as input_file:
        return json.load(input_file)


def main() -> int:
    """Load accepted and quarantined IOC results into PostgreSQL."""
    try:
        summary = load_json_file("pipeline_summary.json")
        accepted_records = load_json_file("accepted_iocs.json")
        quarantined_records = load_json_file("quarantined_iocs.json")
    except FileNotFoundError as error:
        print(
            "Error: pipeline output file not found. "
            "Run python run_threat_pipeline.py first."
        )
        print(f"Missing file: {error.filename}")
        return 1

    run_id = save_pipeline_results(
        summary,
        accepted_records,
        quarantined_records,
    )

    print("SentinelLake warehouse load complete.")
    print(f"Pipeline run ID: {run_id}")
    print(f"Accepted IOCs saved: {len(accepted_records)}")
    print(f"Quarantined records saved: {len(quarantined_records)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
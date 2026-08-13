"""Functions for saving SentinelLake reports."""

import json
from pathlib import Path


def write_json_report(
    report: dict[str, object],
    output_path: str | Path,
) -> Path:
    """Save an analysis report as a formatted JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2)
        report_file.write("\n")

    return path
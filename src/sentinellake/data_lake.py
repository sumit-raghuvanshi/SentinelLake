"""Helpers for SentinelLake local data-lake storage zones."""

from __future__ import annotations

import json
from pathlib import Path
from shutil import copy2
from typing import Any


DATA_LAKE_ZONES = (
    "raw",
    "validated",
    "quarantine",
    "curated",
)


def create_run_directories(
    data_lake_root: Path,
    run_id: str,
) -> dict[str, Path]:
    """Create and return data-lake directories for one pipeline run."""

    if not run_id.strip():
        raise ValueError("run_id must not be empty.")

    directories = {
        zone: data_lake_root / zone / run_id
        for zone in DATA_LAKE_ZONES
    }

    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    return directories


def archive_raw_feed(
    source_path: Path,
    raw_directory: Path,
) -> Path:
    """Copy one source feed into the immutable raw zone."""

    if not source_path.is_file():
        raise FileNotFoundError(
            f"Threat feed file not found: {source_path}"
        )

    raw_directory.mkdir(parents=True, exist_ok=True)

    archived_path = raw_directory / source_path.name
    copy2(source_path, archived_path)

    return archived_path


def write_json_dataset(
    records: Any,
    destination_path: Path,
) -> Path:
    """Write a JSON dataset to a data-lake zone."""

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    return destination_path
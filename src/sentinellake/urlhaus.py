"""URLhaus Community API download helpers."""

from __future__ import annotations

from pathlib import Path
import ssl
from typing import Callable
from urllib.parse import quote
from urllib.request import Request, urlopen

import certifi


URLHAUS_RECENT_CSV_URL = (
    "https://urlhaus-api.abuse.ch/v2/files/exports/{auth_key}/recent.csv"
)


def load_local_environment(env_path: Path) -> dict[str, str]:
    """Load simple KEY=value settings from a local .env file."""

    if not env_path.is_file():
        raise FileNotFoundError(
            f"Local environment file not found: {env_path}"
        )

    settings: dict[str, str] = {}

    for line in env_path.read_text(encoding="utf-8").splitlines():
        cleaned_line = line.strip()

        if not cleaned_line or cleaned_line.startswith("#"):
            continue

        key, separator, value = cleaned_line.partition("=")

        if not separator or not key.strip():
            raise ValueError(
                f"Invalid environment setting in {env_path}: {line}"
            )

        settings[key.strip()] = value.strip()

    return settings


def build_recent_csv_url(auth_key: str) -> str:
    """Build the authenticated URLhaus recent-CSV download URL."""

    cleaned_key = auth_key.strip()

    if not cleaned_key:
        raise ValueError("URLhaus Auth-Key is required.")

    return URLHAUS_RECENT_CSV_URL.format(
        auth_key=quote(cleaned_key, safe=""),
    )


def download_recent_csv(
    auth_key: str,
    destination_path: Path,
    *,
    timeout_seconds: int = 30,
    urlopen_function: Callable = urlopen,
) -> Path:
    """Download the authenticated URLhaus recent CSV to local raw storage."""

    download_url = build_recent_csv_url(auth_key)

    request = Request(
        download_url,
        headers={
            "User-Agent": "SentinelLake-Learning-Project/1.0",
        },
    )

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    with urlopen_function(
        request,
        timeout=timeout_seconds,
        context=ssl_context,
    ) as response:
        feed_content = response.read()

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_bytes(feed_content)

    return destination_path
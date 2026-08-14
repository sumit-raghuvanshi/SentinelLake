"""Download a live URLhaus recent CSV into SentinelLake raw storage."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

from src.sentinellake.urlhaus import (
    download_recent_csv,
    load_local_environment,
)


ENV_PATH = Path(".env")
DATA_LAKE_RAW_ROOT = Path("runtime/data_lake/raw")
MANIFEST_ROOT = Path("runtime/live_feeds/manifests")


def main() -> int:
    try:
        settings = load_local_environment(ENV_PATH)
        auth_key = settings.get("URLHAUS_AUTH_KEY", "").strip()

        if not auth_key:
            raise ValueError("URLHAUS_AUTH_KEY is missing from .env.")
    except (FileNotFoundError, ValueError) as error:
        print(f"Configuration error: {error}")
        return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination_path = (
        DATA_LAKE_RAW_ROOT / run_id / "urlhaus_recent.csv"
    )

    try:
        saved_path = download_recent_csv(auth_key, destination_path)
    except (HTTPError, URLError, OSError) as error:
        print(f"URLhaus download failed: {error}")
        return 1

    manifest = {
        "source_name": "urlhaus_recent_csv",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "raw_data_path": str(saved_path),
        "file_size_bytes": saved_path.stat().st_size,
        "auth_key_saved": False,
    }

    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_ROOT / f"urlhaus_{run_id}.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("SentinelLake URLhaus Raw Feed Download")
    print("---------------------------------------")
    print(f"Raw feed saved: {saved_path}")
    print(f"Downloaded bytes: {manifest['file_size_bytes']}")
    print(f"Manifest saved: {manifest_path}")
    print("The Auth-Key was not written to the manifest.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Run the local SentinelLake threat-intelligence pipeline."""

import argparse
from pathlib import Path

from src.sentinellake.pipeline import run_local_pipeline


def get_arguments() -> argparse.Namespace:
    """Read command-line options for the local demo pipeline."""
    parser = argparse.ArgumentParser(
        description="Run SentinelLake's local threat-intelligence pipeline."
    )
    parser.add_argument(
        "--ip-feed",
        type=Path,
        default=Path("data/demo_feeds/ip_reputation_feed.csv"),
        help="Path to the demo CSV IP threat feed.",
    )
    parser.add_argument(
        "--domain-feed",
        type=Path,
        default=Path("data/demo_feeds/domain_watchlist_feed.json"),
        help="Path to the demo JSON domain threat feed.",
    )
    parser.add_argument(
        "--community-feed",
        type=Path,
        default=Path("data/demo_feeds/community_ioc_feed.json"),
        help="Path to the demo community IOC JSON feed.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/latest_run"),
        help="Folder where accepted, quarantined, and summary files are saved.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the pipeline and print its processing metrics."""
    args = get_arguments()

    try:
        summary = run_local_pipeline(
            args.ip_feed,
            args.domain_feed,
            args.community_feed,
            args.output_dir,
        )
    except FileNotFoundError as error:
        print(f"Error: threat-feed file not found: {error.filename}")
        return 1
    except ValueError as error:
        print(f"Error: invalid threat feed: {error}")
        return 1

    print("SentinelLake Threat Intelligence Pipeline")
    print("-" * 42)
    print(f"Sources processed: {summary['source_count']}")
    print(f"Records ingested: {summary['records_ingested']}")
    print(
        "Accepted before deduplication: "
        f"{summary['records_accepted_before_deduplication']}"
    )
    print(f"Unique IOCs accepted: {summary['unique_iocs_accepted']}")
    print(
        "Duplicate IOC records consolidated: "
        f"{summary['duplicate_ioc_records_consolidated']}"
    )
    print(f"Records quarantined: {summary['records_quarantined']}")
    print(
        "Processing duration (ms): "
        f"{summary['processing_duration_milliseconds']}"
    )
    print(f"Accepted output: {summary['accepted_output_path']}")
    print(f"Quarantine output: {summary['quarantine_output_path']}")
    print(f"Run summary: {summary['summary_output_path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
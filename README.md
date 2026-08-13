# SentinelLake

SentinelLake is a local cyber threat-intelligence data pipeline built with Python and PostgreSQL.

It ingests fictional demonstration threat feeds, converts records into one common IOC format, validates data quality, quarantines invalid records, consolidates duplicate IOCs, tracks incremental changes, and saves results in a PostgreSQL warehouse.

> This is a learning project. The included feeds are fictional and are not live threat intelligence.

## What it currently does

- Ingests CSV and JSON threat-feed files
- Normalizes different source formats into a canonical IOC record
- Validates IPv4 addresses, domain names, timestamps, and confidence scores
- Sends invalid records to a quarantine dataset with a reason
- Deduplicates accepted IOCs across sources
- Preserves source evidence and calculates source counts
- Writes pipeline outputs as JSON files
- Loads accepted IOCs, quarantined records, and pipeline runs into PostgreSQL
- Tracks each IOC as `new`, `changed`, or `unchanged`
- Stores immutable snapshots for new and changed IOCs
- Calculates data-quality, quarantine, and deduplication metrics
- Produces JSON observability reports and structured JSON-line event logs
- Detects low-volume and high-quarantine-rate incidents
- Stores detected incidents in PostgreSQL
- Retries transient pipeline failures up to three times
- Runs automated unit tests through GitHub Actions

## Pipeline flow

```text
Demo CSV / JSON feeds
        |
        v
Ingestion and normalization
        |
        v
Validation -----> Quarantine invalid records
        |
        v
Deduplication and consolidation
        |
        v
Incremental state + IOC history
        |
        v
JSON runtime output + PostgreSQL warehouse
        |
        v
Observability metrics + health checks + controlled retry

```text
Technology
    Python 3
    PostgreSQL 18
    psycopg 3
    unittest
    GitHub Actions

```text
Project structure
data/demo_feeds/         Fictional input threat feeds
docs/                      Architecture and data dictionary
sql/                    PostgreSQL schema migrations
src/sentinellake/      Pipeline source code
tests/                 Automated tests
run_threat_pipeline.py Basic local pipeline runner
run_resilient_pipeline.py Pipeline runner with controlled retry
run_incremental_check.py Incremental IOC classifier and history writer
run_observability_report.py Pipeline metric report generator
run_health_check.py    Health check and incident recorder
load_warehouse.py      Load latest pipeline result into PostgreSQL
Setup
Create and activate a virtual environment:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Install dependencies:
python -m pip install -r requirements.txt
# SentinelLake

SentinelLake is a local cyber threat-intelligence data pipeline built with Python, PostgreSQL, and Docker.

It ingests fictional demonstration threat feeds, converts records into one common IOC format, validates data quality, quarantines invalid records, consolidates duplicate IOCs, tracks incremental changes, and saves results in a PostgreSQL warehouse.

> This is a learning project. The included feeds are fictional and are not live threat intelligence.

## What it currently does

- Ingests CSV and JSON threat-feed files
- Normalizes different source formats into a canonical IOC record
- Validates IPv4 addresses, domain names, timestamps, and confidence scores
- Sends invalid records to a quarantine dataset with a reason
- Deduplicates accepted IOCs across sources
- Preserves source evidence and calculates source counts
- Tracks each IOC as `new`, `changed`, or `unchanged`
- Stores immutable snapshots for new and changed IOCs
- Loads accepted IOCs, quarantined records, and pipeline runs into PostgreSQL
- Calculates data-quality, quarantine, and deduplication metrics
- Detects low-volume and high-quarantine-rate incidents
- Stores detected incidents in PostgreSQL
- Retries transient pipeline failures up to three times
- Runs locally or through Docker Compose
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
PostgreSQL warehouse
        |
        v
Observability metrics + health checks + controlled retry
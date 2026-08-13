# SentinelLake

SentinelLake is a local cyber threat-intelligence data pipeline built with Python and PostgreSQL.

It ingests fictional demonstration threat feeds, converts records into one common IOC format, validates data quality, quarantines invalid records, consolidates duplicate IOCs, and saves the results in a PostgreSQL warehouse.

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
JSON runtime output + PostgreSQL warehouse
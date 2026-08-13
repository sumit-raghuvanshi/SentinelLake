# SentinelLake

SentinelLake is a local Python MVP for a cyber threat-intelligence data pipeline.

It ingests threat-feed data from multiple source formats, normalizes records into one canonical Indicator of Compromise (IOC) schema, validates data quality, and separates accepted records from quarantined records.

## Current MVP capabilities

- Ingest a CSV IP reputation feed and a JSON domain watchlist feed
- Preserve each raw source record for traceability
- Normalize source-specific fields into a canonical IOC schema
- Validate:
  - IPv4 addresses
  - Domain names
  - IOC types
  - Required IOC values
  - Source names and ingestion timestamps
  - Confidence scores from 0 to 100
- Quarantine invalid records with a stored rejection reason
- Save accepted records, quarantined records, and pipeline metrics as JSON files
- Track pipeline metrics:
  - Sources processed
  - Records ingested
  - Records accepted
  - Records quarantined
  - Processing duration
- Run automated tests locally and through GitHub Actions

## Run the threat-intelligence pipeline

From the SentinelLake project folder:

```text
python run_threat_pipeline.py
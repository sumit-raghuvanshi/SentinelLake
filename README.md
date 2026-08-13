# SentinelLake

SentinelLake is a local Python MVP for a cyber threat-intelligence data pipeline.

It ingests threat-feed data from multiple source formats, normalizes records into a canonical Indicator of Compromise (IOC) schema, validates data quality, quarantines invalid records, and consolidates duplicate IOCs across sources.

## Current MVP capabilities

- Ingest three local threat-intelligence feeds:
  - CSV IP reputation feed
  - JSON domain watchlist feed
  - JSON community IOC feed
- Preserve raw source records for traceability
- Normalize different source schemas into one canonical IOC schema
- Validate:
  - IPv4 addresses
  - Domain names
  - IOC types and values
  - Source names and ingestion timestamps
  - Confidence scores from 0 to 100
- Quarantine invalid records with a stored rejection reason
- Deduplicate accepted IOCs across sources
  - Preserve source evidence
  - Keep all observed threat categories
  - Keep the highest confidence score
- Save accepted IOCs, quarantined records, and pipeline metrics as JSON files
- Track pipeline metrics:
  - Sources processed
  - Records ingested
  - Records accepted before deduplication
  - Unique IOCs accepted
  - Duplicate IOC records consolidated
  - Records quarantined
  - Processing duration
- Run automated tests locally and through GitHub Actions

## Run the pipeline

```text
python run_threat_pipeline.py
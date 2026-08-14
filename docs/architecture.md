# SentinelLake Architecture

## Purpose

SentinelLake is a local learning project for a cyber threat-intelligence pipeline. It turns the included fictional feed records into validated, deduplicated canonical IOCs and records the results for local analysis.

## Processing flow

```text
Fictional CSV and JSON demo feeds
        |
        v
Python ingestion layer
        |
        v
Canonical IOC normalization
        |
        v
Validation ------------------> Quarantine records and reasons
        |
        v
Cross-source deduplication
        |
        +-----------------> Incremental classification and history
        |
        +-----------------> Local data-lake archive
        |
        +-----------------> Local-mode Spark analytics
        |
        v
Local PostgreSQL warehouse
        |
        v
Observability, health checks, incidents, and controlled retry
```

## Components

| Component | Responsibility |
|---|---|
| `src/sentinellake/ingestion.py` | Reads CSV and JSON source records. |
| `src/sentinellake/normalization.py` | Converts supported source records into the canonical IOC schema. |
| `src/sentinellake/validation.py` | Accepts valid IOCs or assigns a quarantine reason. |
| `src/sentinellake/deduplication.py` | Consolidates the same IOC found in multiple accepted records. |
| `src/sentinellake/data_lake.py` | Archives run-scoped raw, validated, quarantine, and curated outputs locally. |
| `src/sentinellake/incremental.py` | Classifies accepted IOCs as new, changed, or unchanged. |
| `src/sentinellake/observability.py` and `health.py` | Creates metrics, health reports, and incident records. |
| `src/sentinellake/warehouse.py` | Loads accepted IOCs, quarantined records, and run details into local PostgreSQL. |
| `dags/sentinellake_pipeline.py` | Defines the local Airflow task sequence. |
| `spark_jobs/build_ioc_analytics.py` | Produces local Spark analytics from curated IOCs. |

## Storage boundaries

The repository contains source code, fictional demo feeds, SQL migrations, and tests. Generated runtime data is intentionally local only:

```text
runtime/
  data_lake/       Run-scoped raw, validated, quarantine, and curated archives
  latest_run/      Latest local pipeline outputs
  live_feeds/      Optional manually downloaded feed files and manifests
  logs/            Local logs
  spark_analytics/ Local Spark output
```

The optional URLhaus downloader stores a raw CSV and manifest under `runtime/`. It does not expose the Auth-Key and is not part of the scheduled pipeline in version 1.0.0.

## Deployment model

Docker Compose starts local PostgreSQL, Airflow, and Spark services. This configuration is for development and learning only: it has no cloud deployment, high availability, or production secret management.

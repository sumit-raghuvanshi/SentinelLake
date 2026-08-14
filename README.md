# SentinelLake

**Version 1.0.0**

SentinelLake is a local cyber threat-intelligence learning project. It processes fictional CSV and JSON feeds into a canonical indicator-of-compromise (IOC) format, validates and quarantines bad records, consolidates duplicates, records run metrics, and can load results into a local PostgreSQL warehouse.

## What version 1.0.0 includes

- CSV and JSON ingestion for the included fictional demonstration feeds
- Canonical IOC normalization for IPv4 addresses, domains, URLs, and SHA-256 hashes
- Validation, quarantine routing, and clear quarantine reasons
- Cross-source IOC deduplication with preserved source evidence
- Incremental new/changed/unchanged classification and historical snapshots
- Local run-scoped data-lake archives
- Local PostgreSQL warehouse loading
- Pipeline observability, health checks, incident records, and controlled retries
- Local Docker Compose services for PostgreSQL, Airflow, and Spark
- A local Airflow DAG and a local-mode PySpark analytics job
- An optional manual URLhaus recent-CSV downloader that stores raw data locally only
- GitHub Actions unit-test workflow

## Important scope and safety notes

- The default pipeline uses only the fictional files in `data/demo_feeds/`.
- URLhaus download is optional and manual. It requires a user-supplied Auth-Key in a local `.env` file; the key is not committed and is not written to the download manifest.
- URLhaus data is not automatically parsed into the pipeline or loaded into PostgreSQL in version 1.0.0.
- Generated runtime data, logs, and raw downloads stay local and are intentionally ignored by Git.
- The Docker Compose database password is a local development credential, not a production secret.

## Quick start on Windows

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m unittest discover -v
```

To run the local Docker workflow, start Docker Desktop and run:

```text
docker compose up --build
```

The application container exits successfully after its one-time workflow finishes. Stop the services with:

```text
docker compose down
```

## Useful commands

```text
# Run the resilient local pipeline
python run_resilient_pipeline.py

# Classify incremental changes and create history
python run_incremental_check.py

# Generate observability and health outputs
python run_observability_report.py
python run_health_check.py

# Load the latest output into local PostgreSQL
python load_warehouse.py

# Run local Spark analytics after a pipeline run
docker compose run --rm spark-analytics

# Run the optional URLhaus raw downloader after creating .env locally
python run_urlhaus_download.py
```

## Local services

| Service | Purpose | Local address |
|---|---|---|
| PostgreSQL | Local warehouse | `localhost:5433` |
| Airflow | Local workflow orchestration | `http://localhost:8080` |
| Spark | Local IOC analytics job | Runs on demand through Docker Compose |

## Documentation

- [Architecture](docs/architecture.md)
- [Canonical IOC data dictionary](docs/data_dictionary.md)
- [Warehouse schema](sql/001_create_warehouse.sql)

## Current limitations

- This is a local learning project, not a production or high-availability deployment.
- Cloud storage, cloud warehousing, Kafka, an API, and a dashboard are not implemented.
- Airflow and Spark run locally in single-container modes.
- Validation rules are implemented for the supported IOC types only.

## License

No license has been selected for this repository yet.

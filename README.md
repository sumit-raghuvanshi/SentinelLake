# SentinelLake

**A local cyber threat-intelligence data pipeline for learning and portfolio use.**

SentinelLake ingests fictional threat feeds, converts them into one canonical Indicator of Compromise (IOC) format, validates and quarantines bad records, consolidates duplicate IOCs, tracks changes between runs, archives local outputs, and loads results into a local PostgreSQL warehouse.

> **Release:** `v1.0.0`
>
> **Author:** Sumit Raghuvanshi
>
> **Project type:** Local learning project — not a production threat-intelligence platform.

---

## Table of contents

- [Features](#features)
- [Architecture and connections](#architecture-and-connections)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Quick start on Windows](#quick-start-on-windows)
- [Run with Docker Compose](#run-with-docker-compose)
- [Airflow orchestration](#airflow-orchestration)
- [Spark analytics](#spark-analytics)
- [Optional URLhaus download](#optional-urlhaus-download)
- [Testing](#testing)
- [Security and data handling](#security-and-data-handling)
- [Current limitations](#current-limitations)
- [Documentation](#documentation)
- [Author](#author)

---

## Features

- **Multi-format ingestion** — reads the included fictional CSV and JSON threat feeds.
- **Canonical IOC normalization** — standardizes IPv4, domain, URL, and SHA-256 records.
- **Validation and quarantine** — invalid records are separated with a specific quarantine reason.
- **Deduplication** — consolidates matching accepted IOCs while preserving source evidence.
- **Incremental processing** — classifies IOCs as `new`, `changed`, or `unchanged` and writes historical snapshots.
- **Local data lake** — creates run-scoped raw, validated, quarantine, and curated archives.
- **PostgreSQL warehouse** — loads accepted IOCs, quarantined records, and run details into a local database.
- **Observability and health checks** — creates pipeline metrics and records low-volume or high-quarantine incidents.
- **Controlled retry** — retries configured transient failures in the local workflow.
- **Airflow orchestration** — provides a local DAG for the project workflow.
- **Spark analytics** — produces local IOC and threat-category aggregates.
- **Optional URLhaus raw download** — downloads a recent CSV locally when the user supplies an Auth-Key.
- **Automated tests** — unit tests run locally and through GitHub Actions.

---

## Architecture and connections

```text
Fictional CSV / JSON demo feeds                 Optional URLhaus recent CSV
              |                                           |
              +-------------------+-----------------------+
                                  |
                                  v
                    Python ingestion and normalization
                                  |
                                  v
                        Validation and quarantine
                         |                     |
                         |                     +--> Quarantined records
                         v
                  Cross-source deduplication
                                  |
              +-------------------+--------------------+
              |                   |                    |
              v                   v                    v
     Local data-lake archive  Incremental history  Spark analytics
              |                   |                    |
              +-------------------+--------------------+
                                  |
                                  v
                    Local PostgreSQL warehouse
                                  |
                                  v
         Observability, health checks, incidents, retries
```

### Docker service connections

| Service | Connects to | Purpose |
|---|---|---|
| `app` | PostgreSQL and mounted `runtime/` directory | Runs the one-time resilient pipeline and warehouse load. |
| `postgres` | Host port `5433` | Stores local warehouse tables and pipeline-run data. |
| `airflow` | Project DAGs, project source, PostgreSQL warehouse | Runs the local orchestration DAG and exposes the Airflow UI on port `8080`. |
| `spark-analytics` | Curated local runtime output | Runs Spark in local mode and writes analytics under `runtime/spark_analytics/`. |

The `app` service waits for PostgreSQL health checks before it runs. The Airflow and Spark containers mount the project directory so they can use the project DAGs, source code, and local runtime outputs.

---

## Technology stack

| Area | Technology |
|---|---|
| Language | Python 3.14 |
| Database | PostgreSQL 18 |
| Containers | Docker and Docker Compose |
| Orchestration | Apache Airflow 3.1.7 |
| Analytics | Apache Spark 4.1.2 / PySpark in local mode |
| Database adapter | psycopg 3 |
| HTTPS certificates | certifi |
| Tests | Python `unittest` |
| Continuous integration | GitHub Actions |

---

## Project structure

```text
SentinelLake/
├── data/
│   └── demo_feeds/              Fictional input feeds
├── dags/                        Airflow DAG definitions
├── docs/                        Architecture and data dictionary
├── spark_jobs/                  Local Spark analytics job
├── sql/                         PostgreSQL schema migrations
├── src/sentinellake/            Pipeline source code
├── tests/                       Automated unit tests
├── runtime/                     Local generated outputs (ignored by Git)
├── docker-compose.yml           Local PostgreSQL, Airflow, app, and Spark services
├── run_resilient_pipeline.py    Pipeline runner with retry and data-lake archive
├── run_incremental_check.py     Incremental IOC classifier and history writer
├── run_observability_report.py  Observability report generator
├── run_health_check.py          Health check and incident recorder
├── run_urlhaus_download.py      Optional manual URLhaus raw downloader
├── load_warehouse.py            Local PostgreSQL warehouse loader
├── requirements.txt             Python dependencies
├── CHANGELOG.md                 Version history
└── VERSION                      Current project version
```

---

## Quick start on Windows

### 1. Create and activate a virtual environment

```text
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```text
python -m pip install -r requirements.txt
```

### 3. Run the full test suite

```text
python -m unittest discover -v
```

### 4. Run the local pipeline scripts

```text
python run_resilient_pipeline.py
python run_incremental_check.py
python run_observability_report.py
python run_health_check.py
```

Generated outputs are stored under `runtime/` and remain local to your machine.

---

## Run with Docker Compose

### Prerequisite

Install and start Docker Desktop.

### Start PostgreSQL and run the one-time application workflow

```text
docker compose up --build
```

The application container exits with code `0` after its one-time workflow completes. PostgreSQL remains available on `localhost:5433`.

### Run tests in Docker

```text
docker compose run --rm app python -m unittest discover -v
```

### Stop local services

```text
docker compose down
```

> The PostgreSQL password in `docker-compose.yml` is for local development only. Do not reuse it in a real deployment.

---

## Airflow orchestration

Start the local Airflow service:

```text
docker compose up -d --build airflow
```

Open the local Airflow UI:

```text
http://localhost:8080
```

The DAG name is:

```text
sentinellake_threat_intelligence_pipeline
```

Its task flow is:

```text
ingest_and_validate
  -> incremental_processing
  -> generate_observability
  -> health_check
  -> load_warehouse
```

Airflow runs locally in standalone mode. It is included for orchestration learning, not production scheduling.

---

## Spark analytics

Run the local Spark job after a pipeline run has created `runtime/latest_run/accepted_iocs.json`:

```text
docker compose run --rm spark-analytics
```

The job writes local output under:

```text
runtime/spark_analytics/
```

It calculates IOC counts by type and threat category, unique IOC count, average confidence score, and total source observations.

---

## Optional URLhaus download

SentinelLake can manually download a recent URLhaus CSV into local raw storage. This feature is optional and does not automatically feed records into the scheduled pipeline in version 1.0.0.

1. Obtain your own Auth-Key from the [URLhaus Community API](https://urlhaus.abuse.ch/api/).
2. Create a local `.env` file in the project root:

```text
URLHAUS_AUTH_KEY=your-private-auth-key
```

3. Run the downloader:

```text
python run_urlhaus_download.py
```

The Auth-Key is not committed to Git and is not written to the generated manifest. Do not share the key in issues, screenshots, commits, or chat messages.

---

## Testing

Run all unit tests locally:

```text
python -m unittest discover -v
```

The GitHub Actions workflow runs the same unit-test command on pushes and pull requests to `main`.

---

## Security and data handling

- `.env` is ignored by Git; use it only for local secrets such as a URLhaus Auth-Key.
- `runtime/` outputs, logs, local feed downloads, and Spark results are ignored by Git.
- The included demo feeds are fictional.
- Do not place production credentials, real incident data, or private threat-intelligence feeds in this repository.

---

## Current limitations

- This is a local learning project, not a production or high-availability deployment.
- Cloud storage, cloud warehousing, Kafka, a REST API, and a dashboard are not implemented.
- Airflow and Spark run in single-machine local modes.
- The optional URLhaus download is manual and is not yet normalized or loaded into PostgreSQL.
- No software license has been selected for this repository yet.

---

## Documentation

- [Architecture](docs/architecture.md)
- [Canonical IOC data dictionary](docs/data_dictionary.md)
- [Warehouse schema](sql/001_create_warehouse.sql)
- [Changelog](CHANGELOG.md)

---

## Author

**Sumit Raghuvanshi**

SentinelLake was created as a hands-on learning and portfolio project for data engineering, threat-intelligence processing, Docker, Airflow, PySpark, PostgreSQL, testing, and GitHub workflows.

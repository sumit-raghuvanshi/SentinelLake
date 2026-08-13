# SentinelLake

SentinelLake is a local cyber threat-intelligence data pipeline built with Python, PostgreSQL, Docker, and Apache Airflow.

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
- Orchestrates the workflow with an Apache Airflow DAG
- Runs automated unit tests through GitHub Actions

## Pipeline flow

```text
Apache Airflow schedule / manual trigger
        |
        v
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
Technology
Python 3
PostgreSQL 18
Docker and Docker Compose
Apache Airflow 3.1.7
psycopg 3
unittest
GitHub Actions
Project structure
data/demo_feeds/              Fictional input threat feeds
dags/                         Apache Airflow DAG definitions
docs/                         Architecture and data dictionary
sql/                          PostgreSQL schema migrations
src/sentinellake/             Pipeline source code
tests/                        Automated tests
Dockerfile                    Application container image
Dockerfile.airflow            Airflow container image
docker-compose.yml            Local application, database, and Airflow services
run_resilient_pipeline.py     Pipeline runner with controlled retry
run_incremental_check.py      Incremental IOC classifier and history writer
run_observability_report.py   Pipeline metric report generator
run_health_check.py           Health check and incident recorder
load_warehouse.py             Load latest pipeline result into PostgreSQL
Docker quick start
Docker Desktop must be running.
Start the PostgreSQL database and complete one-time application workflow:
docker compose up --build
The app container exits with code 0 after the workflow completes. This is expected. PostgreSQL remains available at port 5433.
Run tests inside Docker:
docker compose run --rm app python -m unittest discover -v
Stop Docker services:
docker compose down
Airflow orchestration
Start the local Airflow service:
docker compose up -d --build airflow
Open the Airflow UI:
http://localhost:8080
The local Airflow administrator password is generated during first startup. Retrieve it locally:
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated
Do not commit or share this password.
The DAG is named:
sentinellake_threat_intelligence_pipeline
It is scheduled daily at 07:00 and runs these dependent tasks:
ingest_and_validate
        |
incremental_processing
        |
generate_observability
        |
health_check
        |
load_warehouse
Each task has up to two Airflow-managed retries. The ingestion task also uses the project’s controlled retry logic for transient failures.
Local setup
Create and activate a virtual environment:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Install dependencies:
python -m pip install -r requirements.txt
Create a PostgreSQL database named sentinellake, then apply migrations:
psql -h localhost -U postgres -d sentinellake -f sql\001_create_warehouse.sql
psql -h localhost -U postgres -d sentinellake -f sql\002_add_incremental_processing.sql
psql -h localhost -U postgres -d sentinellake -f sql\003_add_ioc_change_history.sql
psql -h localhost -U postgres -d sentinellake -f sql\004_add_pipeline_incidents.sql
The local default connection is:
postgresql://postgres@localhost:5432/sentinellake
You can override it with the SENTINELLAKE_DATABASE_URL environment variable. Never commit a real database password.
Run locally
python run_resilient_pipeline.py
python run_incremental_check.py
python run_observability_report.py
python run_health_check.py
python load_warehouse.py
Run tests
python -m unittest discover -v
Current limitations
Uses local fictional demo feeds; it does not fetch live threat-intelligence feeds.
Airflow runs locally in standalone mode with its local metadata store; it is not a production or high-availability Airflow deployment.
PostgreSQL is local; cloud deployment is not implemented yet.
Retry is limited to transient connection, file-system, and timeout errors.
It does not currently provide an API, dashboard, Kafka, Spark, AWS S3, or cloud data warehouse.
Documentation
[Architecture](docs/architecture.md)
[Data dictionary](docs/data_dictionary.md)
[Warehouse schema](sql/001_create_warehouse.sql)
License
This project is for learning and portfolio demonstration.
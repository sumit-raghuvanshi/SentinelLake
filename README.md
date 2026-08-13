```markdown
# 🛡️ SentinelLake

SentinelLake is a local cyber threat-intelligence data pipeline built with Python, PostgreSQL, Docker, Apache Airflow, and PySpark.

It ingests fictional demonstration threat feeds, converts records into one common IOC (Indicator of Compromise) format, validates data quality, quarantines invalid records, consolidates duplicate IOCs, tracks incremental changes, archives run-scoped data-lake outputs, and saves results in a PostgreSQL warehouse.

> **Note:** This is a learning project. The included feeds are fictional and are not live threat intelligence.

---

## 📋 Table of Contents
- [Features](#-features)
- [Pipeline Flow](#-pipeline-flow)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Local Data Lake](#-local-data-lake)
- [Getting Started: Docker](#-getting-started-docker)
- [PySpark Analytics](#-pyspark-analytics)
- [Airflow Orchestration](#-airflow-orchestration)
- [Local Development Setup](#-local-development-setup)
- [Current Limitations](#-current-limitations)
- [Documentation & License](#-documentation--license)
- [Author & Disclaimer](#-author--disclaimer)

---

## ✨ Features

- **Multi-format Ingestion:** Ingests CSV and JSON threat-feed files.
- **Normalization:** Converts different source formats into a canonical IOC record.
- **Strict Validation:** Validates IPv4 addresses, domain names, timestamps, and confidence scores. Sends invalid records to a quarantine dataset with a reason.
- **Deduplication:** Deduplicates accepted IOCs across sources while preserving source evidence and calculating source counts.
- **State Tracking:** Tracks each IOC as `new`, `changed`, or `unchanged`.
- **Historical Snapshots:** Stores immutable snapshots for new and changed IOCs.
- **Data Lake Archiving:** Archives raw feed copies and pipeline outputs into local data-lake zones.
- **Data Warehousing:** Loads accepted IOCs, quarantined records, and pipeline runs into PostgreSQL.
- **Observability:** Calculates data-quality, quarantine, and deduplication metrics. Detects and stores low-volume and high-quarantine-rate incidents.
- **Resiliency:** Retries transient pipeline failures up to three times.
- **Flexible Execution:** Runs locally via scripts or through Docker Compose.
- **Orchestration & CI/CD:** Orchestrates the Python workflow with an Apache Airflow DAG and runs automated unit tests through GitHub Actions.
- **Big Data Processing:** Runs a PySpark analytics job over curated IOC data.

---

## 🔄 Pipeline Flow

```text
Apache Airflow schedule / manual trigger
        |
        v
Demo CSV / JSON feeds
        |
        v
Raw data-lake archive
        |
        v
Ingestion and normalization
        |
        v
Validation -----> Quarantine data-lake zone
        |
        v
Deduplication and consolidation
        |
        v
Curated data-lake zone + incremental IOC history
        |
        +--------------------> PySpark IOC analytics
        |
        v
PostgreSQL warehouse
        |
        v
Observability metrics + health checks + controlled retry

```

---

## 💻 Technology Stack

* **Language:** Python 3
* **Database:** PostgreSQL 18
* **Containerization:** Docker and Docker Compose
* **Orchestration:** Apache Airflow 3.1.7
* **Big Data Analytics:** Apache Spark 4.1.2 / PySpark
* **Database Adapter:** psycopg 3
* **Testing:** `unittest`
* **CI/CD:** GitHub Actions

---

## 📂 Project Structure

```text
.
├── data/demo_feeds/            # Fictional input threat feeds
├── dags/                       # Apache Airflow DAG definitions
├── docs/                       # Architecture and data dictionary
├── spark_jobs/                 # PySpark analytics jobs
├── sql/                        # PostgreSQL schema migrations
├── src/sentinellake/           # Pipeline source code
├── tests/                      # Automated tests
├── Dockerfile                  # Application container image
├── Dockerfile.airflow          # Airflow container image
├── docker-compose.yml          # Local app, database, Airflow, and Spark services
├── run_resilient_pipeline.py   # Pipeline runner with retry and data-lake archiving
├── run_incremental_check.py    # Incremental IOC classifier and history writer
├── run_observability_report.py # Pipeline metric report generator
├── run_health_check.py         # Health check and incident recorder
└── load_warehouse.py           # Load latest pipeline result into PostgreSQL

```

---

## 🗄️ Local Data Lake

Each successful resilient pipeline run creates a timestamped local archive to preserve the raw input and output of each run for local auditing and reprocessing:

```text
runtime/data_lake/
├── raw/<run-id>/        # Original CSV and JSON feed copies
├── validated/<run-id>/  # Validation summary
├── quarantine/<run-id>/ # Invalid IOC records
└── curated/<run-id>/    # Accepted deduplicated IOCs and pipeline summary

```

---

## 🐳 Getting Started: Docker

*Prerequisite: Docker Desktop must be running.*

**1. Start PostgreSQL and run the one-time application workflow:**

```bash
docker compose up --build

```

> *Note: The app container will exit with code 0 after the workflow completes. This is expected behavior. PostgreSQL will remain available at port `5433`.*

**2. Run tests inside Docker:**

```bash
docker compose run --rm app python -m unittest discover -v

```

**3. Stop Docker services:**

```bash
docker compose down

```

---

## ⚡ PySpark Analytics

Run the Spark job after the pipeline has created `runtime/latest_run/accepted_iocs.json`:

```bash
docker compose run --rm spark-analytics

```

The Spark job reads curated accepted IOCs and writes these local analytics datasets:

```text
runtime/spark_analytics/
├── ioc_type_counts/
├── threat_category_counts/
└── summary/

```

**It calculates:**

* IOC counts by type
* IOC counts by threat category
* Unique IOC count
* Average confidence score
* Total source observations

> *Note: The job uses Spark local mode inside Docker. It is not a multi-node Spark cluster.*

---

## 🌬️ Airflow Orchestration

**1. Start the local Airflow service:**

```bash
docker compose up -d --build airflow

```

**2. Access the UI:**
Open [http://localhost:8080](http://localhost:8080) in your browser.

**3. Retrieve the administrator password:**
The local Airflow administrator password is generated during the first startup. Retrieve it locally by running:

```bash
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated

```

> ⚠️ **Warning:** Do not commit or share this password.

**DAG Details:**

* **Name:** `sentinellake_threat_intelligence_pipeline`
* **Schedule:** Daily at `07:00 UTC`
* **Task Flow:** `ingest_and_validate` -> `incremental_processing` -> `generate_observability` -> `health_check` -> `load_warehouse`
* *Note: Each task can retry twice through Airflow. The ingestion task also uses the project’s controlled retry logic for transient failures.*

---

## 🛠️ Local Development Setup

**1. Create and activate a virtual environment:**

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

```

**2. Install dependencies:**

```bash
python -m pip install -r requirements.txt

```

**3. Setup the Database:**
Create a PostgreSQL database named `sentinellake`, then apply the migrations in order:

```bash
psql -h localhost -U postgres -d sentinellake -f sql\001_create_warehouse.sql
psql -h localhost -U postgres -d sentinellake -f sql\002_add_incremental_processing.sql
psql -h localhost -U postgres -d sentinellake -f sql\003_add_ioc_change_history.sql
psql -h localhost -U postgres -d sentinellake -f sql\004_add_pipeline_incidents.sql

```

**4. Run locally:**

```bash
python run_resilient_pipeline.py
python run_incremental_check.py
python run_observability_report.py
python run_health_check.py
python load_warehouse.py

```

**5. Run tests:**

```bash
python -m unittest discover -v

```

---

## 🚧 Current Limitations

* Uses local fictional demo feeds; it does not fetch live threat-intelligence feeds yet.
* The data lake is local filesystem storage; AWS S3 is not implemented yet.
* Airflow runs locally in standalone mode; it is not a production or high-availability Airflow deployment.
* Spark runs locally in one Docker container; it is not a distributed Spark cluster.
* PostgreSQL is local; cloud deployment is not implemented yet.
* Retry is limited to transient connection, file-system, and timeout errors.
* It does not currently provide an API, dashboard, Kafka, AWS S3, or cloud data warehouse integrations.

---

## 📚 Documentation & License

**Documentation:**

* [Architecture](https://www.google.com/search?q=docs/architecture.md)
* [Data Dictionary](https://www.google.com/search?q=docs/data_dictionary.md)
* [Warehouse Schema](https://www.google.com/search?q=sql/001_create_warehouse.sql)

**License:**
This project is for learning and portfolio demonstration purposes.

---

## 👨‍💻 Author & Disclaimer

**Author:** Sumit Raghuvanshi

> **🤖 AI Disclaimer:** *This README file was generated with the assistance of AI because writing all of this out manually is just too much work!*

```

```
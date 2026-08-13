"""Airflow orchestration for the SentinelLake local pipeline."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_DIRECTORY = "/opt/sentinellake"

DATABASE_URL = (
    "postgresql://sentinellake:sentinellake_dev_password"
    "@postgres:5432/sentinellake"
)

COMMON_COMMAND_PREFIX = (
    f"export SENTINELLAKE_DATABASE_URL='{DATABASE_URL}' && "
    f"cd {PROJECT_DIRECTORY} && "
)


with DAG(
    dag_id="sentinellake_threat_intelligence_pipeline",
    description="Scheduled SentinelLake threat-intelligence workflow.",
    start_date=datetime(2026, 8, 13),
    schedule="0 7 * * *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["sentinellake", "threat-intelligence", "data-engineering"],
) as dag:
    ingest_and_validate = BashOperator(
        task_id="ingest_and_validate",
        bash_command=(
            COMMON_COMMAND_PREFIX
            + "python run_resilient_pipeline.py"
        ),
    )

    incremental_processing = BashOperator(
        task_id="incremental_processing",
        bash_command=(
            COMMON_COMMAND_PREFIX
            + "python run_incremental_check.py"
        ),
    )

    generate_observability = BashOperator(
        task_id="generate_observability",
        bash_command=(
            COMMON_COMMAND_PREFIX
            + "python run_observability_report.py"
        ),
    )

    health_check = BashOperator(
        task_id="health_check",
        bash_command=(
            COMMON_COMMAND_PREFIX
            + "python run_health_check.py"
        ),
    )

    load_warehouse = BashOperator(
        task_id="load_warehouse",
        bash_command=(
            COMMON_COMMAND_PREFIX
            + "python load_warehouse.py"
        ),
    )

    (
        ingest_and_validate
        >> incremental_processing
        >> generate_observability
        >> health_check
        >> load_warehouse
    )
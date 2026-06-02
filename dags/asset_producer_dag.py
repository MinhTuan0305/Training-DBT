"""A simple producer DAG that publishes a Dataset event.

Use this DAG to test Asset-based scheduling end-to-end:
1) Trigger this DAG manually.
2) Airflow emits the Dataset event.
3) Consumer DAGs that schedule on this Dataset are triggered.
"""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator


DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# Keep this URI identical to the consumer DAG Dataset URI.
RAW_DBT_INPUT_READY = Dataset("asset://training-dbt/raw-dbt-input-ready")


with DAG(
    dag_id="asset_ready_producer",
    description="Publishes a Dataset event to trigger asset-scheduled dbt DAGs.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["learning", "airflow", "asset", "dataset"],
) as dag:
    publish_raw_ready_asset = EmptyOperator(
        task_id="publish_raw_ready_asset",
        outlets=[RAW_DBT_INPUT_READY],
    )

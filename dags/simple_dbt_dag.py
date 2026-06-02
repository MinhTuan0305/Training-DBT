"""A minimal Airflow DAG that runs a dbt pipeline in order.

This example is intentionally simple for learning purposes:
dbt seed -> dbt run -> dbt test
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.bash import BashOperator


REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", str(REPO_ROOT))
DBT_PROFILES_DIR = os.environ.get("DBT_PROFILES_DIR", str(REPO_ROOT))

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# Asset consumed by this DAG. Another DAG/task should publish this Dataset
# via outlets=[RAW_DBT_INPUT_READY] to trigger this pipeline.
RAW_DBT_INPUT_READY = Dataset("asset://training-dbt/raw-dbt-input-ready")


with DAG(
    dag_id="simple_dbt_pipeline",
    description="A beginner-friendly Airflow DAG that runs dbt seed, run, and test.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule=[RAW_DBT_INPUT_READY],
    catchup=False,
    tags=["learning", "dbt", "airflow"],
) as dag:
    seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f'dbt seed --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
    )

    run_models = BashOperator(
        task_id="dbt_run",
        bash_command=f'dbt run --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
    )

    test_models = BashOperator(
        task_id="dbt_test",
        bash_command=f'dbt test --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
    )

    seed >> run_models >> test_models
"""An Airflow DAG that demonstrates TaskGroup with a dbt pipeline.

In the Airflow Graph view, the tasks are shown as two grouped boxes:
- dbt_build: seed -> run staging -> run marts
- dbt_quality: test staging -> test marts
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup


REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", str(REPO_ROOT))
DBT_PROFILES_DIR = os.environ.get("DBT_PROFILES_DIR", str(REPO_ROOT))

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="task_group_dbt_pipeline",
    description="A beginner-friendly dbt DAG that uses TaskGroup to organize build and test steps.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["learning", "dbt", "airflow", "task-group"],
) as dag:
    start = EmptyOperator(task_id="start")

    with TaskGroup(group_id="dbt_build") as dbt_build:
        seed = BashOperator(
            task_id="dbt_seed",
            bash_command=f'dbt seed --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
        )

        run_staging = BashOperator(
            task_id="dbt_run_staging",
            bash_command=f'dbt run --select staging --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
        )

        run_marts = BashOperator(
            task_id="dbt_run_marts",
            bash_command=f'dbt run --select marts --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
        )

        seed >> run_staging >> run_marts

    with TaskGroup(group_id="dbt_quality") as dbt_quality:
        test_staging = BashOperator(
            task_id="dbt_test_staging",
            bash_command=f'dbt test --select staging --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
        )

        test_marts = BashOperator(
            task_id="dbt_test_marts",
            bash_command=f'dbt test --select marts --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
        )

        test_staging >> test_marts

    end = EmptyOperator(task_id="end")

    start >> dbt_build >> dbt_quality >> end
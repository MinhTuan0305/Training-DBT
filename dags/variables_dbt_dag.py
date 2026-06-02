"""An Airflow DAG that demonstrates using Variables with dbt.

Set the Airflow Variable `dbt_model_scope` in the web UI to `staging` or `marts`.
The DAG prints the chosen value and then runs dbt against that selection.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", str(REPO_ROOT))
DBT_PROFILES_DIR = os.environ.get("DBT_PROFILES_DIR", str(REPO_ROOT))

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


def log_variable_value() -> None:
    selected_scope = Variable.get("dbt_model_scope", default_var="staging")
    print(f"dbt_model_scope={selected_scope}")


with DAG(
    dag_id="variables_dbt_pipeline",
    description="A beginner-friendly dbt DAG that reads an Airflow Variable to choose the model scope.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["learning", "dbt", "airflow", "variables"],
) as dag:
    start = EmptyOperator(task_id="start")

    show_variable = PythonOperator(
        task_id="show_variable",
        python_callable=log_variable_value,
    )

    run_dbt = BashOperator(
        task_id="dbt_run_selected_scope",
        bash_command=(
            'dbt run --select "{{ var.value.dbt_model_scope | default(\'staging\', true) }}" '
            '--project-dir "' + DBT_PROJECT_DIR + '" --profiles-dir "' + DBT_PROFILES_DIR + '"'
        ),
    )

    test_dbt = BashOperator(
        task_id="dbt_test_selected_scope",
        bash_command=(
            'dbt test --select "{{ var.value.dbt_model_scope | default(\'staging\', true) }}" '
            '--project-dir "' + DBT_PROJECT_DIR + '" --profiles-dir "' + DBT_PROFILES_DIR + '"'
        ),
    )

    end = EmptyOperator(task_id="end")

    start >> show_variable >> run_dbt >> test_dbt >> end
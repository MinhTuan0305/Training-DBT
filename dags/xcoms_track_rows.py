from airflow import DAG
import os
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", str(REPO_ROOT))
DBT_PROFILES_DIR = os.environ.get("DBT_PROFILES_DIR", str(REPO_ROOT))

def count_rows(ti):
    #connection tới postgres
    hook = PostgresHook(postgres_conn_id="postgres_default")

    conn = hook.get_conn()
    cursor = conn.cursor()

    #query
    cursor.execute("SELECT COUNT(*) FROM marts.dim_customer_profile_scd2")

    row_count = cursor.fetchone()[0]

    #push xcoms
    ti.xcom_push(key="row_count", value=row_count)

    print(f"Pushed row count: {row_count}")

def print_row_count(ti):
    row_count = ti.xcom_pull(task_ids='push_rows', key='row_count')

    print(f"Pulled row count: {row_count}")

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="xcoms_track_rows",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026,1,1),
    schedule_interval=None,
    catchup=False,
    tags=["xcoms", "rows"]
) as dag:
    
    run_seed_scd2 = BashOperator(
        task_id="run_seed_scd2",
        bash_command=f'dbt seed --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}" --select raw_customer_profile_history'
    )

    run_stg_scd2 = BashOperator(
        task_id="run_stg_scd2",
        bash_command=(
            f'dbt run --select stg_customer_profile_history --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"'
        ),
    )

    run_scd2 = BashOperator(
        task_id="run_scd2",
        bash_command=(
            f'dbt run --select dim_customer_profile_scd2 --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"'
        ),
    )

    push_rows = PythonOperator(
        task_id='push_rows',
        python_callable=count_rows,
        provide_context=True
    )

    print_rows = PythonOperator(
        task_id='print_rows',
        python_callable=print_row_count,
        provide_context=True
    )

    run_seed_scd2 >> run_stg_scd2 >> run_scd2 >> push_rows >> print_rows
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd

@dag(schedule=None, catchup=False)
def check_if_dollar():
    
    @task.branch(task_id="check_if_dollar")
    def check_dollar():
        #connection tới postgres
        hook = PostgresHook(postgres_conn_id="postgres_default")
        conn = hook.get_conn()
        cursor = conn.cursor()

        #query
        cursor.execute("SELECT is_dollar FROM dbt_dev.raw_products2 WHERE is_dollar = true LIMIT 1")

        result = cursor.fetchone()
        if result and result[0] == True:
            return "convert_to_dollar"
        else:
            return "skip_pipeline"
    
    check = check_dollar()

    convert_to_dollar = BashOperator(
        task_id="convert_to_dollar",
        bash_command="dbt run --select stg_product2 --project-dir /opt/airflow/project --profiles-dir /opt/airflow/project/docker")
    
    skip_pipeline = EmptyOperator(
        task_id="skip_pipeline"
    )

    check  >> [convert_to_dollar, skip_pipeline]
check_if_dollar()
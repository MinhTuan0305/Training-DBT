from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json

def task1(**kwargs):
    data={"message": "task 1 completed"}
    kwargs['ti'].xcom_push(key='data_key', value=json.dumps(data))

def task2(**kwargs):
    ti = kwargs['ti']
    received_data = ti.xcom_pull(task_ids='task1', key='data_key')
    data = json.loads(received_data)
    print(f"received data in task 2: {data['message']}")

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="xcoms_practice",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["xcoms", "learning"]
) as dag:
    
    #task 1     
    t1 = PythonOperator(
        task_id='task1',
        python_callable=task1,
        provide_context=True
    )

    #task 2
    t2 = PythonOperator(
        task_id='task2',
        python_callable=task2,
        provide_context=True
    )

t1 >> t2
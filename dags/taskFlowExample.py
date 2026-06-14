from airflow import DAG
from airflow.decorators import task
from airflow.providers.smtp.operators.smtp import EmailOperator
from pendulum import datetime
import requests

@task
def get_ip():
    return requests.get("https://api.ipify.org").text

@task(multiple_outputs=True)
def compose_email(external_ip):
    return{
        "subject":f'Server connected from IP {external_ip}',
        "body": f'Server cua may da duoc ket noi tu IP {external_ip}<br>',
    }

with DAG(
    dag_id="taskflow_example",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["example", "taskflow"],
) as dag:
    email_info = compose_email(get_ip())

    EmailOperator(
        task_id="send_email",
        to="minhtuan032005@gmail.com",
        subject=email_info["subject"],
        html_content=email_info["body"],
        conn_id="smtp_default",
    )
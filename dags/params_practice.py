from airflow import DAG
from airflow.decorators import task
from airflow.models.param import Param

from pendulum import datetime

with DAG(
    "params_practice",
    start_date=datetime(2026, 1, 1),
    params={
        "my_int_param": Param(42, type="integer", minimum=0, maximum=100, description="An integer parameter"),
        "my_str_param": Param("hello", type="string", description="A string parameter"),
        "multi_type_param": Param("option1", type=["string", "integer"], description="A parameter that can be either string or integer"),
        "enum_param": Param("option1", type="string", enum=["option1", "option2", "option3"], description="A parameter that must be one of the specified options")
    }
) as dag:

    @task
    def print_params(**context):
        print(f"Integer parameter: {context['my_int_param']}")
        print(f"String parameter: {context['my_str_param']}")
        print(f"Multi-type parameter: {context['multi_type_param']}")
        print(f"Enum parameter: {context['enum_param']}")

    print_params()
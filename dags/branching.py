from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from airflow.utils.edgemodifier import Label

import random

@dag(schedule=None, catchup=False)
def branch_example():

    run_this_first = EmptyOperator(task_id="run_this_first")

    options = ["branch_a", "branch_b"]

    @task.branch(task_id="branching")
    def random_choice():
        return random.choice(options)

    branch = random_choice()

    join = EmptyOperator(
        task_id="join",
        trigger_rule="none_failed_min_one_success"
    )

    run_this_first >> branch

    for option in options:

        t = EmptyOperator(task_id=option)

        follow = EmptyOperator(
            task_id=f"follow_{option}"
        )

        branch >> Label(option) >> t >> follow >> join

branch_example()
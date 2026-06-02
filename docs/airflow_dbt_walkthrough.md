# Walkthrough: Airflow DAG with TaskGroup and dbt

This note explains the example in `dags/task_group_dbt_dag.py` and how it differs from the linear version in `dags/simple_dbt_dag.py`.

## What the DAG does

The DAG splits the dbt workflow into two TaskGroups:

1. `dbt_build`
2. `dbt_quality`

Inside the first group, the tasks run in order:

- `dbt seed`
- `dbt run --select staging`
- `dbt run --select marts`

Inside the second group, the tests run in order:

- `dbt test --select staging`
- `dbt test --select marts`

## What TaskGroup changes in Airflow

TaskGroup does not change the runtime behavior by itself. It changes how Airflow organizes the graph:

- the UI shows each group as one collapsible box
- related tasks are easier to scan
- large DAGs become easier to maintain

In the Graph view, you will see `start -> dbt_build -> dbt_quality -> end`.

## Key parts of the DAG

### `dag_id`

`task_group_dbt_pipeline` is the name Airflow uses to identify this example.

### `TaskGroup`

The code uses `with TaskGroup(group_id="dbt_build")` and `with TaskGroup(group_id="dbt_quality")` to group tasks.

### `EmptyOperator`

`start` and `end` are simple placeholders that make the overall flow clearer in the graph.

### `start_date`, `schedule`, and `catchup`

These are kept simple for learning:

- `start_date=datetime(2026, 1, 1)` gives Airflow a fixed reference point
- `schedule="@daily"` means Airflow treats it as a daily DAG
- `catchup=False` prevents backfilling old runs when the DAG is enabled

## How dbt is called

Each task uses `BashOperator`, which runs a shell command.

The command pattern is:

```bash
dbt <command> --project-dir "<repo_root>" --profiles-dir "<repo_root>"
```

The DAG calculates `REPO_ROOT` with `Path(__file__).resolve().parents[1]`, so it can find the dbt project relative to the DAG file instead of relying on a hard-coded path.

## How to run the example

If you are using the Docker setup from this repo:

```bash
docker compose build
docker compose up airflow-init
docker compose up -d
```

Open the Airflow UI at:

```text
http://localhost:8080
```

Then trigger the TaskGroup example manually:

```bash
docker compose exec airflow-webserver airflow dags trigger task_group_dbt_pipeline
```

If you want to compare it with the simpler linear example, trigger:

```bash
docker compose exec airflow-webserver airflow dags trigger simple_dbt_pipeline
```

## What to look for in the UI

Open the DAG in Graph view and expand the groups. You should see that:

- `dbt_build` contains the seed and run steps
- `dbt_quality` contains the test steps
- the groups are still just normal tasks underneath, only visually organized

## If you want to extend it later

Good next steps are:

- add a `dbt docs generate` task in its own group
- add Airflow Connections for dbt configuration
- split staging and marts work into separate TaskGroups for larger projects
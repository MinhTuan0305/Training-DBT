# Walkthrough: Airflow Variables with dbt

This note explains the example in `dags/variables_dbt_dag.py` and how to try it in the Airflow web UI.

## What the DAG does

The DAG reads one Airflow Variable named `dbt_model_scope` and uses it to decide which dbt selection to run.

If the variable is set to `staging`, the DAG runs:

- `dbt run --select staging`
- `dbt test --select staging`

If the variable is set to `marts`, the DAG runs:

- `dbt run --select marts`
- `dbt test --select marts`

If the variable does not exist yet, the DAG falls back to `staging`.

## Why this is useful for learning

Variables let you change behavior without editing code.

That makes them useful for:

- environment-specific settings
- simple feature switches
- reusing one DAG across multiple model scopes

## What to look at in the UI

In Airflow, you can inspect this example in two places:

- Admin -> Variables, where you create or edit `dbt_model_scope`
- the DAG graph and task logs, where you can see the selected value being used

## Key parts of the DAG

### `Variable.get`

The Python task calls `Variable.get("dbt_model_scope", default_var="staging")` and prints the result.

### Jinja template access

The Bash tasks use `{{ var.value.dbt_model_scope | default('staging', true) }}` so the value is read when the task runs.

### Task flow

The graph is simple:

`start -> show_variable -> dbt_run_selected_scope -> dbt_test_selected_scope -> end`

That keeps the example easy to follow while still showing that the variable changes behavior.

## How to try it

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

Then create the variable:

1. Open `Admin`
2. Choose `Variables`
3. Add `dbt_model_scope`
4. Set the value to `staging` or `marts`

After that, trigger the DAG:

```bash
docker compose exec airflow-webserver airflow dags trigger variables_dbt_pipeline
```

Open the task logs for `show_variable` to see the selected value, then compare the dbt commands that ran.

## Good next experiments

- Change `dbt_model_scope` from `staging` to `marts` and rerun the DAG
- Remove the variable and confirm the default value is used
- Add a second variable such as `dbt_extra_args` and pass it into the Bash command
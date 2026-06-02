# Docker Setup for Airflow + dbt

This guide explains the Docker-based setup added to this project, how to start it, and what each command does.

## What was added

- `Dockerfile` to build an Airflow image with `dbt-postgres` installed.
- `docker-compose.yml` to run Airflow and its metadata database.
- `docker/profiles.yml` to give dbt container-friendly database settings.
- `dags/simple_dbt_dag.py` for the linear dbt example.
- `dags/task_group_dbt_dag.py` for the TaskGroup example.
- `dags/variables_dbt_dag.py` for the Airflow Variables example.

## Why Docker is useful here

Airflow does not run natively on Windows in a reliable way, so Docker gives you a Linux environment that is much closer to how Airflow is usually deployed.

It also keeps the Airflow installation separate from your local Python environment.

## Folder layout used by the container

- `/opt/airflow/dags` contains the DAG file.
- `/opt/airflow/project` contains the dbt project.
- `/opt/airflow/project/docker` contains the Docker-specific `profiles.yml`.

## Main commands

### Build the image

```bash
docker compose build
```

This creates the custom Airflow image from `Dockerfile` and installs `dbt-postgres` inside it.

### Initialize Airflow

```bash
docker compose up airflow-init
```

This prepares the Airflow metadata database and creates the admin user defined in the compose file.

### Start the services

```bash
docker compose up -d
```

This starts Airflow in the background:

- `airflow-db` stores Airflow metadata
- `airflow-webserver` serves the UI
- `airflow-scheduler` schedules and launches tasks

### Open the UI

```text
http://localhost:8080
```

This opens the Airflow web interface where you can see the DAG and trigger it manually.

### Trigger the DAG manually

```bash
docker compose exec airflow-webserver airflow dags trigger simple_dbt_pipeline
```

This tells Airflow to run the DAG immediately instead of waiting for the schedule.

For the TaskGroup example, trigger this DAG instead:

```bash
docker compose exec airflow-webserver airflow dags trigger task_group_dbt_pipeline
```

For the Variables example, trigger this DAG:

```bash
docker compose exec airflow-webserver airflow dags trigger variables_dbt_pipeline
```

### List DAGs

```bash
docker compose exec airflow-webserver airflow dags list
```

This shows which DAGs Airflow has discovered inside the mounted `dags/` folder.

### View logs

```bash
docker compose logs -f airflow-scheduler
```

This streams scheduler logs so you can see when the DAG is picked up and when tasks are queued.

### Stop everything

```bash
docker compose down
```

This stops the containers but keeps the volumes.

### Remove everything including data

```bash
docker compose down -v
```

This stops the containers and also removes the volumes, including the Airflow metadata database.

## What the DAG tasks do

The linear example runs these dbt commands in order:

1. `dbt seed` to load CSV files from `seeds/` into the database.
2. `dbt run` to build the dbt models.
3. `dbt test` to validate the built models.

## Why the environment variables matter

`dags/simple_dbt_dag.py` reads:

- `DBT_PROJECT_DIR`
- `DBT_PROFILES_DIR`

In Docker, these are set to container paths so the Bash tasks can find the dbt project and its profile.

## Important note about the database host

Inside Docker, `localhost` points to the container itself, not to your Windows host.

That is why `docker/profiles.yml` uses `host.docker.internal` by default. On Docker Desktop this usually points back to the host machine where your PostgreSQL instance is running.

If your database runs somewhere else, adjust `DBT_HOST`, `DBT_PORT`, `DBT_USER`, `DBT_PASSWORD`, and `DBT_DBNAME`.

## Suggested first run order

```bash
docker compose build
docker compose up airflow-init
docker compose up -d
docker compose exec airflow-webserver airflow dags trigger simple_dbt_pipeline
```

That sequence builds the image, prepares Airflow, starts the services, and then launches the DAG.
# Asset-based Scheduling (Quick Demo)

Project now includes:
- Producer DAG: `asset_ready_producer`
- Consumer DAG: `simple_dbt_pipeline`
- Shared asset URI: `asset://training-dbt/raw-dbt-input-ready`

## How It Works

1. Run `asset_ready_producer` manually.
2. Task `publish_raw_ready_asset` emits a Dataset event.
3. Airflow triggers `simple_dbt_pipeline` because it schedules on that Dataset.

## Quick Test

1. In Airflow UI, trigger DAG `asset_ready_producer`.
2. Wait for `publish_raw_ready_asset` to succeed.
3. Check DAG `simple_dbt_pipeline` for an auto-created run.

This pattern is useful when you want downstream pipelines to start only after an upstream data asset is ready.

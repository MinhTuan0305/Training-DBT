{% snapshot customer_profile_snapshot %}

{{ config(
  target_schema='snapshots',
  unique_key='customer_id',
  strategy='check',
  check_cols=['full_name', 'email', 'status']
) }}

select
    customer_id,
    full_name,
    email,
    status,
    updated_at
from {{ ref('stg_customer_snapshot_source') }}

{% endsnapshot %}

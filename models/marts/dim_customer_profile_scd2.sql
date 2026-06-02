{{ config(
    materialized='table',
    tags=['marts', 'scd2', 'customers']
) }}

{{ scd2_from_source(
    source_relation=ref('stg_customer_profile_history'),
    business_key='customer_id',
    tracked_columns=['full_name', 'email', 'status'],
    effective_from_column='updated_at'
) }}

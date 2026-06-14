{{ config(
    materialized='view',
    tags=['staging', 'scd2', 'customers', 'history']
) }}

with source as (
    select * from {{ ref('raw_customer_profile_history') }}
),

renamed as (
    select
        customer_id,
        full_name,
        email,
        status,
        updated_at::timestamp as updated_at
    from source
    where customer_id is not null
      and updated_at is not null
)

select * from renamed

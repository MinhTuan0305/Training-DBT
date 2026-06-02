{{ config(
    materialized='view',
    tags=['staging', 'snapshot', 'customers']
) }}

with source as (
    select * from {{ ref('raw_customer_snapshot') }}
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

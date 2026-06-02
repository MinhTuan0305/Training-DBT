{{ config(
    materialized='view',
    tags=['staging', 'customers']
) }}

with source as (
    select * from {{ source('raw', 'raw_customers') }}
),

renamed as (
    select
        customer_id,
        first_name,
        last_name,
        first_name || ' ' || last_name  as full_name,
        email,
        created_at::timestamp           as created_at,
        status
    from source
    where customer_id is not null
)

select * from renamed

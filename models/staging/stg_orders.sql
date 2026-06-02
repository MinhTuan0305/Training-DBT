{{ config(
    materialized='view',
    tags=['staging', 'orders']
) }}

with source as (
    select * from {{ source('raw', 'raw_orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        product_id,
        {{ cents_to_dollars('amount_cents') }} as amount_dollars,
        status,
        ordered_at::timestamp                  as ordered_at
    from source
    where order_id is not null
      and status in ('pending', 'completed', 'cancelled')
)

select * from renamed

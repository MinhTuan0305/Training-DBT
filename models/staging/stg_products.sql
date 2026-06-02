{{ config(
    materialized='view',
    tags=['staging', 'products']
) }}

with source as (
    select * from {{ source('raw', 'raw_products') }}
),

renamed as (
    select
        product_id,
        product_name,
        category,
        {{ cents_to_dollars('price_cents') }} as price_dollars,
        is_active
    from source
    where product_id is not null
      and is_active = true
)

select * from renamed

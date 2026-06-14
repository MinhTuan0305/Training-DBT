{{ config(
    materialized='view',
    tags=['staging', 'products', 'dollars']
) }}

with source as (
    select * from {{ source('raw', 'raw_products2') }}
),

renamed as(
    select
        product_id,
        product_name,
        category,
        case
            when is_dollar = true then price
            else {{ cents_to_dollars('price') }}
        end as price_dollars,
        is_active
    from source
    where product_id is not null
      and is_active = true
)

select * from renamed
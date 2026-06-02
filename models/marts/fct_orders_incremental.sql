{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='order_id',
        tags=['marts', 'incremental']
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        o.order_id,
        o.customer_id,
        c.full_name,
        o.amount_dollars,
        o.status,
        o.ordered_at
    from orders o
    left join customers c using (customer_id)

    {% if is_incremental() %}
    -- Chỉ load các đơn hàng mới hơn giá trị lớn nhất đang có trong bảng
    where o.ordered_at > (select max(ordered_at) from {{ this }})
    {% endif %}
)

select * from final



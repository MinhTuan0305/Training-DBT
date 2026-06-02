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
)

select * from final

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_orders as (
    select
        customer_id,
        count(order_id)      as total_orders,
        sum(amount_dollars)  as total_spent,
        min(ordered_at)      as first_order_at,
        max(ordered_at)      as last_order_at
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.full_name,
        c.email,
        c.status,
        coalesce(co.total_orders, 0)  as total_orders,
        coalesce(co.total_spent, 0)   as total_spent,
        co.first_order_at,
        co.last_order_at
    from customers c
    left join customer_orders co using (customer_id)
)

select * from final

-- Singular test: assert_positive_order_amounts
-- Validates: Property 9 (Requirements 7.4)
--
-- This test FAILS if any row is returned.
-- DBT convention: a singular test fails when the query returns any rows.
--
-- Business rule: All orders must have a positive amount_dollars value.
-- No order should have amount_dollars <= 0.

select
    order_id,
    amount_dollars
from {{ ref('fct_orders') }}
where amount_dollars <= 0

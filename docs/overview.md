{% docs model_overview %}

## DBT Practice Project — Data Pipeline Overview

Project này xây dựng một data pipeline hoàn chỉnh theo mô hình ELT (Extract, Load, Transform) sử dụng DBT và PostgreSQL, với domain **E-commerce**.

### Luồng dữ liệu

```
Seeds (CSV) → Raw Tables → Staging Layer (VIEW) → Mart Layer (TABLE)
```

1. **Seeds** — Ba file CSV (`raw_customers`, `raw_orders`, `raw_products`) được load vào PostgreSQL bằng `dbt seed`.

2. **Staging Layer** — Ba models làm sạch và chuẩn hóa dữ liệu từ raw tables:
   - `stg_customers` — chuẩn hóa thông tin khách hàng, tạo cột `full_name`
   - `stg_orders` — chuyển đổi `amount_cents` → `amount_dollars`, lọc status hợp lệ
   - `stg_products` — chuyển đổi `price_cents` → `price_dollars`, lọc sản phẩm active

3. **Mart Layer** — Hai models tổng hợp dữ liệu phục vụ báo cáo:
   - `fct_orders` — fact table JOIN orders với customers
   - `dim_customers` — dimension table với aggregated metrics (total_orders, total_spent)

### Macros

- `cents_to_dollars(column_name, precision=2)` — chuyển đổi cents sang dollars
- `generate_schema_name(custom_schema_name, node)` — tùy chỉnh tên schema khi deploy
- `limit_data_in_dev(column_name, dev_limit=100)` — giới hạn dữ liệu trong môi trường dev

### Tests

- **Generic tests**: `not_null`, `unique`, `accepted_values`, `relationships` khai báo trong `schema.yml`
- **Singular test**: `assert_positive_order_amounts.sql` — kiểm tra tất cả đơn hàng có giá trị dương
- **Unit tests**: `pytest tests/unit/` — kiểm tra macro logic và code patterns (không cần database)

{% enddocs %}

{% docs stg_customers_overview %}

Staging model cho bảng khách hàng. Đọc từ `raw_customers` qua `source()`, thực hiện:
- Cast `created_at` sang timestamp
- Tạo cột `full_name` = `first_name || ' ' || last_name`
- Lọc bỏ records có `customer_id IS NULL`

Materialized as **VIEW**.

{% enddocs %}

{% docs stg_orders_overview %}

Staging model cho bảng đơn hàng. Đọc từ `raw_orders` qua `source()`, thực hiện:
- Chuyển đổi `amount_cents` → `amount_dollars` bằng macro `cents_to_dollars()`
- Cast `ordered_at` sang timestamp
- Lọc bỏ records có `order_id IS NULL` hoặc `status` không hợp lệ

Materialized as **VIEW**.

{% enddocs %}

{% docs fct_orders_overview %}

Fact table tổng hợp đơn hàng. JOIN `stg_orders` với `stg_customers` để bổ sung thông tin `full_name`.
Mỗi row đại diện cho một đơn hàng.

Materialized as **TABLE**.

{% enddocs %}

{% docs dim_customers_overview %}

Dimension table khách hàng với aggregated metrics. LEFT JOIN `stg_customers` với aggregation từ `stg_orders`.
Mỗi row đại diện cho một khách hàng, kèm theo tổng số đơn hàng và tổng chi tiêu.
Khách hàng chưa có đơn hàng sẽ có `total_orders = 0` và `total_spent = 0`.

Materialized as **TABLE**.

{% enddocs %}

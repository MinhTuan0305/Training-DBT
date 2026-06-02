# Implementation Plan: DBT Practice Project

## Overview

Xây dựng một DBT practice project hoàn chỉnh kết nối PostgreSQL, bao gồm seeds, staging models, mart models, macros, tests (generic, singular, property-based), và documentation. Các task được tổ chức theo thứ tự dependency: cấu hình → seeds → staging → marts → macros → tests → documentation.

## Tasks

- [x] 1. Khởi tạo cấu hình project và cấu trúc thư mục
  - Tạo file `dbt_project.yml` với đầy đủ các trường bắt buộc: `name`, `version`, `profile`, `model-paths`, `seed-paths`, `macro-paths`, `test-paths`, `analysis-paths`, `docs-paths`, `target-path`, `clean-targets`
  - Cấu hình `models.dbt_practice_project.staging.+materialized: view` và `models.dbt_practice_project.marts.+materialized: table`
  - Tạo file `.gitignore` loại trừ `target/` và `profiles.yml`
  - Tạo file `profiles.yml` mẫu (đặt tại root project để tham khảo, không commit) với cấu hình PostgreSQL dùng `env_var()` cho cả `dev` và `prod` target
  - Tạo `README.md` hướng dẫn cài đặt DBT, cấu hình `profiles.yml`, và chạy project lần đầu
  - Tạo cấu trúc thư mục: `models/staging/`, `models/marts/`, `macros/`, `seeds/`, `tests/`, `tests/unit/`, `docs/`, `analyses/`
  - _Requirements: 1.1, 1.2, 1.5, 10.1, 10.3_

- [x] 2. Tạo seed data (CSV files)
  - [x] 2.1 Tạo file `seeds/raw_customers.csv` với ít nhất 10 rows, các cột: `customer_id`, `first_name`, `last_name`, `email`, `created_at`, `status`
    - Đảm bảo có đa dạng giá trị `status` (`active`, `inactive`) để test `accepted_values`
    - _Requirements: 2.1_

  - [x] 2.2 Tạo file `seeds/raw_orders.csv` với ít nhất 15 rows, các cột: `order_id`, `customer_id`, `product_id`, `amount_cents`, `status`, `ordered_at`
    - Đảm bảo `customer_id` tham chiếu đến `raw_customers`, `status` chỉ gồm `pending`, `completed`, `cancelled`
    - Đảm bảo tất cả `amount_cents > 0`
    - _Requirements: 2.1_

  - [x] 2.3 Tạo file `seeds/raw_products.csv` với ít nhất 5 rows, các cột: `product_id`, `product_name`, `category`, `price_cents`, `is_active`
    - _Requirements: 2.1_

  - [x] 2.4 Tạo file `seeds/schema.yml` khai báo column types và descriptions cho cả 3 seed tables
    - Khai báo `column_types` cho các cột date/timestamp và boolean
    - Thêm `description` cho từng table và từng column
    - _Requirements: 2.3_

- [x] 3. Khai báo Sources và tạo Staging Models
  - [x] 3.1 Tạo file `models/staging/schema.yml` với source block `raw` tham chiếu 3 bảng seed
    - Khai báo `loaded_at_field` và `freshness` cho source `raw_orders`
    - Thêm `description` cho từng source table và các cột quan trọng (PK, FK)
    - Khai báo generic tests `not_null` + `unique` trên primary keys của source tables
    - _Requirements: 3.1, 3.4_

  - [x] 3.2 Tạo macro `macros/cents_to_dollars.sql`
    - Implement macro `cents_to_dollars(column_name, precision=2)` trả về `round(column_name / 100.0, precision)`
    - Thêm docstring mô tả mục đích, tham số, và ví dụ sử dụng
    - _Requirements: 6.2, 6.7_

  - [x] 3.3 Tạo file `models/staging/stg_customers.sql`
    - Dùng `{{ source('raw', 'raw_customers') }}` để tham chiếu raw table
    - Rename columns, cast `created_at` sang timestamp, filter `customer_id is not null`
    - Tạo cột `full_name` bằng cách concat `first_name` và `last_name`
    - _Requirements: 3.2, 4.1, 4.3, 4.5_

  - [x] 3.4 Tạo file `models/staging/stg_orders.sql`
    - Dùng `{{ source('raw', 'raw_orders') }}` để tham chiếu raw table
    - Dùng macro `{{ cents_to_dollars('amount_cents') }}` để tạo cột `amount_dollars`
    - Cast `ordered_at` sang timestamp, filter `order_id is not null` và `status in ('pending', 'completed', 'cancelled')`
    - _Requirements: 3.2, 4.1, 4.3, 4.5, 6.2_

  - [x] 3.5 Tạo file `models/staging/stg_products.sql`
    - Dùng `{{ source('raw', 'raw_products') }}` để tham chiếu raw table
    - Dùng macro `{{ cents_to_dollars('price_cents') }}` để tạo cột `price_dollars`
    - Filter `is_active = true` và `product_id is not null`
    - _Requirements: 3.2, 4.1, 4.3, 4.5_

  - [x] 3.6 Bổ sung model documentation vào `models/staging/schema.yml`
    - Thêm `description` cho cả 3 staging models
    - Thêm `description` cho các cột PK và FK
    - Khai báo generic tests: `not_null` + `unique` trên PKs, `accepted_values` cho `stg_orders.status`, `relationships` từ `stg_orders.customer_id` → `stg_customers.customer_id`
    - _Requirements: 7.1, 7.2, 7.3, 9.1, 9.2_

  - [x] 3.7 Viết property test cho Property 1: staging models dùng `source()`
    - **Property 1: Staging models chỉ tham chiếu raw data qua `source()`**
    - **Validates: Requirements 3.2, 4.5**
    - Tạo file `tests/unit/test_code_patterns.py`, implement `test_staging_models_use_source()`
    - Kiểm tra tất cả file `.sql` trong `models/staging/` đều chứa `{{ source(` và không chứa hard-coded schema name
    - _Requirements: 3.2, 4.5_

- [x] 4. Tạo Macros còn lại
  - [x] 4.1 Tạo macro `macros/generate_schema_name.sql`
    - Implement logic: nếu `custom_schema_name is none` → trả về `target.schema`; ngược lại → trả về `custom_schema_name | trim`
    - Thêm docstring mô tả mục đích và ví dụ
    - _Requirements: 6.3, 6.7_

  - [x] 4.2 Tạo macro `macros/limit_data_in_dev.sql`
    - Implement logic: khi `target.name == 'dev'` → sinh `WHERE column_name >= current_date - interval 'dev_limit days'`; ngược lại → sinh chuỗi rỗng
    - Thêm docstring mô tả mục đích, tham số, và ví dụ
    - _Requirements: 6.4, 6.7_

  - [x] 4.3 Tạo file `macros/properties.yml` khai báo documentation cho cả 3 macros
    - _Requirements: 6.1, 6.7_

  - [x] 4.4 Viết property test cho Property 4: `cents_to_dollars` correctness
    - **Property 4: `cents_to_dollars` tính toán đúng**
    - **Validates: Requirements 6.2**
    - Tạo file `tests/unit/test_macros.py`, implement `test_cents_to_dollars_property()` dùng Hypothesis
    - Test với `st.integers(min_value=0, max_value=10_000_000)`, assert `result == round(cents / 100.0, 2)`
    - _Requirements: 6.2_

  - [x] 4.5 Viết property test cho Property 5: `generate_schema_name` logic
    - **Property 5: `generate_schema_name` trả về đúng schema**
    - **Validates: Requirements 6.3**
    - Implement `test_generate_schema_name_property()` trong `tests/unit/test_macros.py` dùng Hypothesis
    - Test với `st.one_of(st.none(), st.text(...))` cho `custom_schema` và `st.text(...)` cho `target_schema`
    - _Requirements: 6.3_

  - [x] 4.6 Viết property test cho Property 6: `limit_data_in_dev` target-aware
    - **Property 6: `limit_data_in_dev` chỉ sinh WHERE clause trong môi trường dev**
    - **Validates: Requirements 6.4**
    - Implement `test_limit_data_in_dev_property()` trong `tests/unit/test_macros.py` dùng Hypothesis
    - Test với `st.sampled_from(['dev', 'prod', 'staging', 'ci'])` cho `target_name`
    - _Requirements: 6.4_

- [x] 5. Checkpoint — Kiểm tra staging layer
  - Đảm bảo tất cả unit tests trong `tests/unit/test_code_patterns.py` và `tests/unit/test_macros.py` pass.
  - Hỏi người dùng nếu có thắc mắc trước khi tiếp tục.

- [x] 6. Tạo Mart Models
  - [x] 6.1 Tạo file `models/marts/fct_orders.sql`
    - Dùng `{{ ref('stg_orders') }}` và `{{ ref('stg_customers') }}` để tham chiếu staging models
    - Thực hiện LEFT JOIN giữa orders và customers theo `customer_id`
    - Chọn các cột: `order_id`, `customer_id`, `full_name`, `amount_dollars`, `status`, `ordered_at`
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 6.2 Tạo file `models/marts/dim_customers.sql`
    - Dùng `{{ ref('stg_customers') }}` và `{{ ref('stg_orders') }}` để tham chiếu staging models
    - Thực hiện aggregation: `COUNT(order_id)`, `SUM(amount_dollars)`, `MIN(ordered_at)`, `MAX(ordered_at)` GROUP BY `customer_id`
    - LEFT JOIN kết quả aggregation vào customers, dùng `COALESCE` cho customers chưa có đơn hàng
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 6.3 Tạo file `models/marts/schema.yml` với documentation và tests cho mart models
    - Thêm `description` cho cả 2 mart models và các cột PK/FK
    - Khai báo generic tests: `not_null` + `unique` trên `order_id` (fct_orders) và `customer_id` (dim_customers)
    - Khai báo `accepted_values` cho `fct_orders.status`
    - _Requirements: 7.1, 7.2, 9.1, 9.2_

  - [x] 6.4 Viết property test cho Property 2: mart models dùng `ref()`
    - **Property 2: Mart models chỉ tham chiếu models khác qua `ref()`**
    - **Validates: Requirements 5.2**
    - Implement `test_mart_models_use_ref()` trong `tests/unit/test_code_patterns.py`
    - _Requirements: 5.2_

  - [x] 6.5 Viết property test cho Property 3: mart models có aggregation/JOIN
    - **Property 3: Mart models thực hiện aggregation hoặc JOIN**
    - **Validates: Requirements 5.3**
    - Implement `test_mart_models_have_aggregation_or_join()` trong `tests/unit/test_code_patterns.py`
    - Kiểm tra SQL chứa ít nhất một trong: `GROUP BY`, `JOIN`, `SUM(`, `COUNT(`, `AVG(`, `MIN(`, `MAX(`
    - _Requirements: 5.3_

  - [x] 6.6 Viết property test cho Property 14: materialization config đúng theo layer
    - **Property 14: Materialization config đúng theo layer**
    - **Validates: Requirements 4.2, 10.2**
    - Implement `test_materialization_config()` trong `tests/unit/test_code_patterns.py`
    - Đọc `dbt_project.yml`, assert `staging.+materialized == 'view'` và `marts.+materialized == 'table'`
    - _Requirements: 4.2, 10.2_

- [x] 7. Tạo Singular Test và hoàn thiện Tests
  - [x] 7.1 Tạo file `tests/assert_positive_order_amounts.sql`
    - Query trả về các rows trong `{{ ref('fct_orders') }}` có `amount_dollars <= 0`
    - Thêm comment giải thích: test fail nếu query trả về bất kỳ row nào
    - _Requirements: 7.4_

  - [x] 7.2 Tạo file `tests/unit/test_artifacts.py` kiểm tra cấu trúc artifact
    - Implement `test_manifest_required_fields()` — **Property 10: `manifest.json` có đầy đủ required fields** — **Validates: Requirements 8.3**
    - Implement `test_run_results_valid_statuses()` — **Property 11: `run_results.json` chỉ chứa status hợp lệ** — **Validates: Requirements 8.4**
    - _Requirements: 8.3, 8.4_

- [x] 8. Tạo Documentation
  - [x] 8.1 Tạo file `docs/overview.md` với docs block cho model overview
    - Viết docs block `{% docs model_overview %}` mô tả tổng quan về data pipeline
    - Minh họa cách sử dụng docs block trong `schema.yml` với `description: '{{ doc("model_overview") }}'`
    - _Requirements: 9.4_

  - [x] 8.2 Tạo file `docs/reading-artifacts.md` hướng dẫn đọc artifacts
    - Giải thích cấu trúc `manifest.json`: các top-level keys, cấu trúc của một node, cách đọc DAG từ `depends_on`
    - Giải thích cấu trúc `run_results.json`: mảng `results`, các giá trị `status`, cách debug lỗi
    - Giải thích `target/compiled/`: cách đọc SQL đã compile để debug Jinja2
    - _Requirements: 8.6_

  - [x] 8.3 Viết property test cho Property 12: documentation coverage ≥ 80%
    - **Property 12: Documentation coverage cho models**
    - **Validates: Requirements 9.1**
    - Tạo file `tests/unit/test_documentation.py`, implement `test_model_description_coverage()`
    - Đọc tất cả `schema.yml` trong `models/`, tính tỷ lệ models có `description` không rỗng, assert ≥ 80%
    - _Requirements: 9.1_

  - [x] 8.4 Viết property test cho Property 13: PK/FK columns có description
    - **Property 13: PK/FK columns có description**
    - **Validates: Requirements 9.2**
    - Implement `test_pk_fk_columns_have_descriptions()` trong `tests/unit/test_documentation.py`
    - Với mỗi column có test `not_null + unique` (PK) hoặc `relationships` (FK), assert `description` không rỗng
    - _Requirements: 9.2_

- [x] 9. Tạo file cấu hình pytest và hoàn thiện test infrastructure
  - [x] 9.1 Tạo file `tests/unit/conftest.py` với helper functions và fixtures dùng chung
    - Tạo fixture `project_root` trả về đường dẫn gốc của project
    - Tạo helper function `parse_macro_output(macro_name, args)` để test macro logic bằng Python thuần
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 9.2 Tạo file `pytest.ini` hoặc `pyproject.toml` cấu hình pytest
    - Cấu hình `testpaths = ["tests/unit"]`
    - Cấu hình Hypothesis settings: `max_examples = 100`
    - Thêm `requirements.txt` hoặc `pyproject.toml` với dependencies: `pytest`, `hypothesis`, `pyyaml`
    - _Requirements: 6.1_

- [x] 10. Checkpoint cuối — Đảm bảo toàn bộ project hoạt động
  - Đảm bảo tất cả unit tests trong `tests/unit/` pass với `pytest tests/unit/ -v`
  - Đảm bảo cấu trúc thư mục khớp với design document
  - Hỏi người dùng nếu có thắc mắc trước khi kết thúc.

## Notes

- Tasks đánh dấu `*` là optional và có thể bỏ qua để tạo MVP nhanh hơn
- Mỗi task tham chiếu đến requirements cụ thể để đảm bảo traceability
- Các property-based tests dùng thư viện **Hypothesis** (Python) với minimum 100 iterations
- DBT native tests (generic + singular) chạy qua `dbt test` sau khi có database connection
- Unit tests cho macros và code patterns chạy qua `pytest tests/unit/ -v` — không cần database
- Thứ tự chạy đầy đủ: `dbt seed && dbt run && dbt test && pytest tests/unit/ -v`
- `profiles.yml` mẫu dùng `env_var()` — người dùng cần set environment variables trước khi chạy DBT

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1", "2.2", "2.3"] },
    { "id": 1, "tasks": ["2.4", "3.2", "9.2"] },
    { "id": 2, "tasks": ["3.1", "3.3", "3.4", "3.5", "4.1", "4.2", "4.3"] },
    { "id": 3, "tasks": ["3.6", "3.7", "4.4", "4.5", "4.6", "9.1"] },
    { "id": 4, "tasks": ["6.1", "6.2"] },
    { "id": 5, "tasks": ["6.3", "6.4", "6.5", "6.6", "7.1"] },
    { "id": 6, "tasks": ["7.2", "8.1", "8.2"] },
    { "id": 7, "tasks": ["8.3", "8.4"] }
  ]
}
```

# Hướng dẫn đọc DBT Artifacts

Sau mỗi lần chạy lệnh DBT, thư mục `target/` sẽ chứa các file artifact. Đây là nguồn thông tin quan trọng để debug và hiểu pipeline.

## Tổng quan các file artifact

| File | Sinh ra bởi | Mô tả |
|------|-------------|-------|
| `manifest.json` | `dbt compile`, `dbt run`, `dbt test` | Metadata toàn bộ DAG |
| `run_results.json` | `dbt run`, `dbt test`, `dbt seed` | Kết quả thực thi |
| `catalog.json` | `dbt docs generate` | Schema của các bảng trong database |
| `compiled/` | `dbt compile`, `dbt run` | SQL đã render Jinja2 |

---

## `manifest.json`

### Cấu trúc top-level

```json
{
  "metadata": { ... },
  "nodes": { ... },
  "sources": { ... },
  "exposures": {},
  "metrics": {}
}
```

### `metadata`

```json
{
  "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v10/manifest.json",
  "dbt_version": "1.7.0",
  "generated_at": "2024-01-15T10:30:00.000000Z",
  "invocation_id": "abc123-..."
}
```

- `dbt_version` — phiên bản DBT đang dùng
- `generated_at` — thời điểm sinh file
- `invocation_id` — ID duy nhất của lần chạy

### `nodes` — cấu trúc một node

```json
{
  "model.dbt_practice_project.stg_customers": {
    "unique_id": "model.dbt_practice_project.stg_customers",
    "name": "stg_customers",
    "resource_type": "model",
    "depends_on": {
      "nodes": ["source.dbt_practice_project.raw.raw_customers"]
    },
    "config": {
      "materialized": "view",
      "schema": "staging"
    },
    "compiled_code": "with source as (\n    select * from \"dbt_dev\".\"raw_customers\"\n)..."
  }
}
```

- `unique_id` — định danh duy nhất, format: `{resource_type}.{project}.{name}`
- `resource_type` — loại node: `model`, `test`, `seed`, `source`, `snapshot`
- `depends_on.nodes` — danh sách upstream dependencies (đọc DAG từ đây)
- `config.materialized` — cách DBT lưu model: `view`, `table`, `incremental`, `ephemeral`
- `compiled_code` — SQL đã render Jinja2 (chỉ có sau `dbt compile` hoặc `dbt run`)

### Đọc DAG từ `depends_on`

```python
import json

with open('target/manifest.json') as f:
    manifest = json.load(f)

# Xem dependencies của fct_orders
node = manifest['nodes']['model.dbt_practice_project.fct_orders']
print(node['depends_on']['nodes'])
# ['model.dbt_practice_project.stg_orders', 'model.dbt_practice_project.stg_customers']
```

---

## `run_results.json`

### Cấu trúc

```json
{
  "metadata": { ... },
  "results": [
    {
      "unique_id": "model.dbt_practice_project.stg_customers",
      "status": "success",
      "execution_time": 0.45,
      "adapter_response": {
        "rows_affected": 0,
        "_message": "CREATE VIEW"
      },
      "message": "CREATE VIEW",
      "failures": null
    }
  ],
  "elapsed_time": 2.3
}
```

### Các giá trị `status`

| Status | Ý nghĩa |
|--------|---------|
| `success` | Model/seed chạy thành công |
| `error` | Lỗi compile hoặc runtime |
| `skipped` | Bị bỏ qua (do upstream error) |
| `warn` | Cảnh báo (test warn threshold) |
| `pass` | Test pass |
| `fail` | Test fail |

### Debug lỗi từ `run_results.json`

```python
import json

with open('target/run_results.json') as f:
    results = json.load(f)

# Tìm các node bị lỗi
errors = [r for r in results['results'] if r['status'] == 'error']
for err in errors:
    print(f"FAILED: {err['unique_id']}")
    print(f"Message: {err.get('message', 'N/A')}")
```

---

## `target/compiled/`

Thư mục này chứa SQL đã được compile (Jinja2 đã render) cho từng model.

### Cấu trúc thư mục

```
target/compiled/
└── dbt_practice_project/
    └── models/
        ├── staging/
        │   ├── stg_customers.sql
        │   ├── stg_orders.sql
        │   └── stg_products.sql
        └── marts/
            ├── fct_orders.sql
            └── dim_customers.sql
```

### Cách đọc để debug Jinja2

Khi macro hoặc `ref()`/`source()` không hoạt động như mong đợi, đọc file compiled để xem SQL thực tế:

```bash
# Compile trước
dbt compile

# Đọc SQL đã compile của stg_orders
cat target/compiled/dbt_practice_project/models/staging/stg_orders.sql
```

Ví dụ output — macro `cents_to_dollars` đã được render:
```sql
with source as (
    select * from "dbt_dev"."raw_orders"
),
renamed as (
    select
        order_id,
        customer_id,
        product_id,
        round(amount_cents / 100.0, 2) as amount_dollars,  -- macro đã render
        status,
        ordered_at::timestamp as ordered_at
    from source
    where order_id is not null
      and status in ('pending', 'completed', 'cancelled')
)
select * from renamed
```

---

## Workflow debug thực tế

```bash
# 1. Chạy và xem kết quả
dbt run

# 2. Nếu có lỗi, đọc run_results.json
python -c "
import json
with open('target/run_results.json') as f:
    r = json.load(f)
for result in r['results']:
    if result['status'] == 'error':
        print(result['unique_id'], '->', result.get('message'))
"

# 3. Xem SQL đã compile của model bị lỗi
cat target/compiled/dbt_practice_project/models/staging/stg_orders.sql

# 4. Xem DAG dependencies
python -c "
import json
with open('target/manifest.json') as f:
    m = json.load(f)
for name, node in m['nodes'].items():
    if node['resource_type'] == 'model':
        print(node['name'], '->', node['depends_on']['nodes'])
"
```

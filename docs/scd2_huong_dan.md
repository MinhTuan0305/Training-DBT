# Hướng dẫn SCD2 trong DBT

Tài liệu này mô tả macro SCD2 đã được thêm vào project và cách thử thay đổi dữ liệu để nhìn thấy lịch sử thay đổi.

## Mục tiêu

SCD2 dùng để lưu lại lịch sử thay đổi của một thực thể, ví dụ:
- khách hàng đổi email
- khách hàng đổi trạng thái active/inactive
- sản phẩm đổi tên hoặc category

Thay vì ghi đè dòng cũ, SCD2 sẽ tạo thêm một version mới và giữ lại version trước đó với khoảng thời gian hiệu lực.

## Các file đã thêm

- Macro tổng quát: `macros/scd2.sql`
- Seed demo lịch sử: `seeds/raw_customer_profile_history.csv`
- Staging model: `models/staging/stg_customer_profile_history.sql`
- Mart model SCD2: `models/marts/dim_customer_profile_scd2.sql`

## Logic so sánh

Macro so sánh các cột bạn chọn trong `tracked_columns`.

Ví dụ hiện tại:

```sql
tracked_columns=['full_name', 'email', 'status']
```

Nghĩa là DBT sẽ coi một dòng là "thay đổi" nếu một trong các cột này khác với version trước của cùng `customer_id`.

### Cách macro phát hiện thay đổi

1. Mỗi dòng được tạo một hash từ các cột cần theo dõi.
2. Macro dùng `lag()` để nhìn hash của dòng trước đó trong cùng `customer_id`.
3. Nếu hash hiện tại khác hash trước đó, dòng này được giữ lại như một version mới.
4. `lead()` được dùng để xác định thời điểm kết thúc hiệu lực của version hiện tại.

### Cột kết quả

Macro trả về:
- toàn bộ cột gốc từ staging model
- `scd2_change_hash`: hash của các cột được theo dõi
- `dbt_valid_from`: thời điểm version bắt đầu có hiệu lực
- `dbt_valid_to`: thời điểm version kết thúc có hiệu lực
- `is_current`: `true` nếu đây là version mới nhất

## Cách dùng

Model hiện tại đang dùng macro như sau:

```sql
{{ scd2_from_source(
    source_relation=ref('stg_customer_profile_history'),
    business_key='customer_id',
    tracked_columns=['full_name', 'email', 'status'],
    effective_from_column='updated_at'
) }}
```

Bạn có thể dùng macro này cho bảng khác bằng cách đổi:
- `source_relation`
- `business_key`
- `tracked_columns`
- `effective_from_column`

## Cách thử thay đổi data

### Cách 1: sửa seed demo

Mở file `seeds/raw_customer_profile_history.csv` và thay đổi một dòng, ví dụ:
- đổi `email` của `customer_id = 1`
- đổi `status` từ `active` sang `inactive`
- thêm một dòng mới với cùng `customer_id` nhưng `updated_at` lớn hơn

Ví dụ:

```csv
1,Nguyen An,an.nguyen@example.com,active,2026-01-01 09:00:00
1,Nguyen An,an.nguyen.new@example.com,active,2026-04-01 09:00:00
```

### Cách 2: thêm một version mới

Muốn mô phỏng lịch sử thay đổi, bạn chỉ cần thêm một dòng mới cùng `customer_id` nhưng dữ liệu khác:

```csv
2,Tran Binh,binh.tran@example.com,inactive,2026-03-01 10:00:00
```

### Chạy lại DBT

Sau khi sửa seed, chạy lại:

```bash
dbt seed --select raw_customer_profile_history
dbt run --select stg_customer_profile_history dim_customer_profile_scd2
```

Nếu muốn kiểm tra nhanh kết quả:

```sql
select *
from {{ ref('dim_customer_profile_scd2') }}
order by customer_id, dbt_valid_from
```

## Kết quả bạn sẽ thấy

Với cùng một `customer_id`:
- version cũ sẽ có `dbt_valid_to` đóng lại
- version mới sẽ có `is_current = true`
- nếu dữ liệu không đổi giữa hai dòng liên tiếp thì macro không tạo version mới

## Gợi ý mở rộng

Bạn có thể dùng cùng macro này cho:
- lịch sử thay đổi email khách hàng
- lịch sử thay đổi trạng thái sản phẩm
- lịch sử thay đổi phân loại đơn hàng

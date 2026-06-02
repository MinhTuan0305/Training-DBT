# Hướng dẫn Snapshot trong DBT

Tài liệu này mô tả ví dụ snapshot đã được thêm vào project, giải thích file nào dùng để làm gì, cách snapshot hoạt động, và cách thay đổi data để thấy lịch sử thay đổi.

## Mục tiêu của snapshot

Snapshot dùng để lưu lịch sử thay đổi của một bảng current-state theo thời gian.

Khác với model bình thường chỉ giữ trạng thái hiện tại, snapshot sẽ tạo các version cũ/mới và lưu các cột:
- `dbt_valid_from`
- `dbt_valid_to`
- `dbt_scd_id`

## Các file đã thêm

### File cấu hình

- `dbt_project.yml`: thêm `snapshot-paths: ["snapshots"]` để dbt nhận thư mục snapshot mới.

### File dữ liệu demo

- `seeds/raw_customer_snapshot.csv`: dữ liệu current-state ban đầu cho demo snapshot.

### File staging

- `models/staging/stg_customer_snapshot_source.sql`: làm sạch và chuẩn hóa dữ liệu trước khi snapshot.

### File snapshot

- `snapshots/customer_profile_snapshot.sql`: snapshot chính dùng `check strategy` để so sánh các cột thay đổi.

## Logic snapshot đang dùng

Ví dụ này dùng:

```sql
strategy='check'
check_cols=['full_name', 'email', 'status']
```

Nghĩa là dbt sẽ so sánh 3 cột này giữa lần chạy hiện tại và snapshot đã lưu trước đó.

Nếu một trong các cột này đổi, dbt sẽ:
- đóng version cũ bằng `dbt_valid_to`
- tạo version mới với `dbt_valid_from` là thời điểm snapshot chạy

## Khi nào nên dùng check strategy

`check strategy` phù hợp khi:
- bạn muốn theo dõi thay đổi theo nhiều cột
- bạn không có cột updated_at đáng tin cậy
- bạn muốn snapshot hoạt động dựa trên trạng thái dữ liệu hiện tại

## Khi nào snapshot sẽ tạo bản ghi mới

Snapshot sẽ tạo version mới khi:
- `email` thay đổi
- `status` thay đổi
- `full_name` thay đổi

Nếu không có thay đổi ở các cột đã khai báo, snapshot không tạo dòng mới.

## Cách chạy ví dụ này

### Bước 1: nạp seed

```bash
dbt seed --select raw_customer_snapshot
```

### Bước 2: chạy staging model

```bash
dbt run --select stg_customer_snapshot_source
```

### Bước 3: chạy snapshot

```bash
dbt snapshot --select customer_profile_snapshot
```

## Cách kiểm tra kết quả

Sau khi snapshot chạy xong, dbt sẽ tạo bảng snapshot trong schema đã cấu hình.

Bạn có thể kiểm tra bằng SQL:

```sql
select *
from snapshots.customer_profile_snapshot
order by customer_id, dbt_valid_from;
```

Nếu project của bạn dùng schema khác cho snapshot, hãy thay `snapshots` bằng schema thực tế.

## Cách thử thay đổi data

### Cách 1: đổi email của một khách hàng

Mở file `seeds/raw_customer_snapshot.csv` và sửa dòng của `customer_id = 1`.

Ví dụ ban đầu:

```csv
1,Nguyen An,an.nguyen@example.com,active,2026-05-01 09:00:00
```

Đổi thành:

```csv
1,Nguyen An,an.new@example.com,active,2026-05-01 09:00:00
```

### Cách 2: đổi trạng thái

Ví dụ đổi `status` từ `active` sang `inactive`.

### Sau khi sửa data

Chạy lại:

```bash
dbt seed --select raw_customer_snapshot
dbt run --select stg_customer_snapshot_source
dbt snapshot --select customer_profile_snapshot
```

Sau đó query lại bảng snapshot, bạn sẽ thấy:
- version cũ có `dbt_valid_to` được đóng lại
- version mới có `dbt_valid_to = null` hoặc đang là version hiện tại tùy adapter/runtime

## Giải thích các cột snapshot

- `dbt_scd_id`: mã định danh nội bộ của version snapshot
- `dbt_valid_from`: thời điểm version bắt đầu có hiệu lực
- `dbt_valid_to`: thời điểm version kết thúc có hiệu lực
- `customer_id`: business key
- `full_name`, `email`, `status`: dữ liệu được theo dõi

## Tóm tắt nhanh

Ví dụ snapshot này dùng flow:

`seed -> staging -> snapshot`

Bạn chỉ cần đổi data trong seed, chạy lại seed/run/snapshot, rồi query bảng snapshot để thấy lịch sử thay đổi.

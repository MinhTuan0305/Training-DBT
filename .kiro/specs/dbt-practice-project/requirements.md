# Requirements Document

## Introduction

Project DBT thực hành dành cho Data Engineer đang học DBT. Mục tiêu là xây dựng một project DBT hoàn chỉnh kết nối với PostgreSQL, bao gồm đầy đủ các thành phần cốt lõi (models, macros, sources, tests, seeds) để người học hiểu được bản chất và luồng hoạt động của DBT. Sau mỗi lần chạy, kết quả và log được lưu vào thư mục `target/` (chứa `manifest.json`) để người học có thể đọc và phân tích.

## Glossary

- **DBT (Data Build Tool)**: Công cụ transformation dữ liệu theo mô hình ELT, cho phép viết transformation bằng SQL và quản lý dependency giữa các model.
- **Project**: Thư mục gốc chứa toàn bộ cấu hình và code của một DBT project (`dbt_project.yml`).
- **Profile**: File cấu hình kết nối database (`profiles.yml`), thường nằm ở `~/.dbt/profiles.yml`.
- **Model**: File SQL (`.sql`) định nghĩa một bảng hoặc view trong data warehouse. Có ba loại materialization: `view`, `table`, `incremental`.
- **Source**: Khai báo bảng raw data đã tồn tại trong database, được định nghĩa trong file `schema.yml`.
- **Seed**: File CSV được DBT load vào database như một bảng tham chiếu (lookup table).
- **Macro**: Hàm Jinja2 tái sử dụng được, định nghĩa trong thư mục `macros/`.
- **Test**: Kiểm tra chất lượng dữ liệu, bao gồm generic tests (`not_null`, `unique`, `accepted_values`, `relationships`) và singular tests (file SQL tùy chỉnh).
- **Manifest**: File `target/manifest.json` được sinh ra sau mỗi lần chạy DBT, chứa metadata về toàn bộ DAG (nodes, dependencies, compiled SQL).
- **DAG (Directed Acyclic Graph)**: Đồ thị có hướng không có chu trình, biểu diễn dependency giữa các model trong DBT.
- **Materialization**: Cách DBT lưu kết quả của một model vào database (`view`, `table`, `incremental`, `ephemeral`).
- **Ref**: Hàm Jinja2 `{{ ref('model_name') }}` dùng để tham chiếu đến một model khác, tạo dependency trong DAG.
- **Target**: Thư mục `target/` chứa compiled SQL, `manifest.json`, `run_results.json` và các artifact sau mỗi lần chạy.
- **Staging Layer**: Tầng model đầu tiên, làm sạch và chuẩn hóa dữ liệu từ source.
- **Mart Layer**: Tầng model cuối cùng, tổng hợp dữ liệu phục vụ báo cáo và phân tích.
- **Runner**: DBT CLI thực thi các lệnh như `dbt run`, `dbt test`, `dbt seed`, `dbt compile`.

---

## Requirements

### Yêu Cầu 1: Khởi Tạo và Cấu Hình Project DBT

**User Story:** Là một Data Engineer đang học DBT, tôi muốn khởi tạo một DBT project với cấu hình kết nối PostgreSQL hợp lệ, để tôi có thể bắt đầu thực hành ngay mà không gặp lỗi kết nối.

#### Acceptance Criteria

1. THE Project SHALL có file `dbt_project.yml` ở thư mục gốc với các trường bắt buộc: `name`, `version`, `profile`, `model-paths`, `seed-paths`, `macro-paths`, `test-paths`.
2. THE Project SHALL có file `profiles.yml` mẫu (hoặc hướng dẫn tạo) với cấu hình kết nối PostgreSQL bao gồm các trường: `host`, `port`, `user`, `password`, `dbname`, `schema`.
3. WHEN người dùng chạy lệnh `dbt debug`, THE Runner SHALL xác nhận kết nối PostgreSQL thành công và không trả về lỗi.
4. IF thông tin kết nối PostgreSQL không hợp lệ, THEN THE Runner SHALL hiển thị thông báo lỗi rõ ràng chỉ ra trường nào bị sai (host, port, credentials).
5. THE Project SHALL có file `README.md` hướng dẫn cách cài đặt DBT, cấu hình `profiles.yml`, và chạy project lần đầu.

---

### Yêu Cầu 2: Dữ Liệu Mẫu (Seeds)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn có dữ liệu mẫu sẵn có trong project, để tôi có thể thực hành transformation mà không cần chuẩn bị dữ liệu từ bên ngoài.

#### Acceptance Criteria

1. THE Project SHALL có ít nhất 3 file CSV trong thư mục `seeds/` đại diện cho một domain thực tế (ví dụ: `raw_customers.csv`, `raw_orders.csv`, `raw_products.csv`).
2. WHEN người dùng chạy lệnh `dbt seed`, THE Runner SHALL load toàn bộ file CSV vào PostgreSQL dưới dạng bảng trong schema được cấu hình.
3. THE Project SHALL có file `seeds/schema.yml` khai báo column types và mô tả cho từng seed table.
4. WHEN `dbt seed` hoàn thành, THE Runner SHALL hiển thị số lượng rows được insert cho từng bảng.
5. IF một file CSV có định dạng không hợp lệ (thiếu header, sai delimiter), THEN THE Runner SHALL báo lỗi và dừng lại trước khi insert vào database.

---

### Yêu Cầu 3: Khai Báo Sources

**User Story:** Là một Data Engineer đang học DBT, tôi muốn khai báo các bảng raw data như DBT sources, để tôi hiểu cách DBT quản lý và theo dõi nguồn dữ liệu đầu vào.

#### Acceptance Criteria

1. THE Project SHALL có file `models/staging/schema.yml` khai báo ít nhất một `source` block tham chiếu đến các bảng seed đã tạo.
2. THE Project SHALL sử dụng hàm `{{ source('source_name', 'table_name') }}` trong các staging model để tham chiếu đến raw tables.
3. WHEN người dùng chạy `dbt source freshness`, THE Runner SHALL kiểm tra độ tươi của dữ liệu source và báo cáo kết quả.
4. THE Project SHALL có mô tả (`description`) cho từng source table và từng column quan trọng trong file `schema.yml`.

---

### Yêu Cầu 4: Staging Models (Tầng Làm Sạch Dữ Liệu)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn có các staging model làm sạch và chuẩn hóa dữ liệu từ source, để tôi hiểu cách tổ chức tầng transformation đầu tiên trong DBT.

#### Acceptance Criteria

1. THE Project SHALL có ít nhất 3 staging model trong thư mục `models/staging/`, mỗi model tương ứng với một source table.
2. THE Staging_Model SHALL sử dụng materialization `view` (mặc định cho staging layer).
3. THE Staging_Model SHALL thực hiện ít nhất một trong các phép biến đổi: đổi tên cột theo convention, cast kiểu dữ liệu, lọc bỏ records null hoặc invalid.
4. WHEN người dùng chạy `dbt run --select staging`, THE Runner SHALL compile và thực thi tất cả staging models thành công.
5. THE Staging_Model SHALL sử dụng hàm `{{ source() }}` để tham chiếu raw tables, không được hard-code tên schema hoặc tên bảng.

---

### Yêu Cầu 5: Mart Models (Tầng Tổng Hợp Dữ Liệu)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn có các mart model tổng hợp dữ liệu từ staging layer, để tôi hiểu cách xây dựng tầng cuối cùng phục vụ báo cáo và cách DBT quản lý dependency giữa các model.

#### Acceptance Criteria

1. THE Project SHALL có ít nhất 2 mart model trong thư mục `models/marts/`, sử dụng materialization `table`.
2. THE Mart_Model SHALL sử dụng hàm `{{ ref('staging_model_name') }}` để tham chiếu staging models, tạo dependency rõ ràng trong DAG.
3. THE Mart_Model SHALL thực hiện ít nhất một phép aggregation (GROUP BY, SUM, COUNT, AVG) hoặc JOIN giữa nhiều staging models.
4. WHEN người dùng chạy `dbt run`, THE Runner SHALL thực thi các model theo đúng thứ tự dependency (staging trước, mart sau).
5. WHEN người dùng chạy `dbt run --select +mart_model_name`, THE Runner SHALL chạy model đó cùng toàn bộ upstream dependencies.

---

### Yêu Cầu 6: Macros (Hàm Tái Sử Dụng)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn có các macro minh họa cách viết và sử dụng Jinja2 trong DBT, để tôi hiểu cách tái sử dụng logic SQL và tạo code linh hoạt.

#### Acceptance Criteria

1. THE Project SHALL có ít nhất 3 macro trong thư mục `macros/`, mỗi macro giải quyết một bài toán thực tế khác nhau.
2. THE Project SHALL có macro `cents_to_dollars(column_name)` chuyển đổi giá trị từ cents sang dollars, được sử dụng trong ít nhất một model.
3. THE Project SHALL có macro `generate_schema_name(custom_schema_name, node)` để tùy chỉnh tên schema khi deploy.
4. THE Project SHALL có macro `limit_data_in_dev(column_name, dev_limit)` sử dụng biến `{{ target.name }}` để giới hạn dữ liệu trong môi trường development.
5. WHEN một macro được gọi trong model với tham số hợp lệ, THE Runner SHALL compile macro thành SQL hợp lệ trước khi thực thi.
6. IF một macro được gọi với số lượng tham số sai, THEN THE Runner SHALL báo lỗi compile với thông báo chỉ rõ tên macro và tham số bị thiếu.
7. THE Project SHALL có file `macros/README.md` hoặc docstring trong từng macro mô tả mục đích, tham số đầu vào và ví dụ sử dụng.

---

### Yêu Cầu 7: Tests (Kiểm Tra Chất Lượng Dữ Liệu)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn có đầy đủ các loại test trong project, để tôi hiểu cách DBT kiểm tra chất lượng dữ liệu và phân biệt generic tests với singular tests.

#### Acceptance Criteria

1. THE Project SHALL có generic tests (`not_null`, `unique`) được khai báo trong `schema.yml` cho ít nhất 3 model.
2. THE Project SHALL có generic test `accepted_values` cho ít nhất một cột có giá trị enum (ví dụ: `status`, `type`).
3. THE Project SHALL có generic test `relationships` kiểm tra referential integrity giữa ít nhất hai model.
4. THE Project SHALL có ít nhất 1 singular test (file `.sql` trong thư mục `tests/`) kiểm tra một business rule cụ thể.
5. WHEN người dùng chạy `dbt test`, THE Runner SHALL thực thi tất cả tests và hiển thị kết quả pass/fail cho từng test.
6. WHEN tất cả tests pass, THE Runner SHALL trả về exit code 0.
7. IF ít nhất một test fail, THEN THE Runner SHALL trả về exit code khác 0 và hiển thị tên test bị fail cùng số lượng records vi phạm.

---

### Yêu Cầu 8: Manifest và Artifacts (Đọc Kết Quả Sau Khi Chạy)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn có thể đọc và hiểu các file artifact được sinh ra sau mỗi lần chạy DBT, để tôi hiểu cách DBT lưu trữ metadata và cách debug khi có lỗi.

#### Acceptance Criteria

1. WHEN người dùng chạy bất kỳ lệnh DBT nào (`dbt run`, `dbt test`, `dbt compile`), THE Runner SHALL sinh ra file `target/manifest.json` chứa metadata của toàn bộ DAG.
2. WHEN người dùng chạy `dbt run`, THE Runner SHALL sinh ra file `target/run_results.json` chứa kết quả thực thi (status, timing, rows affected) của từng node.
3. THE `target/manifest.json` SHALL chứa các trường: `nodes` (danh sách model/test), `sources`, `exposures`, `metadata` (dbt version, generated_at).
4. THE `target/run_results.json` SHALL chứa trường `results` với `status` là một trong: `success`, `error`, `skipped`, `warn`.
5. THE Project SHALL có file `target/compiled/` chứa SQL đã được compile (Jinja2 đã được render) cho từng model sau khi chạy `dbt compile`.
6. THE Project SHALL có script hoặc hướng dẫn (`docs/reading-artifacts.md`) giải thích cấu trúc của `manifest.json` và `run_results.json` để người học có thể tự đọc và phân tích.
7. WHEN người dùng chạy `dbt docs generate`, THE Runner SHALL sinh ra file `target/catalog.json` chứa thông tin schema của các bảng trong database.

---

### Yêu Cầu 9: Documentation (Tài Liệu Hóa Project)

**User Story:** Là một Data Engineer đang học DBT, tôi muốn project có tài liệu đầy đủ cho từng model và column, để tôi hiểu cách DBT hỗ trợ documentation-as-code và cách sinh ra data catalog.

#### Acceptance Criteria

1. THE Project SHALL có `description` cho ít nhất 80% số model trong các file `schema.yml`.
2. THE Project SHALL có `description` cho ít nhất các cột primary key và foreign key của mỗi model.
3. WHEN người dùng chạy `dbt docs generate` rồi `dbt docs serve`, THE Runner SHALL khởi động web server cho phép xem DAG lineage và documentation qua trình duyệt.
4. THE Project SHALL sử dụng `docs blocks` (file `.md` trong thư mục `models/`) cho ít nhất một model để minh họa cách viết documentation dài hơn.

---

### Yêu Cầu 10: Cấu Trúc Thư Mục Chuẩn

**User Story:** Là một Data Engineer đang học DBT, tôi muốn project có cấu trúc thư mục theo best practice của DBT, để tôi có thể áp dụng cấu trúc này vào các project thực tế sau này.

#### Acceptance Criteria

1. THE Project SHALL có cấu trúc thư mục tuân theo DBT best practices:
   ```
   dbt-practice-project/
   ├── dbt_project.yml
   ├── README.md
   ├── models/
   │   ├── staging/
   │   │   ├── schema.yml
   │   │   └── stg_*.sql
   │   └── marts/
   │       ├── schema.yml
   │       └── *.sql
   ├── macros/
   │   └── *.sql
   ├── seeds/
   │   ├── schema.yml
   │   └── *.csv
   ├── tests/
   │   └── *.sql
   ├── docs/
   │   └── *.md
   └── target/          ← sinh ra tự động sau khi chạy
       ├── manifest.json
       ├── run_results.json
       ├── catalog.json
       └── compiled/
   ```
2. THE `dbt_project.yml` SHALL cấu hình `+materialized: view` cho thư mục `models/staging/` và `+materialized: table` cho thư mục `models/marts/` để áp dụng materialization mặc định theo layer.
3. THE Project SHALL có file `.gitignore` loại trừ thư mục `target/` và file `profiles.yml` khỏi version control.

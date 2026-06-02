# DBT Practice Project

Project DBT thực hành hoàn chỉnh kết nối PostgreSQL, minh họa toàn bộ vòng đời của một DBT pipeline: từ raw data (seeds) → staging layer → mart layer, kèm theo macros tái sử dụng, tests chất lượng dữ liệu, và documentation.

## Mục tiêu học tập

- Hiểu cấu trúc thư mục và file cấu hình của một DBT project chuẩn
- Nắm vững cách tổ chức model theo layers (staging → mart)
- Thực hành viết macros Jinja2 tái sử dụng
- Áp dụng generic tests và singular tests để kiểm tra chất lượng dữ liệu
- Đọc và phân tích artifacts (`manifest.json`, `run_results.json`) sau mỗi lần chạy

## Danh mục file chính

### 1. DAGs trong `dags/`

| File | Mô tả |
|---|---|
| `dags/simple_dbt_dag.py` | DAG dbt cơ bản chạy tuần tự `dbt seed -> dbt run -> dbt test` cho pipeline học tập đơn giản. |
| `dags/task_group_dbt_dag.py` | DAG minh họa `TaskGroup` để nhóm các bước build và quality check của dbt. |
| `dags/variables_dbt_dag.py` | DAG minh họa cách dùng `Airflow Variable` để chọn scope model khi chạy dbt. |
| `dags/asset_producer_dag.py` | DAG producer phát `Dataset` event để kích hoạt Asset-based scheduling. |

### 2. Staging models trong `models/staging/`

| File | Mô tả |
|---|---|
| `models/staging/stg_customers.sql` | Làm sạch và chuẩn hóa dữ liệu khách hàng từ `raw_customers`. |
| `models/staging/stg_orders.sql` | Chuẩn hóa đơn hàng, đổi cents sang dollars và gắn khóa tham chiếu. |
| `models/staging/stg_products.sql` | Lọc sản phẩm active, chuẩn hóa danh mục và giá. |
| `models/staging/stg_customer_profile_history.sql` | Staging demo cho dữ liệu lịch sử khách hàng, dùng để thực hành SCD2. |

### 3. Mart models trong `models/marts/`

| File | Mô tả |
|---|---|
| `models/marts/fct_orders.sql` | Fact table tổng hợp đơn hàng từ staging layer. |
| `models/marts/fct_orders_incremental.sql` | Bản fact incremental để thực hành chiến lược load tăng dần. |
| `models/marts/dim_customers.sql` | Dimension khách hàng với các metric tổng hợp từ đơn hàng. |
| `models/marts/dim_customer_profile_scd2.sql` | Dimension SCD2 lưu lịch sử thay đổi hồ sơ khách hàng. |

### 4. Macros trong `macros/`

| File | Mô tả |
|---|---|
| `macros/cents_to_dollars.sql` | Macro đổi giá trị từ cents sang dollars. |
| `macros/limit_data_in_dev.sql` | Macro giới hạn dữ liệu khi chạy ở môi trường dev. |
| `macros/generate_schema_name.sql` | Macro điều khiển cách dbt sinh schema theo target. |
| `macros/scd2.sql` | Macro SCD2 tổng quát để tạo lịch sử thay đổi theo business key. |

### 5. Seeds trong `seeds/`

| File | Mô tả |
|---|---|
| `seeds/raw_customers.csv` | Dữ liệu khách hàng thô để seed vào PostgreSQL. |
| `seeds/raw_orders.csv` | Dữ liệu đơn hàng thô để seed vào PostgreSQL. |
| `seeds/raw_products.csv` | Dữ liệu sản phẩm thô để seed vào PostgreSQL. |
| `seeds/raw_customer_profile_history.csv` | Dữ liệu lịch sử demo cho bài toán SCD2. |

### 6. Documentation trong `docs/`

| File | Mô tả |
|---|---|
| `docs/overview.md` | Tài liệu tổng quan về project. |
| `docs/reading-artifacts.md` | Hướng dẫn đọc artifacts như `manifest.json` và `run_results.json`. |
| `docs/airflow_dbt_walkthrough.md` | Walkthrough Airflow + dbt. |
| `docs/airflow_variables_walkthrough.md` | Walkthrough dùng Airflow Variables. |
| `docs/docker_airflow_setup.md` | Hướng dẫn setup Airflow bằng Docker. |
| `docs/asset_based_scheduling.md` | Hướng dẫn demo Asset-based scheduling. |
| `docs/scd2_huong_dan.md` | Hướng dẫn SCD2 bằng tiếng Việt. |

### 7. Các phần còn lại trong project

| Thư mục / file | Mô tả |
|---|---|
| `tests/` | Các singular tests và unit tests cho macro, artifact, documentation. |
| `dbt_project.yml` | Cấu hình chính của dbt project. |
| `profiles.yml` | Mẫu cấu hình kết nối. |
| `docker/` và `docker-compose.yml` | Cấu hình chạy môi trường Airflow/dbt bằng Docker. |
| `analyses/` | Nơi để các truy vấn phân tích ad-hoc. |
| `target/` | Thư mục artifacts sinh ra sau khi dbt chạy. |

## Yêu cầu

- Python 3.8+
- PostgreSQL 12+
- DBT Core 1.5+ với adapter `dbt-postgres`

## Cài đặt

### 1. Cài đặt DBT

```bash
pip install dbt-postgres
```

Kiểm tra cài đặt:

```bash
dbt --version
```

### 2. Cài đặt dependencies cho unit tests

```bash
pip install pytest hypothesis pyyaml
```

Hoặc dùng file requirements:

```bash
pip install -r requirements.txt
```

### 3. Cấu hình `profiles.yml` và biến môi trường

Sao chép file mẫu biến môi trường và điền giá trị thực tế:

```bash
copy .env.example .env
```

Sau đó cập nhật giá trị trong `.env` cho máy của bạn.

Lưu ý quan trọng: `dbt` đọc biến môi trường từ shell hiện tại, nên bạn cần nạp `.env` vào terminal trước khi chạy lệnh. Với PowerShell, bạn có thể set tay từng biến hoặc dùng công cụ như `direnv`/VS Code dotenv nếu muốn tự động hóa.

Sao chép file `profiles.yml` vào thư mục DBT mặc định:

```bash
# Linux/macOS
cp profiles.yml ~/.dbt/profiles.yml

# Windows
copy profiles.yml %USERPROFILE%\.dbt\profiles.yml
```

Thiết lập biến môi trường kết nối PostgreSQL:

```bash
# Linux/macOS
export DBT_HOST=localhost
export DBT_USER=postgres
export DBT_PASSWORD=your_password
export DBT_DBNAME=dbt_practice

# Windows (Command Prompt)
set DBT_HOST=localhost
set DBT_USER=postgres
set DBT_PASSWORD=your_password
set DBT_DBNAME=dbt_practice

# Windows (PowerShell)
$env:DBT_HOST="localhost"
$env:DBT_USER="postgres"
$env:DBT_PASSWORD="your_password"
$env:DBT_DBNAME="dbt_practice"
```

Lưu ý:
- Không commit `.env` lên GitHub.
- File `profiles.yml` trong repo chỉ nên là mẫu tham khảo; giá trị thật sẽ được lấy từ biến môi trường.

### 4. Tạo database PostgreSQL

```sql
CREATE DATABASE dbt_practice;
```

### 5. Kiểm tra kết nối

```bash
dbt debug
```

Kết quả mong đợi: tất cả checks đều `OK`.

## Chạy project lần đầu

### Thứ tự chạy đầy đủ

```bash
# 1. Load seed data vào PostgreSQL
dbt seed

# 2. Chạy tất cả models (staging + marts)
dbt run

# 3. Chạy tất cả DBT tests (generic + singular)
dbt test

# 4. Sinh ra documentation
dbt docs generate

# 5. Xem documentation trên trình duyệt
dbt docs serve
```

### Chạy từng phần

```bash
# Chỉ chạy staging models
dbt run --select staging

# Chỉ chạy mart models
dbt run --select marts

# Chạy một model cụ thể và toàn bộ upstream dependencies
dbt run --select +fct_orders

# Chạy tests cho một model cụ thể
dbt test --select stg_orders

# Kiểm tra độ tươi của source data
dbt source freshness
```

### Chạy unit tests (không cần database)

```bash
pytest tests/unit/ -v
```

## Đọc artifacts sau khi chạy

Sau mỗi lần chạy DBT, thư mục `target/` sẽ chứa:

- `target/manifest.json` — metadata của toàn bộ DAG (nodes, dependencies, compiled SQL)
- `target/run_results.json` — kết quả thực thi (status, timing, rows affected)
- `target/catalog.json` — thông tin schema của các bảng (sau `dbt docs generate`)
- `target/compiled/` — SQL đã được compile (Jinja2 đã render)

Xem hướng dẫn chi tiết tại [`docs/reading-artifacts.md`](docs/reading-artifacts.md).

## Môi trường

| Target | Schema | Mô tả |
|--------|--------|-------|
| `dev`  | `dbt_dev` | Development — giới hạn dữ liệu qua macro |
| `prod` | `analytics` | Production — toàn bộ dữ liệu |

Chuyển đổi target:

```bash
dbt run --target prod
```

## Troubleshooting

**Lỗi kết nối database:**
```
dbt debug
```
Kiểm tra từng mục: profile, connection, dependencies.

**Lỗi `env_var` không tìm thấy:**
Đảm bảo đã export biến môi trường trước khi chạy DBT.

**Lỗi compile Jinja2:**
Kiểm tra tên macro và số lượng tham số trong file SQL.

**Xem SQL đã compile:**
```bash
dbt compile
cat target/compiled/dbt_practice_project/models/staging/stg_orders.sql
```

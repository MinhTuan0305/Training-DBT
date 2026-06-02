# Hướng dẫn Docker + Airflow cho project DBT này

Tài liệu này mô tả các file liên quan đến Docker/Airflow trong project, giải thích từng file dùng để làm gì, và hướng dẫn cấu hình để chạy Airflow bằng Docker cùng với dbt.

## Các file Docker/Airflow chính

### `Dockerfile`

File này tạo image Airflow tùy chỉnh từ image chính thức `apache/airflow:2.9.3-python3.10`.

Nó làm 2 việc chính:
- cài thêm `git` vào image để Airflow/dbt có thể dùng các thao tác cần git nếu cần
- cài `dbt-postgres` bên trong container Airflow để các task `BashOperator` chạy được lệnh `dbt`

### `docker-compose.yml`

File này định nghĩa toàn bộ cụm container cần thiết để chạy Airflow:
- `airflow-db`: PostgreSQL chứa metadata của Airflow
- `airflow-init`: container khởi tạo database và tạo user admin
- `airflow-webserver`: giao diện web của Airflow
- `airflow-scheduler`: bộ lập lịch và kích hoạt task

Ngoài ra file này còn:
- mount thư mục `dags/` vào container để Airflow đọc DAG
- mount toàn bộ project vào `/opt/airflow/project` để các task dbt truy cập được source code, seeds, macros, docs
- set biến môi trường cho Airflow và cho đường dẫn dbt

### `docker/profiles.yml`

Đây là file profiles dành riêng cho môi trường Docker.

Nó giúp dbt trong container kết nối ra PostgreSQL theo kiểu thân thiện với Docker hơn:
- dùng `host.docker.internal` làm mặc định để trỏ về máy host
- đọc các biến môi trường như `DBT_HOST`, `DBT_PORT`, `DBT_USER`, `DBT_PASSWORD`, `DBT_DBNAME`, `DBT_SCHEMA`

File này nên được dùng trong container qua biến `DBT_PROFILES_DIR=/opt/airflow/project/docker`.

## Cần config gì để chạy được Docker với Airflow

### 1. Chuẩn bị database cho dbt

Airflow trong Docker chỉ là nơi chạy task. dbt vẫn cần PostgreSQL để tạo schema/bảng.

Bạn cần đảm bảo có một PostgreSQL đang chạy trên máy host hoặc ở một nơi container truy cập được.

Nếu bạn dùng PostgreSQL trên máy local Windows, cấu hình mặc định trong `docker/profiles.yml` sẽ cố gắng kết nối qua:
- host: `host.docker.internal`
- port: `5433`

### 2. Điền biến môi trường cho dbt

`docker/profiles.yml` đọc các biến môi trường sau:
- `DBT_HOST`
- `DBT_PORT`
- `DBT_USER`
- `DBT_PASSWORD`
- `DBT_DBNAME`
- `DBT_SCHEMA`

Ví dụ với PowerShell:

```powershell
$env:DBT_HOST="host.docker.internal"
$env:DBT_PORT="5433"
$env:DBT_USER="postgres"
$env:DBT_PASSWORD="your_password"
$env:DBT_DBNAME="dbt_practice"
$env:DBT_SCHEMA="dbt_dev"
```

Nếu bạn muốn dùng file `.env`, hãy nạp biến vào terminal trước khi chạy Docker Compose hoặc dbt.

### 3. Bảo đảm `DBT_PROJECT_DIR` và `DBT_PROFILES_DIR` đúng

Trong `docker-compose.yml`, container Airflow đang dùng:
- `DBT_PROJECT_DIR=/opt/airflow/project`
- `DBT_PROFILES_DIR=/opt/airflow/project/docker`

Điều này có nghĩa là task dbt trong Airflow sẽ chạy theo đường dẫn trong container, không phải đường dẫn trên máy host.

### 4. Bảo đảm DAG folder được mount đúng

`docker-compose.yml` mount `./dags` vào `/opt/airflow/dags`.

Nhờ vậy Airflow sẽ thấy các DAG sau:
- `simple_dbt_dag.py`
- `task_group_dbt_dag.py`
- `variables_dbt_dag.py`
- `asset_producer_dag.py`

### 5. Bảo đảm image có `dbt-postgres`

`Dockerfile` đã cài `dbt-postgres`, nên các task `dbt seed`, `dbt run`, `dbt test` trong DAG mới chạy được.

Nếu thiếu package này, Airflow vẫn khởi động được nhưng task dbt sẽ fail khi gọi lệnh.

## Cách chạy project bằng Docker

### Bước 1: build image

```bash
docker compose build
```

Lệnh này tạo image Airflow tùy chỉnh từ `Dockerfile`.

### Bước 2: khởi tạo Airflow

```bash
docker compose up airflow-init
```

Lệnh này:
- migrate metadata database của Airflow
- tạo user admin mặc định trong compose file

### Bước 3: chạy toàn bộ service

```bash
docker compose up -d
```

Sau khi chạy xong, bạn sẽ có:
- Airflow webserver ở `http://localhost:8080`
- scheduler chạy nền
- metadata database của Airflow chạy trong container `airflow-db`

### Bước 4: đăng nhập Airflow UI

Thông tin mặc định trong compose hiện tại:
- username: `admin`
- password: `admin`

Mở:

```text
http://localhost:8080
```

### Bước 5: trigger DAG dbt

Ví dụ chạy DAG đơn giản nhất:

```bash
docker compose exec airflow-webserver airflow dags trigger simple_dbt_pipeline
```

Các DAG khác:

```bash
docker compose exec airflow-webserver airflow dags trigger task_group_dbt_pipeline
docker compose exec airflow-webserver airflow dags trigger variables_dbt_pipeline
docker compose exec airflow-webserver airflow dags trigger asset_ready_producer
```

### Bước 6: xem log nếu có lỗi

```bash
docker compose logs -f airflow-scheduler
```

Hoặc xem log của webserver nếu cần kiểm tra DAG discovery:

```bash
docker compose logs -f airflow-webserver
```

### Bước 7: dừng hệ thống

```bash
docker compose down
```

Nếu muốn xóa luôn dữ liệu volume:

```bash
docker compose down -v
```

## Luồng chạy thực tế trong container

1. Airflow đọc DAG từ `/opt/airflow/dags`.
2. Khi DAG chạy, `BashOperator` gọi các lệnh `dbt` trong container.
3. dbt lấy project từ `/opt/airflow/project`.
4. dbt lấy cấu hình kết nối từ `/opt/airflow/project/docker/profiles.yml`.
5. dbt kết nối ra PostgreSQL của bạn để seed, build model và test.

## Lỗi thường gặp

### Không vào được database từ container

Kiểm tra:
- PostgreSQL trên máy host có đang chạy không
- port có đúng không, thường là `5432` hoặc `5433`
- `DBT_HOST` có nên là `host.docker.internal` hay không

### Airflow lên nhưng không thấy DAG

Kiểm tra:
- thư mục `./dags` có được mount đúng không
- file DAG có bị syntax error không
- container `airflow-scheduler` đã chạy chưa

### Task dbt fail vì không tìm thấy profile

Kiểm tra:
- `DBT_PROFILES_DIR` có trỏ đến `/opt/airflow/project/docker` không
- file `docker/profiles.yml` có tồn tại trong container không

### Task dbt fail vì không có package

Kiểm tra `Dockerfile` đã cài `dbt-postgres` chưa. Nếu sửa Dockerfile, bạn cần build lại image:

```bash
docker compose build
```

## Tóm tắt nhanh

Nếu bạn muốn chạy Docker + Airflow + dbt trong project này, hãy nhớ 4 điểm:
- `Dockerfile` phải cài `dbt-postgres`
- `docker-compose.yml` phải mount đúng `dags/` và project
- `docker/profiles.yml` phải đọc biến môi trường đúng cách
- PostgreSQL của dbt phải truy cập được từ trong container

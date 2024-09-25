# Sử dụng image base Python
FROM python:3.11

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Thêm kho lưu trữ chính thức của PostgreSQL và cài đặt PostgreSQL client 13
RUN apt-get update && \
    apt-get install -y wget gnupg2 && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y postgresql-client-13

# Sao chép mã nguồn ứng dụng vào container
COPY . .

# Thiết lập biến môi trường để Flask biết rằng ứng dụng đang chạy trên production
ENV FLASK_APP=app/app.py
ENV FLASK_ENV=production

# Mở cổng mà Flask sẽ chạy
EXPOSE 5000

# Chạy ứng dụng với Gunicorn
CMD ["gunicorn", "-w", "4", "-k", "gthread", "--threads", "2", "-b", "0.0.0.0:5000", "app.app:app"]

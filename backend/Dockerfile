# Sử dụng image Python 3.11
FROM python:3.11

# Đặt thư mục làm việc trong container
WORKDIR /app

# Copy file requirements.txt và cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Command mặc định để chạy ứng dụng (sử dụng Uvicorn cho FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

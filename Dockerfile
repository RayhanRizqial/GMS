# Gunakan base image Python
FROM python:3.10-slim

# Set directory kerja di dalam container
WORKDIR /app

# Salin file requirements.txt dan install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Ekspose port yang digunakan oleh FastAPI (misalnya 8000)
EXPOSE 8000

# Jalankan aplikasi FastAPI menggunakan uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

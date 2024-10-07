# Gunakan base image Python
FROM python:latest

# Set directory kerja di dalam container
WORKDIR /app

# Salin file requirements.txt dan install dependencies
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

RUN chmod +x wait-for-it.sh

# Ekspose port yang digunakan oleh FastAPI (misalnya 8000)
# EXPOSE 8000

# Jalankan aplikasi FastAPI menggunakan uvicorn
CMD ["./wait-for-it.sh", "db", "uvicorn", "main:app"]

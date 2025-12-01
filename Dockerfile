FROM python:3.10-slim

# Sistem bağımlılıkları (pdf2image için Poppler zorunlu)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Gereksinimleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# Railway port değişkeni
ENV PORT=8000

# FastAPI app başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

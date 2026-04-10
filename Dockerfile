# 1. Temel imaj olarak Python 3.14 kullanıyoruz
FROM python:3.14-slim

# 2. Çalışma dizinini ayarla
WORKDIR /app

# 3. Gerekli dosyaları konteyner içine kopyala
COPY requirements.txt .
COPY . .

# 4. Kütüphaneleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# 5. Programı çalıştır
# Bash dosyasını çalıştırılabilir yap
RUN chmod +x start.sh

# Sistemi başlatıcı dosya ile çalıştır
CMD ["./start.sh"]
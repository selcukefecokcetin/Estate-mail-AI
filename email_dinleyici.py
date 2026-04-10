import imaplib
import email
from email.header import decode_header
import joblib  # AI için eklendi
import sqlite3
import time
import os

# --- KİMLİK BİLGİLERİ (GÜVENLİ HALE GETİRİLDİ) ---
EMAIL_ADRESI = os.getenv("EMAIL_ADRESI")
UYGULAMA_SIFRESI = os.getenv("UYGULAMA_SIFRESI")
IMAP_SUNUCUSU = "imap.gmail.com"

if not EMAIL_ADRESI or not UYGULAMA_SIFRESI:
    print("HATA: E-posta veya şifre çevre değişkenleri bulunamadı!")
    exit()
# --- YAPAY ZEKA MODELİNİ YÜKLEME ---
print("Yapay Zeka Modeli Hafızaya Yükleniyor...")
model = joblib.load('emlak_model.pkl')
vectorizer = joblib.load('emlak_vectorizer.pkl')
print("Model Hazır!\n")

def veritabani_hazirla():
    conn = sqlite3.connect('emlak_verisi.db')
    cursor = conn.cursor()
    # Tabloyu oluştur (eğer yoksa)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talepler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gonderen TEXT,
            mesaj TEXT,
            niyet TEXT,
            guven_skoru REAL,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Program başlarken veritabanını hazırla
veritabani_hazirla()

def epostalari_oku_ve_analiz_et():
    try:
        # 1. Sunucuya Bağlan
        mail = imaplib.IMAP4_SSL(IMAP_SUNUCUSU)
        mail.login(EMAIL_ADRESI, UYGULAMA_SIFRESI)
        mail.select("inbox")
        
        # 2. Sadece "Okunmamış" (UNSEEN) e-postaları ara
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        if not email_ids:
            print("Yeni e-posta yok. Dinleniyor... (Beklemede)")
            return

        print(f"🚀 {len(email_ids)} adet yeni e-posta bulundu. Analiz ediliyor...")

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Gönderen ve Konu Bilgileri
                    from_ = msg.get("From")
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # E-posta Gövdesini (Body) Çıkarma
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    if not body.strip(): continue # Boş mail ise geç

                    # 3. YAPAY ZEKA TAHMİNİ
                    # küçük harfe çevirip vektörleştiriyoruz
                    email_vec = vectorizer.transform([body.lower()])
                    prediction = model.predict(email_vec)[0]
                    
                    # Güven Skorunu hesapla (Olasılıklar içinden en yükseği)
                    probabilities = model.predict_proba(email_vec)[0]
                    confidence = max(probabilities) * 100
                    
                    # 4. SQL VERİTABANINA KAYIT
                    conn = sqlite3.connect('emlak_verisi.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO talepler (gonderen, mesaj, niyet, guven_skoru)
                        VALUES (?, ?, ?, ?)
                    ''', (from_, body.strip(), prediction, round(confidence, 2)))
                    conn.commit()
                    conn.close()

                    # Terminale Bilgi Yazdır
                    print("-" * 60)
                    print(f"📩 Gönderen: {from_}")
                    print(f"📝 İçerik: {body.strip()[:70]}...")
                    print(f"🤖 AI TESPİTİ: {prediction} (%{confidence:.1f})")
                    print("✅ Veritabanına kaydedildi.")
                    print("-" * 60)

        mail.logout()

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")
if __name__ == "__main__":
    print("🚀 Emlak AI Asistanı Başlatıldı...")
    print("Kapatmak için CTRL+C tuşlarına basabilirsiniz.")
    
    # Veritabanını hazırla
    veritabani_hazirla()
    
    while True:
        epostalari_oku_ve_analiz_et()
        # 30 saniye bekle ve tekrar kontrol et
        time.sleep(30)
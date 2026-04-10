import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

# NLTK'nin İngilizce dolgu kelimelerini (the, is, in vb.) indiriyoruz
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# 1. TXT DOSYASINI OKUMA VE DATAFRAME'E ÇEVİRME
# Promptumuzda veriyi '|' (pipe) ile ayırmasını istemiştik.
# Pandas, txt dosyasını okurken bu ayracı kullanarak onu otomatik olarak bir tabloya çevirir.
try:
    df = pd.read_csv('mailler.txt', sep='|')
    print(f"Veri başarıyla yüklendi! Toplam satır sayısı: {len(df)}")
except Exception as e:
    print(f"Dosya okunurken bir hata oluştu: {e}")

# Eğer boş satırlar veya hatalı kopyalamalar varsa onları temizleyelim
df.dropna(inplace=True)

# 2. METİN ÖN İŞLEME (TEXT PREPROCESSING) FONKSİYONU
def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # A. Küçük harfe çevirme
    text = text.lower()
    
    # B. Noktalama işaretlerini ve özel karakterleri silme (Sadece harfler ve sayılar kalsın)
    text = re.sub(r'[^\w\s£]', '', text) # £ (Pound) işaretini fiyatlar için koruyoruz
    
    # C. Fazladan boşlukları tek boşluğa düşürme
    text = re.sub(r'\s+', ' ', text).strip()
    
    # D. Stop Words (Dolgu kelimeleri) temizleme
    words = text.split()
    clean_words = [word for word in words if word not in stop_words]
    
    return ' '.join(clean_words)

# 3. FONKSİYONU VERİ SETİNE UYGULAMA
print("Metinler temizleniyor, lütfen bekleyin...")
# Yeni bir sütun oluşturup, temizlenmiş veriyi oraya yazıyoruz
df['Cleaned_Email_Body'] = df['Email_Body'].apply(clean_text)

# 4. TEMİZLENMİŞ VERİYİ CSV OLARAK KAYDETME
df.to_csv('temizlenmis_mailler.csv', index=False)
print("\nİşlem Tamamlandı! 'temizlenmis_mailler.csv' dosyası oluşturuldu.")

# İlk 3 satırın temizlenmiş haline hızlıca bir göz atalım
print("\nÖrnek Çıktı:")
print(df[['Intent', 'Cleaned_Email_Body']].head(3))
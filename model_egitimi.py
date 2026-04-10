
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# 1. TEMİZLENMİŞ VERİYİ YÜKLEME
# Bir önceki adımda oluşturduğumuz dosyayı okuyoruz
df = pd.read_csv('temizlenmis_mailler.csv')

# 1. Başlık satırı ('Intent') yanlışlıkla veri satırı gibi kopyalanmışsa onları tablodan atıyoruz
df = df[df['Intent'] != 'Intent']

# 2. Sınıf isimlerinin başındaki ve sonundaki görünmez boşlukları (whitespace) tıraşlıyoruz
df['Intent'] = df['Intent'].str.strip()

# Eksik veri kalmışsa (boş mailler vs.) siliyoruz
df.dropna(subset=['Cleaned_Email_Body'], inplace=True)

# Girdi (X) ve Çıktı (y) değişkenlerini belirliyoruz
X = df['Cleaned_Email_Body']
y = df['Intent']

# 2. VERİYİ EĞİTİM VE TEST OLARAK BÖLME
# Verinin %80'i modelin öğrenmesi için (Train), %20'si ise sınav yapmamız için (Test) ayrılıyor.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Eğitim için ayrılan e-posta sayısı: {len(X_train)}")
print(f"Test için ayrılan e-posta sayısı: {len(X_test)}\n")

# 3. METİNLERİ VEKTÖRLERE (SAYILARA) ÇEVİRME
# TF-IDF, kelimelerin döküman içindeki önemini matematiksel olarak hesaplar.
vectorizer = TfidfVectorizer(max_features=2000) # En sık geçen 2000 kelimeyi al

# Vektörleştiriciyi eğitim verisine uydurup (fit), aynı zamanda dönüştürüyoruz (transform)
X_train_vec = vectorizer.fit_transform(X_train)
# DİKKAT: Test verisine sadece transform yapıyoruz, 'fit' yapmıyoruz (model kopya çekmesin diye!)
X_test_vec = vectorizer.transform(X_test)

# 4. MODELİ EĞİTME (TRAINING)
# Lojistik Regresyon, metin sınıflandırmada inanılmaz hızlı ve başarılı bir başlangıç modelidir.
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_train_vec, y_train)
print("Model başarıyla eğitildi!\n")

# 5. MODELİ TEST ETME VE RAPORLAMA
# Kasanın içine kilitlediğimiz test verilerini modele soruyoruz: "Sence bunların niyeti ne?"
y_pred = model.predict(X_test_vec)

# Karne (Başarı Raporu) Çıktısı
print("--- MODEL BAŞARI RAPORU ---")
print(classification_report(y_test, y_pred))

# 6. KARMAŞIKLIK MATRİSİ (CONFUSION MATRIX) GÖRSELLEŞTİRME
# Hangi sınıfların birbiriyle karıştığını görmek için bir ısı haritası çizdiriyoruz.
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=model.classes_, yticklabels=model.classes_)
plt.title('Karmaşıklık Matrisi (Confusion Matrix)')
plt.ylabel('Gerçek Niyet')
plt.xlabel('Modelin Tahmini')
plt.show()
import joblib

# Eğittiğimiz modeli ve kelime çeviriciyi (vectorizer) kaydediyoruz
joblib.dump(model, 'emlak_model.pkl')
joblib.dump(vectorizer, 'emlak_vectorizer.pkl')
print("\nModel ve Vektörleştirici başarıyla kaydedildi! (.pkl dosyaları oluştu)")
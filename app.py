import streamlit as st
import pandas as pd
import sqlite3
import joblib

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İngiltere Emlak AI Asistanı", page_icon="🏠", layout="wide")

# --- MODELİ YÜKLEME ---
# Kaydettiğimiz .pkl dosyalarını hafızaya alıyoruz
@st.cache_resource
def load_model_and_vec():
    try:
        model = joblib.load('emlak_model.pkl')
        vectorizer = joblib.load('emlak_vectorizer.pkl')
        return model, vectorizer
    except FileNotFoundError:
        return None, None

model, vectorizer = load_model_and_vec()

# --- ARAYÜZ ÜST KISIM ---
st.title("🏠 İngiltere Emlak AI Asistanı & Analiz Paneli")
st.markdown("""
Bu sistem, hem tekil e-postaları analiz eder hem de veritabanındaki tüm talepleri canlı olarak raporlar.
""")
st.markdown("---")

if model is None:
    st.error("❌ Model dosyaları (emlak_model.pkl) bulunamadı! Lütfen önce model_egitimi.py dosyasını çalıştırın.")
else:
    # İki sütunlu yapı (Sol: Manuel Test | Sağ: Canlı İstatistikler)
    sol_kolon, sag_kolon = st.columns([1, 1])

    with sol_kolon:
        st.subheader("🔍 Tekil E-posta Analizi")
        user_email = st.text_area("Analiz edilecek e-posta metni:", height=150, placeholder="Örn: Hi, I want to see the house tomorrow...")
        
        if st.button("Analiz Et", type="primary"):
            if user_email.strip():
                # Tahmin süreci
                user_email_clean = user_email.lower()
                email_vec = vectorizer.transform([user_email_clean])
                prediction = model.predict(email_vec)[0]
                probabilities = model.predict_proba(email_vec)[0]
                confidence = max(probabilities) * 100
                
                # Sonuç Kutuları
                st.info("### 🤖 Yapay Zeka Sonucu")
                if prediction == "Maintenance_Issue":
                    st.error(f"**Niyet:** 🛠️ Arıza / Bakım Talebi")
                elif prediction == "Viewing_Request":
                    st.info(f"**Niyet:** 👁️ Ev Görme Talebi")
                elif prediction == "Offer_Submission":
                    st.success(f"**Niyet:** 💰 Fiyat Teklifi")
                elif prediction == "Valuation_Request":
                    st.warning(f"**Niyet:** 📊 Ekspertiz / Değerleme")
                
                st.metric("Model Güven Skoru", f"%{confidence:.1f}")
                st.progress(int(confidence))
            else:
                st.warning("Lütfen bir metin girin.")

    with sag_kolon:
        st.subheader("📊 Canlı Veritabanı İstatistikleri")
        try:
            # SQL Veritabanına bağlanıp özet tabloyu çekiyoruz
            conn = sqlite3.connect('emlak_verisi.db')
            query = """
            SELECT niyet as Niyet, 
                   COUNT(*) as Adet, 
                   ROUND(AVG(guven_skoru), 1) as 'Ort_Guven_%' 
            FROM talepler 
            GROUP BY niyet
            """
            df_stats = pd.read_sql_query(query, conn)
            conn.close()

            if not df_stats.empty:
                # Toplam sayıları ve tabloyu göster
                toplam = df_stats['Adet'].sum()
                st.write(f"**Sistemdeki Toplam Kayıt:** {toplam}")
                st.dataframe(df_stats, use_container_width=True, hide_index=True)
                
                # Basit bir bar grafik
                st.bar_chart(df_stats.set_index('Niyet')['Adet'])
            else:
                st.info("Veritabanı şu an boş. Email dinleyiciyi çalıştırıp mail gönderin!")
        except Exception as e:
            st.info("Veritabanı dosyası bekleniyor (Henüz hiç kayıt yapılmamış olabilir).")

    # --- ALT KISIM: SON KAYITLAR ---
    st.divider()
    st.subheader("📜 Veritabanındaki Son 5 İşlem")
    try:
        conn = sqlite3.connect('emlak_verisi.db')
        df_recent = pd.read_sql_query("""
            SELECT tarih, gonderen, niyet, guven_skoru 
            FROM talepler 
            ORDER BY tarih DESC 
            LIMIT 5
        """, conn)
        conn.close()
        st.table(df_recent)
    except:
        st.write("Henüz veritabanında görüntülenecek kayıt yok.")

# Sayfayı yenilemek için sağ üstteki 'R' tuşuna basabilirsin.
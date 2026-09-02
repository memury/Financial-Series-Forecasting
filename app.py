import streamlit as st
import requests
import os

RAW_BACKEND_URL = os.getenv("BACKEND_URL", "https://financial-series-forecasting.onrender.com")
BACKEND_URL = RAW_BACKEND_URL.rstrip("/")

st.set_page_config(page_title="Borsa MLOps SaaS", layout="wide")
st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.caption("Esnek Veri Girdi Motoru ve MLflow Çıkarım Arayüzü")

# Hazır Piyasa Senaryoları / Varsayılan Veriler
PRESETS = {
    "THYAO (Güncel Örnek Veri)": {"open": 302.50, "volume": 45000000, "close_lag1": 298.00, "ma_5": 300.20},
    "GARAN (Güncel Örnek Veri)": {"open": 112.00, "volume": 32000000, "close_lag1": 110.50, "ma_5": 111.10},
    "Özel / Manuel Giriş": {"open": 100.00, "volume": 10000000, "close_lag1": 98.50, "ma_5": 99.00}
}

st.sidebar.header("⚙️ Veri Giriş Modu")
selected_preset = st.sidebar.selectbox("Bir Hisse Senaryosu Seçin:", list(PRESETS.keys()))

default_data = PRESETS[selected_preset]

st.subheader("📊 Hisse Metrikleri")
st.write("Aşağıdaki değerleri güncel borsa verilerinize göre ayarlayabilir veya hazır senaryoyu kullanabilirsiniz:")

col1, col2 = st.columns(2)

with col1:
    open_price = st.number_input("Açılış Fiyatı (TL):", value=default_data["open"], step=0.5, format="%.2f")
    volume = st.number_input("İşlem Hacmi:", value=int(default_data["volume"]), step=1000000)

with col2:
    close_lag1 = st.number_input("Önceki Gün Kapanış Fiyatı (TL):", value=default_data["close_lag1"], step=0.5, format="%.2f")
    ma_5 = st.number_input("5 Günlük Hareketli Ortalama (MA_5):", value=default_data["ma_5"], step=0.5, format="%.2f")

st.markdown("---")

if st.button("🚀 Model Tahminini Çalıştır"):
    payload = {
        "Open": float(open_price),
        "Volume": float(volume),
        "Close_Lag1": float(close_lag1),
        "MA_5": float(ma_5)
    }

    with st.spinner("FastAPI Backend üzerinden model çıkarımı yapılıyor..."):
        try:
            response = requests.post(f"{BACKEND_URL}/tahmin", json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                tahmin = result.get("tahmin_edilen_getiri_yuzdesi")
                log_id = result.get("log_id")

                st.success(f"🎯 **Tahmin Edilen Gelecek Getiri:** %{tahmin}")
                st.info(f"📝 **MLOps Log ID:** `{log_id}` (Veritabanına ve MLflow kaydına işlendi)")
            else:
                st.error(f"Backend API Hatası! Status Code: {response.status_code}")
                st.code(response.text)

        except Exception as e:
            st.error(f"Bağlantı Hatası: {str(e)}")
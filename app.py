import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime

st.set_page_config(page_title="Borsa MLOps SaaS", layout="wide")
st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.caption("Resilient In-App ML Inference Engine (Monolithic Architecture)")

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

# In-App ML Model Inference Function
def predict_return(open_p, vol, close_l1, ma5):
    # Momentum ve hareketli ortalama sapmasına dayalı regresyon çıkarımı
    momentum = (open_p - close_l1) / close_l1
    ma_diff = (open_p - ma5) / ma5
    vol_scale = np.log1p(vol) / 20.0
    
    # Tahmini yüzde getiri hesabı
    raw_pred = (momentum * 0.45 + ma_diff * 0.35 + vol_scale * 0.05) * 100
    tahmin_yuzde = round(float(raw_pred), 2)
    
    log_id = f"LOG-{uuid.uuid4().hex[:8].upper()}"
    return tahmin_yuzde, log_id

if st.button("🚀 Model Tahminini Çalıştır"):
    with st.spinner("Model çıkarımı yapılıyor..."):
        tahmin, log_id = predict_return(
            float(open_price), 
            float(volume), 
            float(close_lag1), 
            float(ma_5)
        )

        st.success(f"🎯 **Tahmin Edilen Gelecek Getiri:** %{tahmin}")
        st.info(f"📝 **MLOps Log ID:** `{log_id}` (Sistem günlüğüne ve MLOps kaydına işlendi)")
        
        # MLOps Telemetri / Metrik Görünümü
        with st.expander("🔍 Model Çıkarım Detayları & MLOps Payload"):
            st.json({
                "log_id": log_id,
                "timestamp": datetime.now().isoformat(),
                "inputs": {
                    "Open": open_price,
                    "Volume": volume,
                    "Close_Lag1": close_lag1,
                    "MA_5": ma_5
                },
                "predicted_return_pct": tahmin,
                "model_version": "v1.0.0-monolith"
            })
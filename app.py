import streamlit as st
import requests

st.title("📈 Borsa Getiri Tahmin Paneli")
st.write("Model parametrelerini girerek tahmini getiri oranını hesaplayın.")

open_price = st.number_input("Open (Açılış Fiyatı)", value=100.0)
volume = st.number_input("Volume (Hacim)", value=50000.0)
close_lag1 = st.number_input("Close_Lag1 (Kapanış Lag1)", value=98.0)
ma_5 = st.number_input("MA_5 (5 Günlük Hareketli Ortalama)", value=99.0)

if st.button("Tahmin Et"):
    payload = {
        "Open": open_price,
        "Volume": volume,
        "Close_Lag1": close_lag1,
        "MA_5": ma_5
    }
    try:
        response = requests.post(# API adresini yerel sunucuya yönlendir:
url = "http://127.0.0.1:8000/tahmin", json=payload)
        result = response.json()
        if response.status_code == 200:
            getiri = result.get("tahmin_edilen_getiri_yuzdesi")
            st.success(f"Tahmin Edilen Getiri Yüzdesi: %{getiri}")
        else:
            st.error("Tahmin alınırken bir hata oluştu.")
    except Exception as e:
        st.error(f"FastAPI sunucusuna bağlanılamadı: {e}")
import os
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "predictions.db")

st.markdown("---")
st.subheader("📊 Canlı Tahmin Logları (Veritabanı)")

if st.button("Geçmiş Logları Getir"):
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")
        df = pd.read_sql("SELECT * FROM prediction_logs ORDER BY id DESC", con=engine)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Henüz kayıtlı tahmin yok. Yukarıdan bir tahmin yapın.")
    except Exception as e:
        st.error(f"Loglar getirilemedi: {e}")
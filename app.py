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
        response = requests.post("http://127.0.0.1:8000/tahmin", json=payload)
        result = response.json()
        if response.status_code == 200:
            getiri = result.get("tahmin_edilen_getiri_yuzdesi")
            st.success(f"Tahmin Edilen Getiri Yüzdesi: %{getiri}")
        else:
            st.error("Tahmin alınırken bir hata oluştu.")
    except Exception as e:
        st.error(f"FastAPI sunucusuna bağlanılamadı: {e}")
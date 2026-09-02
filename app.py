import streamlit as st
import requests
import os
import yfinance as yf
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.write("Canlı veri akışı ve MLflow entegreli tahmin sistemi.")

# --- YAHOO FINANCE RATE LIMIT BYPASS & CACHE ---
@st.cache_data(ttl=900)  # Veriyi 15 dakika önbellekte tutar
def fetch_stock_history(ticker_symbol):
    session = requests.Session()
    # Gerçek bir tarayıcı gibi görünmek için User-Agent ekliyoruz
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    stock = yf.Ticker(ticker_symbol, session=session)
    return stock.history(period="10d")
# ----------------------------------------------

# 1. Kullanıcıdan Hisse Kodu Al
ticker = st.text_input("Hisse Sembolü Giriniz (Örn: THYAO.IS, AAPL, MSFT):", value="THYAO.IS")

if st.button("Canlı Veri Çek ve Tahmin Et"):
    try:
        # Rate limit korumalı fonksiyonumuz ile veriyi çekiyoruz
        df = fetch_stock_history(ticker)

        if len(df) < 5:
            st.error("Yeterli geçmiş veri bulunamadı.")
        else:
            # Otomatik Feature Engineering
            open_price = float(df['Open'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            close_lag1 = float(df['Close'].iloc[-2]) # Dünkü kapanış
            ma_5 = float(df['Close'].tail(5).mean())   # Son 5 günün hareketli ortalaması

            # Metrikleri Ekranda Göster
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Açılış", f"{open_price:.2f}")
            col2.metric("Hacim", f"{volume:,.0f}")
            col3.metric("Dünkü Kapanış", f"{close_lag1:.2f}")
            col4.metric("5 Günlük MA", f"{ma_5:.2f}")

            # Backend API İstek Payload'ı
            payload = {
                "Open": open_price,
                "Volume": volume,
                "Close_Lag1": close_lag1,
                "MA_5": ma_5
            }

            # FastAPI'ye İstek At
            response = requests.post(f"{BACKEND_URL}/tahmin", json=payload)

            if response.status_code == 200:
                result = response.json()
                tahmin = result.get("tahmin_edilen_getiri_yuzdesi")
                st.success(f"**Tahmin Edilen Gelecek Getiri:** %{tahmin}")
                st.caption(f"Log ID: {result.get('log_id')}")
            else:
                st.error("Backend API hatası oluştu.")

    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {str(e)}")
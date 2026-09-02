import streamlit as st
import requests
import os
import yfinance as yf
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.write("Canlı veri akışı ve MLflow entegreli tahmin sistemi.")

# --- YAHOO FINANCE RATE LIMIT ABSOLUTE FIX ---
@st.cache_data(ttl=1800, show_spinner=False)  # Veriyi 30 dakika hafızada tutar
def fetch_stock_history(ticker_symbol):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    
    # yf.Ticker yerine doğrudan session destekleyen yf.download kullanımı
    df = yf.download(
        tickers=ticker_symbol,
        period="15d",
        interval="1d",
        session=session,
        progress=False
    )
    
    # Çift seviyeli kolon başlığı hatasını düzeltme (MultiIndex Fix)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    return df
# ---------------------------------------------

# 1. Kullanıcıdan Hisse Kodu Al
ticker = st.text_input("Hisse Sembolü Giriniz (Örn: THYAO.IS, AAPL, MSFT):", value="THYAO.IS")

if st.button("Canlı Veri Çek ve Tahmin Et"):
    try:
        df = fetch_stock_history(ticker)

        if df.empty or len(df) < 5:
            st.error("Yeterli geçmiş veri bulunamadı veya Yahoo geçici yanıt vermiyor.")
        else:
            # Feature Engineering
            open_price = float(df['Open'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            close_lag1 = float(df['Close'].iloc[-2])
            ma_5 = float(df['Close'].tail(5).mean())

            # Metrikleri Göster
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
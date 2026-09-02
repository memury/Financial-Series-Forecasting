import streamlit as st
import requests
import os
import yfinance as yf
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.write("Canlı veri akışı ve MLflow entegreli tahmin sistemi.")

# --- KESİN RECOVERY DATA FETCH (yfinance Session Injection) ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_history_safe(ticker_symbol):
    clean_symbol = ticker_symbol.strip().replace('ı', 'i').replace('I', 'i').upper()
    
    # Custom Session Oluşturma (User-Agent ile WAF bypass)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    })
    
    try:
        ticker_obj = yf.Ticker(clean_symbol, session=session)
        df = ticker_obj.history(period="1mo", interval="1d")
        
        if df.empty:
            df = yf.download(clean_symbol, period="1mo", interval="1d", session=session, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        return df
    except Exception as e:
        st.error(f"Detaylı Hata Akışı: {str(e)}")
        return pd.DataFrame()
# -----------------------------------------------------------------

ticker = st.text_input("Hisse Sembolü Giriniz (Örn: THYAO.IS, AAPL, MSFT):", value="THYAO.IS")

if st.sidebar.button("Önbelleği Temizle"):
    st.cache_data.clear()
    st.success("Önbellek temizlendi!")

if st.button("Canlı Veri Çek ve Tahmin Et"):
    try:
        df = fetch_stock_history_safe(ticker)

        if df.empty or len(df) < 5:
            st.error("Veri çekilemedi. Lütfen sol menüden 'Önbelleği Temizle' butonuna basıp tekrar deneyin.")
        else:
            open_price = float(df['Open'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            close_lag1 = float(df['Close'].iloc[-2])
            ma_5 = float(df['Close'].tail(5).mean())

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Açılış", f"{open_price:.2f}")
            col2.metric("Hacim", f"{volume:,.0f}")
            col3.metric("Dünkü Kapanış", f"{close_lag1:.2f}")
            col4.metric("5 Günlük MA", f"{ma_5:.2f}")

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
        st.error(f"Uygulama hatası: {str(e)}")
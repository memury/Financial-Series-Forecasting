import streamlit as st
import requests
import os
import pandas as pd
from io import StringIO

RAW_BACKEND_URL = os.getenv("BACKEND_URL", "https://financial-series-forecasting.onrender.com")
BACKEND_URL = RAW_BACKEND_URL.rstrip("/")

st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.write("Canlı veri akışı ve MLflow entegreli tahmin sistemi.")

# --- AUTO-TRANSLATING STOOQ ENGINE ---
@st.cache_data(ttl=60, show_spinner=False)
def fetch_bist_data_stooq(ticker_symbol):
    clean_symbol = ticker_symbol.strip().upper()
    
    # BIST Hisseleri için Otomatik Sembol Çevirici (.IS -> .TR)
    if clean_symbol.endswith(".IS"):
        stooq_symbol = clean_symbol.replace(".IS", ".TR").lower()
    elif not "." in clean_symbol and clean_symbol not in ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]:
        stooq_symbol = f"{clean_symbol}.tr".lower()
    else:
        stooq_symbol = clean_symbol.lower()
    
    url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and "Date,Open,High,Low,Close" in res.text:
            df = pd.read_csv(StringIO(res.text))
            df = df.dropna()
            if len(df) >= 2:
                # En güncel tarih en alta gelecek şekilde sırala
                df = df.iloc[::-1].reset_index(drop=True)
                return df
    except Exception:
        pass
        
    return pd.DataFrame()
# -----------------------------------------------------------------

ticker = st.text_input("Hisse Sembolü Giriniz (Örn: THYAO.IS, AAPL, MSFT):", value="THYAO.IS")

if st.sidebar.button("Önbelleği Temizle"):
    st.cache_data.clear()
    st.success("Önbellek temizlendi!")

if st.button("Canlı Veri Çek ve Tahmin Et"):
    try:
        df = fetch_bist_data_stooq(ticker)

        if df.empty or len(df) < 2:
            st.error("Veri çekilemedi. Lütfen sembolü kontrol edin veya sol menüden 'Önbelleği Temizle' butonuna basın.")
        else:
            open_price = float(df['Open'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            close_lag1 = float(df['Close'].iloc[-2])
            ma_5 = float(df['Close'].tail(5).mean())

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Açılış (TL)", f"{open_price:.2f}")
            col2.metric("Hacim", f"{volume:,.0f}")
            col3.metric("Dünkü Kapanış", f"{close_lag1:.2f}")
            col4.metric("5 Günlük MA", f"{ma_5:.2f}")

            payload = {
                "Open": open_price,
                "Volume": volume,
                "Close_Lag1": close_lag1,
                "MA_5": ma_5
            }

            response = requests.post(f"{BACKEND_URL}/tahmin", json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                tahmin = result.get("tahmin_edilen_getiri_yuzdesi")
                st.success(f"**Tahmin Edilen Gelecek Getiri:** %{tahmin}")
                st.caption(f"Log ID: {result.get('log_id')}")
            else:
                st.error(f"Backend API hatası oluştu. Status Code: {response.status_code}")

    except Exception as e:
        st.error(f"Uygulama hatası: {str(e)}")
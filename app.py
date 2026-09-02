import streamlit as st
import requests
import os
import pandas as pd
from io import StringIO

RAW_BACKEND_URL = os.getenv("BACKEND_URL", "https://financial-series-forecasting.onrender.com")
BACKEND_URL = RAW_BACKEND_URL.rstrip("/")

st.set_page_config(page_title="Borsa MLOps SaaS", layout="wide")
st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.caption("Gün Sonu (EOD) Otomatik Veri Entegrasyonu ve Model Çıkarım Arayüzü")

# --- GÜN SONU (EOD) RESILIENT DATA ENGINE ---
@st.cache_data(ttl=3600, show_spinner=False) # Gün sonu verisi olduğu için 1 saat önbellekte tutulur
def fetch_eod_market_data(ticker_symbol):
    clean_symbol = ticker_symbol.strip().upper()
    
    # BIST (.IS -> .TR) & Yabancı Borsa Dönüştürücü
    if clean_symbol.endswith(".IS"):
        stooq_symbol = clean_symbol.replace(".IS", ".TR").lower()
    elif "." not in clean_symbol and clean_symbol not in ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]:
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
            if len(df) >= 5:
                # Veriyi kronolojik sıraya al (En eski -> En yeni)
                df = df.iloc[::-1].reset_index(drop=True)
                return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)
        
    return pd.DataFrame(), "Veri kümesi boş döndü veya sembol bulunamadı."
# -----------------------------------------------------------------

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, GARAN.IS, AAPL):", value="THYAO.IS")

if st.sidebar.button("Önbelleği Temizle"):
    st.cache_data.clear()
    st.success("Gün sonu verileri temizlendi!")

if st.button("Gün Sonu Verilerini Çek ve Tahmin Et"):
    with st.spinner("Gün sonu borsa verileri işleniyor..."):
        df, err = fetch_eod_market_data(ticker)

        if df.empty or len(df) < 5:
            st.error(f"Gün sonu verisi alınamadı: {err}")
        else:
            # En son günün (EOD) değerleri
            last_date = str(df['Date'].iloc[-1])
            open_price = float(df['Open'].iloc[-1])
            close_price = float(df['Close'].iloc[-1])
            volume = float(df['Volume'].iloc[-1])
            close_lag1 = float(df['Close'].iloc[-2])
            ma_5 = float(df['Close'].tail(5).mean())

            st.info(f"🗓️ **Son Güncelleme Tarihi (EOD):** {last_date}")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Açılış", f"{open_price:.2f} TL")
            col2.metric("Son Kapanış", f"{close_price:.2f} TL")
            col3.metric("Önceki Kapanış", f"{close_lag1:.2f} TL")
            col4.metric("5 Günlük MA", f"{ma_5:.2f} TL")

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
                st.success(f"🎯 **Gelecek Seans Tahmin Edilen Getiri:** %{tahmin}")
                st.caption(f"Log ID: {result.get('log_id')}")
            else:
                st.error(f"Backend API Hatası. Status Code: {response.status_code}")
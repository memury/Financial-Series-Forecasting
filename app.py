import streamlit as st
import requests
import os
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("📈 Borsa Getiri Tahmin & MLOps SaaS")
st.write("Canlı veri akışı ve MLflow entegreli tahmin sistemi.")

# --- DIRECT STOOQ CSV FETCH (Otomatik .US Ekini Engeller) ---
@st.cache_data(ttl=900)
def fetch_stock_history_stooq(ticker_symbol):
    symbol = ticker_symbol.strip().upper()
    
    # Sembol dönüşüm kontrolü
    if symbol.endswith(".IS"):
        stooq_symbol = symbol.replace(".IS", ".TR")
    elif "." not in symbol:
        stooq_symbol = f"{symbol}.US"
    else:
        stooq_symbol = symbol

    # Stooq CSV Endpoint'ine doğrudan bağlanıyoruz
    url = f"https://stooq.com/q/d/l/?s={stooq_symbol.lower()}&i=d"
    
    df = pd.read_csv(url)
    
    if df.empty or 'Date' not in df.columns:
        return pd.DataFrame()

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    return df
# ------------------------------------------------------------

ticker = st.text_input("Hisse Sembolü Giriniz (Örn: THYAO.IS, AAPL, MSFT):", value="THYAO.IS")

if st.button("Canlı Veri Çek ve Tahmin Et"):
    try:
        df = fetch_stock_history_stooq(ticker)

        if df.empty or len(df) < 5:
            st.error("Yeterli geçmiş veri bulunamadı veya Stooq geçici yanıt veremiyor.")
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
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# 1. FastAPI Uygulaması
app = FastAPI(title="Borsa Getiri Tahmin API")

# 2. Modeli Yükle (.pkl dosyası main.py ile aynı klasörde olmalı)
model = joblib.load("borsa_modeli.pkl")

# 3. Girdi Şablonu
class BorsaGirdileri(BaseModel):
    Open: float
    Volume: float
    Close_Lag1: float
    MA_5: float

# 4. Tahmin Endpoint'i
@app.post("/tahmin")
def tahmin_et(veri: BorsaGirdileri):
    girdi_dizisi = np.array([[veri.Open, veri.Volume, veri.Close_Lag1, veri.MA_5]])
    tahmin = model.predict(girdi_dizisi)[0]
    
    return {
        "durum": "basarili",
        "tahmin_edilen_getiri_yuzdesi": round(float(tahmin), 4)
    }
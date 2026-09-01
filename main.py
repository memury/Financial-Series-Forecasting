from fastapi import FastAPI, Depends
from pydantic import BaseModel
import joblib
import numpy as np
from sqlalchemy.orm import Session
from database import get_db, PredictionLog

# 1. FastAPI Uygulaması
app = FastAPI(title="Borsa Getiri Tahmin API")

# 2. Modeli Yükle
model = joblib.load("borsa_modeli.pkl")

# 3. Girdi Şablonu
class BorsaGirdileri(BaseModel):
    Open: float
    Volume: float
    Close_Lag1: float
    MA_5: float

# 4. Tahmin Endpoint'i (Veritabanı Entegreli)
@app.post("/tahmin")
def tahmin_et(veri: BorsaGirdileri, db: Session = Depends(get_db)):
    # Model Tahmini
    girdi_dizisi = np.array([[veri.Open, veri.Volume, veri.Close_Lag1, veri.MA_5]])
    tahmin = model.predict(girdi_dizisi)[0]
    tahmin_yuzdesi = round(float(tahmin), 4)

    # Veritabanına İstek ve Tahmin Kaydı
    log_entry = PredictionLog(
        open_price=veri.Open,
        volume=veri.Volume,
        close_lag1=veri.Close_Lag1,
        ma_5=veri.MA_5,
        predicted_return=tahmin_yuzdesi
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return {
        "durum": "basarili",
        "tahmin_edilen_getiri_yuzdesi": tahmin_yuzdesi,
        "log_id": log_entry.id
    }
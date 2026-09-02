from fastapi import FastAPI, Depends
from pydantic import BaseModel
import pandas as pd
import mlflow.sklearn
from sqlalchemy.orm import Session
from database import get_db, PredictionLog, engine, Base 

# Veritabanı Tabloları
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Borsa Getiri Tahmin API (MLflow)")

# --- DEĞİŞEN KISIM: Modeli MLflow Havuzundan Yüklüyoruz ---
MODEL_URI = "models:/BorsaModeli/1"
model = mlflow.sklearn.load_model(MODEL_URI)
# ---------------------------------------------------------

class BorsaGirdileri(BaseModel):
    Open: float
    Volume: float
    Close_Lag1: float
    MA_5: float

@app.post("/tahmin")
def tahmin_et(veri: BorsaGirdileri, db: Session = Depends(get_db)):
    # Girdiyi DataFrame'e çeviriyoruz
    girdi_df = pd.DataFrame([{
        "Open": veri.Open,
        "Volume": veri.Volume,
        "Close_Lag1": veri.Close_Lag1,
        "MA_5": veri.MA_5
    }])
    
    # MLflow'dan gelen modelle tahmin
    tahmin = model.predict(girdi_df)[0]
    tahmin_yuzdesi = round(float(tahmin), 4)

    # Veritabanına Kayıt
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
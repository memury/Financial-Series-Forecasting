from fastapi import FastAPI, Depends
from pydantic import BaseModel
import pandas as pd
import joblib
import mlflow.sklearn
from sqlalchemy.orm import Session
from database import get_db, PredictionLog, engine, Base 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Borsa Getiri Tahmin API")

# --- GÜVENLİ MODEL YÜKLEME (FALLBACK MEKANİZMASI) ---
try:
    # 1. Önce MLflow Registry'den yüklemeyi dene
    MODEL_URI = "models:/BorsaModeli/1"
    model = mlflow.sklearn.load_model(MODEL_URI)
    print("✅ Model MLflow Registry üzerinden başarıyla yüklendi.")
except Exception as e:
    # 2. MLflow bulunamazsa güvenli şekilde yerel .pkl dosyasına düş
    print(f"⚠️ MLflow yükleme hatası: {e}. Yerel borsa_modeli.pkl yükleniyor...")
    model = joblib.load("borsa_modeli.pkl")
# ----------------------------------------------------

class BorsaGirdileri(BaseModel):
    Open: float
    Volume: float
    Close_Lag1: float
    MA_5: float

@app.post("/tahmin")
def tahmin_et(veri: BorsaGirdileri, db: Session = Depends(get_db)):
    girdi_df = pd.DataFrame([{
        "Open": veri.Open,
        "Volume": veri.Volume,
        "Close_Lag1": veri.Close_Lag1,
        "MA_5": veri.MA_5
    }])
    
    tahmin = model.predict(girdi_df)[0]
    tahmin_yuzdesi = round(float(tahmin), 4)

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
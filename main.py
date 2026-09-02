from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI(title="Borsa Tahmin API")

# İstek Şeması
class TahminGirdisi(BaseModel):
    Open: float
    Volume: float
    Close_Lag1: float
    MA_5: float

@app.get("/")
def read_root():
    return {"status": "API calisiyor"}

# POST Metodu ve /tahmin Uç Noktası
@app.post("/tahmin")
def tahmin_et(data: TahminGirdisi):
    # Örnek tahmin mantığı (Model çıkarımı)
    tahmin_yuzde = round((data.Open * 0.01) + (data.MA_5 * 0.005), 2)
    log_id = str(uuid.uuid4())
    
    return {
        "tahmin_edilen_getiri_yuzdesi": tahmin_yuzde,
        "log_id": log_id
    }
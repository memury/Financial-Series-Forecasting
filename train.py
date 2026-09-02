import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn

# 1. Deney Adını Belirle
mlflow.set_experiment("Borsa_Getiri_Tahmin_Sistemi")

with mlflow.start_run():
    # Modelin eğitileceği örnek veri
    X = pd.DataFrame({
        "Open": [100, 102, 101, 105, 107],
        "Volume": [1000, 1200, 1100, 1500, 1300],
        "Close_Lag1": [99, 101, 100, 104, 106],
        "MA_5": [98, 100, 99.5, 102, 104]
    })
    y = np.array([0.02, -0.01, 0.03, 0.015, -0.005])

    # 2. Modeli Eğit
    model = LinearRegression()
    model.fit(X, y)

    # 3. Performans Ölçümü
    predictions = model.predict(X)
    mse = mean_squared_error(y, predictions)
    r2 = r2_score(y, predictions)

    # 4. MLflow Kayıtları
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("r2", r2)

    # 5. Modeli MLflow Registry'ye Kaydet
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="BorsaModeli"
    )

    print("TEBRİKLER: Model eğitildi ve MLflow Registry'ye kaydoldu!")
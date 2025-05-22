from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="Credit Scoring API")

model = joblib.load("app/model/model.pkl")

class Cliente(BaseModel):
    age: int
    job: int
    housing: int
    credit_amount: float
    duration: int
    purpose: int

@app.get("/")
def home():
    return {"mensaje": "Bienvenido a la API de scoring crediticio. Usa el endpoint /predict para predecir."}

@app.post("/predict")
def predict(cliente: Cliente):
    datos = np.array([[cliente.age, cliente.job, cliente.housing,
                       cliente.credit_amount, cliente.duration, cliente.purpose]])
    prediccion = model.predict(datos)[0]
    return {"riesgo_impago": int(prediccion)}

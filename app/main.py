from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import pandas as pd
import sqlite3
import os
import joblib

app = FastAPI(title="API de Scoring Crediticio")

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model", "modelo_entrenado.pkl")
DB_PATH = os.path.join(BASE_DIR, "database", "clientes.db")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"No se pudo cargar el modelo: {e}")

class Cliente(BaseModel):
    person_age: int
    person_income: float
    person_home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER"]
    person_emp_exp: float
    loan_amnt: float
    loan_intent: Literal[
        "PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"
    ]
    person_education: Literal[
        "Master", "High School", "Bachelor", "Associate", "Doctorate"
    ]
    person_gender: Literal["female", "male"]
    previous_loan_defaults_on_file: int
    credit_score: float

@app.get("/")
def home():
    return {"mensaje": "Bienvenido a la API de scoring. Usa el endpoint /predict para hacer una predicción."}

@app.post("/predict")
def predict(cliente: Cliente):
    try:
        df = pd.DataFrame([cliente.dict()])

        df["person_age"] = pd.to_numeric(df["person_age"], errors="coerce")
        df["person_income"] = pd.to_numeric(df["person_income"], errors="coerce")
        df["person_emp_exp"] = pd.to_numeric(df["person_emp_exp"], errors="coerce")
        df["loan_amnt"] = pd.to_numeric(df["loan_amnt"], errors="coerce")
        df["previous_loan_defaults_on_file"] = pd.to_numeric(df["previous_loan_defaults_on_file"], errors="coerce")
        df["credit_score"] = pd.to_numeric(df["credit_score"], errors="coerce")

        if df.isnull().any().any():
            return {"error": "Algunos campos numéricos no son válidos. Revisa los tipos."}

        pred = model.predict(df)[0]

    except Exception as e:
        return {"error": f"Error al hacer la predicción: {e}"}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predicciones (
                person_age, person_income, person_home_ownership, person_emp_exp,
                loan_amnt, loan_intent, person_education, person_gender,
                previous_loan_defaults_on_file, credit_score, resultado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (*cliente.dict().values(), int(pred))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        return {"error": f"Error al guardar en la base de datos: {e}"}

    return {"resultado": "Aprobado" if pred == 1 else "No aprobado"}


# uvicorn app.main:app --reload
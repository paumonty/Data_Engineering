import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "clientes.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predicciones (
    person_age INTEGER,
    person_income REAL,
    person_home_ownership TEXT,
    person_emp_exp REAL,
    loan_amnt REAL,
    loan_intent TEXT,
    person_education TEXT,
    person_gender TEXT,
    previous_loan_defaults_on_file INTEGER,
    credit_score REAL,
    resultado INTEGER
)
""")

conn.commit()
conn.close()
print("Base de datos creada correctamente.")


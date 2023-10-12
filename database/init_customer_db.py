import sqlite3
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import database

database_dir = "data/raw/telco_customer_churn.db"
conn = sqlite3.connect(database_dir)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customers (
        customerID TEXT PRIMARY KEY,
        gender TEXT,
        SeniorCitizen INTEGER,
        Partner TEXT,
        Dependents TEXT,
        tenure INTEGER,
        PhoneService TEXT,
        MultipleLines TEXT,
        InternetService TEXT,
        OnlineSecurity TEXT,
        OnlineBackup TEXT,
        DeviceProtection TEXT,
        TechSupport TEXT,
        StreamingTV TEXT,
        StreamingMovies TEXT,
        Contract TEXT,
        PaperlessBilling TEXT,
        PaymentMethod TEXT,
        MonthlyCharges REAL,
        TotalCharges REAL,
        Churn TEXT
    )
"""
)
conn.close()

Base = declarative_base()

engine = create_engine(f"sqlite:///{database_dir}")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

data_dir = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
data = pd.read_csv(data_dir)
data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")

for _, row in data.iterrows():
    customer = database.Customer(**row.to_dict())
    session.add(customer)

session.commit()

session.close()

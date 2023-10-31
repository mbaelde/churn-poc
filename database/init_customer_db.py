from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import (
    Base,
    Contract,
    Customer,
    CustomerChurn,
    InternetService,
    PhoneService,
)

# Create an SQLite database (You can use a different database URL if needed)
database_url = "sqlite:///customers.db"
engine = create_engine(database_url)

# Create tables in the database
Base.metadata.create_all(engine)

# Initialize a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

data_dir = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
data = pd.read_csv(data_dir)
data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
data["SeniorCitizen"] = data["SeniorCitizen"].map({0: "No", 1: "Yes"})

for _, row in data.iterrows():
    phone_service = PhoneService(
        hasPhoneService=row["PhoneService"], multipleLines=row["MultipleLines"]
    )
    internet_service = InternetService(
        internetServiceType=row["InternetService"],
        onlineSecurity=row["OnlineSecurity"],
        onlineBackup=row["OnlineBackup"],
        deviceProtection=row["DeviceProtection"],
        techSupport=row["TechSupport"],
        streamingTV=row["StreamingTV"],
        streamingMovies=row["StreamingMovies"],
    )
    contract = Contract(
        contractType=row["Contract"],
        tenure=row["tenure"],
        paperlessBilling=row["PaperlessBilling"],
        paymentMethod=row["PaymentMethod"],
        monthlyCharges=row["MonthlyCharges"],
        totalCharges=row["TotalCharges"],
        phone_service=phone_service,
        internet_service=internet_service,
    )
    customer_churn = CustomerChurn(churn=row["Churn"])

    customer = Customer(
        id=row["customerID"],
        gender=row["gender"],
        seniorCitizen=row["SeniorCitizen"],
        partner=row["Partner"],
        dependents=row["Dependents"],
        contracts=[contract],
        churns=[customer_churn],
    )

    session.add(customer)

session.commit()

session.close()

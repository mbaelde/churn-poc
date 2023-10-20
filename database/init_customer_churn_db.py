import os
import sqlite3

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from database.models import get_customer, create_customer

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customer_churn (
        id TEXT PRIMARY KEY NOT NULL,
        customerID TEXT,
        churn_prediction TEXT
    )
"""
)
conn.close()


# Step 1: Create a SQLAlchemy database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Step 2: Define your database model
Base = declarative_base()

# Step 3: Create the database tables
Base.metadata.create_all(bind=engine)

# Create a new customer entry
db = SessionLocal()
create_customer(db, customerID="12345", churn_prediction="Churn")

# Retrieve customer data
customer = get_customer(db, customerID="12345")
if customer:
    print(
        f"Customer ID: {customer.customerID}, Churn Prediction: {customer.churn_prediction}"
    )
else:
    print("Customer not found.")

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customerID = Column(String, primary_key=True)
    gender = Column(String)
    SeniorCitizen = Column(Integer)
    Partner = Column(String)
    Dependents = Column(String)
    tenure = Column(Integer)
    PhoneService = Column(String)
    MultipleLines = Column(String)
    InternetService = Column(String)
    OnlineSecurity = Column(String)
    OnlineBackup = Column(String)
    DeviceProtection = Column(String)
    TechSupport = Column(String)
    StreamingTV = Column(String)
    StreamingMovies = Column(String)
    Contract = Column(String)
    PaperlessBilling = Column(String)
    PaymentMethod = Column(String)
    MonthlyCharges = Column(Float)
    TotalCharges = Column(Float)
    Churn = Column(String)

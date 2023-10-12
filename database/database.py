from sqlalchemy import Column, Float, Integer, String, func
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


class CustomerChurn(Base):
    __tablename__ = "customer_churn"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customerID = Column(String, unique=True, index=True)
    churn_prediction = Column(String)


# Step 4: Interact with the database (e.g., insert data)
def create_customer(db, customerID: str, churn_prediction: str):
    id_max = int(db.query(func.max(CustomerChurn.id)).scalar())
    db_customer = CustomerChurn(
        id=id_max + 1, customerID=customerID, churn_prediction=churn_prediction
    )
    db.add(db_customer)
    db.commit()


#    db.refresh(db_customer)


def get_customer(db, customerID: str):
    return (
        db.query(CustomerChurn).filter(CustomerChurn.customerID == customerID).first()
    )

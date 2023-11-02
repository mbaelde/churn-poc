# api/schemas/prediction.py

from pydantic import BaseModel


class CustomerData(BaseModel):
    customerID: str
    gender: str
    seniorCitizen: str
    partner: str
    dependents: str
    tenure: int
    hasPhoneService: str
    multipleLines: str
    internetServiceType: str
    onlineSecurity: str
    onlineBackup: str
    deviceProtection: str
    techSupport: str
    streamingTV: str
    streamingMovies: str
    contractType: str
    paperlessBilling: str
    paymentMethod: str
    monthlyCharges: float
    totalCharges: float


class CustomerChurnPrediction(BaseModel):
    churnPrediction: str

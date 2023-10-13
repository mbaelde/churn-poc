import os

from dotenv import load_dotenv
from fastapi import FastAPI
from api.routers.prediction import predict_churn
from api.schemas.prediction import CustomerData

load_dotenv()

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

app = FastAPI()


@app.post("/predict-churn")
async def predict_churn_endpoint(data: CustomerData):
    prediction = predict_churn(data)
    return {"Churn Prediction": prediction}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

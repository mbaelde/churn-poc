from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.prediction import predict_churn
from schemas.prediction import CustomerData

app = FastAPI()

# Enable CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict-churn")
async def predict_churn_endpoint(data: CustomerData):
    prediction = predict_churn(data)
    return {"Churn Prediction": prediction}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

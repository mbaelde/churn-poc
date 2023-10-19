import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from api.routers.prediction import predict_churn
from api.schemas.prediction import CustomerData

security = HTTPBasic()
load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=secret_key)

fake_users_db = {"testuser": {"password": "testpassword"}}


def form_input_to_dict(form_input: str) -> dict:
    # Split the input string by '&' to separate key-value pairs
    key_value_pairs = form_input.split("&")

    # Create a dictionary to store the parsed values
    data_dict = {}

    for key_value in key_value_pairs:
        key, value = key_value.split("=")
        # Convert the value to the appropriate data type based on the CustomerData class
        if key in CustomerData.__annotations__:
            data_type = CustomerData.__annotations__[key]
            if data_type == int:
                value = int(value)
            elif data_type == float:
                value = float(value)
            # Add the key-value pair to the dictionary
            data_dict[key] = value

    return data_dict


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if user is None or user["password"] != password:
        return templates.TemplateResponse(
            "login.html", {"request": request, "message": "Invalid credentials"}
        )

    # Set a session variable to track the user's authentication
    request.session["user"] = username

    # Redirect to a protected route
    return templates.TemplateResponse("prediction.html", {"request": request})


@app.post("/predict-churn")
async def predict_churn_endpoint(
    data: dict, credentials: HTTPBasicCredentials = Depends(security)
):
    user = fake_users_db.get(credentials.username)
    if user is None or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    data = CustomerData(**data)
    prediction = predict_churn(data)
    return {"Churn Prediction": prediction}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

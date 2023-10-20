import os
import sqlite3

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from api.routers.prediction import predict_churn
from api.schemas.prediction import CustomerChurnPrediction, CustomerData

# Create FastAPI app
app = FastAPI()

# Initialize Jinja2Templates for HTML templates
templates = Jinja2Templates(directory="templates")

# Set up session middleware with secret key
load_dotenv()
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=secret_key)

# Simulated user database
fake_users_db = {"testuser": {"password": "testpassword"}}


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Response containing the login page.

    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/churn-prediction", response_class=HTMLResponse)
async def churn_prediction_page(request: Request):
    return templates.TemplateResponse("prediction.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle user login.

    Args:
        request (Request): The request object.
        username (str): User's username (Form parameter).
        password (str): User's password (Form parameter).

    Returns:
        HTMLResponse: Response with authentication status or redirection.

    """
    user = fake_users_db.get(username)
    if user is None or user["password"] != password:
        return templates.TemplateResponse(
            "login.html", {"request": request, "message": "Invalid credentials"}
        )

    # Set a session variable to track the user's authentication
    request.session["user"] = username

    # Redirect to a protected route
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.post("/predict-churn")
async def predict_churn_endpoint(data: dict) -> CustomerChurnPrediction:
    """Predict churn based on customer data.

    Args:
        data (dict): Customer data for prediction.

    Returns:
        dict: Prediction result.

    """
    data = CustomerData(**data)
    prediction = predict_churn(data)
    return CustomerChurnPrediction(**{"churnPrediction": prediction})


# SQLite database file
db_file = "data/raw/telco_customer_churn.db"


def fetch_customer_ids():
    customer_ids = []
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT customerID FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return customer_ids


@app.get("/customer-database", response_class=HTMLResponse)
async def customer_database_page(request: Request):
    # Fetch customer IDs from the database
    customer_ids = fetch_customer_ids()

    return templates.TemplateResponse(
        "customer-database.html", {"request": request, "customer_ids": customer_ids}
    )


def fetch_customer_info(customerID):
    customer_info = {}
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Execute a SQL query to fetch customer information by customerID
        cursor.execute("SELECT * FROM customers WHERE customerID=?", (customerID,))
        customer_data = cursor.fetchone()  # Fetch the first matching record

        if customer_data:
            # The cursor.fetchone() result is a tuple with columns in order
            customer_info = {
                "customerID": customer_data[0],
                "gender": customer_data[1],
                "SeniorCitizen": customer_data[2],
                "Partner": customer_data[3],
                "Dependents": customer_data[4],
                "tenure": customer_data[5],
                "PhoneService": customer_data[6],
                "MultipleLines": customer_data[7],
                "InternetService": customer_data[8],
                "OnlineSecurity": customer_data[9],
                "OnlineBackup": customer_data[10],
                "DeviceProtection": customer_data[11],
                "TechSupport": customer_data[12],
                "StreamingTV": customer_data[13],
                "StreamingMovies": customer_data[14],
                "Contract": customer_data[15],
                "PaperlessBilling": customer_data[16],
                "PaymentMethod": customer_data[17],
                "MonthlyCharges": customer_data[18],
                "TotalCharges": customer_data[19],
                "Churn": customer_data[20],
            }
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return customer_info


@app.post("/customer-database/access", response_class=HTMLResponse)
async def access_customer(request: Request, customerID: str = Form(...)):
    # Fetch the customer's information based on customerID
    customer_info = fetch_customer_info(customerID)
    customer_ids = fetch_customer_ids()

    return templates.TemplateResponse(
        "customer-database.html",
        {
            "request": request,
            "customer_info": customer_info,
            "customer_ids": customer_ids,
        },
    )


@app.post("/customer-database/add", response_class=HTMLResponse)
async def add_customer(request: Request, customer_data: dict = Form(...)):
    # You can implement code to add a new customer with the provided data
    # Replace the following line with your database insert logic
    # Insert customer_data into your database
    return templates.TemplateResponse(
        "customer-database.html", {"request": request, "message": "Customer added"}
    )


@app.post("/customer-database/delete", response_class=HTMLResponse)
async def delete_customer(request: Request, customerID: str = Form(...)):
    # You can implement code to delete a customer based on customerID
    # Replace the following line with your database delete logic
    # Delete the customer with customerID from your database
    return templates.TemplateResponse(
        "customer-database.html", {"request": request, "message": "Customer deleted"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

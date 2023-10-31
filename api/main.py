import os

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.sessions import SessionMiddleware

from api.routers.prediction import predict_churn
from api.schemas.prediction import CustomerChurnPrediction, CustomerData
from database.models import (
    Base,
    Contract,
    Customer,
    CustomerChurn,
    InternetService,
    PhoneService,
)
from utils.logger import DEBUG, INFO, setup_logger

logger = setup_logger("api_main")

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

# Create an SQLite database (You can use a different database URL if needed)
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

# Create tables in the database
Base.metadata.create_all(engine)

# Initialize a session to interact with the database
Session = sessionmaker(bind=engine)


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


@app.post("/churn-prediction/predict-churn")
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


def fetch_customer_ids():
    customer_ids = []

    with Session() as session:
        # Retrieve customer IDs from the Customer table
        customer_ids = [customer.id for customer in session.query(Customer).all()]
        customer_ids.sort()
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
    with Session() as session:
        # Use SQLAlchemy to fetch customer data by customer ID and join multiple tables
        customer_data = (
            session.query(
                Customer.id,
                Customer.gender,
                Customer.seniorCitizen,
                Customer.partner,
                Customer.dependents,
                Contract.tenure,
                PhoneService.hasPhoneService,
                PhoneService.multipleLines,
                InternetService.internetServiceType,
                InternetService.onlineSecurity,
                InternetService.onlineBackup,
                InternetService.deviceProtection,
                InternetService.techSupport,
                InternetService.streamingTV,
                InternetService.streamingMovies,
                Contract.contractType,
                Contract.paperlessBilling,
                Contract.paymentMethod,
                Contract.monthlyCharges,
                Contract.totalCharges,
                CustomerChurn.churn,
            )
            .join(Contract, Contract.customer_id == Customer.id)
            .join(PhoneService, PhoneService.contract_id == Contract.id)
            .join(InternetService, InternetService.contract_id == Contract.id)
            .join(CustomerChurn, CustomerChurn.customer_id == Customer.id, isouter=True)
            .filter(Customer.id == customerID)
            .first()
        )

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
        else:
            logger.log(INFO, "Customer not found.")

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
async def add_customer(
    request: Request,
    customerID: str = Form(...),
    gender: str = Form(...),
    SeniorCitizen: int = Form(...),
    Partner: str = Form(...),
    Dependents: str = Form(...),
    tenure: int = Form(...),
    phoneService: str = Form(...),
    MultipleLines: str = Form(...),
    internetService: str = Form(...),
    OnlineSecurity: str = Form(...),
    OnlineBackup: str = Form(...),
    DeviceProtection: str = Form(...),
    TechSupport: str = Form(...),
    StreamingTV: str = Form(...),
    StreamingMovies: str = Form(...),
    contract: str = Form(...),
    PaperlessBilling: str = Form(...),
    PaymentMethod: str = Form(...),
    MonthlyCharges: float = Form(...),
    TotalCharges: float = Form(...),
):
    # Add the data to the database
    with Session() as session:
        phone_service = PhoneService(
            hasPhoneService=phoneService, multipleLines=MultipleLines
        )
        internet_service = InternetService(
            internetServiceType=internetService,
            onlineSecurity=OnlineSecurity,
            onlineBackup=OnlineBackup,
            deviceProtection=DeviceProtection,
            techSupport=TechSupport,
            streamingTV=StreamingTV,
            streamingMovies=StreamingMovies,
        )
        contract = Contract(
            contractType=contract,
            tenure=tenure,
            paperlessBilling=PaperlessBilling,
            paymentMethod=PaymentMethod,
            monthlyCharges=MonthlyCharges,
            totalCharges=TotalCharges,
            phone_service=phone_service,
            internet_service=internet_service,
        )

        customer = Customer(
            id=customerID,
            gender=gender,
            seniorCitizen=SeniorCitizen,
            partner=Partner,
            dependents=Dependents,
            contracts=[contract],
        )
        session.add(customer)
        session.commit()

        message = f"Customer {customerID} added successfully"

    customer_ids = fetch_customer_ids()
    return templates.TemplateResponse(
        "customer-database.html",
        {
            "request": request,
            "message_customer_added": message,
            "customer_ids": customer_ids,
        },
    )


def delete_customer_data(session, customer):
    # Delete related data (child tables)
    session.query(CustomerChurn).filter_by(customer_id=customer.id).delete()
    session.query(InternetService).filter_by(contract_id=customer.contract.id).delete()
    session.query(PhoneService).filter_by(contract_id=customer.contract.id).delete()


def delete_customer(session, customer):
    # Delete the customer
    session.delete(customer)


@app.post("/customer-database/delete", response_class=HTMLResponse)
async def delete_customer(
    request: Request, customerID: str = Form(...)
):  # Use a context manager to create and manage a session
    with Session() as session:
        # Retrieve the customer to delete
        customer_to_delete = session.query(Customer).filter_by(id=customerID).first()

        if customer_to_delete:
            contract_to_delete = (
                session.query(Contract)
                .filter_by(customer_id=customer_to_delete.id)
                .first()
            )
            session.query(PhoneService).filter_by(
                contract_id=contract_to_delete.id
            ).delete()
            session.query(InternetService).filter_by(
                contract_id=contract_to_delete.id
            ).delete()
            session.query(CustomerChurn).filter_by(
                customer_id=customer_to_delete.id
            ).delete()

            # Delete the customer
            session.delete(customer_to_delete)
            session.delete(contract_to_delete)
            session.commit()
            message = f"Customer {customerID} deleted successfully"
        else:
            message = f"Customer {customerID} not found"

    customer_ids = fetch_customer_ids()

    return templates.TemplateResponse(
        "customer-database.html",
        {
            "request": request,
            "message_customer_deleted": message,
            "customer_ids": customer_ids,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

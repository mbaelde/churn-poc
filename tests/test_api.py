import json
import unittest

from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

from api.main import Session, app
from database.models import Contract, Customer, InternetService, PhoneService


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.fake_users_db = {"testuser": {"password": "testpassword"}}
        self.templates = Jinja2Templates(directory="templates")

        # Add a test customer to the database
        self.phone_service = PhoneService(
            hasPhoneService="No", multipleLines="No phone service"
        )
        self.internet_service = InternetService(
            internetServiceType="Yes",
            onlineSecurity="No",
            onlineBackup="No",
            deviceProtection="Yes",
            techSupport="Yes",
            streamingTV="Yes",
            streamingMovies="No",
        )
        self.contract = Contract(
            contractType="Month-to-month",
            tenure=5,
            paperlessBilling="Yes",
            paymentMethod="Mailed check",
            monthlyCharges=1,
            totalCharges=1,
            phone_service=self.phone_service,
            internet_service=self.internet_service,
        )
        self.test_customer = Customer(
            id="test_customer_delete",
            gender="Male",
            seniorCitizen=0,
            partner="No",
            dependents="No",
            contracts=[self.contract],
        )

    def test_predict_churn(self):
        # Define a sample request data
        with open("data/example_no_churn.json", "r") as f:
            data = json.load(f)

        # Make a test request to the prediction endpoint
        response = self.client.post("/churn-prediction/predict-churn", json=data)

        # Validate the response
        self.assertEqual(response.status_code, 200)
        prediction = response.json()
        self.assertEqual(prediction, {"churnPrediction": "No Churn"})

    def test_predict_churn_error(self):
        # Define a sample request data
        with open("data/example_churn.json", "r") as f:
            data = json.load(f)

        data["gender"] = "Non binary"

        # Make a test request to the prediction endpoint
        with self.assertRaises(ValueError) as context:
            response = self.client.post("/churn-prediction/predict-churn", json=data)

        exception = context.exception
        self.assertEqual(
            str(exception), "y contains previously unseen labels: 'Non binary'"
        )

    def test_successful_login(self):
        response = self.client.post(
            "/login", data={"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(
            response.status_code, 200
        )  # Modify to your expected status code for success

    def test_failed_login(self):
        response = self.client.post(
            "/login", data={"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(
            response.status_code, 200
        )  # Modify to your expected status code for failure
        self.assertIn("Invalid credentials", response.text)

    def test_add_customer(self):
        with Session() as session:
            # Send a POST request to add a customer
            response = self.client.post(
                "/customer-database/add",
                data={
                    "customerID": "test_customer_add",
                    "gender": "Male",
                    "SeniorCitizen": 0,
                    "Partner": "No",
                    "Dependents": "No",
                    "tenure": 12,
                    "phoneService": "Yes",
                    "MultipleLines": "No",
                    "internetService": "DSL",
                    "OnlineSecurity": "No",
                    "OnlineBackup": "Yes",
                    "DeviceProtection": "No",
                    "TechSupport": "No",
                    "StreamingTV": "No",
                    "StreamingMovies": "No",
                    "contractType": "Month-to-month",
                    "PaperlessBilling": "Yes",
                    "PaymentMethod": "Electronic check",
                    "MonthlyCharges": 49.95,
                    "TotalCharges": 599.40,
                },
            )
            self.assertEqual(response.status_code, 200)

            # Verify the customer is added to the database
            customer = session.query(Customer).filter_by(id="test_customer_add").first()
            self.assertIsNotNone(customer)

    def test_access_customer(self):
        with Session() as session:
            session.add(self.test_customer)
            session.commit()

            # Send a POST request to access the test customer's information
            response = self.client.post(
                "/customer-database/access", data={"customerID": "test_customer_delete"}
            )
            self.assertEqual(response.status_code, 200)

            # Verify the response contains expected customer data
            self.assertIn("test_customer_delete", response.text)

            session.delete(self.phone_service)
            session.delete(self.internet_service)
            session.delete(self.contract)
            session.delete(self.test_customer)
            session.commit()

    def test_delete_customer(self):
        with Session() as session:
            session.add(self.test_customer)
            session.commit()

            # Send a POST request to delete the test customer
            response = self.client.post(
                "/customer-database/delete", data={"customerID": "test_customer_delete"}
            )
            self.assertEqual(response.status_code, 200)

            # Verify the test customer is deleted from the database
            customer = (
                session.query(Customer).filter_by(id="test_customer_delete").first()
            )
            self.assertIsNone(customer)

    def tearDown(self) -> None:
        self.client.post(
            "/customer-database/delete", data={"customerID": "test_customer_add"}
        )


if __name__ == "__main__":
    unittest.main()

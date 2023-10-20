import json
import unittest

from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.fake_users_db = {"testuser": {"password": "testpassword"}}
        self.templates = Jinja2Templates(directory="templates")

    def test_predict_churn(self):
        # Define a sample request data
        with open("data/example_no_churn.json", "r") as f:
            data = json.load(f)

        # Make a test request to the prediction endpoint
        response = client.post("/predict-churn", json=data)

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
            response = client.post("/predict-churn", json=data)

        exception = context.exception
        self.assertEqual(
            str(exception), "y contains previously unseen labels: 'Non binary'"
        )

    def test_successful_login(self):
        response = client.post(
            "/login", data={"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(
            response.status_code, 200
        )  # Modify to your expected status code for success

    def test_failed_login(self):
        response = client.post(
            "/login", data={"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(
            response.status_code, 200
        )  # Modify to your expected status code for failure
        self.assertIn("Invalid credentials", response.text)


if __name__ == "__main__":
    unittest.main()

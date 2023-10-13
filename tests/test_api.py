import json
import unittest

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestAPI(unittest.TestCase):
    def test_predict_churn(self):
        # Define a sample request data
        with open("data/example.json", "r") as f:
            data = json.load(f)

        # Make a test request to the prediction endpoint
        response = client.post("/predict-churn", json=data)

        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("Churn Prediction", response.json())

        # Add more test cases as needed


if __name__ == "__main__":
    unittest.main()

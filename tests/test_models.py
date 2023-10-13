import json
import unittest
from pathlib import Path

import pandas as pd

from api.models import ChurnModel


class TestChurnModel(unittest.TestCase):
    def setUp(self):
        # Create an instance of the ChurnModel
        label_encoded_variables = [
            "gender",
            "Partner",
            "Dependents",
            "PhoneService",
            "PaperlessBilling",
            "Contract",
            "PaymentMethod",
            "TenureGroup",
        ]
        onehot_encoded_variables = [
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
        ]
        standard_scaler_variables = [
            "tenure",
            "MonthlyCharges",
            "TotalCharges",
            "MonthlyTotalChargesRatio",
        ]
        self.churn_model = ChurnModel(
            label_encoded_variables=label_encoded_variables,
            onehot_encoded_variables=onehot_encoded_variables,
            standard_scaler_variables=standard_scaler_variables,
        )
        self.churn_model.deserialize(Path("data/processed"))

        # Sample input data for prediction
        with open("data/example.json", "r") as f:
            self.data = json.load(f)

    def test_churn_prediction(self):

        # Convert the input data to a Pandas DataFrame
        input_data = pd.DataFrame([self.data])

        # Perform the necessary preprocessing steps on the input data
        # (e.g., encoding categorical variables and feature scaling)
        X = self.churn_model.preprocess(input_data)

        # Make a prediction using the model
        prediction = self.churn_model.predict(X)

        # Validate the prediction
        self.assertIn(prediction, [0, 1])


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from models.churn import ChurnModel
from models.features import (
    FeaturePreprocessor,
    MultiColumnLabelEncoder,
    RatioComputer,
    TenureBinarizer,
)


class TestChurnModel(unittest.TestCase):
    def setUp(self):

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

        bins = [0, 12, 24, 36, 48, 60, np.inf]
        labels = [
            "0-1 Year",
            "1-2 Years",
            "2-3 Years",
            "3-4 Years",
            "4-5 Years",
            "5+ Years",
        ]
        tenure_binarizer = FeaturePreprocessor(
            TenureBinarizer(bins=bins, labels=labels),
            encoded_variables=["tenure"],
            output_variables=["tenure", "TenureGroup"],
        )
        ratio_computer = FeaturePreprocessor(
            RatioComputer("MonthlyCharges", "TotalCharges", "MonthlyTotalChargesRatio"),
            encoded_variables=["MonthlyCharges", "TotalCharges"],
            output_variables=[
                "MonthlyCharges",
                "TotalCharges",
                "MonthlyTotalChargesRatio",
            ],
        )
        scaler = FeaturePreprocessor(
            model=StandardScaler(),
            encoded_variables=standard_scaler_variables,
            output_variables=standard_scaler_variables,
        )
        label_encoder = MultiColumnLabelEncoder(
            encoded_variables=label_encoded_variables
        )
        onehot_encoder = FeaturePreprocessor(
            model=OneHotEncoder(sparse=False, drop="first"),
            encoded_variables=onehot_encoded_variables,
            output_variables=onehot_encoded_variables,
            transform_to_dataframe=True,
        )
        preprocessor_dir = Path("data/preprocessors")
        scaler.deserialize(preprocessor_dir.joinpath("standard_scaler.pkl"))
        label_encoder.deserialize(preprocessor_dir.joinpath(f"label_encoder.pkl"))
        onehot_encoder.deserialize(preprocessor_dir.joinpath(f"onehot_encoder.pkl"))

        preprocessors = Pipeline(
            [
                ("tenure_binarizer", tenure_binarizer),
                ("ratio_computer", ratio_computer),
                ("scaler", scaler),
                ("label_encoder", label_encoder),
                ("onehot_encoder", onehot_encoder),
            ]
        )
        self.churn_model = ChurnModel(
            preprocessors=preprocessors,
        )
        models_dir = Path("data/models")
        self.churn_model.deserialize(models_dir.joinpath("churn_model_prod.pkl"))

        # Sample input data for prediction
        with open("data/example_no_churn.json", "r") as f:
            self.data = json.load(f)

    def test_churn_prediction(self):

        # Convert the input data to a Pandas DataFrame
        input_data = pd.DataFrame([self.data])

        # Make a prediction using the model
        prediction = self.churn_model.predict(input_data)

        # Validate the prediction
        self.assertIn(prediction, [0, 1])


if __name__ == "__main__":
    unittest.main()

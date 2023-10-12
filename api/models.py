import pickle
from pathlib import Path
from typing import List

import pandas as pd


class ChurnModel:
    def __init__(
        self,
        label_encoded_variables: List[str],
        onehot_encoded_variables: List[str],
        standard_scaler_variables: List[str],
    ):
        # Initialize and load your trained model and encoders here
        self.label_encoded_variables = label_encoded_variables
        self.onehot_encoded_variables = onehot_encoded_variables
        self.standard_scaler_variables = standard_scaler_variables

    def deserialize(self, processed_data_dir: Path):
        # load prediction model
        with open(processed_data_dir.joinpath("churn_model.pkl"), "rb") as f:
            self.model = pickle.load(f)
        # load label encoders
        self.label_encoder = {}
        for var in self.label_encoded_variables:
            with open(
                processed_data_dir.joinpath(f"label_encoder_{var}.pkl"), "rb"
            ) as f:
                self.label_encoder[var] = pickle.load(f)
        # load onehot encoder
        with open(processed_data_dir.joinpath("onehot_encoder.pkl"), "rb") as f:
            self.onehot_encoder = pickle.load(f)
        # load standard scaler
        with open(processed_data_dir.joinpath("standard_scaler.pkl"), "rb") as f:
            self.standard_scaler = pickle.load(f)

    def preprocess(self, X: pd.DataFrame) -> pd.DataFrame:
        processed_X = X.copy()
        processed_X["TenureGroup"] = pd.cut(
            processed_X["tenure"],
            bins=[0, 12, 24, 36, 48, 60, 72],
            labels=[
                "0-1 Year",
                "1-2 Years",
                "2-3 Years",
                "3-4 Years",
                "4-5 Years",
                "5+ Years",
            ],
        )
        processed_X["MonthlyTotalChargesRatio"] = (
            processed_X["MonthlyCharges"] / processed_X["TotalCharges"]
        )
        processed_X[self.standard_scaler_variables] = self.standard_scaler.transform(
            processed_X[self.standard_scaler_variables]
        )
        for var in self.label_encoded_variables:
            processed_X[var] = self.label_encoder[var].transform(processed_X[var])

        nominal_data = self.onehot_encoder.transform(
            processed_X[self.onehot_encoded_variables]
        )
        nominal_columns = self.onehot_encoder.get_feature_names(
            self.onehot_encoded_variables
        )
        nominal_df = pd.DataFrame(nominal_data, columns=nominal_columns)

        processed_X = pd.concat(
            [processed_X.drop(columns=self.onehot_encoded_variables), nominal_df],
            axis=1,
        )

        return processed_X

    def train(self, X: pd.DataFrame, y: pd.DataFrame) -> "ChurnModel":
        # Train your model here
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        # Use your model to make predictions here
        return self.model.predict(X)

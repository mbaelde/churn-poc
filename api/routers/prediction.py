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

# Initialize the model
# Define the columns to be encoded
label_encoded_variables = [
    "gender",
    "seniorCitizen",
    "partner",
    "dependents",
    "hasPhoneService",
    "paperlessBilling",
    "contractType",
    "paymentMethod",
    "TenureGroup",
]
onehot_encoded_variables = [
    "multipleLines",
    "internetServiceType",
    "onlineSecurity",
    "onlineBackup",
    "deviceProtection",
    "techSupport",
    "streamingTV",
    "streamingMovies",
]
standard_scaler_variables = [
    "tenure",
    "monthlyCharges",
    "totalCharges",
    "MonthlyTotalChargesRatio",
]

bins = [0, 12, 24, 36, 48, 60, np.inf]
labels = ["0-1 Year", "1-2 Years", "2-3 Years", "3-4 Years", "4-5 Years", "5+ Years"]
tenure_binarizer = FeaturePreprocessor(
    TenureBinarizer(bins=bins, labels=labels),
    encoded_variables=["tenure"],
    output_variables=["tenure", "TenureGroup"],
)
ratio_computer = FeaturePreprocessor(
    RatioComputer("monthlyCharges", "totalCharges", "MonthlyTotalChargesRatio"),
    encoded_variables=["monthlyCharges", "totalCharges"],
    output_variables=["monthlyCharges", "totalCharges", "MonthlyTotalChargesRatio"],
)
scaler = FeaturePreprocessor(
    model=StandardScaler(),
    encoded_variables=standard_scaler_variables,
    output_variables=standard_scaler_variables,
)
label_encoder = MultiColumnLabelEncoder(encoded_variables=label_encoded_variables)
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
churn_model = ChurnModel(
    preprocessors=preprocessors,
)
models_dir = Path("data/models")
churn_model.deserialize(models_dir.joinpath("churn_model_prod.pkl"))

output_map = {0: "No Churn", 1: "Churn"}


def predict_churn(data):
    # Convert the input data to a Pandas DataFrame
    input_data = pd.DataFrame(
        [{k: v for k, v in data.dict().items() if k != "customerID"}]
    )

    # Perform the necessary preprocessing steps on the input data
    # (e.g., encoding categorical variables and feature scaling)
    # X = churn_model.preprocess(input_data)
    # Make predictions using the model
    predictions = churn_model.predict(input_data)

    # Convert the predictions to human-readable labels if needed
    # (e.g., 'Churn' or 'No Churn')

    # Return the predictions
    return output_map[predictions[0]]

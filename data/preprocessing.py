import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from features import (
    FeaturePreprocessor,
    MultiColumnLabelEncoder,
    RatioComputer,
    TenureBinarizer,
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Load the dataset
raw_data_dir = Path("data/raw")
processed_data_dir = Path("data/processed")
conn = sqlite3.connect(raw_data_dir.joinpath("telco_customer_churn.db"))
data = pd.read_sql_query("SELECT * FROM customers", conn)
conn.close()

# Define the columns to be encoded
binary_cols = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "PaperlessBilling",
    "Churn",
]
ordinal_cols = ["Contract", "PaymentMethod", "TenureGroup"]
nominal_cols = [
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]

# Handle missing values (if any)
imputer = FeaturePreprocessor(
    SimpleImputer(strategy="median"),
    encoded_variables=["TotalCharges"],
    output_variables=["TotalCharges"],
)

# Feature engineering
bins = [0, 12, 24, 36, 48, 60, np.inf]
labels = ["0-1 Year", "1-2 Years", "2-3 Years", "3-4 Years", "4-5 Years", "5+ Years"]
tenure_binarizer = FeaturePreprocessor(
    TenureBinarizer(bins=bins, labels=labels),
    encoded_variables=["tenure"],
    output_variables=["tenure", "TenureGroup"],
)

ratio_computer = FeaturePreprocessor(
    RatioComputer("MonthlyCharges", "TotalCharges", "MonthlyTotalChargesRatio"),
    encoded_variables=["MonthlyCharges", "TotalCharges"],
    output_variables=["MonthlyCharges", "TotalCharges", "MonthlyTotalChargesRatio"],
)

# Feature scaling
standard_scaled_variables = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "MonthlyTotalChargesRatio",
]
scaler = FeaturePreprocessor(
    model=StandardScaler(),
    encoded_variables=standard_scaled_variables,
    output_variables=standard_scaled_variables,
)

# Initialize encoders
label_encoder_variables = binary_cols + ordinal_cols
label_encoder = MultiColumnLabelEncoder(encoded_variables=label_encoder_variables)

# One-hot encoding for nominal variables
onehot_encoder = FeaturePreprocessor(
    model=OneHotEncoder(sparse=False, drop="first"),
    encoded_variables=nominal_cols,
    output_variables=nominal_cols,
    transform_to_dataframe=True,
)

feature_pipeline = Pipeline(
    [
        ("imputer", imputer),
        ("tenure_binarizer", tenure_binarizer),
        ("ratio_computer", ratio_computer),
        ("scaler", scaler),
        ("label_encoder", label_encoder),
        ("onehot_encoder", onehot_encoder),
    ]
)
data_encoded = feature_pipeline.fit_transform(data)

scaler.serialize(processed_data_dir.joinpath("standard_scaler.pkl"))
label_encoder.serialize(processed_data_dir.joinpath(f"label_encoder.pkl"))
onehot_encoder.serialize(processed_data_dir.joinpath(f"onehot_encoder.pkl"))

# Display the transformed dataset
data_encoded.to_csv(
    processed_data_dir.joinpath("telco_customer_churn.csv"), index=False
)

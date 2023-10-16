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
from sklearn.preprocessing import OneHotEncoder, StandardScaler

raw_data_dir = Path("data/raw")
processed_data_dir = Path("data/processed")
conn = sqlite3.connect(raw_data_dir.joinpath("telco_customer_churn.db"))
# Load the dataset
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
imputer = SimpleImputer(strategy="median")
data["TotalCharges"] = imputer.fit_transform(data[["TotalCharges"]])

# Feature engineering
bins = [0, 12, 24, 36, 48, 60, np.inf]
labels = ["0-1 Year", "1-2 Years", "2-3 Years", "3-4 Years", "4-5 Years", "5+ Years"]
tenure_binarizer = TenureBinarizer(bins=bins, labels=labels)
data = tenure_binarizer.fit_transform(data)

ratio_computer = RatioComputer(
    "MonthlyCharges", "TotalCharges", "MonthlyTotalChargesRatio"
)
data = ratio_computer.fit_transform(data)

# Feature scaling
standard_scaled_variables = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "MonthlyTotalChargesRatio",
]
scaler = FeaturePreprocessor(
    model=StandardScaler(), encoded_variables=standard_scaled_variables
)
data[standard_scaled_variables] = scaler.fit_transform(data[standard_scaled_variables])
scaler.serialize(processed_data_dir.joinpath("standard_scaler.pkl"))

# Initialize encoders
label_encoder_variables = binary_cols + ordinal_cols
label_encoder = MultiColumnLabelEncoder(encoded_variables=label_encoder_variables)
data[label_encoder_variables] = label_encoder.fit_transform(data)
label_encoder.serialize(processed_data_dir.joinpath(f"label_encoder.pkl"))

# One-hot encoding for nominal variables
onehot_encoder = FeaturePreprocessor(
    model=OneHotEncoder(sparse=False, drop="first"), encoded_variables=nominal_cols
)  # 'drop' is set to 'first' to avoid multicollinearity

nominal_data = onehot_encoder.fit_transform(data)
nominal_columns = onehot_encoder.get_feature_names(nominal_cols)
nominal_df = pd.DataFrame(nominal_data, columns=nominal_columns)
onehot_encoder.serialize(processed_data_dir.joinpath(f"onehot_encoder.pkl"))

# Combine the one-hot encoded nominal variables with the rest of the dataset
data_encoded = pd.concat([data.drop(columns=nominal_cols), nominal_df], axis=1)

# Display the transformed dataset
data_encoded.to_csv(
    processed_data_dir.joinpath("telco_customer_churn.csv"), index=False
)

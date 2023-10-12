import pickle
import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

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
ordinal_cols = ["Contract", "PaymentMethod"]
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

# Initialize encoders
label_encoder = {col: LabelEncoder() for col in binary_cols + ordinal_cols}
onehot_encoder = OneHotEncoder(
    sparse=False, drop="first"
)  # 'drop' is set to 'first' to avoid multicollinearity

# Label encoding for binary and ordinal variables
for col in binary_cols + ordinal_cols:
    data[col] = label_encoder[col].fit_transform(data[col])
    with open(processed_data_dir.joinpath(f"label_encoder_{col}.pkl"), "wb") as le_file:
        pickle.dump(label_encoder[col], le_file)

# One-hot encoding for nominal variables
nominal_data = onehot_encoder.fit_transform(data[nominal_cols])
nominal_columns = onehot_encoder.get_feature_names(nominal_cols)
nominal_df = pd.DataFrame(nominal_data, columns=nominal_columns)
with open(processed_data_dir.joinpath(f"onehot_encoder.pkl"), "wb") as ohe_file:
    pickle.dump(onehot_encoder, ohe_file)

# Combine the one-hot encoded nominal variables with the rest of the dataset
data_encoded = pd.concat([data.drop(columns=nominal_cols), nominal_df], axis=1)

# Display the transformed dataset
data_encoded.to_csv(
    processed_data_dir.joinpath("telco_customer_churn.csv"), index=False
)

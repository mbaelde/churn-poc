from pathlib import Path

import pandas as pd

import api.models as models

# Initialize the model
# Define the columns to be encoded
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
churn_model = models.ChurnModel(
    label_encoded_variables=label_encoded_variables,
    onehot_encoded_variables=onehot_encoded_variables,
    standard_scaler_variables=standard_scaler_variables,
)
churn_model.deserialize(Path("data/processed"))

output_map = {0: "No Churn", 1: "Churn"}


def predict_churn(data):
    # Convert the input data to a Pandas DataFrame
    input_data = pd.DataFrame([data.dict()])

    # Perform the necessary preprocessing steps on the input data
    # (e.g., encoding categorical variables and feature scaling)
    X = churn_model.preprocess(input_data)
    # Make predictions using the model
    predictions = churn_model.predict(X)

    # Convert the predictions to human-readable labels if needed
    # (e.g., 'Churn' or 'No Churn')

    # Return the predictions
    return output_map[predictions[0]]

import argparse
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from models.churn import ChurnModel
from models.features import (
    FeaturePreprocessor,
    MultiColumnLabelEncoder,
    RatioComputer,
    TenureBinarizer,
)


def main(
    base_path: Path = Path("data"),
    to_production: bool = False,
    overwrite_preprocessing: bool = False,
    n_splits: int = 5,
):
    # Load the dataset
    raw_data_dir = base_path.joinpath("raw")
    processed_data_dir = base_path.joinpath("processed")
    models_dir = base_path.joinpath("models")
    if not models_dir.exists():
        models_dir.mkdir(exist_ok=True)
    preprocessors_dir = base_path.joinpath("preprocessors")
    if not preprocessors_dir.exists():
        preprocessors_dir.mkdir(exist_ok=True)

    conn = sqlite3.connect(raw_data_dir.joinpath("telco_customer_churn.db"))
    data = pd.read_sql_query("SELECT * FROM customers", conn, index_col="customerID")
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

    training_data_path = processed_data_dir.joinpath("telco_customer_churn.csv")
    if overwrite_preprocessing:
        data_encoded = feature_pipeline.fit_transform(data)
        scaler.serialize(preprocessors_dir.joinpath("standard_scaler.pkl"))
        label_encoder.serialize(preprocessors_dir.joinpath(f"label_encoder.pkl"))
        onehot_encoder.serialize(preprocessors_dir.joinpath(f"onehot_encoder.pkl"))
        data_encoded.to_csv(training_data_path)
    else:
        data_encoded = pd.read_csv(training_data_path, index_col=0)
        scaler.deserialize(preprocessors_dir.joinpath("standard_scaler.pkl"))
        label_encoder.deserialize(preprocessors_dir.joinpath(f"label_encoder.pkl"))
        onehot_encoder.deserialize(preprocessors_dir.joinpath(f"onehot_encoder.pkl"))

    # Split the data into training and testing sets
    X = data_encoded.drop("Churn", axis=1)
    y = data_encoded["Churn"]

    churn_model = ChurnModel(
        preprocessors=feature_pipeline,
        model=RandomForestClassifier(n_estimators=100, random_state=42),
    )

    suffix = "_prod" if to_production else "_dev"
    if to_production:
        churn_model.train(X, y, preprocess_features=False)
        churn_model.serialize(models_dir.joinpath(f"churn_model{suffix}.pkl"))
    else:
        kfold = StratifiedKFold(n_splits=n_splits)
        train_ids = {}
        test_ids = {}
        for i, (train_index, test_index) in enumerate(kfold.split(X, y)):
            train_ids[f"fold_{i}"] = X.index[train_index].to_list()
            test_ids[f"fold_{i}"] = X.index[test_index].to_list()
            churn_model.train(
                X.iloc[train_index], y.iloc[train_index], preprocess_features=False
            )
            churn_model.serialize(models_dir.joinpath(f"churn_model{suffix}_{i}.pkl"))
        with open(processed_data_dir.joinpath("train_folds.json"), "w") as f:
            json.dump(train_ids, f)
        with open(processed_data_dir.joinpath("test_folds.json"), "w") as f:
            json.dump(test_ids, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--base-path", default="data")
    parser.add_argument("--to-production", action="store_true")
    parser.add_argument("--overwrite-preprocessing", action="store_true")

    args = parser.parse_args()
    main(
        base_path=Path(args.base_path),
        to_production=args.to_production,
        overwrite_preprocessing=args.overwrite_preprocessing,
    )
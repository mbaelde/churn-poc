from pathlib import Path
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

processed_data_dir = Path("data/processed")
# Load the Telco Customer Churn dataset
data = pd.read_csv(processed_data_dir.joinpath('telco_customer_churn.csv'), index_col=0)

# Split the data into training and testing sets
X = data.drop('Churn', axis=1)
y = data['Churn']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier (or your chosen model)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

with open(processed_data_dir.joinpath("churn_model.pkl"), "wb") as model_file:
    pickle.dump(clf, model_file)
gcloud auth login

gcloud config set project churn-prediction-poc

gsutil -m cp data/models/*.pkl gs://models-churn/models/
gsutil -m cp data/preprocessors/*.pkl gs://models-churn/preprocessors/


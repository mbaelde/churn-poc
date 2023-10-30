gcloud auth login

gcloud config set project churn-prediction-poc

gsutil cp data/models/*.pkl gs://models-churn/models/
gsutil cp data/preprocessors/*.pkl gs://models-churn/preprocessors/


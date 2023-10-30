# Use the official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy your entire project into the container
COPY api /app/api
COPY database /app/database
COPY models /app/models
COPY notebooks /app/notebooks
COPY scripts /app/scripts
COPY templates /app/templates
COPY tests /app/tests
COPY utils /app/utils 
COPY requirements.txt /app/requirements.txt
COPY setup.py /app/setup.py

# Install gsutil (Google Cloud Storage CLI tool)
RUN apt-get update && apt-get install -y curl
RUN curl https://sdk.cloud.google.com | bash
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"

# Set Google Cloud Storage credentials file (replace with your own service account key)
COPY churn-prediction-poc-9b523c379363.json /root/churn-prediction-poc-9b523c379363.json

# Authenticate with GCS using your service account key
RUN gcloud auth activate-service-account --key-file /root/churn-prediction-poc-9b523c379363.json

# Copy models and preprocessors from GCS to your Docker image
RUN mkdir -p /app/data/models
RUN gsutil -m cp -r gs://models-churn/models /app/data/
RUN mkdir -p /app/data/preprocessors
RUN gsutil -m cp -r gs://models-churn/preprocessors /app/data/

# Copy the requirements file into the container and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install .

# Expose the port that your FastAPI app is running on (if not using reverse proxy)
EXPOSE 8000

# Command to run your FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# churn-poc

The goal of this project is to create a data-driven application that predicts customer churn for a subscription-based business using a provided dataset. 

## How to

### Download the dataset

I used the ["Telco Customer Churn"](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) from Kaggle. The data directory should be organized as follows:

```bash
churn-poc/
├── data/
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed data files
│
```

The file `WA_Fn-UseC_-Telco-Customer-Churn.csv` should be put in the `data/raw/` directory.

## Init the database

The first time you use the package, you have to initialize the database by running the following script:

```bash
$ python database/init_customer_db.py
```

## Train the model

You can train a basic classification model using the following script:

```bash
$ python models/train_model.py
```

This will create a cross validation over 5 folds. You can assess the performance of the model by computing the predictions:

```bash
$ python models/predict_model.py
```

In order to train a model for production, run:

```bash
$ python models/train_model.py --to-production
```

## Run a server with FastAPI

Once the model is trained you can run a server by running the following command:

```bash
$ uvicorn api.main:app --reload
```

You can then use the sample example in `data/example.json` to make a prediction.

## Use a Docker container

The github action is setup so that a docker image is built for every push on the repo. You can instantiate a VM to run the container by running the following commands:

```BASH
$ docker pull mbaelde/churn-prediction-poc
# Copy the customers.db file on the VM in the directory /home/user/database
$ echo "DATABASE_URL=sqlite:////data/customers.db" > .env
$ docker run -v /home/user/database:/data -d -p 8000:8000 mbaelde/churn-prediction-poc
$ docker cp .env container_id:/app
$ docker restart container_id
```

## Dataset description

The "Telco Customer Churn" dataset is a popular dataset often used for customer churn analysis and prediction. It typically contains various customer-related variables, including demographic information, subscription details, and whether the customer has churned or not. Below is a description of the common variables found in such a dataset:

1. **customerID:** A unique identifier for each customer. This variable is a string matching `\d\d\d\d-[A-Za-z][A-Za-z][A-Za-z][A-Za-z][A-Za-z]`.

2. **gender:** The customer's gender, which can be binary, i.e., "Male" or "Female."

3. **SeniorCitizen:** A binary variable indicating whether the customer is a senior citizen (1 for "Yes" 0 for "No").

4. **Partner:** A binary variable indicating whether the customer has a partner or spouse ("Yes" or "No").

5. **Dependents:** A binary variable indicating whether the customer has dependents (e.g., children or other family members) ("Yes" or "No").

6. **tenure:** The number of months a customer has been with the company. This variable represents the customer's loyalty or tenure.

7. **PhoneService:** A binary variable indicating whether the customer subscribes to phone services ("Yes" or "No").

8. **MultipleLines:** A variable indicating the type of phone service, such as "No phone service" "Single line" or "Multiple lines"

9. **InternetService:** The type of internet service subscribed to, such as "DSL" "Fiber optic" or "No internet service"

10. **OnlineSecurity:** A variable indicating whether the customer has online security services (e.g., "Yes" "No" or "No internet service").

11. **OnlineBackup:** A variable indicating whether the customer has online backup services (e.g., "Yes" "No" or "No internet service").

12. **DeviceProtection:** A variable indicating whether the customer has device protection services (e.g., "Yes" "No" or "No internet service").

13. **TechSupport:** A variable indicating whether the customer has tech support services (e.g., "Yes" "No" or "No internet service").

14. **StreamingTV:** A variable indicating whether the customer subscribes to streaming TV services (e.g., "Yes" "No" or "No internet service").

15. **StreamingMovies:** A variable indicating whether the customer subscribes to streaming movie services (e.g., "Yes" "No" or "No internet service").

16. **Contract:** The type of contract the customer has, such as "Month-to-month" "One year" or "Two year".

17. **PaperlessBilling:** A binary variable indicating whether the customer has opted for paperless billing ("Yes" or "No").

18. **PaymentMethod:** The customer's preferred payment method, such as "Electronic check" "Mailed check" "Bank transfer" or "Credit card (automatic)".

19. **MonthlyCharges:** The monthly charges incurred by the customer for the subscription services.

20. **TotalCharges:** The total charges incurred by the customer during their entire tenure.

21. **Churn:** The target variable indicating whether the customer who left within the last monthh, called Churn (1 for "Yes," 0 for "No"). This is the variable of primary interest for churn prediction.

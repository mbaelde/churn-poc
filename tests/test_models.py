import unittest
from models import ChurnModel

class TestChurnModel(unittest.TestCase):
    def setUp(self):
        # Create an instance of the ChurnModel
        self.churn_model = ChurnModel()

    def test_churn_prediction(self):
        # Sample input data for prediction
        data = {
            "tenure": 24,
            "MonthlyCharges": 65.0,
            "TotalCharges": 1500.0,
            # Add more features as needed
        }

        # Make a prediction using the model
        prediction = self.churn_model.predict(data)

        # Validate the prediction
        self.assertIn(prediction, ["Churn", "No Churn"])

if __name__ == '__main__':
    unittest.main()

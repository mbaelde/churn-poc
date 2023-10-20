import os
import unittest

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import CustomerChurn, create_customer, get_customer

load_dotenv()


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a Database instance using the connection to an in-memory SQLite database
        DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()
        self.customer_id = "123"
        self.churn_prediction = "Churn"

    def tearDown(self):
        # Close the connection after each test
        record_to_delete = (
            self.db.query(CustomerChurn)
            .filter(CustomerChurn.customerID == self.customer_id)
            .first()
        )
        self.db.delete(record_to_delete)

    def test_database_insert(self):
        # Insert test data
        data = {
            "customerID": self.customer_id,
            "churn_prediction": self.churn_prediction,
        }
        create_customer(self.db, **data)

        # Retrieve the inserted data
        retrieved_data = get_customer(self.db, customerID=self.customer_id)

        # Validate the retrieved data
        self.assertEqual(retrieved_data.customerID, data["customerID"])
        self.assertEqual(retrieved_data.churn_prediction, data["churn_prediction"])

    def test_database_not_found(self):
        # Attempt to retrieve data for a non-existent customer
        retrieved_data = get_customer(self.db, "456")

        # Validate that the data is not found
        self.assertIsNone(retrieved_data)


if __name__ == "__main__":
    unittest.main()

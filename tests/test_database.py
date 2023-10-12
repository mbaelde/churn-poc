import unittest
import sqlite3
from database import Customer

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a Database instance using the connection to an in-memory SQLite database
        self.conn = sqlite3.connect(":memory:")
        self.db = Customer(self.conn)

    def tearDown(self):
        # Close the connection after each test
        self.conn.close()

    def test_database_insert(self):
        # Insert test data
        data = {"customer_id": "123", "churn_prediction": "Churn"}
        self.db.insert_data(data)

        # Retrieve the inserted data
        retrieved_data = self.db.get_data("123")

        # Validate the retrieved data
        self.assertEqual(retrieved_data, data)

    def test_database_not_found(self):
        # Attempt to retrieve data for a non-existent customer
        retrieved_data = self.db.get_data("456")

        # Validate that the data is not found
        self.assertIsNone(retrieved_data)

if __name__ == '__main__':
    unittest.main()

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import (
    Base,
    Contract,
    Customer,
    CustomerChurn,
    InternetService,
    PhoneService,
)


class TestCustomerDatabase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_customer_creation(self):
        # Test creating a customer
        customer = Customer(
            id="1", gender="Male", seniorCitizen="No", partner="Yes", dependents="No"
        )
        self.session.add(customer)
        self.session.commit()
        self.assertEqual(customer.gender, "Male")
        self.assertEqual(customer.seniorCitizen, "No")
        self.assertEqual(customer.partner, "Yes")
        self.assertEqual(customer.dependents, "No")

    def test_contract_creation(self):
        # Test creating a contract for a customer
        customer = Customer(
            id="2", gender="Female", seniorCitizen="Yes", partner="No", dependents="Yes"
        )
        contract = Contract(
            contractType="Month-to-Month",
            tenure=12,
            paperlessBilling="Yes",
            paymentMethod="Credit Card",
            monthlyCharges=55.0,
            totalCharges=660.0,
            customer=customer,
        )
        customer.contracts.append(contract)
        self.session.add(customer)
        self.session.commit()
        self.assertEqual(contract.contractType, "Month-to-Month")
        self.assertEqual(contract.tenure, 12)
        self.assertEqual(contract.paperlessBilling, "Yes")
        self.assertEqual(contract.paymentMethod, "Credit Card")
        self.assertEqual(contract.customer.id, "2")

    def test_phone_service_creation(self):
        # Test creating a phone service for a contract
        customer = Customer(
            id="3", gender="Male", seniorCitizen="No", partner="No", dependents="No"
        )
        contract = Contract(
            contractType="Month-to-Month",
            tenure=12,
            paperlessBilling="Yes",
            paymentMethod="Credit Card",
            monthlyCharges=55.0,
            totalCharges=660.0,
            customer=customer,
        )
        phone_service = PhoneService(
            hasPhoneService="Yes", multipleLines="No", contract=contract
        )
        contract.phone_service = phone_service
        customer.contracts.append(contract)
        self.session.add(customer)
        self.session.commit()
        self.assertEqual(phone_service.hasPhoneService, "Yes")
        self.assertEqual(phone_service.multipleLines, "No")
        self.assertEqual(phone_service.contract.customer.id, "3")

    def test_internet_service_creation(self):
        # Test creating an internet service for a contract
        customer = Customer(
            id="4", gender="Female", seniorCitizen="No", partner="Yes", dependents="Yes"
        )
        contract = Contract(
            contractType="Month-to-Month",
            tenure=12,
            paperlessBilling="Yes",
            paymentMethod="Credit Card",
            monthlyCharges=55.0,
            totalCharges=660.0,
            customer=customer,
        )
        internet_service = InternetService(
            internetServiceType="DSL",
            onlineSecurity="Yes",
            onlineBackup="No",
            deviceProtection="Yes",
            techSupport="No",
            streamingTV="Yes",
            streamingMovies="No",
            contract=contract,
        )
        contract.internet_service = internet_service
        customer.contracts.append(contract)
        self.session.add(customer)
        self.session.commit()
        self.assertEqual(internet_service.internetServiceType, "DSL")
        self.assertEqual(internet_service.onlineSecurity, "Yes")
        self.assertEqual(internet_service.onlineBackup, "No")

    def test_customer_churn_creation(self):
        # Test creating a customer churn entry for a customer
        customer = Customer(
            id="5", gender="Male", seniorCitizen="No", partner="Yes", dependents="Yes"
        )
        churn = CustomerChurn(churn="Yes", customer=customer)
        customer.churns.append(churn)
        self.session.add(customer)
        self.session.commit()
        self.assertEqual(churn.churn, "Yes")
        self.assertEqual(churn.customer.id, "5")


if __name__ == "__main__":
    unittest.main()

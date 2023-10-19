from setuptools import find_packages, setup

setup(
    name="customer-churn-predictor",
    version="1.0.0",
    description="Customer Churn Predictor",
    author="Maxime BAELDE",
    author_email="baelde.maxime@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "sqlalchemy",
        "seaborn",
        "fastapi",
        "python-dotenv",
        "httpx",
        "jinja2",
    ],
    entry_points={
        "console_scripts": [
            "run-customer-churn = api.main:app",
        ],
    },
)

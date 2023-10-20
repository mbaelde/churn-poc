import os

from dotenv import load_dotenv

load_dotenv()

# Define your configuration settings as constants
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test.db")
API_KEY = os.getenv("API_KEY", "your-api-key")
DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "yes", "1"]

# You can also define more complex settings
DATABASE_SETTINGS = {
    "user": os.getenv("DB_USER", "username"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "mydatabase"),
}

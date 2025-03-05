import os
import logging
import json  # For parsing ALLOWED_ORIGINS
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------------
# API Keys
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("Missing OpenAI API Key! Set it in environment variables.")
    raise ValueError("Missing OpenAI API Key! Set it in environment variables.")
else:
    logger.info("OpenAI API Key loaded successfully.")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # Optional API key

# ------------------------------------------------------------------
# Database Configuration
# ------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logger.error("Missing MONGO_URI! Set it in the .env file.")
    raise ValueError("Missing MONGO_URI! Set it in the .env file.")
else:
    logger.info("MONGO_URI loaded successfully.")

# ------------------------------------------------------------------
# Application Settings
# ------------------------------------------------------------------
REACT_APP_API_URL = os.getenv("REACT_APP_API_URL", "http://localhost:8002")  # Default value

# Use a default JSON string if ALLOWED_ORIGINS is not set
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000"]')
try:
    ALLOWED_ORIGINS = json.loads(ALLOWED_ORIGINS_STR)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in ALLOWED_ORIGINS: {e}. Using default ['http://localhost:3000'].")
    ALLOWED_ORIGINS = ["http://localhost:3000"]

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  # Default value

# Convert the TESTING variable to a boolean
TESTING = os.getenv("TESTING", "False").lower() == "true"

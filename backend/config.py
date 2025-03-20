import os
import logging
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------------
# API Keys
# ------------------------------------------------------------------
def get_env_var(var_name, required=True, default=None, sensitive=False):
    """Retrieve environment variables with logging and error handling."""
    value = os.getenv(var_name, default)
    if required and not value:
        logger.critical(f"Missing required environment variable: {var_name}")
        raise ValueError(f"Missing required environment variable: {var_name}")
    if value and sensitive:
        logger.info(f"{var_name} loaded successfully (value hidden for security).")
    elif value:
        logger.info(f"{var_name} loaded successfully.")
    return value

OPENAI_API_KEY = get_env_var("OPENAI_API_KEY", sensitive=True)
DEEPSEEK_API_KEY = get_env_var("DEEPSEEK_API_KEY", required=False, default="")

# ------------------------------------------------------------------
# Database Configuration
# ------------------------------------------------------------------
MONGO_URI = get_env_var("MONGO_URI", sensitive=True)

# ------------------------------------------------------------------
# Application Settings
# ------------------------------------------------------------------
REACT_APP_API_URL = get_env_var("REACT_APP_API_URL", required=False, default="http://localhost:8002")

# Handle allowed origins safely
ALLOWED_ORIGINS_STR = get_env_var("ALLOWED_ORIGINS", required=False, default='["http://localhost:3000"]')
try:
    ALLOWED_ORIGINS = json.loads(ALLOWED_ORIGINS_STR)
    if not isinstance(ALLOWED_ORIGINS, list):
        raise ValueError("ALLOWED_ORIGINS must be a list.")
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Invalid JSON in ALLOWED_ORIGINS: {e}. Using default ['http://localhost:3000'].")
    ALLOWED_ORIGINS = ["http://localhost:3000"]

REDIS_HOST = get_env_var("REDIS_HOST", required=False, default="localhost")

# Convert TESTING variable to a boolean
TESTING = os.getenv("TESTING", "False").strip().lower() == "true"
logger.info(f"Testing Mode: {'Enabled' if TESTING else 'Disabled'}")

# Final logging summary
logger.info("Environment configuration loaded successfully.")

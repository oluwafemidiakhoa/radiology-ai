import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("MongoSetup")

# Read MONGO_URI from the environment (.env file)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logger.error("MONGO_URI is not set in the environment.")
    raise EnvironmentError("MONGO_URI is not defined. Please set it in your .env file.")

DB_NAME = "radiology_db"
COLLECTION_NAME = "ai_reports"

def get_mongo_client():
    """Create and return a MongoClient using the MONGO_URI from the environment."""
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')  # Verify connection
        logger.info("Successfully connected to MongoDB.")
        return client
    except Exception as e:
        logger.exception("Failed to connect to MongoDB.")
        raise

def setup_database():
    """Ensure that the required database and collection exist."""
    client = get_mongo_client()
    db = client[DB_NAME]
    if COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME)
        logger.info(f"Created collection: {COLLECTION_NAME}")
    else:
        logger.info(f"Collection '{COLLECTION_NAME}' already exists.")

if __name__ == "__main__":
    setup_database()

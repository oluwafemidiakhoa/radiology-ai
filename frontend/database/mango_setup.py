import os
import logging
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Retrieve MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logger.critical("MONGO_URI is not set in the environment.")
    raise EnvironmentError("MONGO_URI is not defined. Please check your .env file.")

# Database and collection names
DB_NAME = "radiology_db"
COLLECTION_NAME = "ai_reports"

def get_mongo_client():
    """Initialize and return a MongoDB client."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # Test connection
        logger.info("Successfully connected to MongoDB.")
        return client
    except errors.ServerSelectionTimeoutError as e:
        logger.critical("MongoDB connection timed out. Check your internet connection and IP whitelisting.")
        raise
    except errors.ConnectionFailure as e:
        logger.critical("Failed to establish a connection to MongoDB. Ensure the cluster is accessible.")
        raise
    except Exception as e:
        logger.exception("Unexpected error while connecting to MongoDB.")
        raise

def setup_database():
    """Ensure the required database and collection exist."""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        if COLLECTION_NAME not in db.list_collection_names():
            db.create_collection(COLLECTION_NAME)
            logger.info(f"Created new collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Collection '{COLLECTION_NAME}' already exists.")
    except Exception as e:
        logger.exception("Error during database setup.")

if __name__ == "__main__":
    setup_database()

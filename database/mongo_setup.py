import os
import logging
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("MongoSetup")

# Read MONGO_URI from environment or default to localhost
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "radiology_db"
COLLECTION_NAME = "ai_reports"

def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI)
        return client
    except Exception as e:
        logger.exception("Failed to connect to MongoDB.")
        raise

def setup_database():
    client = get_mongo_client()
    db = client[DB_NAME]

    if COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME)
        logger.info(f"Created collection: {COLLECTION_NAME}")
    else:
        logger.info(f"Collection '{COLLECTION_NAME}' already exists.")

if __name__ == "__main__":
    setup_database()

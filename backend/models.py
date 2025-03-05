from dotenv import load_dotenv
load_dotenv()  # Load environment variables as early as possible

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from typing import Any, List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Retrieve MongoDB credentials and cluster details from environment variables
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "ethagagroalliedltd")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Flindell1977")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "radiologyal.1n3v2.mongodb.net")

# Construct the MongoDB URI (only if not in testing mode)
MONGO_URI = None
if os.getenv("TESTING") != "True":
    if MONGO_PASSWORD:
        MONGO_URI = (
            f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/"
            "?retryWrites=true&w=majority&appName=RadiologyAl"
        )
    else:
        logger.error("MONGO_PASSWORD environment variable not set! Database connection will fail.")
else:
    logger.info("TESTING environment detected. Skipping MongoDB connection.")

client = None
db = None
reports_collection = None

try:
    if MONGO_URI:
        # Log only a partial URI for security
        logger.info(f"Connecting to MongoDB using URI: {MONGO_URI[:50]}...")
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=30000,  # 30 seconds timeout
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        # Verify connection with a ping
        client.admin.command("ping")
        db = client["radiology_db"]
        reports_collection = db["ai_reports"]
        logger.info("Connected to MongoDB and obtained 'ai_reports' collection.")
    else:
        if os.getenv("TESTING") != "True":
            raise ValueError("MONGO_URI is not defined. Cannot connect to MongoDB.")
except ServerSelectionTimeoutError as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

def store_report(filename: str, report: str) -> None:
    """
    Store a report in the MongoDB 'ai_reports' collection.

    Args:
        filename (str): The identifier for the report.
        report (str): The AI-generated report content.
    """
    try:
        if reports_collection is not None:
            document = {"filename": filename, "report": report}
            result = reports_collection.insert_one(document)
            logger.info(f"Stored report for {filename} with ObjectId: {result.inserted_id}")
        else:
            logger.warning("MongoDB connection not initialized. Report not stored.")
    except Exception as e:
        logger.error(f"Error storing report for {filename}: {e}")
        raise

def get_report(filename: str) -> Dict[str, Any]:
    """
    Retrieve a report from MongoDB by filename.

    Args:
        filename (str): The report filename.

    Returns:
        Dict[str, Any]: The report document, excluding the internal MongoDB ID.
    """
    if reports_collection is None:
        logger.error("MongoDB connection not initialized. Cannot retrieve report.")
        return {}
    return reports_collection.find_one({"filename": filename}, {"_id": 0})

def list_reports() -> List[Dict[str, Any]]:
    """
    List all reports stored in MongoDB.

    Returns:
        List[Dict[str, Any]]: A list of report documents.
    """
    if reports_collection is None:
        logger.error("MongoDB connection not initialized. Cannot list reports.")
        return []
    return list(reports_collection.find({}, {"_id": 0}))

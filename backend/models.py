from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load the .env file from the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Get the MongoDB URI components from environment variables
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "ethagagroalliedltd")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "hV5wlRUhbvh9qhZt")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "radiologyal.1n3v2.mongodb.net")

# Construct the MongoDB URI if not in testing mode
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
        client = MongoClient(MONGO_URI)
        client.admin.command("ping")  # Verify connection
        db = client["radiology_db"]
        reports_collection = db["ai_reports"]
        logger.info("Connected to MongoDB and obtained 'ai_reports' collection.")
    else:
        if os.getenv("TESTING") != "True":
            raise ValueError("MONGO_URI is not defined. Cannot connect to MongoDB.")
except Exception as e:
    if os.getenv("TESTING") != "True":
        logger.error(f"Error connecting to MongoDB or accessing collection: {e}")
        raise

def store_report(filename: str, report: str):
    """
    Stores the analysis report along with the filename into the MongoDB 'ai_reports' collection.
    """
    try:
        # Use an explicit check for None
        if reports_collection is not None:
            document = {"filename": filename, "report": report}
            result = reports_collection.insert_one(document)
            logger.info(f"Stored report for {filename} with ObjectId: {result.inserted_id}")
        else:
            logger.warning("Skipping store_report because MongoDB connection is not initialized.")
    except Exception as e:
        logger.error(f"Error storing report for {filename}: {e}")
        raise

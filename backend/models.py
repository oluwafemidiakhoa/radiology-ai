# models.py
from pymongo import MongoClient
import os
import io
import logging
from dotenv import load_dotenv  # Import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load the .env file from the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')  # Construct the path
load_dotenv(dotenv_path=dotenv_path)  # Load the variables

# Get the MongoDB URI components from environment variables
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "ethagagroalliedltd")  # Default username
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")  # Required password
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "radiologyal.1n3v2.mongodb.net")  # Default cluster

# Construct the MongoDB URI
MONGO_URI = None  # Initialize to None
if os.getenv("TESTING") != "True":
    if MONGO_PASSWORD:
        MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/?retryWrites=true&w=majority&appName=RadiologyAl"
    else:
        logger.error(
            "MONGO_PASSWORD environment variable not set! Database connection will fail."
        )
else:
    logger.info("TESTING environment detected. Skipping MongoDB connection.")


client = None
db = None
reports_collection = None

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')  # Check connection
        db = client["radiology_db"]
        reports_collection = db["ai_reports"]
        logger.info("Connected to MongoDB and obtained ai_reports collection.")
    else:
        if os.getenv("TESTING") != "True":
          raise ValueError("MONGO_URI is not defined. Cannot connect to MongoDB.")

except Exception as e:
    if os.getenv("TESTING") != "True":
        logger.error(f"Error connecting to MongoDB or accessing collection: {e}")
        # Re-raise the exception to prevent the app from starting if the database connection fails
        raise

def store_report(filename: str, report: str):
    """Stores the analysis report along with the filename into MongoDB."""
    try:
        if reports_collection:
            document = {"filename": filename, "report": report}
            result = reports_collection.insert_one(document)
            logger.info(f"Stored report for {filename} with ObjectId: {result.inserted_id}")
        else:
            logger.warning("Skipping store_report because MongoDB connection is not initialized.")
    except Exception as e:
        logger.error(f"Error storing report for {filename}: {e}")
        # Consider whether to re-raise the exception or handle it differently based on your app's requirements
        raise
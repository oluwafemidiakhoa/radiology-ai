from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Retrieve MONGO_URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not defined. Cannot connect to MongoDB.")

# Initialize MongoDB connection
try:
    logger.info("Connecting to MongoDB...")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=30000,  # 30 seconds timeout
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    # Verify connection with a ping
    client.admin.command("ping")
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

# Set up the database and collection
db = client["radiology_db"]
reports_collection = db["ai_reports"]
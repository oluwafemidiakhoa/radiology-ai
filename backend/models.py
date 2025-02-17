# models.py
from pymongo import MongoClient
import os

# Get the MongoDB URI from environment variables or default to localhost
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["radiology_db"]
reports_collection = db["ai_reports"]

def store_report(filename: str, report: str):
    """
    Stores the analysis report along with the filename into MongoDB.
    """
    document = {
        "filename": filename,
        "report": report
    }
    reports_collection.insert_one(document)

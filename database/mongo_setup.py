from pymongo import MongoClient
import os

# Get MongoDB URI from environment or use default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["radiology_db"]

def setup_database():
    # Create the collection if it doesn't already exist
    if "ai_reports" not in db.list_collection_names():
        db.create_collection("ai_reports")
        print("Created collection: ai_reports")
    else:
        print("Collection ai_reports already exists.")

if __name__ == "__main__":
    setup_database()

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["radiology_db"]
collection = db["ai_reports"]

def store_report(filename, report):
    collection.insert_one({"filename": filename, "report": report})

from database import reports_collection
import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

def store_report(filename: str, report: str) -> None:
    """
    Store the analysis report in MongoDB.
    
    Args:
        filename (str): The name of the report file.
        report (str): The AI-generated report content.
    """
    try:
        if reports_collection is not None:
            document = {"filename": filename, "report": report}
            result = reports_collection.insert_one(document)
            logger.info(f"Stored report for {filename} with ObjectId: {result.inserted_id}")
        else:
            logger.warning("MongoDB connection is not initialized. Skipping report storage.")
    except Exception as e:
        logger.error(f"Error storing report for {filename}: {e}")
        raise

def get_report(filename: str) -> Dict[str, Any]:
    """
    Retrieve a report from MongoDB by filename.
    
    Args:
        filename (str): The name of the report file.
    
    Returns:
        Dict[str, Any]: The report document (excluding the internal MongoDB ID).
    """
    try:
        if reports_collection is not None:
            return reports_collection.find_one({"filename": filename}, {"_id": 0})
        else:
            logger.warning("MongoDB connection is not initialized. Cannot retrieve report.")
            return {}
    except Exception as e:
        logger.error(f"Error retrieving report for {filename}: {e}")
        raise

def list_reports() -> List[Dict[str, Any]]:
    """
    List all reports stored in MongoDB.
    
    Returns:
        List[Dict[str, Any]]: A list of report documents.
    """
    try:
        if reports_collection is not None:
            return list(reports_collection.find({}, {"_id": 0}))
        else:
            logger.warning("MongoDB connection is not initialized. Cannot list reports.")
            return []
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise

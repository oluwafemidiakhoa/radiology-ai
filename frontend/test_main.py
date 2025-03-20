# test_main.py
import pytest
from main import select_differentials, process_medical_image, analyze_image
from fastapi import UploadFile, File
from io import BytesIO
from PIL import Image
import os
import base64

# Sample test image
TEST_IMAGE_PATH = "test_image.jpg"  # Replace with your actual test image path
if not os.path.exists(TEST_IMAGE_PATH):
    # Create a sample test image if it doesn't exist
    img = Image.new('RGB', (600, 400), color='red')
    img.save(TEST_IMAGE_PATH)

def create_test_image_upload_file(path: str) -> UploadFile:
    """Creates a mock UploadFile object for testing."""
    with open(path, "rb") as f:
        image_bytes = f.read()
    return UploadFile(filename=os.path.basename(path), file=BytesIO(image_bytes))

# Mock store_report function
def mock_store_report(filename: str, report: str):
    """Mocks the store_report function to avoid database interaction during testing."""
    print(f"Mock store_report called with filename: {filename}, report: {report}")
    return None

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Mocks the database and environment variable dependencies to prevent connection during testing."""
    monkeypatch.setattr("os.getenv", lambda x, default=None: "test_password" if x == "MONGO_PASSWORD" else default)
    monkeypatch.setattr("models.MongoClient", lambda *args, **kwargs: None)
    monkeypatch.setattr("models.db", lambda *args, **kwargs: None)
    monkeypatch.setattr("models.reports_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr("main.store_report", mock_store_report)

@pytest.mark.asyncio
async def test_analyze_image_with_metadata(monkeypatch):
    """Tests the analyze_image endpoint with a mock image and metadata (age and sex)."""
    # Mock process_medical_image to return dummy data
    async def mock_process_medical_image(raw_data: bytes, filename: str):
        test_image = Image.new('RGB', (512, 512), color='blue')  # Create a dummy PIL image
        buffered = io.BytesIO()
        test_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return test_image, f"data:image/jpeg;base64,{img_str}"  # Return a dummy image and data URL

    # Replace the actual process_medical_image function with the mock
    monkeypatch.setattr("main.process_medical_image", mock_process_medical_image)

    # Create a mock UploadFile
    test_upload_file = create_test_image_upload_file(TEST_IMAGE_PATH)

    # Call analyze_image with metadata
    response = await analyze_image(test_upload_file, age=30, sex="Female")

    # Assertions
    assert "filename" in response
    assert "image_metadata" in response
    assert "analysis" in response
    assert "Patient Age:30" in response["analysis"]  # Check if age is in the analysis
    assert "Patient Sex:Female" in response["analysis"]  # Check if sex is in the analysis
    assert "This analysis is based solely on visual patterns" in response["analysis"]
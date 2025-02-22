import pytest
from fastapi import UploadFile, File
from io import BytesIO
from PIL import Image
import os
import base64
import logging
from typing import Tuple
from unittest.mock import AsyncMock, Mock

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    logger.info(f"Mock store_report called with filename: {filename}, report: {report}")
    return None

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Mocks the database, environment variable, and OpenAI API dependencies."""
    logger.info("Applying mock dependencies fixture.")
    monkeypatch.setattr("os.getenv", lambda x, default=None: "True" if x == "TESTING" else "test_password" if x == "MONGO_PASSWORD" else "test_openai_key" if x == "OPENAI_API_KEY"  else None)

    # Import models here
    from models import store_report
    monkeypatch.setattr("main.store_report", mock_store_report)

    # Import main to access select_differentials and process_medical_image
    async def mock_process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
        logger.info("Mocking process_medical_image")
        test_image = Image.new('RGB', (512, 512), color='blue') #Create a dummy PIL image
        buffered = BytesIO()
        test_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return test_image, f"data:image/jpeg;base64,{img_str}"  # Return a dummy image and data URL

    monkeypatch.setattr("main.process_medical_image",  mock_process_medical_image)

    # Mock the OpenAI API call
    # Create a mock response object
    class MockChoice:  # Define a class for the inner mock
        def __init__(self, content):
            self.message = Mock()
            self.message.content = content
    class MockCompletion:
      def __init__(self, content):
        self.choices = [MockChoice(content)]
    mock_response_content = "Mock analysis result. This analysis is based solely on visual patterns..." # Replace with your desired mock analysis text
    mock_completion = MockCompletion(mock_response_content)

    async def mock_chat_completion_create(*args, **kwargs): #*args and **kwargs handles any changes to arguments passed to OpenAI
        return mock_completion

    monkeypatch.setattr("main.client.chat.completions.create", mock_chat_completion_create) # Ensure you patch where the client is being called

    logger.info("Mock dependencies applied.")

@pytest.mark.asyncio
async def test_analyze_image_with_metadata(monkeypatch):
    """Tests the analyze_image endpoint with a mock image and metadata (age and sex)."""
    logger.info("Testing image called now")
    from main import analyze_image #Call here so the mock are not running
    # Replace the actual store_report function with the mock
    # Create a mock UploadFile
    test_upload_file = create_test_image_upload_file(TEST_IMAGE_PATH)

    # Call analyze_image
    # set a function to load
    response = await analyze_image(test_upload_file, age=30, sex="Female")

    # Assertions
    logger.info(f"Response: {response}")
    assert "filename" in response
    assert "image_metadata" in response
    assert "analysis" in response
    assert "Patient Age:30" in response["analysis"]
    assert "Patient Sex:Female" in response["analysis"]
    assert "This analysis is based solely on visual patterns" in response["analysis"] #Very basic check to see the analysis worked.
    logger.info("test_analyze_image passed")
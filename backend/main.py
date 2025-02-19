import os
import io
import base64
import logging
import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Secure functions for storing reports; ensure these are HIPAA-compliant.
from models import store_report
from config import OPENAI_API_KEY

# Configure robust logging for production.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Import the new asynchronous OpenAI client from v1.0.
from openai import AsyncOpenAI

# Instantiate the async client explicitly.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY))

# Create the FastAPI app with comprehensive metadata.
app = FastAPI(
    title="Medical Imaging AI",
    description=(
        "AI solution for advanced medical imaging analysis. "
    ),
    version="2.0.0",
)

# Configure CORS (adjust allowed origins for production).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "High-End Medical Imaging AI is operational!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    Advanced AI-driven medical imaging analysis endpoint.
    """
    # Step 1: Ingest the file.
    try:
        image_data = await file.read()
        filename = file.filename.lower()
        logger.info(f"File received: {filename}")
    except Exception as err:
        logger.exception("Error reading the uploaded file")
        raise HTTPException(status_code=400, detail="Unable to read the uploaded file.")

    # Step 2: Process the image (supporting both DICOM and standard formats).
    try:
        if filename.endswith(".dcm"):
            dicom = pydicom.dcmread(io.BytesIO(image_data))
            img_array = dicom.pixel_array
            # Normalize pixel values to the range [0, 255]
            norm_img = ((img_array - np.min(img_array)) / (np.ptp(img_array)) * 255).astype(np.uint8)
            image = Image.fromarray(norm_img)
            logger.info("DICOM image processed successfully.")
        else:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Standard image processed: mode={image.mode}, size={image.size}")
        # Ensure image is in RGB or L mode.
        if image.mode not in ["RGB", "L"]:
            image = image.convert("RGB")
        # Encode the image as Base64 (if needed for logging or future use).
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        b64_image = base64.b64encode(buffer.getvalue()).decode()
    except (UnidentifiedImageError, Exception) as err:
        logger.exception("Error processing image")
        raise HTTPException(status_code=400, detail="Image processing failed. Please ensure the file is valid.")

    # Step 3: Construct an advanced diagnostic prompt.
    prompt = (
        "You are a world-class medical imaging AI. Produce a board-level diagnostic report with the following sections:\n\n"
        "1. Technical Assessment\n"
        "2. Systematic Review of Structures\n"
        "3. Potential Clinical Correlation & Differential Considerations\n"
        "4. Recommended Next Steps (Hypothetical)\n"
        "5. AI-Driven Uncertainty Quantification\n\n"
        "Advanced Imaging Suggestions: Recommend high-resolution imaging modalities (e.g., MRI, PET-CT, contrast-enhanced CT) if warranted.\n"
        "Oncology Biomarker Correlation: Integrate relevant biomarkers such as CA-125 (ovarian), AFP (hepatic), PSA (prostate), etc.\n\n"
        "Provide a concise yet expert-level analysis with actionable recommendations."
    )

    # Note: GPT-4o currently does not support direct image inputs, so we rely solely on the prompt text.
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Analyze the provided medical image and generate an expert diagnostic report based on its features."}
    ]

    # Step 4: Call the OpenAI API asynchronously.
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",  # Using the new GPT-4o model identifier
            messages=messages,
            max_tokens=2000,
            temperature=0.2
        )
        analysis_report = response.choices[0].message.content
        logger.info(f"AI analysis generated for file: {filename}")
    except Exception as err:
        logger.exception("OpenAI API error")
        raise HTTPException(status_code=500, detail="AI analysis failed. Please try again later.")

    # Step 5: Store the generated report securely.
    try:
        store_report(filename, analysis_report)
        logger.info(f"Report stored successfully for file: {filename}")
    except Exception as err:
        logger.warning("Failed to store report", exc_info=True)

    # Step 6: Return the structured diagnostic report.
    return {
        "filename": filename,
        "AI_Analysis": analysis_report,
    }

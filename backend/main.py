from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
from PIL import Image, UnidentifiedImageError
import io
import base64
import logging
import pydicom
import numpy as np
import os

# Secure functions for storing reports and managing API keys
from models import store_report
from config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("HighEndImagingAI")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

app = FastAPI(
    title="High-End Medical Imaging AI",
    description="AI-augmented imaging analysis with advanced diagnostic and oncologic biomarker suggestions.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "High-End Medical Imaging AI is operational!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    This endpoint performs advanced AI-driven medical imaging analysis,
    offering high-resolution imaging recommendations (MRI, PET, contrast CT)
    and oncologic biomarker correlation (CA-125, AFP, PSA, etc.).
    """
    # Step 1: File Ingestion
    try:
        image_data = await file.read()
        filename = file.filename.lower()
        logger.info(f"File received: {filename}")
    except Exception as e:
        logger.error("File read error", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to read uploaded file.")

    # Step 2: Distinguish DICOM vs. Standard Image
    try:
        if filename.endswith(".dcm"):
            # Process DICOM
            dicom_data = pydicom.dcmread(io.BytesIO(image_data))
            img_arr = dicom_data.pixel_array
            norm_img = ((img_arr - np.min(img_arr)) / (np.max(img_arr) - np.min(img_arr)) * 255).astype(np.uint8)
            image = Image.fromarray(norm_img)
            logger.info("Processed DICOM successfully.")
        else:
            # Process standard image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Processed standard image: {image.mode}, size {image.size}")

        if image.mode not in ["RGB", "L"]:
            image = image.convert("RGB")

        # Encode image as Base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        base64_img = base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        logger.error("Image processing error", exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid or corrupt image.")

    # Step 3: Construct a GPT-4 prompt with advanced imaging & biomarker suggestions
    advanced_prompt = (
        "You are an advanced medical imaging AI. Generate a board-level diagnostic report with:\n\n"
        "1. Technical Assessment\n"
        "2. Systematic Review of Structures\n"
        "3. Potential Clinical Correlation & Differential Considerations\n"
        "4. Next Steps: Emphasize advanced imaging (MRI, PET-CT, contrast-enhanced scans) and relevant oncologic biomarker tests (CA-125, AFP, PSA, etc.)\n"
        "5. AI-Driven Uncertainty Quantification\n\n"
        "In your systematic review, incorporate any subtle findings that might warrant correlation with biomarkers or high-resolution imaging. "
        "If lung nodules or suspicious masses are present, suggest PET-CT. If hepatic lesions are suspected, consider AFP. "
        "For gynecological masses, note CA-125 correlation. For prostate concerns, mention PSA. "
        "Offer a succinct, high-level analysis that showcases advanced diagnostic reasoning."
    )

    messages = [
        {"role": "system", "content": advanced_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this medical image thoroughly and provide advanced recommendations."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ],
        },
    ]

    # Step 4: Call GPT-4 with advanced reasoning
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-4-turbo" if available
            messages=messages,
            max_tokens=2000,
            temperature=0.2,  # keep it low for factual detail
        )
        result_text = response.choices[0].message.content
        logger.info(f"AI generated report for: {filename}")
    except Exception as e:
        logger.error("OpenAI API error", exc_info=True)
        raise HTTPException(status_code=500, detail="AI processing error.")

    # Step 5: Store the AI report
    try:
        store_report(filename, result_text)
        logger.info(f"Report stored for {filename}")
    except Exception as e:
        logger.warning("Failed to store report", exc_info=True)

    # Step 6: Return the structured result
    return {
        "filename": filename,
        "AI_Analysis": result_text,
    }

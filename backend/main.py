import os
import io
import base64
import logging
import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Secure functions for storing reports; ensure compliance with HIPAA/data protection.
from models import store_report
from config import OPENAI_API_KEY

# Set up robust logging for production.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Import the new asynchronous OpenAI client (v1.0)
from openai import AsyncOpenAI

# Instantiate the async client explicitly.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY))

# Create the FastAPI application with robust metadata.
app = FastAPI(
    title="High-End Medical Imaging AI",
    description=(
        "AI solution for advanced medical imaging analysis. "
    ),
    version="2.0.0",
)

# Configure CORS (adjust allowed origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "High-End Medical Imaging AI is Operational!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    Advanced AI-driven medical imaging analysis endpoint.
    
    Workflow:
      1. Ingest the image file (supports DICOM and standard formats).
      2. Process and normalize the image.
      3. Build an expert diagnostic prompt that includes:
           - High-resolution imaging suggestions (MRI, PET-CT, contrast CT)
           - Oncology biomarker correlation (e.g., CA-125, AFP, PSA)
      4. Invoke OpenAI's GPT-4 asynchronously for analysis.
      5. Store and return a structured, board-level diagnostic report.
    
    This endpoint is production-ready and designed for rigorous clinical review.
    """
    # Step 1: Ingest file
    try:
        image_data = await file.read()
        filename = file.filename.lower()
        logger.info(f"File received: {filename}")
    except Exception as e:
        logger.exception("Error reading uploaded file")
        raise HTTPException(status_code=400, detail="Unable to read uploaded file.")

    # Step 2: Process image (DICOM or standard)
    try:
        if filename.endswith(".dcm"):
            dicom = pydicom.dcmread(io.BytesIO(image_data))
            img_array = dicom.pixel_array
            # Normalize to [0, 255]
            norm_img = ((img_array - np.min(img_array)) / (np.ptp(img_array)) * 255).astype(np.uint8)
            image = Image.fromarray(norm_img)
            logger.info("DICOM image processed successfully.")
        else:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Standard image processed: mode {image.mode}, size {image.size}")
        if image.mode not in ["RGB", "L"]:
            image = image.convert("RGB")
        # Encode image as Base64 for inclusion in prompt
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        b64_image = base64.b64encode(buf.getvalue()).decode()
    except (UnidentifiedImageError, Exception) as e:
        logger.exception("Error processing image")
        raise HTTPException(status_code=400, detail="Image processing failed. Ensure the file is valid.")

    # Step 3: Build the diagnostic prompt with advanced suggestions.
    prompt = (
        "You are an expert-level medical imaging AI. Produce a board-level diagnostic report with the following sections:\n\n"
        "1. Technical Assessment\n"
        "2. Systematic Review of Structures\n"
        "3. Potential Clinical Correlation & Differential Considerations\n"
        "4. Recommended Next Steps (Hypothetical)\n"
        "5. AI-Driven Uncertainty Quantification\n\n"
        "Incorporate the following advanced considerations:\n"
        "🔹 Suggest high-resolution imaging modalities (e.g., MRI, PET-CT, contrast-enhanced CT) if necessary.\n"
        "🔹 Correlate oncologic biomarkers such as CA-125 for ovarian cancer, AFP for liver lesions, PSA for prostate issues, etc.\n"
        "Provide a concise yet detailed analysis, identifying any subtle findings and recommending follow-up investigations."
    )

    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please analyze the provided medical image and generate an expert diagnostic report."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ],
        },
    ]

    # Step 4: Call OpenAI's async API for GPT-4 analysis.
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=2000,
            temperature=0.2  # Low temperature for accuracy
        )
        analysis = response.choices[0].message.content
        logger.info(f"AI analysis generated for file: {filename}")
    except Exception as e:
        logger.exception("OpenAI API error")
        raise HTTPException(status_code=500, detail="AI analysis failed. Please try again later.")

    # Step 5: Store the generated report.
    try:
        store_report(filename, analysis)
        logger.info(f"Report stored for file: {filename}")
    except Exception as e:
        logger.warning("Failed to store report", exc_info=True)

    # Step 6: Return the diagnostic report.
    return {
        "filename": filename,
        "AI_Analysis": analysis,
    }

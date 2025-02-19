import os
import io
import base64
import logging
import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# If using SlowAPI for rate limiting, import here:
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.middleware import SlowAPIMiddleware
# from slowapi.errors import RateLimitExceeded

from models import store_report  # HIPAA-compliant storage function
from config import OPENAI_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Import the new asynchronous OpenAI client (v1.0)
from openai import AsyncOpenAI

# Instantiate the async OpenAI client
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY))

# If using SlowAPI, configure it here:
# limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Medical Images AI",
    description=(
        "A production-grade AI solution for advanced medical imaging analysis. "
        "Generates board-level reports with high-resolution imaging suggestions (MRI, PET-CT, contrast-enhanced CT) "
        "and oncologic biomarker correlations (CA-125, AFP, PSA)."
    ),
    version="2.0.0",
)

# If using SlowAPI:
# app.add_middleware(SlowAPIMiddleware, limiter=limiter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# If using SlowAPI rate limiting:
# @app.exception_handler(RateLimitExceeded)
# async def rate_limit_handler(request, exc):
#     logger.warning("Rate limit exceeded")
#     return HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

@app.get("/")
async def home():
    return {"message": "Medical Images AI is operational!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    Advanced AI-driven medical imaging analysis endpoint, returning headings as Markdown (##, ###).
    """
    # Step 1: Read the file
    try:
        image_data = await file.read()
        filename = file.filename.lower()
        logger.info(f"File received: {filename}")
    except Exception as exc:
        logger.exception("Error reading uploaded file")
        raise HTTPException(status_code=400, detail="Unable to read the uploaded file.")

    # Step 2: Process image (DICOM or standard)
    try:
        if filename.endswith(".dcm"):
            dicom_data = pydicom.dcmread(io.BytesIO(image_data))
            img_array = dicom_data.pixel_array
            # Normalize pixel values to [0, 255]
            norm_img = ((img_array - np.min(img_array)) / (np.ptp(img_array)) * 255).astype(np.uint8)
            image = Image.fromarray(norm_img)
            logger.info("DICOM image processed successfully.")
        else:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Standard image processed: mode={image.mode}, size={image.size}")
        if image.mode not in ["RGB", "L"]:
            image = image.convert("RGB")
        # Encode as Base64 (optional)
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        b64_image = base64.b64encode(buf.getvalue()).decode()
    except (UnidentifiedImageError, Exception) as exc:
        logger.exception("Error processing image")
        raise HTTPException(status_code=400, detail="Image processing failed. Ensure the file is valid.")

    # Step 3: Build the prompt with heading-level Markdown (##, ###) for bold headings
diagnostic_prompt = (
        "You are an advanced medical imaging AI following ACR/ESR guidelines. "
        "Generate a board-level interpretation with these sections EXACTLY. "
        "Use heading-level Markdown (##, ###) so headings appear bold:\n\n"

        "## 1. Technical Assessment\n"
        "### Projection & Positioning\n"
        "The image is an anterior-posterior (AP) chest X-ray. This projection captures the lung fields, heart, "
        "and thoracic structures, including the clavicles, ribs, and portions of the diaphragm.\n"
        "### Image Quality\n"
        "Exposure: The contrast appears acceptable for routine evaluation, though subtle underpenetration cannot be excluded.\n"
        "Rotation: The spinous processes and clavicular alignment suggest minimal rotation.\n"
        "Artifacts: No external lines, tubes, or hardware are evident.\n\n"

        "## 2. Systematic Review of Structures\n"
        "### Cardiac Silhouette & Mediastinum\n"
        "The heart size and contours are within normal limits for an AP projection. The mediastinal structures, including the aortic knob "
        "and tracheal alignment, are properly oriented.\n"
        "### Lungs & Pleural Spaces\n"
        "The lung fields are uniformly radiolucent without focal opacities suggesting consolidation, pneumonia, or mass.\n"
        "The pleural spaces are clear, and the costophrenic angles are sharp, indicating no effusion.\n"
        "### Diaphragm\n"
        "The diaphragm is well visualized, with no signs of elevation or subdiaphragmatic air.\n"
        "### Bones\n"
        "The ribs, spine, and clavicles exhibit normal contours, with no evidence of fractures or lytic lesions.\n"
        "### Trachea & Airways\n"
        "The trachea is centrally positioned, and the airway appears unobstructed.\n"
        "### Soft Tissues\n"
        "No abnormal soft tissue masses or calcifications observed.\n\n"

        "## 3. Potential Clinical Correlation & Differential Considerations\n"
        "### Normal Variation\n"
        "The findings are largely within normal limits for an AP chest X-ray, though mild underexposure may mask minimal pathology.\n"
        "### Early or Minimal Changes\n"
        "In cases of clinical suspicion (e.g., respiratory distress, chest pain), correlate with patient history, labs, etc.\n"
        "### Differential Considerations\n"
        "No significant opacities or structural abnormalities. If symptoms persist, consider additional imaging (PA/lateral views, CT chest).\n\n"

        "## 4. Recommended Next Steps (Hypothetical)\n"
        "### Clinical Correlation\n"
        "Review the patient's presentation, vital signs, and lab findings (including inflammatory markers).\n"
        "### Additional Imaging\n"
        "High-resolution techniques: MRI, PET, or Contrast-Enhanced CT if subtle lesions are suspected.\n"
        "### Oncology Biomarker Correlation\n"
        "If oncologic processes are suspected, correlate with biomarkers such as CA-125, AFP, PSA, or other tumor markers.\n"
        "### Interdisciplinary Consultation\n"
        "Engage radiology, oncology, cardiology, or pulmonology specialists for complex findings.\n\n"

        "## 5. AI-Driven Uncertainty Quantification\n"
        "### Confidence in Findings\n"
        "Absence of Focal Consolidation: ~88% confidence\n"
        "Clear Pleural Spaces: ~92% confidence\n"
        "Normal Cardiac Silhouette: ~85% confidence\n\n"
        "(These confidence levels are illustrative. Always integrate with clinical judgment.)\n\n"
        "Concise Expert Analysis:\n"
        "The AP chest X-ray demonstrates no significant abnormalities. Heart and mediastinal structures are normal, and the lung fields "
        "are largely clear. If clinical symptoms persist, further imaging and interdisciplinary consultation are recommended to rule out "
        "any underlying conditions."
    )


    messages = [
        {"role": "system", "content": diagnostic_prompt},
        {"role": "user", "content": "Please analyze this medical image and generate an expert diagnostic report."}
    ]

    # Step 4: Call GPT-4o asynchronously
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2000,
            temperature=0.2
        )
        analysis = response.choices[0].message.content
        logger.info(f"AI analysis generated for file: {filename}")
    except Exception as exc:
        logger.exception("OpenAI API error")
        raise HTTPException(status_code=500, detail="AI analysis failed. Please try again later.")

    # Step 5: Store the generated report
    try:
        store_report(filename, analysis)
        logger.info(f"Report stored successfully for file: {filename}")
    except Exception as exc:
        logger.warning("Failed to store report", exc_info=True)

    # Step 6: Return the structured diagnostic report
    return {
        "filename": filename,
        "AI_Analysis": analysis,
    }

import os
import io
import base64
import logging
import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# If you have a HIPAA-compliant storage function, import it here.
from models import store_report
from config import OPENAI_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# The new asynchronous OpenAI client (v1.0)
from openai import AsyncOpenAI

# Instantiate the async client
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY))

app = FastAPI(
    title="Medical Images AI",
    description=(
        "AI solution for medical imaging."
    ),
    version="2.0.0",
)

# Basic CORS for demonstration (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "Medical Images AI is operational!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    AI-driven medical imaging.
    """
    # Step 1: Read the file
    try:
        image_data = await file.read()
        filename = file.filename.lower()
        logger.info(f"File received: {filename}")
    except Exception as exc:
        logger.exception("Error reading uploaded file")
        raise HTTPException(status_code=400, detail="Unable to read the uploaded file.")

    # Step 2: Process image (DICOM vs standard)
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

        # Optionally encode as Base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        b64_image = base64.b64encode(buffer.getvalue()).decode()
    except (UnidentifiedImageError, Exception) as exc:
        logger.exception("Error processing image")
        raise HTTPException(status_code=400, detail="Image processing failed. Ensure the file is valid.")

    # Step 3: Build the concise heading-level Markdown prompt
    prompt_md = (
        "You are an advanced medical imaging AI. Provide a board-level report with **no** numeric labeling, "
        "only heading-level Markdown (`##` and `###`) for bold headings:\n\n"

        "## Technical Assessment\n"
        "### Projection & Positioning\n"
        "This is an anterior-posterior (AP) chest X-ray capturing the lungs, heart, and thoracic structures.\n"
        "### Image Quality\n"
        "Exposure appears suitable for routine evaluation, though subtle underpenetration may obscure minor findings.\n"
        "Rotation: Spinous processes/clavicular alignment suggest minimal rotation.\n"
        "Artifacts: No lines, tubes, or hardware noted.\n\n"

        "## Systematic Review of Structures\n"
        "### Cardiac Silhouette & Mediastinum\n"
        "Heart size and contours are within normal limits; mediastinal structures properly oriented.\n"
        "### Lungs & Pleural Spaces\n"
        "No focal opacities indicating consolidation, pneumonia, or mass; pleural spaces are clear.\n"
        "### Diaphragm\n"
        "Diaphragm is well-defined, with no elevation or free air.\n"
        "### Bones\n"
        "Ribs, spine, and clavicles appear intact, no fractures or lytic lesions.\n"
        "### Trachea & Airways\n"
        "Trachea is midline, airway unobstructed.\n"
        "### Soft Tissues\n"
        "No abnormal soft tissue masses or calcifications.\n\n"

        "## Potential Clinical Correlation & Differential Considerations\n"
        "### Normal Variation\n"
        "Findings are largely consistent with a normal AP chest X-ray.\n"
        "### Early or Minimal Changes\n"
        "If clinical suspicion arises (e.g., respiratory distress, chest pain), correlate with labs and history.\n"
        "### Differential Considerations\n"
        "No significant pathology evident; consider further imaging (PA/lateral views, CT chest) if symptoms persist.\n\n"

        "## Recommended Next Steps\n"
        "### Clinical Correlation\n"
        "Evaluate patient presentation, vital signs, labs.\n"
        "### Additional Imaging\n"
        "Consider MRI, PET, or contrast-enhanced CT for subtle or complex findings.\n"
        "### Oncology Biomarker Correlation\n"
        "If malignancy is suspected, correlate with CA-125, AFP, PSA, or other relevant markers.\n"
        "### Interdisciplinary Consultation\n"
        "Involve radiology, oncology, cardiology, or pulmonology for complex cases.\n\n"

        "## AI-Driven Uncertainty Quantification\n"
        "### Confidence in Findings\n"
        "Absence of Focal Consolidation: ~88% confidence\n"
        "Clear Pleural Spaces: ~92% confidence\n"
        "Normal Cardiac Silhouette: ~85% confidence\n\n"
        "_(Values are illustrative; always integrate with clinical judgment.)_\n\n"
        "Concluding Note:\n"
        "No acute abnormalities detected on this AP chest X-ray. If symptoms persist or risk factors are present, "
        "consider advanced imaging or specialist input."
    )

    messages = [
        {"role": "system", "content": prompt_md},
        {"role": "user", "content": "Please analyze this medical image and generate a final report with heading-level Markdown."}
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

    # Step 5: Store the AI-generated report
    try:
        store_report(filename, analysis)
        logger.info(f"Report stored successfully for file: {filename}")
    except Exception as exc:
        logger.warning("Failed to store report", exc_info=True)

    # Step 6: Return the final Markdown-formatted report
    return {
        "filename": filename,
        "AI_Analysis": analysis,
    }

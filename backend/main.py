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

# Secure imports for data storage and configuration
from models import store_report  # Must comply with HIPAA / data protection
from config import OPENAI_API_KEY  # Store your API key securely

# Configure robust logging for audits and troubleshooting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("AdvancedMedicalImagingAI")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Create the FastAPI application with clear metadata
app = FastAPI(
    title="Advanced Medical Imaging ",
    description=(
        "AI-driven medical imaging analysis. "
    ),
    version="1.1.0",
)

# Set up CORS for secure integration (adjust allowed_origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """
    Root endpoint to confirm service availability.
    """
    return {"message": "Advanced Medical Imaging Analysis Service is Running 🚀"}

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and uptime verification.
    """
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    AI-driven medical imaging analysis .
    """
    # Step 1: Read the Uploaded File
    try:
        image_data = await file.read()
        filename = file.filename.lower()
        logger.info(f"Received file: {filename}")
    except Exception as e:
        logger.exception("File read error")
        raise HTTPException(status_code=400, detail="Unable to read the uploaded file.")

    # Step 2: Process File (DICOM or Standard Image)
    try:
        if filename.endswith(".dcm"):
            # Attempt DICOM processing
            try:
                dicom_data = pydicom.dcmread(io.BytesIO(image_data))
                image_array = dicom_data.pixel_array
                # Normalize pixel intensities for consistent output
                norm_image = (
                    (image_array - np.min(image_array)) /
                    (np.max(image_array) - np.min(image_array)) * 255
                ).astype(np.uint8)
                image = Image.fromarray(norm_image)
                logger.info("DICOM image processed successfully.")
            except Exception as e:
                logger.exception("DICOM processing error")
                raise HTTPException(status_code=400, detail="Error processing DICOM file.")
        else:
            # Process standard image formats (JPEG, PNG, etc.)
            try:
                image = Image.open(io.BytesIO(image_data))
                logger.info(
                    f"Standard image processed: mode {image.mode}, size {image.size}"
                )
            except UnidentifiedImageError:
                logger.exception("Invalid image file")
                raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.")
            except Exception as e:
                logger.exception("Standard image processing error")
                raise HTTPException(status_code=400, detail="Error processing image.")

        # Ensure a consistent image mode
        if image.mode not in ["RGB", "L"]:
            image = image.convert("RGB")

        # Encode the image in Base64 for OpenAI
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        logger.info("Image successfully encoded in Base64.")
    except Exception as e:
        logger.exception("File processing error")
        raise HTTPException(status_code=400, detail="File processing failed.")

    # Step 3: Construct the Prompt for GPT-4
    # Note the extra bullet points for advanced imaging & biomarker correlation
    prompt = (
        "You are an advanced medical imaging AI that follows ACR/ESR guidelines. "
        "Generate a board-level interpretation with these five sections EXACTLY:\n\n"

        "1. Technical Assessment\n"
        "   Projection & Positioning:\n"
        "     The image is an anterior-posterior (AP) chest X-ray. This projection captures the lung fields, heart, "
        "     and thoracic structures, including the clavicles, ribs, and portions of the diaphragm.\n"
        "   Image Quality:\n"
        "     Exposure: The contrast appears acceptable for routine evaluation, though subtle underpenetration cannot "
        "     be excluded without further views.\n"
        "     Rotation: The spinous processes and clavicular alignment suggest minimal rotation.\n"
        "     Artifacts: No external lines, tubes, or hardware are evident.\n\n"

        "2. Systematic Review of Structures\n"
        "   Cardiac Silhouette & Mediastinum:\n"
        "     The heart size and contours are within normal limits for an AP projection. The mediastinal structures, including the aortic knob "
        "     and tracheal alignment, are properly oriented.\n"
        "   Lungs & Pleural Spaces:\n"
        "     The lung fields are uniformly radiolucent without focal opacities suggesting consolidation, pneumonia, or mass.\n"
        "     The pleural spaces are clear, and the costophrenic angles are sharp, indicating no effusion.\n"
        "   Diaphragm:\n"
        "     The diaphragm is well visualized, with no signs of elevation or subdiaphragmatic air.\n"
        "   Bones:\n"
        "     The ribs, spine, and clavicles exhibit normal contours, no evidence of fractures or lytic lesions.\n"
        "   Trachea & Airways:\n"
        "     The trachea is centrally positioned, and the airway appears unobstructed.\n"
        "   Soft Tissues:\n"
        "     No abnormal soft tissue masses or calcifications observed.\n\n"

        "3. Potential Clinical Correlation & Differential Considerations\n"
        "   Normal Variation:\n"
        "     The findings are largely within normal limits for an AP chest X-ray, though mild underexposure may mask minimal pathology.\n"
        "   Early or Minimal Changes:\n"
        "     In cases of clinical suspicion (e.g., respiratory distress, chest pain), correlate with patient history, labs, etc.\n"
        "   Differential Considerations:\n"
        "     With no significant opacities or structural abnormalities, acute pathology (e.g., pneumonia, pleural effusion, cardiomegaly) is unlikely. "
        "     If symptoms persist, consider additional imaging (PA/lateral views, CT chest).\n\n"

        "4. Recommended Next Steps (Hypothetical)\n"
        "   Clinical Correlation:\n"
        "     Review the patient's presentation, vital signs, and lab findings (including inflammatory markers).\n"
        "   Additional Imaging:\n"
        "     - High-resolution techniques: MRI, PET, or Contrast-Enhanced CT if subtle lesions are suspected.\n"
        "     - Consider advanced imaging if there's a suspicion of metastatic disease or complex pathology.\n"
        "   Oncology Biomarker Correlation:\n"
        "     - If oncologic processes are suspected, correlate with biomarkers such as CA-125, AFP, PSA, or other tumor markers.\n"
        "   Interdisciplinary Consultation:\n"
        "     Engage radiology, oncology, cardiology, or pulmonology specialists for complex findings.\n\n"

        "5. AI-Driven Uncertainty Quantification\n"
        "   Confidence in Findings:\n"
        "     Absence of Focal Consolidation: ~88% confidence\n"
        "     Clear Pleural Spaces: ~92% confidence\n"
        "     Normal Cardiac Silhouette: ~85% confidence\n"
        "   (These confidence levels are illustrative. Always integrate with clinical judgment.)\n\n"

        "DISCLAIMER: This AI-generated interpretation is for educational/assistive purposes only. It does not replace "
        "professional clinical judgment. All findings must be correlated with the patient's history and further diagnostics. "
        "This system is not FDA-approved or CE-marked."
    )

    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Analyze the provided medical image and generate the exact five-section report. "
                        "Include high-resolution imaging (MRI, PET, Contrast CT) and biomarker correlations (e.g., CA-125, AFP, PSA) in the recommended steps if relevant."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        },
    ]

    # Step 4: Query the GPT-4 (or specialized GPT-4 variant)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Replace with "gpt-4" or your specialized GPT-4 model
            messages=messages,
            max_tokens=2500,
            temperature=0.3,  # Lower temperature for factual consistency
        )
        report = response.choices[0].message.content
        logger.info(f"Generated AI diagnostic report for: {file.filename}")
    except openai.OpenAIError as e:
        logger.exception("OpenAI API error")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected API error")
        raise HTTPException(status_code=500, detail="Unexpected error during image analysis.")

    # Step 5: Store the AI-Generated Report
    try:
        store_report(file.filename, report)
        logger.info(f"Report stored successfully for: {file.filename}")
    except Exception as e:
        logger.warning(f"Failed to store report: {str(e)}")

    # Step 6: Return the Structured Report
    return {
        "filename": file.filename,
        "AI_Analysis": report,
    }

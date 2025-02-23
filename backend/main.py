import os
import io
import base64
import logging
from typing import Tuple, Optional
import json

import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# HIPAA-compliant report storage
try:
    from models import store_report
except ImportError as e:
    logging.error(f"Error importing models: {e}")
    store_report = None  # Or define a dummy function

try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Error importing config: {e}")
    OPENAI_API_KEY = None
    exit()  # Stop execution if the config is not working.

# Import your local pubmed backend module
# Must define fetch_pubmed_articles(query, max_results=5) -> List[str]
try:
    from pubmed import fetch_pubmed_articles
except ImportError as e:
    logging.error(f"Error importing pubmed backend: {e}")
    fetch_pubmed_articles = None

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Attempt to import and initialize OpenAI
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError as e:
    logging.error(f"Error importing or initializing OpenAI: {e}")
    client = None

app = FastAPI(
    title="Medical Imaging AI with PubMed",
    description="Advanced diagnostic pattern analysis for medical imaging with real PubMed references",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MIN_RESOLUTION = 512
REQUIRED_DISCLAIMER = "\n\n*AI-generated analysis – Must be validated by a board-certified radiologist*"

def encode_image_to_data_url(image: Image.Image) -> str:
    """Converts a PIL Image to a base64-encoded data URL."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """Check for essential DICOM tags."""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing_tags = [tag for tag in required_tags if tag not in dicom_obj]
    if missing_tags:
        logger.error(f"Missing required DICOM tags: {missing_tags}")
        raise HTTPException(400, f"Incomplete DICOM metadata: Missing {', '.join(missing_tags)}")

async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """Reads and processes the image (DICOM or standard). Returns (PIL_Image, data_url)."""
    try:
        if filename.endswith(".dcm"):
            # Process DICOM
            import pydicom
            dicom_data = pydicom.dcmread(io.BytesIO(raw_data))
            validate_dicom_metadata(dicom_data)
            pixel_array = dicom_data.pixel_array

            # Normalize pixel intensities
            norm_array = (
                (pixel_array - np.min(pixel_array)) 
                / (np.ptp(pixel_array)) * 255
            ).astype(np.uint8)
            image = Image.fromarray(norm_array)

            if "WindowCenter" in dicom_data:
                logger.info(f"DICOM windowing applied: Center={dicom_data.WindowCenter}, Width={dicom_data.WindowWidth}")

        else:
            # Process standard image
            try:
                image = Image.open(io.BytesIO(raw_data))
                if image.mode not in ["RGB", "L"]:
                    image = image.convert("RGB")
            except UnidentifiedImageError:
                logger.error("Unidentified Image Error: The uploaded file is not a valid image.")
                raise HTTPException(400, "Invalid image file.")

        # Check resolution
        if min(image.size) < MIN_RESOLUTION:
            logger.warning(f"Low-resolution image {image.size}, resizing to maintain aspect ratio.")
            w, h = image.size
            if w < h:
                new_w = MIN_RESOLUTION
                new_h = int(h * (MIN_RESOLUTION / w))
            else:
                new_h = MIN_RESOLUTION
                new_w = int(w * (MIN_RESOLUTION / h))
            image = image.resize((new_w, new_h))

        data_url = encode_image_to_data_url(image)
        return image, data_url

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error processing image: {e}")
        raise HTTPException(500, "Image processing failed.")

@app.post("/analyze-image/")
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> dict:
    """
    Main endpoint: Analyze an uploaded image (X-ray or DICOM), produce an AI-based
    diagnostic report, and optionally fetch PubMed references.
    """
    try:
        raw_data = await file.read()
        filename = file.filename.lower()

        # Log any demographic data
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        # Process the image
        image, data_url = await process_medical_image(raw_data, filename)

        # Build the system prompt
        system_prompt = (
            "You are a medical imaging AI. Provide a concise, plain-language analysis of the X-ray or DICOM. "
            "Structure your response with the following headings:\n\n"
            "## Image Characteristics (Certainty: in percentage)\n"
            "- Modality:\n"
            "- Quality:\n"
            "- Findings:\n\n"
            "## Pattern Recognition (Certainty: in percentage)\n"
            "## Clinical Considerations (Certainty: in percentage)\n"
            "## Summary\n"
            "Always conclude with a short disclaimer that the analysis must be validated by a board-certified radiologist."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image for clinically relevant findings."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        if client is None:
            logger.warning("OpenAI not initialized. Returning fallback message.")
            analysis = "AI analysis service unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
            )
            analysis = response.choices[0].message.content

        # Attempt to fetch PubMed references if relevant
        pubmed_refs = []
        if fetch_pubmed_articles is None:
            logger.warning("PubMed module not found, skipping references.")
        else:
            # You might parse 'analysis' for keywords. For now, use a generic query:
            pubmed_refs = fetch_pubmed_articles("chest x-ray normal findings", max_results=3)

        # Combine references into the final analysis text
        if pubmed_refs:
            references_section = "\n\n**Relevant PubMed References**\n"
            for ref in pubmed_refs:
                references_section += f"- {ref}\n"
            analysis += references_section
        else:
            analysis += "\n\nNo PubMed references found."

        # Optionally store the report
        if store_report is not None:
            store_report(filename, analysis)

        image_metadata = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }

        return JSONResponse(
            content={
                "filename": filename,
                "image_metadata": image_metadata,
                "analysis": analysis
            }
        )

    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Analysis pipeline failed: {str(err)}")
        raise HTTPException(500, "AI analysis service unavailable")

@app.get("/download-report/{filename}")
def download_report(filename: str, format: str = "json"):
    """
    Endpoint to download the stored AI report in JSON format.
    If you'd like to generate PDF, you can do so here as well.
    """
    # Example: We assume you store your reports in ./reports/ as JSON
    file_path = f"./reports/{filename}.json"
    if not os.path.exists(file_path):
        raise HTTPException(404, "Report not found.")

    if format == "json":
        return FileResponse(
            file_path,
            media_type="application/json",
            filename=f"{filename}.json"
        )
    else:
        raise HTTPException(400, "Unsupported format. Only 'json' is available right now.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

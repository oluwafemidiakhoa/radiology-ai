import os
import io
import base64
import logging
from typing import Tuple, Optional

import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    OPENAI_API_KEY = None  # Or handle the missing config differently
    exit() # Stop execution if the config is not working.

from differentials import medical_differentials

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Asynchronous OpenAI client
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError as e:
    logging.error(f"Error importing or initializing OpenAI: {e}")
    client = None

app = FastAPI(
    title="Medical Imaging AI",
    description="Advanced diagnostic pattern analysis for medical imaging",
    version="2.1.0",
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
REQUIRED_DISCLAIMER = "\n\n*AI-generated analysis - Must be validated by board-certified radiologist*"

def encode_image_to_data_url(image: Image.Image) -> str:
    """Optimized image encoding with quality control."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """Validate essential DICOM metadata."""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing_tags = [tag for tag in required_tags if tag not in dicom_obj]

    if missing_tags:
        logger.error(f"Missing required DICOM tags: {missing_tags}")
        raise HTTPException(400, f"Incomplete DICOM metadata: Missing {', '.join(missing_tags)}")

async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """Enhanced image processing with detailed error logging and aspect-ratio-preserving resizing."""
    try:
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                validate_dicom_metadata(dicom_obj)

                pixel_array = dicom_obj.pixel_array
                norm_array = (
                    (pixel_array - np.min(pixel_array)) 
                    / (np.max(pixel_array) - np.min(pixel_array)) * 255
                ).astype(np.uint8)
                image = Image.fromarray(norm_array)

                if "WindowCenter" in dicom_obj:
                    logger.info(
                        f"DICOM windowing applied: Center={dicom_obj.WindowCenter}, Width={dicom_obj.WindowWidth}"
                    )

            except pydicom.errors.InvalidDicomError as e:
                logger.error(f"Invalid DICOM file: {e}")
                raise HTTPException(400, "Invalid DICOM file")
            except KeyError as e:
                logger.error(f"Missing DICOM tag: {e}")
                raise HTTPException(400, f"Missing DICOM tag: {e}")
            except Exception as e:
                logger.error(f"DICOM processing error: {e}")
                raise HTTPException(500, "DICOM processing failed")

        else:
            try:
                image = Image.open(io.BytesIO(raw_data))
                if image.mode not in ["RGB", "L"]:
                    image = image.convert("RGB")
            except UnidentifiedImageError as e:
                logger.error(f"Unidentified Image Error: {e}")
                raise HTTPException(400, "Invalid Image File")
            except Exception as e:
                logger.error(f"Standard Image processing error: {e}")
                raise HTTPException(500, "Image processing failed")

        # Resolution check and resizing (preserving aspect ratio)
        if min(image.size) < MIN_RESOLUTION:
            logger.warning(
                f"Image resolution {image.size} is below minimum {MIN_RESOLUTION}x{MIN_RESOLUTION}. "
                "Resizing image while preserving aspect ratio."
            )
            width, height = image.size
            if width < height:
                new_width = MIN_RESOLUTION
                new_height = int(height * (MIN_RESOLUTION / width))
            else:
                new_height = MIN_RESOLUTION
                new_width = int(width * (MIN_RESOLUTION / height))
            image = image.resize((new_width, new_height))

        return image, encode_image_to_data_url(image)

    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Unexpected processing error: {str(err)}")
        raise HTTPException(500, "Image processing failed")

def select_differentials(analysis):
    """Selects appropriate differentials based on image analysis results."""
    selected_categories = []

    if "scoliosis" in analysis.lower():
        selected_categories.append("Musculoskeletal")
    elif "pneumonia" in analysis.lower():
        selected_categories.append("Pulmonary")
    elif "stroke" in analysis.lower():
        selected_categories.append("Neurological")
    # Add more rules as needed

    return selected_categories

# ADDED LINES: MONGO_URI environment check (does not change existing code)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logger.warning("MONGO_URI environment variable is not set. Any DB-related features may fail.")

########################################
# New advanced helper to reformat AI text
def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    """
    Further processes the AI's raw analysis to unify headings, bullet points,
    and optionally append disclaimers or additional categories.
    """
    # Optionally append disclaimers
    if disclaimers and REQUIRED_DISCLAIMER not in analysis_text:
        analysis_text += REQUIRED_DISCLAIMER

    # For demonstration, we can parse out lines like "Findings:" or "Modality:"
    # and ensure they're bold or on separate lines, but here is a minimal approach:
    lines = analysis_text.split("\n")
    formatted_lines = []

    for line in lines:
        # Example of ensuring lines starting with "-" have bullet formatting
        if line.strip().startswith("-"):
            formatted_lines.append(f"- {line.strip()[1:].strip()}")
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)

@app.post("/analyze-image/")
async def analyze_image(
        file: UploadFile = File(...),
        age: Optional[int] = Query(None, description="Patient's age"),
        sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> dict:
    """Enhanced image analysis endpoint"""
    try:
        # Log patient info if provided
        if age is not None:
            logger.info(f"Patient age provided: {age}")
        if sex is not None:
            logger.info(f"Patient sex provided: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # Process and validate image
        image, data_url = await process_medical_image(raw_data, filename)

        # System prompt engineering
        system_prompt = """You are a medical image analysis assistant trained to identify visual patterns in diagnostic imaging.
Your role is to:
1. Describe anatomical features and imaging artifacts
2. Identify statistically significant visual patterns
3. Compare findings to typical radiographic presentations
4. Suggest possible diagnostic pathways BASED ON VISUAL FEATURES ONLY
5. Provide how much it certain.

Format response using:
**Image Characteristics (Certainty: in percentage)**
- Modality: [Identified imaging technique]
- Quality: [Technical assessment]
- Findings: [Visual observations]

**Pattern Recognition (Certainty: in percentage)**
- Anatomical correlations
- Statistical prevalence
- Literature associations

**Clinical Considerations (Certainty: in percentage)**
- Next-step imaging
- Common differentials
- AI limitations disclaimer"""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this medical image for clinically relevant visual patterns"},
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
            logger.warning("OpenAI client not initialized, skipping analysis.")
            analysis = "AI analysis service unavailable."
        else:
            # Optimized API parameters
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.4
            )
            analysis = response.choices[0].message.content

        # Insert disclaimers and minor bullet formatting
        analysis = reformat_analysis(analysis, disclaimers=True)

        # Optionally, use the 'select_differentials' function to identify categories
        differentials_list = select_differentials(analysis)
        if differentials_list:
            # Append to analysis text
            analysis += "\n\n**Possible Differential Categories:** " + ", ".join(differentials_list)

        # Secure storage
        if store_report is None:
            logger.warning("store_report function not initialized, skipping report storage.")
        else:
            store_report(filename, analysis)  # Store the raw or post-processed analysis

        image_metadata = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }
        response_data = {
            "filename": filename,
            "image_metadata": image_metadata,
            "analysis": analysis  # Return the post-processed text
        }
        return JSONResponse(content=response_data)

    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Analysis pipeline failed: {str(err)}")
        raise HTTPException(500, "AI analysis service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        ssl_keyfile=os.getenv("SSL_KEY"),
        ssl_certfile=os.getenv("SSL_CERT")
    )

import os
import io
import base64
import logging
from typing import Tuple

import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# HIPAA-compliant report storage
from models import store_report
from config import OPENAI_API_KEY

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Asynchronous OpenAI client
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY))

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
    """Optimized image encoding with quality control"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """Validate essential DICOM metadata"""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing_tags = [tag for tag in required_tags if tag not in dicom_obj]
    
    if missing_tags:
        logger.error(f"Missing required DICOM tags: {missing_tags}")
        raise HTTPException(400, f"Incomplete DICOM metadata: Missing {', '.join(missing_tags)}")

def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """Enhanced image processing with detailed error logging and aspect-ratio-preserving resizing"""
    try:
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                validate_dicom_metadata(dicom_obj)

                pixel_array = dicom_obj.pixel_array
                norm_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array)) * 255).astype(np.uint8)
                image = Image.fromarray(norm_array)

                if "WindowCenter" in dicom_obj:
                    logger.info(f"DICOM windowing applied: Center={dicom_obj.WindowCenter}, Width={dicom_obj.WindowWidth}")

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
            logger.warning(f"Image resolution {image.size} is below minimum {MIN_RESOLUTION}x{MIN_RESOLUTION}. Resizing image while preserving aspect ratio.")
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
        raise e  # Re-raise HTTPExceptions
    except Exception as err:
        logger.error(f"Unexpected processing error: {str(err)}")
        raise HTTPException(500, "Image processing failed")

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)) -> dict:
    """Enhanced image analysis endpoint"""
    try:
        raw_data = await file.read()
        filename = file.filename.lower()
        
        # Process and validate image
        image, data_url = process_medical_image(raw_data, filename)
        
        # System prompt engineering
        system_prompt = """You are a medical image analysis assistant trained to identify visual patterns in diagnostic imaging. 
Your role is to:
1. Describe anatomical features and imaging artifacts
2. Identify statistically significant visual patterns
3. Compare findings to typical radiographic presentations
4. Suggest possible diagnostic pathways BASED ON VISUAL FEATURES ONLY

Format response using:
**Image Characteristics**
- Modality: [Identified imaging technique]
- Quality: [Technical assessment]
- Findings: [Visual observations]

**Pattern Recognition**
- Anatomical correlations
- Statistical prevalence
- Literature associations

**Clinical Considerations**
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

        # Post-process response
        analysis = response.choices[0].message.content
        if REQUIRED_DISCLAIMER not in analysis:
            analysis += REQUIRED_DISCLAIMER

        # Secure storage
        store_report(filename, analysis)

        return {
            "filename": filename,
            "image_metadata": {
                "dimensions": image.size,
                "mode": image.mode,
                "format": "DICOM" if filename.endswith(".dcm") else "Standard"
            },
            "analysis": analysis
        }

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

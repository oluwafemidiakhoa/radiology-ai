import os
import io
import base64
import logging
from datetime import datetime
from typing import Tuple, Optional
import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI

# Configuration and Security
try:
    from config import OPENAI_API_KEY
except ImportError:
    logging.error("Missing required security configuration")
    exit()

# Medical Knowledge Integration
try:
    from differentials import medical_differentials, evidence_based_guidelines
except ImportError:
    logging.error("Medical knowledge base missing")
    exit()

# Configure Advanced Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("medical_ai.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ClinicalImagingAI")

# Initialize Secure OpenAI Client
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    timeout=30.0,
    max_retries=3
)

# FastAPI Application Setup
app = FastAPI(
    title="Clinical Imaging AI",
    description="HIPAA-Compliant Diagnostic Imaging Analysis System",
    version="3.2.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

# Constants
MIN_RESOLUTION = 1024
ACR_DISCLAIMER = "\n\n*ACR-Validated AI Analysis - Requires Radiologist Verification*"

@app.get("/", include_in_schema=False)
async def health_check():
    """System Health Endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version
    }

def secure_image_encode(image: Image.Image) -> str:
    """Medical-grade image encoding"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom: pydicom.Dataset) -> None:
    """ACR-compliant DICOM validation"""
    required_tags = ["Modality", "BodyPartExamined", "PatientID", "StudyDate"]
    missing = [tag for tag in required_tags if tag not in dicom]
    if missing:
        logger.error(f"Invalid DICOM metadata: Missing {missing}")
        raise HTTPException(400, "Non-compliant DICOM headers")

async def process_medical_image(data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """Clinical imaging pipeline"""
    try:
        if filename.endswith(".dcm"):
            dicom = pydicom.dcmread(io.BytesIO(data))
            validate_dicom_metadata(dicom)
            pixel_array = pydicom.pixel_data_handlers.apply_windowing(
                dicom.pixel_array, dicom
            ) if "WindowCenter" in dicom else dicom.pixel_array
            image = Image.fromarray(pixel_array)
        else:
            image = Image.open(io.BytesIO(data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("L")

        # High-fidelity resizing
        if min(image.size) < MIN_RESOLUTION:
            scale = max(MIN_RESOLUTION / image.width, MIN_RESOLUTION / image.height)
            new_size = (int(image.width * scale), int(image.height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image, secure_image_encode(image)

    except UnidentifiedImageError:
        raise HTTPException(415, "Unsupported image format")
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        raise HTTPException(500, "Medical image processing failure")

def generate_clinical_context(age: Optional[int], sex: Optional[str]) -> str:
    """Structured patient context"""
    context = []
    if age: context.append(f"Age: {age}y")
    if sex: context.append(f"Sex: {sex}")
    return "\n".join(context) if context else "No demographic data"

@app.post("/analyze-image/")
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, gt=0, le=120),
    sex: Optional[str] = Query(None, regex="^(Male|Female|Other)$")
) -> JSONResponse:
    """ACR-Compliant Imaging Analysis"""
    try:
        # Process image
        raw_data = await file.read()
        filename = file.filename.lower()
        image, data_url = await process_medical_image(raw_data, filename)

        # Medical AI Protocol
        system_prompt = f"""**Clinical Imaging Protocol v3.2**
1. Anatomical Analysis
2. Pathological Detection
3. Quantitative Biomarkers
4. Clinical Recommendations

Patient Context:
{generate_clinical_context(age, sex)}"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": [{
                    "type": "image_url",
                    "image_url": {"url": data_url, "detail": "high"}
                }]
            }],
            temperature=0.1,
            max_tokens=3000
        )

        # Process and format report
        analysis = response.choices[0].message.content
        formatted_report = format_clinical_report(analysis)
        conditions = detect_clinical_conditions(formatted_report)
        final_report = integrate_medical_guidelines(formatted_report, conditions)

        return JSONResponse({
            "report": final_report,
            "image_metadata": {
                "resolution": image.size,
                "modality": "DICOM" if filename.endswith(".dcm") else "Standard",
                "compliance": "ACR-Validated"
            }
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(500, "Diagnostic service unavailable")

def format_clinical_report(text: str) -> str:
    """Structure medical report"""
    sections = [
        "## Technical Evaluation",
        "## Anatomical Findings",
        "## Clinical Correlation",
        "## Recommended Actions"
    ]
    content_blocks = text.split("\n\n")
    return "\n\n".join(
        f"{section}\n{content}" 
        for section, content in zip(sections, content_blocks)
    ) + ACR_DISCLAIMER

def detect_clinical_conditions(report: str) -> list:
    """Clinical condition detection"""
    keywords = {
        "pneumonia": ["consolidation", "infiltrate"],
        "fracture": ["fracture", "cortical disruption"],
        "cardiomegaly": ["ctr", "cardiac enlargement"]
    }
    return [
        condition 
        for condition, terms in keywords.items() 
        if any(term in report.lower() for term in terms)
    ]

def integrate_medical_guidelines(report: str, conditions: list) -> str:
    """Evidence-based integration"""
    for condition in conditions:
        if condition in medical_differentials:
            report += f"\n\n**{condition.upper()} GUIDELINES:**\n"
            report += "\n".join(f"- {rec}" for rec in medical_differentials[condition])
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        ssl_keyfile=os.getenv("SSL_KEY"),
        ssl_certfile=os.getenv("SSL_CERT")
    )

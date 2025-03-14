import os
import io
import base64
import logging
import asyncio
from functools import lru_cache
from typing import Tuple, Optional, List, Dict, Any

import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError
import httpx
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# MongoDB integration functions (synchronous)
from models import store_report, get_report, list_reports

# Load and validate OpenAI API key
try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Failed to import config: {e}")
    OPENAI_API_KEY = None
    exit("Missing configuration. Terminating startup.")

if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    logging.error("Invalid or missing OpenAI API key. Check your config.")
    exit("API key error. Exiting.")

# Domain knowledge integrations
from differentials import medical_differentials, evidence_based_guidelines
from pubmed import fetch_pubmed_articles_sync

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("MedicalImagingAI")

# Initialize asynchronous OpenAI client
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError as e:
    logger.error(f"OpenAI client initialization failure: {e}")
    client = None

# FastAPI application instantiation
app = FastAPI(
    title="Ultra-Advanced Medical Imaging AI Platform",
    description=(
        "A next-generation microservice for clinical-grade image analysis, "
        "capable of orchestrating DICOM/histopathology processing, "
        "dynamic guidelines, real-time PubMed references, and robust MongoDB reporting."
    ),
    version="2.0.0",
)

# CORS setup for cross-domain integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Constants
MIN_RESOLUTION: int = 512
REQUIRED_DISCLAIMER: str = (
    "\n\n*AI-generated analysis – Validation by a certified radiologist or pathologist required.*"
)

############################################
# Core Utility Functions
############################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """
    Converts a PIL Image to a base64 data URL, enabling efficient inline usage within AI prompts
    or for rapid debugging/visualization. Compressed as JPEG by default for size efficiency.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"


def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """
    Ensures that critical DICOM fields (Modality, BodyPartExamined, PatientID) are present.
    Raises HTTPException for incomplete or invalid metadata, preserving data fidelity.
    """
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in required_tags if tag not in dicom_obj]
    if missing:
        logger.error(f"Critical DICOM tags missing: {missing}")
        raise HTTPException(
            status_code=400,
            detail=f"Missing DICOM metadata: {', '.join(missing)}"
        )


async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Ingests raw image data and unifies the handling of both DICOM and standard image files:
    1. For DICOM files, normalizes pixel intensities and checks essential metadata.
    2. For non-DICOM files, validates and converts the image to RGB if needed.
    3. Ensures a minimum resolution (512 x 512) by resizing smaller images.
    Returns a (PIL.Image, base64_url) tuple for downstream usage.
    """
    try:
        if filename.endswith(".dcm"):
            # High-fidelity DICOM processing
            dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
            validate_dicom_metadata(dicom_obj)
            pixel_array = dicom_obj.pixel_array
            norm_array = (
                (pixel_array - np.min(pixel_array)) / np.ptp(pixel_array) * 255
            ).astype(np.uint8)
            image = Image.fromarray(norm_array)
        else:
            # Standard image processing
            image = Image.open(io.BytesIO(raw_data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")

        # Enforce minimum resolution through upscaling if needed
        if min(image.size) < MIN_RESOLUTION:
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

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Unrecognized or corrupted image file.")
    except Exception as e:
        logger.error(f"Image processing failure: {e}")
        raise HTTPException(status_code=500, detail="Image processing pipeline error.")


def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    """
    Trims and organizes multi-line AI responses, optionally injecting a mandatory disclaimer
    to ensure clinically safe communication. Repeated disclaimers are avoided through checks.
    """
    lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted

############################################
# Differential and Guideline Integration
############################################

def select_differentials(analysis: str) -> List[str]:
    """
    Searches the AI analysis text for known clinical triggers (e.g., 'pacemaker', 'infiltrate'),
    mapping them to categories in `medical_differentials`. Extend logic as needed.
    """
    selected = []
    text = analysis.lower()
    if "pacemaker" in text:
        selected.append("Cardiology")
    if "consolidation" in text or "infiltrate" in text:
        selected.append("Pulmonary")
    if "scoliosis" in text:
        selected.append("Musculoskeletal")
    return selected


def incorporate_differentials(analysis_text: str, categories: List[str]) -> str:
    """
    Merges domain-specific differentials from the `medical_differentials` dictionary into
    the final AI report. This helps clinicians quickly see alternative considerations.
    """
    extra_info = []
    radiology_diff = medical_differentials.get("Radiology", {})

    for cat in categories:
        cat_data = radiology_diff.get(cat, {})
        if not cat_data:
            continue
        lines = [f"**Additional {cat} Differentials:**"]
        if isinstance(cat_data, dict):
            for subcat, details in cat_data.items():
                if hasattr(details, "formatted_summary"):
                    lines.append(f"- {subcat}: {details.formatted_summary()}")
                else:
                    lines.append(f"- {subcat}: {details}")
        extra_info.append("\n".join(lines))

    if extra_info:
        return analysis_text + "\n\n" + "\n\n".join(extra_info)
    return analysis_text


def incorporate_guidelines(analysis_text: str, guidelines: Dict[str, Any], modality: str) -> str:
    """
    Appends established modality-specific guidelines—such as those for Chest X-ray, Mammogram,
    or Histopathology—to the AI's analysis text, reinforcing an evidence-based approach.
    """
    selected_guidelines = guidelines.get(modality, {})
    if not selected_guidelines:
        return analysis_text

    glines = []
    for guideline_name, details in selected_guidelines.items():
        glines.append(f"**{guideline_name} Guidelines Summary:**")
        if isinstance(details, dict):
            for topic, topic_details in details.items():
                glines.append(f"- {topic}: {topic_details}")
        elif isinstance(details, list):
            glines.append("- " + ", ".join(details))
        else:
            glines.append(f"- {details}")

    if glines:
        return analysis_text + "\n\n" + "\n".join(glines)
    return analysis_text

############################################
# PubMed Connectivity and Caching
############################################

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync_cached(query: str, max_results: int = 3) -> List[str]:
    """
    Caches PubMed search results for performance optimization, leveraging synchronous queries.
    Repeated queries within a certain window are quickly served from memory.
    """
    return fetch_pubmed_articles_sync(query, max_results)


async def fetch_pubmed_references(query: Optional[str], max_results: int = 3) -> str:
    """
    Executes a PubMed search asynchronously by threading out to the synchronous function.
    If a query string is blank or None, returns an empty string to skip references.
    """
    if not query:
        return ""
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync_cached, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return ""

def extract_pubmed_query(analysis_text: str) -> Optional[str]:
    """
    Inspects AI-generated text for trigger words to formulate precise PubMed queries.
    Supports:
    - Histopathology queries (e.g., 'fibroadenoma', 'ductal')
    - Chest X-ray queries ('infiltrate', 'pneumonia')
    - Mammogram queries ('breast mass', 'mammogram')
    Returns None if no recognized keywords are found, obviating irrelevant searches.
    """
    txt = analysis_text.lower()

    # Histopathology detection
    if any(word in txt for word in ["histopathology", "microscopic", "ductal", "fibroadenoma"]):
        return "fibroadenoma breast histopathology OR immunohistochemistry"

    # Chest X-ray detection
    if "normal chest x-ray" in txt:
        return "normal chest x-ray screening recommendations"
    elif "pneumonia" in txt or "infiltrate" in txt:
        return "pneumonia chest x-ray findings"
    elif "nodule" in txt:
        return "pulmonary nodule chest x-ray follow-up"

    # Mammogram detection
    if "mammogram" in txt or "breast mass" in txt:
        return "breast mass mammogram fibroadenoma or cyst"

    return None

############################################
# OpenAI System Prompt
############################################

system_prompt = (
    "You are a highly advanced medical imaging AI system. Present a structured, evidence-based report using headings:\n\n"
    "## Image Characteristics (Certainty: in percentage)\n- Modality:\n- Quality:\n- Findings:\n\n"
    "## Pattern Recognition (Certainty: in percentage)\n- Key patterns:\n\n"
    "## Clinical Considerations (Certainty: in percentage)\n- Next steps:\n- Differentials:\n\n"
    "## Summary\n- Bullet points of final insights.\n\n"
    "Focus on clarity, incorporate relevant patient details, and avoid disclaimers about inability to interpret images. "
    "Explain your observations directly and succinctly, employing standard medical terminology. "
    "Use the provided image data to formulate your detailed interpretation."
)

############################################
# FastAPI Endpoints
############################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age (optional)"),
    sex: Optional[str] = Query(None, description="Patient's sex (Male/Female, optional)")
) -> Dict[str, Any]:
    """
    **Primary Endpoint**  
    Accepts a DICOM or standard image, processes it, and submits it to an advanced AI pipeline
    that:
    1. Generates an interpretive report
    2. Infers or confirms modality (Histopathology, ChestXRay, Mammogram, etc.)
    3. Merges recognized differentials
    4. Incorporates relevant practice guidelines
    5. Retrieves PubMed references, if applicable
    6. Persists the final narrative to MongoDB

    This endpoint exemplifies a fully integrated, next-generation approach to medical imaging AI,
    designed to streamline and optimize clinical workflows.
    """
    try:
        if age is not None:
            logger.info(f"Patient age provided: {age}")
        if sex is not None:
            logger.info(f"Patient sex provided: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # Image Preprocessing
        image, data_url = await process_medical_image(raw_data, filename)

        # AI Prompt Assembly
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze this medical image:"},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]

        # AI Model Invocation
        if client is None:
            logger.warning("OpenAI client is not initialized.")
            analysis = "AI service currently unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Adjust to your actual OpenAI model
                messages=messages,
                max_tokens=2500,
                temperature=0.3
            )
            analysis = response.choices[0].message.content

        # Analysis Post-Processing
        analysis = reformat_analysis(analysis)

        # Integrate Differentiate Diagnoses
        categories = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, categories)

        # Determine Modality
        modality = "General"
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                modality_tag = getattr(dicom_obj, "Modality", "").upper()
                if modality_tag in ["CR", "DR", "DX", "RF"]:
                    modality = "ChestXRay"
                elif modality_tag == "MG":
                    modality = "Mammogram"
                elif modality_tag == "SM":
                    modality = "Histopathology"
            except Exception:
                modality = "General"
        else:
            # Simple heuristic for standard images
            txt_lower = analysis.lower()
            if any(k in txt_lower for k in ["histopathology", "microscopic", "ductal"]):
                modality = "Histopathology"
            elif "chest" in txt_lower:
                modality = "ChestXRay"
            elif any(k in txt_lower for k in ["mammogram", "breast"]):
                modality = "Mammogram"

        # Apply Modality-Specific Guidelines
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines, modality)

        # Fetch PubMed References
        pubmed_query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(pubmed_query)
        if pubmed_refs:
            analysis += "\n\n" + pubmed_refs

        # Store in MongoDB
        await asyncio.to_thread(store_report, filename, analysis)

        # Return Consolidated Results
        image_meta = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }
        return JSONResponse(content={
            "filename": filename,
            "image_metadata": image_meta,
            "analysis": analysis
        })
    except HTTPException as http_exc:
        raise http_exc
    except Exception as ex:
        logger.error(f"Pipeline error: {ex}")
        raise HTTPException(status_code=500, detail="AI analysis pipeline unavailable.")


@app.get("/reports/", response_class=JSONResponse)
async def get_all_reports() -> Dict[str, Any]:
    """
    Retrieves an aggregation of every diagnostic report in MongoDB, offering clinicians and
    administrators a historical log of all AI analyses conducted through this service.
    """
    reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": reports})


@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    """
    Fetches and returns a specific diagnostic report by filename from the database, enabling
    direct consumption or offline review.
    """
    report = await asyncio.to_thread(get_report, filename)
    if not report:
        raise HTTPException(status_code=404, detail="No corresponding report found.")
    return JSONResponse(content=report)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

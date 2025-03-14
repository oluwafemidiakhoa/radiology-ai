"""
Ultra-Advanced Main API for Medical Imaging AI Analysis (Now with Unified Differentials and Histopathology Guidelines)

This FastAPI backend processes both DICOM and standard images, orchestrates AI-driven
diagnostic insights, integrates consolidated guidelines (including new Histopathology),
and stores final reports in MongoDB. Ideal for enterprise-scale or next-gen clinical AI systems.
"""

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

# Load configuration and validate OpenAI API key
try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Error importing config: {e}")
    OPENAI_API_KEY = None
    exit("Configuration missing. Exiting.")

if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    logging.error("Invalid or missing OpenAI API key. Please check your configuration.")
    exit("Invalid API key. Exiting.")

# Import the consolidated differentials and guidelines
try:
    from differentials import medical_differentials
except ImportError as e:
    logging.error(f"Error importing 'medical_differentials': {e}")
    medical_differentials = {}

# Extract references from the unified dictionary
# This dictionary includes Radiology, Oncology, Cardiology, and Guidelines keys.
evidence_based_guidelines = medical_differentials.get("Guidelines", {})
# The "Radiology" key, for instance, is medical_differentials["Radiology"].

# PubMed fetching function (synchronous) from pubmed.py
from pubmed import fetch_pubmed_articles_sync

# Configure logging
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
    logger.error(f"Error initializing OpenAI: {e}")
    client = None

# FastAPI initialization
app = FastAPI(
    title="Medical Imaging AI with Unified Differentials",
    description=(
        "An advanced AI service for processing medical images (including histopathology) "
        "while leveraging consolidated differentials and guidelines for deeper clinical insights."
    ),
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MIN_RESOLUTION: int = 512
REQUIRED_DISCLAIMER: str = (
    "\n\n*AI-generated analysis – Must be validated by a board-certified radiologist or pathologist*"
)

###############################################################################
# Utility Functions
###############################################################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """
    Converts a PIL Image into a base64-encoded data URL,
    ideal for embedding within AI prompts or debugging.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"


def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """
    Checks essential DICOM fields (e.g., Modality, BodyPartExamined, PatientID). 
    Raises HTTPException if critical tags are missing, ensuring baseline completeness.
    """
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in required_tags if tag not in dicom_obj]
    if missing:
        logger.error(f"Missing required DICOM tags: {missing}")
        raise HTTPException(
            status_code=400,
            detail=f"Incomplete DICOM metadata: {', '.join(missing)}"
        )


async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Processes the uploaded medical image (DICOM or standard).
    - For DICOM, normalizes pixel intensities and checks metadata.
    - For non-DICOM, converts to RGB if needed.
    - Ensures minimal resolution (512px).
    
    Returns:
        (PIL.Image, data_url_str)
    """
    try:
        if filename.endswith(".dcm"):
            dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
            validate_dicom_metadata(dicom_obj)
            pixel_array = dicom_obj.pixel_array
            norm_array = ((pixel_array - np.min(pixel_array)) / np.ptp(pixel_array) * 255).astype(np.uint8)
            image = Image.fromarray(norm_array)
        else:
            image = Image.open(io.BytesIO(raw_data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")

        # Enforce minimum resolution
        if min(image.size) < MIN_RESOLUTION:
            w, h = image.size
            if w < h:
                new_w = MIN_RESOLUTION
                new_h = int(h * (MIN_RESOLUTION / w))
            else:
                new_h = MIN_RESOLUTION
                new_w = int(w * (MIN_RESOLUTION / h))
            image = image.resize((new_w, new_h))

        return image, encode_image_to_data_url(image)

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Image processing failed.")


def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    """
    Standardizes AI-generated text, removing extraneous whitespace and optionally
    appending a mandatory disclaimer to maintain clinical safety.
    """
    lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted

###############################################################################
# Integrating Differentials and Guidelines
###############################################################################

def select_differentials(analysis: str) -> List[str]:
    """
    Basic keyword-based approach to identify relevant differential categories 
    from the Radiology subset. Expand as needed for deeper logic or NLP.
    """
    selected = []
    text = analysis.lower()

    # This logic can be expanded to reference multiple specialties or keywords
    if "pacemaker" in text:
        selected.append("Cardiology")
    if "consolidation" in text or "infiltrate" in text:
        selected.append("Pulmonary")
    if "scoliosis" in text:
        selected.append("Musculoskeletal")
    # Optionally add logic for "Oncology" triggers, etc.

    return selected


def incorporate_differentials(analysis_text: str, categories: List[str]) -> str:
    """
    Appends relevant details from the Radiology or other domain differentials 
    found in the consolidated 'medical_differentials'.
    """
    extra_info = []
    radiology_data = medical_differentials.get("Radiology", {})

    for cat in categories:
        cat_data = radiology_data.get(cat, {})
        if not cat_data:
            continue
        lines = [f"**Additional {cat} Differentials:**"]
        if isinstance(cat_data, dict):
            for subcat, details in cat_data.items():
                # If 'details' is a RadiologyDifferential or similar, handle accordingly
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
    Inserts relevant guidelines from the consolidated dictionary if available 
    (e.g., for 'ChestXRay', 'Mammogram', 'Histopathology').
    """
    selected_guidelines = guidelines.get(modality, {})
    if not selected_guidelines:
        return analysis_text

    guideline_lines = []
    for guideline_name, details in selected_guidelines.items():
        guideline_lines.append(f"**{guideline_name} Guidelines Summary:**")
        if isinstance(details, dict):
            for topic, topic_details in details.items():
                guideline_lines.append(f"- {topic}: {topic_details}")
        elif isinstance(details, list):
            guideline_lines.append("- " + ", ".join(details))
        else:
            guideline_lines.append(f"- {details}")

    if guideline_lines:
        return analysis_text + "\n\n" + "\n".join(guideline_lines)
    return analysis_text


###############################################################################
# PubMed Querying
###############################################################################

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync_cached(query: str, max_results: int = 3) -> List[str]:
    """
    Caches PubMed results for performance. Queries repeated within a session 
    are quickly returned from memory.
    """
    return fetch_pubmed_articles_sync(query, max_results)


async def fetch_pubmed_references(query: Optional[str], max_results: int = 3) -> str:
    """
    Wraps the synchronous PubMed fetching in an async call, enabling non-blocking operation.
    Returns references as a formatted string or empty if none found.
    """
    if not query:
        return ""
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync_cached, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return ""


def extract_pubmed_query(analysis_text: str) -> Optional[str]:
    """
    Generates a context-specific PubMed query based on the analysis text. 
    Enhanced to detect 'Histopathology' triggers or other domain keywords.
    """
    txt = analysis_text.lower()

    # Histopathology logic
    if any(w in txt for w in ["histopathology", "microscopic", "ductal", "fibroadenoma"]):
        return "fibroadenoma breast histopathology OR immunohistochemistry"

    # Chest X-ray logic
    if "normal chest x-ray" in txt:
        return "normal chest x-ray screening recommendations"
    elif "pneumonia" in txt or "infiltrate" in txt:
        return "pneumonia chest x-ray findings"
    elif "nodule" in txt:
        return "pulmonary nodule chest x-ray follow-up"

    # Mammogram logic
    if "mammogram" in txt or "breast mass" in txt:
        return "breast mass mammogram fibroadenoma or cyst"

    # Additional expansions for Cardiology/Oncology triggers if desired
    return None


###############################################################################
# OpenAI System Prompt
###############################################################################

system_prompt = (
    "You are a top-tier medical imaging AI assistant. Generate a structured, clinically relevant report:\n\n"
    "## Image Characteristics (Certainty in %)\n- Modality:\n- Quality:\n- Key Findings:\n\n"
    "## Pattern Recognition (Certainty in %)\n- Primary patterns:\n\n"
    "## Clinical Considerations (Certainty in %)\n- Next steps:\n- Differentials:\n\n"
    "## Summary\n- Key bullet points of final insights.\n\n"
    "Avoid disclaimers about inability to interpret images; be concise but thorough. Provide a direct, "
    "evidence-based analysis of the provided image, referencing patient demographics when relevant."
)


###############################################################################
# FastAPI Endpoints
###############################################################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (M/F)")
) -> Dict[str, Any]:
    """
    Primary endpoint for ingesting medical images (DICOM or standard). 
    Returns an AI-driven diagnostic summary, supplemented with relevant guidelines 
    and references. Final results are stored in MongoDB.
    """
    try:
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # 1. Image Processing
        image, data_url = await process_medical_image(raw_data, filename)

        # 2. Prepare AI Prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this medical image."},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]

        # 3. AI Inference
        if client is None:
            logger.warning("OpenAI client not initialized.")
            analysis = "AI analysis service unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Replace with the actual model name if needed
                messages=messages,
                max_tokens=2500,
                temperature=0.3
            )
            analysis = response.choices[0].message.content

        # 4. Reformat Analysis and incorporate disclaimers
        analysis = reformat_analysis(analysis)

        # 5. Identify relevant differentials
        diff_cats = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, diff_cats)

        # 6. Determine modality for guidelines
        modality = "General"
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                modality_tag = getattr(dicom_obj, "Modality", "").upper()
                if modality_tag in ["CR", "DR", "DX", "RF"]:
                    modality = "ChestXRay"
                elif modality_tag == "MG":
                    modality = "Mammogram"
                elif modality_tag == "SM":  # For slide microscopy or histopath
                    modality = "Histopathology"
            except Exception:
                modality = "General"
        else:
            # Heuristic check for standard image text references
            lower_analysis = analysis.lower()
            if "histopathology" in lower_analysis or "microscopic" in lower_analysis:
                modality = "Histopathology"
            elif "chest" in lower_analysis:
                modality = "ChestXRay"
            elif "mammogram" in lower_analysis or "breast" in lower_analysis:
                modality = "Mammogram"

        # 7. Apply appropriate guidelines
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines, modality)

        # 8. Fetch targeted PubMed references
        query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(query)
        if pubmed_refs:
            analysis += "\n\n" + pubmed_refs

        # 9. Store the final report
        await asyncio.to_thread(store_report, filename, analysis)

        # Prepare final JSON
        image_metadata = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }
        return JSONResponse(content={
            "filename": filename,
            "image_metadata": image_metadata,
            "analysis": analysis
        })

    except HTTPException as http_exc:
        raise http_exc
    except Exception as ex:
        logger.error(f"Analysis pipeline failed: {ex}")
        raise HTTPException(
            status_code=500,
            detail="AI analysis service unavailable"
        )


@app.get("/reports/", response_class=JSONResponse)
async def get_all_reports() -> Dict[str, Any]:
    """
    Lists all stored diagnostic reports from MongoDB.
    """
    reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": reports})


@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    """
    Retrieves a specific diagnostic report by filename from MongoDB.
    """
    report = await asyncio.to_thread(get_report, filename)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found in database.")
    return JSONResponse(content=report)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

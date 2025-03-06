"""
Advanced Main API for Medical Imaging AI Analysis (Updated with Histopathology Modality)

This FastAPI backend processes medical images (including DICOM and standard) using an AI model,
integrates evidence-based guidelines with real-time PubMed references, and stores reports in MongoDB.

Changes in this version:
1. Detects "Histopathology" modality from the AI analysis text or user input.
2. Uses a refined PubMed query to retrieve references relevant to histopathology.
3. Skips references if no relevant query is identified.
4. Conditionally incorporates guidelines if a "Histopathology" section exists in evidence_based_guidelines.
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

# Import dictionaries for differentials and guidelines
from differentials import medical_differentials, evidence_based_guidelines

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

# Initialize FastAPI application
app = FastAPI(
    title="Medical Imaging AI with PubMed",
    description=(
        "Advanced AI-based analysis of medical images (including histopathology), "
        "integrating evidence-based guidelines and real-time PubMed references."
    ),
    version="1.2.0",
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
    "\n\n*AI-generated analysis – Must be validated by a board-certified radiologist*"
)

############################################
# Utility Functions
############################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """Convert a PIL Image to a base64-encoded data URL."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"


def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """Validate that the DICOM dataset contains essential metadata tags."""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in required_tags if tag not in dicom_obj]
    if missing:
        logger.error(f"Missing required DICOM tags: {missing}")
        raise HTTPException(status_code=400, detail=f"Incomplete DICOM metadata: {', '.join(missing)}")


async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Process the uploaded medical image ensuring minimum resolution.
    Handles both DICOM and standard image files.
    """
    try:
        if filename.endswith(".dcm"):
            # Process DICOM
            dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
            validate_dicom_metadata(dicom_obj)
            pixel_array = dicom_obj.pixel_array
            norm_array = ((pixel_array - np.min(pixel_array)) / np.ptp(pixel_array) * 255).astype(np.uint8)
            image = Image.fromarray(norm_array)
        else:
            # Process a standard image
            image = Image.open(io.BytesIO(raw_data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")

        # Resize if below minimum resolution
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
    """Standardize and reformat the AI analysis text, appending a disclaimer if needed."""
    lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted


############################################
# Incorporating Differentials and Guidelines
############################################

def select_differentials(analysis: str) -> List[str]:
    """
    Example placeholder:
    Select differential categories based on keywords in the analysis text.
    Expand or refine for your specific use cases.
    """
    selected = []
    text = analysis.lower()
    if "pacemaker" in text:
        selected.append("Cardiology")
    if "consolidation" in text or "infiltrate" in text:
        selected.append("Pulmonary")
    if "scoliosis" in text:
        selected.append("Musculoskeletal")
    # You can add more logic here if needed.
    return selected


def incorporate_differentials(analysis_text: str, categories: List[str]) -> str:
    """Append additional differential diagnosis details from the `medical_differentials` dictionary."""
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
                    # If details is a RadiologyDifferential or similar
                    lines.append(f"- {subcat}: {details.formatted_summary()}")
                else:
                    lines.append(f"- {subcat}: {details}")
        extra_info.append("\n".join(lines))
    if extra_info:
        return analysis_text + "\n\n" + "\n\n".join(extra_info)
    return analysis_text


def incorporate_guidelines(analysis_text: str, guidelines: Dict[str, Any], modality: str) -> str:
    """
    Append a summary of modality-specific evidence-based guidelines to the analysis text.
    For example, "ChestXRay", "Mammogram", "Histopathology", etc.
    If no guidelines exist for the given modality, it will skip appending.
    """
    selected_guidelines = guidelines.get(modality, {})
    if not selected_guidelines:
        return analysis_text  # No guidelines for this modality

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
# PubMed Query and Fetching
############################################

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync_cached(query: str, max_results: int = 3) -> List[str]:
    """Cached wrapper for the PubMed query to avoid redundant API calls."""
    return fetch_pubmed_articles_sync(query, max_results)


async def fetch_pubmed_references(query: Optional[str], max_results: int = 3) -> str:
    """
    Asynchronously fetch PubMed references by wrapping the synchronous query function.
    If the query is None or empty, returns an empty string.
    """
    if not query:
        return ""
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync_cached, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return ""


def extract_pubmed_query(analysis_text: str) -> Optional[str]:
    """
    Refined function to generate a PubMed query specific to the recognized modality or keywords.
    If no relevant keywords are found, returns None (skips references).
    """
    txt = analysis_text.lower()

    # Histopathology-specific logic
    if "histopathology" in txt or "microscopic" in txt or "ductal" in txt or "fibroadenoma" in txt:
        # Adjust your query to target histopathology or breast pathology
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

    # If no matches, return None to skip references
    return None


############################################
# OpenAI Prompt Definition
############################################

system_prompt = (
    "You are a medical imaging AI assistant. Generate a clear, evidence-based report using headings:\n\n"
    "## Image Characteristics (Certainty: in percentage)\n- Modality:\n- Quality:\n- Findings:\n\n"
    "## Pattern Recognition (Certainty: in percentage)\n- Key patterns:\n\n"
    "## Clinical Considerations (Certainty: in percentage)\n- Next steps:\n- Differentials:\n\n"
    "## Summary\n- Bullet points of final insights.\n\n"
    "Use plain language, incorporate patient demographics, and avoid excessive jargon. "
    "Do NOT include disclaimers about inability to analyze images – provide direct analysis. "
    "Proceed with detailed interpretation of the provided medical image."
)


############################################
# API Endpoints
############################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> Dict[str, Any]:
    """
    Analyze an uploaded medical or histopathology image and return a detailed AI-generated report.
    Processes DICOM and standard image files, generates an AI analysis using an OpenAI model,
    enriches the report with differential diagnoses, modality-specific guidelines, and targeted PubMed references,
    and stores the final report in MongoDB.
    """
    try:
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # Process the medical image
        image, data_url = await process_medical_image(raw_data, filename)

        # Prepare messages for AI analysis
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

        # Generate analysis using the AI model
        if client is None:
            logger.warning("OpenAI client not initialized.")
            analysis = "AI analysis service unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Replace with your actual model name if different
                messages=messages,
                max_tokens=2500,
                temperature=0.3
            )
            analysis = response.choices[0].message.content

        # Reformat the analysis
        analysis = reformat_analysis(analysis)

        # Incorporate differentials (optional logic)
        differential_cats = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, differential_cats)

        # Determine modality for guidelines
        # (1) If it's a DICOM, check DICOM tags. If not, fallback to text heuristics.
        modality = "General"
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                modality_tag = getattr(dicom_obj, "Modality", "").upper()
                if modality_tag in ["CR", "DR", "DX", "RF"]:
                    modality = "ChestXRay"
                elif modality_tag == "MG":
                    modality = "Mammogram"
                elif modality_tag == "SM":  # Example for slide microscopy
                    modality = "Histopathology"
            except Exception:
                modality = "General"
        else:
            # For standard images, we do a heuristic check in the analysis text
            lower_analysis = analysis.lower()
            if "histopathology" in lower_analysis or "microscopic" in lower_analysis or "ductal" in lower_analysis:
                modality = "Histopathology"
            elif "chest" in lower_analysis:
                modality = "ChestXRay"
            elif "mammogram" in lower_analysis or "breast" in lower_analysis:
                modality = "Mammogram"

        # Incorporate modality-specific guidelines if available
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines, modality)

        # Append targeted PubMed references
        pubmed_query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(pubmed_query)
        if pubmed_refs:
            analysis += "\n\n" + pubmed_refs

        # Store the report in MongoDB
        await asyncio.to_thread(store_report, filename, analysis)

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
        logger.error(f"Analysis pipeline failed: {ex}")
        raise HTTPException(status_code=500, detail="AI analysis service unavailable")


@app.get("/reports/", response_class=JSONResponse)
async def get_all_reports() -> Dict[str, Any]:
    """Retrieve all stored diagnostic reports from MongoDB."""
    reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": reports})


@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    """
    Download a specific diagnostic report from MongoDB by filename.
    """
    report = await asyncio.to_thread(get_report, filename)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found in database.")
    return JSONResponse(content=report)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

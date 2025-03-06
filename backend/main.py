"""
main.py (Updated)

Advanced FastAPI Backend for Medical Imaging AI Analysis:
 - Processes DICOM and standard images
 - Generates AI-based analysis using the GPT-4o multimodal model
 - Integrates relevant guidelines (Radiology, Oncology, Cardiology)
 - Fetches domain-specific PubMed references
 - Stores results in MongoDB
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

# MongoDB integration (replace with your actual implementations).
from models import store_report, get_report, list_reports

# Load configuration containing OpenAI API key
try:
    from config import OPENAI_API_KEY
except ImportError:
    logging.error("Could not import config. Check if config.py with OPENAI_API_KEY exists.")
    OPENAI_API_KEY = None

if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    raise SystemExit("Invalid or missing OpenAI API key. Please update your configuration.")

# Import the updated guidelines dictionary & retrieval functions
from evidence_based_guidelines import evidence_based_guidelines

# Import synchronous PubMed fetch function.
from pubmed import fetch_pubmed_articles_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("MedicalImagingAI")

# Initialize the asynchronous OpenAI client using the latest SDK
try:
    from openai import AsyncOpenAI
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    openai_client = None
    logger.warning("OpenAI client not initialized. Please install the openai library.")

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Domain Medical Imaging AI",
    description=(
        "AI-based analysis of medical images, integrating Radiology, "
        "Oncology, and Cardiology guidelines, and relevant PubMed references."
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

MIN_RESOLUTION = 512
REQUIRED_DISCLAIMER = "\n\n*AI-generated analysis – Must be validated by a board-certified radiologist*"

################################################################################
# Utility Functions
################################################################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """Convert a PIL Image to a base64-encoded data URL."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"

def validate_dicom_metadata(dcm: pydicom.Dataset) -> None:
    """Ensure critical DICOM tags are present."""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [t for t in required_tags if t not in dcm]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing DICOM tags: {missing}")

async def process_medical_image(raw: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Load and process an uploaded DICOM or standard image, ensuring minimum resolution.
    Returns:
        - PIL Image
        - base64 data URL
    """
    try:
        if filename.endswith(".dcm"):
            # Handle DICOM
            dcm = pydicom.dcmread(io.BytesIO(raw))
            validate_dicom_metadata(dcm)
            pixels = dcm.pixel_array
            # Normalize pixel values to 0-255 for display
            norm = ((pixels - np.min(pixels)) / (np.ptp(pixels) or 1) * 255).astype(np.uint8)
            image = Image.fromarray(norm)
        else:
            # Handle standard image
            image = Image.open(io.BytesIO(raw))
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

def reformat_analysis(analysis_text: str) -> str:
    """
    Cleanup the AI-generated text and append disclaimers if not present.
    """
    lines = [ln.strip() for ln in analysis_text.splitlines() if ln.strip()]
    joined = "\n".join(lines)
    if REQUIRED_DISCLAIMER not in joined:
        joined += REQUIRED_DISCLAIMER
    return joined

################################################################################
# Domain Detection and Guidelines Incorporation
################################################################################

def detect_domains(analysis_text: str) -> List[str]:
    """
    Simple keyword-based domain detection for Radiology, Oncology, and Cardiology
    based on the AI analysis text.
    """
    text_lower = analysis_text.lower()
    domains = []

    # Radiology triggers
    if any(term in text_lower for term in ["x-ray", "ct", "mri", "radiograph", "dicom", "lung nodule", "pneumonia"]):
        domains.append("radiology")
    # If we see 'mammogram' or 'breast', consider radiology and oncology.
    if "mammogram" in text_lower or "breast" in text_lower:
        if "radiology" not in domains:
            domains.append("radiology")
        if "oncology" not in domains:
            domains.append("oncology")
    # Cardiology triggers
    if any(term in text_lower for term in ["cardiac", "heart", "acs", "pe", "hf", "pacemaker", "arrhythmia"]):
        if "cardiology" not in domains:
            domains.append("cardiology")
    # Oncology triggers
    if any(term in text_lower for term in ["cancer", "tumor", "carcinoma", "malignancy", "metastasis"]):
        if "oncology" not in domains:
            domains.append("oncology")

    if not domains:
        domains.append("radiology")
    return domains

def incorporate_guidelines_by_domain(analysis_text: str, domains: List[str]) -> str:
    """
    Append relevant guidelines from 'evidence_based_guidelines' based on the recognized domains.
    """
    guidelines_sections = []

    # ACR for Radiology
    if "radiology" in domains:
        if any(x in analysis_text.lower() for x in ["mammogram", "breast"]):
            if "ACR" in evidence_based_guidelines and "BI-RADS" in evidence_based_guidelines["ACR"]:
                birads_data = evidence_based_guidelines["ACR"]["BI-RADS"]
                lines = ["**ACR BI-RADS**:"]
                for category, desc in birads_data.items():
                    lines.append(f"- {category}: {desc}")
                guidelines_sections.append("\n".join(lines))
        else:
            if "lung" in analysis_text.lower():
                if "ACR" in evidence_based_guidelines and "LungRADS" in evidence_based_guidelines["ACR"]:
                    lung_data = evidence_based_guidelines["ACR"]["LungRADS"]
                    lines = ["**ACR LungRADS**:"]
                    for cat, desc in lung_data.items():
                        lines.append(f"- {cat}: {desc}")
                    guidelines_sections.append("\n".join(lines))
            else:
                if "ACR" in evidence_based_guidelines and "General_Radiology" in evidence_based_guidelines["ACR"]:
                    gen_rad = evidence_based_guidelines["ACR"]["General_Radiology"]
                    lines = ["**ACR General Radiology Guidelines**:"]
                    for key, val in gen_rad.items():
                        lines.append(f"- {key}: {val}")
                    guidelines_sections.append("\n".join(lines))

    # ESC for Cardiology
    if "cardiology" in domains:
        if "ESC" in evidence_based_guidelines:
            sub_sections = []
            text_lower = analysis_text.lower()
            if any(x in text_lower for x in ["acs", "st elevation", "chest pain"]):
                if "ACS" in evidence_based_guidelines["ESC"]:
                    acs_data = evidence_based_guidelines["ESC"]["ACS"]
                    sub_lines = ["**ESC Guidelines: ACS**:"]
                    for cat, items in acs_data.items():
                        sub_lines.append(f"- {cat}: {items}")
                    sub_sections.append("\n".join(sub_lines))
            if "pe" in text_lower or "pulmonary embol" in text_lower:
                if "PE" in evidence_based_guidelines["ESC"]:
                    pe_data = evidence_based_guidelines["ESC"]["PE"]
                    sub_lines = ["**ESC Guidelines: PE**:"]
                    for cat, items in pe_data.items():
                        sub_lines.append(f"- {cat}: {items}")
                    sub_sections.append("\n".join(sub_lines))
            if any(x in text_lower for x in ["hf", "heart failure"]):
                if "Heart_Failure" in evidence_based_guidelines["ESC"]:
                    hf_data = evidence_based_guidelines["ESC"]["Heart_Failure"]
                    sub_lines = ["**ESC Guidelines: Heart Failure**:"]
                    for cat, items in hf_data.items():
                        sub_lines.append(f"- {cat}: {items}")
                    sub_sections.append("\n".join(sub_lines))
            if not sub_sections:
                esc_lines = ["**ESC Guidelines Summary**:"]
                for section_name, details in evidence_based_guidelines["ESC"].items():
                    esc_lines.append(f"- {section_name}: {details}")
                sub_sections.append("\n".join(esc_lines))
            guidelines_sections.extend(sub_sections)

    # NCCN for Oncology
    if "oncology" in domains:
        if "NCCN" in evidence_based_guidelines:
            text_lower = analysis_text.lower()
            nccn_sections = []
            if any(x in text_lower for x in ["breast", "mammogram"]):
                bc_data = evidence_based_guidelines["NCCN"].get("Breast_Cancer", {})
                bc_lines = ["**NCCN: Breast Cancer**:"]
                for heading, items in bc_data.items():
                    bc_lines.append(f"- {heading}: {items}")
                nccn_sections.append("\n".join(bc_lines))
            elif "lung" in text_lower:
                lc_data = evidence_based_guidelines["NCCN"].get("Lung_Cancer", {})
                lc_lines = ["**NCCN: Lung Cancer**:"]
                for heading, items in lc_data.items():
                    lc_lines.append(f"- {heading}: {items}")
                nccn_sections.append("\n".join(lc_lines))
            elif "colon" in text_lower or "colorectal" in text_lower:
                cc_data = evidence_based_guidelines["NCCN"].get("Colorectal_Cancer", {})
                cc_lines = ["**NCCN: Colorectal Cancer**:"]
                for heading, items in cc_data.items():
                    cc_lines.append(f"- {heading}: {items}")
                nccn_sections.append("\n".join(cc_lines))
            else:
                fallback_lines = ["**NCCN Oncology Guidelines**:"]
                for cancer_type, details in evidence_based_guidelines["NCCN"].items():
                    fallback_lines.append(f"- {cancer_type}: {details}")
                nccn_sections.append("\n".join(fallback_lines))
            guidelines_sections.extend(nccn_sections)

    if guidelines_sections:
        return analysis_text + "\n\n" + "\n\n".join(guidelines_sections)
    else:
        return analysis_text

################################################################################
# PubMed Integration
################################################################################

def generate_domain_specific_pubmed_query(analysis_text: str, domains: List[str]) -> str:
    """
    Create a targeted PubMed query based on recognized domain(s) and keywords in the analysis text.
    """
    lower_text = analysis_text.lower()
    if "oncology" in domains and any(x in lower_text for x in ["breast", "mammogram"]):
        return "breast mass imaging fibroadenoma or malignant tumor mammogram"
    if any(x in domains for x in ["oncology", "radiology"]) and "lung" in lower_text:
        return "lung cancer imaging or lung nodule CT"
    if "cardiology" in domains:
        if "pe" in lower_text:
            return "pulmonary embolism esc guidelines or acute pe diagnosis"
        elif "acs" in lower_text or "stemi" in lower_text:
            return "acute coronary syndrome management or stemi guidelines"
        else:
            return "cardiac imaging or heart failure guidelines"
    if "oncology" in domains and any(x in lower_text for x in ["colon", "colorectal"]):
        return "colorectal cancer imaging or colon tumor"
    return "medical imaging diagnostic guidelines"

@lru_cache(maxsize=32)
def fetch_pubmed_sync_cached(query: str, max_results: int = 5) -> List[str]:
    """Cached wrapper for the synchronous PubMed fetch."""
    return fetch_pubmed_articles_sync(query, max_results)

async def fetch_pubmed_references(analysis_text: str, domains: List[str]) -> str:
    """
    Build a domain-based query and fetch references from PubMed.
    """
    query = generate_domain_specific_pubmed_query(analysis_text, domains)
    refs = await asyncio.to_thread(fetch_pubmed_sync_cached, query, 3)
    if refs:
        lines = ["**Relevant PubMed References:**"]
        lines.extend(f"- {r}" for r in refs)
        return "\n".join(lines)
    return "No PubMed references found."

################################################################################
# OpenAI Prompt
################################################################################

system_prompt = (
    "You are an advanced medical imaging AI assistant. Analyze the provided image and generate a structured report "
    "with headings for 'Image Characteristics', 'Pattern Recognition', 'Clinical Considerations', and 'Summary'. "
    "Do not disclaim inability to diagnose; provide a direct, concise interpretation."
)

################################################################################
# FastAPI Endpoints
################################################################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age (optional)"),
    sex: Optional[str] = Query(None, description="Patient's sex (optional)"),
) -> Dict[str, Any]:
    """
    Upload a medical image (DICOM or standard), generate an AI-based analysis,
    append relevant guidelines & references, then store the report in MongoDB.
    """
    try:
        raw_data = await file.read()
        filename = file.filename.lower()

        # Process the image and generate a base64 URL
        image, data_url = await process_medical_image(raw_data, filename)

        # Prepare chat messages.
        # Note: We now use "file" as the type (supported value) for image inputs.
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Patient age: {age}, sex: {sex}. Analyze this medical image."},
                    {"type": "file", "file": {"url": data_url, "detail": "high"}}
                ],
            },
        ]

        # Generate analysis using GPT-4o if available
        if not openai_client:
            logger.warning("OpenAI client not initialized, returning fallback analysis.")
            analysis = "AI analysis service unavailable."
        else:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",  # Using the GPT-4o multimodal model
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
            )
            analysis = response.choices[0].message.content

        # Reformat analysis and detect domains
        analysis = reformat_analysis(analysis)
        domains = detect_domains(analysis)

        # Incorporate domain-specific guidelines
        analysis = incorporate_guidelines_by_domain(analysis, domains)

        # Append relevant PubMed references
        references = await fetch_pubmed_references(analysis, domains)
        analysis = analysis + "\n\n" + references

        # Store the final report in MongoDB
        await asyncio.to_thread(store_report, filename, analysis)

        # Prepare the response
        image_meta = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard",
        }

        return JSONResponse(
            content={
                "filename": filename,
                "image_metadata": image_meta,
                "analysis": analysis,
            }
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Analysis pipeline failed: {e}")
        raise HTTPException(status_code=500, detail="AI analysis service unavailable")

@app.get("/reports/", response_class=JSONResponse)
async def get_all_reports() -> Dict[str, Any]:
    """List all stored reports from MongoDB."""
    reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": reports})

@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    """Retrieve a specific stored report by filename."""
    report = await asyncio.to_thread(get_report, filename)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return JSONResponse(content=report)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)

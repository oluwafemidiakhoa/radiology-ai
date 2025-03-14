"""
Enhanced Main API for AI-Powered Medical Imaging (Now Including Histopathology)

This FastAPI application processes both DICOM and standard image formats through an AI model,
integrates evidence-based guidelines with dynamic PubMed references, and logs final reports in MongoDB.

New in this release:
1. Identifies “Histopathology” modality from AI output or user input.
2. Applies a refined PubMed query to gather histopathology-specific references.
3. Omits PubMed citations if no pertinent query is generated.
4. Adds guidelines only if a “Histopathology” key is present in `evidence_based_guidelines`.
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

# MongoDB data operations
from models import store_report, get_report, list_reports

# Validate OpenAI API key from config
try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Cannot import config: {e}")
    OPENAI_API_KEY = None
    exit("Configuration not found. Shutting down.")

if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    logging.error("OpenAI API key missing or invalid. Please check your configuration.")
    exit("API key is invalid. Stopping execution.")

# Bring in dictionaries for differential diagnoses and guidelines
from differentials import medical_differentials, evidence_based_guidelines

# Synchronous PubMed retrieval
from pubmed import fetch_pubmed_articles_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("MedicalImagingAI")

# Initialize the asynchronous OpenAI client
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError as e:
    logger.error(f"Could not initialize OpenAI: {e}")
    client = None

# Set up the FastAPI application
app = FastAPI(
    title="Medical Imaging AI with PubMed",
    description=(
        "A next-generation AI service for analyzing medical imaging (including histopathology) "
        "that integrates evidence-based guidelines and PubMed data in real time."
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

# Global constants
MIN_RESOLUTION = 512
REQUIRED_DISCLAIMER = (
    "\n\n*AI-generated content – Requires confirmation by a board-certified radiologist*"
)

#######################################
# Helper Functions
#######################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """
    Converts a PIL Image instance to a base64-encoded data URL.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def validate_dicom_metadata(dicom_data: pydicom.Dataset) -> None:
    """
    Checks that a DICOM dataset contains the required tags for further processing.
    """
    necessary_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in necessary_tags if tag not in dicom_data]
    if missing:
        logger.error(f"Required DICOM tags missing: {missing}")
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient DICOM metadata: {', '.join(missing)}"
        )


async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Reads and converts an uploaded medical image (DICOM or standard) into a PIL Image,
    ensuring it meets the minimum resolution.
    """
    try:
        if filename.endswith(".dcm"):
            # Handle DICOM
            dicom_data = pydicom.dcmread(io.BytesIO(raw_data))
            validate_dicom_metadata(dicom_data)
            pixel_array = dicom_data.pixel_array
            normalized_array = (
                (pixel_array - np.min(pixel_array)) / np.ptp(pixel_array) * 255
            ).astype(np.uint8)
            image = Image.fromarray(normalized_array)
        else:
            # Handle standard image formats
            image = Image.open(io.BytesIO(raw_data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")

        # Enlarge image if it’s below the minimum resolution
        if min(image.size) < MIN_RESOLUTION:
            width, height = image.size
            if width < height:
                new_width = MIN_RESOLUTION
                new_height = int(height * (MIN_RESOLUTION / width))
            else:
                new_height = MIN_RESOLUTION
                new_width = int(width * (MIN_RESOLUTION / height))
            image = image.resize((new_width, new_height))

        return image, encode_image_to_data_url(image)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
    except Exception as e:
        logger.error(f"Error when processing image: {e}")
        raise HTTPException(status_code=500, detail="Image processing failed.")


def reformat_analysis(text: str, include_disclaimer: bool = True) -> str:
    """
    Cleans up the AI-derived text, optionally adding a disclaimer if not present.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    structured = "\n".join(lines)
    if include_disclaimer and REQUIRED_DISCLAIMER not in structured:
        structured += REQUIRED_DISCLAIMER
    return structured


#######################################
# Integrating Differentials & Guidelines
#######################################

def select_differentials(analysis_text: str) -> List[str]:
    """
    Simple keyword-based approach to identify potential differential categories.
    Extend or tailor as necessary.
    """
    selected = []
    lower_text = analysis_text.lower()
    if "pacemaker" in lower_text:
        selected.append("Cardiology")
    if "consolidation" in lower_text or "infiltrate" in lower_text:
        selected.append("Pulmonary")
    if "scoliosis" in lower_text:
        selected.append("Musculoskeletal")
    # Add more conditions or logic if needed.
    return selected


def incorporate_differentials(analysis_text: str, categories: List[str]) -> str:
    """
    Adds supplementary differential diagnostic details from `medical_differentials`.
    """
    extra_sections = []
    radiology_info = medical_differentials.get("Radiology", {})

    for category in categories:
        cat_content = radiology_info.get(category, {})
        if not cat_content:
            continue

        lines = [f"**Additional {category} Differentials:**"]
        if isinstance(cat_content, dict):
            for subcat, details in cat_content.items():
                if hasattr(details, "formatted_summary"):
                    lines.append(f"- {subcat}: {details.formatted_summary()}")
                else:
                    lines.append(f"- {subcat}: {details}")
        extra_sections.append("\n".join(lines))

    if extra_sections:
        return analysis_text + "\n\n" + "\n\n".join(extra_sections)
    return analysis_text


def incorporate_guidelines(
    analysis_text: str, guidelines_data: Dict[str, Any], modality: str
) -> str:
    """
    If relevant guidelines are available for the recognized modality,
    adds a guidelines summary to the analysis text.
    """
    relevant_guidelines = guidelines_data.get(modality, {})
    if not relevant_guidelines:
        return analysis_text

    lines = []
    for guideline_title, guideline_content in relevant_guidelines.items():
        lines.append(f"**{guideline_title} Guidelines Summary:**")
        if isinstance(guideline_content, dict):
            for topic, topic_info in guideline_content.items():
                lines.append(f"- {topic}: {topic_info}")
        elif isinstance(guideline_content, list):
            lines.append("- " + ", ".join(guideline_content))
        else:
            lines.append(f"- {guideline_content}")

    if lines:
        return analysis_text + "\n\n" + "\n".join(lines)
    return analysis_text


#######################################
# PubMed Lookup
#######################################

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync_cached(query: str, max_results: int = 3) -> List[str]:
    """
    Provides a cached call to PubMed, reducing duplicate requests for identical queries.
    """
    return fetch_pubmed_articles_sync(query, max_results)


async def fetch_pubmed_references(query: Optional[str], max_results: int = 3) -> str:
    """
    Runs a PubMed lookup asynchronously. Returns an empty string if `query` is invalid or empty.
    """
    if not query:
        return ""
    references = await asyncio.to_thread(
        fetch_pubmed_articles_sync_cached, query, max_results
    )
    if references:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {ref}" for ref in references)
    return ""


def extract_pubmed_query(analysis_text: str) -> Optional[str]:
    """
    Generates a PubMed query based on detected modalities or keywords. 
    Returns `None` if no relevant keywords are present, thereby skipping references.
    """
    txt = analysis_text.lower()

    # Histopathology-specific rule
    if any(
        keyword in txt
        for keyword in ["histopathology", "microscopic", "ductal", "fibroadenoma"]
    ):
        return "fibroadenoma breast histopathology OR immunohistochemistry"

    # Chest X-ray-based logic
    if "normal chest x-ray" in txt:
        return "normal chest x-ray screening recommendations"
    elif "pneumonia" in txt or "infiltrate" in txt:
        return "pneumonia chest x-ray findings"
    elif "nodule" in txt:
        return "pulmonary nodule chest x-ray follow-up"

    # Mammogram-based logic
    if "mammogram" in txt or "breast mass" in txt:
        return "breast mass mammogram fibroadenoma or cyst"

    # If nothing matches, no references are added
    return None


#######################################
# OpenAI Prompt Configuration
#######################################

system_prompt = (
    "You are a medical imaging AI assistant. Compose a concise, evidence-based report using these headings:\n\n"
    "## Image Characteristics (Certainty: in percentage)\n- Modality:\n- Quality:\n- Findings:\n\n"
    "## Pattern Recognition (Certainty: in percentage)\n- Key patterns:\n\n"
    "## Clinical Considerations (Certainty: in percentage)\n- Next steps:\n- Differentials:\n\n"
    "## Summary\n- Final key points.\n\n"
    "Use accessible language, incorporate relevant demographics, and avoid excessive jargon. "
    "Do not insert disclaimers about inability to interpret images—directly provide an assessment. "
    "Proceed with a detailed interpretation of the supplied medical image."
)


#######################################
# API Routes
#######################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's gender (Male/Female)")
) -> Dict[str, Any]:
    """
    Accepts an uploaded medical or histopathology image and returns an AI-generated report.
    The system handles both DICOM and standard formats, enhances the analysis with differentials,
    modality-specific guidelines, targeted PubMed references, and saves the final outcome to MongoDB.
    """
    try:
        if age is not None:
            logger.info(f"Patient's age: {age}")
        if sex is not None:
            logger.info(f"Patient's sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # Convert and validate the uploaded image
        image, data_url = await process_medical_image(raw_data, filename)

        # Assemble messages for the AI model
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze this medical image."},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]

        # Invoke the AI model for analysis
        if client is None:
            logger.warning("OpenAI client is not initialized.")
            analysis = "AI analysis is currently unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Adjust to your specific model if needed
                messages=messages,
                max_tokens=2500,
                temperature=0.3
            )
            analysis = response.choices[0].message.content

        # Clean and finalize the AI-generated text
        analysis = reformat_analysis(analysis)

        # Integrate differential diagnoses
        diffs = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, diffs)

        # Detect the modality for guidelines
        modality = "General"
        if filename.endswith(".dcm"):
            try:
                dicom_data = pydicom.dcmread(io.BytesIO(raw_data))
                dicom_modality = getattr(dicom_data, "Modality", "").upper()
                if dicom_modality in ["CR", "DR", "DX", "RF"]:
                    modality = "ChestXRay"
                elif dicom_modality == "MG":
                    modality = "Mammogram"
                elif dicom_modality == "SM":  # Example for slide microscopy
                    modality = "Histopathology"
            except Exception:
                modality = "General"
        else:
            # Use textual cues in the analysis
            lowercase_analysis = analysis.lower()
            if any(
                term in lowercase_analysis
                for term in ["histopathology", "microscopic", "ductal"]
            ):
                modality = "Histopathology"
            elif "chest" in lowercase_analysis:
                modality = "ChestXRay"
            elif "mammogram" in lowercase_analysis or "breast" in lowercase_analysis:
                modality = "Mammogram"

        # Add guidelines for the determined modality
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines, modality)

        # Look up and embed PubMed references
        pubmed_query = extract_pubmed_query(analysis)
        references = await fetch_pubmed_references(pubmed_query)
        if references:
            analysis += "\n\n" + references

        # Save the completed report to MongoDB
        await asyncio.to_thread(store_report, filename, analysis)

        image_info = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }
        return JSONResponse(content={
            "filename": filename,
            "image_metadata": image_info,
            "analysis": analysis
        })
    except HTTPException as e:
        raise e
    except Exception as ex:
        logger.error(f"Analysis failed: {ex}")
        raise HTTPException(status_code=500, detail="AI analysis could not be completed.")


@app.get("/reports/", response_class=JSONResponse)
async def get_all_reports() -> Dict[str, Any]:
    """
    Retrieves all stored diagnostic reports from MongoDB.
    """
    all_reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": all_reports})


@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    """
    Fetches a single diagnostic report from MongoDB by filename.
    """
    report_data = await asyncio.to_thread(get_report, filename)
    if not report_data:
        raise HTTPException(status_code=404, detail="No report found with that filename.")
    return JSONResponse(content=report_data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

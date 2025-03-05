"""
Advanced Main API for Medical Imaging AI Analysis

This FastAPI backend processes medical images (DICOM and standard) using an AI model,
integrates evidence-based guidelines with real-time PubMed references, and stores reports in MongoDB.
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

# Import evidence-based guidelines and differential dictionaries
from differentials import medical_differentials, evidence_based_guidelines

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
        "Advanced AI-based analysis of medical images, integrating evidence-based guidelines "
        "and real-time PubMed references."
    ),
    version="1.1.0",
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
REQUIRED_DISCLAIMER: str = "\n\n*AI-generated analysis – Must be validated by a board-certified radiologist*"

############################################
# Utility Functions
############################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """
    Convert a PIL Image to a base64-encoded data URL.
    
    Args:
        image: The PIL Image to encode.
        
    Returns:
        A base64-encoded data URL string.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"


def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """
    Validate that the DICOM dataset contains essential metadata tags.
    
    Args:
        dicom_obj: The DICOM dataset.
    
    Raises:
        HTTPException: If any required tag is missing.
    """
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in required_tags if tag not in dicom_obj]
    if missing:
        logger.error(f"Missing required DICOM tags: {missing}")
        raise HTTPException(status_code=400, detail=f"Incomplete DICOM metadata: {', '.join(missing)}")


async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Process the uploaded medical image ensuring minimum resolution.
    
    Handles both DICOM and standard image files. If the image resolution is below the
    minimum threshold, it is resized while preserving the aspect ratio.
    
    Args:
        raw_data: Raw image data in bytes.
        filename: Name of the uploaded file.
    
    Returns:
        A tuple containing the processed PIL Image and its base64-encoded data URL.
    
    Raises:
        HTTPException: If the image cannot be processed.
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


def select_differentials(analysis: str) -> List[str]:
    """
    Select differential diagnosis categories based on keywords in the analysis text.
    
    Args:
        analysis: AI-generated analysis text.
    
    Returns:
        A list of selected differential categories.
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


def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    """
    Standardize and reformat the AI analysis text, appending a disclaimer if needed.
    
    Args:
        analysis_text: Raw AI analysis text.
        disclaimers: Whether to append the disclaimer.
        
    Returns:
        Reformatted analysis text.
    """
    lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted


def incorporate_differentials(analysis_text: str, categories: List[str]) -> str:
    """
    Append additional differential diagnosis details from the medical_differentials dictionary.
    
    Args:
        analysis_text: Current analysis text.
        categories: List of selected differential categories.
    
    Returns:
        Analysis text enriched with differential details.
    """
    extra_info = []
    try:
        radiology_diff = medical_differentials.get("Radiology", {})
    except Exception as e:
        logger.error(f"Error retrieving Radiology differentials: {e}")
        radiology_diff = {}

    for cat in categories:
        try:
            # Assume radiology_diff is a dictionary mapping condition names to details
            cat_data = radiology_diff.get(cat, {})
            lines = [f"**Additional {cat} Differentials:**"]
            # If cat_data is a dictionary of sub-entries, iterate over them
            if isinstance(cat_data, dict):
                for subcat, details in cat_data.items():
                    if isinstance(details, dict):
                        desc = details.get("Description", "No description available.")
                        lines.append(f"- **{subcat}**: {desc}")
                    else:
                        lines.append(f"- {subcat}: {details}")
            extra_info.append("\n".join(lines))
        except Exception as e:
            logger.warning(f"Error incorporating differentials for {cat}: {e}")
            continue
    if extra_info:
        return analysis_text + "\n\n" + "\n\n".join(extra_info)
    return analysis_text


def incorporate_guidelines(analysis_text: str, guidelines: Dict[str, Any]) -> str:
    """
    Append a summary of evidence-based guidelines to the analysis text.
    
    Args:
        analysis_text: Current analysis text.
        guidelines: Guidelines information.
    
    Returns:
        Analysis text enriched with guideline summaries.
    """
    glines = []
    for org, topics in guidelines.items():
        glines.append(f"**{org} Guidelines Summary:**")
        for topic, details in topics.items():
            if isinstance(details, dict):
                points = ", ".join(f"{k}: {v}" for k, v in details.items())
                glines.append(f"- {topic}: {points}")
            elif isinstance(details, list):
                glines.append(f"- {topic}: " + ", ".join(details))
            else:
                glines.append(f"- {topic}: {details}")
    if glines:
        return analysis_text + "\n\n" + "\n".join(glines)
    return analysis_text


def extract_pubmed_query(analysis_text: str) -> str:
    """
    Extract a focused PubMed query based on key terms in the analysis text.
    
    Args:
        analysis_text: AI-generated analysis text.
    
    Returns:
        A PubMed search query.
    """
    txt = analysis_text.lower()
    if "pacemaker" in txt:
        return "pacemaker leads chest x-ray"
    elif "consolidation" in txt or "infiltrate" in txt:
        return "lung consolidation chest x-ray"
    else:
        return "chest x-ray diagnostic findings"


@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync(query: str, max_results: int = 3) -> List[str]:
    """
    Synchronously query PubMed for articles related to the provided query.
    
    Caches results to minimize redundant network calls.
    
    Args:
        query: The search query.
        max_results: Maximum number of articles to retrieve.
    
    Returns:
        A list of formatted reference strings.
    """
    pubmed_api = os.getenv("PUB_MED_API")
    if not pubmed_api:
        return ["No PubMed API key provided."]
    
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "api_key": pubmed_api
    }
    try:
        search_resp = httpx.get(esearch_url, params=params)
        if search_resp.status_code != 200:
            return ["PubMed search failed."]
        data = search_resp.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return ["No relevant PubMed articles found."]
        
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
            "api_key": pubmed_api
        }
        summary_resp = httpx.get(esummary_url, params=params)
        if summary_resp.status_code != 200:
            return ["PubMed summary retrieval failed."]
        sum_data = summary_resp.json().get("result", {})
        
        refs = []
        for pid in ids:
            article = sum_data.get(pid, {})
            title = article.get("title", "No title")
            pubdate = article.get("pubdate", "Unknown date")
            source = article.get("source", "Unknown source")
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            refs.append(f"**{title}** ({pubdate}, {source}) [Read more]({link})")
        return refs
    except Exception as e:
        return [f"Error retrieving PubMed references: {str(e)}"]

async def fetch_pubmed_references(query: str, max_results: int = 3) -> str:
    """
    Asynchronously fetch PubMed references by wrapping the synchronous query function.
    
    Args:
        query: The search query.
        max_results: Maximum number of articles to retrieve.
    
    Returns:
        A formatted string containing PubMed references.
    """
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return "No PubMed references found."


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
    Analyze an uploaded medical image and return a detailed AI-generated report.
    
    Processes DICOM and standard image files, generates an AI analysis using an OpenAI model,
    enriches the report with differential diagnoses and evidence-based guidelines, appends PubMed references,
    and stores the final report in MongoDB.
    
    Args:
        file: The uploaded image file.
        age: Optional patient age.
        sex: Optional patient sex.
    
    Returns:
        A JSON response containing the filename, image metadata, and AI analysis.
    
    Raises:
        HTTPException: If processing or analysis fails.
    """
    try:
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()
        image, data_url = await process_medical_image(raw_data, filename)

        # Construct the system prompt for AI analysis
        system_prompt = (
            "You are a medical imaging AI assistant. Generate a clear, evidence-based report using headings:\n\n"
            "## Image Characteristics (Certainty: in percentage)\n- Modality:\n- Quality:\n- Findings:\n\n"
            "## Pattern Recognition (Certainty: in percentage)\n- Key patterns:\n\n"
            "## Clinical Considerations (Certainty: in percentage)\n- Next steps:\n- Differentials:\n\n"
            "## Summary\n- Bullet points of final insights.\n\n"
            "Use plain language, incorporate patient demographics, and avoid excessive jargon. "
            "Do NOT include any disclaimers about inability to analyze images – provide direct analysis. "
            "Proceed with detailed interpretation of the provided medical image."
        )

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

        if client is None:
            logger.warning("OpenAI client not initialized.")
            analysis = "AI analysis service unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2500,
                temperature=0.3
            )
            analysis = response.choices[0].message.content

        # Process and enrich the analysis report
        analysis = reformat_analysis(analysis)
        differential_cats = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, differential_cats)
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines)

        # Append PubMed references
        pubmed_query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(pubmed_query)
        analysis += "\n\n" + pubmed_refs

        # Store report in MongoDB asynchronously (wrap synchronous call)
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
    """
    Retrieve all stored diagnostic reports from MongoDB.
    
    Returns:
        A JSON response containing a list of reports.
    """
    reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": reports})


@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    """
    Download a specific diagnostic report from MongoDB by filename.
    
    Args:
        filename: The report filename.
    
    Returns:
        A JSON response containing the report details.
    
    Raises:
        HTTPException: If the report is not found.
    """
    report = await asyncio.to_thread(get_report, filename)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found in database.")
    return JSONResponse(content=report)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

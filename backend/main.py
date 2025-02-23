import os
import io
import base64
import logging
import asyncio
from functools import lru_cache
from typing import Tuple, Optional

import numpy as np
import pydicom
from PIL import Image, UnidentifiedImageError
import httpx  # For asynchronous HTTP requests to PubMed

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# HIPAA-compliant report storage
try:
    from models import store_report
except ImportError as e:
    logging.error(f"Error importing models: {e}")
    store_report = None

try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Error importing config: {e}")
    OPENAI_API_KEY = None
    exit()  # Critical error; stop execution if config is missing.

# Import differentials and evidence-based guidelines
from differentials import medical_differentials, evidence_based_guidelines

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Asynchronous OpenAI client initialization
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError as e:
    logger.error(f"Error initializing OpenAI: {e}")
    client = None

app = FastAPI(
    title="Medical Imaging AI with PubMed",
    description="Advanced diagnostic pattern analysis for medical imaging with real-time evidence-based PubMed references.",
    version="3.1.0",
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

############################################
# Helper Functions

def encode_image_to_data_url(image: Image.Image) -> str:
    """Converts a PIL Image to a base64-encoded data URL."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """Checks for essential DICOM tags."""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing_tags = [tag for tag in required_tags if tag not in dicom_obj]
    if missing_tags:
        logger.error(f"Missing required DICOM tags: {missing_tags}")
        raise HTTPException(400, f"Incomplete DICOM metadata: Missing {', '.join(missing_tags)}")

async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """Processes the uploaded image (DICOM or standard) and ensures minimum resolution."""
    try:
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                validate_dicom_metadata(dicom_obj)
                pixel_array = dicom_obj.pixel_array
                norm_array = ((pixel_array - np.min(pixel_array)) / (np.ptp(pixel_array)) * 255).astype(np.uint8)
                image = Image.fromarray(norm_array)
                if "WindowCenter" in dicom_obj:
                    logger.info(f"DICOM windowing: Center={dicom_obj.WindowCenter}, Width={dicom_obj.WindowWidth}")
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
                logger.error(f"Unidentified image error: {e}")
                raise HTTPException(400, "Invalid image file")
            except Exception as e:
                logger.error(f"Standard image processing error: {e}")
                raise HTTPException(500, "Image processing failed")
        if min(image.size) < MIN_RESOLUTION:
            logger.warning(f"Low resolution {image.size}; resizing to {MIN_RESOLUTION}x{MIN_RESOLUTION}.")
            w, h = image.size
            if w < h:
                new_w = MIN_RESOLUTION
                new_h = int(h * (MIN_RESOLUTION / w))
            else:
                new_h = MIN_RESOLUTION
                new_w = int(w * (MIN_RESOLUTION / h))
            image = image.resize((new_w, new_h))
        return image, encode_image_to_data_url(image)
    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Unexpected image processing error: {err}")
        raise HTTPException(500, "Image processing failed")

def select_differentials(analysis: str):
    """Selects differential categories based on the AI analysis text."""
    selected = []
    lower_text = analysis.lower()
    if "pacemaker" in lower_text:
        selected.append("Cardiology")
    if "consolidation" in lower_text or "infiltrate" in lower_text:
        selected.append("Pulmonary")
    if "scoliosis" in lower_text:
        selected.append("Musculoskeletal")
    # Extend with additional rules as needed
    return selected

def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    """
    Reformats the AI analysis text by removing extra spaces and standardizing headings.
    Emphasizes plain language and evidence-based conclusions.
    """
    lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted

def incorporate_differentials(analysis_text: str, categories: list) -> str:
    """Appends differential diagnosis details from the medical_differentials dictionary."""
    add_info = []
    for cat in categories:
        try:
            cat_data = medical_differentials["Radiology"][cat]
            info_lines = [f"**Additional {cat} Differentials:**"]
            for subcat, details in cat_data.items():
                if isinstance(details, dict):
                    desc = details.get("Description", "No description available.")
                    info_lines.append(f"- **{subcat}**: {desc}")
                else:
                    info_lines.append(f"- {subcat}: {details}")
            add_info.append("\n".join(info_lines))
        except KeyError:
            logger.warning(f"No dictionary entry found for category '{cat}'.")
            continue
    if add_info:
        return analysis_text + "\n\n" + "\n\n".join(add_info)
    return analysis_text

def incorporate_guidelines(analysis_text: str, guidelines: dict) -> str:
    """Appends a simplified summary of evidence-based guidelines to the analysis text."""
    guide_lines = []
    for org, topics in guidelines.items():
        guide_lines.append(f"**{org} Guidelines Summary:**")
        for topic, details in topics.items():
            if isinstance(details, dict):
                points = ", ".join(f"{k}: {v}" for k, v in details.items())
                guide_lines.append(f"- {topic}: {points}")
            elif isinstance(details, list):
                guide_lines.append(f"- {topic}: " + ", ".join(details))
            else:
                guide_lines.append(f"- {topic}: {details}")
    if guide_lines:
        return analysis_text + "\n\n" + "\n".join(guide_lines)
    return analysis_text

def extract_pubmed_query(analysis_text: str) -> str:
    """
    Extracts a focused PubMed query based on key findings in the analysis text.
    """
    lower_text = analysis_text.lower()
    if "pacemaker" in lower_text:
        return "pacemaker leads chest x-ray"
    elif "consolidation" in lower_text or "infiltrate" in lower_text:
        return "lung consolidation chest x-ray"
    else:
        return "chest x-ray diagnostic findings"

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync(query: str, max_results: int = 3) -> list:
    """Synchronous function to query PubMed and return a list of formatted article references."""
    pubmed_api = os.getenv("PUB_MED_API")
    if not pubmed_api:
        logger.warning("PUB_MED_API is not set. Skipping PubMed references.")
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
        search_resp = requests.get(esearch_url, params=params)
        if search_resp.status_code != 200:
            logger.error(f"PubMed search failed with status: {search_resp.status_code}")
            return ["PubMed search failed."]
        search_data = search_resp.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return ["No relevant PubMed articles found."]
        
        params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
            "api_key": pubmed_api
        }
        summary_resp = requests.get(esummary_url, params=params)
        if summary_resp.status_code != 200:
            logger.error(f"PubMed summary retrieval failed with status: {summary_resp.status_code}")
            return ["PubMed summary retrieval failed."]
        summary_data = summary_resp.json().get("result", {})
        
        references = []
        for pid in id_list:
            article = summary_data.get(pid, {})
            title = article.get("title", "No title available")
            pubdate = article.get("pubdate", "Unknown date")
            source = article.get("source", "Unknown source")
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            references.append(f"**{title}** ({pubdate}, {source}) [Read more]({link})")
        return references
    except Exception as e:
        logger.error(f"Error querying PubMed: {e}")
        return [f"Error retrieving PubMed references: {str(e)}"]

async def fetch_pubmed_references(query: str, max_results: int = 3) -> str:
    """Asynchronous wrapper for fetching PubMed references."""
    references = await asyncio.to_thread(fetch_pubmed_articles_sync, query, max_results)
    if references:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {ref}" for ref in references)
    return "No PubMed references found."

############################################

@app.post("/analyze-image/")
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> dict:
    """
    Advanced image analysis endpoint with AI diagnostic report generation,
    evidence-based guidelines, and real-time PubMed references.
    """
    try:
        if age is not None:
            logger.info(f"Patient age provided: {age}")
        if sex is not None:
            logger.info(f"Patient sex provided: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        image, data_url = await process_medical_image(raw_data, filename)

        # Build advanced system prompt with clear plain language instructions
        system_prompt = (
            "You are a medical imaging AI assistant. Analyze the diagnostic image and generate a clear, evidence-based report in plain language. "
            "Structure your response with the following headings (use Markdown):\n\n"
            "## Image Characteristics (Certainty: in percentage)\n"
            "- Modality:\n"
            "- Quality:\n"
            "- Findings:\n\n"
            "## Pattern Recognition (Certainty: in percentage)\n"
            "- Key visual patterns and correlations:\n\n"
            "## Clinical Considerations (Certainty: in percentage)\n"
            "- Recommended next steps:\n"
            "- Common differentials:\n\n"
            "## Summary\n"
            "- Concise bullet-point overview of key findings.\n\n"
            "Use simple, plain language. Incorporate patient demographics if available. "
            "Avoid excessive technical jargon."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image for clinically relevant findings."},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]
        if client is None:
            logger.warning("OpenAI client not initialized; returning fallback message.")
            analysis = "AI analysis service unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2500,
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.4
            )
            analysis = response.choices[0].message.content

        analysis = reformat_analysis(analysis, disclaimers=True)
        detected_categories = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, detected_categories)
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines)
        
        # Extract focused PubMed query and fetch references
        pubmed_query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(pubmed_query, max_results=3)
        analysis += "\n\n" + pubmed_refs

        if store_report is not None:
            store_report(filename, analysis)

        image_metadata = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }
        response_data = {
            "filename": filename,
            "image_metadata": image_metadata,
            "analysis": analysis
        }
        return JSONResponse(content=response_data)

    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Analysis pipeline failed: {err}")
        raise HTTPException(500, "AI analysis service unavailable")

def extract_pubmed_query(analysis_text: str) -> str:
    """
    Extracts a focused PubMed query based on key terms in the analysis.
    """
    lower_text = analysis_text.lower()
    if "pacemaker" in lower_text:
        return "pacemaker leads chest x-ray"
    elif "consolidation" in lower_text or "infiltrate" in lower_text:
        return "lung consolidation chest x-ray"
    else:
        return "chest x-ray diagnostic findings"

@app.get("/download-report/{filename}")
def download_report(filename: str, format: str = "json"):
    """
    Endpoint to download the stored AI report in JSON format.
    Extendable to support PDF downloads.
    """
    file_path = f"./reports/{filename}.json"
    if not os.path.exists(file_path):
        raise HTTPException(404, "Report not found.")
    if format == "json":
        return FileResponse(file_path, media_type="application/json", filename=f"{filename}.json")
    else:
        raise HTTPException(400, "Unsupported format. Only 'json' is available at this time.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

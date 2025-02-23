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
import httpx  # For asynchronous HTTP requests

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# HIPAA-compliant report storage
try:
    from models import store_report
except ImportError as e:
    logging.error(f"Error importing models: {e}")
    store_report = None  # Fallback if not using DB

# Load configuration
try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Error importing config: {e}")
    OPENAI_API_KEY = None
    exit()  # Stop execution if config is missing

# Extra API key validation check
if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    logging.error("Invalid or missing OpenAI API key. Please check your configuration.")
    exit()

# Import differentials and evidence-based guidelines
from differentials import medical_differentials, evidence_based_guidelines

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

app = FastAPI(
    title="Medical Imaging AI with PubMed",
    description="Advanced AI-based analysis of medical images, integrating evidence-based guidelines & real-time PubMed references.",
    version="1.0.0",
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
# Helper functions

def encode_image_to_data_url(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in required_tags if tag not in dicom_obj]
    if missing:
        logger.error(f"Missing required DICOM tags: {missing}")
        raise HTTPException(400, f"Incomplete DICOM metadata: {', '.join(missing)}")

async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    try:
        if filename.endswith(".dcm"):
            dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
            validate_dicom_metadata(dicom_obj)
            pixel_array = dicom_obj.pixel_array
            norm_array = ((pixel_array - np.min(pixel_array)) / (np.ptp(pixel_array)) * 255).astype(np.uint8)
            image = Image.fromarray(norm_array)
        else:
            image = Image.open(io.BytesIO(raw_data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")
        
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
        raise HTTPException(400, "Invalid image file.")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(500, "Image processing failed.")

def select_differentials(analysis: str):
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
    lines = [l.strip() for l in analysis_text.splitlines() if l.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted

def incorporate_differentials(analysis_text: str, categories: list) -> str:
    extra_info = []
    for cat in categories:
        try:
            cat_data = medical_differentials["Radiology"][cat]
            lines = [f"**Additional {cat} Differentials:**"]
            for subcat, details in cat_data.items():
                if isinstance(details, dict):
                    desc = details.get("Description", "No description available.")
                    lines.append(f"- **{subcat}**: {desc}")
                else:
                    lines.append(f"- {subcat}: {details}")
            extra_info.append("\n".join(lines))
        except KeyError:
            logger.warning(f"No dictionary entry found for category '{cat}'.")
            continue
    if extra_info:
        return analysis_text + "\n\n" + "\n\n".join(extra_info)
    return analysis_text

def incorporate_guidelines(analysis_text: str, guidelines: dict) -> str:
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
    txt = analysis_text.lower()
    if "pacemaker" in txt:
        return "pacemaker leads chest x-ray"
    elif "consolidation" in txt or "infiltrate" in txt:
        return "lung consolidation chest x-ray"
    else:
        return "chest x-ray diagnostic findings"

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync(query: str, max_results: int = 3) -> list:
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
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return "No PubMed references found."

############################################

@app.post("/analyze-image/")
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> dict:
    try:
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()
        image, data_url = await process_medical_image(raw_data, filename)

        system_prompt = (
            "You are a medical imaging AI assistant. Generate a clear, evidence-based report using headings:\n\n"
            "## Image Characteristics (Certainty: in percentage)\n- Modality:\n- Quality:\n- Findings:\n\n"
            "## Pattern Recognition (Certainty: in percentage)\n- Key patterns:\n\n"
            "## Clinical Considerations (Certainty: in percentage)\n- Next steps:\n- Differentials:\n\n"
            "## Summary\n- Bullet points of final insights.\n\n"
            "Use plain language, incorporate patient demographics, avoid excessive jargon. "
            "Do NOT include any disclaimers about inability to analyze images - provide direct analysis. "
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

        analysis = reformat_analysis(analysis)
        cats = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, cats)
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines)

        query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(query)
        analysis += "\n\n" + pubmed_refs

        if store_report:
            store_report(filename, analysis)

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
    except HTTPException as e:
        raise e
    except Exception as ex:
        logger.error(f"Analysis pipeline failed: {ex}")
        raise HTTPException(500, "AI analysis service unavailable")

@app.get("/download-report/{filename}")
def download_report(filename: str, format: str = "json"):
    file_path = f"./reports/{filename}.json"
    if not os.path.exists(file_path):
        raise HTTPException(404, "Report not found.")
    if format == "json":
        return FileResponse(file_path, media_type="application/json", filename=f"{filename}.json")
    else:
        raise HTTPException(400, "Unsupported format. Only 'json' is available.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
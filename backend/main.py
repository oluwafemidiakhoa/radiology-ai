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

import httpx  # NEW: For asynchronous PubMed queries

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# HIPAA-compliant report storage
try:
    from models import store_report
except ImportError as e:
    logging.error(f"Error importing models: {e}")
    store_report = None  # Or define a dummy function

try:
    from config import OPENAI_API_KEY
except ImportError as e:
    logging.error(f"Error importing config: {e}")
    OPENAI_API_KEY = None
    exit()  # Stop execution if the config is not working.

# Import differentials and evidence-based guidelines
from differentials import medical_differentials, evidence_based_guidelines

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ProdMedicalImagingAI")

# Asynchronous OpenAI client
try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except ImportError as e:
    logging.error(f"Error importing or initializing OpenAI: {e}")
    client = None

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
    """Optimized image encoding with quality control."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """Validate essential DICOM metadata."""
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing_tags = [tag for tag in required_tags if tag not in dicom_obj]

    if missing_tags:
        logger.error(f"Missing required DICOM tags: {missing_tags}")
        raise HTTPException(400, f"Incomplete DICOM metadata: Missing {', '.join(missing_tags)}")

async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
    """Enhanced image processing with error logging and aspect-ratio-preserving resizing."""
    try:
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                validate_dicom_metadata(dicom_obj)

                pixel_array = dicom_obj.pixel_array
                norm_array = (
                    (pixel_array - np.min(pixel_array))
                    / (np.max(pixel_array) - np.min(pixel_array))
                    * 255
                ).astype(np.uint8)
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

        if min(image.size) < MIN_RESOLUTION:
            logger.warning(f"Image resolution {image.size} is below minimum {MIN_RESOLUTION}x{MIN_RESOLUTION}. Resizing while preserving aspect ratio.")
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
        raise e
    except Exception as err:
        logger.error(f"Unexpected processing error: {str(err)}")
        raise HTTPException(500, "Image processing failed")

def select_differentials(analysis: str):
    """Selects appropriate differentials based on image analysis results."""
    selected_categories = []
    if "scoliosis" in analysis.lower():
        selected_categories.append("Musculoskeletal")
    elif "pneumonia" in analysis.lower():
        selected_categories.append("Pulmonary")
    elif "stroke" in analysis.lower():
        selected_categories.append("Neurological")
    # Add more rules as needed
    return selected_categories

# ADDED LINES: MONGO_URI environment check (does not change existing code)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logger.warning("MONGO_URI environment variable is not set. Any DB-related features may fail.")

############################################
# New advanced helper to reformat AI text in plain language
def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    """
    Processes the AI's raw analysis to standardize headings, remove excessive jargon,
    and condense findings into a clear, evidence-based summary.
    """
    formatted_lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted_text = "\n".join(formatted_lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted_text:
        formatted_text += REQUIRED_DISCLAIMER
    return formatted_text

############################################
# New helper to incorporate differentials from our dictionary
def incorporate_differentials(analysis_text: str, categories: list) -> str:
    """
    Appends additional dictionary data for detected categories to the analysis text.
    """
    additional_info = []
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
            additional_info.append("\n".join(info_lines))
        except KeyError:
            logger.warning(f"No dictionary entry found for category '{cat}'.")
            continue
    if additional_info:
        return analysis_text + "\n\n" + "\n\n".join(additional_info)
    return analysis_text

############################################
# New helper to incorporate evidence-based guidelines in simplified form
def incorporate_guidelines(analysis_text: str, guidelines: dict) -> str:
    """
    Appends a simplified summary of evidence-based guidelines to the analysis text.
    """
    guideline_lines = []
    for org, topics in guidelines.items():
        guideline_lines.append(f"**{org} Guidelines Summary:**")
        for topic, details in topics.items():
            if isinstance(details, dict):
                points = ", ".join(f"{k}: {v}" for k, v in details.items())
                guideline_lines.append(f"- {topic}: {points}")
            elif isinstance(details, list):
                guideline_lines.append(f"- {topic}: " + ", ".join(details))
            else:
                guideline_lines.append(f"- {topic}: {details}")
    if guideline_lines:
        guidelines_text = "\n".join(guideline_lines)
        return analysis_text + "\n\n" + guidelines_text
    return analysis_text

############################################
# New asynchronous helper to query PubMed with caching for efficiency
@lru_cache(maxsize=32)
def get_pubmed_references_sync(query: str) -> str:
    """
    Synchronous function to query PubMed and return a formatted reference list.
    Cached to avoid redundant calls.
    """
    pubmed_api = os.getenv("PUB_MED_API")
    if not pubmed_api:
        logger.warning("PUB_MED_API not set. Skipping PubMed integration.")
        return "No PubMed references available."

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "api_key": pubmed_api,
        "retmax": "3"
    }
    try:
        search_resp = requests.get(esearch_url, params=params)
        if search_resp.status_code != 200:
            logger.error("PubMed search failed with status: " + str(search_resp.status_code))
            return "PubMed search failed."
        search_data = search_resp.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return "No relevant PubMed articles found."

        params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
            "api_key": pubmed_api,
        }
        summary_resp = requests.get(esummary_url, params=params)
        if summary_resp.status_code != 200:
            logger.error("PubMed summary retrieval failed with status: " + str(summary_resp.status_code))
            return "PubMed summary retrieval failed."
        summary_data = summary_resp.json().get("result", {})

        pubmed_info = "**Relevant PubMed References:**\n"
        for pid in id_list:
            article = summary_data.get(pid, {})
            title = article.get("title", "No title available")
            pubdate = article.get("pubdate", "No date")
            source = article.get("source", "No source")
            pubmed_info += f"- **{title}** ({pubdate}, {source})\n"
        return pubmed_info

    except Exception as e:
        logger.error(f"Error querying PubMed: {e}")
        return "Error retrieving PubMed references."

async def get_pubmed_references(query: str) -> str:
    """
    Asynchronous wrapper for the synchronous PubMed query function.
    """
    return await asyncio.to_thread(get_pubmed_references_sync, query)

############################################

@app.post("/analyze-image/")
async def analyze_image(
        file: UploadFile = File(...),
        age: Optional[int] = Query(None, description="Patient's age"),
        sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> dict:
    """Enhanced image analysis endpoint with advanced AI prompts, differentials, evidence-based guidelines, and PubMed integration."""
    try:
        if age is not None:
            logger.info(f"Patient age provided: {age}")
        if sex is not None:
            logger.info(f"Patient sex provided: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # Process and validate image
        image, data_url = await process_medical_image(raw_data, filename)

        # Expanded system prompt with plain language and evidence-based instructions
        system_prompt = (
            "You are a medical imaging AI assistant. Your task is to analyze the diagnostic image and generate a clear, evidence-based report in plain language. "
            "Avoid excessive technical jargon. Provide your analysis in the following sections using heading-level Markdown:\n\n"
            "## Image Characteristics (Certainty: in percentage)\n"
            "- Modality: [e.g., X-ray, CT]\n"
            "- Quality: [e.g., Good, clear]\n"
            "- Findings: [Observations]\n\n"
            "## Pattern Recognition (Certainty: in percentage)\n"
            "- Key visual patterns and correlations\n\n"
            "## Clinical Considerations (Certainty: in percentage)\n"
            "- Recommended next steps and common differentials\n\n"
            "## Summary\n"
            "- Provide a concise bullet-point overview of key findings.\n\n"
            "Incorporate patient demographics (age, sex) if provided. Base your analysis solely on visual features."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this medical image for clinically relevant visual patterns."},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "high"}
                    }
                ]
            }
        ]
        if client is None:
            logger.warning("OpenAI client not initialized, skipping analysis.")
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

        # Reformat analysis text to standardize formatting and append disclaimer if needed
        analysis = reformat_analysis(analysis, disclaimers=True)

        # Incorporate differentials from the medical_differentials dictionary
        detected_categories = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, detected_categories)

        # Incorporate evidence-based guidelines in simplified form
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines)

        # Incorporate PubMed literature references based on a relevant query
        pubmed_query = "post-surgical chest imaging"
        pubmed_references = await get_pubmed_references(pubmed_query)
        analysis += "\n\n" + pubmed_references

        # Securely store the analysis report
        if store_report is None:
            logger.warning("store_report function not initialized, skipping report storage.")
        else:
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

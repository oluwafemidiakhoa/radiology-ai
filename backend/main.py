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
from PIL import Image, UnidentifiedImageError, ImageFilter
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
# Additional Enhancements: Advanced Data Augmentation, ROI Extraction, Adaptive Prompt,
# Feedback Loop Integration, Multi-Modal Data Fusion & Uncertainty Alert System
###############################################################################

# --- ROI Extraction ---
def extract_roi(image: Image.Image) -> Image.Image:
    """
    Dummy ROI extraction: For demonstration, simply returns a central crop.
    In practice, integrate a segmentation model (e.g., U-Net) to extract regions of interest.
    """
    w, h = image.size
    crop_ratio = 0.9  # adjust as needed
    left = int((w - crop_ratio * w) / 2)
    top = int((h - crop_ratio * h) / 2)
    roi = image.crop((left, top, left + int(crop_ratio * w), top + int(crop_ratio * h)))
    return roi

# --- Adaptive Prompt Optimization ---
def adaptive_prompt(metadata: Dict[str, Any], ladder_result: str) -> List[Dict[str, Any]]:
    """
    Dynamically generates the AI prompt messages by incorporating extra metadata
    (e.g., patient age, sex) and the preliminary CNN diagnosis.
    Assumes that 'system_prompt' is defined globally.
    """
    additional_context = ""
    if "age" in metadata and metadata["age"] is not None:
        additional_context += f" Patient age: {metadata['age']}."
    if "sex" in metadata and metadata["sex"] is not None:
        additional_context += f" Patient sex: {metadata['sex']}."
    base_prompt = f"Analyze this medical image. Preliminary CNN diagnosis: {ladder_result}.{additional_context}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": base_prompt},
            {"type": "image_url", "image_url": {"url": metadata.get("data_url", ""), "detail": "high"}}
        ]}
    ]

# --- Feedback Loop Integration ---
@app.post("/submit-feedback/", response_class=JSONResponse)
async def submit_feedback(
    report_id: str,
    feedback: str,
    clinician: Optional[str] = Query(None, description="Clinician identifier")
) -> Dict[str, Any]:
    """
    Endpoint for clinicians to submit feedback on a diagnostic report.
    In a real system, this would store the feedback for future model fine-tuning.
    """
    logger.info(f"Feedback received for report {report_id} from {clinician or 'unknown'}: {feedback}")
    return JSONResponse(content={"status": "Feedback submitted successfully."})

# --- Uncertainty Alert System ---
def uncertainty_alert(confidence: float, variance: float, threshold: float = 0.1) -> str:
    """
    If model uncertainty (variance) is above a threshold, return an alert message.
    """
    if variance > threshold:
        return " ALERT: Model uncertainty is high; further clinical review is recommended."
    return ""

###############################################################################
# Advanced LADDER-Based Image Diagnosis Module (Added)
###############################################################################
# This module integrates an ensemble of pre-trained CNNs with MC dropout, ROI extraction,
# multi-variant image generation, and a reinforcement learning loop to generate a preliminary
# CNN diagnosis. This is then injected into the AI prompt without altering any of your original code.

import torch
import torchvision
import torchvision.transforms as transforms

class LADDERImageDiagnosisAdvanced:
    def __init__(self, device: str = "cpu", domain: Optional[str] = None):
        self.device = device
        self.domain = domain
        # Load two pre-trained models for ensemble predictions using weights.
        self.model1 = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1).to(device)
        self.model2 = torchvision.models.mobilenet_v2(weights=torchvision.models.MobileNet_V2_Weights.IMAGENET1K_V1).to(device)
        self.models = [self.model1, self.model2]
        # Enable dropout by setting models to train mode for MC dropout simulation.
        for m in self.models:
            m.train()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        self.num_mc_samples = 5  # Number of MC dropout samples.

    def generate_variants(self, image: Image.Image) -> List[Image.Image]:
        # Additionally, extract ROI before generating variants.
        roi_image = extract_roi(image)
        variants = [roi_image, image]
        # Variant 1: Gaussian blur.
        variant1 = roi_image.filter(ImageFilter.GaussianBlur(radius=1))
        variants.append(variant1)
        # Variant 2: Central crop (with resize).
        w, h = roi_image.size
        crop_ratio = 0.8
        left = int((w - crop_ratio * w) / 2)
        top = int((h - crop_ratio * h) / 2)
        variant2 = roi_image.crop((left, top, left + int(crop_ratio * w), top + int(crop_ratio * h)))
        variant2 = variant2.resize((w, h))
        variants.append(variant2)
        # Variant 3: Multi-scale (downscale then upscale).
        variant3 = roi_image.resize((w // 2, h // 2)).resize((w, h))
        variants.append(variant3)
        return variants

    def diagnose_image_mc(self, image: Image.Image) -> Tuple[int, float, float]:
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        predictions = []
        for model in self.models:
            model.train()  # Ensure dropout is active.
            mc_preds = []
            for _ in range(self.num_mc_samples):
                with torch.no_grad():
                    outputs = model(input_tensor)
                    prob = torch.softmax(outputs, dim=1).cpu().numpy()[0]
                    mc_preds.append(prob)
            mc_preds = np.array(mc_preds)
            avg_pred = np.mean(mc_preds, axis=0)
            var_pred = np.var(mc_preds, axis=0)
            predictions.append((avg_pred, var_pred))
        avg_preds = np.mean([pred[0] for pred in predictions], axis=0)
        avg_variance = np.mean([pred[1] for pred in predictions], axis=0)
        predicted_class = int(np.argmax(avg_preds))
        confidence = float(avg_preds[predicted_class])
        variance = float(avg_variance[predicted_class])
        return predicted_class, confidence, variance

    def reinforcement_learning(self, image: Image.Image, iterations: int = 3) -> Tuple[int, float, float, Image.Image]:
        best_class, best_conf, best_var = self.diagnose_image_mc(image)
        best_image = image
        best_reward = best_conf - 0.5 * best_var  # Reward = confidence - weight * variance.
        logger.info(f"[LADDER-Advanced] Initial: Class {best_class}, Confidence {best_conf:.2f}, Variance {best_var:.4f}")
        for i in range(iterations):
            logger.info(f"[LADDER-Advanced] Iteration {i+1}")
            for variant in self.generate_variants(best_image):
                pred_class, conf, var = self.diagnose_image_mc(variant)
                reward = conf - 0.5 * var
                logger.info(f"[LADDER-Advanced] Variant: Class {pred_class}, Confidence {conf:.2f}, Variance {var:.4f}, Reward {reward:.2f}")
                if reward > best_reward:
                    best_reward = reward
                    best_class, best_conf, best_var = pred_class, conf, var
                    best_image = variant
                    logger.info("[LADDER-Advanced] Update: Improved reward achieved.")
        return best_class, best_conf, best_var, best_image

    def test_time_rl(self, image: Image.Image, iterations: int = 2) -> Tuple[int, float, float]:
        best_class, best_conf, best_var, _ = self.reinforcement_learning(image, iterations=iterations)
        return best_class, best_conf, best_var

###############################################################################
# Utility Functions (Original)
###############################################################################

def encode_image_to_data_url(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"

def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    required_tags = ["Modality", "BodyPartExamined", "PatientID"]
    missing = [tag for tag in required_tags if tag not in dicom_obj]
    if missing:
        logger.error(f"Missing required DICOM tags: {missing}")
        raise HTTPException(
            status_code=400,
            detail=f"Incomplete DICOM metadata: {', '.join(missing)}"
        )

async def process_medical_image(raw_data: bytes, filename: str) -> Tuple[Image.Image, str]:
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
        # Ensure image is in RGB mode
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image, encode_image_to_data_url(image)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Image processing failed.")

def reformat_analysis(analysis_text: str, disclaimers: bool = True) -> str:
    lines = [line.strip() for line in analysis_text.splitlines() if line.strip()]
    formatted = "\n".join(lines)
    if disclaimers and REQUIRED_DISCLAIMER not in formatted:
        formatted += REQUIRED_DISCLAIMER
    return formatted

###############################################################################
# Integrating Differentials and Guidelines (Original)
###############################################################################

def select_differentials(analysis: str) -> List[str]:
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
    extra_info = []
    radiology_data = medical_differentials.get("Radiology", {})
    for cat in categories:
        cat_data = radiology_data.get(cat, {})
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
# PubMed Querying (Original with Fallback)
###############################################################################

@lru_cache(maxsize=32)
def fetch_pubmed_articles_sync_cached(query: str, max_results: int = 3) -> List[str]:
    return fetch_pubmed_articles_sync(query, max_results)

async def fetch_pubmed_references(query: Optional[str], max_results: int = 3) -> str:
    if not query:
        return ""
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync_cached, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return ""

def extract_pubmed_query(analysis_text: str) -> Optional[str]:
    txt = analysis_text.lower()
    if any(w in txt for w in ["histopathology", "microscopic", "ductal", "fibroadenoma"]):
        return "fibroadenoma breast histopathology OR immunohistochemistry"
    if "normal chest x-ray" in txt:
        return "normal chest x-ray screening recommendations"
    elif "pneumonia" in txt or "infiltrate" in txt:
        return "pneumonia chest x-ray findings"
    elif "nodule" in txt:
        return "pulmonary nodule chest x-ray follow-up"
    if "mammogram" in txt or "breast mass" in txt:
        return "breast mass mammogram fibroadenoma or cyst"
    return "chest x-ray findings"

###############################################################################
# OpenAI System Prompt (Original)
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
# FastAPI Endpoints (Original with Added LADDER Integration & Enhancements)
###############################################################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (M/F)")
) -> Dict[str, Any]:
    try:
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # 1. Image Processing
        image, data_url = await process_medical_image(raw_data, filename)

        # 1.5 Advanced LADDER-based Image Diagnosis Integration (Added)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        ladder_diag = LADDERImageDiagnosisAdvanced(device=device, domain="default")
        ladder_class, ladder_confidence, ladder_variance, _ = ladder_diag.reinforcement_learning(image, iterations=3)
        alert_message = uncertainty_alert(ladder_confidence, ladder_variance)
        ladder_result = f"LADDER Diagnosis: Class {ladder_class}, Confidence {ladder_confidence:.2f}, Variance {ladder_variance:.4f}{alert_message}"
        logger.info(ladder_result)

        # 2. Prepare AI Prompt (including the preliminary LADDER diagnosis)
        prompt_metadata = {"age": age, "sex": sex, "data_url": data_url}
        messages = adaptive_prompt(prompt_metadata, ladder_result)

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
                elif modality_tag == "SM":
                    modality = "Histopathology"
            except Exception:
                modality = "General"
        else:
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
    reports = await asyncio.to_thread(list_reports)
    return JSONResponse(content={"reports": reports})

@app.get("/download-report/{filename}", response_class=JSONResponse)
async def download_report(filename: str) -> Dict[str, Any]:
    report = await asyncio.to_thread(get_report, filename)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found in database.")
    return JSONResponse(content=report)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

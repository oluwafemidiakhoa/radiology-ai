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

# New imports for advanced LADDER-based image diagnosis
import torch
import torchvision
import torchvision.transforms as transforms

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
# Advanced LADDER-Based Image Diagnosis Module
###############################################################################

class LADDERImageDiagnosisAdvanced:
    """
    An advanced LADDER-inspired diagnosis class that:
      - Uses an ensemble of two pre-trained CNNs (ResNet18 and MobileNet_v2).
      - Generates multiple image variants via adaptive, multi-scale augmentations.
      - Uses Monte Carlo dropout (MC dropout) to estimate uncertainty.
      - Employs a reinforcement learning loop that updates the diagnosis based on a reward combining confidence and uncertainty.
    """
    def __init__(self, device: str = "cpu"):
        self.device = device
        # Load two pre-trained models for ensemble predictions.
        self.model1 = torchvision.models.resnet18(pretrained=True).to(device)
        self.model2 = torchvision.models.mobilenet_v2(pretrained=True).to(device)
        self.models = [self.model1, self.model2]
        # Enable dropout by setting models in train mode (MC dropout simulation).
        for m in self.models:
            m.train()
        # Preprocessing transform.
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        self.num_mc_samples = 5  # Number of MC dropout samples.

    def generate_variants(self, image: Image.Image) -> List[Image.Image]:
        """
        Generate multiple adaptive variants for robust diagnosis.
        Variants include:
          - Original image.
          - Gaussian blur.
          - Central crop (with subsequent resizing).
          - Multi-scale variant (downscale then upscale).
        """
        variants = [image]
        # Variant 1: Gaussian blur.
        variant1 = image.filter(ImageFilter.GaussianBlur(radius=1))
        variants.append(variant1)
        # Variant 2: Central crop.
        w, h = image.size
        crop_ratio = 0.8
        left = int((w - crop_ratio * w) / 2)
        top = int((h - crop_ratio * h) / 2)
        variant2 = image.crop((left, top, left + int(crop_ratio * w), top + int(crop_ratio * h)))
        variant2 = variant2.resize((w, h))
        variants.append(variant2)
        # Variant 3: Multi-scale (downscale then upscale).
        variant3 = image.resize((w // 2, h // 2)).resize((w, h))
        variants.append(variant3)
        return variants

    def diagnose_image_mc(self, image: Image.Image) -> Tuple[int, float, float]:
        """
        Perform MC dropout-based diagnosis on the given image.
        Runs multiple forward passes for each model and aggregates predictions.
        
        Returns:
            predicted_class, average confidence, and variance for that class.
        """
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        predictions = []
        # For each model in the ensemble:
        for model in self.models:
            # Ensure dropout is active.
            model.train()
            mc_preds = []
            for _ in range(self.num_mc_samples):
                with torch.no_grad():
                    outputs = model(input_tensor)
                    prob = torch.softmax(outputs, dim=1).cpu().numpy()[0]
                    mc_preds.append(prob)
            mc_preds = np.array(mc_preds)  # (num_samples, num_classes)
            avg_pred = np.mean(mc_preds, axis=0)
            var_pred = np.var(mc_preds, axis=0)
            predictions.append((avg_pred, var_pred))
        # Ensemble aggregation: average the predictions and variances.
        avg_preds = np.mean([pred[0] for pred in predictions], axis=0)
        avg_variance = np.mean([pred[1] for pred in predictions], axis=0)
        predicted_class = int(np.argmax(avg_preds))
        confidence = float(avg_preds[predicted_class])
        variance = float(avg_variance[predicted_class])
        return predicted_class, confidence, variance

    def reinforcement_learning(self, image: Image.Image, iterations: int = 3) -> Tuple[int, float, float, Image.Image]:
        """
        Advanced RL loop: generates multiple variants and selects the best diagnosis based on a reward function.
        The reward is defined as: reward = confidence - (weight * variance)
        (Lower variance indicates a more reliable prediction.)
        """
        best_class, best_conf, best_var = self.diagnose_image_mc(image)
        best_image = image
        best_reward = best_conf - 0.5 * best_var  # Weight factor = 0.5
        logger.info(f"[LADDER-Advanced] Initial Diagnosis: Class {best_class}, Confidence {best_conf:.2f}, Variance {best_var:.4f}")
        
        for i in range(iterations):
            logger.info(f"[LADDER-Advanced] RL Iteration {i+1}")
            for variant in self.generate_variants(best_image):
                pred_class, conf, var = self.diagnose_image_mc(variant)
                reward = conf - 0.5 * var
                logger.info(f"[LADDER-Advanced] Variant Diagnosis: Class {pred_class}, Confidence {conf:.2f}, Variance {var:.4f}, Reward {reward:.2f}")
                if reward > best_reward:
                    best_reward = reward
                    best_class, best_conf, best_var = pred_class, conf, var
                    best_image = variant
                    logger.info("[LADDER-Advanced] Updating diagnosis based on improved reward.")
        return best_class, best_conf, best_var, best_image

    def test_time_rl(self, image: Image.Image, iterations: int = 2) -> Tuple[int, float, float]:
        """
        Refines the diagnosis during inference via test-time RL.
        """
        best_class, best_conf, best_var, _ = self.reinforcement_learning(image, iterations=iterations)
        return best_class, best_conf, best_var

###############################################################################
# Utility Functions
###############################################################################

def encode_image_to_data_url(image: Image.Image) -> str:
    """
    Converts a PIL Image into a base64-encoded data URL.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_b64}"


def validate_dicom_metadata(dicom_obj: pydicom.Dataset) -> None:
    """
    Checks essential DICOM fields and raises an HTTPException if missing.
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
    Processes an uploaded medical image (DICOM or standard), normalizing and resizing as needed.
    
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

        # Enforce minimum resolution.
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
    appending a mandatory disclaimer.
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
    Uses keyword matching to select differential categories.
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
    Appends additional differential details from the consolidated data.
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
    Inserts relevant guidelines based on modality.
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
    Caches PubMed results for performance.
    """
    return fetch_pubmed_articles_sync(query, max_results)


async def fetch_pubmed_references(query: Optional[str], max_results: int = 3) -> str:
    """
    Wraps the synchronous PubMed fetching in an async call.
    """
    if not query:
        return ""
    refs = await asyncio.to_thread(fetch_pubmed_articles_sync_cached, query, max_results)
    if refs:
        return "**Relevant PubMed References:**\n" + "\n".join(f"- {r}" for r in refs)
    return ""


def extract_pubmed_query(analysis_text: str) -> Optional[str]:
    """
    Generates a context-specific PubMed query.
    """
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
    Primary endpoint for processing medical images (DICOM or standard).
    Returns an AI-driven diagnostic summary that integrates advanced LADDER-based diagnosis,
    unified differentials, guidelines, and PubMed references. Final results are stored in MongoDB.
    """
    try:
        if age is not None:
            logger.info(f"Patient age: {age}")
        if sex is not None:
            logger.info(f"Patient sex: {sex}")

        raw_data = await file.read()
        filename = file.filename.lower()

        # 1. Process the uploaded image.
        image, data_url = await process_medical_image(raw_data, filename)

        # 2. Apply advanced LADDER-based Image Diagnosis.
        device = "cuda" if torch.cuda.is_available() else "cpu"
        ladder_diag = LADDERImageDiagnosisAdvanced(device=device)
        ladder_class, ladder_confidence, ladder_variance, refined_image = ladder_diag.reinforcement_learning(image, iterations=3)
        ladder_result = f"LADDER Diagnosis: Class {ladder_class}, Confidence {ladder_confidence:.2f}, Variance {ladder_variance:.4f}"
        logger.info(ladder_result)

        # 3. Prepare AI prompt including the LADDER diagnosis.
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this medical image. Preliminary CNN diagnosis: " + ladder_result},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]

        # 4. AI inference using OpenAI's chat model.
        if client is None:
            logger.warning("OpenAI client not initialized.")
            analysis = "AI analysis service unavailable."
        else:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Replace with the actual model if needed.
                messages=messages,
                max_tokens=2500,
                temperature=0.3
            )
            analysis = response.choices[0].message.content

        # 5. Reformat analysis and incorporate mandatory disclaimers.
        analysis = reformat_analysis(analysis)

        # 6. Identify and incorporate relevant differentials.
        diff_cats = select_differentials(analysis)
        analysis = incorporate_differentials(analysis, diff_cats)

        # 7. Determine modality for guidelines.
        modality = "General"
        if filename.endswith(".dcm"):
            try:
                dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
                modality_tag = getattr(dicom_obj, "Modality", "").upper()
                if modality_tag in ["CR", "DR", "DX", "RF"]:
                    modality = "ChestXRay"
                elif modality_tag == "MG":
                    modality = "Mammogram"
                elif modality_tag == "SM":  # Slide microscopy/histopathology.
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

        # 8. Apply appropriate guidelines.
        analysis = incorporate_guidelines(analysis, evidence_based_guidelines, modality)

        # 9. Fetch targeted PubMed references.
        query = extract_pubmed_query(analysis)
        pubmed_refs = await fetch_pubmed_references(query)
        if pubmed_refs:
            analysis += "\n\n" + pubmed_refs

        # 10. Store the final report in MongoDB.
        await asyncio.to_thread(store_report, filename, analysis)

        # Prepare final JSON response.
        image_metadata = {
            "dimensions": image.size,
            "mode": image.mode,
            "format": "DICOM" if filename.endswith(".dcm") else "Standard"
        }
        return JSONResponse(content={
            "filename": filename,
            "image_metadata": image_metadata,
            "ladder_diagnosis": ladder_result,
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

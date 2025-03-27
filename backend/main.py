"""
Ultra-Advanced Main API for Medical Imaging AI Analysis (Now Aligned with Updated Differentials)

This FastAPI backend processes both DICOM and standard images, orchestrates AI-driven
diagnostic insights, integrates consolidated guidelines (including histopathology),
and stores final reports in MongoDB.

It aligns with the updated `differentials.py` structure, which includes:
  - Radiology Differentials
  - Oncology Differentials
  - Cardiology Differentials
  - Evidence-Based Guidelines
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

# Evidence-based guidelines are nested within `medical_differentials["Guidelines"]`
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
    title="Medical Imaging AI with Updated Differentials",
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
    "\n\n*AI-generated analysis – Must be validated by a board-certified specialist (radiology, cardiology, or oncology)*"
)

###############################################################################
# Additional Enhancements: Advanced Data Augmentation, ROI Extraction, Adaptive Prompt,
# Feedback Loop Integration, Multi-Modal Data Fusion & Uncertainty Alert System
###############################################################################

def extract_roi(image: Image.Image) -> Image.Image:
    """
    Dummy ROI extraction: For demonstration, returns a central crop.
    In practice, integrate a segmentation model (e.g., U-Net) to extract regions of interest.
    """
    w, h = image.size
    crop_ratio = 0.9  # adjust as needed
    left = int((w - crop_ratio * w) / 2)
    top = int((h - crop_ratio * h) / 2)
    roi = image.crop((left, top, left + int(crop_ratio * w), top + int(crop_ratio * h)))
    return roi

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
            {"type": "image_url", "image_url": {"url": metadata.get('data_url', ''), "detail": "high"}}
        ]}
    ]

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

def uncertainty_alert(confidence: float, variance: float, threshold: float = 0.1) -> str:
    """
    If model uncertainty (variance) is above a threshold, return an alert message.
    """
    if variance > threshold:
        return " ALERT: Model uncertainty is high; further clinical review is recommended."
    return ""

###############################################################################
# Advanced LADDER-Based Image Diagnosis Module
###############################################################################

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
        # Reward = confidence - weight * variance
        best_reward = best_conf - 0.5 * best_var
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
# UTILITY FUNCTIONS
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
# INTEGRATING DIFFERENTIALS AND GUIDELINES
###############################################################################

def select_differentials(analysis: str) -> List[str]:
    """
    Example logic to choose relevant specialty categories based on analysis text.
    You can expand or adapt this as needed.
    """
    selected = []
    text = analysis.lower()

    # Radiology sub-check
    if "pacemaker" in text:
        selected.append("Cardiology")
    if "consolidation" in text or "infiltrate" in text:
        selected.append("Pulmonary")
    if "scoliosis" in text:
        selected.append("Musculoskeletal")

    # Oncology sub-check
    if any(word in text for word in ["tumor", "lesion", "nodule", "mass"]):
        selected.append("Oncology")

    return selected

def incorporate_differentials(analysis_text: str, categories: List[str]) -> str:
    """
    Incorporates specialty-specific differentials from the updated `medical_differentials`.
    For example, 'Radiology' or 'Oncology' subcategories from `radiology_differentials`, etc.
    """
    extra_info = []
    # Radiology dictionary
    radiology_data = medical_differentials.get("Radiology", {})
    # Oncology dictionary
    oncology_data = medical_differentials.get("Oncology", {})
    # Cardiology dictionary
    cardiology_data = medical_differentials.get("Cardiology", {})

    # Add relevant info from Radiology if the user selected any radiology-like category
    if any(cat in ["Pulmonary", "Musculoskeletal"] for cat in categories):
        lines = ["**Additional Radiology Differentials:**"]
        for subcat, details in radiology_data.items():
            lines.append(f"- {subcat}: {details}")
        extra_info.append("\n".join(lines))

    # If "Oncology" was detected
    if "Oncology" in categories and oncology_data:
        lines = ["**Additional Oncology Differentials:**"]
        for subcat, details in oncology_data.items():
            lines.append(f"- {subcat}: {details}")
        extra_info.append("\n".join(lines))

    # If "Cardiology" was detected
    if "Cardiology" in categories and cardiology_data:
        lines = ["**Additional Cardiology Differentials:**"]
        for subcat, details in cardiology_data.items():
            lines.append(f"- {subcat}: {details}")
        extra_info.append("\n".join(lines))

    if extra_info:
        return analysis_text + "\n\n" + "\n\n".join(extra_info)
    return analysis_text

def incorporate_guidelines(analysis_text: str, guidelines: Dict[str, Any], modality: str) -> str:
    """
    Incorporates guidelines from `medical_differentials["Guidelines"]` based on the recognized modality.
    For instance, if the DICOM's 'Modality' is 'MG', we might want breast imaging guidelines, etc.
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
# PUBMED QUERYING (with Fallback)
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
    """
    A simple function that attempts to determine a relevant PubMed search query
    based on keywords in the final analysis text.
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
    if any(w in txt for w in ["mammogram", "breast mass"]):
        return "breast mass mammogram fibroadenoma or cyst"
    return "chest x-ray findings"

###############################################################################
# OPENAI SYSTEM PROMPT
###############################################################################

system_prompt = (
    "You are the world's foremost medical imaging AI, combining deep clinical expertise with advanced image analysis. "
    "Your task is to produce an impeccably detailed, precise, and clinically actionable report based solely on the provided image. "
    "Do not output any statements of inability to analyze the image or instruct the user to consult a medical professional. "
    "Your report must be structured into four sections: Image Characteristics, Pattern Recognition, Clinical Considerations, and Summary.\n\n"

    "### Image Characteristics (Certainty in %)\n"
    "• Modality: [Modality] – [Confidence]%\n"
    "  (Example: 'MRI Brain – 95%: T1-weighted sequences in axial, coronal, and sagittal planes')\n"
    "• Quality: [Quality Description] – [Confidence]%\n"
    "  (Example: 'Excellent resolution with clear anatomical delineation and minimal artifacts')\n"
    "• Key Findings: [Key Findings] – [Confidence]%\n"
    "  (Example: 'Large, well-circumscribed extra-axial mass in the frontal region with characteristic signal intensity')\n\n"

    "### Pattern Recognition (Certainty in %)\n"
    "• Primary Patterns: [Primary patterns] – [Confidence]%\n"
    "  (Example: 'Meningioma-like morphology with uniform enhancement and minimal surrounding edema')\n\n"

    "### Clinical Considerations (Certainty in %)\n"
    "• Next Steps: [Next steps] – [Confidence]%\n"
    "  (Example: 'Recommend surgical consultation and further diagnostic workup with contrast-enhanced imaging')\n"
    "• Differentials: [Differentials] – [Confidence]%\n"
    "  (Example: 'Meningioma is highly likely; consider hemangiopericytoma as a less common alternative')\n\n"

    "### Summary\n"
    "Provide a concise, clinically actionable summary synthesizing the key findings and recommendations. "
    "Include patient demographics if available to add context. Do not output any disclaimers or limitations.\n\n"

    "Additional Instructions:\n"
    "1. Under no circumstances should you include phrases like 'unable to provide' or 'consult a medical professional'\n"
    "2. Avoid filler or placeholder text\n"
    "3. Use clear bullet points without trailing punctuation\n"
    "4. Deliver a confident, robust report suitable for expert clinical review"
)


###############################################################################
# FASTAPI ENDPOINTS
###############################################################################

@app.post("/analyze-image/", response_class=JSONResponse)
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (M/F)")
) -> Dict[str, Any]:
    """
    Primary endpoint for analyzing medical images using the advanced LADDER-based approach
    plus GPT-based summarization and differential integration. Now aligned with the updated
    `differentials.py` for Radiology, Oncology, and Cardiology.
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

        # 1.5 Advanced LADDER-based Image Diagnosis
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

        # 4. Reformat Analysis
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
            # Fallback heuristic if not DICOM
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

###############################################################################
# ADVANCED TRANSFORMER-BASED CLASSIFICATION MODULE
###############################################################################
try:
    from transformers import ViTFeatureExtractor, ViTForImageClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("transformers library not found. Transformer-based classification unavailable.")

class TransformerImageDiagnosis:
    """
    An example advanced classification class that uses a vision transformer (ViT).
    Only active if 'transformers' is installed.
    """
    def __init__(self, device: str = "cpu"):
        self.device = device
        if not HAS_TRANSFORMERS:
            self.available = False
            logger.warning("Transformer-based classification not available.")
        else:
            self.available = True
            self.feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224")
            self.model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224").to(self.device)
            self.model.eval()

    def classify_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform classification on the input image using ViT.
        Returns a dictionary with predicted label and confidence.
        """
        if not self.available:
            return {"error": "Transformer-based classification not installed."}

        if image.mode != "RGB":
            image = image.convert("RGB")

        encoding = self.feature_extractor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**{k: v.to(self.device) for k, v in encoding.items()})
            logits = outputs.logits[0].cpu().numpy()

        probs = np.exp(logits) / np.sum(np.exp(logits))
        predicted_idx = int(np.argmax(probs))
        predicted_label = self.model.config.id2label[predicted_idx]
        confidence = float(probs[predicted_idx])
        return {"label": predicted_label, "confidence": confidence}

@app.post("/classify-image-advanced/", response_class=JSONResponse)
async def classify_image_advanced(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Endpoint that demonstrates how to run an advanced Transformer-based classification
    on the uploaded image. This is separate from the main /analyze-image pipeline.
    """
    try:
        raw_data = await file.read()
        filename = file.filename.lower()

        # 1. Process image
        image, _ = await process_medical_image(raw_data, filename)

        # 2. Initialize Transformer classifier if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        transformer_classifier = TransformerImageDiagnosis(device=device)

        # 3. Run classification
        result = transformer_classifier.classify_image(image)
        if "error" in result:
            return JSONResponse(content={"status": "error", "message": result["error"]})

        # 4. Return classification result
        return JSONResponse(content={
            "filename": filename,
            "transformer_classification": result
        })
    except Exception as e:
        logger.error(f"Transformer-based classification failed: {e}")
        raise HTTPException(status_code=500, detail="Classification service unavailable.")

###############################################################################
# NEW: OPEN_CLIP-BASED CLASSIFICATION MODULE (ADDED FOR BIOMEDCLIP-Finetuned)
###############################################################################
try:
    import open_clip
    HAS_OPEN_CLIP = True
except ImportError:
    HAS_OPEN_CLIP = False
    logger.warning("open_clip library not found. open_clip-based classification unavailable.")

class OpenClipViTDiagnosis:
    """
    Demonstrates how to use open_clip to load a BiomedCLIP-Finetuned model
    for classification or embedding tasks. This uses the huggingface hub
    reference: 'hf-hub:mgbam/OpenCLIP-BiomedCLIP-Finetuned'.
    """
    def __init__(self, device: str = "cpu"):
        self.device = device
        if not HAS_OPEN_CLIP:
            self.available = False
            logger.warning("open_clip-based classification not available.")
        else:
            self.available = True
            # Load model & transforms from Hugging Face Hub
            self.model, self.preprocess_train, self.preprocess_val = open_clip.create_model_and_transforms(
                "hf-hub:mgbam/OpenCLIP-BiomedCLIP-Finetuned"
            )
            self.tokenizer = open_clip.get_tokenizer("hf-hub:mgbam/OpenCLIP-BiomedCLIP-Finetuned")
            self.model.to(self.device)
            self.model.eval()

    def classify_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform classification/embedding extraction on the input image using open_clip.
        For actual zero-shot classification, you would compare image embeddings
        to text embeddings for various condition prompts.
        """
        if not self.available:
            return {"error": "open_clip-based classification not installed."}

        img_tensor = self.preprocess_val(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(img_tensor)
            # Example: just return the embedding norm as "confidence."
            norms = image_features.norm(dim=-1).cpu().numpy().tolist()

        return {
            "label": "BiomedCLIP_Embedding",
            "confidence": float(norms[0]),
            "note": (
                "This is a raw embedding norm, not a standard classification. "
                "For actual classification, use text prompts and compute similarities."
            )
        }

@app.post("/classify-image-openclip/", response_class=JSONResponse)
async def classify_image_openclip(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    An endpoint to demonstrate classification or embedding extraction with
    the BiomedCLIP-Finetuned model from open_clip on Hugging Face Hub.
    """
    try:
        raw_data = await file.read()
        filename = file.filename.lower()

        # 1. Process image
        image, _ = await process_medical_image(raw_data, filename)

        # 2. Initialize open_clip-based classifier
        device = "cuda" if torch.cuda.is_available() else "cpu"
        openclip_classifier = OpenClipViTDiagnosis(device=device)

        # 3. Run classification/embedding
        result = openclip_classifier.classify_image(image)
        if "error" in result:
            return JSONResponse(content={"status": "error", "message": result["error"]})

        # 4. Return classification result
        return JSONResponse(content={
            "filename": filename,
            "openclip_classification": result
        })
    except Exception as e:
        logger.error(f"open_clip-based classification failed: {e}")
        raise HTTPException(status_code=500, detail="open_clip classification service unavailable.")

###############################################################################
# MAIN SERVER LAUNCH
###############################################################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

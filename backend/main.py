import os
import io
import base64
import logging
import numpy as np
import pydicom
import re
from typing import Tuple, Optional, Dict, List
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydicom.pixel_data_handlers import apply_modality_lut, apply_voi_lut

# Enhanced medical knowledge integration
from differentials import medical_differentials, evidence_based_guidelines

# Advanced analytics module
try:
    from analytics import ImagingAnalytics
    analytics = ImagingAnalytics()
except ImportError:
    analytics = None

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("medical_imaging.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AdvancedMedicalImagingAI")

# Advanced DICOM configuration
DICOM_CONFIG = {
    "modality_settings": {
        "CT": {
            "window_presets": {
                "lung": {"center": -600, "width": 1500},
                "mediastinum": {"center": 40, "width": 400}
            },
            "rescale": {"slope": 1, "intercept": -1024}
        },
        "MR": {
            "window_presets": {
                "brain": {"center": 0, "width": 500}
            }
        }
    },
    "min_resolution": 512,
    "max_file_size": 1024 * 1024 * 100  # 100MB
}

class AdvancedDICOMProcessor:
    """Advanced DICOM processing with modality-specific optimizations"""
    
    def __init__(self, dicom_obj: pydicom.Dataset):
        self.dicom = dicom_obj
        self.modality = dicom_obj.Modality
        self.anatomical_region = getattr(dicom_obj, 'BodyPartExamined', 'Unknown')
        
    def apply_advanced_processing(self) -> np.ndarray:
        """Perform modality-specific image optimization"""
        try:
            pixel_array = apply_modality_lut(self.dicom.pixel_array, self.dicom)
            pixel_array = apply_voi_lut(pixel_array, self.dicom)
            
            if self.modality in DICOM_CONFIG["modality_settings"]:
                settings = DICOM_CONFIG["modality_settings"][self.modality]
                if "rescale" in settings:
                    pixel_array = (
                        pixel_array * settings["rescale"]["slope"] 
                        + settings["rescale"]["intercept"]
                    )
                
                # Apply optimal windowing
                window_preset = self._get_optimal_window()
                pixel_array = self._apply_window(pixel_array, window_preset)
            
            return pixel_array
        except Exception as e:
            logger.error(f"DICOM processing failed: {str(e)}")
            raise HTTPException(500, "Advanced DICOM processing error")

    def _get_optimal_window(self) -> Dict[str, int]:
        """Select optimal window settings based on anatomical region"""
        presets = DICOM_CONFIG["modality_settings"][self.modality]["window_presets"]
        return presets.get(self.anatomical_region.lower(), presets["default"])

    def _apply_window(self, pixel_array: np.ndarray, window: Dict) -> np.ndarray:
        """Apply window-level transformation"""
        center = window["center"]
        width = window["width"]
        lower = center - width/2
        upper = center + width/2
        return np.clip((pixel_array - lower) * (255/(upper-lower)), 0, 255).astype(np.uint8)

class AIDiagnosticEngine:
    """Advanced AI diagnostic engine with clinical context integration"""
    
    def __init__(self, clinical_context: Dict):
        self.context = clinical_context
        self.certainty_scores = {}
        self.evidence_recommendations = []
        
    async def generate_analysis(self, image_data: str) -> str:
        """Generate enhanced diagnostic report"""
        system_prompt = self._create_system_prompt()
        messages = self._create_message_payload(system_prompt, image_data)
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4-medical",
                messages=messages,
                max_tokens=2500,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return self._process_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            raise HTTPException(500, "Advanced AI analysis unavailable")

    def _create_system_prompt(self) -> str:
        """Generate context-aware system prompt"""
        prompt = f"""You are an expert medical imaging AI analyzing this study considering:
- Patient age: {self.context.get('age', 'N/A')}
- Patient sex: {self.context.get('sex', 'N/A')}
- Clinical history: {self.context.get('history', 'N/A')}

Generate report with:
1. Quantitative measurements
2. Probabilistic assessments
3. Differential diagnosis matrix
4. Evidence-based recommendations

JSON format:"""
        return prompt

    def _process_response(self, response: str) -> str:
        """Process and validate AI response"""
        try:
            report_data = json.loads(response)
            self._validate_report(report_data)
            return self._format_report(report_data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from AI")
            raise HTTPException(500, "Analysis formatting error")

    def _validate_report(self, report: Dict):
        """Validate report structure and content"""
        required_sections = [
            "image_characteristics", 
            "pattern_recognition",
            "clinical_considerations"
        ]
        for section in required_sections:
            if section not in report:
                raise ValueError(f"Missing section: {section}")

    def _format_report(self, report: Dict) -> str:
        """Convert structured data to formatted report"""
        formatted = []
        formatted.append(f"## AI Diagnostic Report\n")
        
        # Process each section with certainty scoring
        for section in ["image_characteristics", "pattern_recognition", "clinical_considerations"]:
            content = report[section]
            formatted.append(f"### {content['title']} (Certainty: {content['certainty']}%)\n")
            formatted.extend(content["findings"])
            
            if section == "clinical_considerations":
                formatted.append("\n**Evidence-Based Recommendations:**")
                formatted.extend(content["recommendations"])
                
        return "\n".join(formatted)

def redact_phi(text: str) -> str:
    """Redact protected health information from text"""
    phi_patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{5}\b",  # Zip codes
        r"\b[A-Za-z]{2}\d{5}\b"  # Medical record numbers
    ]
    for pattern in phi_patterns:
        text = re.sub(pattern, "[REDACTED]", text)
    return text

@app.post("/analyze-image/")
async def analyze_image(
    file: UploadFile = File(...),
    age: Optional[int] = Query(None, description="Patient's age"),
    sex: Optional[str] = Query(None, description="Patient's sex (Male/Female)")
) -> dict:
    """Enhanced image analysis endpoint with advanced processing"""
    try:
        # Validate input size
        if file.size > DICOM_CONFIG["max_file_size"]:
            raise HTTPException(413, "File size exceeds maximum limit")

        raw_data = await file.read()
        filename = file.filename.lower()
        
        # Process image with advanced pipeline
        if filename.endswith(".dcm"):
            dicom_obj = pydicom.dcmread(io.BytesIO(raw_data))
            processor = AdvancedDICOMProcessor(dicom_obj)
            pixel_array = processor.apply_advanced_processing()
            image = Image.fromarray(pixel_array)
        else:
            image = Image.open(io.BytesIO(raw_data))
            if image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")

        # Generate analysis
        clinical_context = {"age": age, "sex": sex}
        diagnostic_engine = AIDiagnosticEngine(clinical_context)
        data_url = encode_image_to_data_url(image)
        analysis = await diagnostic_engine.generate_analysis(data_url)
        
        # Apply PHI redaction
        analysis = redact_phi(analysis)

        # Log analytics
        if analytics:
            analytics.log_study({
                "modality": processor.modality if filename.endswith(".dcm") else "Standard",
                "findings": diagnostic_engine.certainty_scores,
                "recommendations": diagnostic_engine.evidence_recommendations
            })

        return JSONResponse(content={
            "filename": filename,
            "analysis": analysis,
            "certainty_scores": diagnostic_engine.certainty_scores,
            "evidence_recommendations": diagnostic_engine.evidence_recommendations
        })

    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Analysis pipeline failed: {str(err)}")
        raise HTTPException(500, "Advanced analysis service unavailable")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        ssl_keyfile=os.getenv("SSL_KEY"),
        ssl_certfile=os.getenv("SSL_CERT")
    )

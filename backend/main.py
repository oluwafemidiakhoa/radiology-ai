# main.py
import os
import io
import base64
import logging
import requests  # Now properly installed
import numpy as np
import pydicom
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseSettings
from openai import AsyncOpenAI

# Configuration
class MedicalConfig(BaseSettings):
    PUB_MED_API: str = "oluwafemidiakhoa@gmail.com"
    OPENAI_API_KEY: str
    MIN_RESOLUTION: int = 1024
    
    class Config:
        env_file = ".env"

try:
    config = MedicalConfig()
except Exception as e:
    logging.critical(f"Config error: {str(e)}")
    exit()

# Initialize components
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

# PubMed Service
class PubMedService:
    def __init__(self):
        self.base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
    def get_evidence(self, diagnosis: str) -> List[Dict]:
        try:
            params = {
                "db": "pubmed",
                "term": f"{diagnosis}[Title/Abstract]",
                "retmax": 5,
                "email": config.PUB_MED_API
            }
            response = requests.get(f"{self.base}esearch.fcgi", params=params)
            return response.json().get('esearchresult', {}).get('idlist', [])
        except Exception as e:
            logging.error(f"PubMed failed: {str(e)}")
            return []

# Core Image Processing
async def process_image(file: UploadFile) -> Tuple[Image.Image, str]:
    try:
        data = await file.read()
        if file.filename.lower().endswith(".dcm"):
            ds = pydicom.dcmread(io.BytesIO(data))
            img = Image.fromarray(ds.pixel_array)
        else:
            img = Image.open(io.BytesIO(data))
            
        if min(img.size) < config.MIN_RESOLUTION:
            img = img.resize((config.MIN_RESOLUTION, config.MIN_RESOLUTION))
            
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=100)
        return img, base64.b64encode(buffered.getvalue()).decode()
    
    except Exception as e:
        logging.error(f"Image error: {str(e)}")
        raise HTTPException(400, "Image processing failed")

@app.post("/analyze")
async def analyze_image(file: UploadFile):
    try:
        # Process image
        img, b64 = await process_image(file)
        
        # Get AI analysis
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                }]
            }]
        )
        
        # Get evidence
        diagnosis = "pneumonia"  # Simplified example
        evidence = PubMedService().get_evidence(diagnosis)
        
        return JSONResponse({
            "analysis": response.choices[0].message.content,
            "evidence": evidence,
            "resolution": img.size
        })
        
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        raise HTTPException(500, "Full analysis failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8042)

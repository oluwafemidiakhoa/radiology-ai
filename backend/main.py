from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
from PIL import Image
import io
import base64
from models import store_report
from config import OPENAI_API_KEY

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="Radiology AI Backend")

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read the uploaded file and load it as an image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Convert RGBA images to RGB (Fixes transparency issue)
    if image.mode in ["RGBA", "P"]:
        image = image.convert("RGB")

    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_bytes = base64.b64encode(buffered.getvalue()).decode()

    # ✅ Correct OpenAI API request format
    messages = [
        {"role": "system", "content": "You are a radiologist analyzing medical images."},
        {"role": "user", "content": [
            {"type": "text", "text": "Analyze this X-ray/CT scan/MRI for abnormalities."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_bytes}"}}
        ]}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=500
        )
        report = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # Store report in the database
    store_report(file.filename, report)

    return {"filename": file.filename, "AI_Analysis": report}

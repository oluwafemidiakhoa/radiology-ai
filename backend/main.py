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
    allow_origins=["*"],  # Change this to frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Radiology AI Backend is Running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read and process the uploaded image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA/P images to RGB
        if image.mode in ["RGBA", "P"]:
            image = image.convert("RGB")

        # Convert image to Base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = base64.b64encode(buffered.getvalue()).decode()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # Construct OpenAI API request
    messages = [
        {"role": "system", "content": "You are a radiologist analyzing medical images."},
        {"role": "user", "content": [
            {"type": "text", "text": "Analyze this X-ray/CT scan/MRI for abnormalities."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_bytes}"}}
        ]}
    ]

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=500
        )
        report = response.choices[0].message.content

    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    # Store report in database
    store_report(file.filename, report)

    return {"filename": file.filename, "AI_Analysis": report}

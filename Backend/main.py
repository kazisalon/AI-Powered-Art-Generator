from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from typing import Optional
import base64
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArtRequest(BaseModel):
    prompt: str
    style: str
    width: Optional[int] = 512
    height: Optional[int] = 512

class ArtResponse(BaseModel):
    image: str

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}

@app.post("/api/generate")
async def generate_art(request: ArtRequest):
    try:
        style_prompts = {
            "realistic": "highly detailed, photorealistic, 8k",
            "abstract": "abstract art style, bold colors, geometric shapes",
            "impressionist": "impressionist painting style, loose brushstrokes",
            "pixel": "pixel art style, 16-bit, retro gaming"
        }
        
        enhanced_prompt = f"{request.prompt}, {style_prompts.get(request.style, '')}"
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": enhanced_prompt}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        base64_image = base64.b64encode(response.content).decode()
        return ArtResponse(image=base64_image)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Art Generator API"}
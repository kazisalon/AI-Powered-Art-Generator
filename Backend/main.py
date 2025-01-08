from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
import os
import base64
from dotenv import load_dotenv
import logging
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Art Generator API",
    description="An API for generating AI art using Stable Diffusion",
    version="1.0.0"
)

# Check if token exists
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
if not HUGGINGFACE_TOKEN:
    logger.error("HUGGINGFACE_TOKEN not found in environment variables!")

# CORS middleware
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

    @validator('prompt')
    def validate_prompt_length(cls, v):
        if len(v) > 500:
            raise ValueError('Prompt must be less than 500 characters')
        return v

    @validator('width', 'height')
    def validate_dimensions(cls, v):
        if v is not None and (v < 128 or v > 1024):
            raise ValueError('Dimensions must be between 128 and 1024 pixels')
        return v

    @validator('style')
    def validate_style(cls, v):
        valid_styles = {'realistic', 'abstract', 'impressionist', 'pixel'}
        if v not in valid_styles:
            raise ValueError(f'Style must be one of: {", ".join(valid_styles)}')
        return v

class ArtResponse(BaseModel):
    image: str
    metadata: Optional[Dict[str, Any]]

# API URLs for different models
API_URLS = {
    "sd-v1-4": "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
    "sd-v1-5": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
    "sd-xl": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
    "openjourney": "https://api-inference.huggingface.co/models/prompthero/openjourney"
}

# Try using openjourney model as default
API_URL = API_URLS["openjourney"]

headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

# Style prompt enhancements
STYLE_PROMPTS = {
    "realistic": "highly detailed, photorealistic, 8k, ultra HD, professional photography, masterpiece",
    "abstract": "abstract art style, bold colors, geometric shapes, modern art, experimental, masterpiece",
    "impressionist": "impressionist painting style, loose brushstrokes, vibrant colors, light effects, masterpiece",
    "pixel": "pixel art style, 16-bit, retro gaming, nostalgic, crisp pixels, masterpiece"
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_huggingface_api(url: str, headers: dict, payload: dict):
    """
    Call Hugging Face API with retry logic using aiohttp
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                raise Exception(f"API call failed with status {response.status}")
            return await response.read()

@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "name": "AI Art Generator API",
        "version": "1.0.0",
        "description": "Generate AI art using Stable Diffusion",
        "endpoints": {
            "/api/generate": "POST - Generate AI art",
            "/health": "GET - Health check",
            "/styles": "GET - List available styles"
        }
    }

@app.get("/styles")
async def get_styles():
    """Get available art styles and their descriptions"""
    return {
        style: {
            "description": prompt,
            "example_prompt": f"A sunset landscape, {prompt}"
        }
        for style, prompt in STYLE_PROMPTS.items()
    }

@app.post("/api/generate")
async def generate_art(request: ArtRequest):
    """Generate AI art based on prompt and style"""
    try:
        logger.info(f"Received request with prompt: {request.prompt}, style: {request.style}")
        
        if not HUGGINGFACE_TOKEN:
            raise HTTPException(status_code=500, detail="API token not configured")

        # Enhance prompt with style
        enhanced_prompt = f"{request.prompt}, {STYLE_PROMPTS[request.style]}"
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        
        # Prepare request payload
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "width": request.width,
                "height": request.height
            }
        }

        try:
            content = await call_huggingface_api(API_URL, headers, payload)
            logger.info("Successfully received response from Hugging Face API")
        except Exception as e:
            logger.error(f"API call failed after retries: {str(e)}")
            # Try fallback model if first attempt fails
            try:
                logger.info("Attempting fallback to SD-v1-4 model")
                content = await call_huggingface_api(API_URLS["sd-v1-4"], headers, payload)
                logger.info("Successfully received response from fallback model")
            except Exception as e2:
                logger.error(f"Fallback API call failed: {str(e2)}")
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable. Please try again later."
                )

        # Encode image and prepare metadata
        try:
            base64_image = base64.b64encode(content).decode()
            metadata = {
                "prompt": request.prompt,
                "style": request.style,
                "dimensions": f"{request.width}x{request.height}",
                "model": "openjourney"
            }
            return ArtResponse(image=base64_image, metadata=metadata)
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing the generated image"
            )

    except Exception as e:
        logger.error(f"Error in generate_art: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check API health status"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, headers=headers, timeout=5) as response:
                api_status = response.status == 200
    except:
        api_status = False

    return {
        "status": "healthy",
        "token_configured": bool(HUGGINGFACE_TOKEN),
        "huggingface_api_status": api_status,
        "available_styles": list(STYLE_PROMPTS.keys()),
        "current_model": "openjourney",
        "fallback_model": "stable-diffusion-v1-4"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
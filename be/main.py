import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import image_generation, streaming

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="LinkedIn Ads Image Generation Studio",
    description="AI-powered image generation for LinkedIn advertisements",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_generation.router, prefix="/api/v1")
app.include_router(streaming.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "LinkedIn Ads Image Generation Studio API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

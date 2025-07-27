from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class ImageGenerationRequest(BaseModel):
    company_url: HttpUrl
    product_name: str
    business_value: str
    audience: str
    body_text: str
    footer_text: str


class ImageModificationRequest(BaseModel):
    original_image_url: str
    modification_prompt: str


class ImageStyle(str, Enum):
    PROFESSIONAL = "professional"
    MODERN = "modern"
    CREATIVE = "creative"
    MINIMALIST = "minimalist"
    BOLD = "bold"


class GeneratedImage(BaseModel):
    id: str
    url: str
    style: ImageStyle
    prompt_used: str
    generation_timestamp: str
    request_id: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    request_id: str
    images: List[GeneratedImage]
    status: str
    message: Optional[str] = None


class ImageModificationResponse(BaseModel):
    image: GeneratedImage
    status: str
    message: Optional[str] = None


class AdCopy(BaseModel):
    headline: str
    description: str
    cta: str


class EnhancedImageGenerationResponse(BaseModel):
    request_id: str
    images: List[GeneratedImage]
    enhanced_prompts: Optional[List[str]] = None
    ad_copy: Optional[AdCopy] = None
    status: str
    message: Optional[str] = None

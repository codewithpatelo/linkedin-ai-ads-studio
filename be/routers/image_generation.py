import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models import (
    GeneratedImage,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageModificationRequest,
    ImageModificationResponse,
    ImageStyle,
)
from services.image_service import image_service

router = APIRouter(prefix="/images", tags=["Image Generation"])

# In-memory storage for generated images (in production, use a database)
generated_images_store: Dict[str, dict] = {}


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_images(request: ImageGenerationRequest):
    """
    Generate 5 different LinkedIn ad images based on company information
    """
    try:
        request_id = str(uuid.uuid4())

        # Generate images using the service
        images = await image_service.generate_images(request)

        if not images:
            raise HTTPException(status_code=500, detail="Failed to generate any images")

        # Store images for future reference
        generated_images_store[request_id] = {
            "images": [img.dict() for img in images],
            "original_request": request.dict(),
        }

        return ImageGenerationResponse(
            request_id=request_id,
            images=images,
            status="success",
            message=f"Successfully generated {len(images)} images",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Image generation failed: {str(e)}"
        )


@router.post("/generate/stream")
async def generate_images_stream(request: ImageGenerationRequest):
    """
    Generate images with real-time streaming progress updates
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            request_id = str(uuid.uuid4())

            # Send initial event
            yield f"data: {json.dumps({'type': 'started', 'message': 'Starting image generation...', 'request_id': request_id})}\n\n"

            # Create a callback that yields events
            async def progress_callback(event_data):
                nonlocal event_stream
                # We can't yield from inside the callback, so we'll store events
                # and let the main loop handle them
                pass

            # Generate images with progress updates
            images = await image_service.generate_images_with_progress(request)

            if images:
                # Store images for future reference
                generated_images_store[request_id] = {
                    "images": [img.dict() for img in images],
                    "original_request": request.dict(),
                }

                # Send completion event
                yield f"data: {json.dumps({'type': 'completed', 'request_id': request_id, 'images': [img.dict() for img in images], 'message': f'Successfully generated {len(images)} images'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to generate any images'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Image generation failed: {str(e)}'})}\n\n"

        # Send end event
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@router.post("/modify", response_model=ImageModificationResponse)
async def modify_image(request: ImageModificationRequest):
    """
    Modify an existing image based on user feedback
    """
    try:
        # Generate modified image using the service
        modified_image = await image_service.modify_image(request)

        return ImageModificationResponse(
            image=modified_image,
            status="success",
            message="Image successfully modified",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Image modification failed: {str(e)}"
        )


@router.get("/request/{request_id}")
async def get_generated_images(request_id: str):
    """
    Retrieve generated images by request ID
    """
    if request_id not in generated_images_store:
        raise HTTPException(status_code=404, detail="Request not found")

    return generated_images_store[request_id]


@router.get("/styles")
async def get_available_styles():
    """
    Get list of available image styles
    """
    from models import ImageStyle

    return {
        "styles": [style.value for style in ImageStyle],
        "descriptions": {
            "professional": "Clean, corporate, and trustworthy design",
            "modern": "Contemporary, sleek, and minimalist",
            "creative": "Artistic, unique, and eye-catching",
            "minimalist": "Simple, clean, and focused",
            "bold": "Strong, vibrant, and attention-grabbing",
        },
    }


@router.delete("/request/{request_id}")
async def delete_generated_images(request_id: str):
    """
    Delete stored images for a request
    """
    if request_id not in generated_images_store:
        raise HTTPException(status_code=404, detail="Request not found")

    del generated_images_store[request_id]
    return {"message": "Images deleted successfully"}

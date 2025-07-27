import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models import ImageGenerationRequest
from services.image_service import image_service

router = APIRouter(prefix="/stream", tags=["Streaming"])


@router.post("/generate")
async def generate_images_stream(request: ImageGenerationRequest):
    """
    Generate images with real-time streaming progress updates
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            request_id = str(uuid.uuid4())

            # Send initial event
            yield f"data: {json.dumps({'type': 'started', 'message': 'Starting image generation...', 'request_id': request_id})}\n\n"

            # Send company analysis step
            yield f"data: {json.dumps({'type': 'progress', 'step': 'company_analysis', 'message': 'Analyzing company information...'})}\n\n"
            await asyncio.sleep(1)  # Small delay for UX

            # Send reference loading step
            yield f"data: {json.dumps({'type': 'progress', 'step': 'loading_references', 'message': 'Loading reference ad examples...'})}\n\n"
            await asyncio.sleep(0.5)

            # Send prompt enhancement step
            yield f"data: {json.dumps({'type': 'progress', 'step': 'prompt_enhancement', 'message': 'Enhancing prompts with GPT-4o...'})}\n\n"
            await asyncio.sleep(1)

            # Send copy generation step
            yield f"data: {json.dumps({'type': 'progress', 'step': 'copy_generation', 'message': 'Generating compelling ad copy...'})}\n\n"
            await asyncio.sleep(1)

            # Send image generation start
            yield f"data: {json.dumps({'type': 'progress', 'step': 'image_generation', 'message': 'Generating images with DALL-E 3...'})}\n\n"

            # Generate images using the workflow (this will take time due to rate limits)
            workflow_result = await image_service.generate_images_with_workflow(request)

            if workflow_result and workflow_result.get("images"):
                # Send enhanced prompts if available
                if workflow_result.get("enhanced_prompts"):
                    yield f"data: {json.dumps({'type': 'prompts_ready', 'prompts': workflow_result['enhanced_prompts'], 'message': 'Enhanced prompts generated'})}\n\n"
                    await asyncio.sleep(0.5)

                # Send ad copy if available
                if workflow_result.get("ad_copy"):
                    yield f"data: {json.dumps({'type': 'copy_ready', 'ad_copy': workflow_result['ad_copy'], 'message': 'Ad copy generated'})}\n\n"
                    await asyncio.sleep(0.5)

                # Send completion event with images
                completion_data = {
                    "type": "completed",
                    "request_id": request_id,
                    "images": [img.dict() for img in workflow_result["images"]],
                    "enhanced_prompts": workflow_result.get("enhanced_prompts"),
                    "ad_copy": workflow_result.get("ad_copy"),
                    "message": f'Successfully generated {len(workflow_result["images"])} images',
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
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

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

            # Step 1: Company Analysis
            yield f"data: {json.dumps({'type': 'progress', 'step': 'company_analysis', 'message': 'Analyzing company information...'})}\n\n"
            
            # Step 2: Load Reference Images
            yield f"data: {json.dumps({'type': 'progress', 'step': 'loading_references', 'message': 'Loading reference ad examples...'})}\n\n"
            
            # Step 3: Generate Enhanced Prompts
            yield f"data: {json.dumps({'type': 'progress', 'step': 'prompt_enhancement', 'message': 'Enhancing prompts with GPT-4o...'})}\n\n"
            
            # Step 4: Generate Ad Copy
            yield f"data: {json.dumps({'type': 'progress', 'step': 'copy_generation', 'message': 'Generating compelling ad copy...'})}\n\n"
            
            # Step 5: Generate Images
            yield f"data: {json.dumps({'type': 'progress', 'step': 'image_generation', 'message': 'Generating images with DALL-E 3...'})}\n\n"

            # Generate images using the workflow with detailed progress
            workflow_result = await image_service.generate_images_with_workflow(request)

            if workflow_result and workflow_result.get("images"):
                # Send step completion with results
                yield f"data: {json.dumps({'type': 'step_completed', 'step': 'company_analysis', 'message': '✅ Company analysis completed'})}\n\n"
                
                yield f"data: {json.dumps({'type': 'step_completed', 'step': 'loading_references', 'message': '✅ Reference images loaded'})}\n\n"
                
                # Send enhanced prompts with detailed console output
                if workflow_result.get("enhanced_prompts"):
                    prompts_preview = "\n".join([f"Style {i+1}: {prompt[:100]}..." for i, prompt in enumerate(workflow_result['enhanced_prompts'])])
                    newline = "\n"
                    message = f'✅ Enhanced prompts generated:{newline}{prompts_preview}'
                    yield f"data: {json.dumps({'type': 'step_completed', 'step': 'prompt_enhancement', 'message': message})}\n\n"
                    yield f"data: {json.dumps({'type': 'prompts_ready', 'prompts': workflow_result['enhanced_prompts'], 'message': 'Enhanced prompts available'})}\n\n"

                # Send ad copy with detailed console output
                if workflow_result.get("ad_copy"):
                    ad_copy = workflow_result['ad_copy']
                    newline = "\n"
                    copy_preview = f"Headline: {ad_copy.get('headline', 'N/A')}{newline}Description: {ad_copy.get('description', 'N/A')[:80]}...{newline}CTA: {ad_copy.get('cta', 'N/A')}"
                    message = f'✅ Ad copy generated:{newline}{copy_preview}'
                    yield f"data: {json.dumps({'type': 'step_completed', 'step': 'copy_generation', 'message': message})}\n\n"
                    yield f"data: {json.dumps({'type': 'copy_ready', 'ad_copy': workflow_result['ad_copy'], 'message': 'Ad copy available'})}\n\n"

                # Send image generation progress
                image_count = len(workflow_result["images"])
                yield f"data: {json.dumps({'type': 'step_completed', 'step': 'image_generation', 'message': f'✅ Generated {image_count} images successfully'})}\n\n"

                # Send completion event with all data
                completion_data = {
                    "type": "completed",
                    "request_id": request_id,
                    "images": [img.dict() for img in workflow_result["images"]],
                    "enhanced_prompts": workflow_result.get("enhanced_prompts"),
                    "ad_copy": workflow_result.get("ad_copy"),
                    "message": f'🎉 Generation complete! {image_count} LinkedIn ads ready',
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': '❌ Failed to generate any images'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ Image generation failed: {str(e)}'})}\n\n"

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

import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import ImageGenerationRequest
from services.image_service import ImageGenerationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["streaming"])

# Create service instance
image_service = ImageGenerationService()


class StreamingRequest(BaseModel):
    """Request model for streaming image generation."""

    company_url: str
    product_name: str
    business_value: str
    audience: str
    body_text: str = ""
    footer_text: str = ""


@router.post("/generate")
async def stream_generate_images(request: StreamingRequest):
    """Generate images with streaming progress updates."""
    print(f"🚀 Starting streaming generation for: {request.product_name}")

    try:
        # Create a custom streaming class to handle real-time events
        class RealTimeStreamer:
            def __init__(self):
                self.queue = asyncio.Queue()
                self.finished = False
                
            async def callback(self, event_data):
                print(f"📡 Streaming event: {event_data.get('type')} - {event_data.get('message', '')}")
                await self.queue.put(event_data)
                
            async def finish(self):
                self.finished = True
                await self.queue.put(None)  # Sentinel value
        
        streamer = RealTimeStreamer()
        
        async def generate_stream() -> AsyncGenerator[str, None]:
            try:
                # Convert to ImageGenerationRequest
                image_request = ImageGenerationRequest(
                    company_url=request.company_url,
                    product_name=request.product_name,
                    business_value=request.business_value,
                    audience=request.audience,
                    body_text=request.body_text,
                    footer_text=request.footer_text,
                )
                
                # Send initial step started event
                yield f"data: {json.dumps({'type': 'step_started', 'step': 'company_analysis', 'message': '🔍 Starting company analysis...'})}\n\n"
                
                # Start the workflow in background
                async def run_workflow():
                    try:
                        result = await image_service.generate_images_with_progress(
                            image_request, 
                            event_stream_callback=streamer.callback
                        )
                        await streamer.finish()
                        return result
                    except Exception as e:
                        await streamer.queue.put({'type': 'error', 'message': str(e)})
                        await streamer.finish()
                        return None
                
                # Start workflow task
                workflow_task = asyncio.create_task(run_workflow())
                
                # Stream events as they arrive
                result = None
                while True:
                    event_data = await streamer.queue.get()
                    
                    if event_data is None:  # Sentinel - workflow finished
                        result = await workflow_task
                        break
                    
                    # Stream the event immediately
                    yield f"data: {json.dumps(event_data)}\n\n"

                # Send final completion event
                if result and len(result) > 0:
                    request_id = str(uuid.uuid4())
                    image_service.image_storage[request_id] = result
                    for image in result:
                        image.request_id = request_id

                    yield f"data: {json.dumps({'type': 'generation_complete', 'images': [{'id': img.id, 'url': img.url, 'style': img.style.value, 'prompt_used': img.prompt_used} for img in result], 'request_id': request_id, 'message': '✅ All images generated successfully!'})}\n\n"
                else:
                    raise Exception("No images were generated")

                # Send final done event
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as e:
                logger.error(f"Error in streaming generation: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'Generation failed: {str(e)}'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )

    except Exception as e:
        logger.error(f"Error setting up streaming: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming setup failed: {str(e)}")

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

            # Execute workflow steps individually with real-time streaming
            from services.image_service import WorkflowState
            import uuid
            
            try:
                # Create initial state
                initial_state = WorkflowState(request=request)
                current_state = initial_state
                
                # Step 1: Company Analysis
                current_state = await image_service._analyze_company(current_state)
                if current_state.error:
                    raise Exception(f"Company analysis failed: {current_state.error}")
                yield f"data: {json.dumps({'type': 'step_completed', 'step': 'company_analysis', 'message': '✅ Company analysis completed'})}

"
                
                # Step 2: Load Reference Images
                current_state = await image_service._load_reference_images(current_state)
                if current_state.error:
                    raise Exception(f"Reference loading failed: {current_state.error}")
                yield f"data: {json.dumps({'type': 'step_completed', 'step': 'loading_references', 'message': '✅ Reference images loaded'})}

"
                
                # Step 3: Generate Enhanced Prompts
                current_state = await image_service._generate_enhanced_prompts(current_state)
                if current_state.error:
                    raise Exception(f"Prompt enhancement failed: {current_state.error}")
                
                # Send enhanced prompts with detailed console output
                if current_state.enhanced_prompts:
                    prompts_preview = "\n".join([f"Style {i+1}: {prompt[:100]}..." for i, prompt in enumerate(current_state.enhanced_prompts)])
                    newline = "\n"
                    message = f'✅ Enhanced prompts generated:{newline}{prompts_preview}'
                    yield f"data: {json.dumps({'type': 'step_completed', 'step': 'prompt_enhancement', 'message': message})}

"
                    yield f"data: {json.dumps({'type': 'prompts_ready', 'prompts': current_state.enhanced_prompts, 'message': 'Enhanced prompts available'})}

"
                
                # Step 4: Generate Ad Copy
                current_state = await image_service._generate_ad_copy(current_state)
                if current_state.error:
                    raise Exception(f"Ad copy generation failed: {current_state.error}")
                
                # Send ad copy with detailed console output
                if current_state.ad_copy:
                    ad_copy = current_state.ad_copy
                    newline = "\n"
                    copy_preview = f"Headline: {ad_copy.get('headline', 'N/A')}{newline}Description: {ad_copy.get('description', 'N/A')[:80]}...{newline}CTA: {ad_copy.get('cta', 'N/A')}"
                    message = f'✅ Ad copy generated:{newline}{copy_preview}'
                    yield f"data: {json.dumps({'type': 'step_completed', 'step': 'copy_generation', 'message': message})}

"
                    yield f"data: {json.dumps({'type': 'copy_ready', 'ad_copy': current_state.ad_copy, 'message': 'Ad copy available'})}

"
                
                # Step 5: Generate Images
                current_state = await image_service._generate_images(current_state)
                if current_state.error:
                    raise Exception(f"Image generation failed: {current_state.error}")
                
                if not current_state.generated_images:
                    raise Exception("No images were generated")
                
                # Store images with request ID
                request_id = str(uuid.uuid4())
                image_service.image_storage[request_id] = current_state.generated_images
                for image in current_state.generated_images:
                    image.request_id = request_id
                
                # Send image generation completion
                image_count = len(current_state.generated_images)
                yield f"data: {json.dumps({'type': 'step_completed', 'step': 'image_generation', 'message': f'✅ Generated {image_count} images successfully'})}

"
                
                # Create workflow result
                workflow_result = {
                    "images": current_state.generated_images,
                    "enhanced_prompts": current_state.enhanced_prompts,
                    "ad_copy": current_state.ad_copy,
                    "request_id": request_id,
                }
                
            except Exception as workflow_error:
                logger.error(f"Workflow step failed: {workflow_error}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'❌ {str(workflow_error)}'})}

"
                return

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

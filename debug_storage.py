#!/usr/bin/env python3
"""
Test script to debug image storage and modification issues.
"""

import asyncio
import sys
import os

# Add the backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'be'))

from services.image_service import ImageGenerationService
from models.image_models import ImageGenerationRequest, ImageModificationRequest

async def test_image_storage():
    """Test image generation and storage."""
    print("🔍 Testing image storage and modification...")
    
    # Create service instance
    service = ImageGenerationService()
    
    # Create a test request
    request = ImageGenerationRequest(
        company_url="https://superhuman.com/",
        product_name="AI powered Email",
        business_value="Reply to Your Customers Faster",
        audience="Director of Sales, Director of Business Development",
        body_text="Test body text",
        footer_text="Test CTA"
    )
    
    print("📝 Generating images...")
    
    # Generate images
    images = await service.generate_images_with_progress(request)
    
    print(f"✅ Generated {len(images)} images")
    print(f"📊 Storage entries: {len(service.image_storage)}")
    
    # Print storage contents
    for req_id, imgs in service.image_storage.items():
        img_ids = [img.id for img in imgs]
        print(f"Request {req_id}: {len(imgs)} images with IDs: {img_ids}")
    
    if images:
        # Try to modify the first image
        first_image = images[0]
        print(f"🔧 Attempting to modify image: {first_image.id}")
        
        modify_request = ImageModificationRequest(
            original_image_id=first_image.id,
            modification_prompt="Make the background blue"
        )
        
        try:
            modified_image = await service.modify_image(modify_request)
            print(f"✅ Successfully modified image: {modified_image.id}")
        except Exception as e:
            print(f"❌ Failed to modify image: {e}")
    
    print("🏁 Test completed")

if __name__ == "__main__":
    asyncio.run(test_image_storage())

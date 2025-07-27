import asyncio
import base64
import logging
import os
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from openai import AsyncOpenAI
from pydantic import BaseModel

from models import (
    GeneratedImage,
    ImageGenerationRequest,
    ImageModificationRequest,
    ImageStyle,
)

logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """State for the LangGraph workflow."""

    request: ImageGenerationRequest
    company_analysis: Optional[str] = None
    enhanced_prompts: Optional[List[str]] = None
    ad_copy: Optional[Dict[str, str]] = None  # headline, description, cta
    reference_images: Optional[List[str]] = None  # base64 encoded reference images
    generated_images: Optional[List[GeneratedImage]] = None
    error: Optional[str] = None


class ImageGenerationService:
    """Service for generating LinkedIn ad images using LangGraph workflow."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not found. Service will use placeholder responses."
            )
            self.openai_client = None
            self.llm = None
        else:
            self.openai_client = AsyncOpenAI()
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
            )
        self.styles = [
            ImageStyle.PROFESSIONAL,
            ImageStyle.MODERN,
            ImageStyle.CREATIVE,
            ImageStyle.MINIMALIST,
            ImageStyle.BOLD,
        ]
        self.workflow = self._create_workflow()
        self.reference_images_path = (
            Path(__file__).parent.parent / "datasets" / "ref_imgs"
        )

        # In-memory storage for generated images
        self.image_storage: Dict[str, List[GeneratedImage]] = {}

    def _create_workflow(self) -> CompiledStateGraph:
        """Create the LangGraph workflow for image generation."""

        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze_company", self._analyze_company)
        workflow.add_node("load_references", self._load_reference_images)
        workflow.add_node("enhance_prompts", self._enhance_prompts)
        workflow.add_node("generate_copy", self._generate_ad_copy)
        workflow.add_node("generate_images", self._generate_images_node)

        # Define the flow
        workflow.set_entry_point("analyze_company")
        workflow.add_edge("analyze_company", "load_references")
        workflow.add_edge("load_references", "enhance_prompts")
        workflow.add_edge("enhance_prompts", "generate_copy")
        workflow.add_edge("generate_copy", "generate_images")
        workflow.add_edge("generate_images", END)

        return workflow.compile()

    async def _analyze_company(self, state: WorkflowState) -> WorkflowState:
        """Analyze the company to understand their brand and context."""
        try:
            if not self.llm:
                state.company_analysis = f"Professional business analysis for {state.request.product_name} targeting {state.request.audience}"
                return state

            analysis_prompt = f"""
            Analyze the following company information and provide comprehensive insights for creating high-performing LinkedIn B2B ad images:

            Company URL: {state.request.company_url}
            Product: {state.request.product_name}
            Business Value: {state.request.business_value}
            Target Audience: {state.request.audience}
            Body Text: {state.request.body_text}
            Footer Text: {state.request.footer_text}

            Provide:
            
            1. **Brand Personality & Visual Tone**: Analyze brand voice and recommend specific visual aesthetics (corporate, innovative, approachable, authoritative)
            2. **Audience Persona Insights**: Detail target customer demographics, pain points, and visual preferences for personalized imagery
            3. **B2B Messaging Themes**: Identify key value propositions that resonate (ROI, efficiency, innovation, trust, expertise)
            4. **Professional Context Settings**: Recommend specific environments (modern office, conference room, tech lab, remote workspace)
            5. **Inclusive Representation**: Suggest diverse, authentic professional scenarios that increase engagement by ~23 points
            6. **Data Visualization Elements**: Recommend incorporating charts, dashboards, metrics, or statistics relevant to the business value
            7. **Emotional Tone & Mood**: Specify lighting, expressions, and atmosphere (confident, collaborative, innovative, trustworthy)
            8. **Technical Specifications**: Recommend camera angles, composition, and photographic details for photorealistic results
            9. **Thumb-Stopping Elements**: Identify attention-grabbing visual elements that maintain B2B credibility
            10. **Industry-Specific Context**: Provide sector-relevant visual cues and professional scenarios

            Format your analysis with specific, actionable recommendations for detailed AI image generation prompts.
            """

            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            state.company_analysis = response.content

        except Exception as e:
            logger.error(f"Error in company analysis: {e}")
            state.error = f"Company analysis failed: {str(e)}"

        return state

    async def _enhance_prompts(self, state: WorkflowState) -> WorkflowState:
        """Generate enhanced prompts for each image style."""
        try:
            prompts = []

            for style in self.styles:
                if not self.llm:
                    # Fallback prompt generation
                    prompt = self._create_fallback_prompt_for_style(
                        state.request, style
                    )
                    prompts.append(prompt)
                    continue

                style_prompt = f"""
        Create a highly-optimized DALL-E 3 prompt for a LinkedIn ad image with people on a simple background and a CTA text with high-contrass background.
        
        Use the proven prompt structure: ACTION + SUBJECT + CONTEXT + VISUAL DETAILS + STYLE CUES + CTA OPTIMIZATION

        **Context:**
        - Product/Service: {state.request.product_name}
        - Target Audience: {state.request.audience}
        - Business Value: {state.request.business_value}
        - Style: {style.value}

        **Style Guide:** {self._get_style_description(style)}

        **DALL-E Prompt Requirements:**

        1. **Main Subject:** Professional business people representing {state.request.audience}
           - Confident, approachable expression
           - Professional business attire appropriate for the industry
           - Diverse representation (vary ethnicity, age, gender)
           - Upper body or headshot composition
           - People should embody the target audience for {state.request.product_name}

        2. **Background:** Simple and clean - NO complex environments
           - Solid colors, subtle gradients, or minimal geometric elements ONLY
           - High contrast with the person for text overlay
           - NO offices, NO detailed environments, NO busy patterns
           - Choose background color that complements the {style.value} style

        3. **Technical Specs:**
           - Square format (1:1 aspect ratio) for LinkedIn feed
           - Professional photography quality (shot on Canon 5D, studio lighting)
           - Sharp focus on person, slightly blurred background if needed
           - Leave 30% of image space clear for text overlay
           - High contrast between person and background

        4. **LinkedIn Optimization:**
           - Design for mobile viewing (clear at small sizes)
           - Professional B2B credibility
           - Thumb-stopping appeal without being flashy
           - Appropriate for {state.request.audience} in {state.request.product_name} context

        The prompt should be concise (max 250 words) with the goal to create a professional LinkedIn ad image with:
        - A business person representing {state.request.audience}
        - Simple, clean background (no complex environments)
        - {style.value} style execution
        - High contrast for text overlay
        - Professional B2B appeal
        
        **Critical Technical Requirements**:
        - Photorealistic quality with simple background and CTA texts should contrass that background.
        - LinkedIn-optimized composition (1:1 aspect ratio preferred)
        - HIGH CONTRAST backgrounds (light backgrounds for dark text, dark backgrounds for light text)
        - Professional lighting for people on the image (studio quality, natural daylight, warm professional tones)
        - Brand-aligned color palette that supports text readability
        - Mobile-first design with clear focal points
        - Space allocation for CTA text overlay in high-contrast areas
        - Visual hierarchy that guides eye to CTA placement areas

        **CTA Integration Requirements**:
        - Reserve 20-30% of image space for text overlay placement
        - Ensure background contrast ratio of at least 4.5:1 for accessibility
        - Consider CTA text: "{state.request.footer_text or 'Learn More'}" when designing contrast areas
        - Include visual elements that naturally frame or highlight CTA placement
        
        **Required Elements (Must Include ALL):**
        1. **Clear Action Verb**: Start with "Create LinkedIn Ad image of..." or "Generate a professional LinkedIn Ad scene showing..."
        2. **Specific Subject**: Name exact people/objects related to {state.request.product_name} and {state.request.audience}
        3. **Rich Context**: Detailed environment that reflects the company analysis and business value
        4. **Technical Photography**: Include "shot on Canon 5D with 50mm lens, studio lighting, shallow depth of field for pictures portraited in the image"
        5. **Audience Empathy**: Diverse, authentic professionals representing {state.request.audience} 
        6. **B2B Credibility**: Thought leadership positioning, expertise signals related to {state.request.business_value}
        7. **Emotional Tone**: Specify mood that aligns with the target audience and business context
        8. **CTA Optimization**: High contrast areas specifically designed for text overlay of "{state.request.footer_text or 'Learn More'}"
        9. **Color Contrast**: Specify background colors that provide high contrast for white/dark text overlay.
        10. **Mobile Optimization**: Clear visual hierarchy optimized for 1200x1200px LinkedIn format
        11. **Thumb-Stopping Appeal**: Attention-grabbing elements balanced with B2B professionalism
        12. **Brand Context**: Visual elements that reflect the company's industry and professional context
        13. **Value Visualization**: Visual metaphors or direct representations of {state.request.business_value}
        """

                response = await self.llm.ainvoke([HumanMessage(content=style_prompt)])
                prompts.append(response.content.strip())

            state.enhanced_prompts = prompts

        except Exception as e:
            logger.error(f"Error enhancing prompts: {e}")
            state.error = f"Prompt enhancement failed: {str(e)}"

        return state

    async def _load_reference_images(self, state: WorkflowState) -> WorkflowState:
        """Load and encode reference images: 1 main_ref + 5 random non-main images."""
        try:
            reference_images = []
            # Use correct path relative to the backend directory
            ref_imgs_path = Path(__file__).parent.parent / "datasets" / "ref_imgs"

            if ref_imgs_path.exists():
                # Get all image files
                all_image_files = (
                    list(ref_imgs_path.glob("*.png"))
                    + list(ref_imgs_path.glob("*.jpg"))
                    + list(ref_imgs_path.glob("*.jpeg"))
                )

                if all_image_files:
                    # Separate main_ref files from other files
                    main_ref_files = [
                        f for f in all_image_files if f.name.startswith("main_ref")
                    ]
                    other_files = [
                        f for f in all_image_files if not f.name.startswith("main_ref")
                    ]

                    # Load 1 main_ref file (randomly selected if multiple exist)
                    if main_ref_files:
                        main_ref_file = random.choice(main_ref_files)
                        try:
                            with open(main_ref_file, "rb") as img_file:
                                img_data = base64.b64encode(img_file.read()).decode(
                                    "utf-8"
                                )
                                reference_images.append(img_data)
                                logger.info(
                                    f"Loaded main reference: {main_ref_file.name}"
                                )
                        except Exception as e:
                            logger.warning(
                                f"Could not load main reference {main_ref_file}: {e}"
                            )

                    # Load up to 5 random other images (non-main_ref)
                    if other_files:
                        selected_other_files = random.sample(
                            other_files, min(5, len(other_files))
                        )

                        for img_path in selected_other_files:
                            try:
                                with open(img_path, "rb") as img_file:
                                    img_data = base64.b64encode(img_file.read()).decode(
                                        "utf-8"
                                    )
                                    reference_images.append(img_data)
                            except Exception as e:
                                logger.warning(
                                    f"Could not load reference image {img_path}: {e}"
                                )
                                continue

                        logger.info(
                            f"Loaded {len(selected_other_files)} additional reference images"
                        )

            state.reference_images = reference_images
            logger.info(
                f"Total loaded reference images: {len(reference_images)} (1 main_ref + {len(reference_images)-1 if reference_images else 0} others)"
            )

        except Exception as e:
            logger.error(f"Error loading reference images: {e}")
            # Continue without reference images
            state.reference_images = []

        return state

    async def _generate_ad_copy(self, state: WorkflowState) -> WorkflowState:
        """Generate high-converting LinkedIn ad copy"""
        try:
            if not self.llm:
                # Enhanced fallback copy generation with SpeedWork Social patterns
                state.ad_copy = {
                    "headline": f"Transform Your Business with {state.request.product_name}",
                    "description": f"Discover how {state.request.product_name} delivers {state.request.business_value} for {state.request.audience}. Join thousands of satisfied customers.",
                    "cta": "Book a Call",
                }
                return state

            copy_prompt = f"""
            Act as a LinkedIn advertising expert. Create high-converting B2B ad copy:
            
            **Campaign Context:**
            Company Analysis: {state.company_analysis or 'Professional B2B business'}
            Product/Service: {state.request.product_name}
            Core Value Proposition: {state.request.business_value}
            Target Audience: {state.request.audience}
            Additional Context: {state.request.body_text}
            
            **SpeedWork Social High-Performance Framework:**
            
            **1. AIDA Structure Implementation:**
            - **Attention**: Hook that grabs attention (problem, stat, or compelling question)
            - **Interest**: Clear value proposition that resonates with audience pain points
            - **Desire**: Social proof, authority, or compelling outcome visualization
            - **Action**: Persuasive, specific CTA that drives immediate response
            
            **2. Target Audience Deep Analysis:**
            - Identify specific job titles and seniority levels within the audience
            - Address core pain points and challenges they face daily
            - Focus on desired outcomes and success metrics they care about
            - Consider their decision-making process and buying triggers
            
            **3. Hook Strategies (Choose Most Effective):**
            - **Problem Hook**: "Struggling with [specific pain point]?"
            - **Stat Hook**: "[X]% of [audience] are missing out on [benefit]"
            - **Question Hook**: "What if you could [achieve desired outcome] in [timeframe]?"
            - **Curiosity Hook**: "The [industry] secret that [outcome]"
            
            **4. Value Proposition Guidelines:**
            - Lead with the transformation/outcome, not the product features
            - Quantify benefits where possible (time saved, revenue increased, etc.)
            - Address the "what's in it for me" immediately
            - Differentiate from competitors with unique positioning
            
            **5. Social Proof & Authority Elements:**
            - Reference client results, case studies, or success stories
            - Include industry recognition, certifications, or thought leadership
            - Mention company size, growth metrics, or market position
            - Use testimonial-style language when appropriate
            
            **6. CTA Optimization:**
            - Use action-oriented language: "Book a Call", "Get Started", "Download Now"
            - Create urgency without being pushy: "Limited spots", "Free consultation"
            - Match CTA to funnel stage and audience readiness
            - Keep CTAs specific and benefit-focused
            
            **7. LinkedIn B2B Best Practices:**
            - Professional tone that builds trust and credibility
            - Avoid overly promotional or salesy language
            - Focus on business outcomes and ROI
            - Use industry-appropriate terminology and context
            - Ensure mobile-friendly formatting and readability
            
            **Output Requirements:**
            Generate JSON with exactly these fields:
            {{
                "headline": "Attention-grabbing headline (max 150 chars) using hook strategy",
                "description": "AIDA-structured description (max 600 chars) with value prop + social proof",
                "cta": "Compelling action-oriented CTA (max 20 chars)"
            }}
            
            **Quality Checklist:**
            ✓ Hook immediately addresses audience pain point or desire
            ✓ Value proposition is clear and benefit-focused
            ✓ Social proof or authority signal included
            ✓ CTA creates urgency and specifies next step
            ✓ Professional tone appropriate for B2B LinkedIn
            ✓ Mobile-optimized length and formatting
            ✓ Differentiated positioning vs. competitors
            
            Return ONLY the JSON with no additional text or formatting.
            """

            response = await self.llm.ainvoke([HumanMessage(content=copy_prompt)])

            try:
                import json

                ad_copy = json.loads(response.content.strip())
                state.ad_copy = ad_copy
            except json.JSONDecodeError:
                # Enhanced fallback if JSON parsing fails
                state.ad_copy = {
                    "headline": f"Ready to Transform Your {state.request.audience} Strategy?",
                    "description": f"See how {state.request.product_name} delivers {state.request.business_value}. Join industry leaders who've already made the switch.",
                    "cta": "Book a Call",
                }

        except Exception as e:
            logger.error(f"Error generating ad copy: {e}")
            # Enhanced fallback copy with SpeedWork Social patterns
            state.ad_copy = {
                "headline": f"What if {state.request.audience} Could Achieve {state.request.business_value}?",
                "description": f"Discover the proven solution that's helping businesses like yours unlock {state.request.business_value}. Don't let competitors get ahead.",
                "cta": "Book a Call",
            }

        return state

    async def _generate_images_node(self, state: WorkflowState) -> WorkflowState:
        """Generate images using the enhanced prompts."""
        try:
            if not state.enhanced_prompts:
                raise ValueError("No enhanced prompts available")

            # Generate images sequentially to respect rate limits (5/min for DALL-E 3)
            images: List[GeneratedImage] = []
            for i, (prompt, style) in enumerate(
                zip(state.enhanced_prompts, self.styles)
            ):
                try:
                    # Add delay between requests to respect rate limits
                    if i > 0:
                        await asyncio.sleep(
                            12
                        )  # 12 seconds between requests (5 per minute)

                    image = await self._generate_single_image(prompt, style)
                    images.append(image)
                    logger.info(f"Generated image {i+1}/5 for style: {style}")

                except Exception as e:
                    logger.error(f"Error generating image for style {style}: {e}")
                    # Continue with other images even if one fails
                    continue

            state.generated_images = images

        except Exception as e:
            logger.error(f"Error generating images: {e}")
            state.error = f"Image generation failed: {str(e)}"

        return state

    async def _generate_single_image(
        self, prompt: str, style: ImageStyle
    ) -> GeneratedImage:
        """Generate a single image using DALL-E 3."""
        try:
            if not self.openai_client:
                # Return placeholder when no API key
                return GeneratedImage(
                    id=str(uuid.uuid4()),
                    url=f"https://via.placeholder.com/1024x1024?text=Modified+{style.value.title()}",
                    style=style,
                    prompt_used=prompt,
                    generation_timestamp=datetime.now().isoformat(),
                )

            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return GeneratedImage(
                id=str(uuid.uuid4()),
                url=response.data[0].url,
                style=style,
                prompt_used=prompt,
                generation_timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"DALL-E generation error: {e}")
            # Return placeholder on error
            return GeneratedImage(
                id=str(uuid.uuid4()),
                url="https://via.placeholder.com/1024x1024?text=Generation+Error",
                style=style,
                prompt_used=prompt,
                generation_timestamp=datetime.now().isoformat(),
            )

    def _get_style_description(self, style: ImageStyle) -> str:
        """Get detailed description for each image style optimized for LinkedIn ads."""
        style_descriptions = {
            ImageStyle.PROFESSIONAL: """Professional business person on clean, simple background. Show: confident business professional in suit or professional attire, positioned prominently in frame, warm studio lighting, diverse representation. Background: solid white, light gray, or subtle blue gradient - NO office environments, NO complex backgrounds. Technical specs: shot on Canon 5D with 50mm lens, shallow depth of field focusing on person, high contrast between person and background for text overlay. Person should have confident, approachable expression with professional credibility.""",
            ImageStyle.MODERN: """Modern professional with tech-forward styling on minimalist backdrop. Show: contemporary business person in modern professional attire, clean lines, tech-savvy appearance. Background: solid modern colors like navy blue, teal, or clean geometric pattern - AVOID complex office environments. Technical specs: crisp quality, modern color schemes, mobile-optimized composition. Focus on single person with contemporary, innovative look against simple background.""",
            ImageStyle.CREATIVE: """Creative professional with artistic but business-appropriate styling. Show: expressive but professional person with creative energy, approachable demeanor, engaging eye contact. Background: simple vibrant colors or subtle artistic patterns - NOT overwhelming, NO complex environments. Use compelling lighting and rich textures on the person while keeping background minimal. Balance creativity with professional credibility through clean composition.""",
            ImageStyle.MINIMALIST: """Ultra-clean portrait with maximum simplicity. Show: single professional person, headshot or upper body, simple clothing, clear focus on person. Background: pure white, light gray, or single solid color - absolutely minimal, NO patterns or distractions. Technical specs: sharp focus on person, clean lines, professional lighting. Emphasize clarity and simplicity with lots of negative space around the person.""",
            ImageStyle.BOLD: """Confident professional with strong visual impact on high-contrast background. Show: dynamic business person with confident presence, strong expression, professional attire. Background: bold solid colors like deep blue, black, or strong contrast colors - NO complex elements. Technical specs: high contrast between person and background, energetic lighting on person. Focus on single confident professional against simple, bold background.""",
        }
        return style_descriptions.get(
            style, "Professional business style optimized for LinkedIn engagement"
        )

    async def generate_images(
        self, request: ImageGenerationRequest
    ) -> List[GeneratedImage]:
        """Generate images using the LangGraph workflow."""
        try:
            # Create initial state
            initial_state = WorkflowState(request=request)

            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)

            if result.error:
                logger.error(f"Workflow error: {result.error}")
                # Fallback to simple generation
                return await self._fallback_generation(request)

            if result.generated_images:
                # Store images with request ID
                request_id = str(uuid.uuid4())
                self.image_storage[request_id] = result.generated_images
                for image in result.generated_images:
                    image.request_id = request_id

                return result.generated_images

            # Fallback if no images generated
            return await self._fallback_generation(request)

        except Exception as e:
            logger.error(f"Error in generate_images: {e}")
            return await self._fallback_generation(request)

    async def generate_images_with_progress(
        self, request: ImageGenerationRequest, event_stream_callback=None
    ) -> List[GeneratedImage]:
        """Generate images with streaming progress updates including all workflow steps."""
        try:
            # Create initial state
            current_state = WorkflowState(request=request)

            # Step 1: Company Analysis
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "progress",
                        "step": "company_analysis",
                        "message": "🔍 Analyzing company information...",
                    }
                )

            current_state = await self._analyze_company(current_state)
            if current_state.error:
                raise Exception(f"Company analysis failed: {current_state.error}")
            
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "step_completed",
                        "step": "company_analysis",
                        "message": "✅ Company analysis completed",
                    }
                )

            # Step 2: Load Reference Images
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "progress",
                        "step": "loading_references",
                        "message": "📁 Loading reference ad examples...",
                    }
                )

            current_state = await self._load_reference_images(current_state)
            if current_state.error:
                raise Exception(f"Reference loading failed: {current_state.error}")
            
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "step_completed",
                        "step": "loading_references",
                        "message": f"✅ Loaded {len(current_state.reference_images)} reference images",
                    }
                )

            # Step 3: Generate Enhanced Prompts
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "progress",
                        "step": "prompt_enhancement",
                        "message": "🎯 Enhancing prompts with AI...",
                    }
                )

            current_state = await self._enhance_prompts(current_state)
            if current_state.error:
                raise Exception(f"Prompt enhancement failed: {current_state.error}")
            
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "step_completed",
                        "step": "prompt_enhancement",
                        "message": "✅ Enhanced prompts generated",
                        "prompts": current_state.enhanced_prompts,
                    }
                )

            # Step 4: Generate Ad Copy
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "progress",
                        "step": "copy_generation",
                        "message": "✍️ Generating compelling ad copy...",
                    }
                )

            current_state = await self._generate_ad_copy(current_state)
            if current_state.error:
                raise Exception(f"Ad copy generation failed: {current_state.error}")
            
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "step_completed",
                        "step": "copy_generation",
                        "message": "✅ Ad copy generated",
                        "ad_copy": current_state.ad_copy,
                    }
                )

            # Step 5: Generate Images
            if event_stream_callback:
                await event_stream_callback(
                    {
                        "type": "progress",
                        "step": "image_generation",
                        "message": "🎨 Generating images with DALL-E 3...",
                    }
                )

            # Generate images with progress updates
            images: List[GeneratedImage] = []
            for i, (prompt, style) in enumerate(
                zip(current_state.enhanced_prompts, self.styles)
            ):
                try:
                    if event_stream_callback:
                        await event_stream_callback(
                            {
                                "type": "progress",
                                "step": "image_generation",
                                "message": f"🎨 Generating {style.value} style image ({i+1}/5)...",
                            }
                        )

                    # Add delay between requests to respect rate limits
                    if i > 0:
                        await asyncio.sleep(12)  # 12 seconds between requests

                    image = await self._generate_single_image(prompt, style)
                    images.append(image)

                    if event_stream_callback:
                        await event_stream_callback(
                            {
                                "type": "image_ready",
                                "step": "image_generation",
                                "message": f"✅ {style.value} style image completed",
                                "image": image.dict(),
                                "progress": f"{i+1}/5",
                            }
                        )

                except Exception as e:
                    logger.error(f"Error generating image for style {style}: {e}")
                    if event_stream_callback:
                        await event_stream_callback(
                            {
                                "type": "error",
                                "step": "image_generation",
                                "message": f"❌ Failed to generate {style.value} style image: {str(e)}",
                            }
                        )
                    continue

            # Store images with request ID
            if images:
                # Use the request_id from the first image (set by workflow)
                request_id = images[0].request_id if images[0].request_id else str(uuid.uuid4())
                self.image_storage[request_id] = images
                # Ensure all images have the same request_id
                for image in images:
                    if not image.request_id:
                        image.request_id = request_id
                
                if event_stream_callback:
                    await event_stream_callback(
                        {
                            "type": "generation_complete",
                            "message": f"🎉 All {len(images)} images generated successfully!",
                            "images": [img.dict() for img in images],
                            "enhanced_prompts": current_state.enhanced_prompts,
                            "ad_copy": current_state.ad_copy,
                            "request_id": request_id,
                        }
                    )

            return images

        except Exception as e:
            logger.error(f"Error in generate_images_with_progress: {e}")
            if event_stream_callback:
                await event_stream_callback(
                    {"type": "error", "message": f"❌ Generation failed: {str(e)}"}
                )
            return await self._fallback_generation(request)

    async def _fallback_generation(
        self, request: ImageGenerationRequest
    ) -> List[GeneratedImage]:
        """Fallback image generation without LangGraph."""
        images = []

        for style in self.styles:
            prompt = self._create_fallback_prompt(request, style)
            image = await self._generate_single_image(prompt, style)
            images.append(image)

        return images

    def _create_fallback_prompt(
        self, request: ImageGenerationRequest, style: ImageStyle
    ) -> str:
        """Create a LinkedIn-optimized prompt without LangGraph enhancement."""
        return f"""
        Create a high-performing LinkedIn advertisement image for {request.product_name}.
        
        Business Value: {request.business_value}
        Target Audience: {request.audience}
        Body Text Context: {request.body_text}
        Call-to-Action: {request.footer_text}
        Style: {self._get_style_description(style)}
        
        LinkedIn Ad Optimization (based on high-performing ad patterns):
        - Thumb-stopping visual that stands out in professional feeds
        - Clear visual hierarchy supporting concise messaging
        - Professional color palette with attention-grabbing elements
        - Mobile-optimized design with readable text areas
        - B2B-appropriate aesthetic with engaging visual elements
        - Space for audience callouts and value proposition
        - Design supports educational/thought leadership positioning
        
        Reference Visual Patterns (incorporate these successful LinkedIn ad elements):
        - Split-screen layouts with person + product/data visualization
        - Professional headshots with subtle brand elements in background
        - Clean infographic-style layouts with key statistics prominently displayed
        - Workspace/office environments showing the product in professional context
        - Before/after comparison layouts showing business transformation
        - Team collaboration scenes with subtle product integration
        - Data dashboard mockups with compelling metrics and charts
        - Executive-level meeting scenarios with strategic business context
        
        Technical Requirements:
        - 1024x1024 pixels, high resolution
        - Professional LinkedIn advertising standards
        - High contrast areas for text overlay
        - Modern, clean composition optimized for business audience engagement
        """

    async def modify_image(self, request: ImageModificationRequest) -> GeneratedImage:
        """Modify an existing image based on user feedback."""
        try:
            logger.info(f"Modifying image {request.original_image_id} with prompt: {request.modification_prompt}")
            logger.info(f"Available images in storage: {list(self.image_storage.keys())}")
            
            # Find the original image
            original_image = None
            for request_id, images in self.image_storage.items():
                logger.info(f"Checking request_id {request_id} with {len(images)} images")
                for img in images:
                    logger.info(f"Checking image ID: {img.id}")
                    if img.id == request.original_image_id:
                        original_image = img
                        break
                if original_image:
                    break

            if not original_image:
                logger.error(f"Original image {request.original_image_id} not found in storage")
                raise ValueError(
                    f"Original image {request.original_image_id} not found"
                )

            # Create modified prompt with LinkedIn optimization
            modified_prompt = f"""{original_image.prompt_used}

Modification Request: {request.modification_prompt}

Apply modifications while preserving research-backed LinkedIn B2B optimization:

**Maintain Core Elements:**
- Photorealistic quality with technical photography specifications (Canon 5D, 50mm lens, studio lighting)
- Professional B2B context and credible business scenarios
- Diverse, authentic representation that increases engagement by ~23 points
- Clear visual hierarchy optimized for mobile LinkedIn viewing
- High contrast areas for text overlay and messaging

**Preserve Engagement Factors:**
- Thumb-stopping visual appeal balanced with B2B professionalism
- Thought leadership positioning and expertise signals
- Space for data visualization, statistics, or compelling metrics
- Emotional tone (confident, collaborative, innovative, trustworthy)
- Industry-specific context and audience-empathetic scenarios

**Technical Consistency:**
- Maintain 1200x1200px or 4:5 aspect ratio for LinkedIn optimization
- Preserve lighting quality (bright daylight, warm studio lighting)
- Keep composition elements that support text readability
- Ensure brand-aligned color palette and professional styling

Apply the requested modifications while strengthening these proven B2B engagement elements."""

            if not self.openai_client:
                # Return placeholder when no API key
                return GeneratedImage(
                    id=str(uuid.uuid4()),
                    url=f"https://via.placeholder.com/1024x1024?text=Modified+{original_image.style.value.title()}",
                    style=original_image.style,
                    prompt_used=modified_prompt,
                    generation_timestamp=datetime.now().isoformat(),
                )

            # Generate modified image
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=modified_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return GeneratedImage(
                id=str(uuid.uuid4()),
                url=response.data[0].url,
                style=original_image.style,
                prompt_used=modified_prompt,
                generation_timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Error modifying image: {e}")
            raise Exception(f"Failed to modify image: {str(e)}")

    def get_stored_images(self, request_id: str) -> Optional[List[GeneratedImage]]:
        """Retrieve stored images by request ID."""
        return self.image_storage.get(request_id)

    def _create_fallback_prompt_for_style(
        self, request: ImageGenerationRequest, style: ImageStyle
    ) -> str:
        """Create research-backed fallback prompts when LLM is not available."""
        base_context = f"professional {request.product_name} for {request.audience}"

        fallback_prompts = {
            ImageStyle.PROFESSIONAL: f"""Professional business person in suit, confident expression, shot on Canon 5D with studio lighting, solid white or light gray background, upper body composition, diverse representation, high contrast for text overlay, square format, LinkedIn optimized. Context: {base_context}""",
            ImageStyle.MODERN: f"""Modern business professional in contemporary attire, tech-savvy appearance, clean navy blue or teal solid background, professional photography, confident pose, diverse representation, high contrast, square format, mobile optimized. Context: {base_context}""",
            ImageStyle.CREATIVE: f"""Creative professional with expressive but business-appropriate styling, approachable demeanor, simple vibrant colored background, artistic lighting, engaging eye contact, diverse representation, clean composition, high contrast for text. Context: {base_context}""",
            ImageStyle.MINIMALIST: f"""Single business professional headshot, simple clothing, pure white background, minimal composition, sharp focus on person, professional lighting, lots of negative space, diverse representation, ultra-clean design. Context: {base_context}""",
            ImageStyle.BOLD: f"""Confident business person with strong presence, professional attire, bold solid color background (deep blue or black), high contrast lighting, dynamic expression, diverse representation, square format, impactful composition. Context: {base_context}""",
        }

        return fallback_prompts.get(
            style,
            f"Professional photorealistic LinkedIn advertisement image for {base_context}, shot on Canon 5D with 50mm lens, diverse representation, modern office setting, high contrast for text overlay, B2B optimized",
        )

    async def generate_images_with_workflow(
        self, request: ImageGenerationRequest
    ) -> Optional[Dict]:
        """Generate images using the full workflow and return enhanced data including prompts and copy."""
        try:
            # Create initial state
            initial_state = WorkflowState(request=request)

            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)

            if result.error:
                logger.error(f"Workflow error: {result.error}")
                return None

            if result.generated_images:
                # Store images with request ID
                request_id = str(uuid.uuid4())
                self.image_storage[request_id] = result.generated_images
                for image in result.generated_images:
                    image.request_id = request_id

                return {
                    "images": result.generated_images,
                    "enhanced_prompts": result.enhanced_prompts,
                    "ad_copy": result.ad_copy,
                    "request_id": request_id,
                }

            return None

        except Exception as e:
            logger.error(f"Error in generate_images_with_workflow: {e}")
            return None


# Global service instance
image_service = ImageGenerationService()

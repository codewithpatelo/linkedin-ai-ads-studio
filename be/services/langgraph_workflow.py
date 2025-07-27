import asyncio
import json
from typing import Any, Dict, List

from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, Graph

from models import ImageGenerationRequest, ImageStyle


class ImageGenerationWorkflow:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow for image generation"""

        # Define the workflow graph
        workflow = Graph()

        # Add nodes matching the streaming steps
        workflow.add_node("company_analysis", self.analyze_company)
        workflow.add_node("load_references", self.load_references)
        workflow.add_node("prompt_enhancement", self.generate_prompts)
        workflow.add_node("copy_generation", self.generate_copy)
        workflow.add_node("image_generation", self.finalize)

        # Add edges
        workflow.add_edge("company_analysis", "load_references")
        workflow.add_edge("load_references", "prompt_enhancement")
        workflow.add_edge("prompt_enhancement", "copy_generation")
        workflow.add_edge("copy_generation", "image_generation")
        workflow.add_edge("image_generation", END)

        # Set entry point
        workflow.set_entry_point("company_analysis")

        return workflow.compile()

    async def analyze_company(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company information to extract key insights for LinkedIn ads"""
        request: ImageGenerationRequest = state["request"]

        analysis_prompt = PromptTemplate(
            input_variables=[
                "company_url",
                "product_name",
                "business_value",
                "audience",
            ],
            template="""
            Act as a LinkedIn advertising expert and analyze this company for high-converting B2B ad creation:
            
            Company URL: {company_url}
            Product: {product_name}
            Business Value: {business_value}
            Target Audience: {audience}
            
            Provide comprehensive analysis for LinkedIn ad optimization:
            
            1. **Industry & Company Profile**:
               - Industry sector and business model
               - Company size and market position
               - Key differentiators and competitive advantages
            
            2. **Target Audience Deep Dive**:
               - Specific job titles and seniority levels
               - Industry pain points and challenges
               - Desired outcomes and success metrics
               - Decision-making process and buying triggers
            
            3. **Visual Brand Strategy**:
               - Professional color palette (primary, secondary, accent colors)
               - Typography recommendations (professional, modern fonts)
               - Visual hierarchy principles for LinkedIn ads
               - Brand personality and visual tone
            
            4. **Messaging Framework**:
               - Hook strategies (problems, stats, questions)
               - Value proposition positioning
               - Social proof opportunities
               - Compelling CTAs for this audience
            
            5. **LinkedIn Ad Best Practices**:
               - Optimal text-to-image ratio (max 50% text)
               - Eye-catching visual elements
               - Mobile-first design considerations
               - Thumb-stopping appeal factors
            
            6. **Content Themes**:
               - Primary messaging angles
               - Emotional triggers for this audience
               - Industry-specific visual metaphors
               - Trust and credibility signals
            
            Return analysis in JSON format with detailed insights for each category.
            """,
        )

        prompt = analysis_prompt.format(
            company_url=request.company_url,
            product_name=request.product_name,
            business_value=request.business_value,
            audience=request.audience,
        )

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        try:
            analysis = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analysis = {
                "industry": "technology",
                "visual_elements": ["modern", "clean", "professional"],
                "color_palette": ["blue", "white", "gray"],
                "tone": "professional",
                "messaging_themes": ["efficiency", "innovation", "growth"],
            }

        state["company_analysis"] = analysis
        return state

    async def load_references(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Load reference images for better generation quality"""
        import base64
        import os
        import random

        # Load reference images from datasets/ref_imgs
        ref_imgs_path = "/home/dell/Documentos/linkedin-ads/be/datasets/ref_imgs"
        reference_images = []

        try:
            if os.path.exists(ref_imgs_path):
                image_files = [
                    f
                    for f in os.listdir(ref_imgs_path)
                    if f.lower().endswith((".png", ".jpg", ".jpeg"))
                ]
                # Select 3-5 random reference images
                selected_files = random.sample(image_files, min(5, len(image_files)))

                for filename in selected_files:
                    file_path = os.path.join(ref_imgs_path, filename)
                    with open(file_path, "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode("utf-8")
                        reference_images.append(
                            {"filename": filename, "data": img_data}
                        )
        except Exception as e:
            print(f"Error loading reference images: {e}")
            # Continue without reference images
            pass

        state["reference_images"] = reference_images
        return state

    async def generate_copy(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LinkedIn ad copy"""
        request: ImageGenerationRequest = state["request"]
        analysis = state["company_analysis"]

        copy_prompt = PromptTemplate(
            input_variables=[
                "company_url",
                "product_name",
                "business_value",
                "audience",
                "analysis",
            ],
            template="""Generate compelling LinkedIn ad copy based on this information:
            
            Company: {company_url}
            Product: {product_name}
            Value Proposition: {business_value}
            Target Audience: {audience}
            Company Analysis: {analysis}
            
            Create a LinkedIn ad copy with:
            1. Compelling headline (max 150 characters)
            2. Engaging description (max 600 characters)
            3. Strong call-to-action (max 30 characters)
            
            Return as JSON with keys: headline, description, cta
            """,
        )

        prompt = copy_prompt.format(
            company_url=request.company_url,
            product_name=request.product_name,
            business_value=request.business_value,
            audience=request.audience,
            analysis=json.dumps(analysis),
        )

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        try:
            ad_copy = json.loads(response.content)
        except:
            # Fallback if JSON parsing fails
            ad_copy = {
                "headline": f"Transform Your {request.product_name} Strategy",
                "description": f"Discover how {request.product_name} delivers {request.business_value} for {request.audience}. Join thousands of professionals already seeing results.",
                "cta": "Learn More",
            }

        state["ad_copy"] = ad_copy
        return state

    async def generate_prompts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-converting LinkedIn ad prompts using proven frameworks"""
        request: ImageGenerationRequest = state["request"]
        analysis = state["company_analysis"]

        prompts = {}

        # Enhanced style-specific templates based on SpeedWork Social best practices
        style_templates = {
            "professional": {
                "visual_approach": "Clean, executive-level design with thought leadership positioning",
                "composition": "Minimal text overlay (max 30%), high contrast background, professional photography style",
                "elements": "Corporate icons, data visualization, professional headshots or office environments",
            },
            "modern": {
                "visual_approach": "Tech-forward design with innovation emphasis and sleek aesthetics",
                "composition": "Bold geometric shapes, gradient backgrounds, modern typography hierarchy",
                "elements": "Digital interfaces, growth charts, modern workspace imagery",
            },
            "creative": {
                "visual_approach": "Artistic visual metaphors balanced with B2B credibility",
                "composition": "Creative layouts with strategic text placement, vibrant but professional colors",
                "elements": "Conceptual imagery, creative typography, artistic representations of business concepts",
            },
            "minimalist": {
                "visual_approach": "Clean, focused mobile-optimized design with maximum impact",
                "composition": "Lots of white space, single focal point, minimal text (max 20%)",
                "elements": "Simple icons, clean typography, single powerful visual element",
            },
            "bold": {
                "visual_approach": "High-impact imagery with compelling data visualization",
                "composition": "Strong contrast, bold typography, attention-grabbing visual hierarchy",
                "elements": "Statistics callouts, bold graphics, dynamic compositions",
            },
        }

        for style in ImageStyle:
            style_config = style_templates.get(
                style.value, style_templates["professional"]
            )

            prompt_template = PromptTemplate(
                input_variables=[
                    "style",
                    "company_url",
                    "product_name",
                    "business_value",
                    "audience",
                    "body_text",
                    "footer_text",
                    "analysis",
                    "visual_approach",
                    "composition",
                    "elements",
                ],
                template="""
                Act as a LinkedIn advertising and prompt engineering expert. Create a high-converting DALL-E prompt for a B2B LinkedIn ad that follows proven performance frameworks:
                
                **Campaign Details:**
                Style: {style}
                Company: {company_url}
                Product: {product_name}
                Value Proposition: {business_value}
                Target Audience: {audience}
                Ad Copy: {body_text}
                CTA: {footer_text}
                
                **Company Intelligence:** {analysis}
                
                **Style Guidelines:**
                Visual Approach: {visual_approach}
                Composition: {composition}
                Key Elements: {elements}
                
                **LinkedIn Ad Performance Rules (CRITICAL):**
                
                1. **Visual Hierarchy & Text Limits:**
                   - Limit text to maximum 50% of image space (preferably 20-30%)
                   - Use bold, readable fonts that work on mobile
                   - Ensure high contrast between text and background
                   - Create clear visual flow toward the CTA
                
                2. **Thumb-Stopping Appeal:**
                   - Design for 1-2 second attention capture
                   - Use eye-catching but relevant visuals
                   - Incorporate movement or dynamic elements
                   - Ensure mobile-first optimization
                
                3. **Professional B2B Standards:**
                   - Maintain credibility and trust signals
                   - Use industry-appropriate imagery
                   - Include subtle brand elements
                   - Avoid overly promotional appearance
                
                4. **Technical Specifications:**
                   - Square format (1:1 ratio) optimized for LinkedIn feed
                   - High resolution and crisp details
                   - Professional color palette
                   - Consistent branding elements
                
                **Content Framework (AIDA Structure):**
                - **Attention:** Hook element that grabs immediate focus
                - **Interest:** Visual representation of the value proposition
                - **Desire:** Outcome visualization or benefit illustration
                - **Action:** Clear, compelling CTA placement
                
                **Required Visual Elements:**
                - Main focal point that represents the core benefit
                - Supporting graphics or icons that enhance understanding
                - Professional color scheme aligned with brand
                - Clear typography hierarchy
                - Strategic white space usage
                - Mobile-optimized text size and placement
                
                Generate a detailed, specific DALL-E prompt that will create a high-performing LinkedIn ad image following these proven frameworks and best practices.
                """,
            )

            prompt = prompt_template.format(
                style=style.value,
                company_url=request.company_url,
                product_name=request.product_name,
                business_value=request.business_value,
                audience=request.audience,
                body_text=request.body_text,
                footer_text=request.footer_text,
                analysis=json.dumps(analysis),
                visual_approach=style_config["visual_approach"],
                composition=style_config["composition"],
                elements=style_config["elements"],
            )

            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            prompts[style.value] = response.content

        state["generated_prompts"] = prompts
        return state

    async def optimize_prompts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize prompts using advanced LinkedIn ad performance techniques"""
        prompts = state["generated_prompts"]
        request = state["request"]
        analysis = state["company_analysis"]
        optimized_prompts = {}

        for style, prompt in prompts.items():
            optimization_template = PromptTemplate(
                input_variables=[
                    "original_prompt",
                    "style",
                    "company_analysis",
                    "audience",
                ],
                template="""
                As a LinkedIn advertising expert, optimize this DALL-E prompt using proven high-performance techniques:
                
                **Original Prompt:** {original_prompt}
                **Style:** {style}
                **Target Audience:** {audience}
                **Company Analysis:** {company_analysis}
                
                **Optimization Framework - Apply These Proven Techniques:**
                
                1. **SpeedWork Social Performance Rules:**
                   - Ensure text occupies less than 50% of image space
                   - Create highly eye-catching and extremely relevant visuals
                   - Design for immediate attention capture (1-2 seconds)
                   - Optimize for mobile viewing experience
                
                2. **Advanced Visual Psychology:**
                   - Use directional cues that guide eyes toward CTA
                   - Implement color psychology for B2B trust building
                   - Create visual contrast that makes text pop
                   - Include subtle motion or dynamic elements
                
                3. **B2B LinkedIn Optimization:**
                   - Incorporate industry-specific visual metaphors
                   - Add credibility signals (charts, data, professional imagery)
                   - Use authentic, diverse professional representation
                   - Balance innovation with trustworthiness
                
                4. **Technical Enhancement:**
                   - Specify exact typography hierarchy
                   - Define precise color codes and gradients
                   - Detail lighting and shadow specifications
                   - Include texture and material descriptions
                
                5. **Engagement Maximization:**
                   - Add elements that create curiosity gaps
                   - Include visual representations of outcomes/benefits
                   - Use social proof visual cues where appropriate
                   - Create thumb-stopping appeal without being clickbait
                
                **Enhanced Prompt Requirements:**
                - Start with specific artistic style and technique
                - Include detailed composition and layout instructions
                - Specify exact color palette and typography
                - Add lighting, texture, and material details
                - Include specific element placement and sizing
                - End with technical specifications (resolution, format)
                
                Return ONLY the optimized, highly detailed DALL-E prompt that incorporates these performance-driven enhancements.
                """,
            )

            optimization_prompt = optimization_template.format(
                original_prompt=prompt,
                style=style,
                company_analysis=json.dumps(analysis),
                audience=request.audience,
            )

            response = await self.llm.ainvoke(
                [HumanMessage(content=optimization_prompt)]
            )
            optimized_prompts[style] = response.content

        state["optimized_prompts"] = optimized_prompts
        return state

    async def finalize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate images using DALL-E 3"""
        import uuid

        from openai import AsyncOpenAI

        from models import GeneratedImage, ImageStyle

        request = state["request"]
        enhanced_prompts = state.get("enhanced_prompts", [])

        # Initialize OpenAI client
        client = AsyncOpenAI()
        generated_images = []

        # Generate images for each style
        styles = [
            ImageStyle.PROFESSIONAL,
            ImageStyle.MODERN,
            ImageStyle.CREATIVE,
            ImageStyle.MINIMALIST,
            ImageStyle.BOLD,
        ]

        for i, style in enumerate(styles):
            try:
                # Use enhanced prompt if available, otherwise use fallback
                if i < len(enhanced_prompts):
                    prompt = enhanced_prompts[i]
                else:
                    # Fallback prompt
                    prompt = f"Professional LinkedIn ad image for {request.product_name}, {style.value} style, high quality, business professional"

                # Generate image with DALL-E 3
                response = await client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )

                # Create GeneratedImage object
                image = GeneratedImage(
                    id=str(uuid.uuid4()),
                    url=response.data[0].url,
                    style=style,
                    prompt_used=prompt,
                    request_id="",  # Will be set later
                    company_url=request.company_url,
                    product_name=request.product_name,
                    business_value=request.business_value,
                    audience=request.audience,
                )

                generated_images.append(image)

            except Exception as e:
                print(f"Error generating image for style {style.value}: {e}")
                # Create placeholder image
                placeholder_image = GeneratedImage(
                    id=str(uuid.uuid4()),
                    url="https://via.placeholder.com/1024x1024/4A90E2/FFFFFF?text=LinkedIn+Ad",
                    style=style,
                    prompt_used=f"Placeholder for {style.value} style",
                    request_id="",
                    company_url=request.company_url,
                    product_name=request.product_name,
                    business_value=request.business_value,
                    audience=request.audience,
                )
                generated_images.append(placeholder_image)

        state["generated_images"] = generated_images
        state["status"] = "completed"
        state["workflow_complete"] = True
        return state

    async def run_workflow(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """Execute the complete workflow"""
        initial_state = {"request": request, "status": "started"}

        result = await self.graph.ainvoke(initial_state)
        return result


# Global workflow instance
image_workflow = ImageGenerationWorkflow()

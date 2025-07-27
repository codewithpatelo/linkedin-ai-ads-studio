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

        # Add nodes
        workflow.add_node("analyze_company", self.analyze_company)
        workflow.add_node("generate_prompts", self.generate_prompts)
        workflow.add_node("optimize_prompts", self.optimize_prompts)
        workflow.add_node("finalize", self.finalize)

        # Add edges
        workflow.add_edge("analyze_company", "generate_prompts")
        workflow.add_edge("generate_prompts", "optimize_prompts")
        workflow.add_edge("optimize_prompts", "finalize")
        workflow.add_edge("finalize", END)

        # Set entry point
        workflow.set_entry_point("analyze_company")

        return workflow.compile()

    async def analyze_company(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company information to extract key insights"""
        request: ImageGenerationRequest = state["request"]

        analysis_prompt = PromptTemplate(
            input_variables=[
                "company_url",
                "product_name",
                "business_value",
                "audience",
            ],
            template="""
            Analyze the following company information and extract key insights for LinkedIn ad image generation:
            
            Company URL: {company_url}
            Product: {product_name}
            Business Value: {business_value}
            Target Audience: {audience}
            
            Please provide:
            1. Industry sector and company type
            2. Key visual elements that would represent this company
            3. Color palette suggestions based on the industry
            4. Tone and style recommendations
            5. Key messaging themes
            
            Return your analysis in JSON format.
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

    async def generate_prompts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized prompts for each image style"""
        request: ImageGenerationRequest = state["request"]
        analysis = state["company_analysis"]

        prompts = {}

        for style in ImageStyle:
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
                ],
                template="""
                Create a detailed DALL-E prompt for a LinkedIn advertisement image with the following specifications:
                
                Style: {style}
                Company: {company_url}
                Product: {product_name}
                Value Proposition: {business_value}
                Target Audience: {audience}
                Ad Body: {body_text}
                Call to Action: {footer_text}
                
                Company Analysis: {analysis}
                
                Generate a comprehensive prompt that includes:
                - Visual composition and layout
                - Color scheme and typography
                - Imagery and graphics style
                - Professional LinkedIn ad format
                - Brand-appropriate elements
                - Target audience appeal
                
                The image should be 1200x627 pixels (LinkedIn ad format) and highly engaging.
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
            )

            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            prompts[style.value] = response.content

        state["generated_prompts"] = prompts
        return state

    async def optimize_prompts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize prompts for better image generation results"""
        prompts = state["generated_prompts"]
        optimized_prompts = {}

        for style, prompt in prompts.items():
            optimization_template = PromptTemplate(
                input_variables=["original_prompt", "style"],
                template="""
                Optimize the following DALL-E prompt for better image generation results:
                
                Original Prompt: {original_prompt}
                Style: {style}
                
                Make the prompt more specific, detailed, and likely to produce high-quality results.
                Focus on:
                - Clear visual descriptions
                - Professional LinkedIn ad aesthetics
                - Specific artistic techniques
                - Composition guidelines
                - Technical specifications
                
                Return only the optimized prompt.
                """,
            )

            optimization_prompt = optimization_template.format(
                original_prompt=prompt, style=style
            )

            response = await self.llm.ainvoke(
                [HumanMessage(content=optimization_prompt)]
            )
            optimized_prompts[style] = response.content

        state["optimized_prompts"] = optimized_prompts
        return state

    async def finalize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the workflow and prepare results"""
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

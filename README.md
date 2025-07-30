# 🚀 AI-Powered LinkedIn Ads Image Generation Studio

![UX](gui.gif)

An AI-powered image generation platform that creates professional LinkedIn advertisement images with real-time streaming progress, enhanced prompt generation, and professional ad copy enhancement.

The UX is simple. Users fill out a form with product name, company URL, target audience and business values. The user has the option to specify the body text and footer text. Then, a fully-automated ad generation pipeline does the magic.

The pipeline is as follows:

1. 🔍 **Company Analysis**: Based on user input, the system analyzes the company to understand their brand and context.
2. 🖼️ **Reference Loading**: The system loads 3-5 LinkedIn ad examples to improve generation quality.
3. ✨ **Prompt Enhancement**: The system generates an optimized prompt to improve the quality of the generated images based on company analysis.
4. 📝 **Ad Copy Generation**: If user doesn't provide body text and footer text, the system generates them based on company analysis.
5. 🎨 **Image Generation**: The system uses optimized prompts to generate 5 ad images using IMAGE-GPT-1 with different styles and reference image integration.
6. 🔄 **Image Modification**: The system modifies the images to improve the quality of the generated images.

## ⚡ Quick Setup
To make things easy. We used MAKEFILES.

At root level, just do:

```bash
make setup
```
Make sure to add FE .env and BE .env file with OPENAI API KEYS. Optionally, you can enable Langsmith which is fully supported in this repository.

Then:

```bash
make quick-dev
```


## 📁 Project Structure

```
linkedin-ads/
├── LICENSE                     # MIT License
├── Makefile                    # Root-level build automation
├── README.md                   # Project documentation
├── docker-compose.yml          # Production Docker setup
├── docker-compose.dev.yml      # Development Docker setup
│
├── be/                         # Backend (FastAPI + Python 3.11)
│   ├── Dockerfile              # Backend container configuration
│   ├── Makefile                # Backend build automation
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models for API
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── datasets/
│   │   └── ref_imgs/           # Reference LinkedIn ad images (26 examples)
│   │       ├── main_ref.jpg    # Primary reference image
│   │       ├── main_ref2.jpg   # Additional main references
│   │       └── *.png           # Various LinkedIn ad examples
│   ├── routers/
│   │   ├── image_generation.py # Standard image generation API
│   │   └── streaming.py        # Real-time streaming API with SSE
│   └── services/
│       ├── image_service.py    # Core business logic 
│       └── langgraph_workflow.py # Workflow definitions
│
└── fe/                         # Frontend (React + TypeScript + Vite)
    ├── Dockerfile              # Frontend container configuration
    ├── Makefile                # Frontend build automation
    ├── package.json            # Node.js dependencies
    ├── package-lock.json       # Dependency lock file
    ├── bun.lockb               # Bun package manager lock
    ├── components.json         # shadcn/ui configuration
    ├── eslint.config.js        # ESLint configuration
    ├── postcss.config.js       # PostCSS configuration
    ├── index.html              # HTML entry point
    ├── nginx.conf              # Production nginx configuration
    ├── public/
    │   ├── favicon.ico
    │   ├── placeholder.svg
    │   └── robots.txt
    └── src/
        ├── App.tsx             # Main application component
        ├── App.css             # Global styles
        ├── main.tsx            # React entry point
        ├── index.css           # Base styles
        ├── vite-env.d.ts       # TypeScript definitions
        ├── components/
        │   ├── CompanyForm.tsx # Form for input data
        │   ├── ImageGallery.tsx# Generated images display
        │   ├── Sidebar.tsx     # Console view with real-time progress
        │   ├── AdPreview.tsx   # LinkedIn-style ad preview
        │   ├── PromptViewer.tsx# Enhanced prompts display
        │   └── ui/             # shadcn/ui components (49 components)
        │       ├── button.tsx
        │       ├── input.tsx
        │       ├── textarea.tsx
        │       └── ... (46 more UI components)
        ├── hooks/
        │   ├── useImageGeneration.ts # Main generation logic
        │   ├── use-toast.ts    # Toast notifications
        │   └── use-mobile.tsx  # Mobile detection
        ├── pages/
        │   ├── Index.tsx       # Main application page
        │   └── NotFound.tsx    # 404 error page
        └── services/
            └── api.ts          # API client with streaming support
```

## ✨ Features

### 🔧 Core Functionality
- **Real-time Streaming**: Server-Sent Events (SSE) for live progress updates
- **AI-Enhanced Prompts**: GPT-4o powered prompt optimization with reference images
- **Professional Ad Copy**: Auto-generated headlines, descriptions, and CTAs
- **5 Image Styles**: Professional, Modern, Creative, Minimalist, Bold
- **Console View**: Developer-friendly sidebar with real-time generation progress
- **Image Modification**: Re-generate specific images with custom feedback

### Backend (FastAPI + Python 3.11)
- **Streaming API**: `/api/v1/stream/generate` with real-time progress
- **LangGraph Workflow**: Multi-step AI pipeline for company analysis and prompt enhancement
- **Reference Images**: Loads 3-5 LinkedIn ad examples to improve generation quality
- **OpenAI IMAGE-GPT-1**: Advanced multimodal image generation with reference image integration
- **Async Processing**: Concurrent operations with proper rate limiting

### Frontend (React + TypeScript + Vite)
- **Modern UI**: Clean, professional interface with shadcn/ui components
- **Sidebar Console**: Terminal-style progress view with enhanced prompts display
- **Real-time Updates**: Live streaming of generation steps and AI-enhanced prompts
- **Image Gallery**: Professional display with modification options
- **Form Validation**: Comprehensive input validation and error handling

### 🔌 API Endpoints
- `POST /api/v1/stream/generate` - **Streaming generation** with real-time progress (recommended)
- `POST /api/v1/images/generate` - Standard generation endpoint
- `POST /api/v1/images/modify` - Modify existing images with feedback
- `GET /api/v1/images/styles` - Get available image styles
- `GET /api/v1/images/request/{request_id}` - Retrieve generated images
- `DELETE /api/v1/images/request/{request_id}` - Delete stored images

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key with IMAGE-GPT-1 access


### Access Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Technical Approach

### 🏗️ Architecture Decisions

1. **🔄 Real-time Streaming Architecture**
   - Server-Sent Events (SSE) for live progress updates
   - Async streaming with proper error handling and connection management
   - Frontend state management for real-time UI updates

2. **🧠 AI-First Design**
   - **Workflow-Based**: Multi-step AI pipeline (company analysis → reference loading → optimized prompt generation → image generation)
   - **GPT-4o Integration**: Advanced prompt optimization with context awareness
   - **Reference Image System**: Uses 3-5 LinkedIn ad examples to improve generation quality
   - **Fallback Mechanisms**: Graceful degradation when AI services are unavailable

3. **💻 Modern Frontend Architecture**
   - **React + TypeScript**: Type-safe component architecture
   - **Custom Hooks**: Centralized state management with `useImageGeneration`
   - **Sidebar Console**: Developer-friendly real-time progress display
   - **Component Separation**: Clear separation between form, gallery, and streaming components

4. **Performance & UX Optimization**
   - **Concurrent Processing**: Parallel image generation with rate limiting
   - **Progressive Enhancement**: Works without streaming, enhanced with real-time updates
   - **Memory Efficiency**: Optimized reference image loading and base64 encoding
   - **Error Boundaries**: Comprehensive error handling with user-friendly messages

### Key Design Patterns

- **Observer Pattern**: Real-time streaming updates with SSE
- **Strategy Pattern**: Multiple image styles and prompt enhancement strategies (self-reflection inspired)
- **Service Layer**: Clean separation between API routes and business logic
- **Custom Hooks**: React state management with `useImageGeneration`
- **Component Composition**: Modular UI components with clear responsibilities

## 🖼️ Visual Examples

### Generated Images by Style

#### Professional Style
<img src="be/static/professional_c5f7e5d6.png" alt="Professional Style Example" width="300" height="300">

*Clean, professional business person with high contrast background for text overlay*

#### Modern Style
<img src="be/static/modern_05c3fcb6.png" alt="Modern Style Example" width="300" height="300">

*Contemporary professional with tech-forward styling on minimalist backdrop*

#### Creative Style
<img src="be/static/creative_de42e3ef.png" alt="Creative Style Example" width="300" height="300">

*Expressive professional with artistic but business-appropriate styling*

#### Minimalist Style
<img src="be/static/minimalist_f34b3df8.png" alt="Minimalist Style Example" width="300" height="300">

*Ultra-clean portrait with maximum simplicity and negative space*

#### Bold Style
<img src="be/static/bold_301f2e62.png" alt="Bold Style Example" width="300" height="300">

*Confident professional with strong visual impact on high-contrast background*

### Modified Images

#### Original → Modified
<img src="be/static/modified_e3d0c320.png" alt="Modified Image Example" width="300" height="300">

*Example of image modification based on user feedback - maintains professional quality while incorporating requested changes*

### Reference Image
<img src="be/static/main_ref.jpg" alt="Reference Image" width="300" height="200">

*Example LinkedIn ad reference used to guide generation style and composition*

### Image URLs Structure

Generated images are served via FastAPI static files:

```
# Generated Images (by style)
http://localhost:8000/static/professional_c5f7e5d6.png
http://localhost:8000/static/modern_05c3fcb6.png
http://localhost:8000/static/creative_de42e3ef.png
http://localhost:8000/static/minimalist_f34b3df8.png
http://localhost:8000/static/bold_301f2e62.png

# Modified Images
http://localhost:8000/static/modified_e3d0c320.png
http://localhost:8000/static/modified_58fe6197.png


```

**Naming Convention:**
- **Generated**: `{style}_{uuid8}.png` (e.g., `professional_c5f7e5d6.png`)
- **Modified**: `modified_{uuid8}.png` (e.g., `modified_e3d0c320.png`)
- **Reference**: `main_ref.jpg`, `ref_2.jpg`, etc.

---

## 📝 API Usage Examples

### 🖼️ Generate Images Request
```json
{
  "company_url": "https://superhuman.com/",
  "product_name": "AI powered Email",
  "business_value": "Reply to Your Customers Faster",
  "audience": "Director of Sales, VP of Sales, Head of Sales",
  "body_text": "Slow response times and missed emails weaken trust...",
  "footer_text": "Boost Client Trust: Respond to Emails 3x Faster!"
}
```

### Response
```json
{
  "request_id": "uuid-here",
  "images": [
    {
      "id": "image-uuid",
      "url": "https://generated-image-url",
      "style": "professional",
      "prompt_used": "Detailed prompt...",
      "generation_timestamp": "2024-01-01T00:00:00"
    }
  ],
  "status": "success",
  "message": "Successfully generated 5 images"
}
```

### 🎯 Enhanced Prompt Example

Here's an example of how the AI enhances a simple user input into a detailed, optimized prompt for IMAGE-GPT-1:

**Original User Input:**
- Product: "AI powered Email"
- Audience: "Sales Managers"
- Style: "Professional"

**Enhanced Prompt for IMAGE-GPT-1:**

```
Create a professional LinkedIn ad image of a confident sales manager, a middle-aged woman of diverse ethnicity, dressed in a navy blue blazer, smiling warmly while engaging with a sleek digital dashboard displaying sales metrics. The background should be a simple, high-contrast solid light gray color, ensuring the subject stands out prominently. Use studio lighting to create a warm and inviting atmosphere, highlighting the professionalism and approachability of the subject. 

The image composition should focus on the upper body of the sales manager, shot on a Canon 5D with a 50mm lens, utilizing a shallow depth of field to keep the attention on her. Reserve 30% of the image space in the bottom third for a bold CTA text area, ensuring a contrast ratio of at least 4.5:1 for accessibility. This text overlay should say 'Buy now' in bright orange font, positioned against the light gray background for maximum visibility. 

Emphasize B2B credibility through her confident posture and authentic expression, showcasing the innovative spirit of SuperTiki's AI-powered mailing solution. Optimize the image for mobile viewing with a clear visual hierarchy, ensuring thumb-stopping appeal while maintaining a professional tone suitable for sales managers. Include elements that subtly suggest boldness, such as upward-trending graphs or metrics in the background, enhancing the overall context of efficiency and innovation

IMPORTANT: Generate image in exactly 1024x1024 pixels resolution. Ensure proper aspect ratio and high quality.
```

**Key Enhancement Features:**
- 🎯 **Specific Demographics**: Detailed person description for better targeting
- 🎨 **Technical Specifications**: Camera settings, lighting, composition details
- 📱 **Mobile Optimization**: Clear visual hierarchy and thumb-stopping appeal
- ♿ **Accessibility**: Contrast ratios and text overlay considerations
- 🎪 **Brand Context**: Integration of product benefits and audience needs
- 📏 **Resolution Guardrails**: Explicit size requirements for consistency

---

## 🔑 Key Decisions & Trade-offs

### 🛠️ Technical Decisions
1. **Real-time Streaming**: Chose SSE over WebSockets for simplicity and better browser compatibility
2. **In-memory Storage**: Prioritized development speed over persistence (production would use database)
3. **Reference Images**: Local file system storage for MVP, cloud storage for production
4. **Component Architecture**: Sidebar overlay vs separate pages for better UX continuity

### ⚖️ Trade-offs Made
1. **Streaming vs Simplicity**: Traded some simplicity for better user experience
2. **AI Enhancement vs Speed**: Slower generation for higher quality prompts
3. **Console View vs Simple UI**: Developer-friendly interface (more appropiate for a tech demo) over production-ready design
4. **Type Safety vs Development Speed**: Full TypeScript for maintainability
5. **Git Commit History Lost**: Given that I started vibe coding both FE (with Lovable) and BE (with Windsurf) some of the first commits are lost. This is because I created a new repository integrating both parts. This made development lightning fast but I sacrificed some commit history.
6. **Quickness vs Code Structure Robustness**: For the sake of quickness and delivery I made a simplified code structure. Normally, for FE I'd implement a feature-based approach where each feature has it's own page, hook, services, etc. Similarly, for the BE I'd use something onionish to separate domain and infrastructure concerns. 


### 🔮 Assumptions
- Users have valid OpenAI API keys with IMAGE-GPT-1 access
- LinkedIn ad format requirements (1:1 or 4:5 aspect ratios)
- Modern browser support for SSE and ES6+ features
- Development environment with Python 3.11+ and Node.js 18+

### 🚧 Current Limitations
1. **IMAGE-GPT-1 text handling**: While IMAGE-GPT-1 has improved multimodal capabilities compared to DALL-E 3, complex text overlays may still benefit from post-processing with tools like Pillow for optimal text placement.
2. **Prompt engineering optimized for people**: Current style descriptions are optimized for generating professional people rather than products, objects, or other characters. This is easily adjustable through prompt engineering modifications.
3. **No persistent storage**: Images stored in memory only
4. **Some steps take long**: Some steps take longer than others, which can lead to a bad user experience. Cache, token optimization, and parallelization are some solutions to this problem.
5. **Local reference images**: Limited to pre-loaded examples
6. **No image caching**: Each request generates fresh images
7. **Rate limiting**: Basic OpenAI API limits only
8. **Modification feature**: While we take the original image as input, IMAGE-GPT-1's multimodal approach provides better consistency but may still vary the image due to the generative nature of the model.


## 🚀 Future Enhancements

1. **🔗 LinkedIn Campaign Manager Integration**: Use LinkedIn Campaign Manager to create and manage campaigns
2. **⚡ Caching**: Redis for frequently requested data
3. **🔄 Background Processing**: Celery for async image generation
4. **📝 Add texts to images**: Use pillow to add high-contrast texts to images
5. **📊 Advanced Analytics**: LangSmith integration for prompt performance
6. **🕸️ Web Scraping**: Automated company information extraction
7. **🔬 A/B Testing**: Comparison and production of multiple prompt strategies, multiple CTAs, multiple body texts
8. **📡 OpenAI Streaming for Image Generation**: Implement OpenAI's streaming API to show real-time progress during image generation, providing users with live updates on generation status
9. **👁️ Computer Vision Spell Checking**: Integrate computer vision technology (OCR + spell checking) to automatically detect spelling errors in generated images and trigger automatic re-modification to correct them

## 🔍 Review Focus Points

1. **⚡ Real-time Architecture**: Streaming implementation and frontend constant visual feedback
2. **🧠 AI Integration**: Workflow design and GPT-4o prompt optimization
3. **🧩 Types-based Design**: TypeScript and Pydantic usage
4. **👤 User Experience**: Sidebar console design and real-time progress feedback
5. **✅ Code Quality**: Clean separation of concerns and maintainable structure
6. **🛡️ Error Handling**: Graceful degradation and comprehensive error handling

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI with Python 3.11+
- **AI/ML**: LangChain, LangGraph, OpenAI IMAGE-GPT-1 + GPT-4o
- **Streaming**: Server-Sent Events (SSE) with async generators
- **HTTP**: aiohttp for async HTTP operations

### Frontend  
- **Framework**: React 18 + TypeScript + Vite
- **UI Components**: shadcn/ui + Tailwind CSS
- **Icons**: Lucide React
- **Notifications**: Sonner toast library
- **State Management**: Custom hooks with React state

### 👨‍💻 Development
- **Code Quality**: ESLint, Prettier, TypeScript strict mode
- **API Client**: Custom service layer with streaming support
- **Environment**: Node.js 18+, Python 3.11+
- **Validation**: Pydantic
- **Documentation**: FastAPI automatic OpenAPI docs


# AI-Powered LinkedIn Ads Image Generation Studio

![UX](gui.gif)

An AI-powered image generation platform that creates professional LinkedIn advertisement images with real-time streaming progress, enhanced prompt generation, and professional ad copy enhancement.

The UX is simple. Users fill out a form with product name, company URL, target audience and business values. The user has the option to specify the body text and footer text. Then, a fully-automated ad generation pipeline does the magic.

The pipeline is as follows:

1. Company Analysis: Based on user input, the system analyzes the company to understand their brand and context.
2. Reference Loading: The system loads 3-5 LinkedIn ad examples to improve generation quality.
3. Prompt Enhancement: The system generates an optimized prompt to improve the quality of the generated images based on company analysis.
4. Image Generation: The system uses optimized prompts to generate 5 ad images using DALL-E 3 with different styles.
5. Image Modification: The system modifies the images to improve the quality of the generated images.

## Quick Setup
To make things easy. We used MAKEFILES.

At root level, just do:

```bash
make setup
```
Make sure to add .env file with OPENAI API KEYS.

Then:

```bash
make quick-dev
```


## Project Structure

```
linkedin-ads/
├── LICENSE                     # MIT License
├── Makefile                    # Root-level build automation
├── README.md                   # Project documentation
├── docker-compose.yml          # Production Docker setup
├── docker-compose.dev.yml      # Development Docker setup
├── debug_storage.py            # Debug utilities
│
├── be/                         # Backend (FastAPI + Python 3.11)
│   ├── Dockerfile              # Backend container configuration
│   ├── Makefile                # Backend build automation
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models for API
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── start.sh                # Production startup script
│   ├── datasets/
│   │   └── ref_imgs/           # Reference LinkedIn ad images (26 examples)
│   │       ├── main_ref.jpg    # Primary reference image
│   │       ├── main_ref2.jpg   # Additional main references
│   │       └── *.png           # Various LinkedIn ad examples
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── image_generation.py # Standard image generation API
│   │   └── streaming.py        # Real-time streaming API with SSE
│   └── services/
│       ├── __init__.py
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

## Features

### Core Functionality
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
- **OpenAI DALL-E 3**: High-quality image generation with fallback handling
- **Async Processing**: Concurrent operations with proper rate limiting

### Frontend (React + TypeScript + Vite)
- **Modern UI**: Clean, professional interface with shadcn/ui components
- **Sidebar Console**: Terminal-style progress view with enhanced prompts display
- **Real-time Updates**: Live streaming of generation steps and AI-enhanced prompts
- **Image Gallery**: Professional display with modification options
- **Form Validation**: Comprehensive input validation and error handling

### API Endpoints
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
- OpenAI API key with DALL-E 3 access


### Access Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Technical Approach

### Architecture Decisions

1. **Real-time Streaming Architecture**
   - Server-Sent Events (SSE) for live progress updates
   - Async streaming with proper error handling and connection management
   - Frontend state management for real-time UI updates

2. **AI-First Design**
   - **Workflow-Based**: Multi-step AI pipeline (company analysis → reference loading → optimized prompt generation → image generation)
   - **GPT-4o Integration**: Advanced prompt optimization with context awareness
   - **Reference Image System**: Uses 3-5 LinkedIn ad examples to improve generation quality
   - **Fallback Mechanisms**: Graceful degradation when AI services are unavailable

3. **Modern Frontend Architecture**
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

## Example Usage

### Generate Images Request
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

## Key Decisions & Trade-offs

### Technical Decisions
1. **Real-time Streaming**: Chose SSE over WebSockets for simplicity and better browser compatibility
2. **In-memory Storage**: Prioritized development speed over persistence (production would use database)
3. **Reference Images**: Local file system storage for MVP, cloud storage for production
4. **Component Architecture**: Sidebar overlay vs separate pages for better UX continuity

### Trade-offs Made
1. **Streaming vs Simplicity**: Added complexity for better user experience
2. **AI Enhancement vs Speed**: Slower generation for higher quality prompts
3. **Console View vs Simple UI**: Developer-friendly interface over simplified design
4. **Type Safety vs Development Speed**: Full TypeScript for maintainability
5. **Git Commit History Lost**: Given that I started vibe coding both FE (with Lovable) and BE (with Windsurf) some of the first commits are lost. This is because I created a new repository integrating both parts. This made development quicker but I sacrificed some commit history.


### Assumptions
- Users have valid OpenAI API keys with DALL-E 3 access
- LinkedIn ad format requirements (1:1 or 4:5 aspect ratios)
- Modern browser support for SSE and ES6+ features
- Development environment with Python 3.11+ and Node.js 18+

### Current Limitations
1. **DALL-E struggles with texts**: DALL-E 3 is not designed to handle complex text-based prompts, which can lead to suboptimal results. A tweak to solve this for further iterations is to complement DALL-E with something like pillow to add those texts.
2. **No persistent storage**: Images stored in memory only
3. **Some steps take long**: Some steps take longer than others, which can lead to a bad user experience. Cache, token optimization, and parallelization are some solutions to this problem.
4. **Local reference images**: Limited to pre-loaded examples
5. **No image caching**: Each request generates fresh images
6. **Rate limiting**: Basic OpenAI API limits only
7. **Modification feature**: While we take the original image as input, DALL-E 3 will probably vary the image considerably due to its own limitations.


## Future Enhancements

1. **LinkedIn Campaign Manager Integration**: Use LinkedIn Campaign Manager to create and manage campaigns
2. **Caching**: Redis for frequently requested data
3. **Background Processing**: Celery for async image generation
4. **Add texts to images**: Use pillow to add high-contrast texts to images
5. **Advanced Analytics**: LangSmith integration for prompt performance
6. **Web Scraping**: Automated company information extraction
7. **A/B Testing**: Multiple prompt strategies comparison

## Review Focus Points

1. **Real-time Architecture**: SSE streaming implementation and frontend state management
2. **AI Integration**: Workflow design and GPT-4o prompt optimization
3. **Component Design**: React component architecture and TypeScript usage
4. **User Experience**: Sidebar console design and real-time progress feedback
5. **Code Quality**: Clean separation of concerns and maintainable structure
6. **Error Handling**: Graceful degradation and comprehensive error boundaries
7. **Performance**: Async processing, memory efficiency, and concurrent operations

## Technology Stack

### Backend
- **Framework**: FastAPI with Python 3.11+
- **AI/ML**: LangChain, LangGraph, OpenAI DALL-E 3 + GPT-4o
- **Streaming**: Server-Sent Events (SSE) with async generators
- **HTTP**: aiohttp for async HTTP operations

### Frontend  
- **Framework**: React 18 + TypeScript + Vite
- **UI Components**: shadcn/ui + Tailwind CSS
- **Icons**: Lucide React
- **Notifications**: Sonner toast library
- **State Management**: Custom hooks with React state

### Development
- **Code Quality**: ESLint, Prettier, TypeScript strict mode
- **API Client**: Custom service layer with streaming support
- **Environment**: Node.js 18+, Python 3.11+
- **Validation**: Pydantic
- **Documentation**: FastAPI automatic OpenAPI docs


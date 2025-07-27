# LinkedIn Ads Image Generation Studio

An AI-powered image generation platform that creates professional LinkedIn advertisement images with real-time streaming progress, enhanced prompt generation, and professional ad copy creation.

## Quick Setup

**Backend**: `cd be && python3.11 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`  
**Frontend**: `cd fe && npm run dev`  
**Environment**: Add `OPENAI_API_KEY` to `be/.env`

## Project Structure

```
linkedin-ads/
├── be/                          # Backend (FastAPI + Python 3.11)
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models for API
│   ├── requirements.txt        # Python dependencies
│   ├── datasets/ref_imgs/      # Reference LinkedIn ad images
│   ├── routers/
│   │   ├── image_generation.py # Standard image generation API
│   │   └── streaming.py        # Real-time streaming API
│   └── services/
│       └── image_service.py    # Core business logic with LangGraph
└── fe/                         # Frontend (React + TypeScript + Vite)
    ├── src/
    │   ├── components/         # UI components
    │   │   ├── CompanyForm.tsx # Form for input data
    │   │   ├── ImageGallery.tsx# Generated images display
    │   │   └── Sidebar.tsx     # Console view with real-time progress
    │   ├── hooks/
    │   │   └── useImageGeneration.ts # Main generation logic
    │   └── services/
    │       └── api.ts          # API client with streaming support
    └── package.json
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
- **Image Gallery**: Professional display with download and modification options
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

### Backend Setup
1. **Install dependencies**:
   ```bash
   cd be
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

3. **Run backend**:
   ```bash
   python3.11 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. **Install dependencies**:
   ```bash
   cd fe
   npm install
   ```

2. **Run frontend**:
   ```bash
   npm run dev
   ```

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
   - **LangGraph Workflow**: Multi-step AI pipeline (company analysis → reference loading → prompt enhancement → image generation)
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
- **Strategy Pattern**: Multiple image styles and prompt enhancement strategies
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

### Assumptions
- Users have valid OpenAI API keys with DALL-E 3 access
- LinkedIn ad format requirements (1:1 or 4:5 aspect ratios)
- Modern browser support for SSE and ES6+ features
- Development environment with Python 3.11+ and Node.js 18+

### Current Limitations
1. **No persistent storage**: Images stored in memory only
2. **No user authentication**: Open API without access controls  
3. **Local reference images**: Limited to pre-loaded examples
4. **No image caching**: Each request generates fresh images
5. **Rate limiting**: Basic OpenAI API limits only

## Future Enhancements

1. **Database Integration**: PostgreSQL with image metadata storage
2. **User Authentication**: JWT-based auth system
3. **Image Caching**: Redis for frequently requested image types
4. **Background Processing**: Celery for async image generation
5. **Advanced Analytics**: LangSmith integration for prompt performance
6. **Web Scraping**: Automated company information extraction
7. **A/B Testing**: Multiple prompt strategies comparison

## Review Focus Points

1. **Real-time Architecture**: SSE streaming implementation and frontend state management
2. **AI Integration**: LangGraph workflow design and GPT-4o prompt optimization
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

## License

This project is part of a coding challenge for Kalos.

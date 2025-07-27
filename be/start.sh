#!/bin/bash

# LinkedIn Ads Image Generation Studio - Backend Startup Script

echo "🚀 Starting LinkedIn Ads Image Generation Studio Backend..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    echo "   Required: OPENAI_API_KEY"
    echo "   Optional: LANGCHAIN_API_KEY, LANGCHAIN_PROJECT"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "❌ OPENAI_API_KEY not configured in .env file"
    echo "📝 Please add your OpenAI API key to .env file"
    echo "   Format: OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌐 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Health check available at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py

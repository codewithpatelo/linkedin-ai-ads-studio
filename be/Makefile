.PHONY: help install dev test clean lint format check-env run build docker-build docker-run

# Default target
help:
	@echo "LinkedIn Ads Image Generation Studio - Backend"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install dependencies and setup virtual environment"
	@echo "  dev         - Run development server with hot reload"
	@echo "  run         - Run production server"
	@echo "  test        - Run API tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black"
	@echo "  check-env   - Check environment variables"
	@echo "  clean       - Clean up temporary files and cache"
	@echo "  build       - Build for production"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run Docker container"

# Install dependencies
install:
	@echo "Setting up virtual environment and installing dependencies..."
	python3.11 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Installation complete!"

# Development server with hot reload
dev: check-env
	@echo "Starting development server..."
	./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
run: check-env
	@echo "Starting production server..."
	./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

# Run API tests
test: check-env
	@echo "Running API tests..."
	./venv/bin/python test_api.py

# Lint code
lint:
	@echo "Running code linting..."
	./venv/bin/python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv
	./venv/bin/python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics --exclude=venv
	./venv/bin/python -m mypy . --ignore-missing-imports --exclude=venv

# Format code
format:
	@echo "Formatting code..."
	./venv/bin/python -m black . --line-length 88 --exclude=venv
	./venv/bin/python -m isort . --profile black --skip venv

# Check environment variables
check-env:
	@echo "Checking environment variables..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Please copy .env.example to .env and configure it."; \
		exit 1; \
	fi
	@if [ -z "$$OPENAI_API_KEY" ] && [ -z "$$(grep OPENAI_API_KEY .env | cut -d '=' -f2)" ]; then \
		echo "❌ OPENAI_API_KEY not set. Please configure it in .env file."; \
		exit 1; \
	fi
	@echo "✅ Environment variables OK"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Build for production
build: clean check-env
	@echo "Building for production..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt --no-cache-dir
	@echo "✅ Build complete"

# Docker build
docker-build:
	@echo "Building Docker image..."
	docker build -t linkedin-ads-backend .

# Docker run
docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 --env-file .env linkedin-ads-backend

# Quick setup for new developers
setup: install check-env
	@echo "🚀 Setup complete! You can now run 'make dev' to start the development server."

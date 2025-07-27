# Frontend Makefile for LinkedIn Ads Image Generation Studio

.PHONY: help install dev build preview lint format clean test

# Default target
help:
	@echo "LinkedIn Ads Frontend - Available commands:"
	@echo ""
	@echo "  setup     - Install dependencies"
	@echo "  dev       - Start development server"
	@echo "  build     - Build for production"
	@echo "  preview   - Preview production build"
	@echo "  lint      - Run ESLint"
	@echo "  format    - Format code with Prettier"
	@echo "  clean     - Clean build artifacts"
	@echo "  test      - Run tests"
	@echo ""

# Install dependencies
setup:
	@echo "📦 Installing frontend dependencies..."
	npm install
	@echo "✅ Frontend dependencies installed!"

# Start development server
dev:
	@echo "🚀 Starting frontend development server..."
	npm run dev

# Build for production
build:
	@echo "🏗️  Building frontend for production..."
	npm run build
	@echo "✅ Frontend build complete!"

# Preview production build
preview:
	@echo "👀 Starting production preview..."
	npm run preview

# Run linting
lint:
	@echo "🔍 Running ESLint..."
	npm run lint

# Format code
format:
	@echo "✨ Formatting code with Prettier..."
	npx prettier --write "src/**/*.{ts,tsx,js,jsx,css,md}"
	@echo "✅ Code formatted!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist
	rm -rf node_modules/.vite
	@echo "✅ Build artifacts cleaned!"

# Run tests
test:
	@echo "🧪 Running tests..."
	npm run test

# Quick development setup
quick-dev: setup dev

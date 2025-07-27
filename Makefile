.PHONY: help install dev prod test clean logs setup check-env build down restart

# Default target
help:
	@echo "LinkedIn Ads Image Generation Studio"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@echo "  setup       - Complete project setup (install dependencies)"
	@echo "  dev         - Start development environment"
	@echo "  prod        - Start production environment"
	@echo "  build       - Build all Docker images"
	@echo "  test        - Run all tests"
	@echo "  logs        - Show logs from all services"
	@echo "  down        - Stop all services"
	@echo "  restart     - Restart all services"
	@echo "  clean       - Clean up containers, images, and volumes"
	@echo "  check-env   - Check environment configuration"

# Complete project setup
setup:
	@echo "🚀 Setting up LinkedIn Ads Image Generation Studio..."
	@echo "Checking environment files..."
	@if [ ! -f be/.env ]; then \
		echo "Creating backend .env from example..."; \
		cp be/.env.example be/.env; \
		echo "⚠️  Please configure OPENAI_API_KEY in be/.env"; \
	fi
	@if [ ! -f fe/.env ]; then \
		echo "Creating frontend .env from example..."; \
		cp fe/.env.example fe/.env; \
	fi
	@echo "Installing backend dependencies..."
	cd be && make install
	@echo "Installing frontend dependencies..."
	cd fe && npm install
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Configure OPENAI_API_KEY in be/.env"
	@echo "2. Run 'make dev' to start development environment"

# Start development environment
dev: check-env
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build

# Start production environment
prod: check-env build
	@echo "🚀 Starting production environment..."
	docker-compose up -d

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "Testing backend..."
	cd be && make test
	@echo "✅ All tests passed!"

# Show logs
logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Restart services
restart: down
	@echo "🔄 Restarting services..."
	docker-compose up -d

# Clean up everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	cd be && make clean
	cd fe && rm -rf node_modules dist 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Check environment
check-env:
	@echo "🔍 Checking environment configuration..."
	@if [ ! -f be/.env ]; then \
		echo "❌ Backend .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -z "$$(grep OPENAI_API_KEY be/.env | cut -d '=' -f2 | tr -d ' ')" ]; then \
		echo "❌ OPENAI_API_KEY not configured in be/.env"; \
		exit 1; \
	fi
	@echo "✅ Environment configuration OK"

# Quick development start
quick-dev:
	@echo "⚡ Quick development start..."
	cd be && make dev &
	cd fe && npm run dev

# Show status
status:
	@echo "📊 Service Status:"
	@docker-compose ps

# View backend logs
logs-be:
	@docker-compose logs -f backend

# View frontend logs  
logs-fe:
	@docker-compose logs -f frontend

# Open application in browser
open:
	@echo "🌐 Opening application..."
	@command -v xdg-open >/dev/null && xdg-open http://localhost:3000 || \
	 command -v open >/dev/null && open http://localhost:3000 || \
	 echo "Please open http://localhost:3000 in your browser"

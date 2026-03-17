#!/bin/bash

# HR & Compliance RAG System - Deployment Script
# This script handles the complete deployment process

set -e  # Exit on error

echo "🚀 HR & Compliance RAG System - Deployment"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create .env file with required variables"
    echo "Copy .env.example and fill in your values"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build Docker images
echo ""
echo "📦 Building Docker images..."
docker-compose build

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check API health
echo ""
echo "🔍 Checking API health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  API is starting up, may take a few more seconds${NC}"
fi

# Display status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "Access your application:"
echo "  🌐 Frontend:  http://localhost:3000"
echo "  📡 API:       http://localhost:8000"
echo "  📖 API Docs:  http://localhost:8000/docs"
echo "  ❤️  Health:    http://localhost:8000/health"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
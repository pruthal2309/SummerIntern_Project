# HR & Compliance RAG System - Deployment Script (PowerShell)
# This script handles the complete deployment process for Windows

$ErrorActionPreference = "Stop"

Write-Host "🚀 HR & Compliance RAG System - Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    Write-Host "Please create .env file with required variables"
    Write-Host "Copy .env.example and fill in your values"
    exit 1
}

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker Compose is not installed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Building Docker images..." -ForegroundColor Yellow
docker-compose build

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check API health
Write-Host ""
Write-Host "🔍 Checking API health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  API is starting up, may take a few more seconds" -ForegroundColor Yellow
}

# Display status
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application:"
Write-Host "  🌐 Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📡 API:       http://localhost:8000" -ForegroundColor Cyan
Write-Host "  📖 API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ❤️  Health:    http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs:"
Write-Host "  docker-compose logs -f"
Write-Host ""
Write-Host "To stop services:"
Write-Host "  docker-compose down"
Write-Host ""
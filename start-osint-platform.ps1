# OSINT Intelligence Platform - Startup Script for Windows
# This script starts the complete OSINT platform with all monitoring services

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Display banner
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OSINT INTELLIGENCE PLATFORM STARTUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop
Write-Host "[1/7] Checking Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker Desktop is not running!" -ForegroundColor Red
        Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not installed or not accessible!" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host ""
Write-Host "[2/7] Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker Compose is not available!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker Compose check failed!" -ForegroundColor Red
    exit 1
}

# Load or create environment variables
Write-Host ""
Write-Host "[3/7] Setting up environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ Loading existing .env file" -ForegroundColor Green
} else {
    Write-Host "! Creating .env file from template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "✓ .env file created" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Please edit .env file to set strong passwords!" -ForegroundColor Yellow
        Write-Host "Press any key to continue or Ctrl+C to exit and edit .env first..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "WARNING: .env.example not found, using defaults" -ForegroundColor Yellow
    }
}

# Create required directories
Write-Host ""
Write-Host "[4/7] Creating required directories..." -ForegroundColor Yellow
$directories = @(
    "logs",
    "storage",
    "data",
    "wireshark-captures",
    "prometheus",
    "grafana/provisioning",
    "grafana/dashboards",
    "logstash/config",
    "logstash/pipeline",
    "logstash/patterns"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories ready" -ForegroundColor Green

# Pull latest images
Write-Host ""
Write-Host "[5/7] Pulling latest Docker images..." -ForegroundColor Yellow
Write-Host "This may take several minutes on first run..." -ForegroundColor Cyan
docker-compose pull
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some images failed to pull, continuing anyway..." -ForegroundColor Yellow
}

# Start services
Write-Host ""
Write-Host "[6/7] Starting OSINT Platform services..." -ForegroundColor Yellow
Write-Host "This may take a few minutes as services initialize..." -ForegroundColor Cyan
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to start services!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Red
    exit 1
}

# Wait for services to initialize
Write-Host ""
Write-Host "[7/7] Waiting for services to become healthy..." -ForegroundColor Yellow
Write-Host "This may take 30-60 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Check service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker-compose ps

# Display access information
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  OSINT PLATFORM STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  OSINT API:          http://localhost:8000" -ForegroundColor White
Write-Host "  API Documentation:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Kibana (Logs):      http://localhost:5601" -ForegroundColor White
Write-Host "  Grafana (Metrics):  http://localhost:3001" -ForegroundColor White
Write-Host "  Prometheus:         http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "  Flower (Celery):    http://localhost:5555" -ForegroundColor White
Write-Host "  Wireshark:          http://localhost:3010" -ForegroundColor White
Write-Host "  cAdvisor:           http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Default Credentials:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  Grafana:  admin / admin (change in .env)" -ForegroundColor White
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  View logs:     docker-compose logs -f [service]" -ForegroundColor White
Write-Host "  Stop platform: .\stop-osint-platform.ps1" -ForegroundColor White
Write-Host "  Check health:  .\health-check.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Notes:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  - All services are running in detached mode" -ForegroundColor White
Write-Host "  - Data is persisted in Docker volumes" -ForegroundColor White
Write-Host "  - Check logs if any service is not responding" -ForegroundColor White
Write-Host "  - Allow 2-3 minutes for all services to be fully ready" -ForegroundColor White
Write-Host ""
Write-Host "Happy investigating! 🔍" -ForegroundColor Green
Write-Host ""

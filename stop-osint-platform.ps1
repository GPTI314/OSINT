# OSINT Intelligence Platform - Shutdown Script for Windows
# This script stops all OSINT platform services

$ErrorActionPreference = "Stop"

# Display banner
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OSINT INTELLIGENCE PLATFORM SHUTDOWN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "ERROR: docker-compose.yml not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Ask for confirmation
Write-Host "This will stop all OSINT platform services." -ForegroundColor Yellow
Write-Host "Data in volumes will be preserved." -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Do you want to continue? (y/N)"

if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Shutdown cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Stopping all services..." -ForegroundColor Yellow

# Stop services
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  PLATFORM STOPPED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "All services have been stopped." -ForegroundColor White
    Write-Host "Data volumes are preserved." -ForegroundColor White
    Write-Host ""
    Write-Host "To start again: .\start-osint-platform.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to stop some services!" -ForegroundColor Red
    Write-Host "You may need to manually stop containers:" -ForegroundColor Yellow
    Write-Host "  docker stop $(docker ps -a -q)" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Optional: Ask if user wants to remove volumes (data cleanup)
Write-Host "Do you want to remove all data volumes? (y/N)" -ForegroundColor Yellow
Write-Host "WARNING: This will DELETE all data!" -ForegroundColor Red
$removeVolumes = Read-Host

if ($removeVolumes -eq 'y' -or $removeVolumes -eq 'Y') {
    Write-Host ""
    Write-Host "Removing volumes..." -ForegroundColor Yellow
    docker-compose down -v

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Volumes removed successfully" -ForegroundColor Green
    } else {
        Write-Host "! Some volumes could not be removed" -ForegroundColor Yellow
    }
}

Write-Host ""

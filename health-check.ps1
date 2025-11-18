# OSINT Intelligence Platform - Health Check Script for Windows
# This script checks the health status of all platform services

$ErrorActionPreference = "Continue"

# Service endpoints to check
$services = @(
    @{Name="OSINT API"; URL="http://localhost:8000/api/v1/health"; Critical=$true},
    @{Name="OSINT API Docs"; URL="http://localhost:8000/docs"; Critical=$false},
    @{Name="Elasticsearch"; URL="http://localhost:9200/_cluster/health"; Critical=$true},
    @{Name="Kibana"; URL="http://localhost:5601/api/status"; Critical=$true},
    @{Name="Prometheus"; URL="http://localhost:9090/-/healthy"; Critical=$true},
    @{Name="Grafana"; URL="http://localhost:3001/api/health"; Critical=$true},
    @{Name="Flower"; URL="http://localhost:5555"; Critical=$false},
    @{Name="cAdvisor"; URL="http://localhost:8080"; Critical=$false},
    @{Name="Wireshark"; URL="http://localhost:3010"; Critical=$false}
)

# Display banner
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OSINT PLATFORM HEALTH CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "Docker Container Status:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker-compose ps
Write-Host ""

# Check service endpoints
Write-Host "Service Endpoint Health:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$healthyCount = 0
$unhealthyCount = 0
$criticalFailures = @()

foreach ($service in $services) {
    Write-Host -NoNewline "$($service.Name.PadRight(25)) ... "

    try {
        $response = Invoke-WebRequest -Uri $service.URL -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop

        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
            Write-Host "✓ HEALTHY" -ForegroundColor Green
            $healthyCount++
        } else {
            Write-Host "✗ UNHEALTHY (Status: $($response.StatusCode))" -ForegroundColor Yellow
            $unhealthyCount++
            if ($service.Critical) {
                $criticalFailures += $service.Name
            }
        }
    } catch {
        Write-Host "✗ UNREACHABLE" -ForegroundColor Red
        $unhealthyCount++
        if ($service.Critical) {
            $criticalFailures += $service.Name
        }
    }
}

# Summary
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  Healthy:   $healthyCount" -ForegroundColor Green
Write-Host "  Unhealthy: $unhealthyCount" -ForegroundColor $(if ($unhealthyCount -gt 0) { "Red" } else { "Gray" })

if ($criticalFailures.Count -gt 0) {
    Write-Host ""
    Write-Host "CRITICAL FAILURES:" -ForegroundColor Red
    foreach ($failure in $criticalFailures) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "ACTION REQUIRED: Check the logs for failed services:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs [service-name]" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check resource usage
Write-Host ""
Write-Host "Resource Usage:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    $dockerStats = docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>&1
    Write-Host $dockerStats
} catch {
    Write-Host "Unable to retrieve resource usage statistics" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  HEALTH CHECK COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($unhealthyCount -eq 0) {
    Write-Host "All services are healthy! ✓" -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "Some services are not responding." -ForegroundColor Yellow
    Write-Host "This is normal during startup (2-3 minutes)." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If services remain unhealthy:" -ForegroundColor Yellow
    Write-Host "  1. Check logs: docker-compose logs -f [service]" -ForegroundColor White
    Write-Host "  2. Restart: docker-compose restart [service]" -ForegroundColor White
    Write-Host "  3. See troubleshooting guide: TROUBLESHOOTING.md" -ForegroundColor White
    Write-Host ""
    exit 0
}

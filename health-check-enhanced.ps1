<#
.SYNOPSIS
    Enhanced Health Check for OSINT Platform with Elasticsearch Verification
.DESCRIPTION
    Comprehensive health check with detailed Elasticsearch cluster validation.
    Verifies all services with emphasis on ELK Stack startup sequence.
.NOTES
    Version: 2.0.0
    Date: 2025-11-18
#>

# Color functions
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Step { param($msg) Write-Host "`n▶ $msg" -ForegroundColor Magenta }

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    OSINT Platform - Enhanced Health Check v2.0          ║" -ForegroundColor Cyan
Write-Host "║       with Elasticsearch Verification                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$healthyCount = 0
$unhealthyCount = 0
$totalServices = 0

# Function to check HTTP endpoint
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [int]$Timeout = 5,
        [bool]$Critical = $false
    )

    $script:totalServices++

    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "$Name is healthy"
            $script:healthyCount++
            return $true
        } else {
            Write-Warning "$Name returned status $($response.StatusCode)"
            $script:unhealthyCount++
            return $false
        }
    } catch {
        if ($Critical) {
            Write-Error "$Name is NOT responding (CRITICAL)"
        } else {
            Write-Warning "$Name is not responding"
        }
        $script:unhealthyCount++
        return $false
    }
}

# 1. CRITICAL: Elasticsearch Check
Write-Step "Elasticsearch Health Check (CRITICAL - MUST BE FIRST)"

if (Test-Endpoint -Name "Elasticsearch API" -Url "http://localhost:9200" -Critical $true) {
    try {
        # Get detailed cluster information
        $esInfo = Invoke-RestMethod -Uri "http://localhost:9200" -UseBasicParsing
        Write-Info "  Cluster Name: $($esInfo.cluster_name)"
        Write-Info "  Node Name: $($esInfo.name)"
        Write-Info "  Version: $($esInfo.version.number)"
        Write-Info "  Build: $($esInfo.version.build_type)"

        # Get cluster health
        $esHealth = Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health" -UseBasicParsing
        $healthStatus = $esHealth.status

        switch ($healthStatus) {
            "green" {
                Write-Success "  Cluster Status: GREEN (All primary and replica shards allocated)"
            }
            "yellow" {
                Write-Success "  Cluster Status: YELLOW (All primary shards allocated, some replicas pending)"
                Write-Info "  This is NORMAL for single-node deployments"
            }
            "red" {
                Write-Error "  Cluster Status: RED (Some primary shards not allocated)"
                Write-Warning "  Action required: Check Elasticsearch logs"
            }
        }

        Write-Info "  Number of Nodes: $($esHealth.number_of_nodes)"
        Write-Info "  Number of Data Nodes: $($esHealth.number_of_data_nodes)"
        Write-Info "  Active Primary Shards: $($esHealth.active_primary_shards)"
        Write-Info "  Active Shards: $($esHealth.active_shards)"

        # List indices
        try {
            $indices = Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices?format=json" -UseBasicParsing
            if ($indices.Count -gt 0) {
                Write-Info "  Total Indices: $($indices.Count)"
            } else {
                Write-Info "  No indices created yet (this is normal on first run)"
            }
        } catch {
            Write-Info "  Could not retrieve indices list"
        }

        Write-Success "Elasticsearch is fully operational!"

    } catch {
        Write-Warning "Could not retrieve detailed Elasticsearch information"
    }
} else {
    Write-Error "CRITICAL: Elasticsearch is not running!"
    Write-Error "Kibana and Logstash require Elasticsearch to be healthy"
    Write-Info "Try: docker-compose restart elasticsearch"
    Write-Info "View logs: docker-compose logs elasticsearch"
}

# 2. Database Health Checks
Write-Step "Database Services Health Check"

# PostgreSQL
$pgHealthy = $false
try {
    $pgHealth = docker inspect --format='{{.State.Health.Status}}' osint-postgres 2>$null
    if ($pgHealth -eq "healthy") {
        Write-Success "PostgreSQL is healthy"
        $healthyCount++
        $pgHealthy = $true
    } else {
        Write-Warning "PostgreSQL status: $pgHealth"
        $unhealthyCount++
    }
    $totalServices++
} catch {
    Write-Error "PostgreSQL container not found"
    $unhealthyCount++
    $totalServices++
}

# MongoDB
try {
    $mongoHealth = docker inspect --format='{{.State.Health.Status}}' osint-mongodb 2>$null
    if ($mongoHealth -eq "healthy") {
        Write-Success "MongoDB is healthy"
        $healthyCount++
    } else {
        Write-Warning "MongoDB status: $mongoHealth"
        $unhealthyCount++
    }
    $totalServices++
} catch {
    Write-Error "MongoDB container not found"
    $unhealthyCount++
    $totalServices++
}

# Redis
try {
    $redisHealth = docker inspect --format='{{.State.Health.Status}}' osint-redis 2>$null
    if ($redisHealth -eq "healthy") {
        Write-Success "Redis is healthy"
        $healthyCount++
    } else {
        Write-Warning "Redis status: $redisHealth"
        $unhealthyCount++
    }
    $totalServices++
} catch {
    Write-Error "Redis container not found"
    $unhealthyCount++
    $totalServices++
}

# 3. ELK Stack Health (Depends on Elasticsearch)
Write-Step "ELK Stack Health Check (Requires Elasticsearch)"

# Logstash
Test-Endpoint -Name "Logstash" -Url "http://localhost:9600/_node/stats"

# Kibana
if (Test-Endpoint -Name "Kibana" -Url "http://localhost:5601/api/status") {
    try {
        $kibanaStatus = Invoke-RestMethod -Uri "http://localhost:5601/api/status" -UseBasicParsing
        $overallStatus = $kibanaStatus.status.overall.state

        if ($overallStatus -eq "green") {
            Write-Success "  Kibana Overall Status: GREEN"
        } elseif ($overallStatus -eq "yellow") {
            Write-Warning "  Kibana Overall Status: YELLOW"
        } else {
            Write-Error "  Kibana Overall Status: $overallStatus"
        }
    } catch {
        Write-Info "  Could not retrieve detailed Kibana status"
    }
}

# 4. OSINT Platform Services
Write-Step "OSINT Platform Services Health Check"

Test-Endpoint -Name "OSINT API" -Url "http://localhost:8000/api/v1/health"
Test-Endpoint -Name "API Documentation" -Url "http://localhost:8000/docs"

# Flower (Celery Monitoring)
Test-Endpoint -Name "Flower (Celery)" -Url "http://localhost:5555"

# Check Celery workers via Docker
try {
    $celeryWorker = docker ps --filter "name=osint-celery-worker" --format "{{.Status}}" 2>$null
    if ($celeryWorker -like "*Up*") {
        Write-Success "Celery Worker is running"
        $healthyCount++
    } else {
        Write-Warning "Celery Worker status: $celeryWorker"
        $unhealthyCount++
    }
    $totalServices++
} catch {
    Write-Warning "Celery Worker container not found"
    $unhealthyCount++
    $totalServices++
}

# 5. Monitoring Stack
Write-Step "Monitoring Stack Health Check"

Test-Endpoint -Name "Prometheus" -Url "http://localhost:9090/-/healthy"
Test-Endpoint -Name "Grafana" -Url "http://localhost:3001/api/health"
Test-Endpoint -Name "cAdvisor" -Url "http://localhost:8080/healthz"

# 6. Summary
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                   Health Check Summary                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$healthPercentage = [math]::Round(($healthyCount / $totalServices) * 100, 1)

Write-Host "  Total Services Checked: $totalServices" -ForegroundColor White
Write-Host "  Healthy Services: $healthyCount" -ForegroundColor Green
Write-Host "  Unhealthy Services: $unhealthyCount" -ForegroundColor $(if ($unhealthyCount -eq 0) { "Green" } else { "Yellow" })
Write-Host "  Health Percentage: $healthPercentage%" -ForegroundColor $(if ($healthPercentage -ge 80) { "Green" } elseif ($healthPercentage -ge 60) { "Yellow" } else { "Red" })

if ($healthyCount -eq $totalServices) {
    Write-Host "`n✓ All services are healthy!" -ForegroundColor Green
    Write-Host "  Platform is ready to use 🚀" -ForegroundColor Green
} elseif ($healthPercentage -ge 75) {
    Write-Host "`n⚠ Most services are healthy" -ForegroundColor Yellow
    Write-Host "  Some non-critical services may need attention" -ForegroundColor Yellow
} else {
    Write-Host "`n✗ Multiple services are unhealthy" -ForegroundColor Red
    Write-Host "  Platform may not function correctly" -ForegroundColor Red
}

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  Service Access URLs                     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$urls = @(
    "Elasticsearch:      http://localhost:9200",
    "Kibana:             http://localhost:5601",
    "OSINT API:          http://localhost:8000",
    "API Docs:           http://localhost:8000/docs",
    "Grafana:            http://localhost:3001 (admin/admin)",
    "Prometheus:         http://localhost:9090",
    "Flower:             http://localhost:5555"
)

foreach ($url in $urls) {
    Write-Host "  $url" -ForegroundColor Cyan
}

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║               Troubleshooting Commands                   ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

Write-Host "  View all logs:          docker-compose logs -f" -ForegroundColor White
Write-Host "  View ES logs:           docker-compose logs elasticsearch" -ForegroundColor White
Write-Host "  View Kibana logs:       docker-compose logs kibana" -ForegroundColor White
Write-Host "  View API logs:          docker-compose logs api" -ForegroundColor White
Write-Host "  Restart service:        docker-compose restart <service>" -ForegroundColor White
Write-Host "  Check containers:       docker-compose ps" -ForegroundColor White

Write-Host ""

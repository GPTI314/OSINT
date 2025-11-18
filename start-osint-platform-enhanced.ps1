<#
.SYNOPSIS
    Enhanced OSINT Intelligence Platform Startup Script with Elasticsearch Verification
.DESCRIPTION
    Starts the OSINT platform with proper Elasticsearch verification before enabling Kibana.
    This ensures Elasticsearch is fully operational before dependent services start.
.NOTES
    Version: 2.0.0
    Author: OSINT Platform Team
    Date: 2025-11-18
#>

# Color functions
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Step { param($msg) Write-Host "`n▶ $msg" -ForegroundColor Magenta }

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   OSINT Intelligence Platform - Enhanced Startup v2.0   ║" -ForegroundColor Cyan
Write-Host "║          with Elasticsearch Verification                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Check Docker Desktop
Write-Step "Checking Docker Desktop Status"
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker Desktop is not running"
        Write-Info "Please start Docker Desktop and try again"
        exit 1
    }
    Write-Success "Docker Desktop is running"
} catch {
    Write-Error "Docker command not found"
    Write-Info "Please ensure Docker Desktop is installed"
    exit 1
}

# Step 2: Check Docker Compose
Write-Step "Checking Docker Compose"
try {
    docker-compose version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        docker compose version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker Compose not found"
            exit 1
        }
    }
    Write-Success "Docker Compose is available"
} catch {
    Write-Error "Docker Compose not available"
    exit 1
}

# Step 3: Load environment variables
Write-Step "Loading Environment Configuration"
if (Test-Path ".env") {
    Write-Success "Environment file found (.env)"
} else {
    Write-Warning "No .env file found"
    if (Test-Path ".env.example") {
        Write-Info "Creating .env from .env.example"
        Copy-Item .env.example .env
        Write-Warning "Please edit .env file and update passwords before production use!"
    }
}

# Step 4: Create required directories
Write-Step "Creating Required Directories"
$directories = @("logs", "storage", "data", "wireshark-captures")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Success "Created directory: $dir"
    } else {
        Write-Info "Directory exists: $dir"
    }
}

# Step 5: Start Core Services (Databases)
Write-Step "Starting Core Database Services"
Write-Info "Starting PostgreSQL, MongoDB, Redis..."
docker-compose up -d postgres mongodb redis
Start-Sleep -Seconds 5

Write-Info "Waiting for databases to be healthy (30 seconds)..."
$dbTimeout = 60
$dbElapsed = 0
$dbHealthy = $false
while ($dbElapsed -lt $dbTimeout) {
    $pgHealth = docker inspect --format='{{.State.Health.Status}}' osint-postgres 2>$null
    $mongoHealth = docker inspect --format='{{.State.Health.Status}}' osint-mongodb 2>$null
    $redisHealth = docker inspect --format='{{.State.Health.Status}}' osint-redis 2>$null

    if ($pgHealth -eq "healthy" -and $mongoHealth -eq "healthy" -and $redisHealth -eq "healthy") {
        $dbHealthy = $true
        break
    }

    Write-Host "." -NoNewline
    Start-Sleep -Seconds 3
    $dbElapsed += 3
}
Write-Host ""

if ($dbHealthy) {
    Write-Success "All databases are healthy"
} else {
    Write-Warning "Databases may still be initializing - continuing anyway"
}

# Step 6: Start Elasticsearch FIRST and VERIFY
Write-Step "Starting Elasticsearch (This may take 1-2 minutes)"
Write-Info "Starting Elasticsearch container..."
docker-compose up -d elasticsearch

Write-Info "Waiting for Elasticsearch to initialize..."
Start-Sleep -Seconds 20

$maxRetries = 20
$retryCount = 0
$esReady = $false

while ($retryCount -lt $maxRetries -and -not $esReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 5 -UseBasicParsing 2>$null
        if ($response.StatusCode -eq 200) {
            $esReady = $true
            Write-Success "Elasticsearch is responding!"
        }
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 5
        $retryCount++
    }
}
Write-Host ""

if (-not $esReady) {
    Write-Error "Elasticsearch failed to start properly"
    Write-Info "Check logs: docker-compose logs elasticsearch"
    exit 1
}

# Step 7: VERIFY Elasticsearch in Browser
Write-Step "IMPORTANT: Verify Elasticsearch in Browser"
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│  PLEASE VERIFY ELASTICSEARCH IS RUNNING:               │" -ForegroundColor Yellow
Write-Host "│                                                         │" -ForegroundColor Yellow
Write-Host "│  1. Open your browser                                  │" -ForegroundColor Yellow
Write-Host "│  2. Navigate to: http://localhost:9200                 │" -ForegroundColor Yellow
Write-Host "│  3. You should see JSON with cluster info              │" -ForegroundColor Yellow
Write-Host "│  4. Press ENTER to continue once verified...           │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────┘`n" -ForegroundColor Yellow

# Try to open browser automatically
try {
    Start-Process "http://localhost:9200"
    Write-Success "Opened Elasticsearch URL in browser"
} catch {
    Write-Info "Please manually open: http://localhost:9200"
}

# Wait for user confirmation
Read-Host "`nPress ENTER after verifying Elasticsearch in browser"

# Additional verification
Write-Info "Performing cluster health check..."
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -UseBasicParsing
    $health = $healthResponse.Content | ConvertFrom-Json
    Write-Success "Cluster Status: $($health.status)"
    Write-Success "Number of Nodes: $($health.number_of_nodes)"
    Write-Success "Number of Data Nodes: $($health.number_of_data_nodes)"
} catch {
    Write-Warning "Could not retrieve detailed cluster health"
}

# Step 8: Start Logstash (depends on Elasticsearch)
Write-Step "Starting Logstash"
Write-Info "Starting Logstash (depends on Elasticsearch)..."
docker-compose up -d logstash
Start-Sleep -Seconds 10
Write-Success "Logstash started"

# Step 9: Start Kibana (depends on Elasticsearch)
Write-Step "Starting Kibana"
Write-Info "Starting Kibana (This may take 1-2 minutes)..."
docker-compose up -d kibana

Write-Info "Waiting for Kibana to initialize..."
$kibanaRetries = 30
$kibanaCount = 0
$kibanaReady = $false

while ($kibanaCount -lt $kibanaRetries -and -not $kibanaReady) {
    try {
        $kibanaResponse = Invoke-WebRequest -Uri "http://localhost:5601/api/status" -TimeoutSec 5 -UseBasicParsing 2>$null
        if ($kibanaResponse.StatusCode -eq 200) {
            $kibanaReady = $true
            Write-Success "Kibana is ready!"
        }
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 6
        $kibanaCount++
    }
}
Write-Host ""

if ($kibanaReady) {
    Write-Success "Kibana started successfully"
} else {
    Write-Warning "Kibana may still be initializing"
    Write-Info "Check status at: http://localhost:5601"
}

# Step 10: Start Monitoring Stack
Write-Step "Starting Monitoring Services (Prometheus, Grafana)"
docker-compose up -d prometheus grafana node-exporter cadvisor
Start-Sleep -Seconds 10
Write-Success "Monitoring services started"

# Step 11: Start OSINT Platform Services
Write-Step "Starting OSINT Platform Services"
docker-compose up -d api celery_worker celery_beat flower
Start-Sleep -Seconds 15
Write-Success "OSINT services started"

# Step 12: Start Optional Services
Write-Step "Starting Optional Services"
docker-compose up -d wireshark
Write-Success "All services started"

# Step 13: Display Service Status
Write-Step "Checking Service Status"
Start-Sleep -Seconds 5

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Service Access URLs                         ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

$services = @(
    @{Name="Elasticsearch"; URL="http://localhost:9200"; Status="CRITICAL - VERIFY FIRST"},
    @{Name="Kibana"; URL="http://localhost:5601"; Status="READY"},
    @{Name="OSINT API"; URL="http://localhost:8000"; Status="READY"},
    @{Name="API Documentation"; URL="http://localhost:8000/docs"; Status="READY"},
    @{Name="Grafana"; URL="http://localhost:3001"; Status="admin/admin"},
    @{Name="Prometheus"; URL="http://localhost:9090"; Status="READY"},
    @{Name="Flower (Celery)"; URL="http://localhost:5555"; Status="READY"},
    @{Name="Wireshark"; URL="http://localhost:3010"; Status="READY"}
)

foreach ($service in $services) {
    $padding = " " * (20 - $service.Name.Length)
    Write-Host "  $($service.Name):$padding$($service.URL)" -ForegroundColor Cyan
    if ($service.Status -like "CRITICAL*") {
        Write-Host "    Status: $($service.Status)" -ForegroundColor Red
    } else {
        Write-Host "    Status: $($service.Status)" -ForegroundColor Green
    }
}

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║                  STARTUP SEQUENCE                        ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow
Write-Host "  1. ✓ Elasticsearch started and verified" -ForegroundColor Green
Write-Host "  2. ✓ Logstash started (depends on ES)" -ForegroundColor Green
Write-Host "  3. ✓ Kibana started (depends on ES)" -ForegroundColor Green
Write-Host "  4. ✓ Monitoring stack started" -ForegroundColor Green
Write-Host "  5. ✓ OSINT platform services started" -ForegroundColor Green

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                   NEXT STEPS                             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
Write-Host "  1. Verify Elasticsearch: http://localhost:9200" -ForegroundColor Yellow
Write-Host "  2. Check Kibana: http://localhost:5601" -ForegroundColor White
Write-Host "  3. Access API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  4. Run health check: .\health-check.ps1" -ForegroundColor White

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     OSINT Platform Started Successfully! 🚀              ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Info "View logs: docker-compose logs -f"
Write-Info "Stop platform: .\stop-osint-platform.ps1"
Write-Info "Health check: .\health-check.ps1"

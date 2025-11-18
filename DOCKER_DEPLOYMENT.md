# OSINT Intelligence Platform - Windows Docker Deployment Guide

Complete guide for deploying the OSINT Intelligence Platform on Windows using Docker Desktop with full monitoring, logging, and analytics capabilities.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Service Details](#service-details)
- [Configuration](#configuration)
- [Management Commands](#management-commands)
- [Monitoring & Observability](#monitoring--observability)
- [Data Persistence](#data-persistence)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)

## Overview

This deployment includes a complete production-ready stack with:

### Core Services
- **OSINT API** - FastAPI application (Port 8000)
- **Celery Workers** - Background task processing
- **Celery Beat** - Task scheduling
- **Flower** - Celery monitoring (Port 5555)

### Databases
- **PostgreSQL 15** - Relational data (Port 5432)
- **MongoDB 7** - Document storage (Port 27017)
- **Redis 7** - Cache & message broker (Port 6379)

### ELK Stack
- **Elasticsearch 7.17.15 LTS** - Search & analytics (Port 9200, 9300) ⭐ STABLE
- **Logstash 7.17.15** - Log processing (Port 5000, 5044, 9600)
- **Kibana 7.17.15** - Log visualization (Port 5601)

**Why Elasticsearch 7.17 LTS?**
- ✅ Long-term support (LTS) version
- ✅ Production-tested and stable
- ✅ Compatible with monitoring stack
- ✅ Security patches and updates
- ✅ Perfect for Windows Docker Desktop deployment
- ⚠️ Note: ES 1.x-6.x are deprecated and unsupported (security risks)

### Monitoring Stack
- **Prometheus** - Metrics collection (Port 9090)
- **Grafana** - Metrics visualization (Port 3001)
- **Node Exporter** - System metrics (Port 9100)
- **cAdvisor** - Container metrics (Port 8080)

### Network Analysis
- **Wireshark** - Network packet analysis (Port 3010)

## Prerequisites

### Required Software

1. **Windows 11** (or Windows 10 Pro/Enterprise)
2. **Docker Desktop for Windows** (latest version)
   - Download: https://www.docker.com/products/docker-desktop
   - WSL2 backend enabled
   - Minimum 8GB RAM allocated to Docker
   - Minimum 4 CPUs allocated to Docker

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16GB | 32GB |
| CPU | 4 cores | 8+ cores |
| Storage | 50GB free | 100GB+ free |
| OS | Windows 10 Pro | Windows 11 Pro |

### Docker Desktop Configuration

1. Open Docker Desktop Settings
2. Go to **Resources** → **Advanced**
3. Configure:
   - **CPUs**: 4 minimum, 6+ recommended
   - **Memory**: 8GB minimum, 16GB+ recommended
   - **Swap**: 2GB
   - **Disk image size**: 100GB+

4. Go to **General**
   - ✓ Enable "Use the WSL 2 based engine"
   - ✓ Enable "Use Docker Compose V2"

5. Apply & Restart

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         OSINT Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Frontend   │  │   OSINT API  │  │   Workers    │         │
│  │  (React)     │  │  (FastAPI)   │  │  (Celery)    │         │
│  │  Port 3000   │  │  Port 8000   │  │              │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                 │
│         └─────────────────┴──────────────────┘                 │
│                           │                                     │
├───────────────────────────┼─────────────────────────────────────┤
│                  Database Layer                                 │
│                           │                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │   MongoDB    │  │    Redis     │         │
│  │  Port 5432   │  │  Port 27017  │  │  Port 6379   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Logging & Analytics                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │                   ELK Stack                         │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │        │
│  │  │  Elastic │─→│ Logstash │←─│  Kibana  │         │        │
│  │  │   9200   │  │   5000   │  │   5601   │         │        │
│  │  └──────────┘  └──────────┘  └──────────┘         │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Monitoring Stack                             │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │              Prometheus & Grafana                   │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │        │
│  │  │Prometheus│─→│ Grafana  │  │   Node   │         │        │
│  │  │   9090   │  │   3001   │  │ Exporter │         │        │
│  │  └──────────┘  └──────────┘  └──────────┘         │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Clone Repository

```powershell
git clone <repository-url>
cd OSINT
```

### 2. Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env file with your preferred editor
notepad .env
```

**Important**: Change these values in `.env`:
- `POSTGRES_PASSWORD`
- `MONGO_PASSWORD`
- `REDIS_PASSWORD`
- `SECRET_KEY`
- `GRAFANA_PASSWORD`

### 3. Start Platform (Enhanced with Elasticsearch Verification)

```powershell
.\start-osint-platform-enhanced.ps1
```

This enhanced startup script ensures **proper Elasticsearch initialization before Kibana**:

1. ✓ Check Docker Desktop is running
2. ✓ Verify Docker Compose is available
3. ✓ Load environment variables
4. ✓ Create required directories
5. ✓ Start database services (PostgreSQL, MongoDB, Redis)
6. ✓ **Start Elasticsearch FIRST** (1-2 minutes initialization)
7. ✓ **VERIFY Elasticsearch in browser** (http://localhost:9200)
8. ✓ Wait for user confirmation
9. ✓ Start Logstash (depends on Elasticsearch)
10. ✓ Start Kibana (depends on Elasticsearch)
11. ✓ Start monitoring services (Prometheus, Grafana)
12. ✓ Start OSINT platform services
13. ✓ Display service URLs and status

**IMPORTANT Elasticsearch Verification Steps**:
1. Script will start Elasticsearch first
2. Browser will open to http://localhost:9200 automatically
3. Verify you see JSON output with cluster information:
   ```json
   {
     "name" : "osint-node-1",
     "cluster_name" : "osint-cluster",
     "version" : {
       "number" : "7.17.15",
       ...
     },
     "tagline" : "You Know, for Search"
   }
   ```
4. Press ENTER in PowerShell to continue with Kibana startup

**First startup takes 5-10 minutes** as images are downloaded and services initialize.

**Alternative**: Use standard startup (no ES verification):
```powershell
.\start-osint-platform.ps1  # Original startup script
```

### 4. Verify Deployment

```powershell
.\health-check.ps1
```

This checks all service endpoints and displays their health status.

### 5. Access Services

Open your browser and navigate to:

- **OSINT API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Kibana**: http://localhost:5601
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Flower**: http://localhost:5555
- **Wireshark**: http://localhost:3010

## Service Details

### OSINT API (Port 8000)

FastAPI application providing REST API endpoints.

**Features:**
- OpenAPI documentation at `/docs`
- ReDoc documentation at `/redoc`
- Health check at `/api/v1/health`
- Metrics at `/api/v1/metrics`

**Environment Variables:**
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://...
MONGODB_URL=mongodb://...
REDIS_URL=redis://...
```

### Elasticsearch (Port 9200)

Search and analytics engine for log data.

**Version**: 7.17.15 LTS (Long-Term Support)

**Configuration:**
- Single node cluster (`osint-cluster`)
- Node name: `osint-node-1`
- 2GB heap size (configurable)
- Security disabled (internal network only - safe for local deployment)
- XPack monitoring enabled
- Data persisted in `elasticsearch_data` volume
- Enhanced health checks with proper startup timing

**CRITICAL STARTUP SEQUENCE:**
1. Elasticsearch MUST start first (60-90 seconds)
2. Verify at http://localhost:9200 in browser
3. Wait for cluster status "yellow" or "green"
4. THEN Kibana can start (depends on ES health)
5. Logstash starts after ES is healthy

**Access & Verification:**
```powershell
# Check cluster health (IMPORTANT - Do this first!)
curl http://localhost:9200/_cluster/health

# Verify cluster info
curl http://localhost:9200/

# List indices
curl http://localhost:9200/_cat/indices?v

# Check nodes
curl http://localhost:9200/_cat/nodes?v
```

**Expected Output (when healthy):**
```json
{
  "name" : "osint-node-1",
  "cluster_name" : "osint-cluster",
  "version" : {
    "number" : "7.17.15",
    "build_flavor" : "default",
    "build_type" : "docker"
  },
  "tagline" : "You Know, for Search"
}
```

**Health Check Status:**
- 🟢 **Green**: All shards allocated (optimal)
- 🟡 **Yellow**: Primary shards allocated, replicas pending (OK for single node)
- 🔴 **Red**: Some primary shards not allocated (requires attention)

### Kibana (Port 5601)

Log visualization and exploration interface.

**Initial Setup:**
1. Navigate to http://localhost:5601
2. Wait for Kibana to initialize (1-2 minutes)
3. Create index pattern: `osint-logs-*`
4. Set time field: `@timestamp`

### Prometheus (Port 9090)

Metrics collection and alerting.

**Configuration:**
- Scrape interval: 15s
- Retention: 30 days
- Alert rules in `prometheus/rules/`

**Targets:**
- Prometheus itself
- Node Exporter (system metrics)
- cAdvisor (container metrics)
- OSINT API

### Grafana (Port 3001)

Metrics visualization and dashboards.

**Default Credentials:**
- Username: `admin`
- Password: `admin` (change in `.env`)

**Pre-configured Datasources:**
- Prometheus (default)
- Elasticsearch

**Dashboards:**
- OSINT Platform Overview
- Container Metrics
- System Metrics

### Logstash (Port 5000, 5044, 9600)

Log processing and enrichment pipeline.

**Inputs:**
- Port 5044: Beats protocol
- Port 5000: TCP JSON
- File: `/app/logs/*.log`

**Outputs:**
- Elasticsearch: `osint-logs-*` indices
- Stdout: Debug output

## Configuration

### Environment Variables

All configuration is managed through the `.env` file.

**Critical Settings:**

```bash
# Database Passwords
POSTGRES_PASSWORD=<strong-password>
MONGO_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# Application Security
SECRET_KEY=<random-secret-key>
JWT_SECRET_KEY=<random-jwt-secret>

# Monitoring
GRAFANA_PASSWORD=<strong-password>
```

**Generate Secure Keys:**

```powershell
# PowerShell command to generate random keys
[System.Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### Docker Compose Overrides

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'

services:
  api:
    environment:
      - DEBUG=true
    ports:
      - "8001:8000"  # Different port
```

This file is git-ignored and won't affect the main configuration.

### Resource Limits

Edit `docker-compose.yml` to adjust resource limits:

```yaml
services:
  elasticsearch:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G
```

## Management Commands

### Start Platform

```powershell
.\start-osint-platform.ps1
```

### Stop Platform

```powershell
.\stop-osint-platform.ps1
```

### Health Check

```powershell
.\health-check.ps1
```

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f elasticsearch

# Last 100 lines
docker-compose logs --tail=100 api
```

### Restart Service

```powershell
docker-compose restart api
docker-compose restart elasticsearch
```

### Rebuild Service

```powershell
docker-compose up -d --build api
```

### Execute Commands in Container

```powershell
# PostgreSQL
docker-compose exec postgres psql -U osint_user -d osint_platform

# MongoDB
docker-compose exec mongodb mongosh -u osint_admin -p

# Redis
docker-compose exec redis redis-cli -a <password>

# API Shell
docker-compose exec api python
```

### Scale Workers

```powershell
docker-compose up -d --scale celery_worker=4
```

## Monitoring & Observability

### Metrics (Prometheus + Grafana)

1. **Access Grafana**: http://localhost:3001
2. **Login**: admin / admin (change on first login)
3. **View Dashboards**:
   - OSINT Platform Overview
   - Node Metrics
   - Container Metrics

**Create Custom Dashboard:**
1. Click "+" → Dashboard
2. Add Panel
3. Select Prometheus datasource
4. Write PromQL query

**Example Queries:**
```promql
# CPU usage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# API request rate
rate(http_requests_total[5m])
```

### Logs (ELK Stack)

1. **Access Kibana**: http://localhost:5601
2. **Create Index Pattern**: `osint-logs-*`
3. **Discover Logs**: Navigate to Discover

**Common Searches:**
```
level: "ERROR"
service: "osint-api"
level: "ERROR" AND service: "osint-api"
```

**Create Visualizations:**
1. Navigate to Visualize
2. Create visualization
3. Select index pattern
4. Configure metrics and buckets

### Container Metrics (cAdvisor)

**Access**: http://localhost:8080

View real-time container resource usage:
- CPU usage
- Memory usage
- Network I/O
- Disk I/O

### Task Monitoring (Flower)

**Access**: http://localhost:5555

Monitor Celery tasks:
- Active tasks
- Task history
- Worker status
- Task details

## Data Persistence

All data is stored in Docker volumes:

| Volume | Service | Data |
|--------|---------|------|
| postgres_data | PostgreSQL | Relational data |
| mongodb_data | MongoDB | Document data |
| mongodb_config | MongoDB | Configuration |
| redis_data | Redis | Cache data |
| elasticsearch_data | Elasticsearch | Logs & indices |
| kibana_data | Kibana | Dashboards & config |
| prometheus_data | Prometheus | Metrics |
| grafana_data | Grafana | Dashboards & config |
| wireshark_data | Wireshark | Captures |

### Backup Volumes

```powershell
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U osint_user osint_platform > backup.sql

# Backup MongoDB
docker-compose exec mongodb mongodump --out=/backup

# Backup volume to tar
docker run --rm -v postgres_data:/data -v ${PWD}:/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Restore Volumes

```powershell
# Restore PostgreSQL
Get-Content backup.sql | docker-compose exec -T postgres psql -U osint_user osint_platform

# Restore volume from tar
docker run --rm -v postgres_data:/data -v ${PWD}:/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

### Remove All Data

```powershell
docker-compose down -v
```

⚠️ **Warning**: This deletes ALL data permanently!

## Security

### Best Practices

1. **Change Default Passwords**
   - Update all passwords in `.env`
   - Use strong, unique passwords
   - Store `.env` securely (not in git)

2. **Network Security**
   - Services communicate on internal `osint-network`
   - Only expose necessary ports to host
   - Use firewall rules to restrict access

3. **Update Regularly**
   ```powershell
   docker-compose pull
   docker-compose up -d
   ```

4. **Monitor Security**
   - Review Prometheus alerts
   - Check logs in Kibana
   - Monitor failed login attempts

### Production Recommendations

1. **Enable HTTPS**
   - Use reverse proxy (nginx/traefik)
   - Configure SSL certificates
   - Redirect HTTP to HTTPS

2. **Enable Authentication**
   - Enable Elasticsearch security
   - Configure Kibana authentication
   - Use strong JWT secrets

3. **Network Isolation**
   - Separate networks for services
   - Use VPN for remote access
   - Implement network policies

4. **Secret Management**
   - Use Docker secrets
   - Consider Vault for secret storage
   - Rotate credentials regularly

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed troubleshooting guide.

### Common Issues

**Docker Desktop not running**
```
Solution: Start Docker Desktop from Windows Start menu
```

**Port conflicts**
```
Solution: Check if ports are in use
netstat -ano | findstr :8000
```

**Services not healthy**
```
Solution: Check logs
docker-compose logs -f <service>
```

**Out of memory**
```
Solution: Increase Docker memory allocation in Docker Desktop settings
```

**Elasticsearch won't start**
```
Solution: Increase vm.max_map_count in WSL2
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
```

## Performance Tuning

### Docker Desktop

Allocate more resources:
- **CPUs**: Match physical cores
- **Memory**: 50-75% of system RAM
- **Disk**: Enable fast disk performance

### Elasticsearch

Adjust heap size in `docker-compose.yml`:
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms4g -Xmx4g"
```

Rule: Heap = 50% of container memory, max 32GB

### PostgreSQL

Tune connections in `docker-compose.yml`:
```yaml
command: >
  postgres
  -c max_connections=200
  -c shared_buffers=256MB
  -c effective_cache_size=1GB
```

### Redis

Enable persistence optimization:
```yaml
command: >
  redis-server
  --requirepass ${REDIS_PASSWORD}
  --appendonly yes
  --appendfsync everysec
```

### Celery Workers

Scale based on workload:
```powershell
docker-compose up -d --scale celery_worker=8
```

## Additional Resources

- [Main README](README.md) - Project overview
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error messages
- Run health check script

---

**Version**: 1.0.0
**Last Updated**: 2025-11-18
**Platform**: Windows 11 / Docker Desktop

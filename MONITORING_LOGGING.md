# OSINT Toolkit - Monitoring & Logging

Comprehensive monitoring and logging infrastructure for the OSINT Toolkit.

## Table of Contents

1. [Overview](#overview)
2. [Logging System](#logging-system)
3. [Monitoring System](#monitoring-system)
4. [Quick Start](#quick-start)
5. [Configuration](#configuration)
6. [Architecture](#architecture)
7. [Usage Examples](#usage-examples)
8. [Dashboards](#dashboards)
9. [Alerts](#alerts)
10. [Troubleshooting](#troubleshooting)

## Overview

The OSINT Toolkit implements enterprise-grade monitoring and logging with:

### Logging Features
- ✅ **Structured logging** (JSON format)
- ✅ **Log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ **Centralized logging** (ELK Stack)
- ✅ **Log rotation** (automatic rotation, configurable size)
- ✅ **Sensitive data masking** (emails, IPs, API keys, etc.)

### Monitoring Features
- ✅ **Prometheus metrics** (application and system metrics)
- ✅ **Grafana dashboards** (visualization and analytics)
- ✅ **AlertManager** (intelligent alerting)
- ✅ **Health checks** (system health monitoring)
- ✅ **Performance monitoring** (execution time tracking)

## Logging System

### Architecture

```
Application → Structured Logger → Multiple Outputs
                                   ├─ Console (JSON/Text)
                                   ├─ File (with rotation)
                                   ├─ Logstash → Elasticsearch → Kibana
                                   └─ Error File (errors only)
```

### Log Levels

| Level    | Usage                                      |
|----------|--------------------------------------------|
| DEBUG    | Detailed diagnostic information            |
| INFO     | General informational messages             |
| WARNING  | Warning messages, degraded functionality   |
| ERROR    | Error messages, failed operations          |
| CRITICAL | Critical errors, system failure            |

### Log Format

JSON structured logs include:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "name": "osint-toolkit",
  "message": "Data collected successfully",
  "service": "osint-toolkit",
  "environment": "production",
  "source": "twitter",
  "type": "profile"
}
```

### Sensitive Data Masking

Automatically masks:
- ✅ Email addresses: `user@example.com` → `u***@example.com`
- ✅ IP addresses: `192.168.1.1` → `XXX.XXX.XXX.XXX`
- ✅ Phone numbers: `555-123-4567` → `XXX-XXX-XXXX`
- ✅ API keys: `sk_test_abc123` → `********`
- ✅ Credit cards: `4111-1111-1111-1111` → `****-****-****-1111`
- ✅ SSN: `123-45-6789` → `XXX-XX-XXXX`
- ✅ Passwords in configs
- ✅ Bearer tokens
- ✅ JWT tokens
- ✅ AWS keys

### Log Rotation

Automatic rotation with configurable settings:
- **Max file size**: 100MB (default)
- **Backup count**: 10 files (default)
- **Rotation strategy**: Size-based

## Monitoring System

### Metrics Categories

#### 1. Application Metrics

**Request Metrics**
- `osint_requests_total` - Total number of requests
- `osint_request_duration_seconds` - Request duration histogram
- `osint_active_requests` - Current active requests

**OSINT Specific**
- `osint_data_collected_total` - Data points collected by source/type
- `osint_enrichment_operations_total` - Enrichment operations
- `osint_analysis_duration_seconds` - Analysis duration
- `osint_cache_operations_total` - Cache hit/miss rates

**Errors**
- `osint_errors_total` - Total errors by type/component

**Database**
- `osint_db_connections_active` - Active DB connections
- `osint_db_query_duration_seconds` - Query duration

**Queue**
- `osint_queue_size` - Queue size by name
- `osint_queue_processing_duration_seconds` - Processing duration

#### 2. System Metrics

- `osint_cpu_usage_percent` - CPU usage
- `osint_memory_usage_bytes` - Memory usage
- `osint_disk_usage_percent` - Disk usage
- `osint_network_bytes_sent_total` - Network sent
- `osint_network_bytes_received_total` - Network received

### Health Checks

Built-in health checks:
- ✅ CPU usage monitoring
- ✅ Memory usage monitoring
- ✅ Disk usage monitoring
- ✅ Process thread count
- ✅ Custom checks (database, cache, APIs)

Health status levels:
- **Healthy**: All systems operational
- **Degraded**: Some issues detected
- **Unhealthy**: Critical issues

### Performance Monitoring

Track performance with decorators:

```python
from monitoring.performance import monitor_performance, track_performance

@monitor_performance('operation_name', include_system_stats=True)
def my_function():
    # Your code here
    pass

# Or use context manager
with track_performance('block_name'):
    # Code to measure
    pass
```

## Quick Start

### 1. Prerequisites

```bash
# Install Docker and Docker Compose
docker --version
docker-compose --version
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Start Monitoring Stack

```bash
# Start all services
docker-compose -f docker-compose.monitoring.yml up -d

# Check status
docker-compose -f docker-compose.monitoring.yml ps
```

### 4. Access Services

| Service       | URL                        | Credentials        |
|---------------|----------------------------|--------------------|
| Application   | http://localhost:5000      | -                  |
| Metrics       | http://localhost:8000      | -                  |
| Kibana        | http://localhost:5601      | -                  |
| Grafana       | http://localhost:3000      | admin/admin        |
| Prometheus    | http://localhost:9090      | -                  |
| AlertManager  | http://localhost:9093      | -                  |

### 5. Verify Setup

```bash
# Check health
curl http://localhost:5000/health

# View metrics
curl http://localhost:8000/metrics

# View performance stats
curl http://localhost:5000/performance
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Application
APP_NAME=osint-toolkit
APP_ENV=production
LOG_LEVEL=INFO

# Logging
LOG_DIR=./logs
LOG_MAX_BYTES=104857600  # 100MB
LOG_BACKUP_COUNT=10

# ELK Stack
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
LOGSTASH_HOST=logstash
LOGSTASH_PORT=5000

# Monitoring
PROMETHEUS_PORT=9090
METRICS_PORT=8000
GRAFANA_PORT=3000

# Alerts
ALERTMANAGER_PORT=9093
ALERT_EMAIL_TO=alerts@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587

# Data Masking
MASK_EMAILS=true
MASK_IPS=true
MASK_PHONE_NUMBERS=true
MASK_API_KEYS=true
```

## Usage Examples

### Logging

```python
from logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Operation completed")
logger.error("Operation failed", exc_info=True)

# Structured logging with context
logger.info("Data collected", extra={
    'source': 'twitter',
    'count': 100,
    'duration': 1.5
})

# Automatic masking
logger.info("User email: user@example.com")  # Masked in logs
logger.info("API key: sk_test_abc123")       # Masked in logs
```

### Metrics

```python
from monitoring import get_metrics_collector

metrics = get_metrics_collector()

# Record custom metrics
metrics.record_data_collection('twitter', 'profile', count=10)
metrics.record_enrichment('geo_lookup', 'success')
metrics.record_error('ValueError', 'data_processor')

# Record request
metrics.record_request('GET', '/api/data', 200, 0.5)
```

### Health Checks

```python
from monitoring.health import HealthChecker, create_database_health_check

health = HealthChecker()

# Register custom check
def check_my_service():
    # Your check logic
    if service_is_healthy:
        return HealthStatus.HEALTHY, "Service OK"
    return HealthStatus.UNHEALTHY, "Service down"

health.register_check('my_service', check_my_service, critical=True)

# Run checks
result = health.run_all_checks()
print(result['status'])  # healthy, degraded, or unhealthy
```

### Performance Tracking

```python
from monitoring.performance import monitor_performance, track_performance

# Decorator approach
@monitor_performance('data_processing', include_system_stats=True)
def process_data(data):
    # Your processing logic
    pass

# Context manager approach
with track_performance('api_call'):
    response = make_api_call()

# Get statistics
from monitoring.performance import get_performance_monitor
monitor = get_performance_monitor()
stats = monitor.get_statistics('data_processing')
print(f"Average: {stats['avg']}s")
```

## Dashboards

### Grafana Dashboards

Two pre-configured dashboards:

#### 1. OSINT Overview Dashboard
- Request rate and errors
- CPU and memory usage
- Data collection metrics
- Active requests
- Queue sizes

#### 2. OSINT Performance Dashboard
- Request duration heatmap
- Percentile analysis (p50, p90, p95, p99)
- Analysis duration by type
- Database query performance
- Network throughput

### Kibana

Access Kibana at http://localhost:5601

**Index Patterns**: `osint-logs-*`

**Useful Searches**:
```
# Error logs in last 24h
level: ERROR OR level: CRITICAL

# Logs from specific source
source: "twitter"

# Slow operations (>1 second)
duration: >1
```

## Alerts

### Alert Rules

Pre-configured alerts in AlertManager:

| Alert              | Condition                      | Severity | Action         |
|--------------------|--------------------------------|----------|----------------|
| HighCPUUsage       | CPU > 80% for 5min            | Warning  | Email          |
| CriticalCPUUsage   | CPU > 95% for 2min            | Critical | Email/Page     |
| HighMemoryUsage    | Memory > 8GB for 5min         | Warning  | Email          |
| HighDiskUsage      | Disk > 85% for 10min          | Warning  | Email          |
| CriticalDiskUsage  | Disk > 95% for 5min           | Critical | Email/Page     |
| HighErrorRate      | Errors > 10/s for 5min        | Warning  | Email          |
| ApplicationDown    | App down for 1min             | Critical | Email/Page     |
| SlowRequests       | p95 latency > 5s for 10min    | Warning  | Email          |
| NoDataCollected    | No data for 15min             | Warning  | Email          |

### Configure Alert Notifications

Edit `monitoring/alertmanager/alertmanager.yml`:

```yaml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'your-email@example.com'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#osint-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

## Troubleshooting

### Logs Not Appearing in Kibana

1. Check Elasticsearch is running:
   ```bash
   curl http://localhost:9200/_cluster/health
   ```

2. Check Logstash is processing:
   ```bash
   docker logs osint-logstash
   ```

3. Verify log files exist:
   ```bash
   ls -lh logs/
   ```

### Metrics Not Showing in Grafana

1. Check Prometheus targets:
   http://localhost:9090/targets

2. Verify metrics endpoint:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. Check Grafana datasource:
   Grafana → Configuration → Data Sources → Prometheus

### Alerts Not Firing

1. Check AlertManager config:
   ```bash
   docker exec osint-alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
   ```

2. Verify SMTP settings in `.env`

3. Check alert rules in Prometheus:
   http://localhost:9090/alerts

### High Resource Usage

1. Adjust log retention:
   - Reduce `LOG_BACKUP_COUNT`
   - Decrease `LOG_MAX_BYTES`

2. Configure Elasticsearch cleanup:
   ```bash
   # Delete old indices
   curl -X DELETE http://localhost:9200/osint-logs-2024.01.*
   ```

3. Limit Prometheus retention:
   ```yaml
   # In prometheus.yml
   storage:
     tsdb:
       retention.time: 15d
   ```

## Best Practices

### Logging
1. Use appropriate log levels
2. Include context in structured logs
3. Don't log sensitive data (it will be masked, but avoid it)
4. Log errors with stack traces (`exc_info=True`)

### Monitoring
1. Monitor business metrics, not just technical
2. Set meaningful alert thresholds
3. Use percentiles (p95, p99) not averages
4. Track SLIs and SLOs

### Performance
1. Use performance monitoring judiciously
2. Don't track every function
3. Focus on critical paths
4. Review statistics regularly

### Security
1. Enable authentication for production
2. Use TLS for external access
3. Rotate credentials regularly
4. Limit network exposure

## Architecture Diagram

```
┌─────────────────┐
│  OSINT Toolkit  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Logging│ │Monitoring│
└───┬────┘ └────┬─────┘
    │           │
    │      ┌────┴────┐
    │      │         │
    ▼      ▼         ▼
┌────────┐ ┌──────────┐ ┌────────────┐
│Logstash│ │Prometheus│ │HealthCheck │
└───┬────┘ └────┬─────┘ └────────────┘
    │           │
    ▼           ▼
┌──────────────┐ ┌──────────────┐
│Elasticsearch │ │ AlertManager │
└───┬──────────┘ └──────┬───────┘
    │                   │
    ▼                   ▼
┌────────┐         ┌─────────┐
│ Kibana │         │ Grafana │
└────────┘         └─────────┘
```

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.monitoring.yml logs`
2. Review this documentation
3. Check service health endpoints
4. Contact the development team

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Maintainer**: OSINT Toolkit Team

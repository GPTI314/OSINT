# OSINT Toolkit

Open-Source Intelligence (OSINT) toolkit with enterprise-grade monitoring and logging.

## Features

### Core OSINT Capabilities (Planned)
- 🔍 Modular data collectors
- 🔄 Enrichment pipeline
- 🔗 Link analysis
- ⚠️ Risk scoring
- 🤖 Investigative workflow automation

### Monitoring & Logging (Implemented) ✅

#### A. Logging System
- ✅ **Structured logging** - JSON format with rich metadata
- ✅ **Log levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Centralized logging** - ELK Stack (Elasticsearch, Logstash, Kibana)
- ✅ **Log rotation** - Automatic rotation with configurable size limits
- ✅ **Sensitive data masking** - Auto-mask emails, IPs, API keys, credentials, etc.

#### B. Monitoring System
- ✅ **Prometheus metrics** - Application and system metrics collection
- ✅ **Grafana dashboards** - Pre-configured visualization dashboards
- ✅ **AlertManager** - Intelligent alerting with email/Slack/PagerDuty
- ✅ **Health checks** - System health monitoring endpoints
- ✅ **Performance monitoring** - Execution time tracking and statistics

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd OSINT

# Copy environment configuration
cp .env.example .env

# Edit configuration as needed
nano .env

# Start the monitoring stack
make start

# Or without make:
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Services

| Service       | URL                        | Credentials        |
|---------------|----------------------------|--------------------|
| Application   | http://localhost:5000      | -                  |
| Metrics       | http://localhost:8000      | -                  |
| Kibana        | http://localhost:5601      | -                  |
| Grafana       | http://localhost:3000      | admin/admin        |
| Prometheus    | http://localhost:9090      | -                  |
| AlertManager  | http://localhost:9093      | -                  |

### Verify Installation

```bash
# Check health
curl http://localhost:5000/health

# View metrics
curl http://localhost:8000/metrics

# View performance stats
curl http://localhost:5000/performance
```

## Documentation

- **[Monitoring & Logging Guide](MONITORING_LOGGING.md)** - Complete documentation for monitoring and logging system
- Architecture diagrams
- Configuration reference
- Usage examples
- Troubleshooting

## Project Structure

```
OSINT/
├── src/
│   ├── logging/              # Logging module
│   │   ├── logger.py         # Structured logging
│   │   ├── masking.py        # Sensitive data masking
│   │   └── elk_handler.py    # ELK Stack integration
│   ├── monitoring/           # Monitoring module
│   │   ├── metrics.py        # Prometheus metrics
│   │   ├── health.py         # Health checks
│   │   └── performance.py    # Performance monitoring
│   └── main.py               # Application entry point
├── monitoring/
│   ├── prometheus/           # Prometheus configuration
│   │   ├── prometheus.yml
│   │   ├── alerts/           # Alert rules
│   │   └── recording_rules/  # Recording rules
│   ├── grafana/              # Grafana dashboards
│   │   ├── dashboards/
│   │   └── provisioning/
│   ├── alertmanager/         # AlertManager config
│   │   ├── alertmanager.yml
│   │   └── templates/
│   └── elk/                  # ELK Stack config
│       ├── elasticsearch.yml
│       ├── logstash.conf
│       └── kibana.yml
├── config/                   # Configuration files
│   ├── logging.yaml
│   └── monitoring.yaml
├── logs/                     # Log files (gitignored)
├── tests/                    # Unit tests
├── docker-compose.monitoring.yml
├── Dockerfile
├── requirements.txt
├── Makefile
└── README.md
```

## Usage Examples

### Logging

```python
from logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Operation completed")

# Structured logging
logger.info("Data collected", extra={
    'source': 'twitter',
    'count': 100
})

# Automatic masking
logger.info("User: user@example.com, API: sk_test_123")  # Masked in logs
```

### Metrics

```python
from monitoring import get_metrics_collector

metrics = get_metrics_collector()

# Record data collection
metrics.record_data_collection('twitter', 'profile', count=10)

# Record enrichment
metrics.record_enrichment('geo_lookup', 'success')

# Record errors
metrics.record_error('ValueError', 'data_processor')
```

### Performance Monitoring

```python
from monitoring.performance import monitor_performance

@monitor_performance('data_processing', include_system_stats=True)
def process_data(data):
    # Your processing logic
    pass
```

## Development

### Using Makefile

```bash
make help              # Show available commands
make install           # Install dependencies
make start             # Start all services
make stop              # Stop all services
make logs              # Show logs
make health            # Check health
make metrics           # View metrics
make test              # Run tests
make clean             # Clean up
```

### Manual Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov=src

# Code quality
black src/          # Format
flake8 src/         # Lint
mypy src/           # Type check
```

## Monitoring & Alerts

### Pre-configured Alerts

- ⚠️ High CPU usage (>80% for 5 minutes)
- ⚠️ High memory usage (>8GB for 5 minutes)
- ⚠️ High disk usage (>85% for 10 minutes)
- 🚨 Application down (>1 minute)
- 🚨 High error rate (>10 errors/second)
- ⚠️ Slow requests (p95 latency >5 seconds)
- ⚠️ No data collected (>15 minutes)

### Grafana Dashboards

1. **OSINT Overview** - Request rates, errors, system metrics, data collection
2. **OSINT Performance** - Latency analysis, percentiles, throughput

## Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Application
APP_NAME=osint-toolkit
LOG_LEVEL=INFO

# ELK Stack
ELASTICSEARCH_HOST=elasticsearch
LOGSTASH_HOST=logstash

# Monitoring
METRICS_PORT=8000
GRAFANA_ADMIN_USER=admin

# Alerts
ALERT_EMAIL_TO=alerts@example.com
SMTP_HOST=smtp.example.com
```

See `.env.example` for all options.

## Testing

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Troubleshooting

See [MONITORING_LOGGING.md](MONITORING_LOGGING.md) for detailed troubleshooting guide.

Common issues:
- **Logs not in Kibana**: Check Elasticsearch and Logstash status
- **No metrics in Grafana**: Verify Prometheus targets
- **Alerts not firing**: Check AlertManager configuration

## Roadmap

- [x] Monitoring & Logging Infrastructure
- [ ] Data Collection Modules
- [ ] Enrichment Pipeline
- [ ] Link Analysis Engine
- [ ] Risk Scoring System
- [ ] Web Interface
- [ ] API Documentation
- [ ] Plugin System

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For issues or questions:
- Check the documentation in [MONITORING_LOGGING.md](MONITORING_LOGGING.md)
- Review logs: `make logs`
- Check health: `make health`

---

**Version**: 1.0.0
**Status**: Active Development

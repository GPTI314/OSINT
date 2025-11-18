# OSINT Toolkit with Celery Task Queue System

Open-Source Intelligence (OSINT) toolkit with comprehensive task scheduling, queue management, and workflow automation powered by Celery.

## Features

### 🚀 Task Queue System
- **Async Task Processing**: Non-blocking task execution with Celery workers
- **Task Prioritization**: 5-level priority queue system (critical, high, default, low, batch)
- **Retry Logic**: Automatic retry with exponential backoff and jitter
- **Task Monitoring**: Real-time monitoring with Flower dashboard
- **Scheduled Tasks**: Cron-based scheduling with Celery Beat
- **Event-Driven Tasks**: Webhook and event-based task triggering

### 📊 Priority Queue System
- **Critical Queue**: Emergency scans, immediate threat response (priority: 10)
- **High Queue**: Threat intelligence, security-critical tasks (priority: 7)
- **Default Queue**: Standard OSINT operations (priority: 5)
- **Low Queue**: Social media monitoring, non-urgent tasks (priority: 3)
- **Batch Queue**: Bulk exports, batch processing (priority: 1)

### ⚙️ Advanced Features
- **Rate Limiting**: Configurable rate limits per task type
- **Retry Logic**: Exponential backoff with configurable max retries
- **Task Chaining**: Sequential task execution workflows
- **Task Groups**: Parallel task execution
- **Task Chords**: Parallel execution with callbacks
- **Event Handlers**: Automatic response to security events
- **Result Backend**: Persistent task result storage
- **Task Routing**: Smart queue routing based on task type

### 🔍 OSINT Capabilities
- Domain reconnaissance and scanning
- Email enumeration
- Social media profile discovery
- Threat intelligence lookups
- WHOIS and DNS enumeration
- Vulnerability scanning
- Data leak detection
- Bulk data export

## Quick Start

### Prerequisites
- Python 3.11+
- Redis server
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd OSINT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start Redis:
```bash
redis-server
```

### Running with Docker

```bash
# Start all services (Redis, Workers, Beat, Flower)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Running Manually

1. **Start Celery Worker** (in separate terminals):
```bash
# Default worker
./start_worker.sh

# High priority worker
./start_worker.sh -q critical,high -c 2

# Low priority worker
./start_worker.sh -q low,batch -c 2
```

2. **Start Celery Beat** (scheduler):
```bash
./start_beat.sh
```

3. **Start Flower** (monitoring dashboard):
```bash
./start_flower.sh
```

Access Flower dashboard at: http://localhost:5555

## Usage Examples

### Basic Task Execution

```python
from tasks.osint import domain_scan, email_enumeration, threat_intelligence

# Submit a task
result = domain_scan.delay('example.com', deep_scan=True)
print(f"Task ID: {result.id}")

# Wait for result
output = result.get(timeout=30)
print(output)
```

### Priority Queue Usage

```python
# Critical priority task
result = emergency_scan.apply_async(
    args=['suspicious-domain.com'],
    queue='critical',
    priority=10
)

# High priority task
result = threat_intelligence.apply_async(
    args=['192.168.1.1', 'ip'],
    queue='high',
    priority=7
)
```

### Task Chaining (Sequential)

```python
from celery import chain
from tasks.osint import whois_lookup, dns_enumeration, domain_scan

# Tasks execute sequentially
workflow = chain(
    whois_lookup.s('example.com'),
    dns_enumeration.s('example.com'),
    domain_scan.s('example.com', deep_scan=True)
)
result = workflow.apply_async()
```

### Task Groups (Parallel)

```python
from celery import group
from tasks.osint import domain_scan

# Tasks execute in parallel
job = group(
    domain_scan.s('example1.com'),
    domain_scan.s('example2.com'),
    domain_scan.s('example3.com')
)
result = job.apply_async()
```

### Scheduled Tasks

```python
from datetime import datetime, timedelta

# Schedule task to run in 5 minutes
eta_time = datetime.now() + timedelta(minutes=5)
result = domain_scan.apply_async(
    args=['example.com'],
    eta=eta_time
)

# Or use countdown (seconds)
result = domain_scan.apply_async(
    args=['example.com'],
    countdown=300
)
```

### Event-Driven Tasks

```python
from tasks.events import on_threat_detected, trigger_investigation_workflow

# Trigger threat response
threat_data = {
    'type': 'malware',
    'level': 'critical',
    'target': 'malicious-site.com'
}
on_threat_detected.delay(threat_data)

# Trigger investigation
trigger_investigation_workflow.delay('target.com', 'comprehensive')
```

### Interactive Examples

Run the interactive example script:
```bash
python example_usage.py
```

This provides 13+ examples demonstrating all features.

## Monitoring

### Command-Line Monitoring

```bash
# Show dashboard
python monitor.py dashboard

# Show active workers
python monitor.py workers

# Show active tasks
python monitor.py active

# Show queue status
python monitor.py queues

# Get task info
python monitor.py task <task_id>

# Cancel a task
python monitor.py cancel <task_id>
```

### Flower Dashboard

Access the web-based monitoring dashboard:
```
http://localhost:5555
```

Features:
- Real-time task monitoring
- Worker management
- Task history and statistics
- Queue inspection
- Task retry and revoke
- Performance metrics

## Architecture

```
┌─────────────────┐
│   Application   │
│   (Your Code)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Celery Tasks   │
│  (Task Queue)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Redis Broker   │◄────►│   Workers    │
│  (Message Queue)│      │  (Executors) │
└─────────────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│ Result Backend  │
│   (Storage)     │
└─────────────────┘
```

## Task Types

### OSINT Tasks (`tasks/osint.py`)
- `emergency_scan`: Critical priority security scan
- `threat_intelligence`: Threat feed lookups
- `domain_scan`: Domain reconnaissance
- `email_enumeration`: Email discovery
- `social_media_scan`: Social media profile search
- `whois_lookup`: WHOIS information retrieval
- `dns_enumeration`: DNS record enumeration
- `bulk_export`: Data export functionality

### Scheduled Tasks (`tasks/scheduled.py`)
- `check_threat_feeds`: Every 5 minutes
- `check_domain_reputation`: Hourly
- `generate_daily_report`: Daily at midnight
- `weekly_vulnerability_scan`: Weekly on Mondays
- `monitor_social_media`: Every 15 minutes
- `update_ip_reputation`: Every 6 hours
- `archive_old_data`: Monthly
- `cleanup_temp_files`: Every 30 minutes

### Event-Driven Tasks (`tasks/events.py`)
- `on_threat_detected`: Threat response handler
- `on_new_ioc`: IoC enrichment handler
- `on_scan_complete`: Scan result processor
- `on_data_leak_found`: Data leak handler
- `trigger_investigation_workflow`: Investigation orchestrator
- `webhook_handler`: Generic webhook handler

## Configuration

### Celery Configuration (`celery_config.py`)

Key settings:
- **Broker**: Redis URL for message broker
- **Result Backend**: Redis URL for result storage
- **Worker Settings**: Concurrency, prefetch, task limits
- **Retry Settings**: Max retries, backoff configuration
- **Rate Limits**: Per-task rate limiting
- **Time Limits**: Soft and hard time limits
- **Beat Schedule**: Cron job definitions

### Environment Variables (`.env`)

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_SOFT_TIME_LIMIT=3600
```

See `.env.example` for full configuration options.

## Deployment

### Production Deployment

1. **Use Process Manager** (systemd, supervisord):
```bash
# Example systemd service
sudo systemctl start celery-worker
sudo systemctl start celery-beat
```

2. **Scale Workers**:
```bash
# Multiple workers for different queues
celery -A celery_app worker -Q critical,high -c 4 -n high@%h
celery -A celery_app worker -Q default -c 8 -n default@%h
celery -A celery_app worker -Q low,batch -c 2 -n low@%h
```

3. **Use Docker Compose**:
```bash
docker-compose up -d --scale celery_worker_default=3
```

### High Availability

- Use Redis Sentinel or Redis Cluster for HA
- Run multiple workers across different machines
- Use RabbitMQ for more advanced features
- Implement health checks and auto-restart

## Security Considerations

- Store API keys in environment variables
- Use Redis authentication (requirepass)
- Enable Flower authentication
- Implement rate limiting
- Validate task inputs
- Use task signing for security
- Monitor for suspicious activity

## Troubleshooting

### Worker Not Starting
```bash
# Check Redis connection
redis-cli -h localhost -p 6379 ping

# Check worker logs
tail -f logs/worker_default.log
```

### Tasks Not Executing
```bash
# Check active workers
python monitor.py workers

# Check queue status
python monitor.py queues

# Purge stuck tasks
python monitor.py purge default
```

### Task Failures
```bash
# Check task details
python monitor.py task <task_id>

# View error logs
tail -f logs/worker_*.log
```

## Performance Tips

1. **Optimize Worker Count**: Set concurrency based on CPU cores
2. **Use Prefetching**: Configure `worker_prefetch_multiplier`
3. **Enable Result Expiry**: Set `result_expires` to clean old results
4. **Use Task Compression**: Enable gzip compression for large payloads
5. **Implement Caching**: Cache frequently accessed data
6. **Monitor Memory**: Restart workers periodically with `max_tasks_per_child`

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

[Your License Here]

## Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
- [OSINT Framework](https://osintframework.com/)

## Support

For issues, questions, or contributions:
- GitHub Issues: [Your Repo URL]
- Documentation: [Your Docs URL]
- Email: [Your Email]
